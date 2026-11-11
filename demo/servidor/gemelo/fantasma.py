"""Estimación del consumo fantasma por proxy (RF-10, RA-08), sin PZEM.

Cuando las luces están encendidas con el aula vacía por más del umbral de alerta del RA-08, se
suma la potencia nominal del inventario (config/aula_l419.yaml): luminarias, una fracción
supuesta de PC que quedan prendidos con ellas y el aire acondicionado si el micrófono oye su
ruido mecánico. Es una **estimación**: el reporte y el dashboard lo dicen así.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .configuracion import Aula
from .estado import EstadoDelAula

MAXIMO_PASO_S = 120  # si el servicio se pausa, no se cuenta de golpe el tiempo perdido


@dataclass
class EstimadorDeConsumoFantasma:
    aula: Aula
    minutos_de_tolerancia: float
    kwh: float = 0.0
    minutos: float = 0.0
    episodios: int = 0
    potencia_actual_w: float = 0.0
    _anterior: datetime | None = None
    _en_episodio: bool = False
    por_carga_kwh: dict[str, float] = field(default_factory=lambda: {"luces": 0.0, "pcs": 0.0, "aire": 0.0})

    def _potencias(self, estado: EstadoDelAula) -> dict[str, float]:
        aula = self.aula
        fraccion_pcs = aula.valor("energia.fraccion_de_pcs_olvidados_con_luces")
        aire = "RUIDO_MECANICO_CONSTANTE" in (estado.anomalias("audio") or ())
        return {
            "luces": aula.potencia_luces_w,
            "pcs": fraccion_pcs * aula.cantidad("pcs") * aula.potencia_w("pcs"),
            "aire": aula.potencia_w("aire_acondicionado") * aula.cantidad("aire_acondicionado") if aire else 0.0,
        }

    def acumular(self, estado: EstadoDelAula) -> None:
        ahora = estado.ahora
        if ahora is None:
            return
        paso_s = 0.0 if self._anterior is None else min(MAXIMO_PASO_S, (ahora - self._anterior).total_seconds())
        self._anterior = ahora
        activo = estado.inicio_fantasma is not None and estado.minutos(estado.inicio_fantasma) >= self.minutos_de_tolerancia
        if not activo:
            self._en_episodio = False
            self.potencia_actual_w = 0.0
            return
        if not self._en_episodio:
            self._en_episodio = True
            self.episodios += 1
        potencias = self._potencias(estado)
        self.potencia_actual_w = sum(potencias.values())
        horas = max(0.0, paso_s) / 3600
        for carga, potencia in potencias.items():
            self.por_carga_kwh[carga] += potencia * horas / 1000
        self.kwh = sum(self.por_carga_kwh.values())
        self.minutos += paso_s / 60

    def como_diccionario(self) -> dict:
        tarifa = self.aula.valor("energia.tarifa_soles_kwh")
        factor = self.aula.valor("energia.factor_emision_kg_kwh")
        claves = ["inventario.luminarias.potencia_w", "inventario.pcs.potencia_w",
                  "energia.fraccion_de_pcs_olvidados_con_luces", "energia.tarifa_soles_kwh",
                  "energia.factor_emision_kg_kwh"]
        return {
            "kwh": round(self.kwh, 3),
            "soles": round(self.kwh * tarifa, 2),
            "kgCo2": round(self.kwh * factor, 2),
            "minutos": round(self.minutos, 1),
            "episodios": self.episodios,
            "potenciaActualW": round(self.potencia_actual_w, 1),
            "porCargaKwh": {k: round(v, 3) for k, v in self.por_carga_kwh.items()},
            "tarifa": tarifa,
            "factorEmision": factor,
            "metodo": "Estimación por proxy: luces (BH1750) + aula vacía (MLX90640) × potencia nominal del inventario",
            "basadoEnSupuestos": any(self.aula.datos[c].supuesto for c in claves),
        }
