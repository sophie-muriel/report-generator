---
tipo: bitacora-clase
curso: Electiva VI
periodo: EAM-2026II
equipo: Juliofi
corte: 2
semana: "9"
clase: "9"
fecha: 2026-10-23
estado: completado
tags:
  - ai
  - bitácora
  - rag
  - evaluación
  - bm25
  - reranking
---
# Bitácora — Clase 9

## 1. Datos de la sesión

| Campo    | Registro                                                                                                                                                                                                                                                                                                                                        |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tema     | Mejora y evaluación del RAG: búsqueda híbrida (BM25 + semántica + RRF) y reranking                                                                                                                                                                                                                                                              |
| Objetivo | Medir si añadir BM25 con fusión RRF (opción B) y un reranker (opción C) mejora la evidencia que recibe el generador de *Report Generator* frente a la búsqueda semántica de la clase 08 (opción A), sin cambiar corpus, embeddings, prompt `rag_report_v3` ni modelo generativo. Decidir con un grupo de desarrollo y confirmar con una reserva |
| Proyecto | Report Generator                                                                                                                                                                                                                                                                                                                                |
| Inicio   | Octubre 23                                                                                                                                                                                                                                                                                                                                      |
| Cierre   | Octubre 25                                                                                                                                                                                                                                                                                                                                      |

## 2. Participación y responsabilidades

| Integrante           | Asistió | Responsabilidad asumida                                                  | Aporte verificable                                                                                       |
| -------------------- | :-----: | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| Juliana Marín Vélez  |   Sí    | Ejecución del notebook y pruebas de recuperación y generación (A, B y C) | `notebooks/C09_Evaluacion_RAG.ipynb` y `notebooks/Clase_09_Evidencia_Evaluacion_RAG_ReportGenerator.zip` |
| Sophie Rosero Muriel |   Sí    | Pruebas, verificación de resultados y registro en bitácora               | `logs/C09_2026-10-23_Evaluacion_RAG.md`                                                                  |

## 3. Reto aplicado al proyecto

### Funcionalidad trabajada

Sobre el mismo corpus de la clase 08 (6 fragmentos por párrafos, máx. 128 tokens, de `tipos_de_informe.md` y `reglas_de_borrador.md`, versión `1.0-ficticia`, huella `ff98b1398c56`) comparamos tres formas de elegir los 3 pasajes que recibe el generador:

- **A - semántica:** la función `clase08_buscar_fragmentos` de Supabase, sin cambios.
- **B - híbrida RRF:** BM25Okapi en memoria (k1 = 1.5, b = 0.75, sin stemming ni stopwords) fusionado con la semántica por RRF (constante 60).
- **C - híbrida + reranking:** los mismos candidatos de B reordenados con `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`.

Fijamos 4 preguntas de desarrollo (D1-D4), 2 de reserva (R1-R2) y 3 de comportamiento (C1-C3) con su evidencia anotada **antes** de ver los rankings; dev y reserva no comparten familia de pregunta (lo comprueba un `assert`). Medimos Precision@3, Recall@3, Hit@3, RR/MRR, cobertura y tiempo de recuperación. Generamos D2 con A y con B (2 llamadas a Groq) y revisamos las respuestas a mano contra las fuentes. Los casos C1-C3 solo se evaluaron en recuperación; no se generaron sus respuestas.

**Resultados de desarrollo (base de la decisión):**

| Opción                  | Precision@3 | Recall@3 | MRR  | Cobertura | Mediana recuperación |
| ----------------------- | ----------- | -------- | ---- | --------- | -------------------- |
| A - semántica           | 0.417       | 1.00     | 1.00 | 1.00      | ~152 ms              |
| B - híbrida RRF         | 0.417       | 1.00     | 1.00 | 1.00      | ~153 ms              |
| C - híbrida + reranking | 0.417       | 1.00     | 1.00 | 1.00      | ~1472 ms             |

- A, B y C **empatan en los cuatro casos** (RR, Recall y cobertura). Solo cambia qué fragmento completa el contexto (por ejemplo, en D1 B trae `reglas:parrafos:1` donde A trae `tipos:parrafos:5`), sin efecto en las métricas.
- Con 6 fragmentos, K = 3 y M = 10, los candidatos son todo el corpus y el contexto final cubre la mitad de él: desarrollo no puede distinguir las opciones. La Precision@3 está limitada por la anotación (máx. 0.667 en D1 y 0.333 en D2-D4, que tienen 2 y 1 fragmentos relevantes).

