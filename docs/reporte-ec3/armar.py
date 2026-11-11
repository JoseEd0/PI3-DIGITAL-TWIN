"""Arma el reporte de la EC3 en un solo HTML con las figuras incrustadas, listo para subir a Google Docs.

    python3 docs/reporte-ec3/armar.py      # escribe docs/reporte-ec3/reporte-ec3.html (ignorado por git)

Las figuras se marcan en la plantilla como {{img:ruta/desde/la/raiz|Pie de figura}}.
"""

import base64
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLA = Path(__file__).with_name("plantilla.html")
SALIDA = Path(__file__).with_name("reporte-ec3.html")
ANCHO_PX = 620  # ancho útil de una página carta con márgenes de 2,54 cm
MARCA = re.compile(r"\{\{img:([^|}]+)\|([^}]+)\}\}")


def figura(coincidencia: re.Match) -> str:
    ruta, pie = coincidencia.group(1).strip(), coincidencia.group(2).strip()
    datos = base64.b64encode((RAIZ / ruta).read_bytes()).decode()
    return (f'<p style="text-align:center"><img src="data:image/png;base64,{datos}" width="{ANCHO_PX}"></p>\n'
            f'<p style="text-align:center"><i>{pie}</i></p>')


if __name__ == "__main__":
    SALIDA.write_text(MARCA.sub(figura, PLANTILLA.read_text(encoding="utf-8")), encoding="utf-8")
    print(SALIDA, f"{SALIDA.stat().st_size / 1e6:.1f} MB")
