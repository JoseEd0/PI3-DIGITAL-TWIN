"""Transporte de mensajes: MQTT real (Mosquitto del stack del docente) o un bus en memoria.

Los dos tienen la misma interfaz. El servicio no sabe cuál usa: con broker los mensajes del
simulador pasan por Mosquitto y llegan también a Telegraf e InfluxDB; sin broker (pruebas o una
laptop sin Docker) todo queda en el proceso.
"""

from __future__ import annotations

import logging
import queue
from typing import Protocol

log = logging.getLogger(__name__)

ESPERA_MINIMA_RECONEXION_S = 1
ESPERA_MAXIMA_RECONEXION_S = 30
SEGUNDOS_DE_KEEPALIVE = 30


class Transporte(Protocol):
    def publicar(self, topico: str, carga: str, retenido: bool = False) -> None: ...
    def suscribir(self, patron: str) -> None: ...
    def recibir_pendientes(self) -> list[tuple[str, bytes]]: ...
    def cerrar(self) -> None: ...


def coincide(patron: str, topico: str) -> bool:
    """Comodines MQTT: '+' es un nivel, '#' es el resto."""
    partes_patron, partes_topico = patron.split("/"), topico.split("/")
    for i, parte in enumerate(partes_patron):
        if parte == "#":
            return True
        if i >= len(partes_topico) or (parte != "+" and parte != partes_topico[i]):
            return False
    return len(partes_patron) == len(partes_topico)


class BusEnMemoria:
    def __init__(self) -> None:
        self._patrones: list[str] = []
        self._cola: list[tuple[str, bytes]] = []
        self.retenidos: dict[str, str] = {}

    def publicar(self, topico: str, carga: str, retenido: bool = False) -> None:
        if retenido:
            self.retenidos[topico] = carga
        if any(coincide(p, topico) for p in self._patrones):
            self._cola.append((topico, carga.encode()))

    def suscribir(self, patron: str) -> None:
        self._patrones.append(patron)
        for topico, carga in self.retenidos.items():
            if coincide(patron, topico):
                self._cola.append((topico, carga.encode()))

    def recibir_pendientes(self) -> list[tuple[str, bytes]]:
        pendientes, self._cola = self._cola, []
        return pendientes

    def cerrar(self) -> None:
        self._cola.clear()


class ClienteMqtt:
    """Cliente paho con reconexión automática; los mensajes llegan por un hilo a una cola."""

    def __init__(self, host: str, puerto: int, identificador: str) -> None:
        import paho.mqtt.client as mqtt

        self._cola: queue.Queue[tuple[str, bytes]] = queue.Queue()
        self._patrones: list[str] = []
        self._cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=identificador)
        self._cliente.reconnect_delay_set(ESPERA_MINIMA_RECONEXION_S, ESPERA_MAXIMA_RECONEXION_S)
        self._cliente.on_connect = self._al_conectar
        self._cliente.on_message = lambda _c, _u, msg: self._cola.put((msg.topic, msg.payload))
        self._cliente.on_disconnect = lambda *_: log.warning("MQTT desconectado; reintentando")
        self._cliente.connect_async(host, puerto, keepalive=SEGUNDOS_DE_KEEPALIVE)
        self._cliente.loop_start()
        self.host, self.puerto = host, puerto

    def _al_conectar(self, cliente, _datos, _banderas, codigo, _propiedades=None) -> None:
        if codigo.is_failure:
            log.error("MQTT rechazó la conexión: %s", codigo)
            return
        log.info("MQTT conectado a %s:%s", self.host, self.puerto)
        for patron in self._patrones:  # al reconectar hay que volver a suscribirse
            cliente.subscribe(patron, qos=0)

    def publicar(self, topico: str, carga: str, retenido: bool = False) -> None:
        self._cliente.publish(topico, carga, qos=0, retain=retenido)

    def suscribir(self, patron: str) -> None:
        self._patrones.append(patron)
        self._cliente.subscribe(patron, qos=0)

    def recibir_pendientes(self) -> list[tuple[str, bytes]]:
        pendientes = []
        while True:
            try:
                pendientes.append(self._cola.get_nowait())
            except queue.Empty:
                return pendientes

    def cerrar(self) -> None:
        self._cliente.loop_stop()
        self._cliente.disconnect()
