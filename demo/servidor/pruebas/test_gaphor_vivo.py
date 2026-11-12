"""Pruebas del enlace en vivo con Gaphor (demo/gaphor-vivo/enlace.py).

`enlace.py` corre dentro del interprete de Gaphor, sin PyYAML, y por eso lleva escrita la tabla de
nodos y RA. Aqui se comprueba que esa tabla siga igual a la configuracion del proyecto y a los
bloques que declara `modelo/tools/build_model.py`, y que los colores salgan de la condicion de cada RA.
"""

import ast
import sys
from typing import Any

import pytest

from gemelo.configuracion import RAIZ_DEL_REPO, cargar_nodos, cargar_requisitos

sys.path.insert(0, str(RAIZ_DEL_REPO / "demo" / "gaphor-vivo"))
import enlace  # noqa: E402

CONSTRUCTOR_DEL_MODELO = RAIZ_DEL_REPO / "modelo" / "tools" / "build_model.py"


def _asignacion(nombre: str) -> Any:
    """El valor asignado a `nombre` en build_model.py, sin importarlo (necesita Gaphor)."""
    arbol = ast.parse(CONSTRUCTOR_DEL_MODELO.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(getattr(t, "id", None) == nombre for t in nodo.targets):
            return nodo.value
    raise AssertionError(f"build_model.py no define {nombre}")


@pytest.fixture(scope="module")
def nodos_del_modelo():
    """{id: (tipo, bloque del nodo, bloque del sensor)} como los declara el constructor del modelo."""
    return {
        llamada.args[0].value: tuple(arg.value for arg in llamada.args[1:4])
        for llamada in _asignacion("NODOS_OFICIALES").elts
    }


def _estado(niveles: dict[str, str] | None = None, caidos: tuple[int, ...] = (),
            gateway: bool | None = True) -> dict[str, Any]:
    niveles = niveles or {}
    return {
        "requisitos": [{"ra": f"RA-{n:02d}", "nivel": niveles.get(f"RA-{n:02d}", "nominal")} for n in range(1, 11)],
        "salud": [{"nodo": n, "caido": n in caidos} for n in range(1, 8)],
        "gatewayEnLinea": gateway,
    }


def test_los_nodos_de_la_tabla_son_los_de_la_configuracion():
    config = cargar_nodos()
    assert {s.nodo: s.tipo for s in enlace.SENSORES} == {i: n.tipo for i, n in config.items()}


def test_los_ra_de_cada_nodo_son_los_de_la_configuracion():
    """Cada nodo lleva los RA que lo listan en `nodos`, salvo RA-10 (su salud se ve en `salud`)."""
    esperados = {s.nodo: set() for s in enlace.SENSORES}
    for ra, requisito in cargar_requisitos().items():
        if ra == "RA-10":
            continue
        for nodo in requisito["nodos"]:
            esperados[nodo].add(ra)
    assert {s.nodo: set(s.ras) for s in enlace.SENSORES} == esperados


def test_los_bloques_son_los_del_modelo(nodos_del_modelo):
    en_la_tabla = {s.nodo: (s.tipo, s.bloque_del_nodo, s.bloque_del_sensor) for s in enlace.SENSORES}
    assert en_la_tabla == nodos_del_modelo


def test_el_indice_tonal_se_declara_de_0_a_1():
    magnitudes = ast.literal_eval(_asignacion("MAGNITUDES_OFICIALES"))
    assert dict(magnitudes["INMP441"])["tonal"] == "Índice [0..1]"


def test_los_valores_salen_de_los_campos_de_cada_nodo():
    estado = {"mediciones": [
        {"tipo": "audio", "campos": {"leq_db": 38.42, "tonal": 0.15, "calibrando": 0}},
        {"tipo": "magnetico", "campos": {"puerta_abierta": 1, "aperturas": 2, "campo_raw": 730}},
        {"tipo": "co2", "campos": {"co2_ppm": 425, "nivel": "NORMAL", "temp_c": None}},
    ]}
    valores = enlace.valores_de_propiedades(estado)
    assert valores[("INMP441", "leq_db")] == "38.4"
    assert valores[("INMP441", "tonal")] == "0.15"
    assert valores[("INMP441", "calibrando")] == "no"
    assert valores[("KY-024 (Hall SS49E)", "puerta_abierta")] == "ABIERTA"
    assert valores[("KY-024 (Hall SS49E)", "aperturas")] == "2"
    assert valores[("MH-Z1911A", "co2_ppm")] == "425"
    assert valores[("MH-Z1911A", "nivel")] == "NORMAL"
    assert valores[("MH-Z1911A", "temp_c")] == enlace.SIN_VALOR


def test_un_tipo_de_nodo_desconocido_no_escribe_nada():
    assert enlace.valores_de_propiedades({"mediciones": [{"tipo": "pzem", "campos": {"w": 1}}]}) == {}
    assert enlace.valores_de_propiedades({}) == {}


def test_todo_nominal_pinta_todo_en_estado_normal():
    colores = enlace.color_por_bloque(_estado())
    assert set(colores) == set(enlace.BLOQUES_QUE_SE_PINTAN)
    assert set(colores.values()) == {enlace.COLOR_NORMAL}


@pytest.mark.parametrize("ra, nivel, bloque, color", [
    ("RA-05", "critico", "MQ-2", enlace.COLOR_CRITICO),
    ("RA-05", "critico", "Nodo 3 Gas y humo", enlace.COLOR_CRITICO),
    ("RA-03", "alerta", "MH-Z1911A", enlace.COLOR_ATENCION),
    ("RA-01", "alerta", "BME280 (GY-BME280)", enlace.COLOR_ATENCION),
    ("RA-07", "desconocido", "INMP441", enlace.COLOR_CAIDO),
])
def test_el_bloque_toma_el_color_de_su_ra(ra, nivel, bloque, color):
    assert enlace.color_por_bloque(_estado({ra: nivel}))[bloque] == color


def test_un_ra_compartido_pinta_a_todos_sus_nodos_y_solo_a_ellos():
    colores = enlace.color_por_bloque(_estado({"RA-09": "alerta"}))  # nodos 5 y 6
    pintados = {b for b, c in colores.items() if c == enlace.COLOR_ATENCION}
    assert pintados == {"Nodo 5 Conteo térmico", "MLX90640 32x24", "Nodo 6 Puerta", "KY-024 (Hall SS49E)"}


def test_el_peor_ra_manda():
    niveles = {"RA-04": "alerta", "RA-06": "critico"}  # los dos tocan el nodo 5
    assert enlace.color_por_bloque(_estado(niveles))["MLX90640 32x24"] == enlace.COLOR_CRITICO


def test_ra10_no_pinta_los_nodos_que_si_reportan():
    colores = enlace.color_por_bloque(_estado({"RA-10": "alerta"}))
    assert set(colores.values()) == {enlace.COLOR_NORMAL}


def test_un_nodo_caido_se_ve_gris_aunque_su_ra_este_en_alerta():
    colores = enlace.color_por_bloque(_estado({"RA-03": "alerta"}, caidos=(1,)))
    assert colores["MH-Z1911A"] == colores["Nodo 1 CO2"] == enlace.COLOR_CAIDO


def test_el_gateway_caido_se_ve_gris():
    assert enlace.color_por_bloque(_estado(gateway=False))["Gateway ESP32 v4"] == enlace.COLOR_CAIDO
    assert enlace.color_por_bloque(_estado(gateway=None))["Gateway ESP32 v4"] == enlace.COLOR_NORMAL


def test_la_hoja_de_estilo_trae_una_regla_por_bloque():
    hoja = enlace.hoja_de_estilo(_estado({"RA-05": "critico"}))
    for bloque in enlace.BLOQUES_QUE_SE_PINTAN:
        assert f'block[name="{bloque}"]' in hoja
    assert f'block[name="MQ-2"] {{ background-color: {enlace.COLOR_CRITICO};' in hoja


def test_el_panel_rotula_los_datos_simulados_y_lista_los_diez_ra():
    estado = _estado({"RA-05": "critico"})
    estado["fuente"] = {"origen": "simulado", "escenario": "gas"}
    estado["requisitos"][4].update(nombre="Seguridad ante gas o humo", valor=3.1, unidad="Rs/R0")
    texto = enlace.panel(estado)
    assert texto.startswith("ESTADO EN VIVO · DATOS SIMULADOS")
    assert texto.count("\nRA-") == 10
    assert "RA-05 Seguridad ante gas o humo: CRÍTICO · 3.1 Rs/R0" in texto


def test_el_panel_sin_estado_no_falla():
    assert enlace.panel({}).startswith("ESTADO EN VIVO")
