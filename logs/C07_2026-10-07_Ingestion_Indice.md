---
tipo: bitacora-clase
curso: Electiva VI
periodo: EAM-2026II
equipo: Juliofi
corte: 2
semana: "7"
clase: "7"
fecha:
  - 2026-10-07
estado: completado
tags:
  - ai
  - bitácora
  - embeddings
  - fragmentación
---
# Bitácora — Clase 7

> [!tip] Cómo usar esta plantilla
> Duplica esta nota al finalizar cada clase y nómbrala `C##_AAAA-MM-DD_Tema`. Completa los campos entre corchetes y conserva enlaces verificables.

## 1. Datos de la sesión

| Campo    | Registro                                                                                                                                                                              |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tema     | Ingesta de documentos, fragmentación e índice                                                                                                                                         |
| Objetivo | Preparar documentos propios, compararlos en dos estrategias de fragmentación, guardar un índice con sus metadatos y comprobar que al volver a cargarlo devuelve los mismos resultados |
| Proyecto | Report Generator                                                                                                                                                                      |
| Inicio   | Octubre 6, 2026                                                                                                                                                                       |
| Cierre   | Octubre 7, 2026 - 7:00 PM                                                                                                                                                             |

## 2. Participación y responsabilidades

| Integrante           | Asistió | Responsabilidad asumida                                                 | Aporte verificable                                                                         |
| -------------------- | :-----: | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Juliana Marín Vélez  |   Sí    | Elaborar y ejecutar el notebook, redactar los dos documentos del corpus | Archivo `notebooks/C07_Ingestion_Indice.ipynb`                                             |
| Sophie Rosero Muriel |   Sí    | Soporte en el notebook, pruebas y registro en bitácora                  | Archivo `notebooks/C07_Ingestion_Indice.ipynb` y `logs/C07_2026-10-07_Ingestion_Indice.md` |

## 3. Reto aplicado al proyecto

### Funcionalidad trabajada

- Redactamos los documentos `tipos_de_informe.md` y `reglas_de_borrador.md`, con título, versión `1.0-ficticia`, origen y huella SHA-256 del original.
- Limpiamos espacios y líneas repetidas sin tocar párrafos, negaciones ni condiciones.
- Implementamos dos estrategias de fragmentación con el mismo modelo, presupuesto de tokens y medida de búsqueda: *ventanas* (por tokens, con solapamiento de 12) y *párrafos* (respeta sus límites y solo divide los que no caben).
- Cada fragmento conserva archivo, sección, versión, huella y número de tokens, para poder volver a la fuente.
- Comparamos las dos estrategias con cuatro preguntas y guardamos el índice elegido (vectores, registros y configuración). Lo volvimos a cargar y comprobamos que devuelve los mismos fragmentos y puntajes.

### Criterios de aceptación

- [x] Los dos documentos se leen desde archivos y se limpian conservando párrafos y condiciones.
- [x] Ningún fragmento supera el límite del modelo (máximo 126 tokens de 128).
- [x] Cada fragmento permite volver al archivo y la sección de origen.
- [x] El índice guardado, al cargarse, devuelve los mismos fragmentos y puntajes (`assert` en el notebook).
- [x] Las dos estrategias se compararon con la misma consulta y las mismas cuatro preguntas.
- [x] Para la pregunta fuera de cobertura leímos el texto recuperado y concluimos que no alcanza, sin usar un umbral.
- [x] La configuración (modelo, revisión, estrategia, tokens, solapamiento) quedó guardada en el ZIP.

### Archivos o componentes modificados

- `[notebooks/C07_Ingestion_Indice.ipynb]`: demo del profesor adaptado al proyecto (corpus propio, celda con las cuatro preguntas y la comprobación de condición y consecuencia, sección 7 con resultados).
- `[notebooks/Clase_07_Indice_y_Corpus.zip]`: índice guardado y documentos del corpus.
- `[logs/C07_2026-10-07_Ingestion_Indice.md]`: redacción de la bitácora para la séptima clase de Electiva VI.

