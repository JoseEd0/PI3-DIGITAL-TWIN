"""Arranca el servicio del grupo.

    # con el simulador, publicando por el Mosquitto del stack del docente (recomendado)
    python -m gemelo --simular

    # leyendo datos reales del Gateway (grupo del Gateway de S1 G1), sin simulador
    python -m gemelo --grupo grupoX

    # sin broker ni Docker: todo en memoria
    python -m gemelo --simular --sin-broker
"""

from __future__ import annotations

import argparse
import logging

import uvicorn

from .api import crear_app
from .configuracion import cargar_fuente
from .servicio import Servicio
from .simulador import Reloj, Simulador
from .transporte import BusEnMemoria, ClienteMqtt

SEGUNDOS_PARA_CERRAR = 3


def main() -> None:
    fuente = cargar_fuente()
    parser = argparse.ArgumentParser(description="Servicio del gemelo digital del L-419 (Grupo 1, Sección 8)")
    parser.add_argument("--simular", action="store_true", help="Corre el simulador de los 7 nodos (grupo 'sim')")
    parser.add_argument("--velocidad", type=float, default=1.0,
                        help="Segundos simulados por segundo real (1 = tiempo real; InfluxDB recibe la hora simulada)")
    parser.add_argument("--grupo", default=None, help="Grupo del Gateway a leer (por defecto el de config/nodos.yaml)")
    parser.add_argument("--sin-broker", action="store_true", help="No usa MQTT: bus en memoria")
    parser.add_argument("--host", default="0.0.0.0", help="0.0.0.0 para que cualquier laptop de la red entre")
    parser.add_argument("--puerto", type=int, default=8000)
    parser.add_argument("--semilla", type=int, default=419)
    argumentos = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    transporte = (BusEnMemoria() if argumentos.sin_broker
                  else ClienteMqtt(fuente.mqtt_host, fuente.mqtt_puerto, "campustwin-servicio"))
    simulador = Simulador(Reloj(velocidad=argumentos.velocidad), semilla=argumentos.semilla) if argumentos.simular else None
    servicio = Servicio(transporte, simulador, grupo=argumentos.grupo)
    # El flujo SSE del tablero nunca cierra solo: sin este límite, Ctrl+C esperaría para siempre.
    uvicorn.run(crear_app(servicio), host=argumentos.host, port=argumentos.puerto, log_level="info",
                timeout_graceful_shutdown=SEGUNDOS_PARA_CERRAR)


if __name__ == "__main__":
    main()
