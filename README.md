> ⚠️ **ESTE PROYECTO ESTÁ EN DESARROLLO Y SU CONTENIDO/README SE ACTUALIZARÁ DE MANERA PERIÓDICA**
 
---
# Report Generator (Generador de Informes con IA)

<img alt="ollama-tool" src="https://github.com/user-attachments/assets/7f8a29db-4182-4cc8-b304-b7f8e18d388d" />


> **Prototipo Generativo con Control de Estructura, *Tool Calling*, Validación de Fuentes, Búsqueda Semántica, *Embeddings*, Fragmentación, Indexación, RAG, Evaluación de la Recuperación y Agente con MCP**  
> 
> Proyecto final desarrollado para el docente Rober Erick García para la asignatura Electiva VI, Periodo 2026-II, en la Institución Universitaria EAM.

## Equipo de Trabajo (Juliofi~)

* **Juliana Marín Vélez:** Elaboración y ejecución de notebooks.
* **Sophie Rosero Muriel:** Soporte técnico en notebooks, verificación de pruebas y registro continuo en bitácoras.

---
## Estructura del Repositorio

```text
report-generator/
├── .obsidian/               # Configuración del vault de Obsidian
├── images/                  # Capturas de pantalla y evidencias de ejecución
├── logs/                    # Bitácoras de clase en Markdown (C02, C03, C04, C06, C07, C08, C09, C11)
│   ├── C02_2026-08-26_Tokens.md
│   ├── C03_2026-09-08_PromptV1.md
│   ├── C04_2026-09-13_Herramientas.md
│   ├── C06_2026-10-05_Busqueda_Semantica.md
│   ├── C07_2026-10-07_Ingestion_Indice.md
│   ├── C08_2026-10-11_RAG.md
│   ├── C09_2026-10-23_Evaluacion_RAG.md
│   ├── C11_AAAA-MM-DD_Agente_MCP.md
│   └── Plantilla_Bitacora.md
├── notebooks/               # Notebooks ejecutables en Google Colab y sus evidencias
│   ├── C02_Report_Generation_Tokens.ipynb
│   ├── C03_Demo_Colab_Groq.ipynb
│   ├── C04_Herramientas.ipynb
│   ├── C06_Busqueda_Semantica.ipynb
│   ├── C07_Ingestion_Indice.ipynb
│   ├── C08_RAG.ipynb
│   ├── C09_Evaluacion_RAG.ipynb
│   ├── C11_RAG_Agente_MCP_ReportGenerator.ipynb
│   ├── Clase_07_Indice_y_Corpus.zip
│   ├── Clase_08_Matriz_Pruebas_ReportGenerator.csv
│   ├── Clase_08_Evidencia_RAG_ReportGenerator.json
│   ├── Clase_09_Evidencia_Evaluacion_RAG_ReportGenerator.zip
│   └── Clase_11_Evidencia_Integracion_ReportGenerator.json
├── presentations/           # Presentaciones finales
│   ├── presentacion-corte1-juliofi.html
│   └── presentacion-corte1-juliofi.pdf
└── prompts/                 # Especificaciones y versiones del prompt del sistema
    ├── SYSTEM_PROMPT_V1
    ├── SYSTEM_PROMPT_V2
    └── SYSTEM_PROMPT_V3
```

## Descripción del Proyecto

*Report Generator* es un sistema inteligente diseñado para automatizar la construcción de borradores de informes empresariales (ejecutivos, técnicos, resúmenes periódicos y generales) garantizando rigor factual, trazabilidad y control estricto sobre los datos.

### El Problema

En el entorno corporativo, los informes internos suelen elaborarse manualmente consolidando métricas de diversas fuentes. El riesgo más crítico no radica en la redacción, sino en publicar un informe basado en datos inexistentes o periodos aún no cerrados. 

### La Solución

Para resolver este problema, *Report Generator* opera como un asistente de solo lectura que:

1. **Clasifica y valida solicitudes:** Parsea peticiones en lenguaje natural a esquemas JSON estrictos mediante Pydantic.
2. **Consulta fuentes registradas:** Invoca herramientas de *Tool Calling* para validar la disponibilidad real de datos en un catálogo de fuentes (`DS-0000`).
3. **Genera borradores auditables:** Redacta plantillas de informes señalando explícitamente cualquier vacío mediante las etiquetas `[DATO AUSENTE]` y `[DATO INCOMPLETO]`, sin inventar cifras ni asumir métricas no confirmadas.
4. **Responde preguntas sobre sus propias reglas con RAG:** Recupera fragmentos de documentos propios mediante *embeddings* y similitud coseno, guardados en Supabase Vector, y genera con Groq una respuesta validada con Pydantic que cita sus fuentes o declara que la evidencia no alcanza. Explica procedimientos (tipos de informe, reglas de borrador); el estado y las fechas de una fuente `DS-0000` siguen viniendo de `consultar_fuente_datos`. La recuperación se evaluó frente a alternativas híbridas y con reranking (Clase 9) y se conservó la búsqueda semántica.
5. **Coordina las capacidades con un agente y MCP (en desarrollo):** Desde una misma entrada, un agente decide si consulta las reglas (RAG), el estado de una fuente (`consultar_fuente_datos`, publicada como servidor MCP propio) o si guarda un borrador de informe mediante Filesystem MCP, solo con evidencia documental del turno y permiso explícito. Conserva los últimos cuatro turnos de cada conversación.

