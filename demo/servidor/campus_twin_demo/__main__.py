"""Arranca el servidor de la demo.

    python -m campus_twin_demo --puerto 8000 --velocidad 60
"""

from __future__ import annotations

import argparse
import logging

import uvicorn

from . import configuracion as cfg


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de la demo de Campus Twin L-419")
    parser.add_argument("--puerto", type=int, default=cfg.PUERTO_POR_DEFECTO)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--velocidad",
        type=float,
        default=cfg.VELOCIDAD_POR_DEFECTO,
        help="Cuantos segundos simulados pasan por segundo real (60 = un dia en 24 min)",
    )
    parser.add_argument("--semilla", type=int, default=419, help="Semilla del simulador")
    argumentos = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    from .api import app, gemelo

    gemelo.ajustar_velocidad(argumentos.velocidad)
    gemelo.simulador.azar.seed(argumentos.semilla)
    uvicorn.run(app, host=argumentos.host, port=argumentos.puerto, log_level="info")


if __name__ == "__main__":
    main()
