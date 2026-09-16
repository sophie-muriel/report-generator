---
tipo: bitacora-clase
curso: Electiva VI
periodo: EAM-2026II
equipo: Juliofi
corte: 1
semana: "4"
clase: "4"
fecha: 2026-09-13
estado: completado
tags:
  - ai
  - bitácora
  - herramientas
---
# Bitácora — Clase 4

> [!tip] Cómo usar esta plantilla
> Duplica esta nota al finalizar cada clase y nómbrala `C##_AAAA-MM-DD_Tema`. Completa los campos entre corchetes y conserva enlaces verificables.

## 1. Datos de la sesión

| Campo    | Registro                                                                                                                                                                                                                                      |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tema     | Herramientas (*tool calling*) y validación de argumentos                                                                                                                                                                                      |
| Objetivo | Agregar al clasificador de la Clase 03 una herramienta de solo lectura que consulte un catálogo de fuentes de datos, validar sus argumentos con un segundo contrato Pydantic y construir un borrador de informe que señale los datos ausentes |
| Proyecto | Report Generator                                                                                                                                                                                                                              |
| Inicio   | 6:00                                                                                                                                                                                                                                          |
| Cierre   | 9:00                                                                                                                                                                                                                                          |

## 2. Participación y responsabilidades

| Integrante           | Asistió | Responsabilidad asumida                                                                                                                | Aporte verificable                                                                 |
| -------------------- | :-----: | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Juliana Marín Vélez  |   Sí    | Elaborar y ejecutar el notebook además de redactar sección nueva propia del caso en el notebook (plantillas y control de consistencia) | Archivo `notebooks/C04_Herramientas.ipynb` y `prompts/SYSTEM_PROMPT_V2`            |
| Sophie Rosero Muriel |   Sí    | Soporte en elaboración del notebook y registro en bitácora, además de verificación y pruebas                                           | Archivo `notebooks/C04_Herramientas.ipynb` y `logs/C04_2026-09-13_Herramientas.md` |

## 3. Reto aplicado al proyecto

### Funcionalidad trabajada

Hasta la Clase 03 el prototipo clasificaba la petición (`tipo_reporte`, `prioridad`, `datos_faltantes`) pero nunca comprobaba si los datos del informe existían; un generador de informes sin fuente solo produce texto plausible. En esta clase agregamos esa verificación:

- Añadimos un catálogo ficticio de fuentes (`DS-1001` ventas trimestrales, `DS-1002` métricas de servidor, `DS-1003` KPIs mensuales), cada una con periodo cubierto, última actualización, métricas disponibles y métricas incompletas.
- Diseñamos una herramienta de solo lectura `consultar_fuente_datos(codigo_fuente)` que devuelve una copia de los metadatos y distingue tres resultados (encontrada, no encontrada y fallo de conexión).
- Diseñamos un segundo contrato Pydantic `ArgumentosFuente` con `extra="forbid"`, `strict=True` y patrón `^DS-[0-9]{4}$`, más una comprobación de que el código propuesto aparezca literalmente en el texto del usuario.
- Añadimos control de consistencia determinista, `detectar_metricas`, que reconoce métricas de un vocabulario cerrado, y `contrastar_disponibilidad`, que separa métricas verificadas, ausentes e incompletas.
- Diseñamos un borrador desde plantilla (`redactar_borrador`) que arma el informe solo con metadatos del catálogo y marca los vacíos como `[DATO AUSENTE: x]` y `[DATO INCOMPLETO: x]`. No escribe cifras porque el prototipo no las calcula.
- Redactamos el SYSTEM_PROMPT_V2 que conserva el V1 completo y le suma las reglas del catálogo (pedir `codigo_fuente`, no afirmar que una métrica existe, escalar a humano si piden publicar o enviar).
 
Esto es directamente el objetivo del proyecto: borradores verificables, datos ausentes señalados y errores detenidos antes de la revisión humana. Adicionalmente, corrimos primero en modo `mock` para probar la interfaz sin gastar cuota, y después cambiamos a modo `groq` para ver el comportamiento real del modelo.

