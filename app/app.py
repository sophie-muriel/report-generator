"""Interfaz Gradio de Report Generator (Clase 12 - entrega final).

Responsabilidades de este archivo (app.py):
- Inicio de sesión con Supabase Auth y cierre de sesión.
- Crear, listar y abrir conversaciones (vía almacenamiento.py).
- Recibir la pregunta, llamar a sistema.atender y mostrar respuesta, fuentes, recorrido y borrador.

La lógica del RAG, el agente y los MCP vive en sistema.py; la persistencia en almacenamiento.py.
El estado de Gradio solo guarda la sesión activa de cada navegador; los datos viven en Supabase.

Ejecutar desde app/:  python app.py
"""
from __future__ import annotations

import asyncio
import html
import json
import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

import sistema
from almacenamiento import AccesoDenegado, Almacenamiento, historial_para_modelo

DIRECTORIO_APP = Path(__file__).resolve().parent
load_dotenv(DIRECTORIO_APP / ".env")

ETIQUETAS_ESTADO = {
    "ACLARAR": "Aclaración", "RECHAZAR": "Solicitud rechazada", "ERROR_TECNICO": "Error técnico",
    "ERROR_VALIDACION": "Control no superado", "LIMITE_OPERACIONES": "Límite de operaciones",
    "LIMITE_DECISIONES": "Límite de decisiones", "LIMITE_TIEMPO": "Tiempo agotado",
    "LIMITE_CONTEXTO": "Contexto demasiado largo", "REPETICION_SIN_AVANCE": "Repetición detenida",
    "INFORME_NO_GENERADO": "Borrador no generado",
}

# color palette
ROSA = "#C8467A"
ROSA_SUAVE = "#F8E6EE"
FONDO = "#FAF8F5"
LATERAL = "#F2EEE8"
TINTA = "#2B2522"

TEMA = gr.themes.Base(
    primary_hue=gr.themes.Color(
        c50="#FCF3F7", c100=ROSA_SUAVE, c200="#F0C9DA", c300="#E5A1BE", c400="#D8739D", c500=ROSA,
        c600="#B03A69", c700="#912F56", c800="#732645", c900="#5A1F37", c950="#381322"),
    neutral_hue=gr.themes.colors.stone,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    radius_size=gr.themes.sizes.radius_md,
    spacing_size=gr.themes.sizes.spacing_md,
).set(
    body_background_fill=FONDO, body_text_color=TINTA,
    background_fill_primary=FONDO, background_fill_secondary=LATERAL,
    block_background_fill="transparent", block_border_width="0px", block_shadow="none",
    block_label_background_fill="transparent", panel_background_fill="transparent",
    input_background_fill="#FFFFFF", input_border_color="#E4DED6", input_border_color_focus=ROSA,
    input_shadow="none", input_shadow_focus="0 0 0 3px " + ROSA_SUAVE,
    button_primary_background_fill=ROSA, button_primary_background_fill_hover="#B03A69",
    button_primary_text_color="#FFFFFF", button_primary_border_color=ROSA,
    button_secondary_background_fill="transparent", button_secondary_background_fill_hover="#E9E3DB",
    button_secondary_border_color="#DDD6CD", button_secondary_text_color=TINTA,
    checkbox_background_color_selected=ROSA, checkbox_border_color_selected=ROSA,
    color_accent=ROSA, color_accent_soft=ROSA_SUAVE,
)

