"""Que campo del gemelo va a que propiedad del modelo SysML oficial, y de que color se pinta cada bloque.

Es el contrato entre la demo y `modelo/campus-twin-l419.gaphor`: si en el modelo cambia el nombre
de un bloque o de una propiedad de valor, se cambia aqui y el enlace en vivo sigue funcionando.
Lo lee el servicio oficial en `GET /api/estado` (demo/servidor/gemelo/servicio.py, `instantanea`).

Solo usa la biblioteca estandar, porque este codigo corre dentro del interprete que trae Gaphor.
Por eso la tabla de nodos y RA esta escrita aqui y no leida de `config/`: una prueba del servicio
(`pruebas/test_gaphor_vivo.py`) la compara con `config/nodos.yaml` y `config/requisitos_ra.yaml`.
"""

from __future__ import annotations

from dataclasses import dataclass

NOMBRE_DEL_PAQUETE = "06 Demo en vivo"
NOMBRE_DEL_DIAGRAMA = "1 bdd [Demo] Estado en vivo del L-419"
NOMBRE_DEL_PROYECTO = "Campus Twin L-419"  # paquete raiz del modelo
BLOQUE_DEL_GATEWAY = "Gateway ESP32 v4"

# Condicion de un RA, tal como la entrega el servicio (demo/servidor/gemelo/requisitos.py).
NOMINAL, ALERTA, CRITICO, DESCONOCIDO = "nominal", "alerta", "critico", "desconocido"
# El bloque de un nodo caido o sin ningun dato fiable.
SIN_DATOS = "sin_datos"


@dataclass(frozen=True)
class SensorEnVivo:
    """Un nodo de la arquitectura oficial, con el bloque de su sensor y los RA que dependen de el."""

    nodo: int
    tipo: str  # tipo del paquete ESP-NOW; es la clave de `mediciones` en el estado
    bloque_del_nodo: str
    bloque_del_sensor: str
    ras: tuple[str, ...]  # sin RA-10: la salud de un nodo se ve en `salud`, no en ese RA


# Los 7 nodos de config/nodos.yaml. Los RA de cada uno salen del campo `nodos` de cada RA en
# config/requisitos_ra.yaml.
SENSORES = (
    SensorEnVivo(1, "co2", "Nodo 1 CO2", "MH-Z1911A", ("RA-03",)),
    SensorEnVivo(2, "audio", "Nodo 2 Ruido", "INMP441", ("RA-07",)),
    SensorEnVivo(3, "gas", "Nodo 3 Gas y humo", "MQ-2", ("RA-05",)),
    SensorEnVivo(4, "luz", "Nodo 4 Luz", "BH1750 (GY-302)", ("RA-04", "RA-08")),
    SensorEnVivo(5, "termico", "Nodo 5 Conteo térmico", "MLX90640 32x24",
                 ("RA-04", "RA-06", "RA-08", "RA-09")),
    SensorEnVivo(6, "magnetico", "Nodo 6 Puerta", "KY-024 (Hall SS49E)",
                 ("RA-06", "RA-08", "RA-09")),
    SensorEnVivo(7, "ambiente", "Nodo 7 Ambiente", "BME280 (GY-BME280)", ("RA-01", "RA-02")),
)

# Bloques que se dibujan en el diagrama de la demo: los 7 sensores, que muestran su lectura, y el
# Gateway, que muestra si esta en linea.
BLOQUES_DEL_TABLERO = [sensor.bloque_del_sensor for sensor in SENSORES] + [BLOQUE_DEL_GATEWAY]
# Todos los bloques que cambian de color: tambien las cajas de los nodos.
BLOQUES_QUE_SE_PINTAN = (
    [sensor.bloque_del_nodo for sensor in SENSORES]
    + [sensor.bloque_del_sensor for sensor in SENSORES] + [BLOQUE_DEL_GATEWAY]
)

# -- como se escribe cada campo ---------------------------------------------------------------
ABIERTA_CERRADA = {"puerta_abierta"}
SI_NO = {"do_alarma", "calentando", "calibrando"}
# Decimales de cada campo numerico; lo que no esta aqui se escribe tal cual si es entero y con dos
# decimales si no lo es.
DECIMALES = {
    "co2_ppm": 0, "delta_30s": 0, "temp_c": 1, "hum_pct": 1, "pres_hpa": 1,
    "leq_db": 1, "lmax_db": 1, "pico_db": 1, "base_db": 1, "freq_dom_hz": 0, "tonal": 2,
    "v_ao": 3, "rs_r0": 2,
    "lux": 0, "lux_min": 0, "lux_max": 0, "lux_mesa_est": 0,
    "t_fondo": 1, "t_max": 1, "seg_abierta": 0, "campo_raw": 0,
}
SIN_VALOR = "—"


