"""Guardado y recuperación de conversaciones en Supabase.

Sustituye el diccionario `MEMORIA` del notebook de la Clase 11.

- Cada instancia trabaja con el cliente autenticado de UNA persona (`ContextoUsuario.supabase`).
  No hay cliente global (dos usuarios nunca comparten sesión).
- Las políticas RLS de sql/01_historial.sql son la barrera real. Además, cada método comprueba
  el propietario antes de leer o escribir mensajes, para dar un error claro y no depender de
  un resultado vacío.
- Se conservan todos los mensajes. `historial_para_modelo` decide cuántos turnos van al modelo
  (MAX_TURNOS); guardar y elegir contexto son responsabilidades distintas.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

PATRON_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
TITULO_INICIAL = "Nueva conversación"


class AccesoDenegado(PermissionError):
    """La conversación no existe o no pertenece al usuario autenticado."""


def validar_uuid(valor: str) -> str:
    if not isinstance(valor, str) or not PATRON_UUID.fullmatch(valor):
        raise AccesoDenegado("Identificador de conversación no válido.")
    return valor


def titulo_desde_pregunta(pregunta: str) -> str:
    limpio = " ".join(pregunta.split())
    return (limpio[:57] + "...") if len(limpio) > 60 else (limpio or TITULO_INICIAL)


def historial_para_modelo(mensajes: list[dict], max_turnos: int) -> list[dict]:
    """Convierte mensajes ordenados en turnos {usuario, respuesta} y conserva los últimos max_turnos."""
    turnos, pendiente = [], None
    for m in mensajes:
        if m["rol"] == "user":
            pendiente = m["contenido"]
        elif m["rol"] == "assistant" and pendiente is not None:
            turnos.append({"usuario": pendiente, "respuesta": m["contenido"]})
            pendiente = None
    return turnos[-max_turnos:] if max_turnos > 0 else []


class Almacenamiento:
    def __init__(self, supabase, usuario_id: str):
        self.db = supabase
        self.usuario_id = usuario_id

    # conversations -----------------------------------------------------------
    def crear_conversacion(self, titulo: str = TITULO_INICIAL) -> dict:
        fila = (self.db.table("conversaciones")
                .insert({"usuario_id": self.usuario_id, "titulo": titulo[:120] or TITULO_INICIAL})
                .execute().data)
        if not fila:
            raise RuntimeError("Supabase no confirmó la creación de la conversación.")
        return fila[0]

    def listar_conversaciones(self, limite: int = 50) -> list[dict]:
        return (self.db.table("conversaciones").select("id,titulo,creada_en,actualizada_en")
                .eq("usuario_id", self.usuario_id)
                .order("actualizada_en", desc=True).limit(limite).execute().data)

    def obtener_conversacion(self, conversacion_id: str) -> dict:
        validar_uuid(conversacion_id)
        filas = (self.db.table("conversaciones").select("id,usuario_id,titulo")
                 .eq("id", conversacion_id).eq("usuario_id", self.usuario_id).limit(1).execute().data)
        if not filas or filas[0]["usuario_id"] != self.usuario_id:
            raise AccesoDenegado("La conversación no existe o no te pertenece.")
        return filas[0]

    # messages -----------------------------------------------------------------
    def cargar_mensajes(self, conversacion_id: str) -> list[dict]:
        self.obtener_conversacion(conversacion_id)
        return (self.db.table("mensajes").select("id,rol,contenido,estado,fuentes,creado_en")
                .eq("conversacion_id", conversacion_id).order("id").execute().data)

    def guardar_turno(self, conversacion_id: str, pregunta: str, traza: dict) -> list[dict]:
        """Inserta pregunta y respuesta en una sola petición (una sentencia: ambas o ninguna)."""
        conversacion = self.obtener_conversacion(conversacion_id)
        citadas = {e: traza.get("fuentes", {}).get(e) for e in traza.get("citas", [])}
        resumen_traza = {k: traza.get(k) for k in ("eventos", "operaciones", "duracion_ms", "permiso_informe",
                                                     "error_detalle", "tipo_error") if traza.get(k) is not None}
        resumen_traza["archivos"] = [a.rsplit("/", 1)[-1] for a in traza.get("archivos", [])]
        filas = (self.db.table("mensajes").insert([
            {"conversacion_id": conversacion_id, "usuario_id": self.usuario_id, "rol": "user",
             "contenido": pregunta, "estado": None, "fuentes": {}, "traza": {}},
            {"conversacion_id": conversacion_id, "usuario_id": self.usuario_id, "rol": "assistant",
             "contenido": traza["respuesta"] or "(sin respuesta)", "estado": traza.get("estado"),
             "fuentes": {"citas": traza.get("citas", []), "detalle": citadas}, "traza": resumen_traza},
        ]).execute().data)
        if len(filas or []) != 2:
            raise RuntimeError("Supabase no confirmó el guardado del turno.")
        cambios = {"actualizada_en": datetime.now(timezone.utc).isoformat()}
        if conversacion["titulo"] == TITULO_INICIAL:
            cambios["titulo"] = titulo_desde_pregunta(pregunta)
        self.db.table("conversaciones").update(cambios).eq("id", conversacion_id).execute()
        return filas