CSS = """
footer {display: none !important;}
.gradio-container {max-width: 100% !important; padding: 0 !important;}
main.app, .gradio-container main, .gradio-container main.fillable, .gradio-container .main
    {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}
.form {background: transparent !important; border: 0 !important; box-shadow: none !important; gap: 12px !important;}
.hide-container {padding: 0 !important;}

/* ---------- light mode ---------- */
.dark {
  --body-background-fill: #FAF8F5 !important; --body-text-color: #2B2522 !important;
  --background-fill-primary: #FAF8F5 !important; --background-fill-secondary: #F2EEE8 !important;
  --block-background-fill: transparent !important; --block-label-background-fill: transparent !important;
  --panel-background-fill: transparent !important;
  --input-background-fill: #FFFFFF !important; --input-border-color: #E4DED6 !important;
  --button-primary-background-fill: #C8467A !important; --button-primary-text-color: #FFFFFF !important;
  --button-secondary-background-fill: transparent !important; --button-secondary-text-color: #2B2522 !important;
  --checkbox-background-color-selected: #C8467A !important; --checkbox-border-color-selected: #C8467A !important;
  --color-accent: #C8467A !important; --color-accent-soft: #F8E6EE !important;
  --border-color-primary: #E4DED6 !important; --border-color-accent: #C8467A !important;
  --pro-background-fill: #C8467A !important;
  --shadow-drop: none !important; --shadow-spread: none !important;
}

/* ---------- login ---------- */
#panel-login {max-width: 360px; margin: 16vh auto 0 auto; padding: 0 16px;}
#panel-login h1 {font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 2.1rem; margin: 0 0 .2rem 0;}
#panel-login p {color: #7A716A;}

/* ---------- structure ---------- */
#app {gap: 0 !important; flex-wrap: nowrap !important; min-height: 100vh;}

/* ---------- side bar ---------- */
#lateral {background: #F2EEE8; border-right: 1px solid #E8E2DA; height: 100vh; position: sticky; top: 0;
          flex: 0 0 264px !important; min-width: 264px !important; max-width: 264px;
          padding: 22px 12px 16px 12px; gap: 4px !important; overflow-y: auto;}
#marca h3 {font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 1.3rem;
           margin: 0 0 14px 10px; letter-spacing: -.01em;}
#marca h3 span {color: #C8467A;}
#nueva {justify-content: flex-start !important; background: transparent !important; border: 0 !important;
        box-shadow: none !important; font-weight: 500; font-size: .92rem; padding: 8px 10px !important;
        border-radius: 10px !important; color: #2B2522 !important;}
#nueva:hover {background: #E9E3DB !important;}
#nueva::before {content: "+"; display: inline-flex; align-items: center; justify-content: center;
                width: 22px; height: 22px; border-radius: 50%; background: #C8467A; color: #fff;
                font-size: 15px; line-height: 1; margin-right: 10px;}
#lista {padding: 0 !important; margin-top: 14px; background: transparent !important; border: 0 !important;}
#lista [data-testid=block-info] {font-size: .75rem; color: #9A9087; padding-left: 10px; margin-bottom: 4px;}
#lista .wrap {flex-direction: column; gap: 1px !important;}
#lista input[type=radio] {display: none;}
#lista label {background: transparent !important; border: 0 !important; box-shadow: none !important;
              width: 100%; padding: 7px 10px !important; border-radius: 8px !important; font-size: .9rem;
              color: #3D3532; cursor: pointer;}
#lista label span {white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0 !important;}
#lista label:hover {background: #E9E3DB !important;}
#lista label.selected {background: #E4DDD4 !important; color: #2B2522;}
#usuario {margin-top: auto !important; padding: 10px 6px 0 6px !important; border-top: 1px solid #E4DDD4;}
.yo {display: flex; align-items: center; gap: 10px; min-width: 0;}
.yo .avatar {flex: 0 0 30px; height: 30px; border-radius: 50%; background: #C8467A; color: #fff;
             display: flex; align-items: center; justify-content: center; font-size: .85rem; font-weight: 600;}
.yo .correo {font-size: .82rem; color: #3D3532; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
.yo-aviso {font-size: .78rem; color: #A23B5F; margin: 6px 0 0 0;}
#salir {justify-content: flex-start !important; background: transparent !important; border: 0 !important;
        box-shadow: none !important; color: #8C837B !important; font-size: .8rem; padding: 4px 6px 4px 46px !important;}
#salir:hover {color: #C8467A !important;}

/* ---------- conversation ---------- */
#principal {height: 100vh; overflow-y: auto; flex-wrap: nowrap !important; padding: 18px 24px 14px 24px !important; gap: 8px !important;}
#principal > * {width: 100%; max-width: 760px; margin-left: auto !important; margin-right: auto !important;}
#chat {border: 0 !important; background: transparent !important; box-shadow: none !important;}
#chat .top-panel {display: none !important;}
#chat .bubble-wrap {background: transparent !important; padding: 8px 0 !important;}
#chat .message-row {margin: 6px 0 !important;}
#chat .message.bot {background: transparent !important; border: 0 !important; box-shadow: none !important;
                    padding-left: 0 !important; max-width: 100% !important;
                    font-family: Georgia, 'Times New Roman', serif; font-size: 1.04rem; line-height: 1.7; color: #2B2522;}
#chat .message.user {background: #F8E6EE !important; border: 0 !important; box-shadow: none !important;
                     border-radius: 18px !important; padding: 10px 16px !important; color: #2B2522;}
#chat .message-buttons {opacity: 0; transition: opacity .15s;}
#chat .message-buttons:hover, #chat .message-row:hover + .message-buttons {opacity: .6;}
.saludo {text-align: center; padding-top: 18vh;}
.saludo h2 {font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 2.1rem;
            color: #2B2522; margin: 0 0 .5rem 0; letter-spacing: -.01em;}
.saludo h2 em {font-style: normal; color: #C8467A;}
.saludo p {color: #8C837B; font-size: .95rem; margin: 0;}

/* message box */
#entrada {background: #FFFFFF !important; border: 1px solid #E4DED6 !important; border-radius: 20px !important;
          box-shadow: 0 1px 2px rgba(60, 40, 30, .04), 0 6px 20px rgba(60, 40, 30, .06) !important;
          padding: 10px 10px 10px 16px !important;}
#entrada:focus-within {border-color: #D9A3BA !important;}
#entrada .input-container {align-items: flex-end; gap: 8px;}
#entrada textarea {border: 0 !important; box-shadow: none !important; background: transparent !important;
                   font-size: 1rem; padding: 6px 0 !important; resize: none;}
#entrada .submit-button {background: #C8467A !important; border-radius: 12px !important; width: 36px !important;
                         height: 36px !important; min-width: 36px; border: 0 !important;}
#entrada .submit-button:hover {background: #B03A69 !important;}
#entrada .submit-button svg {filter: brightness(0) invert(1); width: 16px; height: 16px;}

#extras {gap: 22px !important; align-items: center; flex-wrap: wrap; justify-content: flex-start;}
#extras .icon {display: none !important;}
#permiso {padding: 0 !important; flex: 0 1 auto !important; min-width: 0 !important;}
#permiso label {font-size: .82rem; color: #7A716A; gap: 8px;}
#extras {flex-wrap: nowrap !important;}
#extras > *, #extras .block {flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;
                             margin: 0 !important;}
#extras .detalle:has(.open), #extras .detalle.open {flex: 1 1 100% !important;}
.detalle {background: transparent !important; border: 0 !important; padding: 0 !important;}
.detalle > button, .detalle .label-wrap {font-size: .82rem !important; color: #7A716A !important; padding: 2px 0 !important;}
#aviso p {color: #A23B5F; font-size: .85rem; margin: 0;}

/* login window (over chat) */
#modal-login {position: fixed !important; inset: 0; z-index: 1000; background: rgba(43, 37, 34, .32);
              display: flex; align-items: center; justify-content: center; padding: 16px; margin: 0 !important;
              max-width: none !important;}
#modal-login.hidden, #modal-login[hidden] {display: none !important;}
#tarjeta-login {background: #FAF8F5; border-radius: 18px; padding: 28px 28px 20px 28px; width: 100%;
                max-width: 380px; box-shadow: 0 20px 60px rgba(43, 37, 34, .25); gap: 12px !important;
                flex: 0 0 auto !important;}
#tarjeta-login h2 {font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 1.6rem; margin: 0 0 .3rem 0;}
#tarjeta-login p {color: #7A716A; font-size: .9rem; margin: 0;}
#cancelar {background: transparent !important; border: 0 !important; box-shadow: none !important;
           color: #8C837B !important; font-size: .85rem;}
#aviso-login p {color: #A23B5F; font-size: .85rem;}
#clave input {padding-right: 42px !important;}
.ojo {position: absolute; right: 8px; top: 50%; transform: translateY(-50%); background: transparent; z-index: 5;
      border: 0; padding: 6px; color: #8C837B; cursor: pointer; display: flex; border-radius: 8px;}
.ojo:hover {color: #C8467A; background: #F8E6EE;}
.sin-sesion {font-size: .8rem; color: #8C837B; margin: 0; line-height: 1.4;}
#abrir-login {background: #C8467A !important; color: #fff !important; border: 0 !important;
              border-radius: 10px !important; font-weight: 500; margin-top: 6px;}
#abrir-login:hover {background: #B03A69 !important;}

/* thinking indicator */
.pensando {display: inline-flex; align-items: center; gap: 10px; color: #8C837B;
           font-family: Inter, system-ui, sans-serif; font-size: .92rem;}
.pensando .puntos {display: inline-flex; gap: 5px;}
.pensando .puntos i {width: 7px; height: 7px; border-radius: 50%; background: #C8467A; opacity: .25;
                     animation: latido 1.2s infinite ease-in-out;}
.pensando .puntos i:nth-child(2) {animation-delay: .15s;}
.pensando .puntos i:nth-child(3) {animation-delay: .3s;}
@keyframes latido {0%, 80%, 100% {opacity: .25; transform: translateY(0);}
                   40% {opacity: 1; transform: translateY(-3px);}}
.estado {display: inline-block; font-family: Inter, system-ui, sans-serif; font-size: .72rem; font-weight: 500;
         color: #A23B5F; background: #F8E6EE; border-radius: 999px; padding: 2px 9px; margin-right: 6px;
         vertical-align: 2px;}
/* remove Gradio's processing layers from the interface */
#app .wrap.default, #app .wrap.minimal, #app [data-testid=status-tracker] {display: none !important;}

.fuente {border-left: 2px solid #C8467A; padding: 4px 12px; margin: 8px 0; font-size: .9rem;}
.fuente small {color: #8C837B;}
"""

