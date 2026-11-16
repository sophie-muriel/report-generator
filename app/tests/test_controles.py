"""Pruebas locales: no consumen Groq ni necesitan Supabase.

Portan las comprobaciones del punto 8 del notebook de la Clase 11 y añaden las de almacenamiento.
Ejecutar desde app/:   python -m pytest -q

Las pruebas de aislamiento entre usuarios con Supabase real están en pruebas_rls.py.
"""
import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sistema  # noqa: E402
from almacenamiento import AccesoDenegado, Almacenamiento, historial_para_modelo, titulo_desde_pregunta  # noqa: E402
from sistema import Decision, Detencion, codigos_permitidos, controlar_operacion, fusionar_rrf, validar_decision  # noqa: E402


@pytest.fixture(scope="module")
def recursos():
    return sistema.Recursos(cargar_modelo=False, exigir_servicios=False)


# ---------------------------------------------------------------- MCP propio (proceso real por stdio)

def test_mcp_catalogo_una_sola_herramienta(recursos):
    catalogo = asyncio.run(recursos.descubrir_mcp())
    assert catalogo["nombre"] == "consultar_fuente_datos"


def test_mcp_fuente_conocida_y_desconocida(recursos):
    conocida = asyncio.run(recursos.consultar_fuente("DS-1001"))
    assert conocida["encontrada"] and "margen_bruto" in conocida["registro"]["metricas_ausentes"]
    desconocida = asyncio.run(recursos.consultar_fuente("DS-9999"))
    assert desconocida["encontrada"] is False and desconocida["registro"] is None


def test_mcp_argumento_invalido_rechazado(recursos):
    async def llamar():
        async with recursos.conexion_mcp() as conexion:
            return await conexion.call_tool("consultar_fuente_datos", {"codigo_fuente": "1001"})
    assert asyncio.run(llamar()).is_error


# ---------------------------------------------------------------- Filesystem MCP (servidor ya construido)

USUARIO_A = "11111111-1111-1111-1111-111111111111"


def test_filesystem_confinado(recursos):
    if not recursos.informes_disponibles:
        pytest.skip("Filesystem MCP no instalado: ejecuta python preparar_mcp.py")
    info = asyncio.run(recursos.descubrir_archivos())
    assert info["fuera_de_carpeta_rechazado"] is True
    assert {"write_file", "read_text_file"} <= set(info["herramientas_descubiertas"])


def test_filesystem_guarda_y_verifica(recursos, tmp_path, monkeypatch):
    if not recursos.informes_disponibles:
        pytest.skip("Filesystem MCP no instalado: ejecuta python preparar_mcp.py")
    monkeypatch.setattr(recursos, "carpeta_informes", tmp_path)
    catalogo = {"F1": {"chunk_id": "c1", "fuente": {"source": "reglas_de_borrador.md"}}}
    datos = asyncio.run(recursos.guardar_informe(USUARIO_A, "pregunta", "Texto [F1]", ["F1"], catalogo, autorizado=True))
    ruta = Path(datos["ruta"])
    assert datos["verificado"] and ruta.parent == tmp_path / USUARIO_A and ruta.is_file()


def test_filesystem_exige_permiso_y_fuentes(recursos):
    with pytest.raises((ValueError, RuntimeError)):
        asyncio.run(recursos.guardar_informe(USUARIO_A, "p", "r [F1]", ["F1"], {"F1": {}}, autorizado=False))
    with pytest.raises((ValueError, RuntimeError)):
        asyncio.run(recursos.guardar_informe(USUARIO_A, "p", "r", [], {}, autorizado=True))


# ---------------------------------------------------------------- contratos y límites del agente

def test_codigos_solo_de_esta_conversacion():
    assert codigos_permitidos("¿Y esa fuente?", []) == set()
    assert codigos_permitidos("Ahora DS-1002", [{"usuario": "Antes DS-1001"}]) == {"DS-1002"}
    assert codigos_permitidos("¿Y esa fuente?", [{"usuario": "Consulta DS-1001"}]) == {"DS-1001"}


