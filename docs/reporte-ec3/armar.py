"""Arma el reporte de la EC3 desde plantilla.html en dos formatos.

    python3 docs/reporte-ec3/armar.py

- reporte-ec3.html: un solo archivo con las figuras incrustadas, listo para subir a Google Docs
  (ignorado por git, porque pesa varios MB).
- reporte-ec3.md: la versión que GitHub muestra renderizada. Enlaza las figuras del repositorio por
  ruta relativa en vez de incrustarlas, así que se versiona sin duplicar imágenes.

Las figuras se marcan en la plantilla como {{img:ruta/desde/la/raiz|Pie de figura}}.
"""

import base64
import os
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
PLANTILLA = AQUI / "plantilla.html"
SALIDA_HTML = AQUI / "reporte-ec3.html"
SALIDA_MD = AQUI / "reporte-ec3.md"
ANCHO_PX = 620  # ancho útil de una página carta con márgenes de 2,54 cm
MARCA = re.compile(r"\{\{img:([^|}]+)\|([^}]+)\}\}")
ENVOLTURA = re.compile(r"</?(html|body)>|<head>.*?</head>", re.DOTALL)
AVISO_MD = ("<!-- Generado por docs/reporte-ec3/armar.py desde plantilla.html. "
            "No se edita a mano: se cambia la plantilla y se vuelve a armar. -->\n\n")


def _partes(coincidencia: re.Match) -> tuple[str, str]:
    return coincidencia.group(1).strip(), coincidencia.group(2).strip()


def figura_incrustada(coincidencia: re.Match) -> str:
    ruta, pie = _partes(coincidencia)
    datos = base64.b64encode((RAIZ / ruta).read_bytes()).decode()
    return (f'<p style="text-align:center"><img src="data:image/png;base64,{datos}" width="{ANCHO_PX}"></p>\n'
            f'<p style="text-align:center"><i>{pie}</i></p>')


def figura_enlazada(coincidencia: re.Match) -> str:
    # GitHub descarta el atributo style, pero respeta align.
    ruta, pie = _partes(coincidencia)
    if not (RAIZ / ruta).is_file():
        raise FileNotFoundError(f"La plantilla cita una figura que no existe: {ruta}")
    relativa = Path(os.path.relpath(RAIZ / ruta, AQUI)).as_posix()
    return (f'<p align="center"><img src="{relativa}" width="{ANCHO_PX}"></p>\n'
            f'<p align="center"><i>{pie}</i></p>')


def armar_html(plantilla: str) -> None:
    SALIDA_HTML.write_text(MARCA.sub(figura_incrustada, plantilla), encoding="utf-8")
    print(SALIDA_HTML, f"{SALIDA_HTML.stat().st_size / 1e6:.1f} MB")


def armar_md(plantilla: str) -> None:
    cuerpo = ENVOLTURA.sub("", MARCA.sub(figura_enlazada, plantilla))
    cuerpo = cuerpo.replace('style="text-align:center"', 'align="center"').strip()
    SALIDA_MD.write_text(AVISO_MD + cuerpo + "\n", encoding="utf-8")
    print(SALIDA_MD, f"{SALIDA_MD.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    texto = PLANTILLA.read_text(encoding="utf-8")
    armar_html(texto)
    armar_md(texto)
