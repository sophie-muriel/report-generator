"""Instala Filesystem MCP (servidor ya construido) en app/mcp_filesystem.

Se ejecuta una vez, fuera de la atención de preguntas (punto 4.b del notebook de la Clase 11).
Usa el Node 24 que trae el paquete `nodejs-wheel`, así que no exige Node en el sistema.

    python preparar_mcp.py
"""
import json
import sys
from importlib.metadata import version
from pathlib import Path

VERSION_NODE, VERSION_MCP_ARCHIVOS = "24.19.0", "2.2.0"
DESTINO = Path(__file__).resolve().parent / "mcp_filesystem"
PAQUETE_JSON = DESTINO / "node_modules/@modelcontextprotocol/server-filesystem/package.json"


def main() -> int:
    if version("nodejs-wheel") != VERSION_NODE:
        print(f"Instala nodejs-wheel=={VERSION_NODE} (está en requirements.txt).")
        return 1
    if PAQUETE_JSON.is_file() and json.loads(PAQUETE_JSON.read_text(encoding="utf-8"))["version"] == VERSION_MCP_ARCHIVOS:
        print("Filesystem MCP", VERSION_MCP_ARCHIVOS, "ya estaba instalado.")
        return 0
    from nodejs_wheel import npm
    proceso = npm(["install", "--prefix", str(DESTINO), "--save-exact", "--ignore-scripts", "--no-audit",
                   "--no-fund", "@modelcontextprotocol/server-filesystem@" + VERSION_MCP_ARCHIVOS],
                  return_completed_process=True)
    if proceso.returncode != 0 or not PAQUETE_JSON.is_file():
        print("No se pudo instalar Filesystem MCP. Revisa la salida de npm.")
        return 1
    print("Filesystem MCP", VERSION_MCP_ARCHIVOS, "instalado en", DESTINO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
