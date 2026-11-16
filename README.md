# Report Generator - Equipo Juliofi

<img alt="ollama-tool" src="https://github.com/user-attachments/assets/7f8a29db-4182-4cc8-b304-b7f8e18d388d" />

Asistente web que ayuda a redactar **borradores de informe** a partir de dos tipos de evidencia: las reglas documentadas del equipo (RAG sobre Supabase) y el estado de fuentes de datos (consultado por MCP). Proyecto semestral de *Inteligencia Artificial Generativa y Sistemas Inteligentes*, EAM 2026-II.

> **Enlaces rápidos:** [Bitácora unificada](BITACORA_PROYECTO.md) - [Presentación](app/presentacion_proyecto.html) - [Evidencias](evidencias/)

## Problema, usuarios y alcance

Quien prepara informes periódicos (ejecutivo, técnico) debe combinar reglas de redacción con datos que a veces llegan incompletos, desactualizados o sin alguna métrica. Report Generator responde preguntas sobre esas reglas citando el fragmento exacto, consulta el estado de una fuente y, con permiso explícito, guarda un borrador con sus fuentes para que una persona lo revise.

- **Usuarios:** analistas que redactan informes y revisores que los aprueban.
- **Resultado:** respuesta con citas `[F#]` a los documentos, `[T#]` a resultados de herramientas, y opcionalmente un archivo `.md` de borrador verificado.
- **Fuera de alcance:** modificar fuentes o documentos, enviar informes, aprobar, estimar cifras ausentes. El agente rechaza esas solicitudes y no existe ninguna herramienta que pueda ejecutarlas.
- **Revisión humana:** todo borrador es un insumo para revisión; las marcas `[DATO AUSENTE]` y `[DATO INCOMPLETO]` nunca se sustituyen por estimaciones.
- **Datos de la demostración:** corpus propio y ficticio (`tipos_de_informe.md`, `reglas_de_borrador.md`, versión `1.0-ficticia`, 6 fragmentos) y tres fuentes ficticias `DS-1001`, `DS-1002`, `DS-1003`. No corresponden a ninguna empresa ni sistema real.

## Arquitectura y procedencia del código

```text
Navegador ──► app.py (Gradio)
               │  login Supabase Auth ─► ContextoUsuario (cliente propio de la persona)
               │  lee historial ───────► almacenamiento.py ─► Supabase: conversaciones / mensajes (RLS)
               ▼
            sistema.atender()  ── agente: hasta 3 decisiones y 2 operaciones, 90 s
               ├─ decidir() ───────────► Groq openai/gpt-oss-20b, salida JSON validada con Pydantic
               ├─ buscar_documentos ───► embeddings MiniLM (local) + RPC app_buscar_fragmentos (Supabase, RLS)
               ├─ consultar_fuente ────► servidor_mcp.py (MCP propio, stdio, solo lectura)
               └─ guardar_informe ─────► Filesystem MCP 2.2.0 (stdio, confinado a la carpeta del usuario)
               ▼
            app.py guarda pregunta + respuesta + fuentes + traza ─► almacenamiento.py ─► Supabase
```

**Recorrido de una pregunta.** La persona escribe en Gradio. `app.py` relee de Supabase los mensajes de la conversación activa (comprobando el propietario) y toma los últimos 4 turnos como contexto. `sistema.atender` pide al modelo una decisión estructurada; el programa la valida (acción permitida, códigos DS aportados por el usuario, citas existentes, permiso de escritura) y ejecuta la operación. Cada resultado vuelve al modelo como observación etiquetada. Al terminar, `app.py` persiste el turno y muestra respuesta, fuentes, recorrido y, si existe, el borrador.

**Conservación de fuentes y validaciones.** Cada fragmento conserva `source`, `section`, `version` y `source_hash`. `buscar_documentos` verifica que lo devuelto por la búsqueda coincida exactamente con el corpus cargado al iniciar sesión. Las citas de la respuesta deben corresponder a resultados de ese mismo turno. Los borradores se escriben con nombre aleatorio asignado por el programa y se releen por MCP para verificar su contenido antes de confirmarlos.

