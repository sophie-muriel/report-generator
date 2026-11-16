"""Servidor MCP propio de Report Generator: consulta de fuentes de datos ficticias.

Procede del punto 4 del notebook de la Clase 11 (antes se escribía como texto desde
una celda). Expone una sola herramienta de lectura, `consultar_fuente_datos`.
La aplicación lo inicia como subproceso por stdio; no abre puertos ni recibe claves.

Las fuentes DS-0000 son datos ficticios: no corresponden a ninguna empresa ni sistema real.
"""
from mcp.server import MCPServer
from pydantic import BaseModel, ConfigDict, Field

mcp = MCPServer("Fuentes de datos Report Generator")

FUENTES = {
    "DS-1001": {"nombre": "ventas_mensuales", "estado": "actualizada", "periodo": "2026-10",
                "ultima_actualizacion": "2026-11-02",
                "metricas": {"ingresos_cop": 152340000, "unidades_vendidas": 8410, "ticket_promedio_cop": 18114},
                "metricas_ausentes": ["margen_bruto"], "registros_faltantes": 0},
    "DS-1002": {"nombre": "inventario_bodegas", "estado": "incompleta", "periodo": "2026-10",
                "ultima_actualizacion": "2026-11-01",
                "metricas": {"existencias_unidades": 23100, "rotacion_dias": 31.5},
                "metricas_ausentes": [], "registros_faltantes": 14},
    "DS-1003": {"nombre": "atencion_clientes", "estado": "desactualizada", "periodo": "2026-08",
                "ultima_actualizacion": "2026-09-03",
                "metricas": {"tickets_atendidos": 1275, "tiempo_medio_respuesta_h": 6.2},
                "metricas_ausentes": [], "registros_faltantes": 0},
}


class Argumentos(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    codigo_fuente: str = Field(pattern=r"^DS-[0-9]{4}$")


class Registro(BaseModel):
    nombre: str
    estado: str
    periodo: str
    ultima_actualizacion: str
    metricas: dict[str, int | float]
    metricas_ausentes: list[str]
    registros_faltantes: int


class ResultadoFuente(BaseModel):
    codigo_fuente: str
    encontrada: bool
    registro: Registro | None
    fuente: str


@mcp.tool()
def consultar_fuente_datos(codigo_fuente: str) -> ResultadoFuente:
    "Consulta el estado actual de una fuente de datos ficticia por código DS-0000: estado, periodo, última actualización, métricas disponibles y ausentes, y registros faltantes. Solo lectura."
    codigo = Argumentos(codigo_fuente=codigo_fuente).codigo_fuente
    registro = FUENTES.get(codigo)
    return ResultadoFuente(codigo_fuente=codigo, encontrada=registro is not None,
                           registro=registro, fuente="fuentes_ficticias_report_generator")


if __name__ == "__main__":
    mcp.run(transport="stdio")
