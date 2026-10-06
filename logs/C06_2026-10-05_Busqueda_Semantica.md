---
tipo: bitacora-clase
curso: Electiva VI
periodo: EAM-2026II
equipo: Juliofi
corte: 2
semana: "6"
clase: "6"
fecha: 2026-10-05
estado: completado
tags:
  - ai
  - bitácora
  - embeddings
---
# Bitácora — Clase 6

> [!tip] Cómo usar esta plantilla
> Duplica esta nota al finalizar cada clase y nómbrala `C##_AAAA-MM-DD_Tema`. Completa los campos entre corchetes y conserva enlaces verificables.

## 1. Datos de la sesión

| Campo    | Registro                                                                                                                                                                    |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tema     | Embeddings y búsqueda semántica                                                                                                                                             |
| Objetivo | Representar textos como vectores, recuperar los pasajes más cercanos a una consulta con similitud coseno y reconocer cuándo lo recuperado todavía no alcanza para responder |
| Proyecto | Report Generator                                                                                                                                                            |
| Inicio   | 2 de Octubre                                                                                                                                                                |
| Cierre   | 5 de Octubre, 5:22 PM                                                                                                                                                       |

## 2. Participación y responsabilidades

| Integrante           | Asistió | Responsabilidad asumida                                                 | Aporte verificable                                                                             |
| -------------------- | :-----: | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Juliana Marín Vélez  |   Sí    | Elaborar y ejecutar el notebook, redactar el corpus propio del proyecto | Archivo `notebooks/C06_Busqueda_Semantica.ipynb`                                               |
| Sophie Rosero Muriel |   Sí    | Soporte en elaboración del notebook, pruebas y registro en bitácora     | Archivo `notebooks/C06_Busqueda_Semantica.ipynb` y `logs/C06_2026-10-05_Busqueda_Semantica.md` |

## 3. Reto aplicado al proyecto

### Funcionalidad trabajada

En esta clase adaptamos la demo del profesor a nuestro proyecto:

- Reemplazamos el corpus de soporte universitario por seis pasajes ficticios sobre *Report Generator* (informe ejecutivo, técnico, resumen periódico, catálogo de fuentes, datos incompletos y alcance del servicio). Cada pasaje guarda identificador, texto, procedencia y fecha de consulta.
- Mantuvimos el modelo `paraphrase-multilingual-MiniLM-L12-v2` con vectores normalizados, de modo que el producto punto equivale a la similitud coseno, y `K = 3`.
- Cambiamos la búsqueda literal para mostrar que ni `gerencia` ni `DS-1001` aparecen en el corpus.
- Escribimos una batería de cinco pruebas con el pasaje esperado definido antes de ejecutar: paráfrasis, coincidencia exacta, pregunta incompleta, dato que vive en la fuente y pregunta fuera de cobertura.

Esta clase solo recupera pasajes. No genera respuestas con ellos ni procesa documentos reales.

### Criterios de aceptación

- [x] El notebook acepta una consulta nueva, calcula su embedding y muestra el ranking con identificador, puntaje y texto.
- [x] La paráfrasis recupera el pasaje esperado entre los primeros `K`.
- [x] Para la pregunta fuera de cobertura leímos el texto recuperado y concluimos que no alcanza, sin usar un umbral automático.
- [x] Para la pregunta por la actualización de `DS-1001` distinguimos entre recuperar el procedimiento (P4) y obtener el dato (herramienta de la Clase 04).
- [x] La configuración (modelo, medida, `K`, corpus) quedó registrada para repetir el experimento.

### Archivos o componentes modificados

- `[notebooks/C06_Busqueda_Semantica.ipynb]`: demo del profesor adaptado al dominio (corpus, búsqueda literal, consulta, preguntas de la sección 7 y nueva batería de pruebas).
- `[logs/C06_2026-10-05_Busqueda_Semantica.md]`: redacción de la bitácora para la sexta clase de Electiva VI.

## 4. Decisiones técnicas

| Decisión                                                                                              | Razón                                                                                                                                                                     | Alternativa descartada                    |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Escribir un corpus de seis pasajes sobre nuestro propio proyecto                                      | La demo del profesor trataba de soporte universitario; reutilizarla no probaría nada sobre Report Generator                                                               | Dejar el corpus de la demo                |
| Conservar el modelo multilingüe `paraphrase-multilingual-MiniLM-L12-v2`                               | Nuestras consultas y pasajes están en español y es el modelo que se proporcionó; cambiarlo junto con el corpus no nos dejaría saber qué causó un cambio en los resultados | Probar otro modelo de embeddings          |
| No fijar un umbral de similitud para decidir si un pasaje sirve                                       | Con seis pasajes siempre hay un primer lugar aunque ninguno responda; el puntaje ordena, no mide certeza                                                                  | Descartar resultados bajo un puntaje fijo |
| Dejar los datos de una fuente (última actualización de `DS-1001`) en la herramienta y no en el corpus | Ese dato cambia y debe consultarse en el catálogo; un pasaje solo explica dónde mirar                                                                                     | Escribir fechas dentro de los pasajes     |
| Escribir la expectativa de cada prueba antes de ejecutar                                              | Sin predicción previa cualquier resultado parece razonable                                                                                                                | Ejecutar y luego decidir qué era correcto |