# browser JS to force light mode and add "show password" button to login form
JS = r"""
() => {
  const forzarClaro = () => {
    document.documentElement.classList.remove('dark');
    if (document.body) document.body.classList.remove('dark');
    document.documentElement.style.colorScheme = 'light';
  };
  forzarClaro();
  new MutationObserver(forzarClaro).observe(document.documentElement, {attributes: true, attributeFilter: ['class']});
  new MutationObserver(forzarClaro).observe(document.body, {attributes: true, attributeFilter: ['class']});
  const OJO = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>';
  const OJO_NO = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18"/><path d="M10.6 5.1A10.9 10.9 0 0 1 12 5c6.5 0 10 7 10 7a17.6 17.6 0 0 1-3.2 4.1M6.6 6.6C3.9 8.3 2 12 2 12s3.5 7 10 7a10.6 10.6 0 0 0 5.4-1.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>';
  const ajustar = () => {
    const correo = document.querySelector('#correo input');
    if (correo) correo.setAttribute('autocomplete', 'off');
    const caja = document.querySelector('#clave');
    const clave = caja && caja.querySelector('input');
    if (!clave) return;
    clave.setAttribute('autocomplete', 'new-password');
    let boton = caja.querySelector('.ojo');
    if (!boton) {
      boton = document.createElement('button');
      boton.type = 'button';
      boton.className = 'ojo';
      boton.onclick = () => {
        clave.type = clave.type === 'password' ? 'text' : 'password';
        pintar();
        clave.focus();
      };
      clave.parentElement.style.position = 'relative';
      clave.parentElement.appendChild(boton);
    }
    const pintar = () => {
      const visible = clave.type === 'text';
      const estado = visible ? 'visible' : 'oculta';
      if (boton.dataset.estado === estado) return;
      boton.dataset.estado = estado;
      boton.innerHTML = visible ? OJO_NO : OJO;
      boton.setAttribute('aria-label', visible ? 'Ocultar contraseña' : 'Mostrar contraseña');
      boton.title = boton.getAttribute('aria-label');
    };
    const modal = document.querySelector('#modal-login');
    if (modal && modal.getClientRects().length === 0 && clave.type !== 'password') clave.type = 'password';
    pintar();
  };
  ajustar();
  new MutationObserver(ajustar).observe(document.body, {childList: true, subtree: true, attributes: true,
                                                        attributeFilter: ['class', 'style']});
}
"""