## Evolución del Proyecto por Sesiones

El proyecto ha evolucionado de forma incremental a través de los laboratorios aplicados:

### 1. Análisis de Tokens, Contexto e Inferencia (`Clase 2`)

* **Notebook:** `notebooks/C02_Report_Generation_Tokens.ipynb`
* **Bitácora:** `logs/C02_2026-08-26_Tokens.md`
* **Enfoque:** Evaluación experimental de la tokenización, latencia y variabilidad de respuestas en un modelo local (`gemma4:e2b` en Ollama) variando la temperatura (0.0, 0.7, 1.2 / 0.8, 1.7, 2.2).
* **Decisión:** Justificación de temperaturas bajas para la generación controlada de reportes y estructuración de contexto mínimo.

### 2. Prompts Versionados y Salidas Estructuradas (`Clase 3`)

* **Notebook:** `notebooks/C03_Demo_Colab_Groq.ipynb`
* **Bitácora:** `logs/C03_2026-09-08_PromptV1.md`
* **Prompt del Sistema:** `prompts/SYSTEM_PROMPT_V1`
* **Enfoque:** Conexión a la API de Groq (`openai/gpt-oss-20b`) con *Structured Outputs*.
* **Contrato de Salida:** Definición de la clase `Solicitud` en Pydantic (`tipo_reporte`: *ejecutivo, tecnico, resumen_periodico, general*, `prioridad`, `resumen`, `datos_faltantes`, `requiere_humano`, `confianza`).
* **Evaluación:** Evaluación de 5 casos de prueba (normal, ambiguo, incompleto, malicioso y fuera de alcance) utilizando Pydantic como barrera de seguridad ante salidas inválidas.

### 3. *Tool Calling* y Control de Consistencia (`Clase 4`)

* **Notebook:** `notebooks/C04_Herramientas.ipynb`
* **Bitácora:** `logs/C04_2026-09-13_Herramientas.md`
* **Prompt del Sistema:** `prompts/SYSTEM_PROMPT_V2`
* **Enfoque:** Integración de la herramienta de solo lectura `consultar_fuente_datos` sobre un catálogo ficticio de fuentes de datos (`DS-1001`, `DS-1002`, `DS-1003`).
* **Segunda Barrera Pydantic:** Validación de argumentos (`ArgumentosFuente`) exigiendo el patrón `DS-0000` y comprobando que el código citado aparezca literalmente en la entrada del usuario.
* **Algoritmo Determinista:** Reconocimiento de métricas con vocabulario cerrado, contraste entre métricas solicitadas vs. disponibles y redacción de borradores no verificados con advertencias explícitas de ausencia.

### 4. Embeddings y Búsqueda Semántica (`Clase 6`)

* **Notebook:** `notebooks/C06_Busqueda_Semantica.ipynb`
* **Bitácora:** `logs/C06_2026-10-05_Busqueda_Semantica.md`
* **Enfoque:** Seis pasajes ficticios (informe ejecutivo, técnico, resumen periódico, catálogo de fuentes, datos incompletos y alcance del servicio) se convierten en vectores con `paraphrase-multilingual-MiniLM-L12-v2`; las consultas se ordenan por similitud coseno (`K = 3`).
* **Batería de pruebas:** Cinco casos con el pasaje esperado escrito antes de ejecutar (paráfrasis, coincidencia exacta, pregunta incompleta, dato que vive en la fuente y pregunta fuera de cobertura). En los cuatro casos con respuesta el pasaje esperado quedó primero.
* **Hallazgo:** Siempre existe un "más cercano" aunque ningún pasaje responda (la pregunta fuera de cobertura devolvió P3 con 0.345), por lo que no se fijó un umbral automático y se exige leer el texto recuperado. Los datos que cambian (p. ej. la última actualización de `DS-1001`) siguen consultándose con `consultar_fuente_datos`.
* **Alcance:** Solo recupera pasajes; no genera respuestas con ellos ni procesa documentos reales.

### 5. Ingesta de Documentos, Fragmentación e Índice (`Clase 7`)

