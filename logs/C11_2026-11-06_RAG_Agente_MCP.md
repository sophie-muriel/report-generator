---
tipo: bitacora-clase
curso: Electiva VI
periodo: EAM-2026II
equipo: Juliofi
corte: 3
semana: "11"
clase: "11"
fecha: 2026-11-10
estado: completado
tags:
  - ai
  - bitácora
  - rag
  - agente
  - mcp
  - memoria
---
# Bitácora — Clase 11

## 1. Datos de la sesión

| Campo    | Registro                                                                                                                                                                                                                                                                                                                             |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Tema     | Integración del RAG con un agente, memoria de conversación y herramientas por MCP real (stdio)                                                                                                                                                                                                                                       |
| Objetivo | Atender desde una sola entrada consultas documentales (RAG de la clase 09) y de estado de fuentes de datos ficticias `DS-0000` (MCP propio), y, con permiso explícito, guardar un borrador de informe sustentado en el RAG mediante Filesystem MCP. Sin cambiar el corpus, los embeddings ni la recuperación decidida en la clase 09 |
| Proyecto | Report Generator                                                                                                                                                                                                                                                                                                                     |
| Inicio   | Noviembre 6                                                                                                                                                                                                                                                                                                                          |
| Cierre   | Noviembre 10                                                                                                                                                                                                                                                                                                                         |

## 2. Participación y responsabilidades

| Integrante           | Asistió | Responsabilidad asumida | Aporte verificable |
| -------------------- | :-----: | ----------------------- | ------------------ |
| Juliana Marín Vélez  |   Sí    | Adaptación y ejecución del notebook (MCP de fuentes, Filesystem MCP y agente) | `notebooks/C11_RAG_Agente_MCP.ipynb` y `notebooks/Clase_11_Evidencia_Integracion_ReportGenerator.json` |
| Sophie Rosero Muriel |   Sí    | Pruebas, revisión manual del borrador y registro en bitácora | `logs/C11_2026-11-06_RAG_Agente_MCP.md` |

## 3. Reto aplicado al proyecto

### Funcionalidad trabajada

Un agente (`openai/gpt-oss-20b` en Groq, salida JSON estricta validada con Pydantic) decide en cada turno entre `buscar_documentos` (RAG, recuperación **A - semántica**, K = 3), `consultar_fuente_datos` (MCP propio de solo lectura sobre `DS-1001`, `DS-1002` y `DS-1003`), `guardar_informe` (Filesystem MCP 2.2.0), `responder`, `aclarar` y `rechazar`. Presupuesto por turno: 3 decisiones, 2 operaciones y 90 s. Memoria volátil de 4 turnos por conversación.

Guardar exige permiso explícito (`GUARDAR_INFORME`) y citas `F` del turno actual. La ruta la fija la aplicación, el archivo se relee por MCP para verificarlo y la confirmación la redacta el programa. De las 16 herramientas que publica Filesystem MCP solo se habilitan `write_file` y `read_text_file`, y una lectura fuera de la carpeta fue rechazada.

**Comprobaciones locales (punto 8):** todas pasan: MCP real, código desconocido sin error técnico, argumento inválido rechazado, informe sin fuentes o sin permiso bloqueado, y aislamiento, reinicio y límites de memoria correctos.

**Resultado del punto 7** (ejecución del 10-nov-2026, permiso activado): "¿qué partes debe tener un informe ejecutivo y qué se escribe si falta una métrica? Guarda un informe…"

| Campo             | Registro                                                                |
| ----------------- | ----------------------------------------------------------------------- |
| Estado            | `RESPONDER`, 2 decisiones y 2 operaciones                               |
| Recorrido         | `buscar_documentos` → `guardar_informe` → `RESPUESTA_DEL_PROGRAMA`      |
| Consulta generada | "partes informe ejecutivo y cómo indicar métrica faltante"              |
| Fragmentos        | F1 `tipos:parrafos:3`, F2 `tipos:parrafos:4`, F3 `reglas:parrafos:0`    |
| Archivo           | `informe_9750aede69f64c1883b3035d1420b3e0.md`, verificado por relectura |
| Tokens            | 1331 + 299 y 2126 + 208 = **3964**                                      |
| Duración          | 3263 ms                                                                 |

