"""Servicio del grupo sobre el contrato oficial: formato del Gateway, simulador, RA, log y API."""

import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from gemelo import gateway
from gemelo.api import crear_app
from gemelo.bitacora import Bitacora
from gemelo.configuracion import ZONA_HORARIA, cargar_aula
from gemelo.grafos import cargar_grafos
from gemelo.servicio import Servicio
from gemelo.simulador import ESCENARIOS, Reloj, Simulador
from gemelo.transporte import BusEnMemoria, coincide

LUNES_9AM = datetime(2026, 11, 9, 9, 0, tzinfo=ZONA_HORARIA)


def servicio_simulado(inicio=LUNES_9AM, tmp_path=None):
    simulador = Simulador(Reloj(inicio, velocidad=1), semilla=1)
    bitacora = Bitacora(tmp_path / "eventos.jsonl" if tmp_path else None)
    return Servicio(BusEnMemoria(), simulador, bitacora)


def correr(servicio, segundos):
    for _ in range(int(segundos)):
        servicio.ciclo(1.0)


def nivel(servicio, ra):
    return servicio.condiciones[ra].nivel


# --- formato del Gateway --------------------------------------------------------------------------

def test_el_mensaje_sigue_el_orden_y_los_campos_del_gateway():
    texto = gateway.mensaje(nodo=1, mac="AA:BB:CC:DD:EE:FF", seq=5, ts_ms=1_700_000_000_000, uptime_ms=10,
                            perdidos=0, tipo="co2", nivel="ALERTA",
                            campos={"co2_ppm": 1050, "delta_30s": 20, "temp_c": 25, "calentando": 0},
                            anom_bits=0b0100)
    cuerpo = json.loads(texto)
    assert list(cuerpo) == ["nodo", "mac", "seq", "ts", "uptime_ms", "perdidos", "tipo", "co2_ppm", "delta_30s",
                            "temp_c", "calentando", "nivel", "anomalias", "anom_bits"]
    assert cuerpo["anomalias"] == "CO2_ALERTA_VENTILACION"


def test_lectura_de_un_mensaje_del_gateway():
    texto = '{"nodo":7,"mac":"x","seq":3,"ts":1700000000000,"uptime_ms":1,"perdidos":2,"tipo":"ambiente",' \
            '"temp_c":27.1,"hum_pct":71.0,"pres_hpa":1010.0,"anomalias":"TEMP_FUERA_CONFORT|HUMEDAD_ALTA","anom_bits":6}'
    lectura = gateway.leer("utec/gemelo/grupoX/nodo7/ambiente", texto)
    assert (lectura.grupo, lectura.nodo, lectura.perdidos) == ("grupoX", 7, 2)
    assert lectura.tiene("HUMEDAD_ALTA") and lectura.campos["temp_c"] == 27.1


def test_rechaza_topicos_fuera_del_contrato():
    with pytest.raises(gateway.MensajeInvalido):
        gateway.leer("l419/ambiental/temperatura", "{}")


def test_comodines_mqtt():
    assert coincide("utec/gemelo/sim/#", "utec/gemelo/sim/nodo1/co2")
    assert coincide("utec/gemelo/+/+/co2", "utec/gemelo/sim/nodo1/co2")
    assert not coincide("utec/gemelo/sim/#", "utec/gemelo/grupoX/nodo1/co2")


# --- simulador ------------------------------------------------------------------------------------

def test_el_simulador_publica_los_7_tipos_en_el_grupo_sim():
    simulador = Simulador(Reloj(LUNES_9AM), semilla=1)
    tipos = set()
    for _ in range(15):
        for topico, carga, _ in simulador.avanzar(1):
            if topico.endswith("/estado"):
                continue
            lectura = gateway.leer(topico, carga)
            assert lectura.grupo == "sim"
            tipos.add(lectura.tipo)
    assert tipos == set(gateway.TIPOS)


def test_el_nodo_co2_calienta_tres_minutos_como_el_del_docente():
    simulador = Simulador(Reloj(LUNES_9AM), semilla=1)
    niveles = []
    for _ in range(200):
        for topico, carga, _ in simulador.avanzar(1):
            if topico.endswith("/co2"):
                niveles.append(json.loads(carga)["nivel"])
    assert niveles[0] == "CALENTANDO" and niveles[-1] != "CALENTANDO"


def test_todos_los_escenarios_existen_y_se_aplican():
    simulador = Simulador(Reloj(LUNES_9AM), semilla=1)
    for nombre in ESCENARIOS:
        simulador.aplicar_escenario(nombre)
        simulador.avanzar(1)
    with pytest.raises(ValueError):
        simulador.aplicar_escenario("inexistente")


# --- requisitos, diagnóstico y log ----------------------------------------------------------------

