# Entrega del proyecto y presentación explicativa — Corte 1

**Inteligencia Artificial Generativa y Sistemas Inteligentes · EAM 2026-II**

## 1. Qué vamos a entregar

Por disponibilidad de tiempo en clase, cada equipo entregará el proyecto completo correspondiente al primer corte y una presentación que permita comprenderlo y revisar sus evidencias sin depender de una exposición oral extensa.

La entrega debe mostrar lo que realmente implementaron: problema, funcionamiento, integración del modelo, decisiones técnicas, validaciones, pruebas y limitaciones. Cada afirmación importante debe acompañarse de una evidencia o una referencia clara al archivo donde pueda comprobarse.

Entreguen estos dos componentes:

1. **Proyecto completo:** código fuente, notebook o aplicación, dependencias, configuración de ejemplo sin claves, datos de prueba, prompts, contratos, evidencias y bitácora.
2. **Presentación explicativa:** diapositivas en el orden indicado en esta guía, con explicaciones comprensibles y resultados legibles. Incluyan una copia en PDF para facilitar su revisión y el archivo editable o fuente utilizado para crearla. Si usan RevealJS, entreguen su HTML y los recursos necesarios, además del PDF.

“Proyecto completo” significa el prototipo generativo del primer corte. No significa que deban terminar desde ahora el sistema RAG o los agentes previstos para los siguientes cortes. El trabajo en Colab es válido si puede ejecutarse en orden y permite ingresar una solicitud nueva.

## 2. Material que el equipo debe entrega

Al preparar la presentación, entregan el mismo material debe quedar incluido o claramente referenciado en la entrega; no se trata de realizar otra exposición extensa en clase.

- Prototipo o notebook ejecutable, con una celda o interfaz identificable para ingresar una solicitud nueva.
- Código y configuración del modelo. Las credenciales deben permanecer ocultas.
- Prompt utilizado y su versión; contrato de salida y validaciones cuando corresponda.
- Herramienta integrada o entrada multimodal y su fuente de datos.
- Matriz de al menos cinco casos: normal, ambiguo, incompleto o inválido, malicioso y fuera de alcance. Debe distinguir expectativa y resultado observado.
- Evidencia de un fallo técnico o de validación y del comportamiento del programa ante ese fallo.
- Bitácora en Obsidian e instrucciones para volver a ejecutar el proyecto.

La tabla de pruebas puede formar parte del notebook. No necesitan duplicar archivos: indiquen su ubicación y lleven a la presentación el resultado que necesitan explicar. Comprueben que las capturas no contengan claves, tokens de autenticación ni datos personales innecesarios.

## 3. Cómo construir la presentación, paso a paso

Utilicen los siguientes 15 apartados como secuencia de diapositivas. Pueden dividir un apartado en dos cuando sea necesario para que el texto, una tabla o una evidencia se lean bien. No reduzcan tanto la letra que la revisión requiera ampliar constantemente el documento.

La presentación debe poder leerse por sí sola. Eviten dejar únicamente títulos, palabras sueltas o capturas sin explicación. No es necesario transcribir todas las clases: expliquen cómo aplicaron sus conceptos a este proyecto.

### Diapositiva 1. Identificación del proyecto

Incluyan nombre del proyecto, integrantes, asignatura, corte y versión o fecha de la entrega. Agreguen una frase que describa qué hace el prototipo.

La descripción debe corresponder a la versión presentada. Si una capacidad todavía está planeada, no la anuncien como implementada.

### Diapositiva 2. Problema, usuario y objetivo

Expliquen quién necesita la solución, qué dificultad tiene y qué resultado concreto busca obtener. Incluyan un ejemplo breve de una situación que atendería la aplicación.

Cierren el apartado con el objetivo del prototipo y una condición observable para comprobarlo. Por ejemplo: recibir una solicitud, clasificarla, detectar datos faltantes y mostrar una respuesta validada.

### Diapositiva 3. Alcance de la primera entrega

Indiquen qué funciones están implementadas, qué entradas acepta el sistema y qué salidas produce. Expliquen también qué peticiones quedan fuera de alcance.

Distingan las capacidades terminadas de las pendientes. Si trabajan con datos ficticios, díganlo. Si solo consultan información, no afirmen que registran, aprueban o modifican datos.

### Diapositiva 4. Recorrido completo del sistema

Presenten un esquema sencillo del flujo real: entrada del usuario, preparación del contexto, llamada al modelo, validación, herramienta o procesamiento adicional cuando corresponda, respuesta y registro de evidencia.

