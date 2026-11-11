"""Deriva los tableros del docente para cargarlos por aprovisionamiento de archivos.

Los JSON de vendor/gemelo_iot_profesor/servidor_iot/ están exportados para importarse a mano
desde la interfaz: cada panel apunta a la fuente `${DS_INFLUXDB}`, que Grafana solo resuelve en
ese asistente. Por aprovisionamiento el marcador queda literal y todos los paneles dicen
"No data". Esta copia derivada cambia esa referencia por `null` (la fuente por defecto, que es la
InfluxDB del docente) y no toca nada más. Se regenera con:

    python3 deploy/grafana/derivar_tableros.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "vendor" / "gemelo_iot_profesor" / "servidor_iot"
DESTINO = Path(__file__).resolve().parent / "tableros"
TABLEROS = ("dashboard_gemelo_L419_7sensores.json", "dashboard_gemelo_iot.json")
MARCADOR_FUENTE = "${DS_INFLUXDB}"


def _es_referencia_al_marcador(valor) -> bool:
    return isinstance(valor, dict) and valor.get("uid") == MARCADOR_FUENTE


def _resolver_fuente(nodo):
    """Recorre el JSON y deja en null cada referencia a la fuente exportada."""
    if isinstance(nodo, dict):
        return {
            clave: None if clave == "datasource" and _es_referencia_al_marcador(valor)
            else _resolver_fuente(valor)
            for clave, valor in nodo.items()
            if clave != "__inputs"
        }
    if isinstance(nodo, list):
        return [_resolver_fuente(elemento) for elemento in nodo]
    return nodo


def derivar(nombre: str) -> int:
    tablero = _resolver_fuente(json.loads((ORIGEN / nombre).read_text(encoding="utf-8")))
    texto = json.dumps(tablero, ensure_ascii=False, indent=2)
    if MARCADOR_FUENTE in texto:
        raise ValueError(f"{nombre}: quedó una referencia a {MARCADOR_FUENTE} sin resolver")
    (DESTINO / nombre).write_text(texto + "\n", encoding="utf-8")
    return texto.count('"datasource": null')


if __name__ == "__main__":
    DESTINO.mkdir(exist_ok=True)
    for nombre in TABLEROS:
        print(f"{nombre}: {derivar(nombre)} referencias resueltas")