### Criterios de aceptación

- [x] La conexión a Groq funciona leyendo `GROQ_API_KEY` desde los secretos de Colab.
- [x] La clasificación de la Clase 03 (`tipo_reporte` + Pydantic) sigue funcionando sin reescribirse.
- [x] La herramienta es de solo lectura: el catálogo `FUENTES` queda idéntico después de todas las pruebas (`assert` de comparación al final).
- [x] Un código de fuente que no aparece en el texto del usuario es rechazado antes de ejecutar la consulta.
- [x] Fuente inexistente (`NO_ENCONTRADA`) y fallo de conexión (`ERROR_HERRAMIENTA`) son estados distintos.
- [x] Los 11 casos de prueba obtuvieron el estado esperado en modo `mock` (11/11). En modo `groq` (modelo real) el resultado varió entre ejecuciones — 8/11 y 7/11 en dos corridas distintas —, con casos distintos fallando cada vez; se documenta como hallazgo de variabilidad del modelo en la sección 9, no como error de código.
- [x] Ninguna métrica ausente aparece como disponible en el borrador (verificado con `assert`).

### Archivos o componentes modificados

- `[notebooks/C04_Herramientas.ipynb]`: Ejecución completa en modo `mock` y `groq` con el modelo `openai/gpt-oss-20b`.
- `[notebooks/C04_ReportGenerator_1789510735794980198.zip]`: Evidencias generadas al ejecutar el notebook mencionado previamente.
- `[logs/C04_2026-09-13_Herramientas.md]`: Redacción de la bitácora para la cuarta clase de Electiva VI, durante la cual se desarrolló el notebook mencionado previamente.
- `prompts/SYSTEM_PROMPT_V2`: Redacción de la versión #2 del prompt del sistema (V1 + reglas del catálogo de fuentes).

## 4. Decisiones técnicas

| Decisión                                                                                                  | Razón                                                                                                                                                                                        | Alternativa descartada                                                                                                |
| --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Ejecutar primero en modo `mock` y después cambiar a `groq`                                                | Permite confirmar que el código, el esquema y las reglas de negocio funcionan sin gastar cuota, antes de exponerlos a la variabilidad de una API real (además es recomendación del profesor) | N/A                                                                                                                   |
| Que la herramienta consulte un catálogo de fuentes y no, por ejemplo, el estado de un informe ya generado | El riesgo real de un generador de informes es redactar sobre datos que no existen. Consultar disponibilidad ataca ese riesgo directamente                                                    | Una herramienta tipo "estado del informe", que habría sido una copia del ejemplo del profesor sin aportar al proyecto |
| Hacer el contraste pedido-vs-disponible en código determinista, no pidiéndoselo al modelo                 | El borrador tiene que ser auditable: el revisor humano debe poder repetir el contraste y obtener lo mismo. Un modelo puede afirmar que una métrica está disponible                           | Pedirle al modelo que devuelva las métricas faltantes en el JSON de clasificación                                     |
| Que el borrador no incluya cifras                                                                         | El catálogo ya contiene metadatos, pero cualquier número sería inventado, añadiendo complejidad innecesaria                                                                                  | Simular valores de ejemplo para que el borrador "se vea" como un informe terminado                                    |
| Exigir que el código `DS-0000` aparezca literalmente en el texto del usuario                              | Evita que el modelo elija una fuente por su cuenta. Un informe construido sobre una fuente que nadie pidió es peor que no generar nada                                                       | Confiar en la validación de formato de Pydantic únicamente                                                            |
| Invertir el orden de `validar_y_decidir`. `requiere_humano` ahora va antes de la aclaración               | En la Clase 03 una petición maliciosa con `datos_faltantes` no vacío salía como `OK_PIDE_ACLARACION`, es decir, el sistema respondía en vez de escalar                                       | Dejar el orden de la Clase 03 tal cual                                                                                |
| Usar un vocabulario cerrado de ocho métricas en `detectar_metricas`                                       | Si extrajéramos nombres de métricas libremente del texto, el sistema inventaría nombres de columna que no existen en la fuente                                                               | Extraer las métricas con el modelo o con una expresión regular abierta                                                |
| Devolver una copia del registro (`json.loads(json.dumps(...))`) en la herramienta                         | Sin la copia, cualquier código posterior podría modificar el catálogo por referencia y el "solo lectura" sería solo una promesa escrita en el `docstring`                                    | Devolver el diccionario original del catálogo                                                                         |


