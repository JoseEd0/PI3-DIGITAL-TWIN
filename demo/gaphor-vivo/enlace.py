"""Que magnitud del gemelo va a que propiedad del modelo SysML.

Es el contrato entre la demo y el modelo: si en `modelo/campus-twin-l419.gaphor`
cambia el nombre de un bloque o de una propiedad de valor, se cambia aqui y el
enlace en vivo sigue funcionando. Solo usa la biblioteca estandar, porque este
codigo corre dentro del interprete que trae Gaphor.
"""

from __future__ import annotations

NOMBRE_DEL_PAQUETE = "04 Demo en vivo"
NOMBRE_DEL_DIAGRAMA = "1 bdd [Demo] Estado en vivo del L-419"

BLOQUE_DEL_SISTEMA = "Campus Twin L-419"
BLOQUE_DE_ENERGIA = "Nodo de Energía"
BLOQUE_AMBIENTAL = "Nodo Ambiental"
BLOQUE_DE_OCUPACION = "Nodo de Ocupación"
BLOQUE_DE_PUERTA = "Nodo de Puerta"
BLOQUE_DE_NODO_BASE = "Nodo Sensor ESP32"
BLOQUE_DEL_SERVIDOR = "Servidor Campus Twin"
BLOQUE_DE_SALUD = "Supervisor de Salud"
BLOQUE_DE_REGLAS = "Motor de Reglas y Alertas"

# Bloques que se dibujan en el diagrama de la demo, en orden de lectura.
BLOQUES_DEL_TABLERO = [
    BLOQUE_DE_ENERGIA,
    BLOQUE_AMBIENTAL,
    BLOQUE_DE_OCUPACION,
    BLOQUE_DE_PUERTA,
    BLOQUE_DE_NODO_BASE,
    BLOQUE_DEL_SERVIDOR,
    BLOQUE_DE_SALUD,
]

def _texto_de_presencia(valor) -> str:
    return "OCUPADO" if valor else "VACÍO"


def _texto_de_puerta(valor) -> str:
    return "ABIERTA" if valor else "CERRADA"


def _decimales(cantidad: int):
    def formatear(valor) -> str:
        try:
            return f"{float(valor):.{cantidad}f}"
        except (TypeError, ValueError):
            return "—"

    return formatear


# bloque -> [(propiedad del modelo, clave del resumen del API, formateador)]
MAPA_DE_PROPIEDADES = {
    BLOQUE_DE_ENERGIA: [
        ("tension", "tension", _decimales(1)),
        ("corriente", "corriente", _decimales(2)),
        ("potencia", "potencia", _decimales(0)),
        ("factorDePotencia", "factorDePotencia", _decimales(2)),
        ("energia", "energia", _decimales(3)),
    ],
    BLOQUE_AMBIENTAL: [
        ("temperatura", "temperatura", _decimales(1)),
        ("humedad", "humedad", _decimales(0)),
        ("co2", "co2", _decimales(0)),
        ("iluminancia", "iluminancia", _decimales(0)),
    ],
    BLOQUE_DE_OCUPACION: [
        ("presencia", "presencia", _texto_de_presencia),
        ("conteo", "conteo", _decimales(0)),
    ],
    BLOQUE_DE_PUERTA: [
        ("estadoPuerta", "puertaAbierta", _texto_de_puerta),
        ("bateria", "bateria", _decimales(0)),
    ],
}

# Estas dos salen de otras secciones del estado, no del resumen.
PROPIEDAD_DE_SENAL = (BLOQUE_DE_NODO_BASE, "senal")
PROPIEDAD_DE_LATENCIA = (BLOQUE_DEL_SERVIDOR, "latenciaDeConsulta")
PROPIEDAD_DE_MUESTRAS_PERDIDAS = (BLOQUE_DE_SALUD, "muestrasPerdidas")

# Que nodo del gemelo corresponde a que bloque, para pintar alertas y caidas.
NODOS_POR_BLOQUE = {
    "energia": BLOQUE_DE_ENERGIA,
    "enchufe-proyector": BLOQUE_DE_ENERGIA,
    "enchufe-pc": BLOQUE_DE_ENERGIA,
    "ambiental": BLOQUE_AMBIENTAL,
    "ocupacion-puerta": BLOQUE_DE_OCUPACION,
    "ocupacion-fondo": BLOQUE_DE_OCUPACION,
    "puerta": BLOQUE_DE_PUERTA,
}

