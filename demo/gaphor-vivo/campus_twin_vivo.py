"""Refleja el estado del laboratorio simulado dentro de Gaphor, en vivo.

Abre la copia de demostracion del modelo SysML y va escribiendo, cada segundo,
el valor de cada magnitud en la propiedad del bloque que le corresponde. Lo que
se ve en pantalla es el modelo del proyecto con numeros encima: el mismo bloque
`Nodo Ambiental` que se entrego en la semana 4, mostrando el CO2 de ahora.

Corre con el interprete que trae Gaphor, asi que solo usa la biblioteca
estandar:

    MODELO_DEMO=... API=http://127.0.0.1:8000 \
        /Applications/Gaphor.app/Contents/MacOS/gaphor exec campus_twin_vivo.py

Variables de entorno:
    MODELO_DEMO  copia del modelo que se abre (obligatoria)
    API          base del servidor de la demo (por defecto 127.0.0.1:8000)
    PERIODO      segundos entre consultas (por defecto 1)
    LOG          archivo donde escribir el registro (por defecto, la salida)
    MAX_TICKS    termina despues de N actualizaciones (para pruebas)
    GUARDAR_EN   guarda el modelo al terminar (para pruebas)
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import enlace  # noqa: E402
from gi.repository import GLib, Gtk  # noqa: E402

from gaphor.core.modeling import StyleSheet  # noqa: E402
from gaphor.storage.save import save  # noqa: E402
from gaphor.SysML import sysml  # noqa: E402
from gaphor.transaction import Transaction  # noqa: E402
from gaphor.ui import Session, run  # noqa: E402
from gaphor.UML.uml import Comment, LiteralString, Property  # noqa: E402

API = os.environ.get("API", "http://127.0.0.1:8000").rstrip("/")
PERIODO = float(os.environ.get("PERIODO", "1"))
MAX_TICKS = int(os.environ.get("MAX_TICKS", "0"))
GUARDAR_EN = os.environ.get("GUARDAR_EN", "")
TIEMPO_DE_ESPERA = 4.0
INTENTOS_DE_ENGANCHE = 50  # 20 s esperando a que Gaphor termine de leer el modelo
ESPERA_TRAS_ERROR = 3.0
MARCA_DEL_PANEL = "ESTADO EN VIVO"

_registro = open(os.environ["LOG"], "w", buffering=1, encoding="utf-8") if os.environ.get("LOG") else sys.stdout


def anotar(*partes) -> None:
    print(*partes, file=_registro, flush=True)


# La sesion se crea dentro de Gaphor cuando abre el archivo; se captura aqui
# porque no hay otra forma de alcanzarla desde un script externo.
SESIONES: list = []
_crear_sesion_original = Session.__init__


def _crear_sesion(self, *args, **kwargs):
    _crear_sesion_original(self, *args, **kwargs)
    SESIONES.append(self)


Session.__init__ = _crear_sesion


class EnlaceConElModelo:
    """Escribe el estado del gemelo en las propiedades del modelo."""

    def __init__(self, sesion) -> None:
        self.sesion = sesion
        self.fabrica = sesion.get_service("element_factory")
        self.eventos = sesion.get_service("event_manager")
        self._propiedades: dict[tuple[str, str], Property] = {}
        self._panel: Comment | None = None
        self._diagrama_abierto = False
        self._indexar()

    def _indexar(self) -> None:
        for bloque in self.fabrica.select(sysml.Block):
            for propiedad in bloque.ownedAttribute:
                if propiedad.name:
                    self._propiedades[(bloque.name, propiedad.name)] = propiedad
        for comentario in self.fabrica.select(Comment):
            if (comentario.body or "").startswith(MARCA_DEL_PANEL):
                self._panel = comentario
        anotar(f"Modelo indexado: {len(self._propiedades)} propiedades de valor")

    # -- escritura -----------------------------------------------------------
    def _fijar(self, bloque: str, propiedad: str, texto: str) -> None:
        objetivo = self._propiedades.get((bloque, propiedad))
        if objetivo is None:
            return
        literal = objetivo.defaultValue
        if not isinstance(literal, LiteralString):
            literal = self.fabrica.create(LiteralString)
            objetivo.defaultValue = literal
        if literal.value != texto:
            literal.value = texto

    def _escribir_magnitudes(self, estado: dict) -> None:
        resumen = estado.get("resumen", {})
        for bloque, campos in enlace.MAPA_DE_PROPIEDADES.items():
            for propiedad, clave, formatear in campos:
                if clave in resumen:
                    self._fijar(bloque, propiedad, formatear(resumen[clave]))

        salud = estado.get("salud", [])
        senales = [fila["senal"] for fila in salud if fila.get("senal") is not None]
        if senales:
            bloque, propiedad = enlace.PROPIEDAD_DE_SENAL
            self._fijar(bloque, propiedad, f"{min(senales):.0f}")

        perdidas = [fila.get("muestrasPerdidas", 0.0) for fila in salud]
        if perdidas:
            bloque, propiedad = enlace.PROPIEDAD_DE_MUESTRAS_PERDIDAS
            self._fijar(bloque, propiedad, f"{max(perdidas):.2f}")

    def _escribir_panel(self, estado: dict) -> None:
        if self._panel is None:
            return
        texto = enlace.panel(estado)
        if self._panel.body != texto:
            self._panel.body = texto

    def _escribir_colores(self, estado: dict) -> None:
        hoja = next(iter(self.fabrica.select(StyleSheet)), None)
        if hoja is None:
            return
        css = enlace.hoja_de_estilo(estado)
        if hoja.styleSheet != css:
            hoja.styleSheet = css

    def aplicar(self, estado: dict, latencia: float) -> None:
        with Transaction(self.eventos):
            self._escribir_magnitudes(estado)
            bloque, propiedad = enlace.PROPIEDAD_DE_LATENCIA
            self._fijar(bloque, propiedad, f"{latencia:.3f}")
            self._escribir_panel(estado)
            self._escribir_colores(estado)

    # -- ventana -------------------------------------------------------------
    def abrir_diagrama_de_demo(self) -> None:
        if self._diagrama_abierto:
            return
        diagrama = next(
            (
                d
                for d in self.fabrica.select(sysml.SysMLDiagram)
                if d.name == enlace.NOMBRE_DEL_DIAGRAMA
            ),
            None,
        )
        if diagrama is None:
            anotar("AVISO: la copia no tiene el diagrama de demo; corre preparar_modelo.py")
            self._diagrama_abierto = True
            return
        try:
            diagramas = self.sesion.get_service("diagrams")
            if not diagramas.set_current_diagram(diagrama):
                diagramas.create_diagram_page(diagrama)
            anotar(f"Diagrama abierto: {diagrama.name}")
        except Exception as error:  # la demo sigue aunque no se pueda abrir solo
            anotar(f"No se pudo abrir el diagrama automaticamente: {error}")
        self._diagrama_abierto = True

    def guardar(self, ruta: str) -> None:
        destino = Path(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "w", encoding="utf-8") as archivo:
            save(archivo, self.fabrica)
        anotar(f"Modelo guardado en {destino}")


class Consultor(threading.Thread):
    """Consulta el API en segundo plano para no congelar la ventana."""

    def __init__(self, al_recibir) -> None:
        super().__init__(daemon=True)
        self.al_recibir = al_recibir
        self.detener = threading.Event()
        self.consultas = 0
        self.fallos = 0

    def run(self) -> None:
        while not self.detener.is_set():
            inicio = time.monotonic()
            try:
                with urllib.request.urlopen(f"{API}/api/estado", timeout=TIEMPO_DE_ESPERA) as respuesta:
                    estado = json.loads(respuesta.read().decode("utf-8"))
                latencia = time.monotonic() - inicio
                self.consultas += 1
                self.fallos = 0
                GLib.idle_add(self.al_recibir, estado, latencia)
                self.detener.wait(PERIODO)
            except (urllib.error.URLError, OSError, ValueError) as error:
                self.fallos += 1
                if self.fallos == 1 or self.fallos % 10 == 0:
                    anotar(f"Sin respuesta del servidor ({error}). Reintentando cada {ESPERA_TRAS_ERROR} s")
                GLib.idle_add(self.al_recibir, None, 0.0)
                self.detener.wait(ESPERA_TRAS_ERROR)


class DemoEnVivo:
    def __init__(self) -> None:
        self.enlace: EnlaceConElModelo | None = None
        self.consultor = Consultor(self.al_recibir)
        self.actualizaciones = 0
        self.intentos_de_enganche = 0

    def al_recibir(self, estado, latencia: float) -> bool:
        if estado is None or self.enlace is None:
            return False
        try:
            self.enlace.aplicar(estado, latencia)
        except Exception as error:
            anotar(f"No se pudo aplicar el estado: {error!r}")
            return False
        self.actualizaciones += 1
        if self.actualizaciones % 10 == 1:
            resumen = estado.get("resumen", {})
            reloj = estado.get("reloj", {})
            anotar(
                f"[{self.actualizaciones}] {reloj.get('hora', '')} "
                f"{resumen.get('potencia', 0):.0f} W · {resumen.get('co2', 0):.0f} ppm · "
                f"{'ocupado' if resumen.get('presencia') else 'vacío'} · "
                f"{len(estado.get('alertas', []))} alertas · {latencia * 1000:.0f} ms"
            )
        if MAX_TICKS and self.actualizaciones >= MAX_TICKS:
            self.terminar()
        return False

    def terminar(self) -> None:
        self.consultor.detener.set()
        if GUARDAR_EN and self.enlace is not None:
            try:
                self.enlace.guardar(GUARDAR_EN)
            except Exception as error:
                anotar(f"No se pudo guardar: {error!r}")
        aplicacion = Gtk.Application.get_default()
        if aplicacion is not None:
            aplicacion.quit()

    def esperar_a_la_sesion(self) -> bool:
        """Engancha con la sesion cuando el modelo ya esta cargado.

        Gaphor crea la sesion antes de terminar de leer el archivo, asi que hay
        que esperar a que aparezcan los bloques: si se indexa antes, el enlace
        queda vacio y no se escribe ningun valor.
        """
        self.intentos_de_enganche += 1
        if self.intentos_de_enganche > INTENTOS_DE_ENGANCHE:
            anotar("El modelo no termino de cargar; se abandona el enlace en vivo")
            self.terminar()
            return False
        if not SESIONES:
            return True
        sesion = SESIONES[-1]
        fabrica = sesion.get_service("element_factory")
        if not any(True for _ in fabrica.select(sysml.Block)):
            return True

        self.enlace = EnlaceConElModelo(sesion)
        self.enlace.abrir_diagrama_de_demo()
        self.consultor.start()
        anotar(f"Enlace en vivo iniciado contra {API} cada {PERIODO} s")
        return False


def main() -> None:
    modelo = os.environ.get("MODELO_DEMO")
    if not modelo or not Path(modelo).is_file():
        anotar("Falta MODELO_DEMO: corre primero lanzar.sh o preparar_modelo.py")
        raise SystemExit(2)
    demo = DemoEnVivo()
    GLib.timeout_add(400, demo.esperar_a_la_sesion)
    run(["gaphor", modelo])
    demo.consultor.detener.set()
    anotar(f"Gaphor cerrado tras {demo.actualizaciones} actualizaciones")


main()