| Archivo | Responsabilidad | Origen en el notebook de la Clase 11 |
|---|---|---|
| `app/app.py` | Interfaz: login, conversaciones, chat, fuentes, recorrido, descarga del borrador. | Punto 7 (entrada) y `mostrar()` |
| `app/sistema.py` | Configuración, RAG, clientes MCP, contrato `Decision`, validaciones, agente `atender()`. | Puntos 2, 3, 4, 4.b, 5 y 6 |
| `app/almacenamiento.py` | Crear/listar conversaciones, cargar mensajes, guardar turnos; comprueba propietario. | Sustituye `MEMORIA` del punto 5 |
| `app/servidor_mcp.py` | MCP propio: `consultar_fuente_datos` (solo lectura, datos ficticios). | Texto `SERVIDOR_MCP` del punto 4 |
| `app/preparar_mcp.py` | Instala Filesystem MCP una vez (fuera de la atención de preguntas). | Punto 4.b |
| `app/config_corpus.json` | Corpus, modelo, revisión de embeddings y recuperación vigentes (sin secretos). | Sustituye `files.upload` del JSON de la Clase 09 |
| `app/sql/01_historial.sql` | Tablas `conversaciones` y `mensajes` con RLS. | Nuevo |
| `app/sql/02_corpus_compartido.sql` | Lectura autorizada del corpus y RPC `app_buscar_fragmentos`. | Nuevo (adapta la Clase 08) |
| `app/tests/test_controles.py` | Pruebas locales sin Groq ni Supabase. | Punto 8 |
| `app/pruebas_rls.py` | Persistencia y aislamiento con dos usuarios reales. | Nuevo |

Lo que se conserva del historial: **todos** los mensajes (pregunta, respuesta, estado, fuentes citadas y una traza resumida). Lo que va al modelo: solo los últimos `MAX_TURNOS = 4` turnos completos, porque la memoria sirve para resolver referencias como "esa fuente", no como evidencia.

## Requisitos

- **Python 3.12** (probado con 3.12.3 en Linux; el notebook usó 3.12 en Colab). `asyncio.timeout` exige 3.11 o superior.
- Dependencias en [`app/requirements.txt`](requirements.txt). Versiones fijadas de la Clase 11 más `gradio==6.32.0` y `python-dotenv==1.2.1`. `torch` se instala desde el índice solo-CPU de PyTorch.
- **Groq:** una API key con acceso a `openai/gpt-oss-20b`.
- **Supabase:** el mismo proyecto de la Clase 08 con el corpus `report_generator-ff98b1398c56` en `clase08_fragmentos`, usuarios en Auth y las tablas de historial de `app/sql/`. SQLite no se usa.
- **Node:** no hace falta instalarlo. Filesystem MCP corre con el Node 24 que trae `nodejs-wheel`.
- **Memoria:** el modelo de embeddings (~470 MB en disco) se descarga de Hugging Face la primera vez; la aplicación ocupa del orden de 0,8-1 GB de RAM en ejecución.

## Instalación desde un clon limpio

PowerShell, desde una carpeta donde podamos clonar:

```powershell
git clone https://github.com/sophie-muriel/report-generator
cd report-generator
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r app/requirements.txt
Copy-Item app/.env.ejemplo app/.env
cd app
..\.venv\Scripts\python.exe preparar_mcp.py
```

Linux/macOS: `python3 -m venv .venv`, `.venv/bin/python -m pip install -r app/requirements.txt`, `cp app/.env.ejemplo app/.env`, y desde `app/`: `../.venv/bin/python preparar_mcp.py`.

## Variables y secretos

`app.py` carga `app/.env` con `python-dotenv`. Solo se publica `app/.env.ejemplo`.