SIN_SESION = "<p class='sin-sesion'>Inicia sesión para guardar tus conversaciones.</p>"

PENSANDO = ("<span class='pensando'><span class='puntos'><i></i><i></i><i></i></span>Pensando</span>")

SALUDO = ("<div class='saludo'><h2>¿En qué te ayudo hoy<em>?</em></h2>"
          "<p>Tipos de informe, reglas de un borrador o el estado de una fuente como DS-1001.</p></div>")


def tarjeta_usuario(email: str, avisos: str = "") -> str:
    inicial = html.escape((email or "?")[0].upper())
    extra = f"<p class='yo-aviso'>{html.escape(avisos)}</p>" if avisos else ""
    return (f"<div class='yo'><span class='avatar'>{inicial}</span>"
            f"<span class='correo' title='{html.escape(email)}'>{html.escape(email)}</span></div>{extra}")


# --------------------------------------------------------------------------- utilidades de presentación

def mensajes_a_chat(mensajes: list[dict]) -> list[dict]:
    chat = []
    for m in mensajes:
        contenido = m["contenido"]
        if m["rol"] == "assistant" and m.get("estado") in ETIQUETAS_ESTADO:
            contenido = f"<span class='estado'>{ETIQUETAS_ESTADO[m['estado']]}</span> {contenido}"
        chat.append({"role": m["rol"], "content": contenido})
    return chat