# El identificador del escenario es para el codigo; en pantalla se lee mejor su
# nombre en castellano.
NOMBRES_DE_ESCENARIO = {
    "normal": "guion normal del día",
    "clase": "entra un grupo",
    "vacio-con-luces": "se van y dejan luces",
    "apertura-fuera-de-horario": "apertura fuera de horario",
    "caida-de-nodo": "nodo caído",
    "senal-debil": "señal débil",
    "restablecer": "guion normal del día",
}

# Paleta del lienzo de Gaphor.
#
# Gaphor no expone su tema a la hoja de estilo del modelo: en modo oscuro pinta
# el texto de blanco por su cuenta. Si aquí se ponen fondos claros, queda letra
# blanca sobre fondo claro y no se lee nada. Por eso la vista de demostración
# fija su propio tema oscuro completo, texto incluido: se ve igual con Gaphor en
# claro o en oscuro, y la exportación a PNG sale con los mismos colores.
#
# Contraste del texto sobre cada fondo (WCAG, mínimo exigible 4.5):
#   normal 12.8 · atención 6.9 · crítico 10.5 · caído 11.5 · nota 13.6
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


def color_por_bloque(estado: dict) -> dict[str, str]:
    """Decide el color de cada bloque segun las alertas y la salud."""
    colores = {nombre: COLOR_NORMAL for nombre in BLOQUES_DEL_TABLERO}

    for fila in estado.get("salud", []):
        if fila.get("caido") and fila.get("ultimaMuestra"):
            bloque = NODOS_POR_BLOQUE.get(fila["nodo"])
            if bloque:
                colores[bloque] = COLOR_CAIDO

    for alerta in estado.get("alertas", []):
        bloque = NODOS_POR_BLOQUE.get(alerta.get("nodo", ""))
        if not bloque or colores.get(bloque) == COLOR_CAIDO:
            continue
        if alerta.get("severidad") == "critica":
            colores[bloque] = COLOR_CRITICO
        elif colores.get(bloque) != COLOR_CRITICO:
            colores[bloque] = COLOR_ATENCION

    if estado.get("alertas"):
        colores[BLOQUE_DE_SALUD] = COLOR_ATENCION
    return colores


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


def panel(estado: dict) -> str:
    """El texto de la nota que resume el estado del laboratorio."""
    reloj = estado.get("reloj", {})
    resumen = estado.get("resumen", {})
    fantasma = estado.get("fantasma", {})
    alertas = estado.get("alertas", [])

    lineas = [
        f"ESTADO EN VIVO · {reloj.get('fecha', '')} {reloj.get('hora', '')}"
        f" (x{reloj.get('velocidad', 0):g})",
        f"Horario oficial: {'dentro' if reloj.get('dentroDeHorario') else 'fuera'}"
        f" · Escenario: {NOMBRES_DE_ESCENARIO.get(estado.get('escenario'), '—')}",
        "",
        f"Energía   {resumen.get('potencia', 0):.0f} W · {resumen.get('energia', 0):.3f} kWh acumulados",
        f"Ambiente  {resumen.get('temperatura', 0):.1f} °C · {resumen.get('humedad', 0):.0f} %HR"
        f" · {resumen.get('co2', 0):.0f} ppm · {resumen.get('iluminancia', 0):.0f} lx",
        f"Ocupación {_texto_de_presencia(resumen.get('presencia'))}"
        f" · {resumen.get('conteo', 0)} personas estimadas",
        f"Puerta    {_texto_de_puerta(resumen.get('puertaAbierta'))}"
        f" · batería {resumen.get('bateria', 0):.0f} %",
        "",
        f"Consumo fantasma  {fantasma.get('kwhFantasma', 0):.3f} kWh"
        f" ({fantasma.get('porcentajeEvitable', 0):.1f} % del total)",
        f"                  S/ {fantasma.get('soles', 0):.2f} · {fantasma.get('kgCO2', 0):.2f} kg CO₂",
    ]
    if alertas:
        lineas.append("")
        lineas.append(f"ALERTAS ACTIVAS ({len(alertas)})")
        for alerta in alertas[:4]:
            lineas.append(f"  [{alerta.get('requisito', '')}] {alerta.get('titulo', '')}")
    else:
        lineas.append("")
        lineas.append("Sin alertas activas")
    return "\n".join(lineas)
