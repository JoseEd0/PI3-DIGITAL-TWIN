"""Constantes del gemelo simulado del L-419.

Todo lo que en el sistema real vive en un archivo de configuracion (RNF-07) vive
aqui: nodos, topicos, periodos, umbrales, horario, tarifa y factor de emision.
Los valores marcados como PENDIENTE dependen de una respuesta del stakeholder
(docs/00-idea-principal.md seccion 15) y se ajustan cuando llegue.
"""

from __future__ import annotations

# --- Reloj virtual ----------------------------------------------------------
# La demo comprime el dia: con VELOCIDAD_POR_DEFECTO = 60, un segundo real es un
# minuto simulado, asi que un dia completo (con su noche) dura 24 minutos.
VELOCIDAD_POR_DEFECTO = 60.0
VELOCIDAD_MINIMA = 1.0
VELOCIDAD_MAXIMA = 600.0
HORA_DE_INICIO = 7.0  # el dia simulado arranca a las 07:00
PERIODO_DE_TICK_S = 0.5  # cada cuanto avanza el simulador en tiempo real

# --- Nodos (seis fisicos, docs seccion 4) -----------------------------------
NODO_ENERGIA = "energia"
NODO_AMBIENTAL = "ambiental"
NODO_OCUPACION_PUERTA = "ocupacion-puerta"
NODO_OCUPACION_FONDO = "ocupacion-fondo"
NODO_PUERTA = "puerta"
NODO_AUDIO = "audio"
ENCHUFE_PROYECTOR = "enchufe-proyector"
ENCHUFE_PC = "enchufe-pc"

# nodo -> (etiqueta para la interfaz, requisito que lo justifica, periodo de envio en segundos simulados)
NODOS = {
    NODO_ENERGIA: ("Nodo de Energía", "RF-01", 10),
    ENCHUFE_PROYECTOR: ("Enchufe del proyector", "RF-12", 60),
    ENCHUFE_PC: ("Enchufe del PC principal", "RF-12", 60),
    NODO_AMBIENTAL: ("Nodo Ambiental", "RF-02", 60),
    NODO_OCUPACION_PUERTA: ("Nodo de Ocupación (puerta)", "RF-03", 30),
    NODO_OCUPACION_FONDO: ("Nodo de Ocupación (fondo)", "RF-03", 30),
    NODO_PUERTA: ("Nodo de Puerta", "RF-04", 1800),
    NODO_AUDIO: ("Nodo de Audio (opcional)", "RF-09", 300),
}

# --- Contrato de datos (docs seccion 6.1) -----------------------------------
PREFIJO_DE_TOPICO = "l419"
ORIGEN_DEMO = "demo"
ORIGEN_REAL = "real"

# magnitud -> unidad
UNIDADES = {
    "tension": "V",
    "corriente": "A",
    "potencia": "W",
    "factorDePotencia": "",
    "energia": "kWh",
    "temperatura": "°C",
    "humedad": "%HR",
    "co2": "ppm",
    "iluminancia": "lx",
    "presencia": "",
    "conteo": "personas",
    "estadoPuerta": "",
    "vibracion": "",
    "bateria": "%",
    "senal": "dBm",
}

# --- Horario oficial del laboratorio ----------------------------------------
# PENDIENTE: confirmar con el coordinador (pregunta 3). Sirve para "fuera de
# horario" en RF-04, RF-08 y RF-10.
HORARIO_OFICIAL = (7.0, 22.0)
BLOQUES_DE_CLASE = [(8.0, 10.0), (10.25, 12.25), (14.0, 16.0), (18.0, 20.0)]
RONDA_DEL_VIGILANTE = 3.0  # el vigilante abre la puerta en su ronda de las 03:00