**Decisión: A.** Con un empate se conserva la opción más simple y barata. B añade unos pocos ms y C es ~10 veces más lenta sin mejorar ningún caso.

**Resultados de la reserva:**

| Opción                  | Precision@3 | Recall@3 | MRR  | Cobertura | Mediana recuperación |
| ----------------------- | ----------- | -------- | ---- | --------- | -------------------- |
| A - semántica           | 0.667       | 0.75     | 0.75 | 1.00      | ~144 ms              |
| B - híbrida RRF         | 0.500       | 0.667    | 1.00 | 0.75      | ~145 ms              |
| C - híbrida + reranking | 0.833       | 1.00     | 1.00 | 1.00      | ~1272 ms             |

| Caso                     | A                                                   | B                                                               | C                                            |
| ------------------------ | --------------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------- |
| R1 - `[DATO INCOMPLETO]` | Recall 0.5 - RR 0.5 (`reglas:2, reglas:1, tipos:4`) | Recall 1.0 - RR 1.0 (`reglas:1, 2, 0`)                          | Recall 1.0 - RR 1.0 (`reglas:1, 0, 2`)       |
| R2 - tipos de informe    | Recall 1.0 - cobertura 1.0 (`tipos:5, 3, 4`)        | **Recall 0.33 - cobertura 0.5** (`tipos:3, reglas:2, reglas:1`) | Recall 1.0 - cobertura 1.0 (`tipos:3, 4, 5`) |

- En R1, B y C llevan las dos partes de la regla partida (`parrafos:0` y `parrafos:1`), el caso que falló en la clase 08; A solo trae una.
- En R2, B **empeora** frente a A: deja fuera el informe técnico y parte del ejecutivo y mete dos fragmentos de reglas. Es la evidencia de que una mejora puede quitar lo que A ya traía. La causa está en la traza: `reglas:parrafos:1` (1.° en BM25, 6.° en semántica) y `tipos:parrafos:5` (1.° en semántica, 6.° en BM25) **empatan exactamente** en RRF (1/61 + 1/66 = 0,031545). El desempate por `chunk_id` ascendente pone `reglas…` antes que `tipos…`, y el informe técnico queda 4.°, fuera de los 3 pasajes.
- C fue la mejor en la reserva (Recall 1.0, MRR 1.0, cobertura 1.0) pero ~9 veces más lenta que A. Con solo 2 casos la diferencia no es concluyente y **no cambia la decisión**.
- **Limitación importante:** la reserva ya se había abierto en una ejecución anterior (sobre un corpus distinto, de 9 fragmentos, huella `0796fd6f213c`) y la decisión se reescribió después de reejecutar con el corpus de 6 fragmentos. Por eso la reserva no es independiente de la decisión; se registra para no sobrevalorar su veredicto. La protección del punto 7 solo detecta aperturas dentro de la misma sesión de Colab, así que no lo impidió. R1 y R2 quedan como **reserva comprometida**; la señal a favor de C se confirmará con preguntas de reserva nuevas.

**Comparación de respuestas (D2, A vs B):**

|                                  | A - semántica                                                           | B - híbrida RRF                   |
| -------------------------------- | ----------------------------------------------------------------------- | --------------------------------- |
| Contexto (F1, F2, F3)            | `reglas:0`, `reglas:1`, `reglas:2`                                      | `reglas:0`, `reglas:1`, `tipos:4` |
| Respuesta                        | «…la escribe como [DATO AUSENTE] en el lugar donde iría la cifra. [F1]» | Idéntica a la de A                |
| correcta / fiel / citas / estado | **No** / Sí / Sí / Sí                                                   | **No** / Sí / Sí / Sí             |
| Tokens (entrada + salida)        | 1159 + 76 = 1235                                                        | 1108 + 75 = 1183                  |
| Generación                       | 456 ms                                                                  | 369 ms                            |

Las dos respuestas omiten que «el borrador no reemplaza ese vacío con una estimación ni con el valor de otro periodo», aunque esa frase está en F1 (`reglas:parrafos:0`), que ambas recibieron. Es un fallo de **generación**, no de recuperación: las métricas de D2 son perfectas en las tres opciones y la respuesta sigue incompleta. Con las dos respuestas idénticas, esta prueba no muestra ninguna diferencia entre A y B.

