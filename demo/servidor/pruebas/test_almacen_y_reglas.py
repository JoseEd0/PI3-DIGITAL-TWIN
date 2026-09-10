"""Pruebas del almacen (ingesta, duplicados, salud) y del motor de reglas."""

from datetime import datetime, timedelta

import pytest

from campus_twin_demo import configuracion as cfg
from campus_twin_demo.almacen import Almacen
from campus_twin_demo.contrato import Muestra
from campus_twin_demo.reglas import AuditorDeConsumoFantasma, MotorDeReglas
from campus_twin_demo.simulador import RelojVirtual, Simulador

INICIO = datetime(2026, 9, 7, 8, 0)


def muestra(nodo=cfg.NODO_AMBIENTAL, magnitud="co2", valor=500.0, seq=1, momento=INICIO):
    return Muestra(
        nodo=nodo,
        magnitud=magnitud,
        valor=valor,
        momento=momento,
        secuencia=seq,
        unidad=cfg.UNIDADES.get(magnitud, ""),
    )


def test_guarda_la_ultima_lectura_y_el_historico():
    almacen = Almacen()
    for i in range(1, 4):
        almacen.registrar_muestra(muestra(valor=500 + i, seq=i, momento=INICIO + timedelta(minutes=i)))
    assert almacen.ultimo(cfg.NODO_AMBIENTAL, "co2") == 503
    assert len(almacen.historico(cfg.NODO_AMBIENTAL, "co2")) == 3


def test_descarta_duplicados_por_secuencia():
    almacen = Almacen()
    assert almacen.registrar_muestra(muestra(seq=5)) is True
    assert almacen.registrar_muestra(muestra(seq=5)) is False
    assert almacen.registrar_muestra(muestra(seq=4)) is False
    assert almacen.salud[cfg.NODO_AMBIENTAL].duplicadas == 2
    assert len(almacen.historico(cfg.NODO_AMBIENTAL, "co2")) == 1


def test_el_historico_tiene_tope():
    almacen = Almacen()
    for i in range(1, cfg.MUESTRAS_POR_SERIE + 50):
        almacen.registrar_muestra(muestra(seq=i, momento=INICIO + timedelta(seconds=i)))
    assert len(almacen.historico(cfg.NODO_AMBIENTAL, "co2", limite=cfg.MUESTRAS_POR_SERIE)) == cfg.MUESTRAS_POR_SERIE


def test_un_nodo_sin_datos_se_marca_caido():
    almacen = Almacen()
    almacen.registrar_muestra(muestra())
    poco_despues = INICIO + timedelta(minutes=cfg.MINUTOS_SIN_DATOS_PARA_CAIDO - 1)
    mucho_despues = INICIO + timedelta(minutes=cfg.MINUTOS_SIN_DATOS_PARA_CAIDO + 1)
    assert almacen.salud[cfg.NODO_AMBIENTAL].esta_caido(poco_despues) is False
    assert almacen.salud[cfg.NODO_AMBIENTAL].esta_caido(mucho_despues) is True


def test_un_nodo_que_nunca_reporto_no_tiene_fecha():
    almacen = Almacen()
    fila = almacen.salud[cfg.NODO_PUERTA].como_diccionario(INICIO)
    assert fila["ultimaMuestra"] is None
    assert fila["minutosSinReportar"] is None


def test_alerta_de_co2_alto_y_silencio():
    reglas = MotorDeReglas()
    reloj = RelojVirtual(INICIO, velocidad=1)
    simulador = Simulador(reloj, semilla=1)
    simulador.estado.co2 = cfg.UMBRAL_DE_CO2_PPM + 200
    simulador.estado.personas = 12

    nuevas = reglas.evaluar(simulador.estado, reloj, [])
    assert [a.codigo for a in nuevas] == ["co2-alto"]

    # sigue activa, pero no vuelve a notificarse antes del silencio
    assert reglas.evaluar(simulador.estado, reloj, []) == []
    simulador.estado.co2 = 500
    reglas.evaluar(simulador.estado, reloj, [])
    assert reglas.activas == {}

    reloj.momento += timedelta(minutes=cfg.SILENCIO_DE_ALERTA_MIN + 1)
    simulador.estado.co2 = cfg.UMBRAL_DE_CO2_PPM + 200
    assert [a.codigo for a in reglas.evaluar(simulador.estado, reloj, [])] == ["co2-alto"]


def test_alerta_de_puerta_solo_fuera_de_horario():
    reglas = MotorDeReglas()
    en_horario = RelojVirtual(datetime(2026, 9, 7, 10, 0), velocidad=1)
    simulador = Simulador(en_horario, semilla=1)
    simulador.estado.puerta_abierta = True
    assert not [a for a in reglas.evaluar(simulador.estado, en_horario, []) if a.codigo == "puerta-fuera-de-horario"]

    de_madrugada = RelojVirtual(datetime(2026, 9, 7, 3, 0), velocidad=1)
    alertas = reglas.evaluar(simulador.estado, de_madrugada, [])
    assert [a.requisito for a in alertas if a.codigo == "puerta-fuera-de-horario"] == ["RF-04"]


