"""Pruebas del simulador: que cada magnitud se mueva por la razon correcta."""

from datetime import datetime, timedelta

import pytest

from campus_twin_demo import configuracion as cfg
from campus_twin_demo.simulador import RelojVirtual, Simulador


def simulador_en(hora: float, velocidad: float = 1.0) -> Simulador:
    inicio = datetime(2026, 9, 7, int(hora), int((hora % 1) * 60))  # lunes
    return Simulador(RelojVirtual(inicio, velocidad), semilla=419)


def correr(simulador: Simulador, minutos: float, paso_min: float = 1.0):
    muestras, eventos = [], []
    for _ in range(int(minutos / paso_min)):
        simulador.reloj.momento += timedelta(minutes=paso_min)
        nuevas, sucesos = simulador.avanzar(paso_min * 60)
        muestras += nuevas
        eventos += sucesos
    return muestras, eventos


def test_el_reloj_corre_a_la_velocidad_configurada():
    reloj = RelojVirtual(datetime(2026, 9, 7, 7, 0), velocidad=60)
    simulados = reloj.avanzar(2.0)
    assert simulados == pytest.approx(120.0)
    assert reloj.momento == datetime(2026, 9, 7, 7, 2)


def test_el_reloj_pausado_no_avanza():
    reloj = RelojVirtual(datetime(2026, 9, 7, 7, 0), velocidad=60)
    reloj.pausado = True
    assert reloj.avanzar(5.0) == 0.0


def test_entra_gente_en_bloque_de_clase():
    simulador = simulador_en(8.0)
    correr(simulador, 15)
    assert simulador.estado.personas > 0
    assert simulador.estado.presencia is True


def test_el_laboratorio_queda_vacio_de_madrugada():
    simulador = simulador_en(1.0)
    correr(simulador, 30)
    assert simulador.estado.personas == 0
    assert simulador.estado.presencia is False


def test_el_co2_sube_con_gente_y_baja_sin_gente():
    simulador = simulador_en(8.0)
    correr(simulador, 45)
    con_gente = simulador.estado.co2
    assert con_gente > cfg.CO2_EXTERIOR_PPM + 100

    vacio = simulador_en(2.0)
    vacio.estado.co2 = 1400.0
    correr(vacio, 60)
    assert vacio.estado.co2 < 700


def test_la_potencia_sube_con_las_luces_encendidas():
    simulador = simulador_en(23.0)
    correr(simulador, 5)
    en_reposo = simulador.estado.potencia
    simulador.aplicar_escenario("vacio-con-luces")
    correr(simulador, 5)
    assert simulador.estado.potencia > en_reposo + cfg.LUMINARIAS * cfg.POTENCIA_POR_LUMINARIA_W * 0.8


def test_la_energia_acumulada_nunca_baja():
    simulador = simulador_en(8.0)
    anterior = 0.0
    for _ in range(30):
        correr(simulador, 2)
        assert simulador.estado.energia_total >= anterior
        anterior = simulador.estado.energia_total


def test_el_conteo_se_reinicia_cuando_el_aula_queda_vacia():
    simulador = simulador_en(12.5)
    simulador.estado.conteo = 7
    correr(simulador, cfg.MINUTOS_VACIO_PARA_REINICIAR_CONTEO + 3)
    assert simulador.estado.conteo == 0


def test_el_conteo_nunca_es_negativo():
    simulador = simulador_en(8.0)
    for _ in range(40):
        correr(simulador, 1)
        assert simulador.estado.conteo >= 0


def test_las_muestras_respetan_el_contrato_de_topicos():
    simulador = simulador_en(8.0)
    muestras, _ = correr(simulador, 5)
    assert muestras
    for muestra in muestras:
        assert muestra.topico.startswith(f"{cfg.PREFIJO_DE_TOPICO}/")
        assert muestra.topico.count("/") == 2
        assert muestra.origen == cfg.ORIGEN_DEMO
        assert muestra.unidad == cfg.UNIDADES.get(muestra.magnitud, "")


def test_la_secuencia_crece_por_nodo_y_magnitud():
    simulador = simulador_en(8.0)
    muestras, _ = correr(simulador, 10)
    vistas = {}
    for muestra in muestras:
        clave = (muestra.nodo, muestra.magnitud)
        assert muestra.secuencia > vistas.get(clave, 0)
        vistas[clave] = muestra.secuencia


def test_cada_nodo_respeta_su_periodo_de_envio():
    simulador = simulador_en(8.0)
    muestras, _ = correr(simulador, 60, paso_min=0.5)
    del_ambiental = [m for m in muestras if m.nodo == cfg.NODO_AMBIENTAL and m.magnitud == "co2"]
    periodo = cfg.NODOS[cfg.NODO_AMBIENTAL][2]
    esperadas = 60 * 60 / periodo
    assert esperadas * 0.7 <= len(del_ambiental) <= esperadas * 1.3


def test_un_nodo_caido_deja_de_emitir():
    simulador = simulador_en(8.0)
    simulador.aplicar_escenario("caida-de-nodo")
    muestras, _ = correr(simulador, 20)
    assert not [m for m in muestras if m.nodo == cfg.NODO_AMBIENTAL]
    simulador.aplicar_escenario("restablecer")
    muestras, _ = correr(simulador, 20)
    assert [m for m in muestras if m.nodo == cfg.NODO_AMBIENTAL]


def test_la_apertura_fuera_de_horario_genera_evento_marcado():
    simulador = simulador_en(3.5)
    eventos = simulador.aplicar_escenario("apertura-fuera-de-horario")
    assert eventos and eventos[0].tipo == "apertura"
    assert eventos[0].datos["fueraDeHorario"] is True


def test_la_bateria_dura_los_dias_declarados():
    simulador = simulador_en(7.0)
    correr(simulador, 60 * 24, paso_min=10)
    consumido = cfg.BATERIA_INICIAL - simulador.estado.bateria
    esperado_por_dia = cfg.BATERIA_INICIAL / cfg.DIAS_DE_AUTONOMIA
    assert consumido == pytest.approx(esperado_por_dia, rel=0.35)


def test_escenario_desconocido_falla():
    simulador = simulador_en(8.0)
    with pytest.raises(ValueError):
        simulador.aplicar_escenario("no-existe")


def test_el_co2_se_estabiliza_en_valores_de_aula_real():
    """Un grupo en clase debe llegar a un CO2 alto pero creible, no a 4000 ppm."""
    simulador = simulador_en(8.0)
    correr(simulador, 120)
    assert 900 < simulador.estado.co2 < 2600, simulador.estado.co2
    assert simulador.estado.co2 <= cfg.CO2_MAXIMO_PPM