* **Notebook:** `notebooks/C07_Ingestion_Indice.ipynb`
* **Bitácora:** `logs/C07_2026-10-07_Ingestion_Indice.md`
* **Índice y corpus:** `notebooks/Clase_07_Indice_y_Corpus.zip`
* **Enfoque:** Dos documentos propios y ficticios (`tipos_de_informe.md` y `reglas_de_borrador.md`) con título, versión `1.0-ficticia`, origen y huella SHA-256. Se limpian sin tocar párrafos ni condiciones y se fragmentan con dos estrategias: *ventanas* (por tokens, con solapamiento de 12) y *párrafos* (respeta sus límites y solo divide los que no caben). Cada fragmento incluye título y sección, no supera los 128 tokens del modelo y conserva archivo, sección, versión y huella para volver a la fuente.
* **Comparación:** Cuatro preguntas con evidencia esperada escrita antes de ejecutar (condición y consecuencia, paráfrasis, dato que vive en la fuente y pregunta fuera de cobertura). Con 128 tokens las dos estrategias solo se separan en la sección del informe ejecutivo, así que se eligió *párrafos* sin darla por demostrada como mejor.
* **Índice:** Se guardan vectores, registros y configuración, se vuelven a cargar sin recalcular y se comprueba con `assert` que devuelven los mismos fragmentos y puntajes.
* **Hallazgo:** La condición de una regla (`[DATO INCOMPLETO]`) y su consecuencia ("no se presenta como verificada") quedaron en fragmentos distintos en ambas estrategias, y el fragmento con la consecuencia empató con uno que no respondía la pregunta (0.589). Con un `K` pequeño habría quedado fuera.
* **Alcance:** Solo recupera fragmentos; no genera respuestas con ellos ni procesa documentos reales.

### 6. RAG con Supabase Vector y Groq (`Clase 8`)

* **Notebook:** `notebooks/C08_RAG.ipynb`
* **Bitácora:** `logs/C08_2026-10-11_RAG.md`
* **Prompt del Sistema:** `prompts/SYSTEM_PROMPT_V3` (`rag_report_v3`)
* **Evidencias:** `notebooks/Clase_08_Matriz_Pruebas_ReportGenerator.csv` y `notebooks/Clase_08_Evidencia_RAG_ReportGenerator.json`
* **Enfoque:** Los 6 fragmentos del índice de la clase 7 (estrategia *párrafos*, huella `ff98b1398c56`) se cargan con `upsert` en la tabla `clase08_fragmentos` de Supabase (pgvector, con RLS por usuario) sin volver a fragmentar ni recalcular vectores. La consulta se recupera con la función `clase08_buscar_fragmentos` (coseno, `K = 3`) y los pasajes se envían a Groq (`openai/gpt-oss-20b`, `temperature=0`) con salida estructurada.
* **Contrato de Salida:** Clase `RespuestaRAG` con cuatro estados (`respondida`, `parcial`, `aclaracion`, `evidencia_insuficiente`), `respuesta` con etiquetas `[F#]` al final de cada oración, `citas` y `limitacion`. Un validador comprueba que las citas existan, coincidan con las etiquetas del texto y que los estados no respondidos expliquen su límite; solo se muestran respuestas que lo pasan.
* **Persistencia:** Un segundo cliente inicia sesión y recupera los mismos fragmentos y puntajes sin volver a cargar el corpus, lo que demuestra que el índice vive en Supabase y no en el disco temporal de Colab.
* **Batería de pruebas:** Siete casos con comportamiento esperado escrito antes de ejecutar (respondible, paráfrasis, ambiguo, parcial, sin cobertura, dato dinámico y malicioso). Con `rag_report_v3` las 7 respuestas pasaron la validación (con v2 solo 3, porque el modelo no escribía las etiquetas en el texto). Revisadas a mano contra los pasajes: 4 cumplen, 2 cumplen parcialmente y 1 no cumple.
* **Hallazgo:** Validar el formato no es validar la fidelidad. La pregunta ambigua ("¿Cómo se marca?") recuperó fragmentos con puntajes bajos (≤ 0.30), no recibió el fragmento con la condición de la regla y respondió `parcial` en lugar de pedir aclaración, perdiendo la condición "registros faltantes". Ninguna respuesta inventó cifras, fechas ni estimaciones, y la fecha de `DS-1001` se remitió a `consultar_fuente_datos`.
* **Alcance:** Responde preguntas sobre los documentos del proyecto; aún no está integrado al flujo de generación de borradores ni procesa documentos reales.

### 7. Mejora y Evaluación del RAG (`Clase 9`)