def fuentes_a_html(citas: list[str], detalle: dict) -> str:
    if not citas:
        return "<p><em>Esta respuesta no cita fuentes.</em></p>"
    bloques = []
    for etiqueta in citas:
        dato = detalle.get(etiqueta) or {}
        if etiqueta.startswith("F"):
            meta = dato.get("fuente", {})
            texto = dato.get("texto", "")
            bloques.append(
                f"<div class='fuente'><b>[{etiqueta}]</b> {html.escape(meta.get('title', meta.get('source', '')))}"
                f" · {html.escape(meta.get('section', ''))} <small>({html.escape(meta.get('source', ''))},"
                f" v{html.escape(str(meta.get('version', '')))})</small><br>{html.escape(texto[:600])}</div>")
        elif dato.get("tipo") == "archivo_generado":
            bloques.append(f"<div class='fuente'><b>[{etiqueta}]</b> Borrador escrito y verificado por Filesystem MCP:"
                           f" <code>{html.escape(dato.get('archivo', ''))}</code></div>")
        else:
            registro = dato.get("registro") or {}
            resumen = (f"{html.escape(registro.get('nombre', ''))} · estado <b>{html.escape(registro.get('estado', ''))}</b>"
                       f" · periodo {html.escape(registro.get('periodo', ''))}") if registro else "no encontrada"
            bloques.append(f"<div class='fuente'><b>[{etiqueta}]</b> MCP consultar_fuente_datos ·"
                           f" {html.escape(dato.get('codigo_fuente', ''))}: {resumen}"
                           f" <small>(datos ficticios)</small></div>")
    return "".join(bloques)


def ultimo_detalle(mensajes: list[dict]) -> str:
    for m in reversed(mensajes):
        if m["rol"] == "assistant":
            f = m.get("fuentes") or {}
            return fuentes_a_html(f.get("citas", []), f.get("detalle", {}))
    return "<p><em>Aún no hay respuestas en esta conversación.</em></p>"


def opciones(conversaciones: list[dict]) -> list[tuple[str, str]]:
    return [(c["titulo"], c["id"]) for c in conversaciones]


# --------------------------------------------------------------------------- interface

