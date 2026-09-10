"""Almacen en memoria de muestras, eventos y salud de los nodos.

En el laboratorio real esto es InfluxDB con retencion de 60 dias (RF-06). Para
la demo basta una ventana en memoria: lo que importa es que el resto del sistema
consulte por el mismo camino (ultimo valor, historico y salud) y que la ingesta
descarte duplicados igual que el servidor real (RF-05).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

from . import configuracion as cfg
from .contrato import Evento, Muestra


@dataclass
class SaludDeNodo:
    nodo: str
    etiqueta: str
    requisito: str
    ultima_muestra: datetime | None = None
    recibidas: int = 0
    duplicadas: int = 0
    senal: float | None = None
    # ultima secuencia vista por magnitud: la diferencia entre lo que el nodo
    # numero y lo que llego es, exactamente, lo que se perdio en el camino
    secuencias: dict[str, int] = field(default_factory=dict)

    def minutos_sin_reportar(self, ahora: datetime) -> float:
        if self.ultima_muestra is None:
            return float("inf")
        return (ahora - self.ultima_muestra).total_seconds() / 60.0

    @property
    def umbral_de_caida_min(self) -> float:
        """Minutos sin reportar a partir de los cuales el nodo se da por caido.

        El nodo de puerta duerme y solo late cada 30 min (RNF-04), asi que un
        umbral fijo de 5 min lo daria por muerto cada rato. El umbral es el
        mayor entre ese minimo y tres periodos de envio del propio nodo.
        """
        periodo_min = cfg.NODOS.get(self.nodo, (None, None, 60))[2] / 60
        return max(cfg.MINUTOS_SIN_DATOS_PARA_CAIDO, cfg.PERIODOS_TOLERADOS * periodo_min)

    def esta_caido(self, ahora: datetime) -> bool:
        return self.minutos_sin_reportar(ahora) > self.umbral_de_caida_min

    @property
    def esperadas(self) -> int:
        """Cuantas muestras numero el nodo, segun la ultima secuencia de cada magnitud."""
        return sum(self.secuencias.values())

    def muestras_perdidas(self) -> float:
        """Porcentaje de muestras que el nodo numero y nunca llegaron (RF-13).

        Se calcula con los huecos de secuencia, no con el reloj: asi la metrica
        vale igual con el dia acelerado de la demo que en tiempo real.
        """
        esperadas = self.esperadas
        if esperadas <= 0:
            return 0.0
        perdidas = 1.0 - (self.recibidas / esperadas)
        return round(max(0.0, min(100.0, perdidas * 100)), 2)

    def como_diccionario(self, ahora: datetime) -> dict:
        return {
            "nodo": self.nodo,
            "etiqueta": self.etiqueta,
            "requisito": self.requisito,
            "ultimaMuestra": self.ultima_muestra.isoformat(timespec="seconds") if self.ultima_muestra else None,
            "minutosSinReportar": round(self.minutos_sin_reportar(ahora), 2)
            if self.ultima_muestra
            else None,
            "caido": self.esta_caido(ahora),
            "umbralDeCaidaMin": round(self.umbral_de_caida_min, 1),
            "senal": round(self.senal, 1) if self.senal is not None else None,
            "muestrasPerdidas": self.muestras_perdidas(),
            "recibidas": self.recibidas,
            "esperadas": self.esperadas,
            "duplicadas": self.duplicadas,
        }


@dataclass
class Almacen:
    ultimos: dict[str, dict[str, Muestra]] = field(default_factory=dict)
    series: dict[tuple[str, str], deque] = field(default_factory=dict)
    salud: dict[str, SaludDeNodo] = field(default_factory=dict)
    eventos: deque = field(default_factory=lambda: deque(maxlen=60))
    _vistas: dict[tuple[str, str], int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for nodo, (etiqueta, requisito, _) in cfg.NODOS.items():
            self.salud[nodo] = SaludDeNodo(nodo=nodo, etiqueta=etiqueta, requisito=requisito)

    # -- ingesta -------------------------------------------------------------
    def registrar_muestra(self, muestra: Muestra) -> bool:
        """Guarda la muestra. Devuelve False si era un duplicado (RF-05)."""
        clave = (muestra.nodo, muestra.magnitud)
        ultima_vista = self._vistas.get(clave)
        salud = self.salud.setdefault(
            muestra.nodo,
            SaludDeNodo(nodo=muestra.nodo, etiqueta=muestra.nodo, requisito=""),
        )
        if ultima_vista is not None and muestra.secuencia <= ultima_vista:
            salud.duplicadas += 1
            return False
        self._vistas[clave] = muestra.secuencia

        self.ultimos.setdefault(muestra.nodo, {})[muestra.magnitud] = muestra
        serie = self.series.setdefault(clave, deque(maxlen=cfg.MUESTRAS_POR_SERIE))
        serie.append((muestra.momento, muestra.valor))

        salud.ultima_muestra = muestra.momento
        salud.secuencias[muestra.magnitud] = muestra.secuencia
        salud.recibidas += 1
        if muestra.magnitud == "senal":
            salud.senal = muestra.valor
        return True

    def registrar_evento(self, evento: Evento) -> None:
        self.eventos.appendleft(evento)

    # -- consulta ------------------------------------------------------------
    def ultimo(self, nodo: str, magnitud: str) -> float | None:
        muestra = self.ultimos.get(nodo, {}).get(magnitud)
        return muestra.valor if muestra else None

    def historico(self, nodo: str, magnitud: str, limite: int = 120) -> list[dict]:
        serie = self.series.get((nodo, magnitud), deque())
        recorte = list(serie)[-limite:]
        return [{"ts": momento.isoformat(timespec="seconds"), "valor": valor} for momento, valor in recorte]

    def lecturas_por_nodo(self) -> dict[str, dict]:
        return {
            nodo: {
                magnitud: {
                    "valor": muestra.valor,
                    "unidad": muestra.unidad,
                    "ts": muestra.momento.isoformat(timespec="seconds"),
                    "seq": muestra.secuencia,
                    "topico": muestra.topico,
                }
                for magnitud, muestra in magnitudes.items()
            }
            for nodo, magnitudes in self.ultimos.items()
        }

    def salud_como_lista(self, ahora: datetime) -> list[dict]:
        return [salud.como_diccionario(ahora) for salud in self.salud.values()]

    def eventos_recientes(self, limite: int = 12) -> list[dict]:
        return [evento.como_diccionario() for evento in list(self.eventos)[:limite]]