| Variable | Uso | ¿Obligatoria? |
|---|---|---|
| `GROQ_API_KEY` | Clave de Groq. | Sí |
| `GROQ_MODEL` | Modelo generativo. Por defecto `openai/gpt-oss-20b`, el probado. | No |
| `SUPABASE_URL` | Project URL (`https://xxxx.supabase.co`). | Sí |
| `SUPABASE_PUBLISHABLE_KEY` | Clave publicable `sb_publishable_...`. La app rechaza cualquier otra. No identifica a nadie: la identidad sale del login. | Sí |
| `CORPUS_PROPIETARIO_ID` | UUID del usuario que cargó el corpus en la Clase 08. No es secreto. | Sí |
| `GRADIO_SERVER_NAME` | `127.0.0.1` (por defecto, ejecución local). | No |
| `PORT` | Puerto HTTP. Por defecto `7860`. | No |
| `INFORMES_DIR`, `LOGS_DIR` | Carpetas de borradores y registros MCP. Por defecto `app/informes_generados` y `app/logs`. | No |

No usamos `MCP_URL`: ambos servidores MCP se inician como subprocesos por **stdio** dentro del mismo entorno. No hay contraseñas de usuarios en `.env`: cada persona inicia sesión con su cuenta de Supabase Auth. Nunca se usa la clave `service_role`/secret.

## Preparación del corpus y de los datos

El corpus **ya está** en Supabase desde la Clase 08 y no se vuelve a insertar. La aplicación solo lo lee.

- **Documentos:** `tipos_de_informe.md` y `reglas_de_borrador.md` (redactados por el equipo, ficticios, compartibles), versión `1.0-ficticia`. Huella del corpus `ff98b1398c56`.
- **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, revisión `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`, dimensión 384, normalizados, similitud coseno.
- **Fragmentación:** por párrafos, máximo 128 tokens, solapamiento 12 → 6 fragmentos.
- **Recuperación:** opción **A (semántica)**, M = 10 candidatos, K = 3 pasajes. En la Clase 09, A, B (híbrida RRF) y C (híbrida + reranking) empataron en los cuatro casos de desarrollo; elegimos A por simple y barata. B queda disponible cambiando `recuperacion.opcion` en `config_corpus.json`.

**Una sola vez:** ejecutar `app/sql/01_historial.sql` y `app/sql/02_corpus_compartido.sql` en el SQL Editor, autorizar lectores (ver abajo) y ejecutar `preparar_mcp.py`.
**En cada inicio de sesión:** se leen los 6 fragmentos visibles para esa persona y se construye su índice BM25 en memoria.
**En cada pregunta:** se calcula el embedding de la consulta localmente y se llama a la RPC `app_buscar_fragmentos`.

**Quién puede leer el corpus.** La política de la Clase 08 (`owner_id = auth.uid()`) solo deja leer al propietario. `02_corpus_compartido.sql` crea la tabla `app_lectores_corpus` y una política SELECT adicional: el propietario autoriza explícitamente qué usuarios pueden **leer** su corpus. No concede escritura, no desactiva RLS y no afecta la privacidad del historial. La RPC es `SECURITY INVOKER`, así que respeta el RLS de quien pregunta.

> Si en el esquema de la Clase 08 la columna vectorial no se llama `embedding`, cambiar las dos líneas marcadas en `02_corpus_compartido.sql`.

## Usuarios e historiales

1. **Crear usuarios de prueba:** Supabase → Authentication → Users → *Add user* → *Create new user*, con correo y contraseña, marcando *Auto Confirm User*. Crear al menos dos (A y B). Las contraseñas no se guardan en el repositorio.
2. **Autorizar su lectura del corpus** (SQL Editor, sustituyendo correos):

   ```sql
   insert into public.app_lectores_corpus (corpus_id, propietario_id, lector_id)
   select 'report_generator-ff98b1398c56', p.id, l.id
   from auth.users p, auth.users l
   where p.email = 'PROPIETARIO@ejemplo.com'
     and l.email in ('usuarioA@ejemplo.com', 'usuarioB@ejemplo.com')
   on conflict do nothing;
   ```

3. **Tablas** (`01_historial.sql`):
   - `conversaciones(id uuid, usuario_id → auth.users, titulo, creada_en, actualizada_en)`.
   - `mensajes(id bigint identity, conversacion_id, usuario_id, rol user|assistant, contenido, estado, fuentes jsonb, traza jsonb, creado_en)`. El `id` incremental da el orden estable.
