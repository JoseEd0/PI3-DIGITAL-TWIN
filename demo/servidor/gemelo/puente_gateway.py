"""Puente entre el Gateway con red propia (gateway_ap.ino) y el broker MQTT de la laptop.

Desde el 17/11/2026 el Gateway del aula (vendor/gateway_ap_l419/, adaptado por otro grupo del
curso) ya no publica por MQTT: crea su propia red Wi-Fi (GEMELO-L419), guarda cada mensaje en su
memoria flash con un `id` correlativo y lo sirve por HTTP. El JSON de cada mensaje es el del
contrato (docs/CONTRATO_DATOS.md) más dos campos: `id` y `gw_ms`.

El puente pide lo nuevo cada pocos segundos y lo publica en Mosquitto con el tópico oficial
`utec/gemelo/<grupo>/nodo<id>/<tipo>`, sin `id` ni `gw_ms`. Así Telegraf, InfluxDB, Grafana, el
servicio del grupo y Gaphor en vivo funcionan igual que con el Gateway MQTT. Además:

- le da al Gateway la hora de la laptop (/api/hora): sin internet no tiene NTP, y Telegraf
  descarta los mensajes con `ts` nulo;
- si aun así llega un mensaje sin hora, la estima con `gw_ms` y la última hora del Gateway;
- publica `online` u `offline` retenido en .../gateway/estado, como el LWT del Gateway MQTT, según
  si el Gateway responde, y deja `offline` como testamento si el puente se cae.

    python -m gemelo.puente_gateway                       # usa gateway_ap de config/nodos.yaml
    python -m gemelo.puente_gateway --url http://localhost:8090 --grupo sim   # ensayo (gateway_falso)
"""

from __future__ import annotations

import argparse
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

from . import gateway
from .configuracion import cargar_fuente, cargar_gateway_ap
from .transporte import ClienteMqtt, Transporte

log = logging.getLogger(__name__)

CAMPOS_PROPIOS_DEL_GATEWAY_AP = ("id", "gw_ms")  # no están en el contrato del Gateway MQTT
PAGINAS_POR_CICLO = 5  # para ponerse al día rápido si se acumularon mensajes
CICLOS_ENTRE_REPETICIONES_DEL_ESTADO = 15  # el estado retenido se repite por si Mosquitto reinició
SEGUNDOS_PARA_CONECTAR_AL_BROKER = 10
EN_LINEA, DESCONECTADO = "online", "offline"


class GatewayNoResponde(ConnectionError):
    """El Gateway no contestó: la laptop no está en su red, está apagado o fuera de alcance."""


class ClienteGatewayAP:
    """Las cuatro rutas de la API HTTP de gateway_ap.ino que usa el puente."""

    def __init__(self, url: str, espera_s: float) -> None:
        self.url = url.rstrip("/")
        self.espera_s = espera_s

    def _pedir(self, ruta: str, **parametros) -> bytes:
        direccion = f"{self.url}{ruta}"
        if parametros:
            direccion += "?" + urllib.parse.urlencode(parametros)
        try:
            with urllib.request.urlopen(direccion, timeout=self.espera_s) as respuesta:
                return respuesta.read()
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise GatewayNoResponde(f"{direccion}: {error}") from error

    def estado(self) -> dict:
        try:
            return json.loads(self._pedir("/api/estado"))
        except json.JSONDecodeError as error:
            raise GatewayNoResponde(f"/api/estado no devolvió JSON: {error}") from error

    def dar_hora(self, epoch_ms: int) -> None:
        self._pedir("/api/hora", epoch_ms=epoch_ms)

    def datos(self, desde: int, maximo: int) -> list[dict]:
        registros = []
        for linea in self._pedir("/api/datos", desde=desde, max=maximo).decode(errors="replace").splitlines():
            if not linea.strip():
                continue
            try:
                registros.append(json.loads(linea))
            except json.JSONDecodeError:
                log.warning("Línea del Gateway que no es JSON, se ignora: %.80s", linea)
        return registros