* **Notebook:** `notebooks/C09_Evaluacion_RAG.ipynb`
* **Bitácora:** `logs/C09_2026-10-23_Evaluacion_RAG.md`
* **Evidencias:** `notebooks/Clase_09_Evidencia_Evaluacion_RAG_ReportGenerator.zip` (CSV de métricas por caso y JSON con trazas de la ejecución final del 25-oct-2026)
* **Enfoque:** Sobre el mismo corpus de la clase 8 (6 fragmentos, huella `ff98b1398c56`), sin cambiar embeddings, prompt `rag_report_v3` ni modelo generativo, se comparan tres formas de elegir los 3 pasajes que recibe el generador:
  * **A - semántica:** la función `clase08_buscar_fragmentos` de Supabase, sin cambios.
  * **B - híbrida RRF:** BM25Okapi en memoria (`k1 = 1.5`, `b = 0.75`) fusionado con la semántica por *Reciprocal Rank Fusion* (constante 60).
  * **C - híbrida + reranking:** los candidatos de B reordenados con el *cross-encoder* `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`.
* **Protocolo:** 4 preguntas de desarrollo (D1-D4), 2 de reserva (R1-R2) y 3 de comportamiento (C1-C3), con la evidencia anotada **antes** de ver los rankings; desarrollo y reserva no comparten familia de pregunta (comprobado con `assert`). Métricas: Precision@3, Recall@3, Hit@3, MRR, cobertura y tiempo de recuperación. Se generó la pregunta D2 con A y con B y se revisaron las respuestas a mano.
* **Resultados de desarrollo:**

  | Opción                  | Precision@3 | Recall@3 | MRR  | Cobertura | Mediana recuperación |
  | ----------------------- | ----------- | -------- | ---- | --------- | -------------------- |
  | A - semántica           | 0.417       | 1.00     | 1.00 | 1.00      | ~358 ms              |
  | B - híbrida RRF         | 0.417       | 1.00     | 1.00 | 1.00      | ~359 ms              |
  | C - híbrida + reranking | 0.417       | 1.00     | 1.00 | 1.00      | ~1754 ms             |

* **Decisión: A (semántica).** Las tres opciones empatan en los cuatro casos de desarrollo; con un empate se conserva la opción más simple y barata (C es ~5 veces más lenta sin mejorar ningún caso).
* **Hallazgos:**
  * En la reserva, B y C recuperan las dos partes de la regla `[DATO INCOMPLETO]` (R1), el caso que falló en la clase 8. Pero B **empeora** R2 (Recall 1.0 → 0.33): dos fragmentos empatan exactamente en RRF (0,031545) y el desempate alfabético por `chunk_id` deja fuera el informe técnico. "Híbrido" no significa "mejor".
  * C fue la mejor en la reserva (Recall 1.0, MRR 1.0), pero con 2 casos no es concluyente y la reserva ya se había abierto en una ejecución anterior, así que no cambia la decisión.
  * Una recuperación perfecta no garantiza una respuesta correcta: en D2 las tres opciones llevaron la frase necesaria al contexto y aun así A y B omitieron que el vacío "no se reemplaza con una estimación". Es un fallo de generación, no de recuperación.
* **Alcance:** Con un corpus de 6 fragmentos y `K = 3` el desarrollo no puede distinguir bien las opciones. Para el segundo corte quedan pendientes ampliar a 12-20 casos con una reserva nueva, fragmentar por sección y probar BM25 con *stopwords*.

### 8. Agente, Memoria y MCP (`Clase 11`)

* **Notebook:** `notebooks/C11_RAG_Agente_MCP_ReportGenerator.ipynb`
* **Bitácora:** `logs/C11_AAAA-MM-DD_Agente_MCP.md` (en progreso)
* **Evidencias:** `notebooks/Clase_11_Evidencia_Integracion_ReportGenerator.json` (trazas, configuración y comprobaciones, sin claves ni contraseñas)
* **Enfoque:** Primera integración de las capacidades del proyecto. Un agente recibe una sola entrada y decide entre seis acciones (`buscar_documentos`, `consultar_fuente_datos`, `guardar_informe`, `responder`, `aclarar` y `rechazar`). Cada decisión la toma Groq (`openai/gpt-oss-20b`, `temperature=0`) con *Structured Outputs* y la valida el contrato Pydantic `Decision` (`extra="forbid"`, `strict=True`) antes de ejecutarse.
* **MCP propio:** `consultar_fuente_datos` deja de ser una función local y se publica como servidor MCP (*MCP Python SDK 2.3.0*, transporte `stdio`, en otro proceso). Es de solo lectura, exige el patrón `DS-0000` y devuelve estado, periodo, última actualización, métricas disponibles y ausentes y registros faltantes de tres fuentes ficticias (`DS-1001` actualizada con `margen_bruto` ausente, `DS-1002` incompleta, `DS-1003` desactualizada). Las claves de Groq y Supabase no salen del notebook.
* **MCP externo:** `@modelcontextprotocol/server-filesystem` 2.2.0, confinado a una carpeta temporal de informes. La aplicación solo habilita `write_file` y `read_text_file` (para verificar lo escrito); el nombre del archivo lo asigna la aplicación (`informe_<uuid>.md`), nunca el modelo. Guardar exige el permiso `GUARDAR_INFORME` y citas `F` del turno actual, y el pie de cada borrador fija que `[DATO AUSENTE]` y `[DATO INCOMPLETO]` no se reemplazan con estimaciones (la negación que el modelo omitió en la clase 9).
* **Recuperación:** Se conserva **A (semántica)**, la decisión de la clase 9; B (híbrida RRF) queda disponible con el selector `RECUPERACION` sin reescribir código.
* **Memoria y límites:** Memoria volátil por identificador de conversación (últimos 4 turnos) para resolver referencias como "esa fuente"; un código nuevo tiene prioridad y una conversación no hereda los códigos de otra. Cada turno admite 3 decisiones, 2 operaciones y 90 s, y se detiene ante una operación repetida.
* **Comprobaciones locales (sin Groq):** Pasan todas: catálogo MCP con una sola herramienta, fuente conocida y desconocida, rechazo de argumento inválido, rechazo de lectura fuera de la carpeta, bloqueo de guardado sin fuentes o sin permiso, aislamiento y reinicio de memoria, límites de repetición y de operaciones, y escritura verificada por lectura.
* **Limitación conocida:** Un borrador con cifras de una fuente necesita tres operaciones (RAG + fuente + escritura) y supera el presupuesto de dos, por lo que se detiene con `LIMITE_OPERACIONES`. Se decidirá con pruebas si se amplía el límite o si se genera en dos turnos.
* **Estado:** Pendiente registrar en la bitácora los resultados de los 13 casos con el modelo (punto 7). La función `atender(texto, conversacion, guardar_informe)` será la que conecte la interfaz con Gradio.