4. **Políticas RLS:** una conversación solo se lee, crea o renombra si `usuario_id = auth.uid()`. Un mensaje solo se lee o inserta si su conversación pertenece a `auth.uid()`. No hay política DELETE: crear una conversación nueva no borra nada. `anon` no tiene permisos.
5. **Recuperación:** al iniciar sesión se listan las conversaciones de la persona y se abre la más reciente. Al refrescar el navegador, cerrar sesión o reiniciar el servidor, los datos siguen en Supabase y se recuperan con el siguiente login.

Cada sesión de Gradio crea su **propio** cliente de Supabase (`ContextoUsuario`), autenticado con la cuenta de esa persona; no existe un cliente global. `gr.State` solo guarda qué sesión y qué conversación están activas en ese navegador.

## Configuración del MCP

| | MCP propio | MCP ya construido |
|---|---|---|
| Nombre | Fuentes de datos Report Generator | `@modelcontextprotocol/server-filesystem` |
| Procedencia | `app/servidor_mcp.py` (equipo) | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) |
| Versión | SDK `mcp==2.3.0` | `2.2.0` sobre Node `24.19.0` (`nodejs-wheel`) |
| Transporte | stdio (subproceso) | stdio (subproceso) |
| Herramientas habilitadas | `consultar_fuente_datos` | `write_file`, `read_text_file` (de 16 descubiertas) |
| Arranque | Lo inicia `sistema.py` en cada consulta | Lo inicia `sistema.py` con `--confine-roots <carpeta del usuario>` |

- **Qué solicitud lo usa:** "¿Cómo está la fuente DS-1001?" invoca el MCP propio; "¿Qué partes tiene un informe ejecutivo? Guarda un informe..." con la casilla de permiso activada usa RAG y luego Filesystem MCP.
- **Evidencia de ejecución:** la etiqueta `[T#]` en la respuesta, el panel "Recorrido del agente", el campo `traza` del mensaje en Supabase y `app/logs/mcp_*.log`.
- **Aprobación humana:** escribir un borrador exige que la persona marque la casilla en ese turno **y** que haya citas documentales del mismo turno; el programa lo comprueba aunque el modelo proponga otra cosa. La ruta la asigna el programa (nombre aleatorio), nunca el modelo.
- **Errores y duplicados:** un código inexistente devuelve `encontrada: false` (no es error técnico); un argumento inválido es rechazado por el servidor; una operación idéntica repetida detiene el turno (`REPETICION_SIN_AVANCE`); no hay reintentos automáticos (`max_retries=0`).
- **Aislamiento:** al iniciar, la app comprueba que Filesystem MCP rechaza leer fuera de su carpeta; cada usuario escribe en `informes_generados/<su UUID>/`.

## Ejecución local

Desde la raíz clonada, con `.env` completo y el SQL aplicado:

```powershell
cd app
..\.venv\Scripts\python.exe app.py
```

Linux/macOS: desde `app/`, `../.venv/bin/python app.py`. Abrir **http://127.0.0.1:7860**. La primera ejecución descarga el modelo de embeddings. Detener con `Ctrl+C`. Los servidores MCP no se inician por separado.

## Pruebas y resultados observados

**Automáticas locales** (sin Groq ni Supabase): desde `app/`, `python -m pytest -q`. Levantan los dos servidores MCP reales.

**Aislamiento con Supabase real:** desde `app/`, `python pruebas_rls.py` (pide correo y contraseña de A y B por teclado, deja JSON en `evidencias/`).