def dar_formato(campo: str, valor) -> str:
    """Escribe un campo del JSON del Gateway como texto para el bloque."""
    if valor is None:
        return SIN_VALOR
    if campo in ABIERTA_CERRADA:
        return "ABIERTA" if valor else "CERRADA"
    if campo in SI_NO or isinstance(valor, bool):
        return "sí" if valor else "no"
    if isinstance(valor, str):
        return valor
    try:
        if campo in DECIMALES:
            return f"{float(valor):.{DECIMALES[campo]}f}"
        return str(int(valor)) if float(valor) == int(valor) else f"{float(valor):.2f}"
    except (TypeError, ValueError):
        return SIN_VALOR


def valores_de_propiedades(estado: dict) -> dict[tuple[str, str], str]:
    """{(bloque del sensor, propiedad): texto} con los campos que cada nodo reporto.

    La propiedad del modelo se llama igual que el campo del JSON del Gateway (`co2_ppm`, `leq_db`...).
    Lo que el modelo no declara se ignora al escribir.
    """
    por_tipo = {m.get("tipo"): m for m in estado.get("mediciones", [])}
    valores = {}
    for sensor in SENSORES:
        for campo, valor in (por_tipo.get(sensor.tipo) or {}).get("campos", {}).items():
            valores[(sensor.bloque_del_sensor, campo)] = dar_formato(campo, valor)
    return valores


# -- condicion de cada bloque -------------------------------------------------------------------
def condicion_del_sensor(sensor: SensorEnVivo, niveles_de_ra: dict[str, str], caido: bool) -> str:
    """El peor de sus RA; gris si el nodo no reporta o ninguno de sus RA se puede evaluar."""
    if caido:
        return SIN_DATOS
    niveles = [niveles_de_ra.get(ra, DESCONOCIDO) for ra in sensor.ras]
    for nivel in (CRITICO, ALERTA, NOMINAL):
        if nivel in niveles:
            return nivel
    return DESCONOCIDO


def condiciones_por_bloque(estado: dict) -> dict[str, str]:
    """Condicion de cada bloque pintable, para pintarlo y para mostrarla en la nota."""
    niveles = {r.get("ra"): r.get("nivel") for r in estado.get("requisitos", [])}
    caidos = {fila.get("nodo"): bool(fila.get("caido")) for fila in estado.get("salud", [])}
    condiciones = {}
    for sensor in SENSORES:
        nivel = condicion_del_sensor(sensor, niveles, caidos.get(sensor.nodo, False))
        condiciones[sensor.bloque_del_nodo] = condiciones[sensor.bloque_del_sensor] = nivel
    condiciones[BLOQUE_DEL_GATEWAY] = (
        SIN_DATOS if estado.get("gatewayEnLinea") is False else NOMINAL
    )
    return condiciones


# Paleta del lienzo de Gaphor.
#
# Gaphor no expone su tema a la hoja de estilo del modelo: en modo oscuro pinta
# el texto de blanco por su cuenta. Si aquí se ponen fondos claros, queda letra
# blanca sobre fondo claro y no se lee nada. Por eso la vista de demostración
# fija su propio tema oscuro completo, texto incluido: se ve igual con Gaphor en
# claro o en oscuro, y la exportación a PNG sale con los mismos colores.
#
# Contraste del texto sobre cada fondo (WCAG, mínimo exigible 4.5):
#   normal 12.8 · atención 6.9 · crítico 10.5 · sin datos 11.5 · nota 13.6
LIENZO = "#14181c"
TEXTO = "#e8eef2"
TEXTO_TENUE = "#93a1aa"
BORDE = "#9db0bb"
FONDO_DE_NOTA = "#1b2329"

# Los cuatro estados se distinguen por tono y por claridad, no solo por tono:
# así siguen siendo distintos para quien no separa el rojo del verde.
COLOR_NORMAL = "#1f2830"
COLOR_ATENCION = "#6b4e0f"
COLOR_CRITICO = "#56201a"
COLOR_CAIDO = "#2a2f34"


COLOR_POR_CONDICION = {
    NOMINAL: COLOR_NORMAL,
    ALERTA: COLOR_ATENCION,
    CRITICO: COLOR_CRITICO,
    DESCONOCIDO: COLOR_CAIDO,
    SIN_DATOS: COLOR_CAIDO,
}


def color_por_bloque(estado: dict) -> dict[str, str]:
    """Color de cada bloque segun la condicion de su RA. Sin estado, todos en estado normal."""
    condiciones = condiciones_por_bloque(estado) if estado else {}
    return {
        nombre: COLOR_POR_CONDICION[condiciones.get(nombre, NOMINAL)]
        for nombre in BLOQUES_QUE_SE_PINTAN
    }