## Instrucciones de Ejecución y Reproducción

Para ejecutar el proyecto y verificar los resultados de las entregas, siga las siguientes instrucciones:

### Requisitos Previos y Variables de Entorno

* **Entorno recomendado:** Google Colab o Python 3.10+ local.
* **Configuración de Credenciales:**
  * En Google Colab: Configurar una clave secreta llamada `GROQ_API_KEY` en el menú de *Secrets / Secretos de Colab*.
  * En entorno local: Definir la variable de entorno `export GROQ_API_KEY=""` o crear un archivo `.env`.
  * Para las Clases 8, 9 y 11 se necesitan además los secretos de Colab `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` (clave publicable `sb_publishable_...`, nunca una clave administrativa), `SUPABASE_EMAIL` y `SUPABASE_PASSWORD` (usuario de Supabase Auth, no la cuenta del panel ni la contraseña de PostgreSQL), con acceso habilitado para cada notebook.

### Guía de Ejecución por Notebook

#### A. Experimento de Tokens e Inferencia Local (`Clase 2`)

1. Abrir `notebooks/C02_Report_Generation_Tokens.ipynb` en Google Colab.
2. Reproducir la instalación automática de Ollama y la descarga del modelo local.
3. Ejecutar las celdas de comparación de temperaturas (0.8, 1.7, 2.2) y conteo de tokens.

#### B. Pruebas de Prompts y Clasificación (`Clase 3`)

1. Abrir `notebooks/C03_Demo_Colab_Groq.ipynb` en Google Colab.
2. Definir `MODO_DEMO = "groq"` o `"mock"`.
3. Ejecutar secuencialmente para observar la validación con Pydantic del contrato `Solicitud` y los 5 casos de prueba base.

#### C. Llamada de Herramientas e Integración Completa (`Clase 4`)

> **Punto de entrada principal para revisar el prototipo completo del Corte 1.**

1. Abrir `notebooks/C04_Herramientas.ipynb` en Google Colab.
2. Seleccionar la modalidad en la celda de configuración inicial:
   * `MODO = "groq"` (ejecución real con la API de Groq y el modelo `openai/gpt-oss-20b`).
   * `MODO = "mock"` (ejecución sin consumo de API ni necesidad de credenciales).
3. **Ingreso de una solicitud nueva:** Ir a la **Sección 9 ("Petición de Informe: Edita y Pulsa ▶")**, modificar la variable `texto_usuario` (p. ej.: `"Genera el reporte ejecutivo del último trimestre con los ingresos por región y la tasa de retención de clientes, usando la fuente DS-1001."`) y ejecutar la celda.
4. **Reproducción de Pruebas:**
   * Ejecutar la **Sección 10** para correr la matriz de 11 casos de prueba (normales, ambiguos, incompletos, maliciosos, fuera de alcance y consultas de fuentes).
   * Ejecutar la **Sección 11** para verificar las pruebas negativas deterministas (rechazo de código no citado, fallos controlados y preservación del catálogo).
5. **Exportación de Evidencias:** Ejecutar la **Sección 13** para generar el paquete comprimido `.zip` con esquemas, trazas y bitácora.

#### D. Búsqueda Semántica (`Clase 6`)

