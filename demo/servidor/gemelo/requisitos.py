"""Evaluación de los requisitos de alto nivel RA-01..10 (config/requisitos_ra.yaml).

Cada RA tiene un evaluador que lee el estado del aula y devuelve su condición: nominal, alerta,
crítico o desconocido (sin datos para decidir). La histéresis evita que una magnitud que ronda el
umbral haga parpadear el semáforo, igual que en los nodos del docente.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .configuracion import ZONA_HORARIA
from .estado import EstadoDelAula

NOMINAL, ALERTA, CRITICO, DESCONOCIDO = "nominal", "alerta", "critico", "desconocido"
GRAVEDAD = {DESCONOCIDO: -1, NOMINAL: 0, ALERTA: 1, CRITICO: 2}


@dataclass
class Condicion:
    ra: str
    nombre: str
    nivel: str
    valor: float | int | bool | None
    unidad: str
    mensaje: str
    desde: datetime | None = None

    def como_diccionario(self) -> dict:
        return {
            "ra": self.ra, "nombre": self.nombre, "nivel": self.nivel, "valor": self.valor,
            "unidad": self.unidad, "mensaje": self.mensaje,
            "desde": self.desde.astimezone(ZONA_HORARIA).isoformat(timespec="seconds") if self.desde else None,
        }


Evaluador = Callable[[dict, EstadoDelAula, str], tuple[str, Any, str]]


def _redondear(valor):
    return round(valor, 1) if isinstance(valor, float) else valor


def _rango(req: dict, estado: EstadoDelAula, previo: str):
    valor = estado.valor(req["campo"])
    if valor is None:
        return DESCONOCIDO, None, "Sin datos del sensor"
    bajo, alto = req["nominal"]
    critico_bajo, critico_alto = req["critico"]
    h = req.get("histeresis", 0.0)
    if valor < critico_bajo or valor > critico_alto:
        return CRITICO, valor, f"{valor:.1f} fuera del rango crítico {critico_bajo}–{critico_alto}"
    if valor < bajo or valor > alto:
        return ALERTA, valor, f"{valor:.1f} fuera del rango nominal {bajo}–{alto}"
    if previo in (ALERTA, CRITICO) and not (bajo + h <= valor <= alto - h):
        return ALERTA, valor, f"{valor:.1f} todavía cerca del límite (histéresis {h})"
    return NOMINAL, valor, f"{valor:.1f} dentro de {bajo}–{alto}"


def _umbral_superior(req: dict, estado: EstadoDelAula, previo: str):
    valor = estado.valor(req["campo"])
    if valor is None:
        return DESCONOCIDO, None, "Sin datos del sensor"
    alerta, critico, h = req["alerta"], req["critico"], req.get("histeresis", 0)
    if valor >= critico:
        return CRITICO, valor, f"{valor:.0f} ≥ {critico} (crítico)"
    if valor >= alerta:
        return ALERTA, valor, f"{valor:.0f} ≥ {alerta} (alerta)"
    if previo == CRITICO and valor >= critico - h:
        return CRITICO, valor, f"{valor:.0f} todavía cerca del umbral crítico"
    if previo in (ALERTA, CRITICO) and valor >= alerta - h:
        return ALERTA, valor, f"{valor:.0f} todavía cerca del umbral de alerta"
    return NOMINAL, valor, f"{valor:.0f} < {alerta}"


def _umbral_inferior_con_ocupacion(req: dict, estado: EstadoDelAula, previo: str):
    valor = estado.valor(req["campo"])
    vacia = estado.aula_vacia()
    if vacia:
        return NOMINAL, valor, "Aula vacía: el requisito no aplica"
    if valor is None or vacia is None:
        return DESCONOCIDO, valor, "Sin datos de luz u ocupación"
    alerta, critico, h = req["alerta"], req["critico"], req.get("histeresis", 0)
    if valor < critico:
        return CRITICO, valor, f"{valor:.0f} lx < {critico} lx con el aula ocupada"
    if valor < alerta or (previo in (ALERTA, CRITICO) and valor < alerta + h):
        return ALERTA, valor, f"{valor:.0f} lx < {alerta} lx con el aula ocupada"
    return NOMINAL, valor, f"{valor:.0f} lx sobre la mesa"


def _gas(req: dict, estado: EstadoDelAula, previo: str):
    valor = estado.valor(req["campo"])
    anomalias = estado.anomalias("gas") or ()
    if estado.campo("gas", "calentando"):
        return DESCONOCIDO, None, "El MQ-2 está calentando"
    if "GAS_DETECTADO" in anomalias or estado.campo("gas", "do_alarma"):
        return CRITICO, valor, "El nodo MQ-2 reporta gas o humo"
    if valor is None:
        return DESCONOCIDO, None, "Sin datos del MQ-2"
    if valor <= req["critico"]:
        return CRITICO, valor, f"Rs/R0 = {valor:.2f} ≤ {req['critico']}"
    if valor <= req["alerta"]:
        return ALERTA, valor, f"Rs/R0 = {valor:.2f} ≤ {req['alerta']}"
    return NOMINAL, valor, f"Rs/R0 = {valor:.2f} (aire limpio ≈ 1)"


def _aforo(req: dict, estado: EstadoDelAula, previo: str):
    ocupacion = estado.ocupacion()
    if ocupacion is None:
        return DESCONOCIDO, None, "Sin datos del conteo térmico"
    aforo = estado.aula.aforo
    fraccion = ocupacion / aforo
    if fraccion > req["critico_fraccion"]:
        return CRITICO, ocupacion, f"{ocupacion} personas > aforo de {aforo}"
    if fraccion >= req["alerta_fraccion"]:
        return ALERTA, ocupacion, f"{ocupacion} de {aforo} personas ({fraccion:.0%})"
    return NOMINAL, ocupacion, f"{ocupacion} de {aforo} personas"


def _fantasma(req: dict, estado: EstadoDelAula, previo: str):
    luces, vacia = estado.luces_encendidas(), estado.aula_vacia()
    if luces is None or vacia is None:
        return DESCONOCIDO, None, "Sin datos de luz u ocupación"
    minutos = estado.minutos(estado.inicio_fantasma)
    fuera = estado.fuera_de_horario()
    if minutos >= req["critico_min"] or (fuera and minutos >= req["alerta_min"]):
        return CRITICO, round(minutos), f"Luces encendidas con el aula vacía hace {minutos:.0f} min"
    if minutos >= req["alerta_min"]:
        return ALERTA, round(minutos), f"Luces encendidas con el aula vacía hace {minutos:.0f} min"
    if minutos > 0:
        return NOMINAL, round(minutos), f"Aula vacía con luces hace {minutos:.0f} min (aún en tolerancia)"
    return NOMINAL, 0, "Sin consumo evitable detectado"


def _seguridad_fisica(req: dict, estado: EstadoDelAula, previo: str):
    abierta = estado.campo("magnetico", "puerta_abierta")
    fuera = estado.fuera_de_horario()
    if abierta is None or fuera is None:
        return DESCONOCIDO, None, "Sin datos de la puerta"
    ocupacion = estado.ocupacion() or 0
    if fuera and abierta and ocupacion > 0:
        return CRITICO, bool(abierta), f"Puerta abierta fuera de horario con {ocupacion} persona(s) dentro"
    if fuera and (abierta or ocupacion > 0):
        return ALERTA, bool(abierta), "Actividad en el aula fuera del horario oficial"
    if "PUERTA_ABIERTA_PROLONGADA" in (estado.anomalias("magnetico") or ()):
        return ALERTA, bool(abierta), "Puerta abierta más de 10 min"
    return NOMINAL, bool(abierta), "Puerta " + ("abierta" if abierta else "cerrada") + (
        " fuera de horario" if fuera else " en horario")


def _salud(req: dict, estado: EstadoDelAula, previo: str):
    caidos = estado.nodos_sin_datos()
    fallas = [f["nodo"] for f in estado.salud() if f["falla"]]
    total = len(estado.nodos)
    if estado.gateway_en_linea is False or len(caidos) / total >= req["fraccion_para_gateway"]:
        return CRITICO, len(caidos), "Gateway desconectado: no llega ningún nodo"
    if caidos or fallas:
        partes = []
        if caidos:
            partes.append("sin datos: " + ", ".join(f"nodo {n}" for n in caidos))
        if fallas:
            partes.append("falla de sensor: " + ", ".join(f"nodo {n}" for n in fallas))
        return ALERTA, len(caidos) + len(fallas), "; ".join(partes)
    if estado.ahora is None:
        return DESCONOCIDO, None, "Todavía no llega ningún dato"
    return NOMINAL, 0, f"Los {total} nodos reportando"


EVALUADORES: dict[str, Evaluador] = {
    "rango": _rango,
    "umbral_superior": _umbral_superior,
    "umbral_inferior_con_ocupacion": _umbral_inferior_con_ocupacion,
    "gas": _gas,
    "aforo": _aforo,
    "fantasma": _fantasma,
    "seguridad_fisica": _seguridad_fisica,
    "salud": _salud,
}


@dataclass
class EvaluadorDeRequisitos:
    requisitos: dict[str, dict]
    previos: dict[str, Condicion] = field(default_factory=dict)
    _sostenido_desde: dict[str, datetime] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for ident, req in self.requisitos.items():
            if req["evaluador"] not in EVALUADORES:
                raise ValueError(f"{ident}: evaluador '{req['evaluador']}' desconocido")

    def evaluar(self, estado: EstadoDelAula) -> dict[str, Condicion]:
        resultado: dict[str, Condicion] = {}
        for ident, req in self.requisitos.items():
            previo = self.previos.get(ident)
            nivel, valor, mensaje = EVALUADORES[req["evaluador"]](req, estado, previo.nivel if previo else NOMINAL)
            nivel = self._aplicar_sostenido(ident, req, nivel, estado.ahora)
            desde = previo.desde if previo and previo.nivel == nivel else estado.ahora
            resultado[ident] = Condicion(ident, req["nombre"], nivel, _redondear(valor),
                                         req.get("unidad", ""), mensaje, desde)
        self.previos = resultado
        estado.niveles_ra = {i: GRAVEDAD[c.nivel] for i, c in resultado.items()}
        return resultado

    def _aplicar_sostenido(self, ident: str, req: dict, nivel: str, ahora: datetime | None) -> str:
        """Si el RA pide un nivel sostenido (p. ej. ruido 60 s), no alerta por picos breves."""
        sostenido = req.get("sostenido_s")
        if not sostenido or ahora is None or nivel in (NOMINAL, DESCONOCIDO):
            self._sostenido_desde.pop(ident, None)
            return nivel
        inicio = self._sostenido_desde.setdefault(ident, ahora)
        if (ahora - inicio).total_seconds() >= sostenido:
            return nivel
        previo = self.previos.get(ident)
        return previo.nivel if previo and previo.nivel != DESCONOCIDO else NOMINAL
