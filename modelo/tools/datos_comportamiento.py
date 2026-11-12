"""Datos del paquete `04 Comportamiento`: actividades, máquinas de estados y casos de uso.

Es solo declaración, sin Gaphor: `build_model.py` la recorre y dibuja. Cada paso, estado y caso
sale de una fuente que se cita en la nota del diagrama:

- el firmware del docente (vendor/gemelo_iot_profesor/), para lo que hace cada nodo;
- el servicio del grupo (demo/servidor/gemelo/), para la evaluación, el diagnóstico y las salidas;
- docs/00-idea-principal.md (casos de uso del §7 y casos borde del §8.5) y el brief de la EC3 (§12),
  que fija los estados del salón y de los nodos y los seis casos de uso.

Posiciones: `columna` y `fila` son coordenadas de una grilla (no pixeles), con decimales para
los elementos que quedan entre dos celdas. Los pasos de un mismo carril comparten columnas.
"""

from dataclasses import dataclass

# -- tipos de paso de una actividad ----------------------------------------------------------
INICIO = "inicio"
FIN = "fin"
FIN_DE_FLUJO = "fin_de_flujo"
ACCION = "accion"
DECISION = "decision"
UNION = "union"  # la unión (merge) de dos caminos alternativos
BIFURCACION = "bifurcacion"  # barra de fork: abre ramas en paralelo
REUNION = "reunion"  # barra de join: espera todas las ramas

# -- lados de una caja, para anclar una línea ------------------------------------------------
NORTE, SUR, ESTE, OESTE = "n", "s", "e", "o"


@dataclass(frozen=True)
class Paso:
    clave: str
    tipo: str
    columna: float
    fila: float
    texto: str = ""
    ancho_en_columnas: float = 0.0  # solo las barras de bifurcación y reunión


@dataclass(frozen=True)
class Flujo:
    """Una flecha entre dos pasos. `sale`/`entra` fijan el lado; `via` son puntos intermedios."""

    origen: str
    destino: str
    etiqueta: str = ""
    sale: str | None = None
    entra: str | None = None
    via: tuple[tuple[float, float], ...] = ()


@dataclass(frozen=True)
class Carril:
    nombre: str
    columna_inicial: float
    columna_final: float


@dataclass(frozen=True)
class Actividad:
    nombre: str
    diagrama: str
    carriles: tuple[Carril, ...]
    pasos: tuple[Paso, ...]
    flujos: tuple[Flujo, ...]
    nota: str


