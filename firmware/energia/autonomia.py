"""Recalcula la tabla de consumo y autonomía de las cajas a partir de config/energia_nodos.yaml.

Todos los resultados son ESTIMADOS (hojas de datos y lectura del código), sin medición real.
Uso, desde la raíz del repo (necesita PyYAML; el venv del servidor lo trae):

    demo/servidor/.venv/bin/python firmware/energia/autonomia.py

Imprime tablas en Markdown, listas para pegar en docs/06-energia-cajas.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

RUTA_CONFIG = Path(__file__).resolve().parents[2] / "config" / "energia_nodos.yaml"
HORAS_POR_DIA = 24
MW_POR_W = 1000
MS_POR_S = 1000


def valor(dato) -> float:
    """Los datos del YAML vienen como {valor, supuesto, fuente}; algunos son números sueltos."""
    return float(dato["valor"]) if isinstance(dato, dict) else float(dato)


@dataclass(frozen=True)
class Parametros:
    capacidad_mah: float
    voltaje_nominal_v: float
    util_ldo: float
    util_elevador: float
    iq_ldo_ma: float
    eficiencia_elevador: float
    iq_ams1117_ma: float
    riel_5v_v: float
    radio_ma: float
    tx_ma: float
    tx_ms: float
    placa_ma: float

    @classmethod
    def desde(cls, config: dict) -> "Parametros":
        bateria, reg, esp = config["bateria"], config["reguladores"], config["esp32"]
        return cls(
            capacidad_mah=valor(bateria["capacidad_mah"]),
            voltaje_nominal_v=valor(bateria["voltaje_nominal_v"]),
            util_ldo=valor(bateria["fraccion_util_ldo"]),
            util_elevador=valor(bateria["fraccion_util_elevador"]),
            iq_ldo_ma=valor(reg["ldo_3v3_iq_ma"]),
            eficiencia_elevador=valor(reg["elevador_5v_eficiencia"]),
            iq_ams1117_ma=valor(reg["ams1117_iq_ma"]),
            riel_5v_v=valor(reg["voltaje_riel_5v"]),
            radio_ma=valor(esp["radio_escucha_ma"]),
            tx_ma=valor(esp["tx_ma"]),
            tx_ms=valor(esp["tx_ms_por_envio"]),
            placa_ma=valor(esp["placa_ma"]),
        )

    def corriente_tx_ma(self, envios_por_s: float) -> float:
        """Promedio que agregan los envíos: pico de TX por la fracción del tiempo que dura."""
        return self.tx_ma * self.tx_ms / MS_POR_S * envios_por_s

    def horas_con_ldo(self, corriente_3v3_ma: float) -> float:
        """LDO lineal: la batería entrega la misma corriente que consume el riel de 3.3 V."""
        return self.capacidad_mah * self.util_ldo / (corriente_3v3_ma + self.iq_ldo_ma)

    def potencia_bateria_elevador_mw(self, corriente_5v_ma: float) -> float:
        return self.riel_5v_v * corriente_5v_ma / self.eficiencia_elevador

    def horas_con_elevador(self, corriente_5v_ma: float) -> float:
        energia_mwh = self.capacidad_mah * self.voltaje_nominal_v * self.util_elevador
        return energia_mwh / self.potencia_bateria_elevador_mw(corriente_5v_ma)


@dataclass(frozen=True)
class Presupuesto:
    nodo: str
    sensor: str
    riel: str
    esp32_ma: float
    sensor_ma: float
    usb_5v_ma: float
    horas_ldo: float | None
    horas_elevador: float

    @property
    def wh_por_dia_usb(self) -> float:
        return 5.0 * self.usb_5v_ma * HORAS_POR_DIA / MW_POR_W


def presupuesto_nodo(id_nodo, nodo: dict, p: Parametros) -> Presupuesto:
    sensor_ma = valor(nodo["sensor_ma"])
    esp32_ma = p.radio_ma + p.corriente_tx_ma(valor(nodo["envios_por_s"])) + p.placa_ma
    en_3v3 = nodo["riel"] == "3v3"
    corriente_3v3 = esp32_ma + (sensor_ma if en_3v3 else 0.0)
    # Por VIN/USB el riel de 3.3 V pasa por el AMS1117 del DevKit; el sensor de 5 V va directo.
    corriente_5v = corriente_3v3 + p.iq_ams1117_ma + (0.0 if en_3v3 else sensor_ma)
    return Presupuesto(
        nodo=f"{id_nodo} {nodo['tipo']}",
        sensor=nodo["sensor"],
        riel="3.3 V" if en_3v3 else "5 V",
        esp32_ma=esp32_ma,
        sensor_ma=sensor_ma,
        usb_5v_ma=corriente_5v,
        horas_ldo=p.horas_con_ldo(corriente_3v3) if en_3v3 else None,
        horas_elevador=p.horas_con_elevador(corriente_5v),
    )


def presupuesto_gateway(gateway: dict, p: Parametros) -> Presupuesto:
    esp32_ma = valor(gateway["radio_ma"]) + p.corriente_tx_ma(valor(gateway["envios_por_s"])) + p.placa_ma
    corriente_5v = esp32_ma + p.iq_ams1117_ma
    return Presupuesto("GW", "ESP32 v4 (Wi-Fi + MQTT)", "—", esp32_ma, 0.0, corriente_5v,
                       None, p.horas_con_elevador(corriente_5v))


def corriente_sueno_ma(nodo: dict, sueno: dict, p: Parametros, con_placa: bool) -> float:
    """Promedio con deep sleep: ráfaga despierto + resto dormido; la placa y el sensor no duermen."""
    periodo = valor(sueno["periodo_s"])
    despierto = valor(sueno["despierto_s"])
    activo_ma = p.radio_ma + p.tx_ma * p.tx_ms / MS_POR_S / despierto
    ciclo_ma = (despierto * activo_ma + (periodo - despierto) * valor(sueno["dormido_ma"])) / periodo
    return ciclo_ma + valor(nodo["sensor_ma"]) + (p.placa_ma if con_placa else 0.0)


def formato_horas(horas: float | None) -> str:
    if horas is None:
        return "no aplica (sensor a 5 V)"
    return f"{horas:.1f} h" if horas < 48 else f"{horas:.0f} h ({horas / HORAS_POR_DIA:.0f} días)"


def tabla_principal(presupuestos: list[Presupuesto]) -> str:
    filas = [
        "| Nodo | Sensor | Riel del sensor | ESP32 + placa (mA, 3.3 V) | Sensor (mA) | "
        "Por USB/VIN (mA a 5 V) | Energía por día en USB (Wh) | 18650 + LDO 3.3 V | 18650 + elevador 5 V |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for b in presupuestos:
        ldo = "USB" if b.nodo == "GW" else formato_horas(b.horas_ldo)
        filas.append(
            f"| {b.nodo} | {b.sensor} | {b.riel} | {b.esp32_ma:.1f} | {b.sensor_ma:g} | "
            f"{b.usb_5v_ma:.0f} | {b.wh_por_dia_usb:.1f} | {ldo} | {formato_horas(b.horas_elevador)} |"
        )
    return "\n".join(filas)


def tabla_sueno(config: dict, p: Parametros) -> str:
    sueno = config["sueno_profundo"]
    filas = [
        f"| Nodo | Promedio con DevKit tal cual (mA) | Autonomía | "
        f"Promedio sin LED ni USB-serie (mA) | Autonomía |",
        "|---|---:|---:|---:|---:|",
    ]
    for id_nodo, nodo in config["nodos"].items():
        if not nodo.get("admite_sueno"):
            continue
        con = corriente_sueno_ma(nodo, sueno, p, con_placa=True)
        sin = corriente_sueno_ma(nodo, sueno, p, con_placa=False)
        filas.append(f"| {id_nodo} {nodo['tipo']} | {con:.2f} | {formato_horas(p.horas_con_ldo(con))} | "
                     f"{sin:.2f} | {formato_horas(p.horas_con_ldo(sin))} |")
    return "\n".join(filas)


def main() -> None:
    config = yaml.safe_load(RUTA_CONFIG.read_text(encoding="utf-8"))
    p = Parametros.desde(config)
    presupuestos = [presupuesto_nodo(i, n, p) for i, n in config["nodos"].items()]
    presupuestos.append(presupuesto_gateway(config["gateway"], p))
    print("## Consumo y autonomía (estimado, sin medición real)\n")
    print(tabla_principal(presupuestos))
    print(f"\n## Escenario con deep sleep cada {valor(config['sueno_profundo']['periodo_s']):g} s "
          "(hipotético, no implementado)\n")
    print(tabla_sueno(config, p))


if __name__ == "__main__":
    main()
