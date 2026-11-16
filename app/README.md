# app/ · Report Generator

Instrucciones completas de instalación, configuración, despliegue y pruebas: [README de la raíz](README.md).

```text
app.py              Interfaz Gradio: login Supabase Auth, conversaciones, chat, fuentes, borrador
sistema.py          RAG, contrato Decision, validaciones, agente atender(), clientes MCP
almacenamiento.py   Historial por usuario en Supabase (conversaciones, mensajes)
servidor_mcp.py     MCP propio: consultar_fuente_datos (solo lectura, datos ficticios)
preparar_mcp.py     Instala Filesystem MCP 2.2.0 (una vez)
config_corpus.json  Corpus, embeddings y recuperación vigentes (sin secretos)
sql/                01_historial.sql, 02_corpus_compartido.sql
tests/              Pruebas locales (pytest)
pruebas_rls.py      Persistencia y aislamiento con dos usuarios reales
.env.ejemplo        Plantilla de variables
```

Arranque rápido desde `app/` (con `.venv` en la raíz y `app/.env` completo):

```bash
../.venv/bin/python preparar_mcp.py   # una vez
../.venv/bin/python -m pytest -q      # pruebas locales
../.venv/bin/python app.py            # http://127.0.0.1:7860
```