| # | Entrada / acción | Ruta esperada | Resultado observado | Evidencia | Estado |
|---|---|---|---|---|---|
| 1 | Pruebas locales `pytest` | 18 pruebas: MCP propio, Filesystem confinado, contratos, límites, almacenamiento | 18/18 aprobadas | salida de pytest (2026-11-15, 18 passed in 3.95 s) | Aprobado |
| 2 | "¿Qué partes debe tener un informe ejecutivo y qué se escribe si falta una métrica? Guarda un informe..." con permiso | `buscar_documentos` → `guardar_informe` → `RESPUESTA_DEL_PROGRAMA` | `RESPONDER`, citas F1-F3 + T1, borrador verificado con `[DATO AUSENTE]` y la negación de estimación | `evidencias/Clase_11_Evidencia_Integracion_ReportGenerator.json`; captura `evidencias/capturas/evidencia-1.png` (2026-11-15) | Aprobado en app |
| 3 | La misma pregunta sin permiso | No guarda ni dice que guardó | "Solicitud rechazada": no crea archivo ni afirma haber guardado | captura `evidencias/capturas/evidencia-2.png` (2026-11-15) | Aprobado |
| 4 | "¿Qué colores y logotipo debe llevar el informe? Guarda un informe" (sin evidencia) | `ACLARAR`, sin archivo | `Aclaración`: "No dispongo de información sobre los colores y el logotipo...". Sin archivo. Nota: con la casilla desmarcada la app rechaza antes ("opción deshabilitada"), por eso se marcó el permiso para llegar a la aclaración | captura `evidencias/capturas/evidencia-3.png` (2026-11-15) | Aprobado |
| 5 | "¿Cómo está la fuente?" en conversación nueva (incompleta) | Pide el código | `Aclaración`: "indique el código de la fuente de datos (formato DS-XXXX)" | captura `evidencias/capturas/evidencia-4.png` (2026-11-15) | Aprobado |
| 6 | "¿Cómo está la fuente DS-1001?" (herramienta autorizada) | MCP propio, `[T1]`, `margen_bruto` ausente | Periodo 2026-10, ingresos/unidades/ticket con valores, "la métrica margen bruto está ausente" | captura `evidencias/capturas/evidencia-5.png` (2026-11-15) | Aprobado |
| 7 | "Actualiza DS-1003 y envía el informe al gerente" (prohibida) | `RECHAZAR` | Bloqueada por los controles del programa ("Control no superado"): sin operaciones, sin archivo y sin tocar la fuente. Observación: en vez del mensaje explicativo de `RECHAZAR` aparece el estado genérico de control (limitación B7 del Corte 3, en mejoras pendientes) | captura `evidencias/capturas/evidencia-6.png` (2026-11-15) | Aprobado con observación |
| 8 | GROQ_API_KEY inválida (falla técnica controlada) | `ERROR_TECNICO`, aviso de conexión, sin afirmar falta de evidencia | `Error técnico` + aviso: "Revisa la conexión con Groq/Supabase o la cuota del modelo; esto no indica falta de evidencia" | captura `evidencias/capturas/evidencia-7.png` (2026-11-15) | Aprobado |
| 9 | Dos usuarios, dos conversaciones de A, recuperación tras nueva sesión | A recupera ambas | 9/9 aprobados: A guarda en 2 conversaciones y recupera ambas con un cliente nuevo | `pruebas_rls.py`; `evidencias/pruebas_rls_20261115_192750.json` | Aprobado |
| 10 | B lee / inserta en conversación de A conociendo el UUID | 0 filas / rechazado | 0 filas en lecturas; `APIError` en los dos intentos de inserción; `AccesoDenegado` vía `almacenamiento.py`; conversación de A intacta. En la UI, B solo ve sus propias conversaciones (historiales claramente distintos) | mismo JSON; captura `evidencias/capturas/evidencia-9.png` | Aprobado |
| 11 | Reiniciar la app y volver a entrar | Conversaciones intactas | Tras reiniciar el servidor y volver a iniciar sesión, todas las conversaciones y su historial están en la lista y se abren completas | captura `evidencias/capturas/evidencia-8.png` (2026-11-15) | Aprobado |
| 12 | Clon limpio + instalación en otra máquina | La app abre y responde | Clon limpio en la máquina de una integrante (y de otra persona): instalación desde el README, `preparar_mcp.py`, `app.py` y la app responde | verificación en equipo (2026-11-15) | Aprobado |

Los casos 3-8 se toman de la tabla y la batería B1-B8 del notebook de la Clase 11. No marcamos como aprobado nada que no se haya ejecutado.

## Seguridad, problemas frecuentes y limitaciones

**Seguridad.** Secretos solo en `app/.env` (ignorado por Git). La app rechaza claves que no sean publicables. RLS protege historial y corpus; `almacenamiento.py` además comprueba el propietario y valida el formato UUID. Los borradores se escriben en una carpeta por usuario y Filesystem MCP está confinado a ella. Si una clave llega al repositorio: revocarla en Groq/Supabase, rotarla y limpiar el historial de Git; el `.gitignore` no la retira.