# ==========================================================================================
# 1. Telemetría de un nodo (firmware del docente: nodo_co2.ino y espnow_nodo.h, gateway.ino)
# ==========================================================================================
TELEMETRIA = Actividad(
    nombre="Telemetría de un nodo",
    diagrama="1 act [Comportamiento] Telemetría de un nodo",
    carriles=(
        Carril("Nodo (ESP32 + sensor)", 0, 1),
        Carril("Gateway ESP32 v4", 2, 3),
        Carril("Laptop (Docker)", 4, 5),
    ),
    pasos=(
        Paso("inicio", INICIO, 0, 0),
        Paso("arranque", ACCION, 0, 1,
             "Arrancar: buscar el canal del Gateway por SSID y calentar el sensor"),
        Paso("repetir", UNION, 0, 2),
        Paso("leer", ACCION, 0, 3, "Leer el sensor (I²C, UART, I²S o analógico)"),
        Paso("valida", DECISION, 0, 4),
        Paso("fallo", ACCION, 1, 4,
             "Contar el fallo y enviar el valor nulo (FALLO_SENSOR tras 5 seguidos)"),
        Paso("seguir", UNION, 0, 5),
        Paso("armar", ACCION, 0, 6, "Armar el paquete: seq, uptime_ms, valores y bits de anomalía"),
        Paso("enviar", ACCION, 0, 7, "Enviar por ESP-NOW al Gateway"),
        Paso("perdido", DECISION, 0, 8),
        Paso("reescanear", ACCION, 1, 8, "Volver a buscar el canal del Gateway (unos 2 s)"),
        Paso("esperar", ACCION, 0, 9, "Esperar el periodo propio del nodo (5 s en el de CO₂)"),
        Paso("recibir", ACCION, 2, 7, "Recibir el paquete ESP-NOW en la cola de 32 mensajes"),
        Paso("cola", DECISION, 2, 8),
        Paso("descartar", ACCION, 3, 8, "Descartar el paquete: queda un hueco en seq"),
        Paso("descartado", FIN_DE_FLUJO, 3, 9),
        Paso("publicar", ACCION, 2, 10,
             "Contar las muestras perdidas por huecos de seq, agregar ts y grupo, y publicar "
             "el JSON en MQTT (QoS 0)"),
        Paso("mosquitto", ACCION, 4, 10, "Mosquitto recibe el mensaje en el tópico del nodo"),
        Paso("abrir", BIFURCACION, 4.5, 11, ancho_en_columnas=1.7),
        Paso("telegraf", ACCION, 4, 12, "Telegraf escribe el punto en InfluxDB (bucket gemelo)"),
        Paso("servicio", ACCION, 5, 12, "El servicio del grupo actualiza el estado del aula"),
        Paso("cerrar", REUNION, 4.5, 13, ancho_en_columnas=1.7),
        Paso("fin", FIN, 4.5, 14),
    ),
    flujos=(
        Flujo("inicio", "arranque"),
        Flujo("arranque", "repetir"),
        Flujo("repetir", "leer"),
        Flujo("leer", "valida"),
        Flujo("valida", "fallo", "[inválida]", sale=ESTE, entra=OESTE),
        Flujo("valida", "seguir", "[válida]"),
        Flujo("fallo", "seguir", sale=SUR, entra=ESTE, via=((1, 5),)),
        Flujo("seguir", "armar"),
        Flujo("armar", "enviar"),
        Flujo("enviar", "perdido"),
        Flujo("enviar", "recibir", "ESP-NOW", sale=ESTE, entra=OESTE),
        Flujo("perdido", "reescanear", "[10 fallos seguidos]", sale=ESTE, entra=OESTE),
        Flujo("perdido", "esperar", "[no]"),
        Flujo("reescanear", "esperar", sale=SUR, entra=ESTE, via=((1, 9),)),
        Flujo("esperar", "repetir", sale=OESTE, entra=OESTE, via=((-0.62, 9), (-0.62, 2))),
        Flujo("recibir", "cola"),
        Flujo("cola", "descartar", "[cola llena]", sale=ESTE, entra=OESTE),
        Flujo("descartar", "descartado"),
        Flujo("cola", "publicar", "[hay lugar]"),
        Flujo("publicar", "mosquitto", "MQTT", sale=ESTE, entra=OESTE),
        Flujo("mosquitto", "abrir", sale=SUR, entra=NORTE),
        Flujo("abrir", "telegraf"),
        Flujo("abrir", "servicio"),
        Flujo("telegraf", "cerrar"),
        Flujo("servicio", "cerrar"),
        Flujo("cerrar", "fin"),
    ),
    nota=("Fuente: firmware del docente (nodo_co2.ino, espnow_nodo.h, gateway.ino), citado y no "
          "modificado, y docs/CONTRATO_DATOS.md. Se dibuja el nodo de CO₂; los demás cambian el "
          "sensor, el periodo y el calentamiento.\n\n"
          "Si el Gateway no tiene hora (sin internet para NTP), ts sale nulo y Telegraf "
          "descarta el mensaje completo: por eso la demo de la EC3 la pone el simulador. "
          "El nodo MQ-2 (nodo 3) usa el .ino propio del grupo (firmware/MQ-2/), que compila pero no se ha probado en hardware.\n\n"
          "Estado: modelo del comportamiento; no hay ninguna medición real."),
)


