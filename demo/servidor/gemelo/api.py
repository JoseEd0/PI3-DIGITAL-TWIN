"""API REST + flujo de eventos (SSE) del servicio del grupo, y el tablero web.

Se crea con `crear_app(servicio)`. El ciclo del servicio corre en una tarea de fondo mientras la
app está viva. El tablero (demo/tablero/dist) se sirve en `/` si está construido.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .configuracion import RAIZ_DEL_REPO, cargar_fuente
from .servicio import Servicio

log = logging.getLogger(__name__)

PERIODO_DEL_CICLO_S = 0.5
PERIODO_DEL_FLUJO_S = 1.0
CARPETA_DEL_TABLERO = RAIZ_DEL_REPO / "demo" / "tablero" / "dist"
VELOCIDAD_MAXIMA = 600.0


def crear_app(servicio: Servicio) -> FastAPI:
    @asynccontextmanager
    async def vida(_app: FastAPI):
        tarea = asyncio.create_task(_correr(servicio))
        yield
        tarea.cancel()
        servicio.transporte.cerrar()

    app = FastAPI(title="Campus Twin L-419 — servicio del Grupo 1", lifespan=vida)
    # El tablero en modo desarrollo (vite, otro puerto) también tiene que poder leer la API.
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

    @app.get("/api/estado")
    def estado():
        return servicio.instantanea()

    @app.get("/api/requisitos")
    def requisitos():
        return [c.como_diccionario() for c in servicio.condiciones.values()]

    @app.get("/api/grafos")
    def grafos():
        return [{"ra": ra, "titulo": g.titulo, "archivo": g.id} for ra, g in servicio.razonador.grafos.items()]

    @app.get("/api/grafos/{ra}")
    def grafo(ra: str):
        if ra not in servicio.razonador.grafos:
            raise HTTPException(404, f"No hay grafo para {ra}")
        diagnostico = servicio.razonador.diagnosticar(ra, servicio.estado)
        return servicio.razonador.estructura(ra) | {"diagnostico": diagnostico.como_diccionario()}

    @app.get("/api/eventos")
    def eventos(tipo: str | None = None, severidad: str | None = None, ra: str | None = None,
                limite: int = Query(200, le=2000)):
        return servicio.bitacora.listar(tipo=tipo, severidad=severidad, ra=ra, limite=limite)

    @app.get("/api/eventos.csv", response_class=PlainTextResponse)
    def eventos_csv(tipo: str | None = None, severidad: str | None = None, ra: str | None = None):
        contenido = servicio.bitacora.como_csv(tipo=tipo, severidad=severidad, ra=ra)
        return PlainTextResponse(contenido, media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=eventos_l419.csv"})

    @app.get("/api/salud")
    def salud():
        return {"gatewayEnLinea": servicio.estado.gateway_en_linea, "nodos": servicio.estado.salud()}

    @app.get("/api/fantasma")
    def fantasma():
        return servicio.fantasma.como_diccionario()

    @app.get("/api/aula")
    def aula():
        return {"nombre": servicio.aula.nombre, "plano": servicio.aula.plano,
                "largo": servicio.aula.valor("aula.largo_m"), "ancho": servicio.aula.valor("aula.ancho_m"),
                "supuestos": servicio.aula.resumen_de_supuestos()}

    @app.get("/api/historico")
    def historico(nodo: int, campo: str, minutos: int = Query(60, le=60 * 24 * 7)):
        if nodo not in servicio.nodos:
            raise HTTPException(404, f"No existe el nodo {nodo}")
        return _historico(servicio, nodo, campo, minutos)

    @app.post("/api/demo/escenario/{nombre}")
    def escenario(nombre: str):
        try:
            servicio.aplicar_escenario(nombre)
        except (ValueError, RuntimeError) as error:
            raise HTTPException(400, str(error)) from error
        return {"escenario": nombre}

    @app.post("/api/demo/velocidad/{valor}")
    def velocidad(valor: float):
        if not servicio.simulador:
            raise HTTPException(400, "No hay simulador")
        servicio.simulador.reloj.velocidad = max(1.0, min(VELOCIDAD_MAXIMA, valor))
        return {"velocidad": servicio.simulador.reloj.velocidad}

    @app.post("/api/demo/pausa")
    def pausa():
        if not servicio.simulador:
            raise HTTPException(400, "No hay simulador")
        servicio.simulador.reloj.pausado = not servicio.simulador.reloj.pausado
        return {"pausado": servicio.simulador.reloj.pausado}

    @app.get("/api/stream")
    async def flujo():
        async def generar():
            while True:
                yield f"data: {json.dumps(servicio.instantanea(), ensure_ascii=False, default=str)}\n\n"
                await asyncio.sleep(PERIODO_DEL_FLUJO_S)

        return StreamingResponse(generar(), media_type="text/event-stream")

    if CARPETA_DEL_TABLERO.exists():
        app.mount("/", StaticFiles(directory=CARPETA_DEL_TABLERO, html=True), name="tablero")
    return app


async def _correr(servicio: Servicio) -> None:
    while True:
        await asyncio.sleep(PERIODO_DEL_CICLO_S)
        try:
            servicio.ciclo(PERIODO_DEL_CICLO_S)
        except Exception:
            # Un ciclo fallido no puede tumbar el tablero delante del público; se registra y sigue.
            log.exception("Falló un ciclo del servicio; se continúa con el siguiente")


def _historico(servicio: Servicio, nodo: int, campo: str, minutos: int) -> dict:
    """Desde InfluxDB si hay token; si no, la tendencia en memoria del servicio."""
    fuente = cargar_fuente()
    tipo = servicio.nodos[nodo].tipo
    if fuente.influx_token:
        try:
            from influxdb_client import InfluxDBClient

            consulta = (
                f'from(bucket: "{fuente.influx_bucket}") |> range(start: -{minutos}m, stop: 1d) '
                f'|> filter(fn: (r) => r._measurement == "{tipo}" and r._field == "{campo}" '
                f'and r.nodo == "{nodo}" and r.grupo == "{servicio.grupo}") '
                f'|> aggregateWindow(every: {max(1, minutos // 120)}m, fn: mean, createEmpty: false)'
            )
            with InfluxDBClient(url=fuente.influx_url, token=fuente.influx_token, org=fuente.influx_org,
                                timeout=5000) as cliente:
                tablas = cliente.query_api().query(consulta)
            puntos = [(r.get_time().isoformat(timespec="seconds"), r.get_value()) for t in tablas for r in t.records]
            return {"fuente": "influxdb", "nodo": nodo, "campo": campo, "puntos": puntos}
        except Exception as error:  # InfluxDB caído o sin red: se cae a la memoria, no se rompe la API
            log.warning("No se pudo consultar InfluxDB (%s); se usa la memoria del servicio", error)
    limite = (servicio.estado.ahora or datetime.now()) - timedelta(minutes=minutos)
    puntos = [p for p in servicio.tendencias[nodo] if datetime.fromisoformat(p[0]) >= limite]
    return {"fuente": "memoria", "nodo": nodo, "campo": campo, "puntos": puntos}
