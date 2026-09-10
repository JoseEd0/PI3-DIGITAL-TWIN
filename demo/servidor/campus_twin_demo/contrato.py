"""Contrato de datos entre los nodos y el servidor.

Es el mismo contrato que define la tarea de la semana 6 (docs/03-plan.md): un
mensaje por nodo y magnitud, publicado en `l419/<nodo>/<magnitud>`, con marca de
tiempo, numero de secuencia y origen. La secuencia es lo que permite descartar
duplicados cuando un nodo reenvia su buffer (RF-05).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime

from . import configuracion as cfg


def topico(nodo: str, magnitud: str) -> str:
    return f"{cfg.PREFIJO_DE_TOPICO}/{nodo}/{magnitud}"


@dataclass(frozen=True)
class Muestra:
    """Una lectura de una magnitud de un nodo."""

    nodo: str
    magnitud: str
    valor: float
    momento: datetime
    secuencia: int
    unidad: str = ""
    origen: str = cfg.ORIGEN_DEMO

    @property
    def topico(self) -> str:
        return topico(self.nodo, self.magnitud)

    def como_diccionario(self) -> dict:
        return {
            "topico": self.topico,
            "nodo": self.nodo,
            "magnitud": self.magnitud,
            "valor": self.valor,
            "unidad": self.unidad or cfg.UNIDADES.get(self.magnitud, ""),
            "ts": self.momento.isoformat(timespec="seconds"),
            "seq": self.secuencia,
            "origen": self.origen,
        }

    def como_json(self) -> str:
        return json.dumps(self.como_diccionario(), ensure_ascii=False)


@dataclass(frozen=True)
class Evento:
    """Un hecho puntual del laboratorio: apertura de puerta, golpe, reinicio."""

    nodo: str
    tipo: str
    momento: datetime
    detalle: str = ""
    datos: dict = field(default_factory=dict)

    def como_diccionario(self) -> dict:
        return {
            "nodo": self.nodo,
            "tipo": self.tipo,
            "ts": self.momento.isoformat(timespec="seconds"),
            "detalle": self.detalle,
            **self.datos,
        }
