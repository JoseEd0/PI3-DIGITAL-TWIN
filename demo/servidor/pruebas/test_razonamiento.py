"""Motor causal: un caso por tipo de lógica, con los ejemplos de las diapositivas de SymCure."""

import pytest

from gemelo.razonamiento import D, F, Grafo, GrafoInvalido, Motor, S, V, valor_por_entrada


def grafo(eventos, aristas, central):
    return Grafo.desde_diccionario("prueba", {
        "ra": "RA-XX", "titulo": "prueba", "evento_central": central,
        "eventos": eventos, "aristas": aristas,
    })


def causas_raiz(*ids, salida="AND"):
    return [{"id": i, "texto": i, "clase": "causa", "salida": salida} for i in ids]


# --- OR-AND: S1 tiene como causas a F1, F2 y F3 (diapositivas 3 a 12) -------------------------

@pytest.fixture
def or_and():
    return grafo(
        causas_raiz("F1", "F2", "F3") + [{"id": "S1", "texto": "S1", "clase": "sintoma", "entrada": "OR"}],
        [["F1", "S1"], ["F2", "S1"], ["F3", "S1"]], "S1",
    )


def test_or_aguas_abajo_una_causa_verdadera_basta(or_and):
    diagnostico = Motor(or_and).diagnosticar({"F2": True})
    assert diagnostico.valores["S1"] == V


def test_or_aguas_arriba_el_sintoma_vuelve_sospechosas_a_sus_causas(or_and):
    diagnostico = Motor(or_and).diagnosticar({"S1": True})
    assert {c["id"] for c in diagnostico.causas_sospechosas} == {"F1", "F2", "F3"}


def test_or_una_causa_descartada_deja_sospechosas_a_las_otras(or_and):
    diagnostico = Motor(or_and).diagnosticar({"S1": True, "F1": False})
    assert diagnostico.valores["F1"] == F
    assert diagnostico.valores["F2"] == S and diagnostico.valores["F3"] == S


def test_unica_causa_posible_de_un_evento_verdadero_es_verdadera(or_and):
    diagnostico = Motor(or_and).diagnosticar({"S1": True, "F1": False, "F2": False})
    assert diagnostico.valores["F3"] == V


def test_efecto_falso_descarta_las_causas_con_salida_and(or_and):
    diagnostico = Motor(or_and).diagnosticar({"S1": False})
    assert {c["id"] for c in diagnostico.causas_descartadas} == {"F1", "F2", "F3"}


def test_efecto_falso_no_descarta_causas_con_salida_or():
    g = grafo(
        causas_raiz("F1", salida="OR") + [{"id": "S1", "texto": "S1", "entrada": "OR"}],
        [["F1", "S1"]], "S1",
    )
    assert Motor(g).diagnosticar({"S1": False}).valores["F1"] == D


def test_lo_observado_prevalece_sobre_lo_inferido(or_and):
    diagnostico = Motor(or_and).diagnosticar({"F2": True, "S1": False})
    assert diagnostico.valores["F2"] == V and diagnostico.valores["S1"] == F


# --- AND-AND: falla de alimentación = primaria AND respaldo (diapositiva 13) ------------------

@pytest.fixture
def and_and():
    return grafo(
        causas_raiz("primaria", "respaldo")
        + [{"id": "fuente", "texto": "Falla de la fuente", "entrada": "AND"}],
        [["primaria", "fuente"], ["respaldo", "fuente"]], "fuente",
    )


def test_and_requiere_todas_las_causas(and_and):
    assert Motor(and_and).diagnosticar({"primaria": True}).valores["fuente"] == D
    assert Motor(and_and).diagnosticar({"primaria": True, "respaldo": True}).valores["fuente"] == V
    assert Motor(and_and).diagnosticar({"primaria": True, "respaldo": False}).valores["fuente"] == F