1. Abrir `notebooks/C06_Busqueda_Semantica.ipynb` en Google Colab. No requiere clave de API ni GPU; la primera ejecución descarga el modelo de embeddings.
2. Ejecutar las celdas en orden (la sección 1 instala `sentence-transformers`).
3. **Ingreso de una consulta nueva:** Ir a la **Sección 5**, modificar `CONSULTA` (y `K` si se desea) y ejecutar la **Sección 6** para ver el ranking.
4. **Reproducción de Pruebas:** Ejecutar la **Sección 7** (preguntas con información insuficiente) y la **Sección 8** (batería de cinco casos con esperado y top-K).

#### E. Ingesta, Fragmentación e Índice (`Clase 7`)

1. Abrir `notebooks/C07_Ingestion_Indice.ipynb` en Google Colab. No requiere clave de API ni GPU; la primera ejecución necesita Internet para instalar `sentence-transformers` y descargar el modelo.
2. Ejecutar las celdas en orden; las secciones 2 y 3 crean y limpian los documentos, y la sección 4 genera los fragmentos de las dos estrategias.
3. **Ingreso de una consulta nueva:** Ir a la **Sección 5**, modificar `CONSULTA` y ejecutar; la celda siguiente (`PREGUNTAS`) compara las cuatro preguntas de la práctica y comprueba si el mejor resultado trae la condición y su consecuencia.
4. **Guardar el índice:** En la **Sección 6**, elegir `ESTRATEGIA` (`ventanas` o `parrafos`) y ejecutar. Para conservar el ZIP fuera de la sesión, poner `DESCARGAR = True` en la celda siguiente.

#### F. RAG con Supabase y Groq (`Clase 8`)

1. **Preparar Supabase:** Ejecutar `Clase_08_Supabase_Setup.sql` en el *SQL Editor* del proyecto (crea la extensión `vector`, la tabla `clase08_fragmentos` con RLS y la función `clase08_buscar_fragmentos`) y crear un usuario en Supabase Auth.
2. Configurar los cinco secretos de Colab indicados en *Requisitos Previos*.
3. Abrir `notebooks/C08_RAG.ipynb` en Google Colab y ejecutar en orden los **puntos 1 a 5**. En el punto 3 se sube `notebooks/Clase_07_Indice_y_Corpus.zip`; la huella impresa debe ser `ff98b1398c56`.
4. **Ingreso de una pregunta nueva:** Ir al **Punto 6**, modificar `CONSULTA`, ejecutar para ver los fragmentos recuperados y luego ejecutar el **Punto 8** para generar, validar y mostrar la respuesta con sus fuentes.
5. **Reproducción de Pruebas:** En el **Punto 9**, activar `EJECUTAR_PRUEBAS` para correr los siete casos (consume siete llamadas a Groq) y descargar la matriz en CSV.
6. **Persistencia y Evidencia:** Ejecutar el **Punto 10** para comprobar la recuperación desde otro cliente y descargar la traza JSON. Para comprobarlo desde otra sesión de Colab, reiniciar y repetir los puntos 1 a 4 y 6, sin el 5.

#### G. Mejora y Evaluación del RAG (`Clase 9`)

> Requiere el corpus de la Clase 8 ya cargado en Supabase. No vuelve a cargar documentos ni ejecuta SQL nuevo.

1. Configurar los cinco secretos de Colab indicados en *Requisitos Previos*.
2. Abrir `notebooks/C09_Evaluacion_RAG.ipynb` en Google Colab y ejecutar los **puntos 1 a 3**. En el punto 2 se sube `notebooks/Clase_08_Evidencia_RAG_ReportGenerator.json`; el corpus debe terminar en `ff98b1398c56`.
3. **Medición en desarrollo:** Ejecutar los **puntos 4 a 6** (preguntas fijadas, BM25 + RRF + reranking y tabla de métricas de A, B y C).
4. **Decisión y reserva:** En el **Punto 7**, escribir `DECISION_DESARROLLO` **antes** de abrir la reserva y luego activar `ABRIR_RESERVA`. La reserva se abre una sola vez y no se ajusta nada después.
5. **Ingreso de una pregunta nueva:** Ir al **Punto 8**, modificar `CONSULTA` y ejecutar para comparar los rankings de las tres opciones.
6. **Generación:** En el **Punto 9**, activar `GENERAR_RESPUESTAS` y elegir `MEJORA_A_GENERAR` (`B_hibrida_RRF` o `C_hibrida_reranking`); consume dos llamadas a Groq (A y la opción elegida). En el **Punto 10** se registra la revisión manual con sus cuatro criterios.
7. **Comprobaciones y Evidencia:** Ejecutar el **Punto 11** para correr los `assert` (RRF, métricas, tokenización y validador de citas) y descargar el ZIP con el CSV de métricas y las trazas JSON.