**Revisión manual del borrador:** correcto, fiel y con las citas que lo respaldan. Nombra las cuatro partes del informe ejecutivo [F1], añade la advertencia de cifras parciales [F2] y escribe `[DATO AUSENTE]` "sin sustituirla por una estimación ni por el valor de otro periodo" [F3]. **Es la negación que A y B omitieron en D2 en la clase 09.** Es una sola ejecución y el prompt se ajustó con esta misma pregunta, así que no prueba que el problema esté resuelto.

`revisar_borrador` marcó `negacion_estimacion = True`, pero la expresión `\bno\b[^.]*estimaci` coincidió con "no está disponible…", no con el "sin sustituirla". Una frase con "sin… estimación" y sin un "no" antes daría `False`. En esta ejecución el resultado es correcto por la revisión manual, no por el control.

**Batería de casos (8.b), Clase 11**: ejecutada con `openai/gpt-oss-20b`, recuperación A_semantica, pausa de 30 s. Coincidencia automática: **4/8**.

- **Cumplidos (B1, B2, B3, B6):** informe con RAG + escritura MCP verificada (B1); sin permiso no guarda ni afirma haberlo hecho (B2); aclara el límite sin guardar cuando el corpus no responde (B3); no hereda el código de otra conversación (B6).
- **B4:** esperado RESPONDER, observado `REPETICION_SIN_AVANCE`. Tras consultar DS-1001 el modelo repitió la misma operación. Limitación registrada.
- **B5:** falla derivada de B4: el turno no terminó, así que no quedó código en memoria.
- **B7:** esperado RECHAZAR, observado ACLARAR. No ejecutó ninguna acción, pero no rechazó explícitamente.
- **B8:** esperado LIMITE_OPERACIONES/ACLARAR, observado `ERROR_VALIDACION`. El control bloqueó la escritura sin evidencia documental; no se guardó archivo ni se inventó ninguna cifra.
- **Decisión:** no se modificó el prompt ni los esperados tras ver los resultados. Cualquier ajuste requiere casos nuevos.
- **Revisión humana:** pendiente de contrastar cada respuesta con sus fuentes.

### Criterios de aceptación

- [x] Los dos servidores MCP se descubren; solo se habilitan las herramientas previstas y se rechaza el acceso fuera de la carpeta.
- [x] Las comprobaciones locales del punto 8 pasan.
- [x] El punto 7 sigue `buscar_documentos` → `guardar_informe` y el borrador queda verificado.
- [x] El borrador conserva `[DATO AUSENTE]` y la negación (revisión manual).
- [x] Ejecutar la batería B1-B8, incluida la prueba sin permiso y el límite de operaciones, y revisar cada respuesta a mano.
- [ ] Corregir `revisar_borrador` para que detecte "sin… estimación", con casos nuevos.

### Archivos o componentes modificados

- `notebooks/C11_RAG_Agente_MCP.ipynb`: notebook del profesor adaptado. Incluye el MCP de fuentes `DS-0000`, la acción `guardar_informe` con Filesystem MCP, la recuperación A por defecto, el ejemplo de citas "una por corchete" y la batería B1-B8.
- `notebooks/Clase_11_Evidencia_Integracion_ReportGenerator.json`: catálogos, límites, comprobaciones y traza del punto 7.
- `notebooks/informes/informe_9750aede69f64c1883b3035d1420b3e0.md`: borrador generado.
- `logs/C11_2026-11-06_RAG_Agente_MCP.md`: esta bitácora.

## 4. Decisiones técnicas

| Decisión | Razón | Alternativa descartada |
| -------- | ----- | ---------------------- |
| Mantener la recuperación A | Es la decisión de la clase 09; B queda disponible desde el punto 2 | Usar la híbrida de la demo sin evidencia nueva |
| MCP propio `consultar_fuente_datos`, solo lectura | Es la operación que nombran nuestros documentos; no hay funciones para modificar ni enviar | Conservar las solicitudes ficticias de la demo |
| Habilitar solo `write_file` y `read_text_file` | Crear y verificar un borrador es todo lo necesario | Exponer las 16 herramientas del servidor |
| La aplicación fija la ruta y exige permiso + citas del turno | El modelo no elige rutas ni guarda sin evidencia; la memoria no es evidencia | Dejar que el modelo nombre el archivo |
| El programa redacta la confirmación | El archivo ya está verificado y así se ahorra una llamada | Pedir una tercera decisión al modelo |
| Conservar 2 operaciones por turno | Ampliarlo sin pruebas cambia lo que medimos; un borrador con cifras de una fuente (3 operaciones) queda como limitación | Subir el límite antes de tener casos |

