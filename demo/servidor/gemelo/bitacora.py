"""Log de eventos del aula: el "footprint" que pide el proyecto del curso.

Cada línea de logs/events.jsonl es un evento con hora, tipo, severidad, RA o nodo involucrado,
causas, recomendaciones y origen (datos simulados o reales). Se puede filtrar y exportar a CSV.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from .configuracion import RAIZ_DEL_REPO, ZONA_HORARIA

log = logging.getLogger(__name__)

RUTA_POR_DEFECTO = Path(os.environ.get("CAMPUSTWIN_LOG", RAIZ_DEL_REPO / "logs" / "events.jsonl"))
EVENTOS_EN_MEMORIA = 2000
SEVERIDADES = ("info", "alerta", "critico")


@dataclass
class EventoDelAula:
    ts: str
    tipo: str
    severidad: str
    mensaje: str
    origen: str
    ra: str | None = None
    nodo: int | None = None
    causas: list[str] = field(default_factory=list)
    recomendaciones: list[str] = field(default_factory=list)


class Bitacora:
    def __init__(self, ruta: Path | None = RUTA_POR_DEFECTO) -> None:
        self.ruta = ruta
        self.eventos: deque[EventoDelAula] = deque(maxlen=EVENTOS_EN_MEMORIA)
        if ruta is not None:
            ruta.parent.mkdir(parents=True, exist_ok=True)

    def registrar(self, momento: datetime, tipo: str, severidad: str, mensaje: str, origen: str, **extra) -> EventoDelAula:
        if severidad not in SEVERIDADES:
            raise ValueError(f"Severidad desconocida: {severidad}")
        # El Gateway fecha en UTC; el log se lee en la hora del aula (Lima), con su desfase explícito.
        local = momento.astimezone(ZONA_HORARIA)
        evento = EventoDelAula(local.isoformat(timespec="seconds"), tipo, severidad, mensaje, origen, **extra)
        self.eventos.appendleft(evento)
        if self.ruta is not None:
            try:
                with self.ruta.open("a", encoding="utf-8") as archivo:
                    archivo.write(json.dumps(asdict(evento), ensure_ascii=False) + "\n")
            except OSError:
                # Perder una línea del archivo no debe tumbar el servicio; queda en memoria.
                log.exception("No se pudo escribir el log de eventos en %s", self.ruta)
        return evento

    def listar(self, *, tipo: str | None = None, severidad: str | None = None, ra: str | None = None,
               limite: int = 200) -> list[dict]:
        filtrados = (
            e for e in self.eventos
            if (tipo is None or e.tipo == tipo)
            and (severidad is None or e.severidad == severidad)
            and (ra is None or e.ra == ra)
        )
        return [asdict(e) for _, e in zip(range(limite), filtrados)]

    def como_csv(self, **filtros) -> str:
        filas = self.listar(limite=EVENTOS_EN_MEMORIA, **filtros)
        salida = io.StringIO()
        columnas = ["ts", "tipo", "severidad", "ra", "nodo", "mensaje", "causas", "recomendaciones", "origen"]
        escritor = csv.DictWriter(salida, fieldnames=columnas)
        escritor.writeheader()
        for fila in filas:
            fila["causas"] = " | ".join(fila["causas"])
            fila["recomendaciones"] = " | ".join(fila["recomendaciones"])
            escritor.writerow({c: fila.get(c) for c in columnas})
        return salida.getvalue()