def hoja_de_estilo(estado: dict) -> str:
    """Arma la hoja de estilo del modelo: tema oscuro y color por estado."""
    reglas = [
        "/* Generado por la demo en vivo. Al cerrar Gaphor no guardes esta copia. */",
        "",
        "/* Tema oscuro completo. El texto se fija aquí a propósito: si se deja el",
        "   de Gaphor, en modo claro sale negro sobre fondo oscuro. */",
        f"* {{ --opaque-background-color: {LIENZO}; }}",
        f":root {{ background-color: {LIENZO}; color: {TEXTO}; }}",
        f"diagram {{ background-color: {LIENZO}; color: {TEXTO}; }}",
        f"diagramframe {{ color: {BORDE}; }}",
        f"comment {{ background-color: {FONDO_DE_NOTA}; color: {TEXTO}; }}",
        f"valuetype, enumeration, package {{ background-color: {FONDO_DE_NOTA}; color: {BORDE}; }}",
        f"requirement {{ background-color: {FONDO_DE_NOTA}; color: {BORDE}; }}",
        f"block {{ background-color: {COLOR_NORMAL}; color: {BORDE}; }}",
        "",
        "/* Los bordes van más apagados que el texto: sobre fondo oscuro una línea",
        "   blanca de 2 px cansa la vista y compite con lo que hay que leer. */",
        f"block compartment, requirement compartment, requirement text, valuetype compartment {{ color: {TEXTO}; }}",
        "",
        "/* Un color por estado del nodo, reescrito en cada actualización. */",
    ]
    for bloque, color in color_por_bloque(estado).items():
        atenuado = f" color: {TEXTO_TENUE};" if color == COLOR_CAIDO else ""
        reglas.append(f'block[name="{bloque}"] {{ background-color: {color};{atenuado} }}')
    return "\n".join(reglas)



ROTULOS_DE_ORIGEN = {"simulado": "DATOS SIMULADOS", "real": "DATOS REALES"}
# Lineas del panel con los diez RA: siete de resumen, el titulo y una por RA.
LINEAS_DEL_PANEL = 8 + 10
ROTULOS_DE_NIVEL = {
    NOMINAL: "nominal", ALERTA: "ALERTA", CRITICO: "CRÍTICO", DESCONOCIDO: "sin dato",
}
LEYENDA_DE_COLORES = (
    "Color de cada bloque, según la condición de su RA: gris azulado, nominal · ámbar, alerta · "
    "rojo oscuro, crítico · gris tenue, nodo caído o RA sin dato."
)


def panel(estado: dict) -> str:
    """El texto de la nota que resume el estado del aula y la condicion de cada RA."""
    reloj = estado.get("reloj", {})
    fuente = estado.get("fuente", {})
    derivados = estado.get("derivados", {})
    fantasma = estado.get("fantasma", {})
    origen = fuente.get("origen", "")

    lineas = [
        f"ESTADO EN VIVO · {ROTULOS_DE_ORIGEN.get(origen, f'DATOS: {origen or chr(8212)}')}",
        f"{reloj.get('fecha', '')} {reloj.get('hora', '')} (x{reloj.get('velocidad', 0):g})"
        f" · horario oficial: {'fuera' if reloj.get('fueraDeHorario') else 'dentro'}",
        f"Escenario: {fuente.get('escenario') or SIN_VALOR}"
        f" · Gateway: {_texto_del_gateway(estado.get('gatewayEnLinea'))}",
        "",
        f"Ocupación {dar_formato('ocupacion_est', derivados.get('ocupacion'))} personas"
        f" · puerta {_texto_de_la_puerta(derivados.get('puerta_abierta'))}"
        f" · luces {_texto_de_si_no(derivados.get('luces_encendidas'))}",
        f"Consumo fantasma estimado: {fantasma.get('kwh', 0):.2f} kWh"
        f" · S/ {fantasma.get('soles', 0):.2f} · {fantasma.get('kgCo2', 0):.2f} kg CO₂",
        "",
        "CONDICIÓN DE LOS RA",
    ]
    requisitos = estado.get("requisitos", [])
    for requisito in requisitos:
        valor = requisito.get("valor")
        medida = SIN_VALOR if valor is None or isinstance(valor, bool) else (
            f"{valor} {requisito.get('unidad', '')}".strip())
        lineas.append(
            f"{requisito.get('ra', '')} {requisito.get('nombre', '')}: "
            f"{ROTULOS_DE_NIVEL.get(requisito.get('nivel'), SIN_VALOR)} · {medida}"
        )
    if not requisitos:
        lineas.append("sin datos del servicio")
    return "\n".join(lineas)


def panel_de_arranque() -> str:
    """El panel vacio, con el alto de uno lleno.

    Gaphor mide la nota al armar el diagrama. Con el texto de "sin datos" la nota queda de
    nueve lineas, y cuando llegan los diez RA crece y se monta sobre la nota de abajo.
    """
    lineas = panel({}).split("\n")
    return "\n".join(lineas + [""] * (LINEAS_DEL_PANEL - len(lineas)))


def _texto_del_gateway(en_linea) -> str:
    return SIN_VALOR if en_linea is None else ("en línea" if en_linea else "caído")


def _texto_de_la_puerta(abierta) -> str:
    return SIN_VALOR if abierta is None else dar_formato("puerta_abierta", abierta).lower()


def _texto_de_si_no(valor) -> str:
    return SIN_VALOR if valor is None else ("sí" if valor else "no")