## 5. Problemas y soluciones

| Problema encontrado                                                                                                | Causa identificada                                                                                                                                                                                                                        | Solución aplicada                                                                                                                                                                                               | ¿Cómo se verificó?                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| El código válido `DS-1002` era aceptado aunque el usuario hubiera escrito `DS-1001`                                | El patrón de Pydantic valida el formato, no la procedencia del dato                                                                                                                                                                       | Se agregó en `validar_llamada` la comprobación contra los códigos hallados con expresión regular en el texto original                                                                                           | Prueba negativa #2 del punto 11: la llamada con `DS-1002` sobre un texto que dice `DS-1001` lanza `ValueError`                                                     |
| Las métricas escritas con tilde ("tasa de retención") no coincidían con las claves del catálogo (`tasa_retencion`) | Comparación directa de cadenas con acentos y mayúsculas                                                                                                                                                                                   | Función `normalizar` con `unicodedata` (NFD + descarte de marcas diacríticas) aplicada a texto y alias                                                                                                          | El caso 1 detecta `ingresos_por_region` y `tasa_retencion` y el borrador marca la incompleta                                                                       |
| Errores de la API de `groq` (timeouts / fallos intermitentes) al inicio de las pruebas en modo `groq`              | El cliente no reintentaba ante errores transitorios (429, 5xx, timeouts) y los parámetros de conexión (`timeout`) y de generación (`max_completion_tokens`) estaban ajustados muy bajo para el volumen de las peticiones con herramientas | Se agregó `llamar_con_reintentos` con backoff exponencial para envolver las llamadas a `clasificar` y `proponer_herramienta`, y se subieron `timeout` y `max_completion_tokens` en la configuración del cliente | Las llamadas dejaron de fallar por timeout en ejecuciones posteriores; las trazas del punto 10 muestran `error: null` en los casos donde antes fallaba la conexión |
## 6. Evidencias

| Tipo    | Descripción                                                                                                                                            | Enlace o ruta                                                                |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| Commit  | Subida de bitácora, notebook, resultado del notebook, y prompt del sistema V2                                                                          | https://github.com/sophie-muriel/report-generator                            |
| Captura | Ejecución exitosa de petición de informe en la sección #9                                                                                              | ![[Pasted image 20260915183134.png]]                                         |
| Captura | Evidencia de 7/11 casos exitosos en modo `groq`                                                                                                        | ![[Pasted image 20260915183316.png]]                                         |
| Captura | Evidencia de 8/11 casos exitosos en modo `groq` en una ejecución distinta (sin cambios en el notebook)                                                 | ![[Pasted image 20260915183548.png]]                                         |
| Captura | Evidencia del caso `normal_01` (Clase 03) mostrando `OK_PIDE_ACLARACION` por falta de `codigo_fuente`                                                  | ![[Pasted image 20260915183928.png]]                                         |
| Captura | Borrador del caso 1 (`DS-1001`, ingresos por región + tasa de retención) mostrando `OK_BORRADOR_CON_AUSENCIAS` con `[DATO INCOMPLETO: tasa_retencion]` | ![[Pasted image 20260915184115.png]]                                         |
| Captura | `DS-9999` → `NO_ENCONTRADA` frente a `SIMULAR_FALLO=True` → `ERROR_HERRAMIENTA`                                                                        | ![[Pasted image 20260915184412.png]]<br>![[Pasted image 20260915184446.png]] |
| Código  | `validar_llamada` y `contrastar_disponibilidad`                                                                                                        | Notebook, puntos 5 y 7                                                       |
| Demo    | Ejecución del punto 10 (11 casos)                                                                                                                      | Notebook, punto 10                                                           |