def test_and_aguas_arriba_un_efecto_verdadero_confirma_todas_sus_causas(and_and):
    diagnostico = Motor(and_and).diagnosticar({"fuente": True})
    assert {c["id"] for c in diagnostico.causas_confirmadas} == {"primaria", "respaldo"}


def test_and_con_una_causa_sospechosa_es_sospechoso():
    evento = grafo(causas_raiz("a", "b") + [{"id": "e", "texto": "e", "entrada": "AND"}],
                   [["a", "e"], ["b", "e"]], "e").eventos["e"]
    assert valor_por_entrada(evento, {"a": V, "b": S}) == S


# --- N/M-AND: interrupción del ISP con ≥ 50 % de servidores caídos (diapositiva 16) -----------

@pytest.fixture
def n_m():
    servidores = causas_raiz("s1", "s2", "s3", "s4")
    isp = {"id": "isp", "texto": "Interrupción del ISP", "entrada": "N/M", "fraccion": 0.5}
    return grafo(servidores + [isp], [[s, "isp"] for s in ("s1", "s2", "s3", "s4")], "isp")


def test_nm_verdadero_al_alcanzar_la_fraccion(n_m):
    assert Motor(n_m).diagnosticar({"s1": True, "s2": False, "s3": False, "s4": False}).valores["isp"] == F
    resultado = Motor(n_m).diagnosticar({"s1": True, "s2": True, "s3": False, "s4": False})
    assert resultado.valores["isp"] == V


def test_nm_cuenta_sospechosos_y_desconocidos_como_dice_la_tabla(n_m):
    evento = n_m.eventos["isp"]
    assert valor_por_entrada(evento, {"s1": V, "s2": S, "s3": F, "s4": F}) == S
    assert valor_por_entrada(evento, {"s1": V, "s2": D, "s3": F, "s4": F}) == D


# --- IF: el evento depende del contexto (diapositiva 19) ---------------------------------------

@pytest.fixture
def con_if():
    return grafo(
        causas_raiz("fuera_de_horario", "puerta_abierta")
        + [{"id": "intrusion", "texto": "Posible intrusión", "entrada": "IF", "condicion": "fuera_de_horario"}],
        [["fuera_de_horario", "intrusion"], ["puerta_abierta", "intrusion"]], "intrusion",
    )


def test_if_solo_propaga_con_la_condicion_verdadera(con_if):
    assert Motor(con_if).diagnosticar({"fuera_de_horario": True, "puerta_abierta": True}).valores["intrusion"] == V
    assert Motor(con_if).diagnosticar({"fuera_de_horario": False, "puerta_abierta": True}).valores["intrusion"] == F


# --- cadena causa → evento central → efecto ----------------------------------------------------

def test_un_evento_central_verdadero_predice_sus_efectos():
    g = grafo(
        causas_raiz("ventilacion") + [
            {"id": "co2_alto", "texto": "CO2 alto", "entrada": "OR"},
            {"id": "fatiga", "texto": "Fatiga", "clase": "efecto", "entrada": "OR"},
        ],
        [["ventilacion", "co2_alto"], ["co2_alto", "fatiga"]], "co2_alto",
    )
    diagnostico = Motor(g).diagnosticar({"co2_alto": True})
    assert diagnostico.activo
    assert [e["id"] for e in diagnostico.efectos_esperados] == ["fatiga"]
    assert diagnostico.valores["ventilacion"] == V  # única causa posible


# --- validación ----------------------------------------------------------------------------------

def test_rechaza_ciclos():
    with pytest.raises(GrafoInvalido, match="ciclos"):
        grafo([{"id": "a", "texto": "a"}, {"id": "b", "texto": "b"}], [["a", "b"], ["b", "a"]], "a")


def test_rechaza_aristas_a_eventos_inexistentes():
    with pytest.raises(GrafoInvalido, match="inexistente"):
        grafo([{"id": "a", "texto": "a"}], [["a", "x"]], "a")