### Criterios de aceptación

- [x] Las preguntas y su evidencia quedaron fijadas antes de ver los rankings; las familias de desarrollo y reserva no se repiten.
- [x] Las comprobaciones del punto 11 (RRF, métricas, tokenización, validador de citas) pasan.
- [x] Se registraron métricas de A, B y C en desarrollo y una decisión justificada.
- [ ] La reserva se abrió una sola vez y no se ajustó nada después (no: una ejecución anterior ya la había abierto; ver sección 5).
- [x] La revisión manual de las dos respuestas está completa (los 4 criterios con justificación).
- [x] Se registraron tiempos de recuperación y tokens informados por Groq.
- [ ] Generar y revisar las respuestas de los casos de comportamiento C1-C3 (puntos 8-10); en esta ejecución solo se evaluó su recuperación.
- [ ] Ampliar el conjunto a 12-20 casos para el segundo corte, con preguntas de reserva nuevas.

### Archivos o componentes modificados

- `notebooks/C09_Evaluacion_RAG.ipynb`: notebook del profesor adaptado a Report Generator. Se corrigieron el texto y las constantes heredadas del corpus de 9 fragmentos (huella, número de fragmentos, referencias a `parrafos:7/8`), se reescribió la decisión del punto 7 y la revisión manual del punto 10, y `revision_humana_completa` exige los cuatro criterios. En la revisión final se corrigieron textos que contradecían los resultados (D3 como regla partida, la negación de D2 «en otro fragmento»), se añadió la lectura de la reserva después del punto 7 y se documentaron la limitación del contrato y la elección de B para generar. Solo cambió texto en markdown: ninguna celda de código ni salida, así que el notebook sigue coincidiendo con el ZIP.
- `notebooks/Clase_09_Evidencia_Evaluacion_RAG_ReportGenerator.zip`: JSON con trazas y CSV de métricas de la ejecución final (25-oct-2026).
- `logs/C09_2026-10-23_Evaluacion_RAG.md`: esta bitácora.

## 4. Decisiones técnicas

| Decisión | Razón                                                                                                                                                    | Alternativa descartada |
|---|---|---|
| Elegir A (semántica) | En desarrollo A, B y C empatan en los 4 casos; con un empate se conserva la opción más simple y barata                                                   | B o C sin evidencia de mejora en desarrollo |
| No cambiar a C aunque ganó la reserva | La reserva confirma, no ajusta; además tiene solo 2 casos y C es ~9-10 veces más lenta                                                                   | Cambiar a C después de ver la reserva |
| Generar A vs B (no A vs C) | En D2 el contexto de C (`reglas:0, 1, 2`) es idéntico al de A, así que generar C repetiría la respuesta de A; B es la única variante con un contexto distinto (`tipos:4` en F3) y además es la más barata | Generar A vs C |
| Reescribir las descripciones del esquema (`Field`) respecto a la clase 08 | Se mantiene el prompt `rag_report_v3`, pero el contrato ya no es idéntico: las respuestas solo se comparan entre A y B, no con las cifras de la clase 08 | Copiar el esquema de la clase 08 exactamente |
| No corregir todavía el ejemplo `[F1, F2]` del esquema | Contradice la regla del prompt («una por corchete»), pero corregirlo obliga a regenerar respuestas y ZIP. En esta ejecución no tuvo efecto (ambas respuestas citan solo `[F1]`) y A y B comparten contrato | Cambiar el código y dejar las salidas desalineadas con el ZIP |
| Anotar D1, D3 y R2 por sección y no por marca textual | Es más simple para fragmentos cortos, pero marca como relevante toda la sección (limitación)                                                             | Reanotar después de ver los rankings (rompe la regla de no ajustar) |
| Dejar la mejora de fragmentación y stopwords para el segundo corte | Cambian el índice o la tokenización; mezclarlas invalidaría la comparación                                                                               | Aplicarlas en este notebook |

## 5. Problemas y soluciones

