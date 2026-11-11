"""Escribe en InfluxDB lo que produce el grupo: el log de eventos y la condición de cada RA.

Telegraf del docente solo se suscribe a los 7 tipos de nodo, así que nuestros tópicos
`campustwin/...` no llegan a la base. En vez de tocar su configuración, el servicio escribe
directo, en measurements propios que no chocan con los del Gateway:

- `campustwin_evento`: una fila por evento del log (tags tipo, severidad, ra, nodo, grupo, origen);
- `campustwin_ra`: el nivel de cada RA (-1 desconocido, 0 nominal, 1 alerta, 2 crítico).

La escritura va por lotes en un hilo del cliente de InfluxDB: si la base está caída, los
reintentos ocurren allí y el ciclo del servicio no se detiene.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Protocol

from .bitacora import EventoDelAula
from .configuracion import Fuente
from .requisitos import GRAVEDAD

log = logging.getLogger(__name__)

MEDICION_DE_EVENTOS = "campustwin_evento"
MEDICION_DE_REQUISITOS = "campustwin_ra"
TAMANO_DEL_LOTE = 200
INTERVALO_DE_ENVIO_MS = 2_000
ESPERA_ENTRE_REINTENTOS_MS = 5_000
REINTENTOS_MAXIMOS = 5
TIEMPO_DE_ESPERA_MS = 5_000
SEVERIDAD_NUMERICA = {"info": 0, "alerta": 1, "critico": 2}


class RegistroDeSalidas(Protocol):
    def evento(self, evento: EventoDelAula, grupo: str) -> None: ...
    def requisitos(self, momento: datetime, condiciones: dict, grupo: str, origen: str) -> None: ...
    def cerrar(self) -> None: ...


def punto_de_evento(evento: EventoDelAula, grupo: str):
    from influxdb_client import Point

    punto = (Point(MEDICION_DE_EVENTOS)
             .tag("grupo", grupo).tag("origen", evento.origen)
             .tag("tipo", evento.tipo).tag("severidad", evento.severidad)
             .field("mensaje", evento.mensaje)
             .field("severidad_num", SEVERIDAD_NUMERICA[evento.severidad])
             .field("causas", " | ".join(evento.causas))
             .field("recomendaciones", " | ".join(evento.recomendaciones))
             .time(datetime.fromisoformat(evento.ts)))
    if evento.ra:
        punto.tag("ra", evento.ra)
    if evento.nodo is not None:
        punto.tag("nodo", str(evento.nodo))
    return punto


def puntos_de_requisitos(momento: datetime, condiciones: dict, grupo: str, origen: str) -> list:
    from influxdb_client import Point

    return [Point(MEDICION_DE_REQUISITOS).tag("grupo", grupo).tag("origen", origen).tag("ra", ra)
            .field("nivel", GRAVEDAD[condicion.nivel]).field("nivel_texto", condicion.nivel).time(momento)
            for ra, condicion in condiciones.items()]


class RegistroEnInflux:
    def __init__(self, fuente: Fuente) -> None:
        from influxdb_client import InfluxDBClient, WriteOptions

        self._bucket, self._org = fuente.influx_bucket, fuente.influx_org
        self._cliente = InfluxDBClient(url=fuente.influx_url, token=fuente.influx_token, org=fuente.influx_org,
                                       timeout=TIEMPO_DE_ESPERA_MS)
        opciones = WriteOptions(batch_size=TAMANO_DEL_LOTE, flush_interval=INTERVALO_DE_ENVIO_MS,
                                retry_interval=ESPERA_ENTRE_REINTENTOS_MS, max_retries=REINTENTOS_MAXIMOS)
        self._escritura = self._cliente.write_api(write_options=opciones,
                                                  error_callback=self._al_fallar)
        log.info("Log de eventos y RA también en InfluxDB (%s, bucket %s)", fuente.influx_url, self._bucket)

    @staticmethod
    def _al_fallar(_lote, _datos, error) -> None:
        log.warning("InfluxDB no aceptó un lote del log (%s); el archivo events.jsonl sigue completo", error)

    def _escribir(self, registros) -> None:
        self._escritura.write(bucket=self._bucket, org=self._org, record=registros)

    def evento(self, evento: EventoDelAula, grupo: str) -> None:
        self._escribir(punto_de_evento(evento, grupo))

    def requisitos(self, momento: datetime, condiciones: dict, grupo: str, origen: str) -> None:
        if condiciones:
            self._escribir(puntos_de_requisitos(momento, condiciones, grupo, origen))

    def cerrar(self) -> None:
        # close() vacía el lote pendiente antes de soltar la conexión.
        self._escritura.close()
        self._cliente.close()


class RegistroEnMemoria:
    """Para pruebas y para correr sin InfluxDB: guarda lo que se habría escrito."""

    def __init__(self) -> None:
        self.eventos: list[tuple[EventoDelAula, str]] = []
        self.requisitos_escritos: list[tuple[datetime, dict]] = []

    def evento(self, evento: EventoDelAula, grupo: str) -> None:
        self.eventos.append((evento, grupo))

    def requisitos(self, momento: datetime, condiciones: dict, grupo: str, origen: str) -> None:
        self.requisitos_escritos.append((momento, {ra: c.nivel for ra, c in condiciones.items()}))

    def cerrar(self) -> None:
        """Nada que vaciar."""


def crear_registro(fuente: Fuente) -> RegistroDeSalidas | None:
    if not fuente.influx_token:
        log.info("Sin INFLUX_TOKEN: el log de eventos queda solo en events.jsonl")
        return None
    return RegistroEnInflux(fuente)