# --- Cargas electricas del laboratorio --------------------------------------
POTENCIA_EN_REPOSO_W = 45.0  # router, reloj, equipos en espera
POTENCIA_POR_LUMINARIA_W = 36.0
LUMINARIAS = 6
POTENCIA_DEL_PROYECTOR_W = 280.0
POTENCIA_POR_PC_W = 62.0
PCS_DEL_LABORATORIO = 12
POTENCIA_DEL_AIRE_W = 1180.0
TEMPERATURA_DE_ENCENDIDO_DEL_AIRE_C = 24.5
TEMPERATURA_DE_APAGADO_DEL_AIRE_C = 23.0
PERSONAS_PARA_ENCENDER_EL_AIRE = 8
TENSION_NOMINAL_V = 220.0
FACTOR_DE_POTENCIA_TIPICO = 0.94

# --- Ambiente ---------------------------------------------------------------
CO2_EXTERIOR_PPM = 420.0
# Calibrado para que un grupo de 13 personas estabilice cerca de 1500 ppm y uno
# de 24 cerca de 2400, que es lo que se mide en un aula sin ventilacion forzada.
CO2_POR_PERSONA_PPM_MIN = 3.0  # aporte de una persona por minuto simulado
CO2_RENOVACION_POR_MIN = 0.035  # fraccion que se renueva por minuto con puerta cerrada
CO2_MAXIMO_PPM = 5000.0  # tope del SCD41: por encima, el sensor satura
CO2_RENOVACION_PUERTA_ABIERTA = 0.18
UMBRAL_DE_CO2_PPM = 1000.0  # PENDIENTE: confirmar con la universidad (pregunta 4)
TEMPERATURA_BASE_C = 20.5
TEMPERATURA_POR_PERSONA_C = 0.14
HUMEDAD_BASE_HR = 62.0
ILUMINANCIA_POR_LUMINARIA_LX = 78.0
ILUMINANCIA_DIURNA_MAXIMA_LX = 260.0

# --- Ocupacion --------------------------------------------------------------
AFORO_DEL_LABORATORIO = 24
MINUTOS_VACIO_PARA_FANTASMA = 15  # RF-10: "desocupado" son 15 min seguidos sin presencia
MINUTOS_VACIO_PARA_REINICIAR_CONTEO = 5  # RF-03: el conteo vuelve a 0 con el aula vacia
ERROR_DE_CONTEO = 2  # RF-03: el conteo es una estimacion de +-2 personas

# --- Nodo de puerta (RNF-04) ------------------------------------------------
BATERIA_INICIAL = 96.0
DIAS_DE_AUTONOMIA = 30
UMBRAL_DE_BATERIA_BAJA = 20.0

# --- Salud del sistema (RF-13) ----------------------------------------------
MINUTOS_SIN_DATOS_PARA_CAIDO = 5
PERIODOS_TOLERADOS = 3  # un nodo se da por caido tras tres periodos sin reportar
SENAL_TIPICA_DBM = -62.0
SENAL_DE_ENLACE_DEBIL_DBM = -87.0
PERDIDA_CON_ENLACE_DEBIL = 0.35  # fraccion de muestras que se pierde con mala senal
MAXIMO_DE_MUESTRAS_PERDIDAS = 1.0  # porcentaje maximo aceptable en una semana

# --- Reglas y alertas (RF-08) ------------------------------------------------
SILENCIO_DE_ALERTA_MIN = 15  # no repetir la misma alerta antes de 15 min simulados
UMBRAL_DE_CONSUMO_CON_AULA_VACIA_W = 120.0

# --- Ahorro (RF-10) ---------------------------------------------------------
# PENDIENTE: tarifa real de la factura de UTEC (pregunta 6).
TARIFA_SOLES_POR_KWH = 0.68
FACTOR_DE_EMISION_KG_POR_KWH = 0.45  # red peruana (SEIN), configurable

# --- Historico en memoria ---------------------------------------------------
# La demo no usa base de datos: guarda una ventana en memoria. En el sistema
# real esto es InfluxDB con retencion de 60 dias (RF-06).
MUESTRAS_POR_SERIE = 720

# --- Servidor ---------------------------------------------------------------
PUERTO_POR_DEFECTO = 8000
INTERVALO_DE_STREAM_S = 0.5
