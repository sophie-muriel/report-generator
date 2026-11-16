"""Pruebas de persistencia y aislamiento con Supabase real (dos usuarios de prueba).

Comprueba lo que exige la entrega:
  1. Un usuario guarda preguntas y respuestas en dos conversaciones propias.
  2. Con un cliente nuevo (equivale a cerrar sesión / reiniciar la app) las recupera.
  3. Otro usuario NO puede leer ni insertar en esas conversaciones aunque conozca el UUID.

Las contraseñas se piden por teclado: no se guardan en .env ni en el repositorio.
Ejecutar desde app/ con app/.env configurado:

    python pruebas_rls.py

Deja una evidencia JSON en ../evidencias/ (sin correos completos ni contraseñas).
No consume Groq ni carga el modelo de embeddings.
"""
from __future__ import annotations

import getpass
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import ClientOptions, create_client

from almacenamiento import AccesoDenegado, Almacenamiento

DIRECTORIO_APP = Path(__file__).resolve().parent
load_dotenv(DIRECTORIO_APP / ".env")
URL, CLAVE = os.environ["SUPABASE_URL"].rstrip("/"), os.environ["SUPABASE_PUBLISHABLE_KEY"]


def sesion(etiqueta: str):
    correo = input(f"Correo del usuario {etiqueta}: ").strip()
    clave = getpass.getpass(f"Contraseña del usuario {etiqueta}: ")
    return correo, clave


def cliente(correo: str, clave: str):
    c = create_client(URL, CLAVE, options=ClientOptions(persist_session=False))
    usuario = c.auth.sign_in_with_password({"email": correo, "password": clave}).user
    return c, usuario.id


def enmascarar(correo: str) -> str:
    nombre, _, dominio = correo.partition("@")
    return nombre[:2] + "***@" + dominio


RESULTADOS: list[dict] = []


def registrar(caso: str, esperado: str, observado: str, ok: bool) -> None:
    RESULTADOS.append({"caso": caso, "esperado": esperado, "observado": observado,
                       "estado": "APROBADO" if ok else "FALLIDO"})
    print(("✔" if ok else "✘"), caso, "→", observado)


def main() -> None:
    correo_a, clave_a = sesion("A")
    correo_b, clave_b = sesion("B")
    db_a, id_a = cliente(correo_a, clave_a)
    db_b, id_b = cliente(correo_b, clave_b)
    registrar("Dos identidades distintas", "UUID A ≠ UUID B", "distintos" if id_a != id_b else "iguales", id_a != id_b)

    a = Almacenamiento(db_a, id_a)
    traza = {"respuesta": "Respuesta de prueba RLS.", "estado": "RESPONDER", "citas": [], "fuentes": {}}
    conv1 = a.crear_conversacion("Prueba RLS 1")
    conv2 = a.crear_conversacion("Prueba RLS 2")
    a.guardar_turno(conv1["id"], "Pregunta de prueba 1", traza)
    a.guardar_turno(conv2["id"], "Pregunta de prueba 2", traza)
    registrar("A guarda en dos conversaciones", "2 mensajes por conversación",
              f"{len(a.cargar_mensajes(conv1['id']))} y {len(a.cargar_mensajes(conv2['id']))}",
              len(a.cargar_mensajes(conv1["id"])) == 2 and len(a.cargar_mensajes(conv2["id"])) == 2)

    # Cliente nuevo para A: equivale a cerrar sesión y volver a entrar / reiniciar el servidor.
    db_a2, _ = cliente(correo_a, clave_a)
    a2 = Almacenamiento(db_a2, id_a)
    ids = {c["id"] for c in a2.listar_conversaciones()}
    recuperado = a2.cargar_mensajes(conv1["id"])
    registrar("A recupera tras nueva sesión", "ambas conversaciones y sus mensajes en orden",
              f"{len({conv1['id'], conv2['id']} & ids)} conversaciones, roles {[m['rol'] for m in recuperado]}",
              {conv1["id"], conv2["id"]} <= ids and [m["rol"] for m in recuperado] == ["user", "assistant"])

    # B intenta leer directamente (sin pasar por almacenamiento.py): RLS debe devolver vacío.
    vistas = db_b.table("conversaciones").select("id").eq("id", conv1["id"]).execute().data
    registrar("B lee conversación de A por UUID", "0 filas", f"{len(vistas)} filas", not vistas)
    mensajes = db_b.table("mensajes").select("id").eq("conversacion_id", conv1["id"]).execute().data
    registrar("B lee mensajes de A por UUID", "0 filas", f"{len(mensajes)} filas", not mensajes)

    # B intenta insertar un mensaje en la conversación de A.
    try:
        db_b.table("mensajes").insert({"conversacion_id": conv1["id"], "usuario_id": id_b,
                                       "rol": "user", "contenido": "intrusión"}).execute()
        registrar("B inserta mensaje en conversación de A", "rechazado por RLS", "INSERTADO", False)
    except Exception as error:
        registrar("B inserta mensaje en conversación de A", "rechazado por RLS", type(error).__name__, True)

    # B intenta suplantar a A como propietario de una conversación nueva.
    try:
        db_b.table("conversaciones").insert({"usuario_id": id_a, "titulo": "suplantación"}).execute()
        registrar("B crea conversación a nombre de A", "rechazado por RLS", "INSERTADA", False)
    except Exception as error:
        registrar("B crea conversación a nombre de A", "rechazado por RLS", type(error).__name__, True)

    # Y a través de la capa de la aplicación.
    try:
        Almacenamiento(db_b, id_b).cargar_mensajes(conv1["id"])
        registrar("almacenamiento.py de B abre conversación de A", "AccesoDenegado", "abrió", False)
    except AccesoDenegado:
        registrar("almacenamiento.py de B abre conversación de A", "AccesoDenegado", "AccesoDenegado", True)

    # Verificamos que el intento de B no dejó rastro en la conversación de A.
    final = a2.cargar_mensajes(conv1["id"])
    registrar("Conversación de A intacta", "2 mensajes", f"{len(final)} mensajes", len(final) == 2)

    evidencia = {"fecha_utc": datetime.now(timezone.utc).isoformat(),
                 "usuarios": [enmascarar(correo_a), enmascarar(correo_b)],
                 "conversaciones_prueba": [conv1["id"], conv2["id"]], "resultados": RESULTADOS}
    carpeta = DIRECTORIO_APP.parent / "evidencias"
    carpeta.mkdir(exist_ok=True)
    salida = carpeta / f"pruebas_rls_{datetime.now():%Y%m%d_%H%M%S}.json"
    salida.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")
    aprobados = sum(r["estado"] == "APROBADO" for r in RESULTADOS)
    print(f"\n{aprobados}/{len(RESULTADOS)} aprobados. Evidencia: {salida}")
    for c in (db_a, db_a2, db_b):
        c.auth.sign_out()


if __name__ == "__main__":
    main()