## 7. Uso de inteligencia artificial

> [!important] Registrar la IA no reemplaza la explicación técnica. El equipo debe verificar, adaptar y comprender cualquier resultado utilizado.

| Herramienta                       | Objetivo o pregunta                                                                                        | Qué se utilizó                                                                                    | Cómo se verificó                                                                        | Qué se modificó                                                   |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Claude / Google Notebook / Gemini | Ayuda para redactar el tema y los objetivos de la sesión, y para pulir la redacción general de la bitácora | Extracción del tema/objetivo principal a partir del notebook y sugerencias de redacción generales | Se comparó contra lo que efectivamente se hizo en el notebook antes de aceptar el texto | Se ajustó la redacción de las secciones 1 y 3 con lenguaje propio |

Si no se utilizó IA, escribir: **No se utilizó inteligencia artificial en esta sesión.**

## 8. Defensa técnica y retroalimentación

| Campo                     | Registro          |
| ------------------------- | ----------------- |
| Integrante que defendió   | [Nombre]          |
| Pregunta recibida         | [Pregunta]        |
| Respuesta resumida        | [Respuesta]       |
| Retroalimentación docente | [Observación]     |
| Mejora acordada           | [Acción concreta] |

## 9. Aprendizajes

- **Concepto comprendido:** que validar el formato de un argumento no es lo mismo que validar su procedencia. Pydantic acepta `DS-1002` porque cumple el patrón, aunque el usuario nunca lo haya escrito; hizo falta una comprobación aparte contra el texto original. Aplicado a nuestro proyecto: un informe correcto en la forma puede estar construido sobre la fuente equivocada.
- **Algo que aún genera duda:**
	- Qué hacer cuando el usuario nombra una métrica que no está en el vocabulario cerrado. Hoy el contraste revisa todas las métricas de la fuente y el borrador no advierte que hubo una petición no reconocida; conviene un estado propio para eso?
	- Por qué el modelo real (`groq`) no logra un resultado estable en el punto 10. En modo `mock` el flujo da 11/11 siempre (porque las respuestas están escritas por nosotras), pero en `groq` obtuvimos 8/11 en una corrida y 7/11 en otra, con casos distintos fallando cada vez. En ambas, el patrón fue el mismo: el modelo pidió aclaración de más (`rango_de_fechas`, `periodicidad`) en peticiones donde el prompt V2 dice explícitamente que no debe hacerlo si ya hay código de fuente y métricas nombradas. Por ejemplo, `DS-1001` con ticket promedio y usuarios activos nunca llegó a `OK_BORRADOR_CON_AUSENCIAS` a través del recorrido completo en ninguna corrida `groq`, aunque `contrastar_disponibilidad` sí marca correctamente `usuarios_activos` como ausente cuando se la llama directamente (sección 7). No sabemos si el prompt necesita un ejemplo más explícito de esa regla o si es variabilidad propia del modelo entre llamadas, como ya vimos con `confianza` en la Clase 03.
- **Qué haríamos diferente:** correr las 11 pruebas en `groq` al menos tres veces (no solo una) antes de reportar un número, porque una sola corrida no distingue un error real de la variabilidad normal del modelo. También añadiríamos al prompt v2 un ejemplo concreto de "código + métricas nombradas → no pedir más datos", en vez de solo la instrucción en prosa.

## 10. Revisión antes de entregar

- [x] Todos los integrantes registraron un aporte verificable.
- [x] Los enlaces y rutas de evidencia funcionan.
- [x] Los criterios de aceptación están actualizados.
- [x] El uso de IA fue declarado y verificado.
- [x] El equipo puede explicar las decisiones registradas.