# ==========================================================================================
# 2. Entrada y salida de personas (KY-024 y MLX90640)
# ==========================================================================================
PERSONAS = Actividad(
    nombre="Entrada y salida de personas",
    diagrama="2 act [Comportamiento] Entrada y salida de personas",
    carriles=(
        Carril("Nodo 6 · KY-024 (puerta)", 0, 0),
        Carril("Servicio del grupo", 1, 2),
        Carril("Nodo 5 · MLX90640 (marco de la puerta)", 3, 4),
    ),
    pasos=(
        Paso("inicio", INICIO, 1.5, 0),
        Paso("abrir", BIFURCACION, 1.5, 1, ancho_en_columnas=3.2),
        Paso("campo", ACCION, 0, 2, "Leer el campo del imán (salida analógica del KY-024)"),
        Paso("antirrebote", ACCION, 0, 3, "Aplicar histéresis y antirrebote de 150 ms"),
        Paso("puerta", ACCION, 0, 4,
             "Enviar el estado de la puerta al cambiar y cada 10 s; marcar la apertura "
             "prolongada a los 10 min"),
        Paso("matriz", ACCION, 3, 2, "Leer la matriz térmica de 32×24 píxeles"),
        Paso("cabezas", ACCION, 3, 3,
             "Restar el fondo y detectar las cabezas sobre el umbral de calor"),
        Paso("cruces", ACCION, 3, 4,
             "Seguir cada cabeza: de la línea A a la B es una entrada, de la B a la A una salida"),
        Paso("negativa", DECISION, 3, 5),
        Paso("limitar", ACCION, 4, 5, "Limitar la ocupación a 0 y marcar CONTEO_CORREGIDO"),
        Paso("seguir", UNION, 3, 6),
        Paso("conteo", ACCION, 3, 7,
             "Enviar entradas, salidas y ocupación estimada (cada 5 s y a los 300 ms de un cruce)"),
        Paso("evento", ACCION, 1, 4, "Registrar el evento de puerta y guardar la última apertura"),
        Paso("presencia", ACCION, 2, 7,
             "Derivar la ocupación y la presencia: el aula está vacía si la ocupación es 0"),
        Paso("cerrar", REUNION, 1.5, 8, ancho_en_columnas=1.4),
        Paso("evaluar", ACCION, 1.5, 9,
             "Evaluar RA-08 (consumo fantasma) y RA-09 (seguridad física) con puerta, presencia "
             "y horario"),
        Paso("fin", FIN, 1.5, 10),
    ),
    flujos=(
        Flujo("inicio", "abrir"),
        Flujo("abrir", "campo"),
        Flujo("abrir", "matriz"),
        Flujo("campo", "antirrebote"),
        Flujo("antirrebote", "puerta"),
        Flujo("puerta", "evento", "ESP-NOW", sale=ESTE, entra=OESTE),
        Flujo("evento", "cerrar", sale=SUR, entra=NORTE),
        Flujo("matriz", "cabezas"),
        Flujo("cabezas", "cruces"),
        Flujo("cruces", "negativa"),
        Flujo("negativa", "limitar", "[bajaría de 0]", sale=ESTE, entra=OESTE),
        Flujo("negativa", "seguir", "[no]"),
        Flujo("limitar", "seguir", sale=SUR, entra=ESTE, via=((4, 6),)),
        Flujo("seguir", "conteo"),
        Flujo("conteo", "presencia", "ESP-NOW", sale=OESTE, entra=ESTE),
        Flujo("presencia", "cerrar", sale=SUR, entra=NORTE),
        Flujo("cerrar", "evaluar"),
        Flujo("evaluar", "fin"),
    ),
    nota=("Fuente: nodo_magnetico.ino y nodo_termico.ino del docente (umbrales, antirrebote y "
          "líneas virtuales A y B) y demo/servidor/gemelo/estado.py.\n\n"
          "Los dos nodos trabajan por separado: el térmico cuenta con la matriz, sin cámaras y sin "
          "mirar al KY-024; el KY-024 solo informa la puerta. Los junta el servicio. Un cruce dudoso "
          "(varias personas a la vez) o un objeto caliente quieto más de 1 min "
          "(OBJETO_ESTATICO) también se marcan en el nodo.\n\n"
          "Estado: modelo del comportamiento; el conteo no se ha medido en el aula (CP-02)."),
)