## 5. Problemas y soluciones

| Problema encontrado                                                                   | Causa identificada                                                      | Solución aplicada                                    | ¿Cómo se verificó?               |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------- | -------------------------------- |
| Revisar la negación en todo el archivo daba un falso positivo                         | El pie fijo del borrador ya menciona las estimaciones                   | `revisar_borrador` solo revisa la sección "Borrador" | Traza del punto 7                |
| `negacion_estimacion` acierta por la razón equivocada                                 | La expresión busca "no … estimaci" y coincidió con "no está disponible" | Pendiente; se confía en la revisión manual           | Lectura del borrador frente a F3 |
| Un borrador con cifras de una fuente supera el presupuesto                            | RAG + fuente + escritura = 3 operaciones (límite 2)                     | Se registra como limitación                          | Pendiente (B8)                   |
| Con permiso desactivado, un `guardar_informe` propuesto termina en `ERROR_VALIDACION` | La validación lanza error en lugar de pedir otra decisión               | Pendiente                                            | Pendiente (B2)                   |

## 6. Evidencias

| Tipo    | Descripción                                                     | Enlace o ruta                                                    |
| ------- | --------------------------------------------------------------- | ---------------------------------------------------------------- |
| Commit  | Notebook, evidencia, borrador y bitácora                        | https://github.com/sophie-muriel/report-generator                |
| Archivo | Evidencia de la ejecución (10-nov-2026)                         | `notebooks/Clase_11_Evidencia_Integracion_ReportGenerator.json`  |
| Archivo | Borrador del punto 7                                            | `notebooks/informes/informe_9750aede69f64c1883b3035d1420b3e0.md` |
| Captura | Catálogos MCP, recorrido del punto 7 y comprobaciones           | ![[Pasted image 20261111181616.png]]                             |
| Captura | Resultados de la ejecución de la batería de casos con el modelo | ![[Pasted image 20261111181512.png]]                             |

## 7. Uso de inteligencia artificial

> [!important] Registrar la IA no reemplaza la explicación técnica. El equipo debe verificar, adaptar y comprender cualquier resultado utilizado.

| Herramienta | Objetivo o pregunta | Qué se utilizó | Cómo se verificó | Qué se modificó |
| ----------- | ------------------- | -------------- | ---------------- | --------------- |
| Claude | Redactar la bitácora a partir del notebook y del JSON de evidencia | Estructura, tablas y riesgos detectados en el código (falso acierto de `negacion_estimacion`, `ERROR_VALIDACION` sin permiso) | Contrastamos cada cifra con el JSON y el borrador con F1-F3 | [Ajustes propios del equipo] |

## 8. Defensa técnica y retroalimentación

| Campo                     | Registro |
| ------------------------- | -------- |
| Integrante que defendió   | [Nombre] |
| Pregunta recibida         | [Pregunta] |
| Respuesta resumida        | [Respuesta] |
| Retroalimentación docente | [Observación] |
| Mejora acordada           | [Acción concreta] |

## 9. Aprendizajes

- **Concepto comprendido:** el agente es la coordinación entre modelo y programa. El modelo propone, el programa valida, ejecuta solo lo permitido y devuelve el resultado.
- **Concepto comprendido:** con MCP el notebook es el anfitrión que decide qué herramientas habilitar. Que un servidor publique 16 no significa que el agente deba usarlas.
- **Concepto comprendido:** un control automático puede acertar por la razón equivocada. `negacion_estimacion` dio `True` por una frase distinta; la revisión manual sigue siendo necesaria.
- **Algo que aún genera duda:** si la negación aparece ahora por el prompt de la clase 11 o por haber ajustado el prompt con esta misma pregunta. La batería lo dirá.
- **Qué haríamos diferente:** ejecutar la batería en la misma sesión que el punto 7, antes de exportar la evidencia.

## 10. Revisión antes de entregar

- [x] Todos los integrantes registraron un aporte verificable.
- [x] Los enlaces y rutas de evidencia funcionan.
- [x] Los criterios de aceptación están actualizados.
- [x] El uso de IA fue declarado y verificado.
- [x] El equipo puede explicar las decisiones registradas.