| Síntoma | Qué revisar |
|---|---|
| `Configuración incompleta: Falta la variable...` al arrancar | `app/.env` existe en `app/` y tiene esa variable. |
| "No pudimos iniciar sesión" | Usuario creado y confirmado en Auth; correo y contraseña. |
| "Tu usuario no tiene acceso al corpus" | Falta la fila en `app_lectores_corpus` o `CORPUS_PROPIETARIO_ID` es incorrecto. |
| `ERROR_VALIDACION` "Revisa la función app_buscar_fragmentos" | `02_corpus_compartido.sql` no se ejecutó o la columna vectorial tiene otro nombre. |
| `ERROR_TECNICO` | Groq (clave, cuota, disponibilidad del modelo) o red. No significa que falten documentos. |
| Casilla de borrador desactivada | No se ejecutó `preparar_mcp.py`. |

**Limitaciones conocidas.**
- Presupuesto de 2 operaciones por turno: un borrador que necesite reglas + datos de una fuente + escritura (3 operaciones) termina en `LIMITE_OPERACIONES`. Lo mantenemos y lo registramos en lugar de ampliar el límite sin pruebas nuevas.
- Contexto: 4 turnos y 24 000 caracteres por decisión; respuestas de hasta 2 500 caracteres.
- Una cita válida solo prueba que corresponde a un resultado del turno; la fidelidad requiere revisión humana.
- Los borradores en disco viven en `app/informes_generados/`; el texto también queda en el mensaje persistido en Supabase.
- Latencia: en Colab un turno con RAG + escritura tardó ~3,3 s; en la app falta medirlo.
- La sesión de Supabase se renueva automáticamente mientras el servidor sigue activo; si el token expira sin renovarse, hay que volver a iniciar sesión.

## Presentación y evidencias

- Presentación: [`app/presentacion_proyecto.html`](app/presentacion_proyecto.html)
- Evidencias compartibles: [`evidencias/`](evidencias/) (JSON de la Clase 11, salidas de `pruebas_rls.py`, capturas de la app).
- Notebook consolidado: [`notebooks/C11_RAG_Agente_MCP.ipynb`](C11_RAG_Agente_MCP.ipynb)
- Bitácora: [`BITACORA_PROYECTO.md`](BITACORA_PROYECTO.md)

## Bitácora unificada del proyecto

[`BITACORA_PROYECTO.md`](BITACORA_PROYECTO.md) documenta los tres cortes: problema y alcance, arquitectura, decisiones, experimentos y pruebas con resultados, errores y correcciones, limitaciones y aportes. Las evidencias se enlazan con rutas relativas del repositorio.

## Equipo y referencias

| Integrante | Responsabilidad |
|---|---|
| Juliana Marín Vélez | Notebooks de los tres cortes, redacción del corpus, configuración de Supabase (corpus, Auth, SQL y RLS), prompts, lógica del sistema (`sistema.py`, `servidor_mcp.py`, agentes y validaciones) y arquitectura de `app/`. |
| Sophie Rosero Muriel | Soporte y verificación de notebooks, pruebas y matriz de evaluación (Clases 08, 09 y 11), gestión del repositorio, bitácora y documentación, pruebas de la aplicación (`test_controles.py`, `pruebas_rls.py`) y revisión manual de borradores. |

Datos: corpus y fuentes ficticias redactados por el equipo Juliofi. Modelo de embeddings bajo la licencia publicada en su ficha de Hugging Face. Filesystem MCP: licencia del repositorio `modelcontextprotocol/servers`.

- Gradio: [estado de sesión](https://www.gradio.app/guides/state-in-blocks) - Supabase: [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security), [Auth con contraseña](https://supabase.com/docs/reference/python/auth-signinwithpassword), [RPC](https://supabase.com/docs/reference/python/rpc)
- MCP Python SDK: [cliente](https://py.sdk.modelcontextprotocol.io/client/) - Groq: [Structured Outputs](https://console.groq.com/docs/structured-outputs) - [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) - [Kotaemon](https://github.com/Cinnamon/kotaemon) (referencia de clase)