# ==========================================================================================
# 3. Detección, diagnóstico y alerta (servicio del grupo: servicio.py, grafos.py)
# ==========================================================================================
ALERTA = Actividad(
    nombre="Detección, diagnóstico y alerta",
    diagrama="3 act [Comportamiento] Detección, diagnóstico y alerta",
    carriles=(
        Carril("Evaluador de RA", 0, 0),
        Carril("Motor causal SymCure", 1, 1),
        Carril("Salidas", 2, 5),
    ),
    pasos=(
        Paso("inicio", INICIO, 0, 0),
        Paso("recibir", ACCION, 0, 1, "Recibir la lectura del Gateway y actualizar el estado del aula"),
        Paso("evaluar", ACCION, 0, 2,
             "Evaluar RA-01..10 con los umbrales de config/requisitos_ra.yaml"),
        Paso("alerta", DECISION, 0, 3),
        Paso("nominal", FIN_DE_FLUJO, 0, 4),
        Paso("grafo", ACCION, 1, 3,
             "Recorrer el grafo del RA aguas arriba: causas confirmadas y sospechosas"),
        Paso("recomendar", ACCION, 1, 4, "Reunir las recomendaciones de las causas"),
        Paso("cambio", DECISION, 1, 5),
        Paso("repetida", FIN_DE_FLUJO, 1, 6),
        Paso("abrir", BIFURCACION, 3.5, 6, ancho_en_columnas=3.2),
        Paso("bitacora", ACCION, 2, 7,
             "Registrar el evento con sus causas y recomendaciones en la bitácora y en InfluxDB"),
        Paso("mqtt", ACCION, 3, 7, "Publicar el evento en MQTT (campustwin/evento)"),
        Paso("tablero", ACCION, 4, 7, "Mostrar la alerta, las causas y las recomendaciones en el tablero"),
        Paso("voz", ACCION, 5, 7, "Anunciar por voz en la siguiente consulta (copiloto: pendiente)"),
        Paso("cerrar", REUNION, 3.5, 8, ancho_en_columnas=3.2),
        Paso("fin", FIN, 3.5, 9),
    ),
    flujos=(
        Flujo("inicio", "recibir"),
        Flujo("recibir", "evaluar"),
        Flujo("evaluar", "alerta"),
        Flujo("alerta", "nominal", "[sin alertas]"),
        Flujo("alerta", "grafo", "[alerta o crítico]", sale=ESTE, entra=OESTE),
        Flujo("grafo", "recomendar"),
        Flujo("recomendar", "cambio"),
        Flujo("cambio", "repetida", "[sin cambio]"),
        Flujo("cambio", "abrir", "[cambió de nivel]", sale=ESTE, entra=NORTE, via=((3.5, 5),)),
        Flujo("abrir", "bitacora"),
        Flujo("abrir", "mqtt"),
        Flujo("abrir", "tablero"),
        Flujo("abrir", "voz"),
        Flujo("bitacora", "cerrar"),
        Flujo("mqtt", "cerrar"),
        Flujo("tablero", "cerrar"),
        Flujo("voz", "cerrar"),
        Flujo("cerrar", "fin"),
    ),
    nota=("Fuente: demo/servidor/gemelo/servicio.py (evaluación y salidas), grafos.py y "
          "razonamiento.py (SymCure) y config/requisitos_ra.yaml.\n\n"
          "El servicio registra un RA solo cuando cambia de nivel, así que una alerta que sigue "
          "activa no se repite. El silencio configurable de 15 min que pide RF-08 no está "
          "implementado todavía. Hoy se publican los tópicos campustwin/evento y campustwin/ra; "
          "el tópico diagnostico de la decisión D4 aún no: las causas y las recomendaciones "
          "viajan dentro del evento.\n\n"
          "Estado: simulado; con el simulador funciona de punta a punta, sin hardware real."),
)