@pytest.mark.parametrize("argumentos,realizadas,motivo", [
    ({"codigo_fuente": "DS-1001"}, 1, "REPETICION_SIN_AVANCE"),
    ({"consulta": "requisitos"}, sistema.MAX_OPERACIONES, "LIMITE_OPERACIONES"),
])
def test_limites_detienen(argumentos, realizadas, motivo):
    visitadas = set()
    controlar_operacion("consultar_fuente_datos", {"codigo_fuente": "DS-1001"}, visitadas, 0)
    nombre = "consultar_fuente_datos" if "codigo_fuente" in argumentos else "buscar_documentos"
    with pytest.raises(Detencion, match=motivo):
        controlar_operacion(nombre, argumentos, visitadas, realizadas)


def test_rrf():
    fusion = fusionar_rrf([{"chunk_id": x} for x in "ABC"], [{"chunk_id": x} for x in "CAD"])
    assert [r["chunk_id"] for r in fusion] == ["A", "C", "B", "D"]


@pytest.mark.parametrize("fuentes,permiso", [({}, True), ({"F1": {}}, False)])
def test_guardar_exige_evidencia_y_permiso(fuentes, permiso):
    propuesta = Decision(accion="guardar_informe", consulta="", codigo_fuente="", respuesta="Resultado [F1].", citas=["F1"])
    with pytest.raises(ValueError):
        validar_decision(propuesta, "Guarda un informe", [], fuentes, permiso)


def test_citas_deben_existir_en_el_turno():
    d = Decision(accion="responder", consulta="", codigo_fuente="", respuesta="Algo [F3].", citas=["F3"])
    with pytest.raises(ValueError):
        validar_decision(d, "pregunta", [], {"F1": {}}, False)


def test_codigo_inventado_rechazado():
    d = Decision(accion="consultar_fuente_datos", consulta="", codigo_fuente="DS-1003", respuesta="", citas=[])
    with pytest.raises(ValueError):
        validar_decision(d, "¿Cómo está DS-1001?", [], {}, False)


# ---------------------------------------------------------------- almacenamiento

def test_historial_para_modelo_ventana():
    mensajes = []
    for i in range(6):
        mensajes += [{"rol": "user", "contenido": f"p{i}"}, {"rol": "assistant", "contenido": f"r{i}"}]
    turnos = historial_para_modelo(mensajes, 4)
    assert [t["usuario"] for t in turnos] == ["p2", "p3", "p4", "p5"]
    assert historial_para_modelo([{"rol": "user", "contenido": "sin respuesta"}], 4) == []


def test_titulo_desde_pregunta():
    assert titulo_desde_pregunta("  hola   mundo ") == "hola mundo"
    assert len(titulo_desde_pregunta("x" * 200)) == 60


class ConsultaFalsa:
    """Imita la cadena de PostgREST y devuelve filas solo del propietario, como haría RLS."""
    def __init__(self, filas, usuario):
        self.filas, self.usuario, self.filtros = filas, usuario, {}

    def select(self, *_):
        return self

    def eq(self, columna, valor):
        self.filtros[columna] = valor
        return self

    def limit(self, *_):
        return self

    def order(self, *_ , **__):
        return self

    def execute(self):
        visibles = [f for f in self.filas if f["usuario_id"] == self.usuario
                    and all(f.get(k) == v for k, v in self.filtros.items())]
        return type("R", (), {"data": visibles})()


class SupabaseFalso:
    def __init__(self, filas, usuario):
        self.filas, self.usuario = filas, usuario

    def table(self, _):
        return ConsultaFalsa(self.filas, self.usuario)


def test_almacenamiento_niega_conversacion_ajena():
    ajena = {"id": "22222222-2222-2222-2222-222222222222", "usuario_id": "otro", "titulo": "x"}
    almacen = Almacenamiento(SupabaseFalso([ajena], USUARIO_A), USUARIO_A)
    with pytest.raises(AccesoDenegado):
        almacen.cargar_mensajes(ajena["id"])
    with pytest.raises(AccesoDenegado):
        almacen.guardar_turno(ajena["id"], "hola", {"respuesta": "r"})


def test_almacenamiento_rechaza_identificador_malformado():
    almacen = Almacenamiento(SupabaseFalso([], USUARIO_A), USUARIO_A)
    with pytest.raises(AccesoDenegado):
        almacen.cargar_mensajes("1 or 1=1")
