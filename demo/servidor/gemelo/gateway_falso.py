"""Gateway falso con la API HTTP de gateway_ap.ino, para ensayar el puente sin el hardware.

Imita lo que hace el Gateway con red propia (vendor/gateway_ap_l419/gateway_ap/gateway_ap.ino):
guarda cada mensaje con un `id` correlativo y `gw_ms`, no tiene hora hasta que alguien llama a
/api/hora (sus mensajes llegan con `ts` nulo) y sirve /api/estado, /api/ultimos, /api/datos,
/api/hora y /api/borrar. Los mensajes los produce el simulador del grupo, así que son datos
**simulados**: el ensayo se corre con `--grupo sim` en el puente para que todo lo rotule así.

    python -m gemelo.gateway_falso --puerto 8090
    curl "http://localhost:8090/falso/escenario?nombre=gas"     # cambiar de escenario
    curl "http://localhost:8090/falso/apagar?segundos=20"       # simular que el Gateway se cae
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .simulador import Reloj, Simulador

log = logging.getLogger(__name__)

CAPACIDAD = 20_000  # el Gateway real guarda ~1,2 MB y descarta lo más antiguo
SEGUNDOS_POR_PASO = 1.0
MAX_POR_DEFECTO = 2000  # como hDatos() de gateway_ap.ino
HORA_MINIMA_VALIDA_MS = 1_700_000_000_000  # el Gateway ignora horas anteriores a esta


class GatewayFalso:
    """El estado del Gateway: mensajes guardados, hora y si está "encendido"."""

    def __init__(self, simulador: Simulador) -> None:
        self.simulador = simulador
        self.registros: deque[dict] = deque(maxlen=CAPACIDAD)
        self.proximo_id = 1
        self.arranque = time.monotonic()
        self.desfase_hora_ms: int | None = None  # hora real - reloj interno; None = sin hora
        self.apagado_hasta = 0.0
        self.candado = threading.Lock()

    # -- reloj --------------------------------------------------------------------------------
    def gw_ms(self) -> int:
        return int((time.monotonic() - self.arranque) * 1000)

    def ahora_ms(self) -> int | None:
        return None if self.desfase_hora_ms is None else self.gw_ms() + self.desfase_hora_ms

    def dar_hora(self, epoch_ms: int) -> None:
        if epoch_ms > HORA_MINIMA_VALIDA_MS:
            self.desfase_hora_ms = epoch_ms - self.gw_ms()

    @property
    def encendido(self) -> bool:
        return time.monotonic() >= self.apagado_hasta

    # -- datos --------------------------------------------------------------------------------
    def paso(self, segundos: float) -> None:
        with self.candado:
            for _topico, carga, retenido in self.simulador.avanzar(segundos):
                if retenido:
                    continue  # el estado online/offline lo maneja el puente, no el Gateway
                self._guardar(json.loads(carga))

    def _guardar(self, mensaje: dict) -> None:
        # Mismo orden de campos que procesar() en gateway_ap.ino: id primero y gw_ms tras ts.
        registro: dict[str, object] = {"id": self.proximo_id}
        for clave, valor in mensaje.items():
            registro[clave] = self.ahora_ms() if clave == "ts" else valor
            if clave == "ts":
                registro["gw_ms"] = self.gw_ms()
        self.registros.append(registro)
        self.proximo_id += 1

    def estado(self) -> dict:
        ahora = self.ahora_ms()
        return {"gw_ms": self.gw_ms(), "ts": ahora or 0, "hora_ok": ahora is not None,
                "id_ultimo": self.proximo_id - 1, "descartados": 0, "modo": "AP", "falso": True}

    def ultimos(self) -> list[dict]:
        por_nodo: dict[int, dict] = {}
        for registro in self.registros:
            por_nodo[registro["nodo"]] = registro
        return [{"nodo": nodo, "tipo": r["tipo"], "hace_s": (self.gw_ms() - r["gw_ms"]) // 1000,
                 "anomalias": r["anomalias"], "msg": r} for nodo, r in sorted(por_nodo.items())]

    def datos(self, desde: int, maximo: int) -> list[dict]:
        with self.candado:
            return [r for r in self.registros if r["id"] > desde][:maximo]

    def borrar(self) -> None:
        with self.candado:
            self.registros.clear()
            self.proximo_id = 1


def crear_manejador(falso: GatewayFalso) -> type[BaseHTTPRequestHandler]:
    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, format, *args) -> None:  # noqa: A002 (firma de http.server)
            log.debug(format, *args)

        def _responder(self, codigo: int, cuerpo: str, tipo: str = "application/json") -> None:
            datos = cuerpo.encode()
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)

        def do_GET(self) -> None:  # noqa: N802 (nombre que exige http.server)
            ruta = urlparse(self.path)
            argumentos = {k: v[0] for k, v in parse_qs(ruta.query).items()}
            if ruta.path.startswith("/falso/"):
                self._control(ruta.path, argumentos)
                return
            if not falso.encendido:
                self._responder(503, '{"error":"gateway apagado (simulado)"}')
                return
            if ruta.path == "/api/estado":
                self._responder(200, json.dumps(falso.estado()))
            elif ruta.path == "/api/ultimos":
                self._responder(200, json.dumps(falso.ultimos(), separators=(",", ":")))
            elif ruta.path == "/api/datos":
                registros = falso.datos(int(argumentos.get("desde", 0)), int(argumentos.get("max", MAX_POR_DEFECTO)))
                lineas = "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in registros)
                self._responder(200, lineas, "application/x-ndjson")
            elif ruta.path == "/api/hora":
                if "epoch_ms" in argumentos:
                    falso.dar_hora(int(argumentos["epoch_ms"]))
                self._responder(200, json.dumps({"ts": falso.ahora_ms() or 0}))
            elif ruta.path == "/api/borrar":
                if argumentos.get("confirmar") != "si":
                    self._responder(400, "Agregue ?confirmar=si para borrar los datos del gateway", "text/plain")
                    return
                falso.borrar()
                self._responder(200, '{"ok":true}')
            else:
                self._responder(404, '{"error":"ruta desconocida"}')

        def _control(self, ruta: str, argumentos: dict) -> None:
            if ruta == "/falso/escenario":
                try:
                    with falso.candado:
                        falso.simulador.aplicar_escenario(argumentos.get("nombre", ""))
                except ValueError as error:
                    self._responder(400, json.dumps({"error": str(error)}))
                    return
                self._responder(200, json.dumps({"escenario": falso.simulador.escenario}))
            elif ruta == "/falso/apagar":
                falso.apagado_hasta = time.monotonic() + float(argumentos.get("segundos", 30))
                self._responder(200, json.dumps({"apagado_s": float(argumentos.get("segundos", 30))}))
            else:
                self._responder(404, '{"error":"control desconocido"}')

    return Manejador


def iniciar(falso: GatewayFalso, puerto: int, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    """Levanta el servidor y el avance del simulador en hilos; devuelve el servidor para cerrarlo."""
    servidor = ThreadingHTTPServer((host, puerto), crear_manejador(falso))
    threading.Thread(target=servidor.serve_forever, daemon=True).start()

    def avanzar_siempre() -> None:
        while True:
            falso.paso(SEGUNDOS_POR_PASO)
            time.sleep(SEGUNDOS_POR_PASO)

    threading.Thread(target=avanzar_siempre, daemon=True).start()
    return servidor


def main() -> None:
    parser = argparse.ArgumentParser(description="Gateway falso con la API de gateway_ap.ino (datos simulados)")
    parser.add_argument("--puerto", type=int, default=8090)
    parser.add_argument("--velocidad", type=float, default=1.0, help="Segundos simulados por segundo real")
    parser.add_argument("--semilla", type=int, default=419)
    argumentos = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    falso = GatewayFalso(Simulador(Reloj(velocidad=argumentos.velocidad), semilla=argumentos.semilla))
    servidor = iniciar(falso, argumentos.puerto)
    log.info("Gateway falso en http://localhost:%d (datos SIMULADOS; sin hora hasta /api/hora)", argumentos.puerto)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        servidor.shutdown()


if __name__ == "__main__":
    main()