ACTIVIDADES = (TELEMETRIA, PERSONAS, ALERTA)


# ==========================================================================================
# Máquinas de estados
# ==========================================================================================
@dataclass(frozen=True)
class Estado:
    clave: str
    nombre: str
    columna: float
    fila: float
    contiene: tuple[str, ...] = ()  # claves de los estados de un estado compuesto


@dataclass(frozen=True)
class Transicion:
    origen: str
    destino: str
    etiqueta: str = ""
    sale: tuple[str, float] | None = None  # (lado, fracción a lo largo del lado)
    entra: tuple[str, float] | None = None
    via: tuple[tuple[float, float], ...] = ()


@dataclass(frozen=True)
class MaquinaDeEstados:
    nombre: str
    diagrama: str
    inicios: tuple[tuple[str, float, float, str], ...]  # (clave, columna, fila, estado al que va)
    estados: tuple[Estado, ...]
    transiciones: tuple[Transicion, ...]
    nota: str


# El brief de la EC3 (§12) fija los estados del salón: Vacío, Ocupado, Sobreaforo, Luces sin
# ocupación, Alarma de gas y Fuera de horario. Los cinco primeros no gas se mueven con la
# ocupación, las luces y el horario; el gas manda sobre todos, por eso el estado compuesto.
AULA = MaquinaDeEstados(
    nombre="Estados del aula",
    diagrama="4 stm [Comportamiento] Estados del aula",
    inicios=(
        ("inicio_aula", -1.35, 1, "operacion"),
        ("inicio_operacion", -0.7, 1, "vacio"),
    ),
    estados=(
        Estado("operacion", "Operación normal", 0, 0,
               contiene=("luces", "vacio", "ocupado", "sobreaforo", "fuera")),
        Estado("luces", "Luces sin ocupación", 0, 0),
        Estado("vacio", "Vacío", 0, 1),
        Estado("fuera", "Uso fuera de horario", 0, 2),
        Estado("ocupado", "Ocupado", 1, 1),
        Estado("sobreaforo", "Sobreaforo", 2, 1),
        Estado("gas", "Alarma de gas", 3.2, 1),
    ),
    # Los pares de transiciones van separados a lo largo del lado, para que sus etiquetas no se
    # enciman. Las dos de «Ocupado» a «Uso fuera de horario» bajan en L, una dentro de la otra.
    transiciones=(
        Transicion("inicio_aula", "operacion"),
        Transicion("inicio_operacion", "vacio"),
        Transicion("vacio", "ocupado", "entra alguien", (ESTE, 0.3), (OESTE, 0.3)),
        Transicion("ocupado", "vacio", "sale el último", (OESTE, 0.7), (ESTE, 0.7)),
        Transicion("ocupado", "sobreaforo", "supera el aforo", (ESTE, 0.3), (OESTE, 0.3)),
        Transicion("sobreaforo", "ocupado", "baja del aforo", (OESTE, 0.7), (ESTE, 0.7)),
        Transicion("vacio", "luces", "luces ≥ 10 min", (NORTE, 0.15), (SUR, 0.15)),
        Transicion("luces", "vacio", "luces apagadas", (SUR, 0.85), (NORTE, 0.85)),
        Transicion("luces", "ocupado", "entra alguien", (ESTE, 0.5), (NORTE, 0.15)),
        Transicion("vacio", "fuera", "fuera de horario", (SUR, 0.15), (NORTE, 0.15)),
        Transicion("fuera", "vacio", "aula vacía", (NORTE, 0.85), (SUR, 0.85)),
        Transicion("ocupado", "fuera", "cierra el horario", (SUR, 0.3), (ESTE, 0.3),
                   via=((0.88, 1.92),)),
        Transicion("fuera", "ocupado", "vuelve el horario", (ESTE, 0.7), (SUR, 0.7),
                   via=((1.12, 2.08),)),
        Transicion("operacion", "gas", "RA-05 crítico", (ESTE, 0.3), (OESTE, 0.3)),
        Transicion("gas", "operacion", "RA-05 nominal", (OESTE, 0.7), (ESTE, 0.7)),
    ),
    nota=("Fuente: brief de la EC3 (§12), config/aula_l419.yaml (aforo y horario) y los RA-05, "
          "RA-08 y RA-09 de config/requisitos_ra.yaml. Las guardas son las condiciones que evalúa el "
          "servicio con las lecturas de los nodos 5 y 6 (ocupación, puerta), 4 (luces) y 3 (gas).\n\n"
          "«Luces sin ocupación» es el consumo fantasma (RA-08): el aula vacía con luces "
          "encendidas 10 min. «Uso fuera de horario» es el RA-09. La alarma de gas manda sobre "
          "cualquier estado y vuelve al estado normal cuando el RA-05 se normaliza.\n\n"
          "Estado: modelo del comportamiento; el aforo y el horario son supuestos de la configuración."),
)

