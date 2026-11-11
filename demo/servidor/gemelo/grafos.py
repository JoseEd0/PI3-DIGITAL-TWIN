"""Carga de los grafos causales (grafos/*.yaml) y evaluación de sus eventos observables."""

from __future__ import annotations

import operator
from pathlib import Path

from .configuracion import CARPETA_DE_GRAFOS, leer_yaml
from .estado import EstadoDelAula
from .razonamiento import Diagnostico, Grafo, Motor

NIVEL_MINIMO_DE_VIOLACION = 1  # alerta

_OPERADORES = {
    "==": operator.eq, "!=": operator.ne, ">": operator.gt, ">=": operator.ge,
    "<": operator.lt, "<=": operator.le,
    "contiene": lambda coleccion, valor: valor in coleccion,
    "no_contiene": lambda coleccion, valor: valor not in coleccion,
}


class ObservableInvalido(ValueError):
    pass


def evaluar_observable(especificacion: dict, estado: EstadoDelAula) -> bool | None:
    """Verdadero, falso o None (sin datos para saberlo)."""
    if "todas" in especificacion:
        resultados = [evaluar_observable(parte, estado) for parte in especificacion["todas"]]
        if False in resultados:
            return False
        return True if all(r is True for r in resultados) else None
    if "alguna" in especificacion:
        resultados = [evaluar_observable(parte, estado) for parte in especificacion["alguna"]]
        if True in resultados:
            return True
        return False if all(r is False for r in resultados) else None
    if "ra" in especificacion:
        nivel = estado.niveles_ra.get(especificacion["ra"])
        return None if nivel is None or nivel < 0 else nivel >= NIVEL_MINIMO_DE_VIOLACION
    try:
        comparar = _OPERADORES[especificacion["op"]]
        campo = especificacion["campo"]
    except KeyError as error:
        raise ObservableInvalido(f"Observable sin 'campo' u 'op' válido: {especificacion}") from error
    valor = estado.valor(campo)
    if valor is None:
        return None
    try:
        return bool(comparar(valor, especificacion["valor"]))
    except TypeError:
        return None


def cargar_grafos(carpeta: Path = CARPETA_DE_GRAFOS) -> dict[str, Grafo]:
    """Un grafo por RA, indexado por el id del RA."""
    grafos: dict[str, Grafo] = {}
    for ruta in sorted(carpeta.glob("ra-*.yaml")):
        grafo = Grafo.desde_diccionario(ruta.stem, leer_yaml(ruta))
        grafos[grafo.ra] = grafo
    return grafos


class Razonador:
    """Evalúa los observables de cada grafo y corre el motor SymCure."""

    def __init__(self, grafos: dict[str, Grafo]) -> None:
        self.grafos = grafos
        self.motores = {ra: Motor(g) for ra, g in grafos.items()}

    def observaciones(self, ra: str, estado: EstadoDelAula) -> dict[str, bool | None]:
        return {
            ident: evaluar_observable(evento.observable, estado)
            for ident, evento in self.grafos[ra].eventos.items()
            if evento.observable
        }

    def diagnosticar(self, ra: str, estado: EstadoDelAula) -> Diagnostico:
        return self.motores[ra].diagnosticar(self.observaciones(ra, estado))

    def diagnosticar_todo(self, estado: EstadoDelAula) -> dict[str, Diagnostico]:
        return {ra: self.diagnosticar(ra, estado) for ra in self.grafos}

    def estructura(self, ra: str) -> dict:
        """El grafo como nodos y aristas, para dibujarlo en el dashboard."""
        grafo = self.grafos[ra]
        return {
            "ra": grafo.ra, "titulo": grafo.titulo, "central": grafo.evento_central,
            "nodos": [
                {"id": e.id, "texto": e.texto, "clase": e.clase, "entrada": e.entrada, "salida": e.salida,
                 "observable": bool(e.observable),
                 "sensor": (e.observable or {}).get("sensor", "") if e.observable else "",
                 "recomendacion": e.recomendacion}
                for e in grafo.eventos.values()
            ],
            "aristas": [[c, ef] for e in grafo.eventos.values() for c in [e.id] for ef in e.efectos],
        }