## 5. Problemas y soluciones

| Problema encontrado                                                            | Causa identificada                                                                                   | Solución aplicada                                                           | ¿Cómo se verificó?                                                            |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| La pregunta fuera de cobertura (tasa de retención) devolvió P3 primero (0.345) | El corpus no explica cálculos y siempre hay un "más cercano"; P3 y P2 comparten temática de informes | No se corrigió con un umbral; se leyó el texto y se concluyó que no alcanza | Lectura de P3 y P2 (ninguno menciona la tasa de retención ni cómo calcularla) |
## 6. Evidencias

| Tipo    | Descripción                                                  | Enlace o ruta                                     |
| ------- | ------------------------------------------------------------ | ------------------------------------------------- |
| Commit  | Subida de bitácora y notebook                                | https://github.com/sophie-muriel/report-generator |
| Captura | Búsqueda literal de `gerencia` y `DS-1001` sin coincidencias | ![[Pasted image 20261005225558.png]]              |
| Captura | Ranking de la paráfrasis (sección 6)                         | ![[Pasted image 20261005225617.png]]              |
| Captura | Preguntas de la sección 7 (tasa de retención y `DS-1001`)    | ![[Pasted image 20261005225658.png]]              |
| Captura | Batería de cinco pruebas con esperado y top-K                | ![[Pasted image 20261005225733.png]]              |
| Código  | Función `buscar` y batería `PRUEBAS`                         | Notebook, secciones 6 y 8                         |
#### 6. 1. Resultados de la batería (K = 3)

| # | Tipo | Esperado | Top 3 (puntaje) | ¿En top 3? | Lectura humana |
| - | ---- | -------- | --------------- | :--------: | -------------- |
| 1 | Paráfrasis | P1 | P1 0.566, P3 0.336, P2 0.278 | Sí | P1 sirve: dice "dirección" donde la pregunta dice "gerencia" |
| 2 | Coincidencia exacta | P2 | P2 0.729, P1 0.551, P4 0.394 | Sí | P2 lista los errores 5xx; P1 queda cerca (0.551) sin responder |
| 3 | Pregunta incompleta | P3 | P3 0.457, P1 0.385, P4 0.315 | Sí | P3 da la periodicidad en general (semanal o mensual), no la de un informe concreto |
| 4 | Dato que vive en la fuente | P4 | P4 0.609, P2 0.298, P1 0.231 | Sí | P4 explica dónde consultar, pero no trae la fecha; hace falta la herramienta |
| 5 | Fuera de cobertura | Ninguno | P3 0.345, P2 0.327, P1 0.252 | N/A | Ningún pasaje explica cómo calcular la tasa de retención |

## 7. Uso de inteligencia artificial

> [!important] Registrar la IA no reemplaza la explicación técnica. El equipo debe verificar, adaptar y comprender cualquier resultado utilizado.

| Herramienta     | Objetivo o pregunta                                                                                                                                                                                                                                                  | Qué se utilizó                                                    | Cómo se verificó                                                                                                                                                                                                                | Qué se modificó                                                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude y Gemini | Ayuda para adaptar la demo del profesor a Report Generator (específicamente el código de la nueva sección y en partes específicas como la sección #2, #4, y #5) y redactar el borrador de la bitácora (específicamente la sección #3 y partes de redacción en la #4) | Corpus, batería de pruebas y la plantilla de la bitácora/notebook | Se ejecutó el notebook, se contrastó cada expectativa con el resultado y con la plantilla, se leyó detalladamente el texto generado, y se comparó con los conocimiento que tenemos y los documentos/material previo de la clase | Redacción, algunas decisiones técnicas, y generalmente retoques. No se modificó el código ya que el generado fue exitoso y generalmente se ve bien |

## 8. Defensa técnica y retroalimentación

| Campo                     | Registro          |
| ------------------------- | ----------------- |
| Integrante que defendió   | [Nombre]          |
| Pregunta recibida         | [Pregunta]        |
| Respuesta resumida        | [Respuesta]       |
| Retroalimentación docente | [Observación]     |
| Mejora acordada           | [Acción concreta] |

## 9. Aprendizajes

- **Concepto comprendido:** que siempre existe un "más cercano" aunque ningún pasaje responda, y que el puntaje de similitud ordena pero no mide certeza. Por eso hay que leer el texto recuperado antes de decidir qué decir. Aplicado a nuestro proyecto: P4 puede salir primero para `DS-1001` y aun así no contener la fecha de actualización.
- **Algo que aún genera duda:** a partir de cuántos casos de prueba sería razonable fijar un umbral de similitud. Aquí los cuatro primeros lugares con respuesta quedaron entre 0.457 y 0.729 y el caso fuera de cobertura en 0.345, así que un umbral las habría separado, pero con cinco casos no sabemos si eso se sostiene.
- **Qué haríamos diferente:** agregar más preguntas fuera de cobertura (en particular una que comparta vocabulario con el corpus) y un caso con negación, que es donde la similitud suele fallar.

## 10. Revisión antes de entregar

- [x] Todos los integrantes registraron un aporte verificable.
- [x] Los enlaces y rutas de evidencia funcionan.
- [x] Los criterios de aceptación están actualizados.
- [x] El uso de IA fue declarado y verificado.
- [x] El equipo puede explicar las decisiones registradas.