# Los estados del nodo son los del brief (§12): Calentando, Activo, Sin datos y Falla. «Sin datos»
# lo decide el servicio por el tiempo sin recibir paquetes, no el nodo.
NODO = MaquinaDeEstados(
    nombre="Estados de un nodo",
    diagrama="5 stm [Comportamiento] Estados de un nodo",
    inicios=(("inicio", -1.0, 0, "calentando"),),
    estados=(
        Estado("calentando", "Calentando", 0, 0),
        Estado("activo", "Activo", 1.3, 0),
        Estado("falla", "Falla del sensor", 2.6, 0),
        Estado("sin_datos", "Sin datos", 1.3, 1.7),
    ),
    transiciones=(
        Transicion("inicio", "calentando", "encendido o reinicio"),
        Transicion("calentando", "activo", "calentamiento terminado"),
        Transicion("activo", "falla", "5 lecturas inválidas", (ESTE, 0.3), (OESTE, 0.3)),
        Transicion("falla", "activo", "lectura válida", (OESTE, 0.7), (ESTE, 0.7)),
        Transicion("activo", "sin_datos", "3 periodos sin paquete (mín. 30 s)"),
        Transicion("sin_datos", "calentando", "vuelve a arrancar", (OESTE, 0.5), (SUR, 0.5),
                   via=((0, 1.7),)),
    ),
    nota=("Fuente: nodo_co2.ino (calentamiento de 3 min, FALLO_SENSOR tras 5 fallos seguidos), "
          "demo/servidor/gemelo/estado.py (un nodo está caído tras tres periodos propios sin "
          "reportar, con un mínimo de 30 s) y el RA-10.\n\n"
          "Los nodos sin calentamiento (ambiente, luz, magnético) pasan de inmediato a «Activo»; "
          "el MQ-2 calienta unos 60 s. «Sin datos» lo decide el servicio, no el nodo, y puede "
          "llegar desde cualquier estado si se agota la batería. Sin nivel de batería en el paquete, "
          "una batería agotada solo se ve como un nodo sin datos.\n\n"
          "Estado: modelo del comportamiento; sin mediciones reales."),
)

MAQUINAS_DE_ESTADOS = (AULA, NODO)


# ==========================================================================================
# Casos de uso
# ==========================================================================================
@dataclass(frozen=True)
class Actor:
    clave: str
    nombre: str
    columna: float  # 0 = izquierda, 1 = derecha
    fila: float


@dataclass(frozen=True)
class CasoDeUso:
    clave: str
    nombre: str
    columna: float  # 0 = escenario de la izquierda, 1 = compartido, 2 = escenario de la derecha
    fila: float
    escenario: bool = True  # False: lo incluyen los escenarios; no lo inicia un actor


