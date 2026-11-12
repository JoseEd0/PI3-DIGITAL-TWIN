"""Exporta RA-01..10 y el resumen de su grafo causal como JSON, para build_model.py.

Corre con el Python del servicio, que tiene PyYAML y los cargadores de `gemelo`:

    demo/servidor/.venv/bin/python modelo/tools/exportar_ra.py

Asi el modelo lee config/requisitos_ra.yaml y grafos/ exactamente igual que el servicio.
build_model.py no puede leerlos directo porque corre en el interprete de Gaphor, que no
tiene pip ni PyYAML.
"""

import json
import sys
from pathlib import Path

RAIZ_DEL_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_DEL_REPO / "demo" / "servidor"))

from gemelo.configuracion import cargar_requisitos  # noqa: E402
from gemelo.grafos import Razonador, cargar_grafos  # noqa: E402


def resumen_del_grafo(estructura: dict) -> dict:
    """Titulo, causas raiz y efectos del grafo, en el orden en que los declara el YAML."""

    def textos(clase: str) -> list[str]:
        return [nodo["texto"] for nodo in estructura["nodos"] if nodo["clase"] == clase]

    return {"titulo": estructura["titulo"], "causas": textos("causa"), "efectos": textos("efecto")}


def main() -> None:
    requisitos = cargar_requisitos()
    razonador = Razonador(cargar_grafos())
    salida = {
        ident: {**requisito, "resumen_del_grafo": resumen_del_grafo(razonador.estructura(ident))}
        for ident, requisito in requisitos.items()
    }
    json.dump(salida, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
