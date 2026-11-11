"""Grabación y reproducción de los mensajes del Gateway (RF-11, CP-11).

Una grabación es un JSONL: la primera línea es una cabecera y cada línea siguiente es un mensaje
MQTT tal como lo publicó el Gateway (o el simulador), con su instante relativo al inicio:

    {"formato": "campustwin-grabacion", "version": 1, "origen": "simulado", "grupo_original": "sim", ...}
    {"t": 12.0, "topico": "utec/gemelo/sim/nodo1/co2", "carga": "{...}", "retenido": false}

Sirve para tres cosas:
- repetir una demo exactamente igual (los escenarios grabados son deterministas por la semilla);
- guardar una sesión con el Gateway real (S15) y volver a analizarla sin el hardware;
- probar el servicio con los mismos datos antes y después de un cambio.

    python -m gemelo.grabacion simular --guion 0:clase,10:gas --minutos 20 --salida grabaciones/gas.jsonl
    python -m gemelo.grabacion grabar --grupo grupoX --minutos 30 --salida grabaciones/real.jsonl
    python -m gemelo.grabacion info grabaciones/gas.jsonl
    python -m gemelo --reproducir grabaciones/gas.jsonl --velocidad 10     # el tablero la muestra

La carga se reproduce sin tocarla (incluido su `ts`): el reloj del aula arranca en la hora de la
grabación, así que InfluxDB y el servicio ven exactamente lo que se grabó. Solo cambia el grupo
del tópico (por defecto `rep`), para que no se mezcle con el simulador ni con el Gateway.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

from . import gateway
from .configuracion import RAIZ_DEL_REPO, ZONA_HORARIA, cargar_fuente
from .simulador import ESCENARIOS, Reloj, Simulador

log = logging.getLogger(__name__)

FORMATO = "campustwin-grabacion"
VERSION = 1
GRUPO_DE_REPRODUCCION = "rep"
CARPETA_DE_GRABACIONES = RAIZ_DEL_REPO / "grabaciones"
PASO_DE_SIMULACION_S = 1.0  # el nodo de audio publica cada 1 s: un paso mayor juntaría mensajes
ESPERA_DEL_GRABADOR_S = 0.2
INDICE_DEL_GRUPO = 2  # utec/gemelo/<grupo>/...


@dataclass
class Cabecera:
    origen: str  # "simulado" o "real": lo que eran los datos cuando se grabaron
    grupo_original: str
    inicio: str  # hora del aula en la que empieza la grabación (ISO 8601)
    descripcion: str
    formato: str = FORMATO
    version: int = VERSION

    @property
    def momento_inicial(self) -> datetime:
        return datetime.fromisoformat(self.inicio)


@dataclass(frozen=True)
class Mensaje:
    t: float
    topico: str
    carga: str
    retenido: bool = False


class GrabacionInvalida(ValueError):
    pass


# -- archivo ----------------------------------------------------------------------------------------

def escribir(ruta: Path, cabecera: Cabecera, mensajes: list[Mensaje]) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8") as archivo:
        archivo.write(json.dumps(asdict(cabecera), ensure_ascii=False) + "\n")
        for mensaje in mensajes:
            archivo.write(json.dumps(asdict(mensaje), ensure_ascii=False) + "\n")
    return ruta


def leer(ruta: Path) -> tuple[Cabecera, list[Mensaje]]:
    with ruta.open(encoding="utf-8") as archivo:
        lineas = [linea for linea in archivo if linea.strip()]
    if not lineas:
        raise GrabacionInvalida(f"{ruta} está vacío")
    try:
        datos = json.loads(lineas[0])
        if datos.get("formato") != FORMATO:
            raise GrabacionInvalida(f"{ruta} no es una grabación de Campus Twin")
        if datos.get("version") != VERSION:
            raise GrabacionInvalida(f"{ruta} es de la versión {datos.get('version')}; se espera {VERSION}")
        cabecera = Cabecera(**datos)
        mensajes = [Mensaje(**json.loads(linea)) for linea in lineas[1:]]
    except (json.JSONDecodeError, TypeError) as error:
        raise GrabacionInvalida(f"{ruta} está dañado: {error}") from error
    return cabecera, sorted(mensajes, key=lambda m: m.t)


def cambiar_grupo(topico: str, grupo: str) -> str:
    partes = topico.split("/")
    partes[INDICE_DEL_GRUPO] = grupo
    return "/".join(partes)


# -- grabar -----------------------------------------------------------------------------------------

def leer_guion(texto: str) -> list[tuple[float, str]]:
    """'0:clase,10:gas' → [(0, 'clase'), (10, 'gas')], en minutos desde el inicio."""
    guion = []
    for parte in filter(None, (p.strip() for p in texto.split(","))):
        minuto, _, escenario = parte.partition(":")
        if escenario not in ESCENARIOS:
            raise ValueError(f"Escenario desconocido en el guion: {escenario!r}")
        guion.append((float(minuto), escenario))
    return sorted(guion)


def grabar_simulacion(guion: list[tuple[float, str]], minutos: float, inicio: datetime,
                      semilla: int) -> tuple[Cabecera, list[Mensaje]]:
    """Corre el simulador sin broker, a toda velocidad, y guarda lo que habría publicado."""
    simulador = Simulador(Reloj(inicio, velocidad=1.0), semilla=semilla)
    pendientes = list(guion)
    mensajes: list[Mensaje] = []
    transcurrido = 0.0
    while transcurrido < minutos * 60:
        while pendientes and pendientes[0][0] * 60 <= transcurrido:
            simulador.aplicar_escenario(pendientes.pop(0)[1])
        for topico, carga, retenido in simulador.avanzar(PASO_DE_SIMULACION_S):
            mensajes.append(Mensaje(round(transcurrido + PASO_DE_SIMULACION_S, 3), topico, carga, retenido))
        transcurrido += PASO_DE_SIMULACION_S
    descripcion = "Simulación con guion " + ", ".join(f"min {m:g}: {e}" for m, e in guion) + f" · semilla {semilla}"
    return Cabecera("simulado", simulador.grupo, inicio.isoformat(timespec="seconds"), descripcion), mensajes


def _momento_del_mensaje(carga: bytes) -> datetime | None:
    try:
        ts = json.loads(carga).get("ts")
    except (json.JSONDecodeError, AttributeError):
        return None
    return datetime.fromtimestamp(ts / 1000, ZONA_HORARIA) if isinstance(ts, (int, float)) else None


def grabar_del_broker(transporte, grupo: str, segundos: float) -> tuple[Cabecera, list[Mensaje]]:
    """Escucha el grupo del Gateway (o del simulador) y guarda todo lo que llega.

    El instante de cada mensaje sale de su `ts` (la hora del Gateway); los que no traen hora,
    como el estado retenido del Gateway, se ubican por la hora de llegada.
    """
    transporte.suscribir(f"{gateway.PREFIJO}/{grupo}/#")
    llegada_inicial = time.monotonic()
    crudos: list[tuple[float, datetime | None, str, bytes]] = []
    while time.monotonic() - llegada_inicial < segundos:
        for topico, carga in transporte.recibir_pendientes():
            if "/campustwin/" not in topico:
                crudos.append((time.monotonic() - llegada_inicial, _momento_del_mensaje(carga), topico, carga))
        time.sleep(ESPERA_DEL_GRABADOR_S)
    transporte.cerrar()
    if not crudos:
        raise GrabacionInvalida(f"No llegó ningún mensaje del grupo «{grupo}» en {segundos:g} s")
    con_hora = [(llegada, momento) for llegada, momento, _, _ in crudos if momento]
    # Hora del aula del primer mensaje: se deduce del primero que trae `ts`.
    inicio = (con_hora[0][1] - timedelta(seconds=con_hora[0][0])) if con_hora else datetime.now(ZONA_HORARIA)
    mensajes = [Mensaje(round(max(0.0, ((momento - inicio).total_seconds() if momento else llegada)), 3),
                        topico, carga.decode(errors="replace"), topico == gateway.topico_estado_gateway(grupo))
                for llegada, momento, topico, carga in crudos]
    origen = "simulado" if grupo == "sim" else "real"
    descripcion = f"Grabado del broker, grupo «{grupo}», {len(mensajes)} mensajes en {segundos:g} s"
    return Cabecera(origen, grupo, inicio.isoformat(timespec="seconds"), descripcion), mensajes


# -- reproducir -------------------------------------------------------------------------------------

class Reproductor:
    """Ocupa el lugar del simulador dentro del servicio: misma interfaz (reloj, grupo, avanzar)."""

    escenario = None
    escenarios: dict[str, str] = {}

    def __init__(self, ruta: Path, velocidad: float = 1.0, grupo: str = GRUPO_DE_REPRODUCCION) -> None:
        self.cabecera, self._mensajes = leer(ruta)
        self.ruta, self.grupo = ruta, grupo
        self.origen = f"reproducido ({self.cabecera.origen})"
        self.reloj = Reloj(self.cabecera.momento_inicial, velocidad=velocidad)
        self._siguiente = 0
        self.terminado = not self._mensajes

    @property
    def duracion_s(self) -> float:
        return self._mensajes[-1].t if self._mensajes else 0.0

    @property
    def avance(self) -> float:
        return self._siguiente / len(self._mensajes) if self._mensajes else 1.0

    def avanzar(self, segundos_reales: float) -> list[tuple[str, str, bool]]:
        if self.terminado:
            return []
        self.reloj.avanzar(segundos_reales)
        transcurrido = (self.reloj.momento - self.cabecera.momento_inicial).total_seconds()
        salida = []
        while self._siguiente < len(self._mensajes) and self._mensajes[self._siguiente].t <= transcurrido:
            mensaje = self._mensajes[self._siguiente]
            salida.append((cambiar_grupo(mensaje.topico, self.grupo), mensaje.carga, mensaje.retenido))
            self._siguiente += 1
        if self._siguiente == len(self._mensajes):
            # El reloj se detiene al final: si siguiera, los nodos parecerían caídos.
            self.terminado = self.reloj.pausado = True
            log.info("Terminó la reproducción de %s", self.ruta.name)
        return salida

    def aplicar_escenario(self, nombre: str) -> None:
        raise ValueError("Durante una reproducción no se pueden aplicar escenarios")


# -- línea de comandos ------------------------------------------------------------------------------

def _resumen(ruta: Path) -> str:
    cabecera, mensajes = leer(ruta)
    por_tipo: dict[str, int] = {}
    for mensaje in mensajes:
        tipo = mensaje.topico.rsplit("/", 1)[-1]
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
    duracion = mensajes[-1].t if mensajes else 0
    detalle = ", ".join(f"{t}: {n}" for t, n in sorted(por_tipo.items()))
    return (f"{ruta}\n  origen: {cabecera.origen} · grupo original: {cabecera.grupo_original}\n"
            f"  inicio: {cabecera.inicio} · duración: {duracion / 60:.1f} min · {len(mensajes)} mensajes\n"
            f"  {cabecera.descripcion}\n  por tipo: {detalle}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Grabación de mensajes del Gateway (RF-11)")
    ordenes = parser.add_subparsers(dest="orden", required=True)
    simular = ordenes.add_parser("simular", help="Genera una grabación con el simulador, sin broker")
    simular.add_argument("--guion", default="0:clase", help="minuto:escenario separados por comas")
    simular.add_argument("--minutos", type=float, default=20)
    simular.add_argument("--inicio", default="2026-11-09T09:00:00-05:00", help="Hora del aula al empezar")
    simular.add_argument("--semilla", type=int, default=419)
    simular.add_argument("--salida", type=Path, required=True)
    grabar = ordenes.add_parser("grabar", help="Graba lo que publica un grupo en el broker")
    grabar.add_argument("--grupo", default=None, help="Por defecto el de config/nodos.yaml")
    grabar.add_argument("--minutos", type=float, default=10)
    grabar.add_argument("--salida", type=Path, required=True)
    info = ordenes.add_parser("info", help="Resume una grabación")
    info.add_argument("archivo", type=Path)
    argumentos = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    if argumentos.orden == "info":
        print(_resumen(argumentos.archivo))
        return
    if argumentos.orden == "simular":
        inicio = datetime.fromisoformat(argumentos.inicio).astimezone(ZONA_HORARIA)
        cabecera, mensajes = grabar_simulacion(leer_guion(argumentos.guion), argumentos.minutos, inicio,
                                               argumentos.semilla)
    else:
        from .transporte import ClienteMqtt

        fuente = cargar_fuente()
        grupo = argumentos.grupo or fuente.grupo
        transporte = ClienteMqtt(fuente.mqtt_host, fuente.mqtt_puerto, "campustwin-grabador")
        cabecera, mensajes = grabar_del_broker(transporte, grupo, argumentos.minutos * 60)
    print(_resumen(escribir(argumentos.salida, cabecera, mensajes)))


if __name__ == "__main__":
    main()