def a_mensaje_oficial(registro: dict, grupo: str) -> tuple[str, str]:
    """Tópico y JSON tal como los publicaría el Gateway MQTT (sin `id` ni `gw_ms`)."""
    tipo, nodo = registro.get("tipo"), registro.get("nodo")
    if tipo not in gateway.CAMPOS or not isinstance(nodo, int):
        raise gateway.MensajeInvalido(f"Registro sin tipo o nodo válido: {registro}")
    cuerpo = {clave: valor for clave, valor in registro.items() if clave not in CAMPOS_PROPIOS_DEL_GATEWAY_AP}
    return gateway.topico(grupo, nodo, tipo), json.dumps(cuerpo, ensure_ascii=False, separators=(",", ":"))


def hora_estimada(registro: dict, foto: dict | None) -> int | None:
    """Hora de un mensaje sin `ts`: la hora del Gateway en la última foto menos lo que pasó desde
    que lo recibió (`gw_ms` es el reloj interno del Gateway). Sin foto con hora, no se puede."""
    if not foto or not foto.get("hora_ok") or not foto.get("ts") or "gw_ms" not in registro:
        return None
    transcurrido = int(foto["gw_ms"]) - int(registro["gw_ms"])
    if transcurrido < 0:
        return None  # el mensaje es de antes de un reinicio del Gateway: su gw_ms no sirve
    return int(foto["ts"]) - transcurrido


class Puente:
    def __init__(self, cliente: ClienteGatewayAP, transporte: Transporte, grupo: str, *,
                 max_por_pedido: int, fallos_para_desconectado: int, desde: int | None = None,
                 reloj_ms: Callable[[], int] = lambda: int(time.time() * 1000)) -> None:
        """`desde=None` empieza por lo que llegue a partir de ahora; un número reenvía lo guardado
        en el Gateway desde ese id (0 = todo su historial)."""
        self.cliente = cliente
        self.transporte = transporte
        self.grupo = grupo
        self.max_por_pedido = max_por_pedido
        self.fallos_para_desconectado = fallos_para_desconectado
        self.ultimo_id = desde
        self.reloj_ms = reloj_ms
        self.en_linea: bool | None = None
        self.publicados = 0
        self.sin_hora = 0
        self._fallos_seguidos = 0
        self._ciclos = 0
        self._foto: dict | None = None

    @property
    def topico_estado(self) -> str:
        return gateway.topico_estado_gateway(self.grupo)

    def ciclo(self) -> int:
        """Un pedido al Gateway; devuelve cuántos mensajes publicó."""
        self._ciclos += 1
        try:
            publicados = self._traer_y_publicar()
        except GatewayNoResponde as error:
            self._fallos_seguidos += 1
            log.debug("Gateway sin respuesta (%d seguidas): %s", self._fallos_seguidos, error)
            if self._fallos_seguidos >= self.fallos_para_desconectado:
                self._marcar(False, str(error))
            return 0
        self._fallos_seguidos = 0
        self._marcar(True)
        if self._ciclos % CICLOS_ENTRE_REPETICIONES_DEL_ESTADO == 0:
            self._publicar_estado()
        return publicados

    def despedirse(self) -> None:
        self._marcar(False, "el puente se detuvo")

    # -- internos -----------------------------------------------------------------------------
    def _traer_y_publicar(self) -> int:
        foto = self._foto_con_hora()
        ultimo_del_gateway = int(foto.get("id_ultimo", 0))
        if self.ultimo_id is None:
            self.ultimo_id = ultimo_del_gateway
            log.info("Puente listo: el Gateway tiene %d mensajes guardados; se publican los nuevos",
                     ultimo_del_gateway)
        elif ultimo_del_gateway < self.ultimo_id:
            log.warning("El Gateway volvió a numerar desde %d (¿se borraron sus datos?); se sigue desde 0",
                        ultimo_del_gateway)
            self.ultimo_id = 0
        publicados = 0
        for _ in range(PAGINAS_POR_CICLO):
            if ultimo_del_gateway <= self.ultimo_id:
                break
            registros = self.cliente.datos(self.ultimo_id, self.max_por_pedido)
            if not registros:
                break
            publicados += sum(self._publicar(registro) for registro in registros)
            self.ultimo_id = max(self.ultimo_id, *(int(r.get("id", 0)) for r in registros))
            if len(registros) < self.max_por_pedido:
                break
        self.publicados += publicados
        return publicados

    def _foto_con_hora(self) -> dict:
        """Estado del Gateway; si perdió la hora (arrancó sin internet o se reinició), se la da."""
        foto = self.cliente.estado()
        if not foto.get("hora_ok"):
            self.cliente.dar_hora(self.reloj_ms())
            log.info("Se le dio la hora de la laptop al Gateway")
            foto = self.cliente.estado()
        self._foto = foto
        return foto

    def _publicar(self, registro: dict) -> int:
        if registro.get("ts") is None:
            self.sin_hora += 1
            registro = {**registro, "ts": hora_estimada(registro, self._foto) or self.reloj_ms()}
        try:
            topico, carga = a_mensaje_oficial(registro, self.grupo)
        except gateway.MensajeInvalido as error:
            log.warning("%s", error)
            return 0
        self.transporte.publicar(topico, carga)
        return 1

    def _marcar(self, en_linea: bool, motivo: str = "") -> None:
        if en_linea == self.en_linea:
            return
        self.en_linea = en_linea
        if en_linea:
            log.info("Gateway en línea en %s", self.cliente.url)
        else:
            log.warning("Gateway desconectado: %s", motivo)
        self._publicar_estado()

    def _publicar_estado(self) -> None:
        if self.en_linea is not None:
            self.transporte.publicar(self.topico_estado, EN_LINEA if self.en_linea else DESCONECTADO, retenido=True)