Debajo del esquema expliquen qué interpreta el modelo y qué controla el programa. Si hay dos llamadas al modelo, señalen ambas y expliquen para qué sirve cada una. El esquema debe coincidir con su implementación.

### Diapositiva 5. Modelo, API y configuración

Identifiquen proveedor o ejecución local, modelo utilizado y entorno de trabajo. Expliquen cómo se configura la conexión sin mostrar la clave.

Muestren los parámetros que realmente utilizaron y justifiquen su elección: límite de salida, temperatura u otros parámetros admitidos por el modelo. Indiquen qué comparación o experimento de la clase de tokens y contexto respalda la decisión.

No inventen configuraciones ni mediciones. Si una opción no está disponible en el modelo o no se probó, indíquenlo.

### Diapositiva 6. Prompt y contexto

Expliquen la tarea que define el prompt, las reglas, el tratamiento de información insuficiente y la separación entre instrucciones y datos del usuario.

Muestren un fragmento representativo y señalen el archivo con el prompt completo y su versión. Describan una decisión de diseño: por qué añadieron una restricción, un ejemplo o una regla de aclaración. Si cambiaron de versión, expliquen el motivo y el resultado observado.

### Diapositiva 7. Salida y validación

Muestren un ejemplo real de la salida y expliquen qué campos o condiciones necesita la aplicación. Si usan JSON, indiquen tipos, campos obligatorios y valores permitidos.

Señalen dónde se valida en el código: por ejemplo, la llamada a Pydantic y la función que la contiene. Expliquen qué ocurre si llega un campo ausente o un valor inválido.

Aclaren cómo comprueban el contenido además del formato. Una salida que cumple el esquema todavía puede interpretar mal la entrada. Si no utilizan JSON, expliquen los controles concretos aplicados a su salida y por qué ese formato es pertinente.

### Diapositiva 8. Herramienta o modalidad integrada

Si integraron una herramienta, expliquen su propósito, argumentos, fuente de datos, validación y resultado. Muestren una propuesta del modelo y la evidencia de la función ejecutada. Indiquen qué operaciones permite y cuáles no.

Si integraron imagen, audio o un documento puntual, muestren la entrada, lo que extrajeron y cómo comprobaron su correspondencia con el original. Expliquen qué ocurre si la entrada es ilegible o insuficiente.

Presenten la capacidad pertinente de su proyecto. No es necesario incorporar todas las modalidades. Conecten esta integración con el trabajo de la clase anterior: qué conservaron y qué añadieron.

### Diapositiva 9. Evidencia de funcionamiento con un caso nuevo

Muestren el recorrido de una solicitud concreta que hayan ejecutado. La evidencia debe permitir identificar:

1. La entrada exacta del usuario.
2. La salida del modelo y su validación.
3. La herramienta ejecutada o el procesamiento adicional, si corresponde.
4. La respuesta final y su relación con el resultado esperado.

Utilicen capturas legibles o extractos de ejecución y expliquen qué demuestra cada uno. Indiquen en qué archivo o celda puede repetirse el caso. No basta una captura de la respuesta final sin entrada ni contexto.

Si la evidencia fue generada en mock, identifíquenla y aporten por separado la evidencia de integración real con el modelo. El mock permite comprobar el programa, pero no demuestra la calidad de las respuestas de la API.

### Diapositiva 10. Matriz de pruebas

Incluyan al menos cinco casos: normal, ambiguo, incompleto o inválido, malicioso y fuera de alcance. La tabla debe mostrar entrada, resultado esperado, resultado observado y conclusión de cada caso.

Si la tabla completa no cabe, distribúyanla en varias diapositivas y entreguen también la versión completa en el proyecto. Los errores observados deben quedar visibles; no cambien la expectativa únicamente para hacerla coincidir con la respuesta del modelo.

### Diapositiva 11. Errores y comportamiento del sistema

Expliquen un fallo técnico o de validación que hayan probado y muestren cómo lo trata el programa. Puede ser un argumento inválido, una respuesta que incumple el esquema o un fallo controlado de consulta.

Distingan el error de una respuesta válida sin resultados. Por ejemplo, “el código no existe” y “no pudimos consultar el servicio” son situaciones diferentes. Indiquen qué recibe el usuario y qué queda registrado para analizar el problema.

### Diapositiva 12. Tokens, latencia y resultados observados