## 4. Decisiones técnicas

| Decisión | Razón | Alternativa descartada |
| -------- | ----- | ---------------------- |
| Escribir dos documentos propios sobre Report Generator | Los de la demo eran de otro dominio; reutilizarlos no probaba nada de nuestro proyecto | Dejar los documentos de la demo |
| Subir `MAX_TOKENS` de 80 a 128 | Con 80 las dos estrategias dieron 9 fragmentos cada una y casi idénticos, así que la comparación no decía nada. 128 es el límite real del modelo | Dejar 80, o usar 130 (supera el límite de 128; el código usa el menor, pero la configuración guardada habría dicho 130) |
| Elegir la estrategia de párrafos | Con 128 la sección ejecutiva queda en dos fragmentos y la regla del periodo no cerrado se recupera sola (0.408). La pregunta de la gerencia puntuó un poco más (0.580 contra 0.556) | Ventanas. Para `reglas_de_borrador` ambas dan lo mismo, así que no hubo razón para preferirla |
| No fijar un umbral de similitud | La pregunta fuera de cobertura sacó 0.329 y las que sí tenían respuesta entre 0.550 y 0.674, pero con cuatro casos no sabemos si esa separación se sostiene | Descartar resultados por debajo de un puntaje |
| Dejar la fecha de actualización de `DS-1001` en la herramienta y no en el corpus | Ese dato cambia y debe consultarse en el catálogo; el pasaje solo explica dónde mirar | Escribir fechas dentro de los documentos |
| Escribir la evidencia esperada de cada pregunta antes de ejecutar | Sin predicción previa cualquier resultado parece razonable | Ejecutar y decidir después qué era correcto |

## 5. Problemas y soluciones

| Problema encontrado                                                          | Causa identificada                                                                                                                                          | Solución aplicada                                                                                     | ¿Cómo se verificó?                                                                                                        |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Las dos estrategias daban casi lo mismo                                      | Con 80 tokens los párrafos largos se dividían igual que en ventanas                                                                                         | Subir el presupuesto a 128                                                                            | Con 128 el resultado fue 5 fragmentos (ventanas) y 6 (párrafos), y la sección ejecutiva se separa en párrafos             |
| `MAX_TOKENS = 130` quedaba por encima del límite del modelo                  | El modelo lee 128 tokens; el código toma el menor de los dos, pero la configuración guardada decía 130                                                      | Poner `MAX_TOKENS = 128`                                                                              | El máximo por fragmento fue 126 y la configuración guardada dice 128                                                      |
| La condición de una regla y su consecuencia quedaron en fragmentos distintos | El primer párrafo de `reglas_de_borrador` ocupa casi todo el presupuesto, el corte cae en `[DATO INCOMPLETO ` y la consecuencia pasa al fragmento siguiente | No se corrigió: se documentó como fallo. El solapamiento repite `[DATO INCOMPLETO]` en el fragmento 1 | La comprobación de la pregunta 1 dio `condición: True` y `consecuencia: False` en el mejor resultado de ambas estrategias |
| Aviso `134 > 128` al fragmentar                                              | Se cuentan los tokens de un párrafo completo antes de dividirlo                                                                                             | No requiere cambio                                                                                    | Ningún embedding se calcula sobre ese texto; el máximo por fragmento fue 126                                              |

## 6. Evidencias

| Tipo    | Descripción                                                      | Enlace o ruta                                     |
| ------- | ---------------------------------------------------------------- | ------------------------------------------------- |
| Commit  | Subida de bitácora, notebook y ZIP del índice                    | https://github.com/sophie-muriel/report-generator |
| Captura | Fragmentos de las dos estrategias (5 y 6, máximo 126 tokens)     | ![[Pasted image 20261007192847.png]]              |
| Captura | Ranking de la consulta sobre métricas incompletas                | ![[Pasted image 20261007192913.png]]              |
| Captura | Las cuatro preguntas en las dos estrategias                      | ![[Pasted image 20261007192930.png]]              |
| Captura | Comprobación de condición y consecuencia (`consecuencia: False`) | ![[Pasted image 20261007192957.png]]              |
| Código  | Funciones `ventanas`, `fragmentar` y `buscar`                    | Notebook, secciones 4 y 5                         |