def main() -> None:
    configuracion, fuente = cargar_gateway_ap(), cargar_fuente()
    parser = argparse.ArgumentParser(description="Pasa los datos del Gateway con red propia (HTTP) al broker MQTT")
    parser.add_argument("--url", default=configuracion.url, help=f"Gateway (por defecto {configuracion.url})")
    parser.add_argument("--grupo", default=configuracion.grupo,
                        help=f"Grupo con que se publican los mensajes (por defecto {configuracion.grupo})")
    parser.add_argument("--periodo", type=float, default=configuracion.periodo_s, help="Segundos entre pedidos")
    parser.add_argument("--desde", type=int, default=None,
                        help="Reenvía lo guardado en el Gateway desde ese id (0 = todo); por defecto, solo lo nuevo")
    argumentos = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    topico_estado = gateway.topico_estado_gateway(argumentos.grupo)
    transporte = ClienteMqtt(fuente.mqtt_host, fuente.mqtt_puerto, "campustwin-puente",
                             testamento=(topico_estado, DESCONECTADO))
    if not transporte.esperar_conexion(SEGUNDOS_PARA_CONECTAR_AL_BROKER):
        log.warning("Mosquitto no responde en %s:%s; se sigue intentando", fuente.mqtt_host, fuente.mqtt_puerto)
    puente = Puente(ClienteGatewayAP(argumentos.url, configuracion.espera_s), transporte, argumentos.grupo,
                    max_por_pedido=configuracion.max_por_pedido,
                    fallos_para_desconectado=configuracion.fallos_para_desconectado, desde=argumentos.desde)
    log.info("Puente %s -> MQTT %s:%s, grupo «%s», cada %.1f s", argumentos.url, fuente.mqtt_host,
             fuente.mqtt_puerto, argumentos.grupo, argumentos.periodo)
    try:
        while True:
            inicio = time.monotonic()
            if puente.ciclo():
                log.debug("Publicados %d en total", puente.publicados)
            time.sleep(max(0.0, argumentos.periodo - (time.monotonic() - inicio)))
    except KeyboardInterrupt:
        log.info("Deteniendo el puente (%d mensajes publicados, %d sin hora del Gateway)",
                 puente.publicados, puente.sin_hora)
    finally:
        puente.despedirse()
        time.sleep(0.5)  # deja salir el "offline" antes de cerrar
        transporte.cerrar()


if __name__ == "__main__":
    main()
