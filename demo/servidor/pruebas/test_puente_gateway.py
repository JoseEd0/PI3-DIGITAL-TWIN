"""Puente HTTP -> MQTT para el Gateway con red propia (gateway_ap.ino), probado contra el Gateway falso."""

import json
import time

import pytest

from gemelo import gateway
from gemelo.configuracion import cargar_gateway_ap
from gemelo.gateway_falso import GatewayFalso, iniciar
from gemelo.puente_gateway import (ClienteGatewayAP, GatewayNoResponde, Puente, a_mensaje_oficial,
                                   hora_estimada)
from gemelo.servicio import Servicio
from gemelo.simulador import Reloj, Simulador
from gemelo.transporte import BusEnMemoria

HORA_LAPTOP_MS = 1_795_000_000_000
REGISTRO_CO2 = {"id": 15, "nodo": 1, "mac": "24:6F:28:AB:12:01", "seq": 2, "ts": 1794950267527, "gw_ms": 10024,
                "uptime_ms": 13024, "perdidos": 0, "tipo": "co2", "co2_ppm": 845, "delta_30s": 12, "temp_c": 24,
                "calentando": 0, "nivel": "NORMAL", "anomalias": "NINGUNA", "anom_bits": 0}  # ejemplo de la guía


@pytest.fixture
def falso():
    gateway_falso = GatewayFalso(Simulador(Reloj(velocidad=1), semilla=1))
    servidor = iniciar(gateway_falso, puerto=0)
    gateway_falso.url = f"http://127.0.0.1:{servidor.server_address[1]}"
    yield gateway_falso
    servidor.shutdown()


def armar_puente(falso, bus, desde=None, grupo="l419"):
    return Puente(ClienteGatewayAP(falso.url, espera_s=2), bus, grupo, max_por_pedido=50,
                  fallos_para_desconectado=2, desde=desde, reloj_ms=lambda: HORA_LAPTOP_MS)


def esperar_mensajes(falso, cuantos, limite_s=8):
    fin = time.monotonic() + limite_s
    while len(falso.registros) < cuantos and time.monotonic() < fin:
        time.sleep(0.1)
    assert len(falso.registros) >= cuantos


# --- formato ------------------------------------------------------------------------------------

def test_el_mensaje_queda_igual_al_del_gateway_mqtt():
    topico, carga = a_mensaje_oficial(REGISTRO_CO2, "l419")
    cuerpo = json.loads(carga)
    assert topico == "utec/gemelo/l419/nodo1/co2"
    assert "id" not in cuerpo and "gw_ms" not in cuerpo
    assert list(cuerpo)[:3] == ["nodo", "mac", "seq"]  # el orden del Gateway se respeta
    lectura = gateway.leer(topico, carga)
    assert lectura.campos["co2_ppm"] == 845 and lectura.grupo == "l419"


def test_un_registro_sin_tipo_valido_se_rechaza():
    with pytest.raises(gateway.MensajeInvalido):
        a_mensaje_oficial({**REGISTRO_CO2, "tipo": "humo"}, "l419")


def test_la_hora_faltante_se_estima_con_el_reloj_del_gateway():
    foto = {"hora_ok": True, "ts": 1_795_000_010_000, "gw_ms": 20_024}
    assert hora_estimada({**REGISTRO_CO2, "ts": None}, foto) == 1_795_000_000_000
    assert hora_estimada({**REGISTRO_CO2, "gw_ms": 99_999}, foto) is None  # de antes de un reinicio
    assert hora_estimada(REGISTRO_CO2, {"hora_ok": False}) is None


def test_la_seccion_gateway_ap_de_la_configuracion():
    configuracion = cargar_gateway_ap()
    assert configuracion.url == "http://192.168.4.1"
    assert configuracion.grupo != "sim"  # los datos del aula se rotulan como reales


# --- contra el Gateway falso por HTTP -----------------------------------------------------------

def test_el_puente_le_da_la_hora_y_publica_solo_lo_nuevo(falso):
    falso.paso(30)
    antes = falso.proximo_id - 1
    assert antes > 0 and falso.registros[0]["ts"] is None  # sin hora, como el Gateway real
    bus = BusEnMemoria()
    bus.suscribir("utec/gemelo/l419/#")
    puente = armar_puente(falso, bus)

    assert puente.ciclo() == 0  # arranca en lo que ya estaba guardado
    assert falso.ahora_ms() is not None  # le dio la hora de la laptop
    assert bus.retenidos["utec/gemelo/l419/gateway/estado"] == "online"

    falso.paso(30)
    publicados = puente.ciclo()
    mensajes = [(t, c) for t, c in bus.recibir_pendientes() if "/nodo" in t]
    assert publicados == len(mensajes) == falso.proximo_id - 1 - antes > 0
    for topico, carga in mensajes:
        lectura = gateway.leer(topico, carga)
        assert lectura.momento is not None  # ya no hay ts nulo


def test_desde_cero_reenvia_el_historial_y_estima_la_hora(falso):
    falso.paso(20)
    bus = BusEnMemoria()
    bus.suscribir("utec/gemelo/l419/#")
    puente = armar_puente(falso, bus, desde=0)
    assert puente.ciclo() == falso.proximo_id - 1
    assert puente.sin_hora == falso.proximo_id - 1  # todo se guardó antes de darle la hora
    assert all(json.loads(c)["ts"] for t, c in bus.recibir_pendientes() if "/nodo" in t)


def test_gateway_apagado_se_avisa_offline_y_vuelve_online(falso):
    bus = BusEnMemoria()
    puente = armar_puente(falso, bus)
    puente.ciclo()
    falso.apagado_hasta = time.monotonic() + 60
    puente.ciclo()
    assert bus.retenidos["utec/gemelo/l419/gateway/estado"] == "online"  # un fallo no basta
    puente.ciclo()
    assert bus.retenidos["utec/gemelo/l419/gateway/estado"] == "offline"
    falso.apagado_hasta = 0
    puente.ciclo()
    assert bus.retenidos["utec/gemelo/l419/gateway/estado"] == "online"


def test_si_el_gateway_borra_sus_datos_el_puente_vuelve_a_empezar(falso):
    falso.paso(20)
    bus = BusEnMemoria()
    bus.suscribir("utec/gemelo/l419/#")
    puente = armar_puente(falso, bus)
    puente.ciclo()
    falso.borrar()
    falso.paso(10)
    assert puente.ciclo() == falso.proximo_id - 1 > 0


def test_un_gateway_inalcanzable_da_un_error_claro():
    cliente = ClienteGatewayAP("http://127.0.0.1:9", espera_s=0.5)  # puerto cerrado
    with pytest.raises(GatewayNoResponde):
        cliente.estado()


def test_de_punta_a_punta_el_servicio_lee_al_gateway_por_el_puente(falso):
    """Gateway falso -> HTTP -> puente -> bus -> servicio del grupo, con los 7 nodos y el Gateway en línea."""
    bus = BusEnMemoria()
    servicio = Servicio(bus, grupo="l419")
    puente = armar_puente(falso, bus)
    puente.ciclo()
    falso.paso(60)
    puente.ciclo()
    servicio.ciclo(1.0)
    assert servicio.origen == "real"  # el grupo del aula se rotula real; el ensayo usa --grupo sim
    assert servicio.estado.gateway_en_linea is True
    assert set(servicio.estado.nodos) == {1, 2, 3, 4, 5, 6, 7}
