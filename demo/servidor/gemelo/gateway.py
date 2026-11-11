"""Formato de los mensajes del Gateway del docente (docs/CONTRATO_DATOS.md).

Reproduce `procesar()` de vendor/gemelo_iot_profesor/gateway/gateway.ino: mismo tópico, mismo
orden de campos, mismos decimales y mismas listas de anomalías. El simulador arma sus mensajes
con este módulo y el servicio los lee con él, así que un mensaje real y uno simulado son
indistinguibles salvo por el grupo del tópico.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone

PREFIJO = "utec/gemelo"
NIVELES_CO2 = ["NORMAL", "ALERTA", "CRITICO", "CALENTANDO", "SIN_DATO"]

# Nombres por bit, en el mismo orden que AN_* del Gateway.
ANOMALIAS = {
    "co2": ["FALLO_SENSOR", "CO2_PICO_RAPIDO", "CO2_ALERTA_VENTILACION", "CO2_CRITICO"],
    "audio": ["FALLO_AUDIO", "RUIDO_IMPACTO", "RUIDO_FUERTE_SOSTENIDO", "RUIDO_MECANICO_CONSTANTE"],
    "termico": ["FALLO_SENSOR", "CONTEO_CORREGIDO", "OBJETO_ESTATICO"],
    "magnetico": ["FALLO_SENSOR", "PUERTA_ABIERTA_PROLONGADA"],
    "ambiente": ["FALLO_SENSOR", "TEMP_FUERA_CONFORT", "HUMEDAD_ALTA", "CAMBIO_RAPIDO_TEMP"],
    "luz": ["FALLO_SENSOR", "ILUMINACION_BAJA"],
    "gas": ["FALLO_SENSOR", "GAS_DETECTADO"],
}

# Campos propios de cada tipo, en el orden del Gateway, con sus decimales (None = entero).
CAMPOS = {
    "co2": [("co2_ppm", None), ("delta_30s", None), ("temp_c", None), ("calentando", None)],
    "audio": [
        ("leq_db", 1), ("lmax_db", 1), ("pico_db", 1), ("base_db", 1), ("freq_dom_hz", 0),
        ("tonal", 2), ("bloques_fuertes", None), ("calibrando", None),
    ],
    "termico": [
        ("entradas", None), ("salidas", None), ("ocupacion_est", None), ("personas_en_vista", None),
        ("cruces_dudosos", None), ("t_fondo", 2), ("t_max", 2), ("calibrando", None),
    ],
    "magnetico": [("puerta_abierta", None), ("aperturas", None), ("seg_abierta", 1), ("campo_raw", None)],
    "ambiente": [("temp_c", 2), ("hum_pct", 1), ("pres_hpa", 2)],
    "luz": [("lux", 1), ("lux_min", 1), ("lux_max", 1), ("lux_mesa_est", 1), ("luces_cambio", None)],
    "gas": [("v_ao", 3), ("rs_r0", 3), ("do_alarma", None), ("calentando", None)],
}
TIPOS = list(CAMPOS)


def topico(grupo: str, nodo: int, tipo: str) -> str:
    return f"{PREFIJO}/{grupo}/nodo{nodo}/{tipo}"


def topico_estado_gateway(grupo: str) -> str:
    return f"{PREFIJO}/{grupo}/gateway/estado"


def bits_a_texto(tipo: str, bits: int) -> str:
    nombres = [nombre for i, nombre in enumerate(ANOMALIAS[tipo]) if bits & (1 << i)]
    return "|".join(nombres) if nombres else "NINGUNA"


def _formatear(valor, decimales):
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return None
    if decimales is None:
        return int(valor)
    return round(float(valor), decimales)


def mensaje(
    *,
    nodo: int,
    mac: str,
    seq: int,
    ts_ms: int | None,
    uptime_ms: int,
    perdidos: int,
    tipo: str,
    campos: dict,
    anom_bits: int,
    nivel: str | None = None,
) -> str:
    """JSON idéntico al que publica el Gateway para un paquete del tipo dado."""
    if tipo not in CAMPOS:
        raise ValueError(f"Tipo de nodo desconocido: {tipo}")
    cuerpo: dict = {
        "nodo": nodo,
        "mac": mac,
        "seq": seq,
        "ts": ts_ms,
        "uptime_ms": uptime_ms,
        "perdidos": perdidos,
        "tipo": tipo,
    }
    for nombre, decimales in CAMPOS[tipo]:
        cuerpo[nombre] = _formatear(campos.get(nombre), decimales)
    if tipo == "co2":
        cuerpo["nivel"] = nivel or NIVELES_CO2[4]
    cuerpo["anomalias"] = bits_a_texto(tipo, anom_bits)
    cuerpo["anom_bits"] = anom_bits
    return json.dumps(cuerpo, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class Lectura:
    """Un mensaje del Gateway ya interpretado."""

    grupo: str
    nodo: int
    tipo: str
    momento: datetime | None
    seq: int
    perdidos: int
    campos: dict
    anomalias: tuple[str, ...]
    anom_bits: int

    def tiene(self, anomalia: str) -> bool:
        return anomalia in self.anomalias


class MensajeInvalido(ValueError):
    pass


def leer(topico_recibido: str, carga: bytes | str) -> Lectura:
    """Interpreta un mensaje de `utec/gemelo/<grupo>/nodo<id>/<tipo>`."""
    partes = topico_recibido.split("/")
    if len(partes) != 5 or "/".join(partes[:2]) != PREFIJO or not partes[3].startswith("nodo"):
        raise MensajeInvalido(f"Tópico fuera del contrato: {topico_recibido}")
    try:
        cuerpo = json.loads(carga)
    except json.JSONDecodeError as error:
        raise MensajeInvalido(f"JSON inválido en {topico_recibido}") from error
    tipo = cuerpo.get("tipo", partes[4])
    if tipo not in CAMPOS:
        raise MensajeInvalido(f"Tipo desconocido '{tipo}' en {topico_recibido}")
    ts = cuerpo.get("ts")
    momento = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts else None
    texto = cuerpo.get("anomalias") or "NINGUNA"
    campos = {nombre: cuerpo.get(nombre) for nombre, _ in CAMPOS[tipo]}
    if tipo == "co2":
        campos["nivel"] = cuerpo.get("nivel")
    return Lectura(
        grupo=partes[2],
        nodo=int(cuerpo.get("nodo", partes[3][4:])),
        tipo=tipo,
        momento=momento,
        seq=int(cuerpo.get("seq", 0)),
        perdidos=int(cuerpo.get("perdidos", 0)),
        campos=campos,
        anomalias=tuple() if texto == "NINGUNA" else tuple(texto.split("|")),
        anom_bits=int(cuerpo.get("anom_bits", 0)),
    )