### 6.1. Resultados de la comparación (K = 3)

| Pregunta | Evidencia esperada | Ventanas | Párrafos |
|---|---|---|---|
| ¿Puedo presentar como verificada una métrica a la que le faltan días de datos? | reglas_de_borrador · Datos ausentes e incompletos | Sí: fragmento 0 (0.674) trae la condición; la consecuencia está en el 1 (0.589), empatado con el de Catálogo (0.589) | Igual, mismos fragmentos y puntajes |
| Necesito el documento para la gerencia con las cifras más importantes | tipos_de_informe · Informe ejecutivo | Sí: fragmento 3 (0.556) | Sí: fragmento 3 (0.580); el párrafo de "cifras parciales" queda aparte (fragmento 4, 0.408) |
| ¿Cuál es la última actualización de DS-1001? | reglas_de_borrador · Catálogo de fuentes (explica dónde consultar, no trae la fecha) | Sí: fragmento 2 (0.550); no trae la fecha | Igual (0.550) |
| ¿Cómo calculo la tasa de retención de clientes? | Ninguno: fuera de cobertura | Devuelve Informe técnico (0.329) aunque no responde | Igual (0.329) |

## 7. Uso de inteligencia artificial

> [!important] Registrar la IA no reemplaza la explicación técnica. El equipo debe verificar, adaptar y comprender cualquier resultado utilizado.

| Herramienta | Objetivo o pregunta                                                                                                                                | Qué se utilizó                                                                                                                            | Cómo se verificó                                                                      | Qué se modificó                                                         |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Claude      | Revisar si el notebook (elaborado manualmente) cumplía lo pedido, explicar cada paso y ayudar a redactar la sección 7 del notebook y esta bitácora | Lectura del notebook con sus salidas, texto propuesto para los resultados, el fallo y la estrategia elegida, y el borrador de la bitácora | Se contrastó cada puntaje y cada número de fragmento contra las salidas del notebook. | Ajustamos la redacción de las secciones 3 y 4 y las decisiones técnicas |

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

- **Concepto comprendido:** que la forma de cortar los documentos decide lo que la búsqueda puede devolver. En nuestro caso la condición de una regla (`[DATO INCOMPLETO]`) y su consecuencia ("no se presenta como verificada") quedaron en fragmentos distintos, y el que tenía la consecuencia empató con uno que no respondía la pregunta. Con un K pequeño habría quedado fuera. También que un buen resultado en una pregunta no demuestra que la estrategia sea mejor: con dos documentos y cuatro preguntas solo podemos describir diferencias pequeñas.
- **Algo que aún genera duda:** cómo cortar sin separar una condición de su consecuencia cuando un párrafo ya ocupa casi todo el presupuesto (por ejemplo por oraciones, o con un solapamiento mayor). Tampoco sabemos si la prueba de `DS-1001` sirve para probar búsqueda semántica, porque el código aparece literalmente en el pasaje.
- **Qué haríamos diferente:** añadir una pregunta por `DS-1001` con palabras distintas a las del corpus, probar `K` más pequeños con la pregunta de las métricas incompletas y repetir la comparación con documentos más largos, donde las dos estrategias sí se separen.

## 10. Revisión antes de entregar

- [x] Todos los integrantes registraron un aporte verificable.
- [x] Los enlaces y rutas de evidencia funcionan.
- [x] Los criterios de aceptación están actualizados.
- [x] El uso de IA fue declarado y verificado.
- [x] El equipo puede explicar las decisiones registradas.