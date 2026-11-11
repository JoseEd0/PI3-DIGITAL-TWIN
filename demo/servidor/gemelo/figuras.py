"""Figuras de los grafos causales para el reporte (Graphviz).

    python -m gemelo.figuras            # grafos/figuras/ra-XX-*.svg y .png

Convención visual: causas raíz en naranja, condiciones de contexto en gris, eventos intermedios en
blanco, el evento central (la violación del RA) en rojo y los efectos en violeta. Borde grueso =
observable con un sensor; borde punteado = inferido. Cada nodo indica su lógica de entrada/salida.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from .configuracion import CARPETA_DE_GRAFOS
from .grafos import cargar_grafos
from .razonamiento import Grafo

COLORES = {"causa": "#fde2c4", "condicion": "#e6e6e6", "intermedio": "#ffffff",
           "sintoma": "#d9ecff", "efecto": "#e8dcf7"}
COLOR_CENTRAL = "#f8c9c9"
FORMATOS = ("svg", "png")


def _escapar(texto: str) -> str:
    return texto.replace('"', '\\"')


def a_dot(grafo: Grafo) -> str:
    lineas = [
        f'digraph "{grafo.id}" {{',
        '  rankdir=LR; splines=true; nodesep=0.25; ranksep=0.5;',
        f'  label="{grafo.ra} · {_escapar(grafo.titulo)}"; labelloc=t; fontsize=18; fontname="Helvetica";',
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11];',
        '  edge [color="#555555", arrowsize=0.7];',
    ]
    for evento in grafo.eventos.values():
        central = evento.id == grafo.evento_central
        logica = f"{evento.entrada}-{evento.salida}" if evento.causas else f"salida {evento.salida}"
        if evento.entrada == "NM" and evento.causas:
            logica = f"N/M≥{evento.fraccion:.0%}-{evento.salida}"
        if evento.entrada == "IF" and evento.condicion:
            logica = f"IF({evento.condicion})-{evento.salida}"
        sensor = (evento.observable or {}).get("sensor", "") if evento.observable else ""
        detalle = f"observable: {sensor}" if evento.observable else "inferido"
        etiqueta = f"{_escapar(evento.texto)}\\n[{logica}] · {_escapar(detalle)}"
        estilo = '"rounded,filled,bold"' if evento.observable else '"rounded,filled,dashed"'
        color = COLOR_CENTRAL if central else COLORES[evento.clase]
        ancho = 3 if central else (2 if evento.observable else 1)
        lineas.append(f'  "{evento.id}" [label="{etiqueta}", fillcolor="{color}", style={estilo}, penwidth={ancho}];')
    for evento in grafo.eventos.values():
        for efecto in evento.efectos:
            lineas.append(f'  "{evento.id}" -> "{efecto}";')
    lineas.append("}")
    return "\n".join(lineas)


def generar(carpeta_salida: Path | None = None) -> list[Path]:
    dot = shutil.which("dot")
    if dot is None:
        raise SystemExit("Falta Graphviz: instálalo con `brew install graphviz`")
    salida = carpeta_salida or CARPETA_DE_GRAFOS / "figuras"
    salida.mkdir(parents=True, exist_ok=True)
    generados: list[Path] = []
    for grafo in cargar_grafos().values():
        fuente = salida / f"{grafo.id}.dot"
        fuente.write_text(a_dot(grafo), encoding="utf-8")
        for formato in FORMATOS:
            destino = salida / f"{grafo.id}.{formato}"
            argumentos = [dot, f"-T{formato}", str(fuente), "-o", str(destino)]
            if formato == "png":
                argumentos.insert(2, "-Gdpi=130")
            subprocess.run(argumentos, check=True, timeout=60)
            generados.append(destino)
    return generados


if __name__ == "__main__":
    for ruta in generar(Path(sys.argv[1]) if len(sys.argv) > 1 else None):
        print(ruta)