#### H. Agente con RAG y MCP (`Clase 11`)

> Requiere el corpus de la Clase 8 ya cargado en Supabase. No vuelve a cargar documentos ni ejecuta SQL nuevo. El servidor MCP propio y Filesystem MCP corren dentro de Colab; no necesitan cuenta, puerto público ni túnel.

1. Configurar los cinco secretos de Colab indicados en *Requisitos Previos*.
2. Abrir `notebooks/C11_RAG_Agente_MCP_ReportGenerator.ipynb` en Google Colab y ejecutar el **Punto 1** (instala `mcp`, `groq`, `pydantic`, `supabase`, `sentence-transformers` y `rank-bm25` en versiones fijas).
3. En el **Punto 2**, dejar `CONECTAR_SERVICIOS = True` y `RECUPERACION = "A_semantica"`, y subir **un solo** JSON: `notebooks/Clase_08_Evidencia_RAG_ReportGenerator.json` o el JSON extraído del ZIP de la Clase 9. Con `CONECTAR_SERVICIOS = False` se pueden ejecutar solo MCP y las comprobaciones locales, sin generar respuestas.
4. Ejecutar los **puntos 3 a 6**: recuperación, servidor MCP `consultar_fuente_datos` (punto 4, muestra el catálogo y la consulta de `DS-1001`), instalación de Node 24 y Filesystem MCP (punto 4.b, debe mostrar `fuera_de_carpeta_rechazado: True`), contrato de decisión, memoria y agente.
5. **Ingreso de una solicitud nueva:** Ir al **Punto 7**, modificar `texto_usuario` y `id_conversacion`, y elegir `GUARDAR_INFORME` (permiso para crear un borrador) y `REINICIAR_ANTES` (borra la memoria de esa conversación). El borrador guardado aparece en la carpeta `Clase_11_Informes_*` del panel de archivos de Colab.
6. **Reproducción de Pruebas:** Ejecutar el **Punto 8** para las comprobaciones locales (no consumen Groq) y probar en el punto 7 los casos de la tabla que le sigue (13 casos en la bitácora).
7. **Evidencia:** Ejecutar el **Punto 9** para descargar `Clase_11_Evidencia_Integracion_ReportGenerator.json`. Los borradores `.md` se descargan por separado: la carpeta de Colab es temporal.

## Tecnologías y Herramientas

* **Lenguaje:** Python 3.10+
* **Entornos de Ejecución:** Google Colab, Jupyter Notebook, Ollama (Local)
* **Modelos de Lenguaje & APIs:** Groq API (`openai/gpt-oss-20b`), Ollama (`gemma4:e2b`), Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`, *cross-encoder* `mmarco-mMiniLMv2-L12-H384-v1`)
* **Recuperación y Evaluación:** `rank-bm25` (BM25Okapi), Reciprocal Rank Fusion, métricas Precision@K, Recall@K, Hit@K y MRR
* **Almacenamiento Vectorial:** Supabase (PostgreSQL + pgvector, Supabase Auth y RLS)
* **Agentes y MCP:** MCP Python SDK 2.3.0 (transporte `stdio`), `@modelcontextprotocol/server-filesystem` 2.2.0, Node 24 (`nodejs-wheel`)
* **Validación:** Pydantic
* **Análisis & Métricas:** Tiktoken, Pandas, Matplotlib, NumPy

## Arquitectura del Flujo de Procesamiento

```text
[Solicitud en Lenguaje Natural]
               │
               ▼
[Clasificación JSON + Validación Pydantic (Solicitud)]
               │
     ¿Requiere Humano / Faltan Datos?
      ├─── (Sí) ──► [Detener o Pedir Aclaración al Usuario]
      └─── (No) ──► [Propuesta de Herramienta + Validación Pydantic (DS-0000)]
                           │
                           ▼
            [Consulta de Solo Lectura al Catálogo de Fuentes]
                           │
                           ▼
            [Contraste Determinista de Métricas (Pedidas vs Disponibles)]
                           │
                           ▼
            [Borrador No Verificado con Etiquetas [DATO AUSENTE] / [DATO INCOMPLETO]]
```

### Módulo de Búsqueda Semántica (Clase 6, aún independiente del flujo anterior)

```text
[Consulta del usuario]
        │
        ▼
[Embedding con el mismo modelo del corpus]
        │
        ▼
[Similitud coseno contra los vectores del corpus]
        │
        ▼
[Ranking top-K con identificador, puntaje y texto]
        │
        ▼
[Lectura humana: ¿el pasaje alcanza para responder?]
```

### Módulo de Ingesta e Índice (Clase 7, aún independiente del flujo principal)

```text
[Documentos Markdown con título, versión y origen]
        │
        ▼
[Lectura y limpieza + metadatos (archivo, versión, huella SHA-256)]
        │
        ▼
