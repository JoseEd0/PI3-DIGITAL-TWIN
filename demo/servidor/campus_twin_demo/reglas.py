"""Motor de reglas (RF-08) y auditoria de consumo fantasma (RF-10).

Las reglas son las mismas que declara el documento maestro: consumo con el
laboratorio vacio, CO2 alto, puerta fuera de horario, nodo sin reportar y
bateria baja. Cada alerta guarda el requisito que la origina, para que el
tablero pueda mostrar de donde sale y la demo sea trazable al modelo SysML.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import configuracion as cfg

INFORMATIVA = "informativa"
ATENCION = "atencion"
CRITICA = "critica"


@dataclass(frozen=True)
class Alerta:
    codigo: str
    titulo: str
    detalle: str
    severidad: str
    requisito: str
    momento: datetime
    nodo: str = ""

    def como_diccionario(self) -> dict:
        return {
            "codigo": self.codigo,
            "titulo": self.titulo,
            "detalle": self.detalle,
            "severidad": self.severidad,
            "requisito": self.requisito,
            "nodo": self.nodo,
            "ts": self.momento.isoformat(timespec="seconds"),
        }


class MotorDeReglas:
    """Evalua las reglas en cada tick y respeta el silencio entre repeticiones."""

    def __init__(self) -> None:
        self._ultima_vez: dict[str, datetime] = {}
        self.activas: dict[str, Alerta] = {}
        self.historial: list[Alerta] = []

    def _puede_repetir(self, codigo: str, ahora: datetime) -> bool:
        anterior = self._ultima_vez.get(codigo)
        if anterior is None:
            return True
        return ahora - anterior >= timedelta(minutes=cfg.SILENCIO_DE_ALERTA_MIN)

    def evaluar(self, estado, reloj, salud: list[dict]) -> list[Alerta]:
        ahora = reloj.momento
        candidatas: list[Alerta] = []

        if (
            not estado.presencia
            and estado.minutos_vacio >= cfg.MINUTOS_VACIO_PARA_FANTASMA
            and estado.potencia > cfg.UMBRAL_DE_CONSUMO_CON_AULA_VACIA_W
        ):
            candidatas.append(
                Alerta(
                    codigo="consumo-con-aula-vacia",
                    titulo="Consumo con el laboratorio vacio",
                    detalle=f"{estado.potencia:.0f} W sin nadie adentro desde hace {estado.minutos_vacio:.0f} min",
                    severidad=ATENCION,
                    requisito="RF-10",
                    momento=ahora,
                    nodo=cfg.NODO_ENERGIA,
                )
            )

        if estado.co2 > cfg.UMBRAL_DE_CO2_PPM:
            candidatas.append(
                Alerta(
                    codigo="co2-alto",
                    titulo="CO2 sobre el umbral",
                    detalle=f"{estado.co2:.0f} ppm con {estado.personas} personas; conviene ventilar",
                    severidad=ATENCION if estado.co2 < cfg.UMBRAL_DE_CO2_PPM * 1.4 else CRITICA,
                    requisito="RF-02",
                    momento=ahora,
                    nodo=cfg.NODO_AMBIENTAL,
                )
            )

        if estado.puerta_abierta and not reloj.dentro_del_horario_oficial:
            candidatas.append(
                Alerta(
                    codigo="puerta-fuera-de-horario",
                    titulo="Puerta abierta fuera de horario",
                    detalle=f"Apertura a las {ahora.strftime('%H:%M')}, fuera del horario oficial",
                    severidad=CRITICA,
                    requisito="RF-04",
                    momento=ahora,
                    nodo=cfg.NODO_PUERTA,
                )
            )

        if estado.bateria <= cfg.UMBRAL_DE_BATERIA_BAJA:
            candidatas.append(
                Alerta(
                    codigo="bateria-baja",
                    titulo="Bateria baja en el nodo de puerta",
                    detalle=f"{estado.bateria:.0f} % restante; toca recargar",
                    severidad=ATENCION,
                    requisito="RNF-04",
                    momento=ahora,
                    nodo=cfg.NODO_PUERTA,
                )
            )

        for nodo in salud:
            if nodo["caido"] and nodo["ultimaMuestra"] is not None:
                candidatas.append(
                    Alerta(
                        codigo=f"nodo-caido:{nodo['nodo']}",
                        titulo=f"{nodo['etiqueta']} sin reportar",
                        detalle=f"Sin datos hace {nodo['minutosSinReportar']:.0f} min",
                        severidad=CRITICA,
                        requisito="RF-13",
                        momento=ahora,
                        nodo=nodo["nodo"],
                    )
                )

        vigentes = {alerta.codigo: alerta for alerta in candidatas}
        nuevas = []
        for codigo, alerta in vigentes.items():
            if codigo not in self.activas and self._puede_repetir(codigo, ahora):
                self._ultima_vez[codigo] = ahora
                nuevas.append(alerta)
                self.historial.insert(0, alerta)
        del self.historial[40:]
        self.activas = vigentes
        return nuevas

    def activas_como_lista(self) -> list[dict]:
        orden = {CRITICA: 0, ATENCION: 1, INFORMATIVA: 2}
        return [
            alerta.como_diccionario()
            for alerta in sorted(self.activas.values(), key=lambda a: orden.get(a.severidad, 9))
        ]

    def historial_como_lista(self, limite: int = 12) -> list[dict]:
        return [alerta.como_diccionario() for alerta in self.historial[:limite]]


@dataclass
class AuditorDeConsumoFantasma:
    """Acumula la energia gastada con el laboratorio desocupado (RF-10)."""

    kwh_totales: float = 0.0
    kwh_fantasma: float = 0.0
    kwh_fantasma_en_horario: float = 0.0
    kwh_fantasma_fuera_de_horario: float = 0.0
    por_carga: dict[str, float] = field(default_factory=lambda: {"iluminacion": 0.0, "computo": 0.0, "otros": 0.0})
    minutos_fantasma: float = 0.0

    def acumular(self, estado, reloj, minutos: float) -> None:
        if minutos <= 0:
            return
        kwh = estado.potencia * (minutos / 60.0) / 1000.0
        self.kwh_totales += kwh
        desocupado = not estado.presencia and estado.minutos_vacio >= cfg.MINUTOS_VACIO_PARA_FANTASMA
        if not desocupado:
            return
        self.kwh_fantasma += kwh
        self.minutos_fantasma += minutos
        if reloj.dentro_del_horario_oficial:
            self.kwh_fantasma_en_horario += kwh
        else:
            self.kwh_fantasma_fuera_de_horario += kwh

        iluminacion = cfg.LUMINARIAS * cfg.POTENCIA_POR_LUMINARIA_W if estado.luces_encendidas else 0.0
        computo = estado.pcs_encendidos * cfg.POTENCIA_POR_PC_W
        otros = max(0.0, estado.potencia - iluminacion - computo)
        for nombre, potencia in (("iluminacion", iluminacion), ("computo", computo), ("otros", otros)):
            self.por_carga[nombre] += potencia * (minutos / 60.0) / 1000.0

    @property
    def porcentaje_evitable(self) -> float:
        if self.kwh_totales <= 0:
            return 0.0
        return round(self.kwh_fantasma / self.kwh_totales * 100, 1)

    def como_diccionario(self) -> dict:
        return {
            "kwhTotales": round(self.kwh_totales, 3),
            "kwhFantasma": round(self.kwh_fantasma, 3),
            "kwhEnHorario": round(self.kwh_fantasma_en_horario, 3),
            "kwhFueraDeHorario": round(self.kwh_fantasma_fuera_de_horario, 3),
            "porcentajeEvitable": self.porcentaje_evitable,
            "soles": round(self.kwh_fantasma * cfg.TARIFA_SOLES_POR_KWH, 2),
            "kgCO2": round(self.kwh_fantasma * cfg.FACTOR_DE_EMISION_KG_POR_KWH, 2),
            "minutosFantasma": round(self.minutos_fantasma),
            "porCarga": {nombre: round(valor, 3) for nombre, valor in self.por_carga.items()},
            "tarifa": cfg.TARIFA_SOLES_POR_KWH,
            "factorDeEmision": cfg.FACTOR_DE_EMISION_KG_POR_KWH,
        }
