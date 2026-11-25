"""Carga de la configuración del proyecto (carpeta config/ en la raíz del repo).

Los datos del aula traen la marca `supuesto` para que el dashboard y el reporte puedan decir qué
valores todavía no se midieron. Nada de este módulo tiene umbrales propios: todo viene de YAML.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import time
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

RAIZ_DEL_REPO = Path(__file__).resolve().parents[3]
CARPETA_DE_CONFIGURACION = Path(os.environ.get("CAMPUSTWIN_CONFIG", RAIZ_DEL_REPO / "config"))
CARPETA_DE_GRAFOS = Path(os.environ.get("CAMPUSTWIN_GRAFOS", RAIZ_DEL_REPO / "grafos"))

ZONA_HORARIA = ZoneInfo("America/Lima")
DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


class ConfiguracionInvalida(ValueError):
    """El YAML no tiene la forma esperada; el mensaje dice qué clave revisar."""


def leer_yaml(ruta: Path) -> dict:
    try:
        with ruta.open(encoding="utf-8") as archivo:
            contenido = yaml.safe_load(archivo)
    except FileNotFoundError as error:
        raise ConfiguracionInvalida(f"No existe el archivo de configuración {ruta}") from error
    if not isinstance(contenido, dict):
        raise ConfiguracionInvalida(f"{ruta} debe ser un diccionario YAML")
    return contenido


@dataclass(frozen=True)
class Dato:
    """Un valor del aula con su procedencia."""

    clave: str
    valor: Any
    supuesto: bool
    fuente: str = ""


def _es_dato(nodo: Any) -> bool:
    return isinstance(nodo, dict) and "valor" in nodo


def _recorrer_datos(nodo: Any, prefijo: str = "") -> list[Dato]:
    if _es_dato(nodo):
        return [Dato(prefijo, nodo["valor"], bool(nodo.get("supuesto", False)), nodo.get("fuente", ""))]
    if isinstance(nodo, dict):
        datos: list[Dato] = []
        for clave, valor in nodo.items():
            datos += _recorrer_datos(valor, f"{prefijo}.{clave}" if prefijo else str(clave))
        return datos
    return []


def _hora(texto: str) -> time:
    horas, minutos = texto.split(":")
    return time(int(horas), int(minutos))


def _a_horas(momento: time) -> float:
    return momento.hour + momento.minute / 60


@dataclass
class Aula:
    """Datos del aula leídos de config/aula_l419.yaml."""

    crudo: dict
    datos: dict[str, Dato] = field(default_factory=dict)

    def __post_init__(self) -> None:
        seccion_sin_plano = {k: v for k, v in self.crudo.items() if k != "plano"}
        self.datos = {dato.clave: dato for dato in _recorrer_datos(seccion_sin_plano)}

    def valor(self, clave: str) -> Any:
        try:
            return self.datos[clave].valor
        except KeyError as error:
            raise ConfiguracionInvalida(f"Falta '{clave}' en config/aula_l419.yaml") from error

    # -- atajos con nombre de dominio -----------------------------------------
    @property
    def nombre(self) -> str:
        return self.crudo["aula"]["nombre"]

    @property
    def aforo(self) -> int:
        return int(self.valor("aula.aforo"))

    @property
    def volumen_m3(self) -> float:
        return self.valor("aula.largo_m") * self.valor("aula.ancho_m") * self.valor("aula.alto_m")

    def potencia_w(self, equipo: str) -> float:
        return float(self.valor(f"inventario.{equipo}.potencia_w"))

    def cantidad(self, equipo: str) -> int:
        return int(self.valor(f"inventario.{equipo}.cantidad"))

    def espera_w(self, equipo: str) -> float:
        return float(self.valor(f"inventario.{equipo}.espera_w"))

    @property
    def potencia_luces_w(self) -> float:
        return self.cantidad("luminarias") * self.potencia_w("luminarias")

    @property
    def bloques_de_clase(self) -> list[tuple[float, float]]:
        return [(_a_horas(_hora(a)), _a_horas(_hora(b))) for a, b in self.valor("horario.bloques_de_clase")]

    @property
    def horario_oficial(self) -> tuple[float, float]:
        return _a_horas(_hora(self.valor("horario.apertura"))), _a_horas(_hora(self.valor("horario.cierre")))

    @property
    def ronda_del_vigilante(self) -> float:
        return _a_horas(_hora(self.valor("horario.ronda_del_vigilante")))

    def es_dia_de_clase(self, dia_de_la_semana: int) -> bool:
        return DIAS[dia_de_la_semana] in self.valor("horario.dias_de_clase")

    def dentro_de_horario(self, dia_de_la_semana: int, hora: float) -> bool:
        apertura, cierre = self.horario_oficial
        return self.es_dia_de_clase(dia_de_la_semana) and apertura <= hora < cierre

    @property
    def plano(self) -> dict:
        return self.crudo.get("plano", {})

    def supuestos(self) -> list[Dato]:
        return [dato for dato in self.datos.values() if dato.supuesto]

    def resumen_de_supuestos(self) -> dict:
        pendientes = self.supuestos()
        return {
            "total": len(self.datos),
            "supuestos": len(pendientes),
            "plano_supuesto": bool(self.plano.get("supuesto", True)),
            "pendientes": [
                {"clave": d.clave, "valor": d.valor, "fuente": d.fuente} for d in pendientes
            ],
        }


@dataclass(frozen=True)
class Nodo:
    id: int
    tipo: str
    sensor: str
    periodo_s: float
    programa: str


@dataclass
class Fuente:
    grupo: str
    mqtt_host: str
    mqtt_puerto: int
    influx_url: str
    influx_org: str
    influx_bucket: str
    influx_token: str | None


@dataclass(frozen=True)
class GatewayAP:
    """El Gateway con red propia (gateway_ap.ino), que sirve sus datos por HTTP."""

    url: str
    grupo: str
    periodo_s: float
    espera_s: float
    max_por_pedido: int
    fallos_para_desconectado: int


@lru_cache(maxsize=1)
def cargar_aula() -> Aula:
    return Aula(leer_yaml(CARPETA_DE_CONFIGURACION / "aula_l419.yaml"))


@lru_cache(maxsize=1)
def cargar_requisitos() -> dict[str, dict]:
    return leer_yaml(CARPETA_DE_CONFIGURACION / "requisitos_ra.yaml")


@lru_cache(maxsize=1)
def _nodos_crudo() -> dict:
    return leer_yaml(CARPETA_DE_CONFIGURACION / "nodos.yaml")


def cargar_nodos() -> dict[int, Nodo]:
    return {
        int(ident): Nodo(int(ident), d["tipo"], d["sensor"], float(d["periodo_s"]), d["programa"])
        for ident, d in _nodos_crudo()["nodos"].items()
    }


def cargar_fuente() -> Fuente:
    """Origen de los datos; las variables de entorno mandan sobre el YAML."""
    base = _nodos_crudo()["fuente"]
    entorno = os.environ.get
    return Fuente(
        grupo=entorno("CAMPUSTWIN_GRUPO", base["grupo"]),
        mqtt_host=entorno("CAMPUSTWIN_MQTT_HOST", base["mqtt_host"]),
        mqtt_puerto=int(entorno("CAMPUSTWIN_MQTT_PUERTO", base["mqtt_puerto"])),
        influx_url=entorno("CAMPUSTWIN_INFLUX_URL", base["influx_url"]),
        influx_org=entorno("CAMPUSTWIN_INFLUX_ORG", base["influx_org"]),
        influx_bucket=entorno("CAMPUSTWIN_INFLUX_BUCKET", base["influx_bucket"]),
        influx_token=entorno("INFLUX_TOKEN"),
    )


def cargar_gateway_ap() -> GatewayAP:
    try:
        base = _nodos_crudo()["gateway_ap"]
        return GatewayAP(
            url=str(os.environ.get("CAMPUSTWIN_GATEWAY_URL") or base["url"]).rstrip("/"),
            grupo=str(base["grupo"]),
            periodo_s=float(base["periodo_s"]),
            espera_s=float(base["espera_s"]),
            max_por_pedido=int(base["max_por_pedido"]),
            fallos_para_desconectado=int(base["fallos_para_desconectado"]),
        )
    except KeyError as error:
        raise ConfiguracionInvalida(f"Falta la clave {error} en gateway_ap de config/nodos.yaml") from error