[Fragmentación: ventanas | párrafos (≤128 tokens, con título y sección)]
        │
        ▼
[Embeddings normalizados]
        │
        ▼
[Índice guardado: vectores.npy + registros.json + configuracion.json]
        │
        ▼
[Recarga + consulta top-K por similitud coseno]
```

### Módulo RAG (Clase 8, aún independiente del flujo principal)

```text
[Índice de la Clase 7 (ZIP verificado por huella)]
        │
        ▼
[Upsert en Supabase: clase08_fragmentos (pgvector + RLS)]
        │
        ▼
[Pregunta del usuario → embedding con el mismo modelo y revisión]
        │
        ▼
[RPC clase08_buscar_fragmentos: top-K por similitud coseno]
        │
        ▼
[Groq gpt-oss-20b: pregunta + pasajes etiquetados [F1..Fk], salida JSON]
        │
        ▼
[Validación Pydantic (RespuestaRAG) + validación de citas]
      ├─── (Falla) ──► [ERROR_TECNICO: no se muestra texto sin validar]
      └─── (Pasa)  ──► [Estado + respuesta con citas + fragmentos fuente]
```

### Evaluación de la Recuperación (Clase 9)

```text
[Preguntas de desarrollo, reserva y comportamiento + evidencia anotada antes de ejecutar]
        │
        ▼
[A: semántica (Supabase)] [B: BM25 + semántica + RRF] [C: B + reranking cross-encoder]
        │
        ▼
[Métricas en desarrollo: Precision@3, Recall@3, MRR, cobertura, tiempo]
        │
        ▼
[Decisión escrita (A por empate)] ──► [Apertura única de la reserva: confirma, no ajusta]
        │
        ▼
[Generación con el mismo prompt (A vs B) + revisión manual contra las fuentes]
```

### Agente con RAG y MCP (Clase 11, primera integración)

```text
[Entrada del usuario + identificador de conversación + permiso GUARDAR_INFORME]
        │
        ▼
[Memoria: últimos 4 turnos de esa conversación]
        │
        ▼
[Groq gpt-oss-20b: Decision JSON → validación Pydantic + reglas del programa] ◄────┐
      ├── buscar_documentos ──────► [RAG semántico en Supabase → fragmentos [F#]] ──┤
      ├── consultar_fuente_datos ─► [MCP propio (stdio) → registro DS-0000 [T#]] ───┤
      ├── guardar_informe ────────► [Filesystem MCP: write_file + read_text_file] ──┘
      │                              (solo con permiso y citas F del turno)
      └── responder / aclarar / rechazar ──► [Respuesta con citas + traza + archivos]

Límites por turno: 3 decisiones · 2 operaciones · 90 s · sin operaciones repetidas
```

## Criterios de Seguridad y Limitaciones

* **Solo Lectura:** El prototipo no calcula cifras, no modifica bases de datos ni publica documentos de forma automática.
* **Supervisión Humana Mandatoria:** Todo borrador sale etiquetado como `BORRADOR NO VERIFICADO` y requiere revisión por parte de un analista antes de su difusión.
* **Protección ante Inyecciones:** Las entradas maliciosas o intentos de manipulación de reglas se clasifican con prioridad alta y se marcan con `requiere_humano=True`. En el RAG, la pregunta y los documentos se tratan como datos no confiables.
* **Credenciales Aisladas:** El notebook RAG solo acepta una clave publicable de Supabase y opera con un usuario de Auth limitado por RLS a sus propias filas; Groq recibe la pregunta y los pasajes, nunca las credenciales de Supabase.
* **Fragmentación sin garantías semánticas:** Cortar por tokens o párrafos puede separar una condición de su consecuencia. Por eso se lee el texto recuperado antes de decidir si alcanza, y no se usa un umbral automático de similitud.
* **Validación de forma, no de fidelidad:** Que una respuesta RAG pase la validación garantiza que su estructura y sus citas son coherentes, no que cada afirmación esté respaldada por el pasaje. Cada respuesta de la matriz se revisa a mano contra el fragmento citado.
* **Evaluación sin ajuste posterior:** Las preguntas y su evidencia se fijan antes de ver los rankings y la decisión se toma solo con el conjunto de desarrollo. La reserva confirma, no ajusta; si se abre antes de tiempo se declara como comprometida.
* **Escritura mínima y con permiso:** La única escritura habilitada es crear un borrador nuevo, con permiso explícito y citas del turno actual. El modelo no elige rutas, el servidor de archivos no puede salir de su carpeta y no existen herramientas para modificar fuentes, cambiar el corpus ni enviar informes.
* **Separación de procesos y credenciales:** Los servidores MCP corren en procesos separados y no reciben las claves de Groq ni de Supabase. El identificador de conversación separa historiales, pero no autentica a una persona; una aplicación multiusuario necesitará identidad real.