@dataclass(frozen=True)
class RelacionDeUso:
    clase: str  # "asociacion", "include" o "extend"
    origen: str  # actor o caso que depende
    destino: str


ACTORES = (
    Actor("docente", "Docente", 0, 0),
    Actor("mantenimiento", "Técnico de mantenimiento", 0, 1.5),
    Actor("limpieza", "Personal de limpieza", 0, 3),
    Actor("brigada", "Brigada de emergencia", 1, 0.5),
    Actor("administrador", "Administrador de infraestructura", 1, 4),
    Actor("vigilante", "Vigilante", 1, 5),
)

CASOS_DE_USO = (
    CasoDeUso("clase", "Dictar clase", 0, 0),
    CasoDeUso("mantener", "Mantener el aula y los nodos", 0, 1.5),
    CasoDeUso("limpiar", "Limpiar el aula", 0, 3),
    CasoDeUso("emergencia", "Atender una emergencia (gas o humo)", 2, 0.5),
    CasoDeUso("monitorear", "Monitorear consumo y condición", 2, 4),
    CasoDeUso("ronda", "Hacer la ronda nocturna", 2, 5),
    CasoDeUso("condicion", "Consultar la condición del aula (RA)", 1, 0, escenario=False),
    CasoDeUso("diagnostico", "Ver el diagnóstico causal y su recomendación", 1, 1, escenario=False),
    CasoDeUso("salud", "Revisar la salud de nodos y Gateway", 1, 2, escenario=False),
    CasoDeUso("evento", "Registrar el evento en el log", 1, 3, escenario=False),
    CasoDeUso("fantasma", "Ver el consumo fantasma y el ahorro", 1, 4, escenario=False),
    CasoDeUso("voz", "Consultar por voz (copiloto, pendiente)", 1, 5, escenario=False),
)

RELACIONES_DE_USO = (
    RelacionDeUso("asociacion", "docente", "clase"),
    RelacionDeUso("asociacion", "mantenimiento", "mantener"),
    RelacionDeUso("asociacion", "limpieza", "limpiar"),
    RelacionDeUso("asociacion", "brigada", "emergencia"),
    RelacionDeUso("asociacion", "administrador", "monitorear"),
    RelacionDeUso("asociacion", "vigilante", "ronda"),
    RelacionDeUso("include", "clase", "condicion"),
    RelacionDeUso("include", "mantener", "diagnostico"),
    RelacionDeUso("include", "mantener", "salud"),
    RelacionDeUso("include", "limpiar", "evento"),
    RelacionDeUso("include", "emergencia", "condicion"),
    RelacionDeUso("include", "emergencia", "diagnostico"),
    RelacionDeUso("include", "monitorear", "fantasma"),
    RelacionDeUso("include", "ronda", "voz"),
)

NOTA_DE_CASOS_DE_USO = (
    "Fuente: brief de la EC3 (§12) y docs/00-idea-principal.md §7. Los seis escenarios de los "
    "extremos son los pedidos; los de la columna central son lo que el sistema ofrece a "
    "varios de ellos y por eso los «incluyen».\n\n"
    "Clase: el CO₂ sube con el aula llena y el RA-03 recomienda ventilar. Mantenimiento: nodos "
    "caídos y reportes de los grafos del RA-01, RA-03, RA-04 y RA-10. Limpieza: la apertura "
    "fuera de horario es esperada, pero queda en el log (RA-08 y RA-09). Emergencia: el RA-05 "
    "crítico muestra los ocupantes para evacuar. Administrador: consumo fantasma y ahorro en S/ "
    "y kg CO₂. Ronda: briefing y consultas por voz, que dependen del copiloto, pendiente (S16).\n\n"
    "Estado: modelo del comportamiento; ninguno de los escenarios se ha ensayado en el aula."
)
