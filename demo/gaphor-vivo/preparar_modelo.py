"""Prepara la copia de demostracion del modelo SysML.

Toma `modelo/campus-twin-l419.gaphor`, le agrega un paquete con el diagrama
"Estado en vivo" y guarda el resultado como copia. El modelo del proyecto no se
toca: la demo siempre trabaja sobre la copia, asi nadie guarda por accidente
lecturas simuladas dentro del entregable.

    MODELO=modelo/campus-twin-l419.gaphor COPIA=/tmp/demo.gaphor \
        /Applications/Gaphor.app/Contents/MacOS/gaphor exec preparar_modelo.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import enlace  # noqa: E402
from gaphor.core.eventmanager import EventManager  # noqa: E402
from gaphor.core.modeling import ElementFactory, StyleSheet  # noqa: E402
from gaphor.diagram.drop import drop  # noqa: E402
from gaphor.plugins.autolayout import AutoLayout  # noqa: E402
from gaphor.services.modelinglanguage import ModelingLanguageService  # noqa: E402
from gaphor.storage.load import load  # noqa: E402
from gaphor.storage.save import save  # noqa: E402
from gaphor.SysML import sysml  # noqa: E402
from gaphor.UML.uml import Comment, Package  # noqa: E402

ANCHO_DE_LA_NOTA = 430.0
ANCHO_DE_BLOQUE = 430.0  # cabe la linea mas larga: "estadoPuerta ... = CERRADA"
SEPARACION = 34.0
COLUMNA_DE_BLOQUES_X = 500.0
BLOQUES_POR_FILA = 2


def cargar(ruta: Path) -> ElementFactory:
    fabrica = ElementFactory()
    lenguaje = ModelingLanguageService(event_manager=EventManager())
    with open(ruta, encoding="utf-8") as archivo:
        load(archivo, fabrica, lenguaje)
    return fabrica


def bloques_por_nombre(fabrica: ElementFactory) -> dict:
    return {bloque.name: bloque for bloque in fabrica.select(sysml.Block) if bloque.name}


def paquete_de_demo(fabrica: ElementFactory) -> Package:
    for paquete in fabrica.select(Package):
        if paquete.name == enlace.NOMBRE_DEL_PAQUETE:
            return paquete
    raiz = next(
        (p for p in fabrica.select(Package) if p.name == enlace.BLOQUE_DEL_SISTEMA and p.nestingPackage is None),
        None,
    )
    paquete = fabrica.create(Package)
    paquete.name = enlace.NOMBRE_DEL_PAQUETE
    if raiz is not None:
        paquete.nestingPackage = raiz
    return paquete


def armar_diagrama(fabrica: ElementFactory) -> None:
    paquete = paquete_de_demo(fabrica)
    for diagrama in fabrica.select(sysml.BlockDefinitionDiagram):
        if diagrama.name == enlace.NOMBRE_DEL_DIAGRAMA:
            return  # ya estaba armado

    diagrama = fabrica.create(sysml.BlockDefinitionDiagram)
    diagrama.name = enlace.NOMBRE_DEL_DIAGRAMA
    paquete.ownedDiagram = diagrama

    panel = fabrica.create(Comment)
    panel.body = enlace.panel({})
    item_de_panel = drop(panel, diagrama, 0, 0)
    item_de_panel.width = ANCHO_DE_LA_NOTA

    aviso = fabrica.create(Comment)
    aviso.body = (
        "Vista de demostración (RF-11). Los valores los escribe el simulador de "
        "demo/servidor en tiempo real. Este archivo es una copia: el entregable es "
        "modelo/campus-twin-l419.gaphor y no se modifica."
    )
    item_de_aviso = drop(aviso, diagrama, 0, 0)
    item_de_aviso.width = ANCHO_DE_LA_NOTA

    catalogo = bloques_por_nombre(fabrica)
    items_de_bloque = []
    for nombre in enlace.BLOQUES_DEL_TABLERO:
        bloque = catalogo.get(nombre)
        if bloque is None:
            print(f"AVISO: el modelo no tiene el bloque {nombre!r}")
            continue
        item = drop(bloque, diagrama, 0, 0)
        item.width = ANCHO_DE_BLOQUE
        if hasattr(item, "show_attributes"):
            item.show_attributes = True
        items_de_bloque.append(item)

    items = [item_de_panel, item_de_aviso, *items_de_bloque]
    # Primero se mide (cada caja crece segun su texto) y recien despues se
    # acomoda: al reves las cajas se solapan. Solo el pase de autolayout mide
    # el texto; sin el, todas conservan el alto por defecto.
    for item in items:
        if hasattr(item, "update_shapes"):
            item.update_shapes()
    AutoLayout().layout(diagrama)
    diagrama.update_now(items)
    acomodar(item_de_panel, item_de_aviso, items_de_bloque)
    diagrama.update_now(items)
    print(f"Diagrama '{diagrama.name}' armado con {len(items)} elementos")


def mover(item, x: float, y: float) -> None:
    item.matrix.translate(x - item.matrix[4], y - item.matrix[5])


def acomodar(item_de_panel, item_de_aviso, items_de_bloque) -> None:
    """Deja el panel a la izquierda y los bloques en una retícula a su derecha."""
    mover(item_de_panel, 0, 0)
    mover(item_de_aviso, 0, item_de_panel.height + SEPARACION)

    y = 0.0
    for inicio in range(0, len(items_de_bloque), BLOQUES_POR_FILA):
        fila = items_de_bloque[inicio : inicio + BLOQUES_POR_FILA]
        x = COLUMNA_DE_BLOQUES_X
        for item in fila:
            mover(item, x, y)
            x += item.width + SEPARACION
        y += max(item.height for item in fila) + SEPARACION


def hoja_de_estilo_inicial(fabrica: ElementFactory) -> None:
    hoja = next(iter(fabrica.select(StyleSheet)), None)
    if hoja is None:
        hoja = fabrica.create(StyleSheet)
    hoja.styleSheet = enlace.hoja_de_estilo({})


def main() -> None:
    origen = Path(os.environ["MODELO"]).resolve()
    destino = Path(os.environ["COPIA"]).resolve()
    fabrica = cargar(origen)
    armar_diagrama(fabrica)
    hoja_de_estilo_inicial(fabrica)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as archivo:
        save(archivo, fabrica)
    print(f"Copia de demostración lista: {destino}")


main()