def construir_interfaz(recursos: sistema.Recursos) -> gr.Blocks:
    with gr.Blocks(title="Report Generator · Juliofi") as demo:
        sesion = gr.State(None, delete_callback=lambda s: s and s["ctx"].cerrar_sesion())
        conversacion = gr.State(None)
        pendiente = gr.State("")

        # login window ----------
        with gr.Column(visible=False, elem_id="modal-login") as modal_login:
            with gr.Column(elem_id="tarjeta-login"):
                gr.Markdown("## Inicia sesión\nPara responderte y guardar la conversación necesitamos tu cuenta.")
                correo = gr.Textbox(label="Correo", type="email", elem_id="correo")
                clave = gr.Textbox(label="Contraseña", type="password", elem_id="clave")
                boton_entrar = gr.Button("Entrar", variant="primary")
                boton_cancelar = gr.Button("Ahora no", elem_id="cancelar", size="sm")
                aviso_login = gr.Markdown(elem_id="aviso-login")

        # application ------------------------------------------------------------
        with gr.Row(equal_height=False, elem_id="app"):
            with gr.Column(scale=0, min_width=264, elem_id="lateral"):
                gr.Markdown("### Report Generator<span>.</span>", elem_id="marca")
                boton_nueva = gr.Button("Nueva conversación", elem_id="nueva")
                lista = gr.Radio(label="Recientes", choices=[], interactive=True, elem_id="lista")
                usuario_md = gr.HTML(SIN_SESION, elem_id="usuario")
                boton_abrir_login = gr.Button("Iniciar sesión", elem_id="abrir-login", size="sm")
                boton_salir = gr.Button("Cerrar sesión", elem_id="salir", size="sm", visible=False)
            with gr.Column(scale=1, elem_id="principal"):
                chat = gr.Chatbot(show_label=False, height="calc(100vh - 175px)", elem_id="chat",
                                  placeholder=SALUDO)
                entrada = gr.Textbox(show_label=False, placeholder="Escribe tu mensaje…", lines=1,
                                     max_lines=6, submit_btn=True, elem_id="entrada")
                with gr.Row(elem_id="extras"):
                    permiso = gr.Checkbox(
                        label="Guardar como borrador de informe",
                        value=False, interactive=recursos.informes_disponibles, elem_id="permiso",
                        info=None if recursos.informes_disponibles else "No disponible en este servidor.")
                    with gr.Accordion("Fuentes", open=False, elem_classes="detalle"):
                        fuentes = gr.HTML()
                    with gr.Accordion("Detalles técnicos", open=False, elem_classes="detalle"):
                        recorrido = gr.JSON(show_label=False)
                aviso = gr.Markdown(elem_id="aviso")
                borrador = gr.File(label="Borrador", visible=False, interactive=False)

        # handlers ----------------------------------------------------------
        async def entrar(email, password):
            vacio = (None, None, gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), "")
            try:
                ctx = await asyncio.to_thread(sistema.ContextoUsuario.iniciar_sesion, recursos, email, password)
            except (PermissionError, ValueError) as error:
                return vacio[:-1] + (f"{error}",)
            except Exception as error:  # network, supabase down, etc.
                return vacio[:-1] + (f"No pudimos conectar con Supabase ({type(error).__name__}).",)
            almacen = Almacenamiento(ctx.supabase, ctx.usuario_id)
            try:
                conversaciones = await asyncio.to_thread(almacen.listar_conversaciones)
                if not conversaciones:
                    conversaciones = [await asyncio.to_thread(almacen.crear_conversacion)]
                actual = conversaciones[0]["id"]
                mensajes = await asyncio.to_thread(almacen.cargar_mensajes, actual)
            except Exception as error:
                ctx.cerrar_sesion()
                detalle = ("falta la tabla de conversaciones; ejecuta sql/01_historial.sql en Supabase"
                           if "PGRST205" in str(error) else type(error).__name__)
                return vacio[:-1] + (f"Entraste, pero no pudimos abrir tu historial: {detalle}.",)
            avisos = " ".join(ctx.avisos)
            return ({"ctx": ctx, "almacen": almacen}, actual,
                    gr.update(visible=False), gr.update(visible=True),
                    tarjeta_usuario(ctx.email, avisos),
                    gr.update(choices=opciones(conversaciones), value=actual),
                    mensajes_a_chat(mensajes), ultimo_detalle(mensajes), "")

        def valida(texto) -> bool:
            return 0 < len((texto or "").strip()) <= 1200

        async def entrar_modal(email, password, texto_pendiente):
            r = await entrar(email, password)
            if r[0] is None:
                return (gr.update(),) * 7 + (r[-1], gr.update(), gr.update(), gr.update(), "")
            s, conversacion_id, _, _, usuario, lista_upd, chat_upd, fuentes_upd, _ = r
            if valida(texto_pendiente):
                conversacion_id, chat_upd = None, [{"role": "user", "content": texto_pendiente.strip()},
                                                   {"role": "assistant", "content": PENSANDO}]
                lista_upd = gr.update(choices=lista_upd["choices"], value=None)
                fuentes_upd = ultimo_detalle([])
            return (s, conversacion_id, gr.update(visible=False), usuario, lista_upd, chat_upd, fuentes_upd, "",
                    gr.update(visible=False), gr.update(visible=True), "", "")

        salidas_login = [sesion, conversacion, modal_login, usuario_md, lista, chat, fuentes, aviso_login,
                         boton_abrir_login, boton_salir, correo, clave]

        def abrir_ventana():
            return gr.update(visible=True), "", "", ""

        def cerrar_ventana(s, chat_actual):
            return gr.update(visible=False), "", (gr.update() if s else []), "", "", ""

        boton_abrir_login.click(abrir_ventana, None, [modal_login, aviso_login, correo, clave],
                                queue=False, show_progress="hidden")
        boton_cancelar.click(cerrar_ventana, [sesion, chat], [modal_login, pendiente, chat, aviso_login, correo, clave],
                             queue=False, show_progress="hidden")

        email_auto = os.environ.get("AUTO_LOGIN_EMAIL", "").strip()
        clave_auto = os.environ.get("AUTO_LOGIN_PASSWORD", "")
        if email_auto and clave_auto and os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1") == "127.0.0.1":
            async def entrar_auto():
                return await entrar_modal(email_auto, clave_auto, "")

            demo.load(entrar_auto, None, salidas_login, show_progress="hidden")

        async def nueva(s):
            if not s:
                return None, gr.update(), [], "", ""
            nueva_conv = await asyncio.to_thread(s["almacen"].crear_conversacion)
            conversaciones = await asyncio.to_thread(s["almacen"].listar_conversaciones)
            return (nueva_conv["id"], gr.update(choices=opciones(conversaciones), value=nueva_conv["id"]), [],
                    ultimo_detalle([]), "")

        boton_nueva.click(nueva, [sesion], [conversacion, lista, chat, fuentes, aviso], show_progress="hidden")

        async def abrir(s, conversacion_id):
            if not s or not conversacion_id:
                return gr.update(), gr.update(), gr.update(), ""
            try:
                mensajes = await asyncio.to_thread(s["almacen"].cargar_mensajes, conversacion_id)
            except AccesoDenegado as error:
                return None, [], "", f"{error}"
            return conversacion_id, mensajes_a_chat(mensajes), ultimo_detalle(mensajes), ""

        lista.input(abrir, [sesion, lista], [conversacion, chat, fuentes, aviso], show_progress="hidden")

        async def enviar(texto, permitir, s, conversacion_id):
            sin_cambio = (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(visible=False), gr.update())
            if not s:
                return ("",) + sin_cambio + ("Tu sesión terminó. Vuelve a iniciar sesión.",)
            texto = (texto or "").strip()
            if not texto:
                return ("",) + sin_cambio + ("Escribe una solicitud.",)
            if len(texto) > 1200:
                return (texto,) + sin_cambio + ("La solicitud supera 1200 caracteres.",)
            ctx, almacen = s["ctx"], s["almacen"]
            try:
                if not conversacion_id:
                    conversacion_id = (await asyncio.to_thread(almacen.crear_conversacion))["id"]
                previos = await asyncio.to_thread(almacen.cargar_mensajes, conversacion_id)
            except AccesoDenegado as error:
                return (texto,) + sin_cambio + (f"{error}",)
            except Exception as error:
                return (texto,) + sin_cambio + (f"No pudimos leer el historial ({type(error).__name__}).",)

            historial = historial_para_modelo(previos, sistema.MAX_TURNOS)
            traza = await sistema.atender(recursos, ctx, texto, historial, guardar_informe=bool(permitir))

            aviso_md = ""
            try:
                await asyncio.to_thread(almacen.guardar_turno, conversacion_id, texto, traza)
                mensajes = await asyncio.to_thread(almacen.cargar_mensajes, conversacion_id)
                conversaciones = await asyncio.to_thread(almacen.listar_conversaciones)
                lista_upd = gr.update(choices=opciones(conversaciones), value=conversacion_id)
                chat_upd = mensajes_a_chat(mensajes)
            except Exception as error:
                chat_upd = mensajes_a_chat(previos) + [{"role": "user", "content": texto},
                                                       {"role": "assistant", "content": traza["respuesta"]}]
                lista_upd = gr.update()
                aviso_md = f"La respuesta se generó pero **no se guardó** en Supabase ({type(error).__name__})."
            if traza["estado"] == "ERROR_TECNICO" and traza.get("tipo_error") in ("APIConnectionError", "APITimeoutError"):
                aviso_md += (" No hubo conexión con el modelo (Groq): suele ser el internet o el DNS de la red."
                             " Espera unos segundos y vuelve a enviar la pregunta.")
            elif traza["estado"] == "ERROR_TECNICO":
                aviso_md += " Revisa la conexión con Groq/Supabase o la cuota del modelo; esto no indica falta de evidencia."
            archivo = traza["archivos"][0] if traza["archivos"] else None
            resumen = {k: traza.get(k) for k in ("estado", "eventos", "operaciones", "duracion_ms",
                                                 "permiso_informe", "error_detalle", "tipo_error") if traza.get(k) is not None}
            return ("", conversacion_id, chat_upd, lista_upd,
                    fuentes_a_html(traza["citas"], traza["fuentes"]),
                    gr.update(value=archivo, visible=bool(archivo)), resumen, aviso_md.strip())

        def mostrar_pregunta(texto, chat_actual, s):
            if not valida(texto):
                return texto, gr.update(), gr.update(), gr.update()
            if not s:
                return texto, "", [{"role": "user", "content": texto.strip()}], gr.update(visible=True)
            return texto, "", (chat_actual or []) + [{"role": "user", "content": texto.strip()},
                                                     {"role": "assistant", "content": PENSANDO}], gr.update()

        async def responder(texto, permitir, s, conversacion_id, chat_actual):
            if not s or not valida(texto):
                return (gr.update(),) * 9
            salida = list(await enviar(texto, permitir, s, conversacion_id))
            if not isinstance(salida[2], list):
                salida[2] = (chat_actual or [])[:-2]
            return tuple(salida) + ("",)

        salidas_envio = [entrada, conversacion, chat, lista, fuentes, borrador, recorrido, aviso, pendiente]
        entrada.submit(mostrar_pregunta, [entrada, chat, sesion], [pendiente, entrada, chat, modal_login],
                       show_progress="hidden", queue=False).then(
            responder, [pendiente, permiso, sesion, conversacion, chat], salidas_envio, show_progress="hidden")

        for disparador in (boton_entrar.click, clave.submit):
            disparador(entrar_modal, [correo, clave, pendiente], salidas_login, show_progress="hidden").then(
                responder, [pendiente, permiso, sesion, conversacion, chat], salidas_envio, show_progress="hidden")

        def salir(s):
            if s:
                s["ctx"].cerrar_sesion()
            return (None, None, gr.update(choices=[], value=None), [], "", "", SIN_SESION,
                    gr.update(visible=True), gr.update(visible=False), "",
                    gr.update(value=None, visible=False), None, "", False, "")

        boton_salir.click(salir, [sesion], [sesion, conversacion, lista, chat, fuentes, clave, usuario_md,
                                            boton_abrir_login, boton_salir, pendiente,
                                            borrador, recorrido, aviso, permiso, correo], show_progress="hidden")

        def ocultar_borrador():
            return gr.update(value=None, visible=False), None

        boton_nueva.click(ocultar_borrador, None, [borrador, recorrido], queue=False, show_progress="hidden")
        lista.input(ocultar_borrador, None, [borrador, recorrido], queue=False, show_progress="hidden")
    return demo


def main() -> None:
    try:
        recursos = sistema.Recursos()
        asyncio.run(recursos.descubrir_mcp())
        asyncio.run(recursos.descubrir_archivos())
    except sistema.ErrorConfiguracion as error:
        raise SystemExit(f"Configuración incompleta: {error}") from None
    print("MCP propio:", recursos.catalogo_mcp["nombre"], "· protocolo", recursos.catalogo_mcp["protocolo"])
    print("Filesystem MCP:", "disponible" if recursos.mcp_existente.get("disponible") else "NO instalado (borradores desactivados)")
    demo = construir_interfaz(recursos)
    demo.queue(default_concurrency_limit=4)
    demo.launch(server_name=os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1"),
                server_port=int(os.environ.get("PORT", "7860")),
                css=CSS, js=JS, theme=TEMA, footer_links=[])


if __name__ == "__main__":
    main()
