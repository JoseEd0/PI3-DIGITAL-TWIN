"""API REST y flujo de eventos del gemelo simulado.

Reproduce la forma de la API del sistema real (RF-06, RF-07): consulta por rango
y magnitud, estado en vivo, alertas, salud y reporte de consumo fantasma. El
tablero web y el modelo SysML en Gaphor son dos clientes distintos de estos
mismos endpoints.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import configuracion as cfg
from .gemelo import GemeloEnVivo
from .simulador import ESCENARIOS

log = logging.getLogger(__name__)

TABLERO = Path(__file__).resolve().parents[2] / "frontend" / "dist"
# El tablero se sirve desde el mismo servidor para que la demo sea una sola URL,
# igual que en la Pi. En desarrollo Vite corre aparte y necesita CORS.
ORIGENES_DE_DESARROLLO = ["http://localhost:5173", "http://127.0.0.1:5173"]

gemelo = GemeloEnVivo()


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    gemelo.iniciar()
    try:
        yield
    finally:
        await gemelo.detener()


app = FastAPI(
    title="Campus Twin L-419 — demo",
    description="Gemelo digital simulado del laboratorio L-419 (RF-11)",
    version="1.0",
    lifespan=ciclo_de_vida,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_DE_DESARROLLO,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/estado")
def estado() -> dict:
    return gemelo.instantanea()


@app.get("/api/resumen")
def resumen() -> dict:
    """Version corta del estado, para clientes con poco ancho de banda."""
    instantanea = gemelo.instantanea()
    return {
        "reloj": instantanea["reloj"],
        "resumen": instantanea["resumen"],
        "alertas": instantanea["alertas"],
        "fantasma": instantanea["fantasma"],
        "salud": instantanea["salud"],
    }


@app.get("/api/historico")
def historico(
    nodo: str = Query(..., description="Identificador del nodo, por ejemplo 'ambiental'"),
    magnitud: str = Query(..., description="Magnitud, por ejemplo 'co2'"),
    limite: int = Query(120, ge=1, le=cfg.MUESTRAS_POR_SERIE),
) -> dict:
    if nodo not in cfg.NODOS:
        raise HTTPException(status_code=404, detail=f"No existe el nodo '{nodo}'")
    return {
        "nodo": nodo,
        "magnitud": magnitud,
        "unidad": cfg.UNIDADES.get(magnitud, ""),
        "muestras": gemelo.almacen.historico(nodo, magnitud, limite),
    }


@app.get("/api/alertas")
def alertas() -> dict:
    return {
        "activas": gemelo.reglas.activas_como_lista(),
        "recientes": gemelo.reglas.historial_como_lista(),
    }


@app.get("/api/salud")
def salud() -> dict:
    return {"nodos": gemelo.almacen.salud_como_lista(gemelo.reloj.momento)}


@app.get("/api/fantasma")
def fantasma() -> dict:
    return gemelo.auditor.como_diccionario()


@app.get("/api/configuracion")
def configuracion() -> dict:
    return {
        "horarioOficial": list(cfg.HORARIO_OFICIAL),
        "umbralDeCo2": cfg.UMBRAL_DE_CO2_PPM,
        "tarifa": cfg.TARIFA_SOLES_POR_KWH,
        "factorDeEmision": cfg.FACTOR_DE_EMISION_KG_POR_KWH,
        "aforo": cfg.AFORO_DEL_LABORATORIO,
        "nodos": {nodo: {"etiqueta": e, "requisito": r, "periodo": p} for nodo, (e, r, p) in cfg.NODOS.items()},
        "escenarios": ESCENARIOS,
    }


@app.post("/api/demo/escenario/{nombre}")
def cambiar_escenario(nombre: str) -> dict:
    if nombre not in ESCENARIOS:
        raise HTTPException(status_code=404, detail=f"Escenario desconocido: {nombre}")
    gemelo.aplicar_escenario(nombre)
    return {"escenario": gemelo.simulador.escenario}


@app.post("/api/demo/velocidad/{valor}")
def cambiar_velocidad(valor: float) -> dict:
    return {"velocidad": gemelo.ajustar_velocidad(valor)}


@app.post("/api/demo/pausa")
def alternar_pausa() -> dict:
    return {"pausado": gemelo.alternar_pausa()}


async def flujo_de_estado():
    """Genera el estado en formato SSE, un evento cada INTERVALO_DE_STREAM_S."""
    while True:
        datos = json.dumps(gemelo.instantanea(), ensure_ascii=False)
        yield f"data: {datos}\n\n"
        await asyncio.sleep(cfg.INTERVALO_DE_STREAM_S)


@app.get("/api/stream")
async def stream() -> StreamingResponse:
    """Envia el estado por SSE, que es como el tablero se mantiene al dia."""
    return StreamingResponse(
        flujo_de_estado(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if TABLERO.is_dir():
    app.mount("/assets", StaticFiles(directory=TABLERO / "assets"), name="assets")

    @app.get("/")
    def tablero() -> FileResponse:
        return FileResponse(TABLERO / "index.html")

else:

    @app.get("/")
    def tablero_sin_construir() -> dict:
        return {
            "mensaje": "El tablero no esta construido todavia.",
            "comoConstruirlo": "cd demo/frontend && npm install && npm run build",
            "mientrasTanto": "La API ya responde en /api/estado",
        }