| Problema encontrado | Causa identificada | Solución aplicada | ¿Cómo se verificó? |
| ------------------- | ------------------ | ----------------- | ------------------ |
| El notebook decía 9 fragmentos, huella `0796fd6f213c`, 80 tokens y `parrafos:7/8`, y mostraba dos AVISO al ejecutarlo | Texto y constantes heredados de una versión anterior del índice (el mismo error ya corregido en la clase 08) | Se actualizaron constantes, comprobación de fragmentos y texto: 6 fragmentos, 128 tokens, `ff98b1398c56` | Reejecución completa desde cero: no aparecen los AVISO y el texto coincide con el README y la bitácora C08 |
| La decisión y la revisión manual describían resultados que el ZIP no contenía (mejoras de B en D3, C peor en D4, B con la negación) | Se habían redactado con una ejecución anterior de 9 fragmentos y no se reescribieron al reejecutar con 6 | Se reescribieron la decisión (A, por empate) y la revisión (A y B `correcta: False`) a partir del CSV y el JSON finales | Contraste de cada cifra con el CSV y de las respuestas con los fragmentos del JSON |
| `revision_humana_completa` podía dar `True` con criterios sin revisar | Solo comprobaba `correcta` | Ahora exige `correcta`, `fiel`, `citas_respaldan` y `estado_adecuado` | Reejecución del punto 11 con los cuatro criterios llenos |
| La reserva se había abierto antes de la decisión final | Ejecución previa sobre el corpus de 9 fragmentos | No se reutilizó para ajustar; se registra como limitación y la decisión se basa solo en desarrollo | Decisión escrita con los números de desarrollo; sección 3 |
| B empeora R2 (Recall 1.0 → 0.33) | BM25 puso `reglas:parrafos:1` primero (puntaje 5.84, contra 1.21 del segundo) y en RRF empató exactamente con `tipos:parrafos:5` (0,031545). El desempate alfabético por `chunk_id` dejó fuera el informe técnico. Por qué BM25 da 5.84 a ese fragmento sigue siendo una hipótesis: coincidencias en palabras comunes sin stopwords | No se corrigió: se registra como límite. El desempate es una regla fija del laboratorio y no se cambia después de ver la reserva | Rankings y puntajes RRF del JSON (`recorridos`, R2) |
| El notebook tenía textos que contradecían los resultados: D3 descrito como regla partida (está completo en `parrafos:5`) y la negación de D2 «en un fragmento distinto» (está en `parrafos:0`, igual que la marca) | Texto heredado del corpus de 80 tokens / 9 fragmentos | Se corrigió el markdown de los puntos 4, 6, 7, 8 y Trabajo del equipo; el `esperado` de D3 se aclara con una nota y no se edita en el código | Comparación con la tabla de fragmentos del punto 3 y con la revisión manual del punto 10 |
| El ejemplo del esquema (`[F1, F2]`) contradice la regla del prompt v3 (`[F1] [F2]`) | La descripción del campo `respuesta` se escribió con el formato que aceptaba el validador de la v2 | Documentado como limitación en el punto 9; se corrige en la próxima ejecución | Las dos respuestas generadas citan solo `[F1]`: no tuvo efecto en esta ejecución |
| La regla de `[DATO INCOMPLETO]` sigue partida entre `parrafos:0` y `parrafos:1` | Fragmentación por párrafos de la clase 07: el límite de 128 tokens corta la regla a mitad de frase | Pendiente para el segundo corte | R1: solo B y C traen las dos partes |
| A y B omiten la negación en D2 aunque la tienen en F1 | Fallo de generación del modelo, no de recuperación | No se corrigió; se registra | Revisión manual de las dos respuestas |

## 6. Evidencias

| Tipo    | Descripción                                                  | Enlace o ruta                                                                                                |
| ------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| Commit  | Notebook, ZIP de evidencia y bitácora de la clase 09         | https://github.com/sophie-muriel/report-generator                                                            |
| Código  | Notebook de la práctica                                      | `notebooks/C09_Evaluacion_RAG.ipynb`                                                                         |
| Archivo | Métricas por caso y trazas (ejecución final del 25-oct-2026) | `notebooks/Clase_09_Evidencia_Evaluacion_RAG_ReportGenerator.zip`                                            |
| Captura | Tabla de desarrollo y agregados del punto 6                  | ![[Pasted image 20261025150029.png]]![[Pasted image 20261025150045.png]]![[Pasted image 20261025150057.png]] |
| Captura | Tabla de reserva del punto 7 (R2: B pierde evidencia)        | ![[Pasted image 20261025150118.png]]![[Pasted image 20261025150126.png]]![[Pasted image 20261025150135.png]] |
| Captura | Respuestas A y B de D2 y revisión manual del punto 10        | ![[Pasted image 20261025150156.png]]                                                                         |
| Demo    | N/A                                                          | N/A                                                                                                          |