def test_con_clase_normal_todos_los_requisitos_quedan_definidos(tmp_path):
    servicio = servicio_simulado(tmp_path=tmp_path)
    correr(servicio, 240)
    assert set(servicio.condiciones) == {f"RA-{i:02d}" for i in range(1, 11)}
    assert nivel(servicio, "RA-10") == "nominal"


def test_gas_pasa_a_critico_y_deja_diagnostico_en_el_log(tmp_path):
    servicio = servicio_simulado(tmp_path=tmp_path)
    correr(servicio, 70)  # el MQ-2 termina de calentar
    servicio.aplicar_escenario("gas")
    correr(servicio, 10)
    assert nivel(servicio, "RA-05") == "critico"
    evento = next(e for e in servicio.bitacora.listar(tipo="requisito") if e["ra"] == "RA-05")
    assert evento["severidad"] == "critico" and evento["recomendaciones"]
    assert (tmp_path / "eventos.jsonl").read_text().count("RA-05") >= 1


def test_gateway_caido_se_diagnostica_como_gateway_y_no_como_siete_sensores():
    servicio = servicio_simulado()
    correr(servicio, 30)
    servicio.aplicar_escenario("gateway-caido")
    correr(servicio, 60)
    assert nivel(servicio, "RA-10") == "critico"
    diagnostico = servicio.diagnosticos["RA-10"]
    assert [c["id"] for c in diagnostico.causas_confirmadas] == ["gateway_caido"]


def test_un_nodo_sin_bateria_se_confirma_por_descarte():
    servicio = servicio_simulado()
    correr(servicio, 30)
    servicio.aplicar_escenario("nodo-sin-bateria")
    correr(servicio, 45)
    diagnostico = servicio.diagnosticos["RA-10"]
    assert "nodo5_apagado" in [c["id"] for c in diagnostico.causas_confirmadas]
    assert "gateway_caido" in [c["id"] for c in diagnostico.causas_descartadas]


def test_consumo_fantasma_se_estima_con_el_inventario_del_aula():
    servicio = servicio_simulado(datetime(2026, 11, 9, 10, 30, tzinfo=ZONA_HORARIA))
    servicio.aplicar_escenario("vacio-con-luces")
    correr(servicio, 25 * 60)
    assert nivel(servicio, "RA-08") in ("alerta", "critico")
    fantasma = servicio.fantasma.como_diccionario()
    assert fantasma["kwh"] > 0 and fantasma["soles"] > 0 and fantasma["basadoEnSupuestos"]


def test_intrusion_nocturna_es_critica():
    servicio = servicio_simulado()
    servicio.aplicar_escenario("intrusion-nocturna")
    correr(servicio, 30)
    assert nivel(servicio, "RA-09") == "critico"


def test_los_supuestos_del_aula_se_cuentan():
    resumen = cargar_aula().resumen_de_supuestos()
    assert resumen["total"] > 0 and resumen["supuestos"] <= resumen["total"]


def test_cada_ra_tiene_su_grafo():
    assert set(cargar_grafos()) == {f"RA-{i:02d}" for i in range(1, 11)}


# --- API --------------------------------------------------------------------------------------------

def test_api_estado_grafo_eventos_y_escenarios():
    servicio = servicio_simulado()
    correr(servicio, 30)
    with TestClient(crear_app(servicio)) as cliente:
        estado = cliente.get("/api/estado").json()
        assert estado["fuente"]["simulado"] and len(estado["mediciones"]) == 7
        assert len(estado["requisitos"]) == 10
        grafo = cliente.get("/api/grafos/RA-03").json()
        assert grafo["central"] == "co2_alto" and grafo["diagnostico"]["ra"] == "RA-03"
        assert cliente.post("/api/demo/escenario/gas").status_code == 200
        assert cliente.post("/api/demo/escenario/no-existe").status_code == 400
        assert cliente.get("/api/eventos.csv").text.startswith("ts,tipo,severidad")
        assert cliente.get("/api/grafos/RA-99").status_code == 404


def test_a_velocidad_alta_la_latencia_mqtt_no_tumba_los_nodos():
    """Regresión: a ×60 un ciclo son 30 s del aula y los mensajes vuelven un ciclo después."""

    class BusConRetraso(BusEnMemoria):
        def __init__(self):
            super().__init__()
            self._en_vuelo = []

        def recibir_pendientes(self):
            # Lo publicado en este ciclo recién se entrega en el siguiente, como pasa con Mosquitto.
            entregar, self._en_vuelo = self._en_vuelo, super().recibir_pendientes()
            return entregar

    servicio = Servicio(BusConRetraso(), Simulador(Reloj(LUNES_9AM, velocidad=60), semilla=1), Bitacora(None))
    for _ in range(40):
        servicio.ciclo(0.5)
    assert nivel(servicio, "RA-10") == "nominal"
