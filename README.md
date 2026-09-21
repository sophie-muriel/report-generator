> ⚠️ **ESTE PROYECTO ESTÁ EN DESARROLLO Y SU CONTENIDO/README SE ACTUALIZARÁ DE MANERA PERIÓDICA**
 
---
# Report Generator (Generador de Informes con IA)

<img width="4096" height="1934" alt="ollama-tool" src="https://github.com/user-attachments/assets/7f8a29db-4182-4cc8-b304-b7f8e18d388d" />


> **Prototipo Generativo con Control de Estructura, *Tool Calling* y Validación de Fuentes**  
> 
> Proyecto final desarrollado para el docente Rober Erick García para la asignatura Electiva VI, Periodo 2026-II, en la Institución Universitaria EAM.

## Equipo de Trabajo (Juliofi~)

* **Juliana Marín Vélez:** Elaboración y ejecución de notebooks.
* **Sophie Rosero Muriel:** Soporte técnico en notebooks, verificación de pruebas y registro continuo en bitácoras.

---
## Descripción del Proyecto

*Report Generator* es un sistema inteligente diseñado para automatizar la construcción de borradores de informes empresariales (ejecutivos, técnicos, resúmenes periódicos y generales) garantizando rigor factual, trazabilidad y control estricto sobre los datos.

### El Problema

En el entorno corporativo, los informes internos suelen elaborarse manualmente consolidando métricas de diversas fuentes. El riesgo más crítico no radica en la redacción, sino en publicar un informe basado en datos inexistentes o periodos aún no cerrados. 

### La Solución

Para resolver este problema, *Report Generator* opera como un asistente de solo lectura que:

1. **Clasifica y valida solicitudes:** Parsea peticiones en lenguaje natural a esquemas JSON estrictos mediante Pydantic.
2. **Consulta fuentes registradas:** Invoca herramientas de *Tool Calling* para validar la disponibilidad real de datos en un catálogo de fuentes (`DS-0000`).
3. **Genera borradores auditables:** Redacta plantillas de informes señalando explícitamente cualquier vacío mediante las etiquetas `[DATO AUSENTE]` y `[DATO INCOMPLETO]`, sin inventar cifras ni asumir métricas no confirmadas.

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

## Estructura del Repositorio

```text
report-generator/
├── .obsidian/               # Configuración del vault de Obsidian
├── images/                  # Capturas de pantalla y evidencias de ejecución
├── logs/                    # Bitácoras de clase en Markdown (C02, C03, C04)
│   ├── C02_2026-08-26_Tokens.md
│   ├── C03_2026-09-08_PromptV1.md
│   └── C04_2026-09-13_Herramientas.md
├── notebooks/               # Notebooks ejecutables en Google Colab
│   ├── C02_Report_Generation_Tokens.ipynb
│   ├── C03_Demo_Colab_Groq.ipynb
│   └── C04_Herramientas.ipynb
└── prompts/                 # Especificaciones y versiones del prompt del sistema
    ├── SYSTEM_PROMPT_V1
    └── SYSTEM_PROMPT_V2
```

## Instrucciones de Ejecución y Reproducción

Para ejecutar el proyecto y verificar los resultados de las entregas, siga las siguientes instrucciones:

### Requisitos Previos y Variables de Entorno

* **Entorno recomendado:** Google Colab o Python 3.10+ local.
* **Configuración de Credenciales:**
  * En Google Colab: Configurar una clave secreta llamada `GROQ_API_KEY` en el menú de *Secrets / Secretos de Colab*.
  * En entorno local: Definir la variable de entorno `export GROQ_API_KEY=""` o crear un archivo `.env`.

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

&gt; **Punto de entrada principal para revisar el prototipo completo del Corte 1.**

1. Abrir `notebooks/C04_Herramientas.ipynb` en Google Colab.
2. Seleccionar la modalidad en la celda de configuración inicial:
   * `MODO = "groq"` (ejecución real con la API de Groq y el modelo `openai/gpt-oss-20b`).
   * `MODO = "mock"` (ejecución sin consumo de API ni necesidad de credenciales).
3. **Ingreso de una solicitud nueva:** Ir a la **Sección 9 ("Petición de Informe: Edita y Pulsa ▶")**, modificar la variable `texto_usuario` (p. ej.: `"Genera el reporte ejecutivo del último trimestre con los ingresos por región y la tasa de retención de clientes, usando la fuente DS-1001."`) y ejecutar la celda.
4. **Reproducción de Pruebas:**
   * Ejecutar la **Sección 10** para correr la matriz de 11 casos de prueba (normales, ambiguos, incompletos, maliciosos, fuera de alcance y consultas de fuentes).
   * Ejecutar la **Sección 11** para verificar las pruebas negativas deterministas (rechazo de código no citado, fallos controlados y preservación del catálogo).
5. **Exportación de Evidencias:** Ejecutar la **Sección 13** para generar el paquete comprimido `.zip` con esquemas, trazas y bitácora.

## Tecnologías y Herramientas

* **Lenguaje:** Python 3.10+
* **Entornos de Ejecución:** Google Colab, Jupyter Notebook, Ollama (Local)
* **Modelos de Lenguaje & APIs:** Groq API (`openai/gpt-oss-20b`), Ollama (`gemma4:e2b`)
* **Validación de Datos & Esquemas:** Pydantic V2, JSON Schema (*Structured Outputs*)
* **Análisis & Métricas:** Tiktoken, Pandas, Matplotlib

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

## Criterios de Seguridad y Limitaciones

* **Solo Lectura:** El prototipo no calcula cifras, no modifica bases de datos ni publica documentos de forma automática.
* **Supervisión Humana Mandatoria:** Todo borrador sale etiquetado como `BORRADOR NO VERIFICADO` y requiere revisión por parte de un analista antes de su difusión.
* **Protección ante Inyecciones:** Las entradas maliciosas o intentos de manipulación de reglas se clasifican con prioridad alta y se marcan con `requiere_humano=True`.