def test_alerta_de_consumo_con_aula_vacia():
    reglas = MotorDeReglas()
    reloj = RelojVirtual(datetime(2026, 9, 7, 23, 0), velocidad=1)
    simulador = Simulador(reloj, semilla=1)
    simulador.estado.personas = 0
    simulador.estado.potencia = cfg.UMBRAL_DE_CONSUMO_CON_AULA_VACIA_W + 200
    simulador.estado.minutos_vacio = cfg.MINUTOS_VACIO_PARA_FANTASMA + 5
    alertas = reglas.evaluar(simulador.estado, reloj, [])
    assert [a.codigo for a in alertas if a.requisito == "RF-10"] == ["consumo-con-aula-vacia"]


def test_alerta_de_nodo_caido_usa_la_salud():
    reglas = MotorDeReglas()
    reloj = RelojVirtual(INICIO, velocidad=1)
    simulador = Simulador(reloj, semilla=1)
    salud = [
        {
            "nodo": cfg.NODO_AMBIENTAL,
            "etiqueta": "Nodo Ambiental",
            "caido": True,
            "ultimaMuestra": INICIO.isoformat(),
            "minutosSinReportar": 7.0,
        }
    ]
    alertas = reglas.evaluar(simulador.estado, reloj, salud)
    assert any(a.codigo.startswith("nodo-caido") and a.requisito == "RF-13" for a in alertas)


def test_el_auditor_solo_cuenta_energia_con_el_aula_vacia():
    auditor = AuditorDeConsumoFantasma()
    reloj = RelojVirtual(datetime(2026, 9, 7, 23, 0), velocidad=1)
    simulador = Simulador(reloj, semilla=1)

    simulador.estado.personas = 10
    simulador.estado.potencia = 800
    auditor.acumular(simulador.estado, reloj, 60)
    assert auditor.kwh_fantasma == 0.0
    assert auditor.kwh_totales == pytest.approx(0.8)

    simulador.estado.personas = 0
    simulador.estado.minutos_vacio = cfg.MINUTOS_VACIO_PARA_FANTASMA + 1
    simulador.estado.luces_encendidas = True
    simulador.estado.pcs_encendidos = 4
    auditor.acumular(simulador.estado, reloj, 60)
    assert auditor.kwh_fantasma == pytest.approx(0.8)
    assert auditor.kwh_fantasma_fuera_de_horario == pytest.approx(0.8)
    assert auditor.por_carga["iluminacion"] > 0
    assert auditor.porcentaje_evitable == pytest.approx(50.0)


def test_el_auditor_espera_los_minutos_declarados():
    auditor = AuditorDeConsumoFantasma()
    reloj = RelojVirtual(datetime(2026, 9, 7, 23, 0), velocidad=1)
    simulador = Simulador(reloj, semilla=1)
    simulador.estado.personas = 0
    simulador.estado.potencia = 500
    simulador.estado.minutos_vacio = cfg.MINUTOS_VACIO_PARA_FANTASMA - 1
    auditor.acumular(simulador.estado, reloj, 1)
    assert auditor.kwh_fantasma == 0.0


def test_el_reporte_traduce_a_soles_y_emisiones():
    auditor = AuditorDeConsumoFantasma()
    auditor.kwh_fantasma = 10.0
    auditor.kwh_totales = 40.0
    reporte = auditor.como_diccionario()
    assert reporte["soles"] == pytest.approx(10.0 * cfg.TARIFA_SOLES_POR_KWH, rel=1e-3)
    assert reporte["kgCO2"] == pytest.approx(10.0 * cfg.FACTOR_DE_EMISION_KG_POR_KWH, rel=1e-3)
    assert reporte["porcentajeEvitable"] == 25.0


def test_el_nodo_de_puerta_tolera_su_periodo_de_latido():
    """RNF-04: el nodo duerme y late cada 30 min; no puede darse por caido a los 5."""
    almacen = Almacen()
    almacen.registrar_muestra(muestra(nodo=cfg.NODO_PUERTA, magnitud="bateria", valor=90.0))
    salud = almacen.salud[cfg.NODO_PUERTA]
    assert salud.esta_caido(INICIO + timedelta(minutes=20)) is False
    assert salud.esta_caido(INICIO + timedelta(minutes=100)) is True


def test_un_nodo_rapido_se_da_por_caido_a_los_cinco_minutos():
    almacen = Almacen()
    almacen.registrar_muestra(muestra(nodo=cfg.NODO_ENERGIA, magnitud="potencia", valor=300.0))
    salud = almacen.salud[cfg.NODO_ENERGIA]
    assert salud.umbral_de_caida_min == cfg.MINUTOS_SIN_DATOS_PARA_CAIDO
    assert salud.esta_caido(INICIO + timedelta(minutes=6)) is True