Presenten las métricas disponibles en sus ejecuciones: tokens de entrada y salida, latencia y configuración asociada. Expliquen qué etapas incluye el tiempo medido y, si hay varias llamadas, si el consumo corresponde a una llamada o al recorrido completo.

Relacionen una observación con una decisión: reducir contexto, ajustar límite de salida o mantener una configuración. Si no cuentan con una métrica, márquenla como no disponible. No presenten tiempos de mock como rendimiento real del modelo.

### Diapositiva 13. Limitaciones y mejoras pendientes

Describan limitaciones concretas sustentadas en pruebas: qué tipo de entrada falla, qué información falta o qué capacidad todavía no implementaron. Eviten frases genéricas como “la IA puede equivocarse” sin mostrar el caso.

Para cada limitación relevante, indiquen una acción de mejora. Separen la corrección pendiente del primer corte de las capacidades que pertenecen a los siguientes cortes, como RAG o agentes más amplios.

### Diapositiva 14. Bitácora y contribuciones

Muestren una decisión importante registrada en Obsidian: objetivo, experimento, resultado, error o limitación y decisión final. Indiquen la ubicación de la nota completa dentro de la entrega.

Expliquen la contribución concreta de cada integrante y cómo se conecta con el sistema. La bitácora debe corresponder a la versión y a las evidencias que presentan.

### Diapositiva 15. Cómo ejecutar y dónde está cada evidencia

Incluyan los pasos mínimos para abrir y ejecutar el proyecto: archivo inicial, entorno, dependencias, configuración requerida y lugar donde se ingresa una solicitud.

Señalen la ubicación del código, prompt, contrato, datos de prueba, matriz de resultados y bitácora. En Colab indiquen qué secreto debe configurar quien revise, sin compartir su valor. En un repositorio o carpeta compartida comprueben que los enlaces tengan permisos de lectura.

Esta diapositiva debe permitir encontrar la evidencia sin tener que preguntar al equipo dónde está cada archivo.

## 4. Organización del proyecto que deben enviar

Entreguen una carpeta o archivo ZIP con un nombre identificable, por ejemplo `Corte1_NombreProyecto_Apellido1_Apellido2`. Si ya tienen una estructura clara en su repositorio, consérvenla y expliquen sus rutas en el README.

La entrega debe contener:

- **README:** descripción, alcance, instrucciones de ejecución y ubicación de las evidencias.
- **Código o notebook completo:** archivos necesarios para ejecutar la versión presentada.
- **Dependencias y configuración de ejemplo:** instrucciones de instalación, nombre del modelo y nombres de variables o secretos; nunca sus valores privados.
- **Prompts y contratos:** versiones utilizadas y validaciones, dentro del código o en archivos separados según la implementación.
- **Datos de prueba:** material necesario para reproducir los casos, preferiblemente ficticio y sin información personal innecesaria.
- **Pruebas y resultados:** expectativas, salidas observadas, métricas y errores.
- **Bitácora:** notas y recursos referenciados necesarios para revisar las decisiones.
- **Presentación:** PDF y archivo editable o fuente con sus recursos.

El PDF explica el proyecto; el código permite comprobarlo. Ambos deben corresponder a la misma versión. No envíen claves de API, archivos de secretos ni carpetas de dependencias instaladas que puedan reconstruirse con las instrucciones.

## 5. Comprobación antes de enviar

- [ ] El proyecto puede abrirse y ejecutarse siguiendo el README.
- [ ] Se identifica claramente dónde ingresar una solicitud nueva.
- [ ] La presentación explica todos los apartados y puede comprenderse sin exposición oral.
- [ ] Las capturas, fragmentos de código y tablas se leen bien en el PDF.
- [ ] El modelo, la configuración y el prompt coinciden con la ejecución presentada.
- [ ] Se muestra dónde valida el programa y qué ocurre ante un error.
- [ ] La herramienta o modalidad aporta al objetivo del proyecto y tiene evidencia de funcionamiento.
- [ ] La matriz contiene los cinco tipos de caso y distingue expectativas de resultados.
- [ ] Los resultados de mock están identificados y no se presentan como ejecución real del modelo.
- [ ] Se incluyen limitaciones, decisiones de bitácora y contribuciones individuales.
- [ ] Los archivos y enlaces citados existen y pueden consultarse.
- [ ] El proyecto y la presentación no contienen credenciales.
- [ ] Se incluyen el PDF, su archivo editable o fuente y el proyecto completo.

La fecha y el medio de envío serán los indicados por el profesor. Esta guía organiza la entrega y no modifica los porcentajes de evaluación comunicados para el corte.