## 7. Uso de inteligencia artificial

> [!important] Registrar la IA no reemplaza la explicación técnica. El equipo debe verificar, adaptar y comprender cualquier resultado utilizado.

| Herramienta | Objetivo o pregunta | Qué se utilizó | Cómo se verificó | Qué se modificó |
| ----------- | ------------------- | -------------- | ---------------- | --------------- |
| Claude | Revisar el notebook y el ZIP frente al notebook del profesor, el README y la bitácora C08 | Detectó texto y constantes de 9 fragmentos, una revisión manual que no coincidía con las respuestas reales y una decisión no sustentada por el CSV | Comparamos cada observación con el CSV/JSON y con el texto de los fragmentos | Constantes y texto del notebook, decisión del punto 7, revisión del punto 10, `limites` y la descripción del contrato |
| Claude | Segunda revisión del notebook frente al del profesor (25-oct) | Detectó textos que contradecían los resultados (D3, negación de D2), la contradicción prompt/esquema en el formato de citas y la causa de la caída de B en R2 (empate exacto en RRF y desempate alfabético) | Recalculamos 1/61 + 1/66 y comparamos con `puntaje_rrf` del JSON; revisamos los fragmentos del punto 3 | Markdown de los puntos 4, 6, 7, 8 y 9, celda nueva «Lectura de la reserva» y esta bitácora |
| Claude | Redactar esta bitácora a partir del ZIP final | Estructura, tablas de resultados y redacción de límites | Contrastamos cada cifra con el CSV final y las respuestas con los fragmentos del JSON | [Ajustes propios del equipo a la redacción] |
| Claude | Proponer mejoras para el segundo corte (BM25 con stopwords, fragmentos por sección) | Ideas de mejora | Solo se usan como hipótesis: no se midieron sobre el corpus final de 6 fragmentos | Ninguna en esta entrega |

## 8. Defensa técnica y retroalimentación

| Campo                     | Registro |
| ------------------------- | -------- |
| Integrante que defendió   | [Nombre] |
| Pregunta recibida         | [Pregunta] |
| Respuesta resumida        | [Respuesta] |
| Retroalimentación docente | [Observación] |
| Mejora acordada           | [Acción concreta] |

## 9. Aprendizajes

- **Concepto comprendido:** con un corpus tan pequeño (6 fragmentos, K = 3) el desarrollo no puede distinguir las opciones: las tres empatan y el MRR es 1.0 en todas. Un empate es un resultado válido y se resuelve con la opción más simple. La reserva sí mostró diferencias, pero con 2 casos no es concluyente.
- **Concepto comprendido:** «híbrido» no significa «mejor». B arregló el orden y el Recall de R1 y, en la misma reserva, perdió evidencia en R2 (Recall 1.0 → 0.33). Una mejora puede ayudar en un caso y quitar lo que ya funcionaba en otro.
- **Concepto comprendido:** una recuperación perfecta no garantiza una respuesta correcta. En D2 las tres opciones llevaron la frase necesaria a F1 y aun así A y B la omitieron. La métrica de recuperación no reemplaza la revisión manual.
- **Algo que aún genera duda:** por qué el modelo descarta una frase que tiene en el mismo fragmento (si se corrige con una regla en el prompt, con ejemplos o subiendo `reasoning_effort`), y por qué BM25 da 5.84 a `reglas:parrafos:1` en R2 (¿palabras comunes sin stopwords?). La caída de B en R2 ya está explicada por el empate en RRF, pero el puntaje BM25 que lo provoca no.
- **Qué haríamos diferente:** regenerar siempre la decisión, la revisión y la bitácora a partir del ZIP final antes de entregar, y no reutilizar texto de una ejecución anterior. Para el segundo corte: ampliar a 12-20 casos, anotar la evidencia por marca textual en vez de por sección, probar fragmentación por sección y BM25 con stopwords (conservando «no», «ni», «sin»), y usar una reserva nueva para medirlo. También revisar los empates de RRF: con corpus pequeños son frecuentes, y un desempate alfabético decide qué fragmento entra.

## 10. Revisión antes de entregar

- [x] Todos los integrantes registraron un aporte verificable.
- [x] Los enlaces y rutas de evidencia funcionan.
- [x] Los criterios de aceptación están actualizados.
- [x] El uso de IA fue declarado y verificado.
- [x] El equipo puede explicar las decisiones registradas.