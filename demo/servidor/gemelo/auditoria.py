"""CP-06: auditoría del consumo fantasma estimado, contra la verdad del simulador.

El sistema no mide potencia (no hay PZEM): estima el consumo fantasma con el proxy de
`fantasma.py`. El simulador sí conoce la potencia que "de verdad" consume el aula simulada, así
que se puede comparar uno con otro en escenarios controlados:

    python -m gemelo.auditoria            # escribe docs/pruebas/CP-06-consumo-fantasma.md

Lo que esto valida es la **lógica** del método (detección, tolerancia, integración, falsos
positivos) con datos simulados. La exactitud real depende de las potencias del inventario, que
son supuestos hasta que se revisen en el aula (config/aula_l419.yaml).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .bitacora import Bitacora
from .configuracion import RAIZ_DEL_REPO, ZONA_HORARIA
from .servicio import Servicio
from .simulador import Reloj, Simulador
from .transporte import BusEnMemoria

PASO_S = 5.0
SALIDA = RAIZ_DEL_REPO / "docs" / "pruebas" / "CP-06-consumo-fantasma.md"
ERROR_ACEPTABLE = 0.15  # ±15 % frente a la verdad simulada: criterio propio para CP-06


@dataclass
class Caso:
    nombre: str
    descripcion: str
    inicio: datetime
    horas: float
    escenario: str | None


@dataclass
class Resultado:
    caso: Caso
    verdad_kwh: float
    verdad_tras_tolerancia_kwh: float
    estimado_kwh: float
    episodios: int
    minutos_estimados: float
    soles: float

    @property
    def error(self) -> float | None:
        if self.verdad_tras_tolerancia_kwh == 0:
            return None
        return (self.estimado_kwh - self.verdad_tras_tolerancia_kwh) / self.verdad_tras_tolerancia_kwh

    @property
    def aprobado(self) -> bool:
        if self.verdad_tras_tolerancia_kwh == 0:
            return self.estimado_kwh == 0  # sin fantasma real, cualquier estimación es un falso positivo
        return abs(self.error or 0.0) <= ERROR_ACEPTABLE


def _lima(dia: int, hora: int, minuto: int = 0) -> datetime:
    return datetime(2026, 11, dia, hora, minuto, tzinfo=ZONA_HORARIA)


CASOS = [
    Caso("A", "Todos salen a las 10:30 y dejan luces y la mitad de los PC encendidos (2 h)",
         _lima(9, 10, 30), 2.0, "vacio-con-luces"),
    Caso("B", "Día normal de 07:00 a 22:00: al terminar la última clase el simulador decide al azar "
              "si alguien olvida las luces", _lima(10, 7), 15.0, None),
    Caso("C", "Noche de 21:30 a 03:30 con el aula apagada: no debe haber falsos positivos",
         _lima(11, 21, 30), 6.0, None),
]


def _fantasma_real_w(simulador: Simulador) -> float:
    """Lo que consume el aula vacía por encima de lo que gastaría todo apagado (espera)."""
    estado, aula = simulador.estado, simulador.aula
    if estado.personas > 0:
        return 0.0
    potencia = aula.potencia_luces_w if estado.luces else 0.0
    potencia += estado.pcs_encendidos * (aula.potencia_w("pcs") - aula.espera_w("pcs"))
    potencia += aula.potencia_w("aire_acondicionado") if estado.aire else 0.0
    return potencia


def auditar(caso: Caso, semilla: int = 419) -> Resultado:
    simulador = Simulador(Reloj(caso.inicio, velocidad=1.0), semilla=semilla)
    servicio = Servicio(BusEnMemoria(), simulador, Bitacora(None))
    tolerancia_s = servicio.fantasma.minutos_de_tolerancia * 60
    if caso.escenario:
        servicio.aplicar_escenario(caso.escenario)
    verdad_kwh = verdad_tras_tolerancia_kwh = 0.0
    vacio_con_carga_s = 0.0
    for _ in range(int(caso.horas * 3600 / PASO_S)):
        servicio.ciclo(PASO_S)
        potencia = _fantasma_real_w(simulador)
        vacio_con_carga_s = vacio_con_carga_s + PASO_S if potencia > 0 else 0.0
        energia = potencia * PASO_S / 3600 / 1000
        verdad_kwh += energia
        if vacio_con_carga_s > tolerancia_s:
            verdad_tras_tolerancia_kwh += energia
    fantasma = servicio.fantasma.como_diccionario()
    return Resultado(caso, verdad_kwh, verdad_tras_tolerancia_kwh, fantasma["kwh"], fantasma["episodios"],
                     fantasma["minutos"], fantasma["soles"])


def informe(resultados: list[Resultado]) -> str:
    filas = []
    for r in resultados:
        error = "—" if r.error is None else f"{r.error:+.1%}"
        filas.append(f"| {r.caso.nombre} | {r.caso.descripcion} | {r.verdad_kwh:.3f} | {r.verdad_tras_tolerancia_kwh:.3f} "
                     f"| {r.estimado_kwh:.3f} | {error} | {r.episodios} | {r.minutos_estimados:.0f} | S/ {r.soles:.2f} "
                     f"| {'✅' if r.aprobado else '❌'} |")
    return "\n".join([
        "# CP-06 · Auditoría del consumo fantasma — **datos simulados**",
        "",
        "> Generado con `cd demo/servidor && .venv/bin/python -m gemelo.auditoria`. No editar a mano.",
        "> **Rótulo: simulado.** Compara la estimación por proxy del sistema (luces del BH1750 + aula vacía",
        "> del MLX90640 × potencias del inventario) con la potencia que conoce el simulador. Valida la",
        "> lógica del método; la exactitud real queda **pendiente** hasta revisar el inventario del aula y",
        "> contrastar con un medidor en S15.",
        "",
        f"Criterio propio: error de la energía estimada ≤ ±{ERROR_ACEPTABLE:.0%} frente a la verdad simulada "
        "contada desde que vence la tolerancia del RA-08, y cero falsos positivos cuando no hay fantasma.",
        "",
        "| Caso | Escenario | Verdad total (kWh) | Verdad tras tolerancia (kWh) | Estimado (kWh) | Error | "
        "Episodios | Minutos | Costo estimado | Resultado |",
        "|---|---|---|---|---|---|---|---|---|---|",
        *filas,
        "",
        "## Cómo leerlo",
        "",
        "- **Verdad total**: todo lo que el aula vacía consumió de más (luces, PC encendidos por encima de su",
        "  consumo en espera y aire acondicionado), desde el primer minuto.",
        "- **Verdad tras tolerancia**: lo mismo, pero solo desde que se cumple el umbral de alerta del RA-08",
        "  (`config/requisitos_ra.yaml`). Es lo que el sistema intenta estimar: los primeros minutos no",
        "  cuentan como olvido.",
        "- La diferencia entre estimado y verdad viene de la fracción supuesta de PC encendidos",
        "  (`energia.fraccion_de_pcs_olvidados_con_luces`) y de la demora en detectar que el aula quedó vacía.",
        "",
    ])


def main() -> None:
    resultados = [auditar(caso) for caso in CASOS]
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else SALIDA
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(informe(resultados), encoding="utf-8")
    for r in resultados:
        print(f"{r.caso.nombre}: verdad {r.verdad_tras_tolerancia_kwh:.3f} kWh, estimado {r.estimado_kwh:.3f} kWh, "
              f"{'aprobado' if r.aprobado else 'NO aprobado'}")
    print(destino)


if __name__ == "__main__":
    main()
