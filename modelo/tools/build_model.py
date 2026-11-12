"""Genera el modelo SysML base de Campus Twin (aula laboratorio L-419).

Se ejecuta con el interprete embebido de Gaphor:

    /Applications/Gaphor.app/Contents/MacOS/gaphor exec modelo/tools/build_model.py

Reconstruye por completo `modelo/campus-twin-l419.gaphor` a partir de los datos
declarados en este archivo. El contenido sale de docs/00-idea-principal.md; los
identificadores de requisito (NS-x, RF-xx, RNF-xx, CP-xx) son los mismos en el
documento, en el modelo y en las tareas de Asana.

Ademas de los diagramas de septiembre (propuesta original), arma el subpaquete
`02 Estructura/0 Arquitectura oficial EC3`: los 7 nodos con sus cajas, el Gateway, la laptop,
los servicios del grupo, los objetos del aula y el IBD del flujo de datos. Agrega los RA-01..10
de config/requisitos_ra.yaml con derivacion, satisfy y verify, y el paquete
`05 Diagnóstico causal` con el grafo de cada RA (los lee exportar_ra.py con el Python del servicio).

Una vez que el modelo se edita a mano en Gaphor, el .gaphor pasa a ser la fuente de
verdad y este script queda como registro reproducible del modelo base.

Los nombres de diagrama empiezan con un numero porque el arbol del modelo de Gaphor
ordena los hijos de cada paquete alfabeticamente: sin el numero, los diagramas quedan
mezclados entre los requisitos y los bloques.
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from gaphas.connector import Handle
from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import connect
from gaphor.plugins.autolayout import AutoLayout
from gaphor.storage.save import save
from gaphor.SysML import sysml
from gaphor.SysML.requirements.relationships import DeriveReqtItem, SatisfyItem, VerifyItem
from gaphor.UML import uml
from gaphor.UML.actions.activitynodes import DecisionNodeItem, ForkNodeItem
from gaphor.UML.actions.flow import ControlFlowItem
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.deployments.connector import ConnectorItem
from gaphor.UML.general.comment import CommentLineItem
from gaphor.UML.states.transition import TransitionItem
from gaphor.UML.usecases.extend import ExtendItem
from gaphor.UML.usecases.include import IncludeItem
from gaphor.UML.uml import Activity, Comment, Package, Property

# El script se ejecuta con `gaphor exec`: su carpeta no esta en sys.path, y los datos del
# paquete 04 viven en un modulo hermano.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import datos_comportamiento as comp  # noqa: E402

MODEL_PATH = Path(__file__).resolve().parents[1] / "campus-twin-l419.gaphor"
GRID_STEP = 220  # separacion inicial entre items; el layout la recalcula
COMMENT_WIDTH = 360  # ancho de las notas, para que el texto no quede en una columna
REQUIREMENT_WIDTH = 250  # sin ancho fijo, el texto del requisito queda en una columna
# Los bloques que muestran magnitudes llevan ancho fijo. Sin el, la caja crece
# cuando la demo escribe el valor ("= CERRADA" son 60 px mas) y se sale encima
# de su vecina, porque el layout ya se calculo con la caja vacia.
ANCHO_DE_BLOQUE_CON_VALORES = 410

# Los diagramas de derivacion, trazabilidad y verificacion son bipartitos: graphviz
# los estira en una sola fila de varios miles de pixeles, asi que se acomodan a mano
# en dos columnas (origen a la izquierda, elementos relacionados a la derecha).
COLUMNA_IZQUIERDA_X = 0.0
COLUMNA_DERECHA_X = 470.0
SEPARACION_VERTICAL = 30.0
SEPARACION_ENTRE_GRUPOS = 60.0

# El diagrama de instrumentacion tambien se acomoda a mano: una columna por nodo,
# con sus sensores debajo. Ver diagrama_de_instrumentacion().
SEPARACION_ENTRE_COLUMNAS = 56.0
SEPARACION_ENTRE_FILAS = 54.0
SEPARACION_ENTRE_SENSORES = 22.0
# Los sensores van indentados respecto de su nodo: la linea baja por el pasillo
# que queda a la izquierda en vez de cruzar por encima de las cajas de arriba.
INDENTACION_DE_SENSORES = 44.0

# --- Requisitos -------------------------------------------------------------
# Version corta de docs/00-idea-principal.md seccion 8 (migrada a la arquitectura
# oficial el 10/11/2026).
# (id, nombre, texto)
NECESIDADES = [
    ("NS-1", "Ronda informada",
     "El vigilante nocturno necesita conocer el estado del laboratorio durante su ronda sin cargar una laptop."),
    ("NS-2", "Consumo bajo control",
     "El administrador de infraestructura necesita evidencia medible del consumo para reducirlo y sustentar certificaciones."),
    ("NS-3", "Ambiente apto",
     "El coordinador del laboratorio necesita temperatura, humedad y CO2 aptos para las clases y los equipos."),
    ("NS-4", "Acceso vigilado",
     "Seguridad del campus necesita detectar aperturas o manipulaciones del laboratorio fuera de horario."),
    ("NS-5", "Demostración reproducible",
     "El equipo de PI3 necesita una demo en vivo que funcione sin depender de la red del campus."),
    ("NS-6", "Red segura",
     "TI de UTEC necesita que los dispositivos del proyecto no abran huecos ni interfieran en la red del campus."),
    ("NS-7", "Privacidad",
     "Los estudiantes y el personal del laboratorio necesitan que el sistema no los identifique ni grabe."),
]

# (id, nombre, texto, necesidades de las que deriva)
REQUISITOS_FUNCIONALES = [
    ("RF-01", "Medición de energía total",
     "El sistema debe estimar la potencia y la energía del aula por proxy, sin PZEM (luces, ocupación, ruido del aire acondicionado y horario por el inventario de potencias), con actualización ≤ 10 s, y presentarla siempre como estimación.",
     ["NS-2"]),
    ("RF-02", "Medición ambiental",
     "El sistema debe medir temperatura (±1 °C), humedad (±3 % HR) y presión con el BME280, CO2 (±50 ppm + 5 %) con el MH-Z1911A, iluminancia (±20 %) con el BH1750 y nivel sonoro aproximado con el INMP441, con periodo ≤ 60 s.",
     ["NS-3"]),
    ("RF-03", "Estimación de ocupación",
     "El sistema debe contar entradas y salidas sin cámaras con la MLX90640 y el KY-024 en la puerta, con error ≤ ±2 hasta 10 personas, y derivar la presencia con acierto ≥ 95 % y latencia ≤ 30 s.",
     ["NS-1", "NS-3"]),
    ("RF-04", "Eventos de puerta",
     "El sistema debe registrar apertura y cierre en ≤ 10 s con el KY-024 y un solo evento por apertura prolongada (≥ 10 min). La detección de vibración se retiró.",
     ["NS-4"]),
    ("RF-05", "Transporte de datos",
     "Los nodos deben enviar por ESP-NOW al Gateway, y este publicar por Wi-Fi y MQTT en el formato del contrato, con seq para contar muestras perdidas y reinicios y el estado del Gateway por LWT. Las pérdidas se miden, no se recuperan (QoS 0).",
     ["NS-5"]),
    ("RF-06", "Histórico y consulta",
     "El servidor debe retener ≥ 60 días en InfluxDB y permitir consultas por rango, magnitud y agregación en Flux, en Grafana y en la API del grupo.",
     ["NS-2"]),
    ("RF-07", "Dashboard web",
     "El dashboard debe mostrar el estado en vivo (refresco ≤ 5 s), la condición de cada RA con causas y recomendaciones, históricos, plano 2D, ahorro y salud, en la red local sin internet desde cualquier laptop.",
     ["NS-2"]),
    ("RF-08", "Alertas por reglas",
     "El sistema debe generar alertas configurables, una regla por RA-01..10 en config/requisitos_ra.yaml, en el dashboard, el log y la voz, sin repetir la misma alerta más de una vez cada 15 min.",
     ["NS-1", "NS-4"]),
    ("RF-09", "Copiloto de voz",
     "La app de voz en el teléfono del vigilante debe dar el briefing de turno y responder al menos 8 intenciones cerradas en español en ≤ 5 s, y pedir repetir cuando no entiende.",
     ["NS-1"]),
    ("RF-10", "Detección de consumo fantasma",
     "El sistema debe reportar la energía estimada con el aula vacía y luces o equipos encendidos por ≥ 10 min, por franja y por carga, con ahorro en S/ y kg CO2 configurables.",
     ["NS-2"]),
    ("RF-11", "Modo demostración y simulador",
     "El sistema debe generar datos sintéticos en el formato exacto del Gateway (grupo sim) y reproducir datos grabados, por nodo o completo, con la franja DATOS SIMULADOS visible.",
     ["NS-5"]),
    ("RF-12", "Medición de energía por carga",
     "El sistema debe estimar el consumo por tipo de carga (luminarias, PC, proyector y aire acondicionado) con el inventario de config/aula_l419.yaml y la señal de cada carga, sin internet.",
     ["NS-2"]),
    ("RF-13", "Supervisión de salud del sistema",
     "El servidor debe reportar por nodo la última muestra, las muestras perdidas y los reinicios, y el estado del Gateway por LWT; marcar caído un nodo tras 3 periodos propios sin datos (mínimo 30 s) y mantener las pérdidas ≤ 1 %.",
     ["NS-5"]),
]

REQUISITOS_NO_FUNCIONALES = [
    ("RNF-01", "Instalación no invasiva y segura",
     "La instalación no debe perforar paredes ni cortar conductores: cajas con montaje adhesivo o bridas, y ningún nodo conectado a 220 V (18650 o USB de 5 V).",
     ["NS-5"]),
    ("RNF-02", "Privacidad por diseño",
     "El sistema no debe usar cámaras: la MLX90640 solo envía conteos y el INMP441 solo niveles en dB; el audio del copiloto se descarta, la ocupación es agregada y no se registra quién consulta.",
     ["NS-4", "NS-7"]),
    ("RNF-03", "Presupuesto acotado",
     "El hardware lo compró el curso (OC-UTEC-004033-26) y no se carga al grupo; el gasto propio, si lo hay, se registra y no supera S/ 2808.",
     ["NS-5"]),
    ("RNF-04", "Autonomía del nodo de puerta",
     "El nodo 6 con la 18650 de 1600 mAh debe operar ≥ 30 días. Con el firmware actual (envío cada 10 s, sin sueño profundo) no se alcanza sin envío por evento o USB.",
     ["NS-4"]),
    ("RNF-05", "Operación autónoma sin internet",
     "Todo el sistema (nodos, Gateway, servidor, dashboard, voz y hora) debe operar en la red local sin internet ni nube, con NTP local en la laptop.",
     ["NS-5", "NS-6"]),
    ("RNF-06", "Disponibilidad para la demo",
     "El sistema debe operar 72 h continuas sin intervención, con arranque automático de servicios y nodos y respaldo diario de InfluxDB a un disco USB.",
     ["NS-5"]),
    ("RNF-07", "Configurabilidad",
     "Pines, umbrales, intervalos, horario oficial, tarifa, factor de emisión y endpoints deben ser configurables y sin credenciales en el repositorio.",
     ["NS-5"]),
    ("RNF-08", "Seguridad básica de acceso",
     "La red propia debe usar WPA2, el broker usuario y contraseña, el dashboard y la API inicio de sesión y HTTPS, sin puertos hacia la red del campus.",
     ["NS-6"]),
]

# (id, nombre, requisitos que verifica, estado). El estado va al campo Note del caso, con los
# rotulos del proyecto: real, simulado o pendiente. CP-01 se retiro el 10/11/2026 (energia
# contra PZEM, que no esta en la arquitectura oficial) y su numero no se reutiliza.
CASOS_DE_PRUEBA = [
    ("CP-02", "Conteo con la MLX90640 y el KY-024", ["RF-03"], "Pendiente (S15)"),
    ("CP-03", "Resiliencia de red y operación sin internet", ["RF-05", "RNF-05"],
     "Simulado (Gateway caído); pendiente en hardware"),
    ("CP-04", "Copiloto de voz en el teléfono", ["RF-09"], "Pendiente (S16)"),
    ("CP-05", "Maratón de 72 horas con corte de energía", ["RNF-06"], "Pendiente (S16)"),
    ("CP-06", "Auditoría de consumo fantasma", ["RF-10", "RF-01", "RF-12"],
     "Simulado (docs/pruebas/CP-06-consumo-fantasma.md)"),
    ("CP-07", "Consistencia ambiental", ["RF-02"], "Pendiente (S15)"),
    ("CP-08", "Eventos de puerta con el KY-024", ["RF-04"], "Pendiente (S15)"),
    ("CP-09", "Histórico, API y dashboard", ["RF-06", "RF-07"], "Simulado"),
    ("CP-10", "Reglas de alerta", ["RF-08"], "Simulado"),
    ("CP-11", "Modo demostración por nodo", ["RF-11"],
     "Simulado (grabación y reproducción de punta a punta, 10/11)"),
    ("CP-12", "Instalación no invasiva, seguridad eléctrica y privacidad", ["RNF-01", "RNF-02"],
     "Privacidad: real, por revisión de código; instalación: pendiente (S15)"),
    ("CP-13", "Autonomía de las cajas con 18650", ["RNF-04"],
     "Estimación de hoja de datos hecha; medición pendiente (S15)"),
    ("CP-14", "Auditoría de costos, configuración y credenciales", ["RNF-03", "RNF-07", "RNF-08"],
     "Real, por revisión del repositorio (docs/pruebas/CP-14-auditoria-repositorio.md)"),
    ("CP-15", "Supervisión de nodos", ["RF-13"], "Simulado"),
]

# --- Estructura -------------------------------------------------------------
SISTEMA = "Campus Twin L-419"
SUBSISTEMAS = [
    "Subsistema de Sensado",
    "Servidor Campus Twin",
    "Dashboard Web",
    "Copiloto de Voz",
    "Red Local",
    "Subsistema de Alimentación",
]
ACTORES_EXTERNOS = [
    "Vigilante Nocturno",
    "Administrador de Infraestructura",
    "Coordinador del Laboratorio",
    "Seguridad del Campus",
    "Laboratorio L-419",
]

NODO_BASE = "Nodo Sensor ESP32"
NODOS = {
    "Nodo de Energía": ["PZEM-004T v3.0", "Pinza SCT-013", "Enchufe Inteligente (Tasmota)"],
    "Nodo Ambiental": ["Sensor SHT31", "Sensor BH1750", "Sensor SCD41"],
    "Nodo de Ocupación": ["Radar HLK-LD2410C", "PIR HC-SR501", "ToF VL53L1X"],
    "Nodo de Puerta": ["Sensor Magnético de Puerta", "Sensor de Vibración SW-420", "Batería LiPo 2000 mAh"],
}

SERVICIOS_SERVIDOR = [
    "Broker MQTT",
    "Base de Datos de Series Temporales",
    "API REST",
    "Motor de Reglas y Alertas",
    "Servicio de Voz STT/TTS",
    "Supervisor de Salud",
    "Simulador y Modo Demo",
    "Servidor NTP Local",
]
NODO_AUDIO = "Nodo de Audio (opcional)"
PARTES_COPILOTO = ["App de Voz (PWA)", NODO_AUDIO]
PARTES_NODO_AUDIO = ["Micrófono INMP441", "Amplificador MAX98357A", "Parlante 4 ohm 3 W"]

TIPOS_DE_VALOR = [
    "Temperatura [°C]",
    "Humedad [%HR]",
    "CO2 [ppm]",
    "Iluminancia [lx]",
    "Tensión [V]",
    "Corriente [A]",
    "Potencia [W]",
    "Factor de potencia [-]",
    "Energía acumulada [kWh]",
    "Presencia [sí/no]",
    "Movimiento [sí/no]",
    "Vibración [sí/no]",
    "Estado de puerta [abierta/cerrada]",
    "Ocupación [personas]",
    "Latencia [s]",
    "Nivel de batería [%]",
    "Señal Wi-Fi [dBm]",
    "Muestras perdidas [%]",
]

# bloque -> [(nombre de la propiedad, tipo de valor)]
PROPIEDADES_DE_VALOR = {
    "Nodo Sensor ESP32": [
        ("senal", "Señal Wi-Fi [dBm]"),
    ],
    "Nodo Ambiental": [
        ("temperatura", "Temperatura [°C]"),
        ("humedad", "Humedad [%HR]"),
        ("co2", "CO2 [ppm]"),
        ("iluminancia", "Iluminancia [lx]"),
    ],
    "Nodo de Energía": [
        ("tension", "Tensión [V]"),
        ("corriente", "Corriente [A]"),
        ("potencia", "Potencia [W]"),
        ("factorDePotencia", "Factor de potencia [-]"),
        ("energia", "Energía acumulada [kWh]"),
    ],
    "Nodo de Ocupación": [
        ("presencia", "Presencia [sí/no]"),
        ("conteo", "Ocupación [personas]"),
    ],
    "Nodo de Puerta": [
        ("estadoPuerta", "Estado de puerta [abierta/cerrada]"),
        ("bateria", "Nivel de batería [%]"),
    ],
    "Servidor Campus Twin": [("latenciaDeConsulta", "Latencia [s]")],
    "Supervisor de Salud": [("muestrasPerdidas", "Muestras perdidas [%]")],
    # Cada sensor declara la magnitud que entrega a su nodo. Es lo que permite
    # leer el diagrama de instrumentacion y saber de donde sale cada dato.
    "PZEM-004T v3.0": [
        ("tension", "Tensión [V]"),
        ("corriente", "Corriente [A]"),
        ("potencia", "Potencia [W]"),
        ("factorDePotencia", "Factor de potencia [-]"),
        ("energia", "Energía acumulada [kWh]"),
    ],
    "Pinza SCT-013": [("corriente", "Corriente [A]")],
    "Enchufe Inteligente (Tasmota)": [
        ("potencia", "Potencia [W]"),
        ("energia", "Energía acumulada [kWh]"),
    ],
    "Sensor SHT31": [
        ("temperatura", "Temperatura [°C]"),
        ("humedad", "Humedad [%HR]"),
    ],
    "Sensor BH1750": [("iluminancia", "Iluminancia [lx]")],
    "Sensor SCD41": [("co2", "CO2 [ppm]")],
    "Radar HLK-LD2410C": [("presencia", "Presencia [sí/no]")],
    "PIR HC-SR501": [("movimiento", "Movimiento [sí/no]")],
    "ToF VL53L1X": [("conteo", "Ocupación [personas]")],
    "Sensor Magnético de Puerta": [("estadoPuerta", "Estado de puerta [abierta/cerrada]")],
    "Sensor de Vibración SW-420": [("vibracion", "Vibración [sí/no]")],
    "Batería LiPo 2000 mAh": [("nivel", "Nivel de batería [%]")],
}


# --- Arquitectura oficial (EC3) ---------------------------------------------
# Hardware que compro el curso, firmware y stack del docente y servicios del grupo, segun
# docs/02-instrumentacion-l419.md, config/nodos.yaml y docs/CONTRATO_DATOS.md.
# Va en un subpaquete propio y con nombres de bloque distintos de los de septiembre: los
# diagramas anteriores se conservan, y demo/gaphor-vivo busca sus bloques por nombre.
PAQUETE_OFICIAL = "0 Arquitectura oficial EC3"
CARPETA_DE_FOTOS = "docs/curso/imagenes"
ORDEN_DE_COMPRA = "OC-UTEC-004033-26"
NODOS_YAML = Path(__file__).resolve().parents[2] / "config" / "nodos.yaml"

SISTEMA_OFICIAL = "Gemelo Digital L-419"
RED_DE_NODOS = "Red de nodos ESP-NOW"
GATEWAY = "Gateway ESP32 v4"
RED_WIFI = "Red Wi-Fi local"
LAPTOP = "Laptop servidor (Docker)"
STACK_DOCENTE = "Stack IoT del docente"
SERVICIOS_DEL_GRUPO = "Servicios del Grupo 1"
AULA = "Aula L-419"

CAJA_DE_NODO = "Caja de nodo"
ESP32_DEVKIT = "ESP32 DevKit V1"
REGULADOR = "Regulador de tensión"
PARTES_DE_LA_CAJA = [
    ESP32_DEVKIT,
    "Protoboard 170 puntos",
    "Batería 18650 1600 mAh",
    "Porta-batería 18650",
    REGULADOR,
]


@dataclass(frozen=True)
class NodoOficial:
    """Un nodo de la arquitectura oficial; `tipo` es el del paquete ESP-NOW y del topico."""

    id: int
    tipo: str
    bloque: str
    sensor: str
    interfaz: str
    foto: str | None
    programa: str


NODOS_OFICIALES = [
    NodoOficial(1, "co2", "Nodo 1 CO2", "MH-Z1911A", "UART", "1-mh-z1911a-co2.jpg",
                "nodo_co2.ino (docente)"),
    NodoOficial(2, "audio", "Nodo 2 Ruido", "INMP441", "I²S", "6-inmp441-microfono.jpg",
                "nodo_audio.ino (docente)"),
    NodoOficial(3, "gas", "Nodo 3 Gas y humo", "MQ-2", "analógica + digital", None,
                "MQ-2.ino (Grupo 1, S8)"),
    NodoOficial(4, "luz", "Nodo 4 Luz", "BH1750 (GY-302)", "I²C", "5-gy-302-bh1750.jpg",
                "nodo_luz.ino (docente)"),
    NodoOficial(5, "termico", "Nodo 5 Conteo térmico", "MLX90640 32x24", "I²C", None,
                "nodo_termico.ino (docente)"),
    NodoOficial(6, "magnetico", "Nodo 6 Puerta", "KY-024 (Hall SS49E)", "analógica (ADC)",
                "2-ky-024-hall-ss49e.jpg", "nodo_magnetico.ino (docente)"),
    NodoOficial(7, "ambiente", "Nodo 7 Ambiente", "BME280 (GY-BME280)", "I²C", "4-bme280.jpg",
                "nodo_ambiente.ino (docente)"),
]

# Fotos que no son de un sensor de los nodos, y la razon de los sensores sin foto.
FOTO_DEL_ESP32 = "3-esp32-devkit-v1.jpg"
SIN_FOTO = {
    "MQ-2": "Sin foto: el MQ-2 no figura en la orden de compra. Reemplaza al detector Wi-Fi "
            f"Tuya de {CARPETA_DE_FOTOS}/7-tuya-detector-humo.jpg (anuncio del 21/10).",
    "MLX90640 32x24": "Sin foto: la etiqueta del MLX90640 no se fotografió.",
}

TIPOS_DE_VALOR_OFICIALES = [
    "Variación de CO2 [ppm/30 s]",
    "Nivel de alerta [texto]",
    "Nivel sonoro [dB SPL]",
    "Frecuencia [Hz]",
    "Indicador [0/1]",
    "Relación Rs/R0 [-]",
    "Cruces [n]",
    "Aperturas [n]",
    "Tiempo [s]",
    "Lectura ADC [cuentas]",
    "Presión [hPa]",
    "Cantidad [n]",
]

# Campos que cada sensor entrega en el JSON del Gateway (CONTRATO_DATOS.md, seccion 3).
MAGNITUDES_OFICIALES = {
    "MH-Z1911A": [
        ("co2_ppm", "CO2 [ppm]"),
        ("delta_30s", "Variación de CO2 [ppm/30 s]"),
        ("temp_c", "Temperatura [°C]"),
        ("nivel", "Nivel de alerta [texto]"),
    ],
    "INMP441": [
        ("leq_db", "Nivel sonoro [dB SPL]"),
        ("lmax_db", "Nivel sonoro [dB SPL]"),
        ("pico_db", "Nivel sonoro [dB SPL]"),
        ("base_db", "Nivel sonoro [dB SPL]"),
        ("freq_dom_hz", "Frecuencia [Hz]"),
        ("tonal", "Indicador [0/1]"),
    ],
    "MQ-2": [
        ("v_ao", "Tensión [V]"),
        ("rs_r0", "Relación Rs/R0 [-]"),
        ("do_alarma", "Indicador [0/1]"),
        ("calentando", "Indicador [0/1]"),
    ],
    "BH1750 (GY-302)": [
        ("lux", "Iluminancia [lx]"),
        ("lux_min", "Iluminancia [lx]"),
        ("lux_max", "Iluminancia [lx]"),
        ("lux_mesa_est", "Iluminancia [lx]"),
        ("luces_cambio", "Indicador [0/1]"),
    ],
    "MLX90640 32x24": [
        ("entradas", "Cruces [n]"),
        ("salidas", "Cruces [n]"),
        ("ocupacion_est", "Ocupación [personas]"),
        ("personas_en_vista", "Ocupación [personas]"),
        ("cruces_dudosos", "Cruces [n]"),
        ("t_fondo", "Temperatura [°C]"),
        ("t_max", "Temperatura [°C]"),
    ],
    "KY-024 (Hall SS49E)": [
        ("puerta_abierta", "Indicador [0/1]"),
        ("aperturas", "Aperturas [n]"),
        ("seg_abierta", "Tiempo [s]"),
        ("campo_raw", "Lectura ADC [cuentas]"),
    ],
    "BME280 (GY-BME280)": [
        ("temp_c", "Temperatura [°C]"),
        ("hum_pct", "Humedad [%HR]"),
        ("pres_hpa", "Presión [hPa]"),
    ],
}

# Stack del docente (vendor/gemelo_iot_profesor/servidor_iot) y servicios del grupo.
MOSQUITTO = "Mosquitto"
TELEGRAF = "Telegraf"
INFLUXDB = "InfluxDB 2.7"
GRAFANA = "Grafana"
PARTES_DEL_STACK = [MOSQUITTO, TELEGRAF, INFLUXDB, GRAFANA]

SERVICIO_GEMELO = "Servicio gemelo"
TABLERO = "Tablero web"
GAPHOR_EN_VIVO = "Gaphor en vivo"
COPILOTO = "Copiloto de voz (pendiente)"
SIMULADOR = "Simulador del Gateway"
PARTES_DE_LOS_SERVICIOS = [SERVICIO_GEMELO, TABLERO, GAPHOR_EN_VIVO, COPILOTO]
# Modulos de demo/servidor/gemelo/
EVALUADOR_DE_RA = "Evaluador de RA-01..10"
MOTOR_CAUSAL = "Motor causal SymCure"
CONSUMO_FANTASMA = "Consumo fantasma"
API_DEL_SERVICIO = "API REST y SSE"
MODULOS_DEL_SERVICIO = [
    "Ingesta MQTT",
    EVALUADOR_DE_RA,
    MOTOR_CAUSAL,
    "Log de eventos",
    CONSUMO_FANTASMA,
    SIMULADOR,
    "Grabación y reproducción",
    API_DEL_SERVICIO,
    "Escritura en InfluxDB",
]

# Objetos del aula (config/aula_l419.yaml: plano.objetos e inventario). Las cantidades y
# potencias viven alli; el modelo solo declara que propiedades tiene cada objeto.
OBJETOS_DEL_AULA = {
    "Puerta": [],
    "Ventana": [],
    "Aire acondicionado": [("potencia", "Potencia [W]")],
    "Luminarias": [("cantidad", "Cantidad [n]"), ("potencia", "Potencia [W]")],
    "PC": [("cantidad", "Cantidad [n]"), ("potencia", "Potencia [W]"),
           ("potenciaEnEspera", "Potencia [W]")],
    "Proyector": [("potencia", "Potencia [W]"), ("potenciaEnEspera", "Potencia [W]")],
    "Pizarra": [],
    "Tablero eléctrico": [],
}
# nodo -> objeto del aula que observa (lo que hace que el nodo "vea" ese objeto)
OBSERVACIONES = [
    ("Nodo 6 Puerta", "Puerta"),
    ("Nodo 5 Conteo térmico", "Puerta"),
    ("Nodo 4 Luz", "Luminarias"),
    ("Nodo 2 Ruido", "Aire acondicionado"),
    ("Nodo 1 CO2", AULA),
    ("Nodo 3 Gas y humo", AULA),
    ("Nodo 7 Ambiente", AULA),
]

# IBD: los items que viajan por cada conector (bloques que solo tipan el flujo).
SENAL = "Señal del sensor"
PAQUETE_ESPNOW = "Paquete ESP-NOW"
JSON_GATEWAY = "JSON del Gateway"
PUNTO_INFLUX = "Punto de InfluxDB"
SERIE = "Serie temporal"
ESTADO_JSON = "Estado del aula (JSON)"
ITEMS_DE_FLUJO = [SENAL, PAQUETE_ESPNOW, JSON_GATEWAY, PUNTO_INFLUX, SERIE, ESTADO_JSON]
CONTEXTO_DEL_FLUJO = "Cadena de datos L-419"

# El IBD se acomoda a mano en columnas; el hueco deja lugar a las etiquetas de los conectores.
HUECO_ENTRE_COLUMNAS_IBD = 250.0
SEPARACION_ENTRE_PARTES = 34.0
ANCHO_DE_SENSOR_OFICIAL = 320
ANCHO_DE_PARTE_IBD = 190


def texto_de_foto(pieza, foto):
    """Referencia a la foto de la etiqueta (con QR) de una pieza, o por que no la hay."""
    if foto is None:
        return SIN_FOTO[pieza]
    return f"Foto de la etiqueta con QR ({ORDEN_DE_COMPRA}):\n{CARPETA_DE_FOTOS}/{foto}"


def _bloque_del_nodo(identificador):
    return next(nodo.bloque for nodo in NODOS_OFICIALES if nodo.id == identificador)


# bloque de la arquitectura oficial -> RF y RNF que satisface. Los RF siguen la columna
# "Bloque que lo satisface" de docs/00-idea-principal.md (seccion 8.2); los RNF, el bloque al
# que restringen. Los bloques de septiembre ya no satisfacen nada: describen la propuesta vieja.
TRAZABILIDAD = {
    _bloque_del_nodo(1): ["RF-02"],
    _bloque_del_nodo(2): ["RF-02"],
    _bloque_del_nodo(4): ["RF-02"],
    _bloque_del_nodo(7): ["RF-02"],
    _bloque_del_nodo(5): ["RF-03"],
    _bloque_del_nodo(6): ["RF-03", "RF-04", "RNF-04"],
    GATEWAY: ["RF-05"],
    RED_WIFI: ["RF-05", "RNF-05", "RNF-08"],
    INFLUXDB: ["RF-06"],
    API_DEL_SERVICIO: ["RF-06"],
    TABLERO: ["RF-07"],
    EVALUADOR_DE_RA: ["RF-08", "RF-13"],
    MOTOR_CAUSAL: ["RF-08"],
    COPILOTO: ["RF-09"],
    CONSUMO_FANTASMA: ["RF-01", "RF-10", "RF-12"],
    SIMULADOR: ["RF-11"],
    LAPTOP: ["RNF-06"],
}


# --- Requisitos de alto nivel RA-01..10 (EC3) ------------------------------
# La fuente es config/requisitos_ra.yaml y grafos/. Los lee exportar_ra.py con el Python del
# servicio (tiene PyYAML y los cargadores de `gemelo`) y se los pasa a este script como JSON.
RAIZ_DEL_REPO = Path(__file__).resolve().parents[2]
PYTHON_DEL_SERVICIO = Path(os.environ.get(
    "CAMPUSTWIN_PYTHON", RAIZ_DEL_REPO / "demo" / "servidor" / ".venv" / "bin" / "python"))
EXPORTADOR_DE_RA = Path(__file__).with_name("exportar_ra.py")
TIEMPO_MAXIMO_DE_EXPORTACION_S = 60
# El interprete de Gaphor es un ejecutable congelado: sus variables de Python no deben
# llegar al del servicio, o este busca su biblioteca estandar en el lugar equivocado.
VARIABLES_DEL_INTERPRETE_DE_GAPHOR = ("PYTHONHOME", "PYTHONPATH", "PYTHONSAFEPATH")

CARPETA_DE_GRAFOS = "grafos"
CARPETA_DE_FIGURAS = "grafos/figuras"
FORMATOS_DE_FIGURA = ("svg", "png")
PAQUETE_DIAGNOSTICO = "05 Diagnóstico causal"
ANCHO_DE_NOTA_DE_DIAGNOSTICO = 480
HUECO_ENTRE_RA_Y_NOTA = 110.0

# Que caso de prueba verifica cada RA. Sale de lo que cubre cada CP en
# docs/00-idea-principal.md (seccion 8.6) y docs/pruebas/README.md: CP-10 prueba con datos
# simulados la evaluacion y el diagnostico de todos los RA; el resto, el sensor o la funcion
# que cada RA usa. RA-05 no tiene ensayo con hardware: el MQ-2 no figura en ningun CP fisico.
VERIFICACION_DE_RA = {
    "RA-01": ["CP-07", "CP-10"],
    "RA-02": ["CP-07", "CP-10"],
    "RA-03": ["CP-07", "CP-10"],
    "RA-04": ["CP-07", "CP-10"],
    "RA-05": ["CP-10"],
    "RA-06": ["CP-02", "CP-10"],
    "RA-07": ["CP-07", "CP-10"],
    "RA-08": ["CP-06", "CP-10"],
    "RA-09": ["CP-08", "CP-10"],
    "RA-10": ["CP-03", "CP-15", "CP-10"],
}

# (clave de requisitos_ra.yaml, como se lee en el texto, si lleva la unidad del RA)
UMBRALES_DE_RA = [
    ("nominal", "nominal", True),
    ("alerta", "alerta", True),
    ("critico", "crítico", True),
    ("alerta_fraccion", "alerta en fracción del aforo", False),
    ("critico_fraccion", "crítico en fracción del aforo", False),
    ("alerta_min", "alerta [min]", False),
    ("critico_min", "crítico [min]", False),
    ("histeresis", "histéresis", True),
    ("sostenido_s", "sostenido [s]", False),
    ("periodos_tolerados", "periodos tolerados", False),
    ("minimo_tolerancia_s", "tolerancia mínima [s]", False),
    ("fraccion_para_gateway", "fracción caída para sospechar del Gateway", False),
]


def leer_requisitos_ra():
    """RA-01..10 tal como los carga el servicio, con el resumen de su grafo."""
    entorno = {clave: valor for clave, valor in os.environ.items()
               if clave not in VARIABLES_DEL_INTERPRETE_DE_GAPHOR}
    try:
        resultado = subprocess.run(
            [str(PYTHON_DEL_SERVICIO), str(EXPORTADOR_DE_RA)], capture_output=True, text=True,
            timeout=TIEMPO_MAXIMO_DE_EXPORTACION_S, check=True, env=entorno)
    except FileNotFoundError as error:
        raise RuntimeError(
            f"No está el Python del servicio en {PYTHON_DEL_SERVICIO}: crea el venv de "
            "demo/servidor (demo/README.md) o fija CAMPUSTWIN_PYTHON") from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"exportar_ra.py falló:\n{error.stderr}") from error
    return json.loads(resultado.stdout)


def _numero(valor):
    """20.0 -> "20", 0.75 -> "0.75": los umbrales se leen como en el YAML."""
    return f"{valor:g}" if isinstance(valor, (int, float)) else str(valor)


def _valor_de_umbral(valor):
    if isinstance(valor, list):
        return "–".join(_numero(v) for v in valor)
    return _numero(valor)


def texto_de_ra(requisito):
    """Texto del requisito: magnitud, nodos, umbrales y la norma que los respalda."""
    unidad = requisito.get("unidad", "")
    nodos = ", ".join(str(n) for n in requisito["nodos"])
    umbrales = [
        f"{etiqueta} {_valor_de_umbral(requisito[clave])}"
        + (f" {unidad}" if con_unidad and unidad else "")
        for clave, etiqueta, con_unidad in UMBRALES_DE_RA if clave in requisito
    ]
    lineas = [
        f"Magnitud: {requisito['campo']} (nodos {nodos}); evaluador {requisito['evaluador']}.",
        ("Umbrales: " + "; ".join(umbrales) + ".") if umbrales
        else "Sin umbral numérico: la condición sale de la lógica del evaluador.",
        f"Fuente ({requisito['origen']}): {requisito['norma']}",
    ]
    return "\n".join(lineas)


def rutas_de_figura(requisito):
    return [f"{CARPETA_DE_FIGURAS}/{requisito['grafo']}.{formato}" for formato in FORMATOS_DE_FIGURA]


def texto_de_diagnostico(requisito):
    """Nota del paquete 05: el grafo causal del RA resumido y donde estan su YAML y su figura."""
    resumen = requisito["resumen_del_grafo"]
    return "\n".join([
        f"Grafo causal: {resumen['titulo']}",
        "Causas raíz: " + "; ".join(resumen["causas"]) + ".",
        "Efectos: " + "; ".join(resumen["efectos"]) + ".",
        "",
        "Figura: " + " y ".join(rutas_de_figura(requisito)),
        f"Grafo: {CARPETA_DE_GRAFOS}/{requisito['grafo']}.yaml",
        "Lo evalúa el motor causal SymCure del servicio (demo/servidor/gemelo/razonamiento.py) "
        "cuando el RA pasa a alerta o crítico.",
    ])


# -- 04 Comportamiento ---------------------------------------------------------------------
PAQUETE_COMPORTAMIENTO = "04 Comportamiento"
# Actividades: una grilla de celdas. La columna es ancha porque entre dos acciones lado a lado
# cabe la etiqueta de la guarda (por ejemplo "[inválida]").
PASO_DE_COLUMNA = 300
PASO_DE_FILA = 105
ANCHO_DE_ACCION = 210
ALTO_DE_ACCION = 80
MARGEN_EXTREMO_DEL_CARRIL = 40  # holgura a izquierda y derecha de los carriles de los extremos
MARGEN_SUPERIOR_DEL_CARRIL = 70  # el titulo del carril ocupa la parte de arriba
MARGEN_INFERIOR_DEL_CARRIL = 70
# Estados: la grilla es mas alta porque entre dos filas caben las transiciones en pares.
PASO_DE_COLUMNA_DE_ESTADOS = 300
PASO_DE_FILA_DE_ESTADOS = 200
ANCHO_DE_ESTADO = 180
ALTO_DE_ESTADO = 80
RELLENO_DEL_ESTADO_COMPUESTO = 40
ENCABEZADO_DEL_ESTADO_COMPUESTO = 40
HOLGURA_DE_ALINEACION = 10  # una linea horizontal no se acerca mas que esto al borde de la caja
# Casos de uso: tres columnas (escenarios, casos compartidos, escenarios) dentro de la frontera.
CENTRO_DE_LA_COLUMNA_DE_CASOS = (420.0, 790.0, 1160.0)
ANCHO_DEL_ESCENARIO = 250
ANCHO_DEL_CASO_COMPARTIDO = 280
ALTO_DEL_CASO = 70
PASO_DE_FILA_DE_CASOS = 120
X_DE_LOS_ACTORES = (40.0, 1540.0)
MARGEN_DE_LA_FRONTERA = 60
ANCHO_DE_NOTA_DE_COMPORTAMIENTO = 900
SEPARACION_DE_LA_NOTA = 50


class ModeloCampusTwin:
    """Arma el modelo en memoria y lo guarda en formato .gaphor."""

    def __init__(self):
        self.factory = ElementFactory()
        self.factory.create(StyleSheet)
        self.autolayout = AutoLayout()
        self.requisitos = {}
        self.bloques = {}
        self.tipos = {}
        self.casos = {}
        self.figuras_de_ra = {}  # RA -> rutas de su figura, para comprobar que existan
        self._items = {}
        self._siguiente_posicion = {}

    # -- elementos del modelo ------------------------------------------------
    def paquete(self, nombre, padre=None):
        paquete = self.factory.create(Package)
        paquete.name = nombre
        if padre is not None:
            paquete.nestingPackage = padre
        return paquete

    def diagrama(self, clase, nombre, paquete):
        diagrama = self.factory.create(clase)
        diagrama.name = nombre
        paquete.ownedDiagram = diagrama
        return diagrama

    def requisito(self, identificador, nombre, texto, paquete):
        requisito = self.factory.create(sysml.Requirement)
        requisito.name = nombre
        requisito.externalId = identificador
        requisito.text = texto
        requisito.owningPackage = paquete
        self.requisitos[identificador] = requisito
        return requisito

    def caso_de_prueba(self, identificador, nombre, paquete):
        # SysML modela el caso de prueba como un comportamiento; Gaphor no dibuja
        # sysml.TestCase, asi que se usa una Activity con ese mismo rol.
        caso = self.factory.create(Activity)
        caso.name = f"{identificador} {nombre}"
        caso.owningPackage = paquete
        self.casos[identificador] = caso
        return caso

    def bloque(self, nombre, paquete, abstracto=False):
        if nombre in self.bloques:
            return self.bloques[nombre]
        bloque = self.factory.create(sysml.Block)
        bloque.name = nombre
        bloque.isAbstract = abstracto
        bloque.owningPackage = paquete
        self.bloques[nombre] = bloque
        return bloque

    def tipo_de_valor(self, nombre, paquete):
        tipo = self.factory.create(sysml.ValueType)
        tipo.name = nombre
        tipo.owningPackage = paquete
        self.tipos[nombre] = tipo
        return tipo

    def propiedad_de_valor(self, bloque, nombre, tipo):
        propiedad = self.factory.create(Property)
        propiedad.name = nombre
        propiedad.type = tipo
        bloque.ownedAttribute = propiedad
        return propiedad

    def nota(self, cuerpo):
        comentario = self.factory.create(Comment)
        comentario.body = cuerpo
        return comentario

    def parte(self, contexto, nombre, tipo):
        """Propiedad de parte de un bloque: lo que el IBD dibuja como `nombre: Tipo`."""
        parte = self.factory.create(Property)
        parte.name = nombre
        parte.type = tipo
        parte.aggregation = "composite"
        contexto.ownedAttribute = parte
        return parte

    # -- presentaciones ------------------------------------------------------
    def item(self, elemento, diagrama, mostrar_atributos=None, ancho=None, mostrar_texto=True):
        """Coloca un elemento en un diagrama (una sola vez por diagrama).

        `mostrar_atributos` fuerza que el compartimento de valores se vea o no.
        Sirve para la vista general, donde los doce sensores con sus magnitudes
        harian el diagrama ilegible. `ancho` reemplaza el ancho por defecto, y
        `mostrar_texto=False` deja un requisito solo con su id y su nombre.
        """
        clave = (diagrama.id, elemento.id)
        if clave not in self._items:
            indice = self._siguiente_posicion.get(diagrama.id, 0)
            self._siguiente_posicion[diagrama.id] = indice + 1
            item = drop(elemento, diagrama, (indice % 5) * GRID_STEP, (indice // 5) * GRID_STEP)
            if item is None:
                raise RuntimeError(f"Gaphor no tiene item de diagrama para {elemento}")
            if hasattr(item, "show_attributes"):
                # el compartimento solo aporta si el bloque declara propiedades de valor
                item.show_attributes = (
                    bool(getattr(elemento, "ownedAttribute", ()))
                    if mostrar_atributos is None
                    else mostrar_atributos
                )
                if item.show_attributes:
                    item.width = ANCHO_DE_BLOQUE_CON_VALORES
            if isinstance(elemento, sysml.Requirement):
                item.width = REQUIREMENT_WIDTH
                item.show_text = mostrar_texto
            elif isinstance(elemento, Comment):
                item.width = COMMENT_WIDTH
            if ancho is not None:
                item.width = ancho
            self._items[clave] = item
        return self._items[clave]

    @staticmethod
    def _centro_derecho(item):
        return item.matrix[4] + item.width, item.matrix[5] + item.height / 2

    @staticmethod
    def _centro_izquierdo(item):
        return item.matrix[4], item.matrix[5] + item.height / 2

    @staticmethod
    def _centro_superior(item):
        return item.matrix[4] + item.width / 2, item.matrix[5]

    @staticmethod
    def _inferior_izquierdo(item):
        return item.matrix[4] + INDENTACION_DE_SENSORES / 2, item.matrix[5] + item.height

    @staticmethod
    def _centro_inferior(item):
        return item.matrix[4] + item.width / 2, item.matrix[5] + item.height

    def _linea(self, clase, diagrama, item_cabeza, item_cola, anclar=None):
        linea = diagrama.create(clase)
        cabeza, cola = linea.handles()[0], linea.handles()[-1]
        # El conector engancha la linea al puerto mas cercano al handle, y un handle
        # recien creado esta en el origen: sin esto, todas las lineas se pegan al
        # borde izquierdo y cruzan por encima de las cajas.
        if anclar == "horizontal":
            cabeza.pos = self._centro_derecho(item_cabeza)
            cola.pos = self._centro_izquierdo(item_cola)
        elif anclar == "columna":
            # De la base del nodo al costado del sensor, bajando por el pasillo.
            cabeza.pos = self._inferior_izquierdo(item_cabeza)
            cola.pos = self._centro_izquierdo(item_cola)
        elif anclar == "vertical":
            cabeza.pos, cola.pos = self._anclas_verticales(item_cabeza, item_cola)
        elif anclar == "enfrentadas":
            cabeza.pos, cola.pos = self._anclas_enfrentadas(item_cabeza, item_cola)
        elif isinstance(anclar, tuple):
            cabeza.pos, cola.pos = anclar
        connect(linea, cabeza, item_cabeza)
        connect(linea, cola, item_cola)
        # La linea de una nota no tiene elemento propio: anota el elemento al conectarse.
        if linea.subject is None and not isinstance(linea, CommentLineItem):
            raise RuntimeError(f"No se pudo crear la relacion {clase.__name__}")
        return linea

    def _anclas_verticales(self, item_a, item_b):
        """El lado por el que sale la linea depende de quien quede arriba."""
        if item_a.matrix[5] < item_b.matrix[5]:
            return self._centro_inferior(item_a), self._centro_superior(item_b)
        return self._centro_superior(item_a), self._centro_inferior(item_b)

    @staticmethod
    def _medio_de_la_franja_comun(inicio_a, largo_a, inicio_b, largo_b):
        """Medio del tramo que dos cajas comparten en un eje, o None si no se solapan."""
        desde = max(inicio_a, inicio_b)
        hasta = min(inicio_a + largo_a, inicio_b + largo_b)
        return (desde + hasta) / 2 if desde < hasta else None

    def _anclas_enfrentadas(self, item_a, item_b):
        """Une los lados que se miran: los laterales si estan lado a lado, si no los de arriba y abajo.

        Si las cajas comparten una franja, la linea sale recta por el medio de esa franja:
        asi varias lineas hacia una caja grande no convergen en un punto, y sus etiquetas
        o sus rombos no se enciman.
        """
        xa, ya, xb, yb = item_a.matrix[4], item_a.matrix[5], item_b.matrix[4], item_b.matrix[5]
        dx = (xb + item_b.width / 2) - (xa + item_a.width / 2)
        dy = (yb + item_b.height / 2) - (ya + item_a.height / 2)
        x = self._medio_de_la_franja_comun(xa, item_a.width, xb, item_b.width)
        y = self._medio_de_la_franja_comun(ya, item_a.height, yb, item_b.height)
        # Manda el eje en que se solapan; sin solape (o con los dos), el de mayor distancia.
        vertical = x is not None if (x is None) != (y is None) else abs(dy) > abs(dx)
        if vertical:
            if x is None:
                return self._anclas_verticales(item_a, item_b)
            if dy > 0:
                return (x, ya + item_a.height), (x, yb)
            return (x, ya), (x, yb + item_b.height)
        y_a, y_b = (y, y) if y is not None else (ya + item_a.height / 2, yb + item_b.height / 2)
        if dx > 0:
            return (xa + item_a.width, y_a), (xb, y_b)
        return (xa, y_a), (xb + item_b.width, y_b)

    # -- relaciones ----------------------------------------------------------
    # La direccion de cada relacion se comprueba en verificar(): la cabeza es el
    # extremo del que cuelga la semantica (origen de la derivacion, requisito
    # satisfecho o verificado, elemento especifico de la generalizacion).
    def generalizacion(self, diagrama, especifico, general, anclar=None):
        return self._linea(GeneralizationItem, diagrama,
                           self.item(especifico, diagrama), self.item(general, diagrama),
                           anclar=anclar)

    def composicion(self, diagrama, todo, parte, anclar=None):
        """Asociacion compuesta: el rombo queda del lado del todo."""
        linea = self._linea(AssociationItem, diagrama,
                            self.item(todo, diagrama), self.item(parte, diagrama),
                            anclar=anclar)
        linea.tail_subject.aggregation = "composite"
        return linea

    def asociacion(self, diagrama, origen, destino, nombre=None):
        linea = self._linea(AssociationItem, diagrama,
                            self.item(origen, diagrama), self.item(destino, diagrama))
        if nombre is not None:
            linea.subject.name = nombre
        return linea

    def anclar_nota(self, diagrama, nota, elemento):
        """Linea punteada de una nota al elemento que comenta."""
        return self._linea(CommentLineItem, diagrama,
                           self.item(nota, diagrama), self.item(elemento, diagrama),
                           anclar="enfrentadas")

    def flujo(self, diagrama, origen, destino, conector, item_nombre, item_tipo):
        """Conector de IBD entre dos partes con el flujo de item que lo recorre.

        El nombre del conector dice por donde viaja el dato (I²C, ESP-NOW, MQTT...),
        y el flujo de item, que viaja y en que sentido: Gaphor dibuja la flecha.
        """
        linea = self._linea(ConnectorItem, diagrama,
                            self.item(origen, diagrama), self.item(destino, diagrama),
                            anclar="enfrentadas")
        linea.subject.name = conector
        propiedad = self.factory.create(Property)
        propiedad.name = item_nombre
        propiedad.type = item_tipo
        flujo = self.factory.create(sysml.ItemFlow)
        flujo.realizingConnector = linea.subject
        flujo.informationSource = origen
        flujo.informationTarget = destino
        flujo.itemProperty = propiedad
        flujo.conveyed = item_tipo
        return linea

    # -- diagramas -----------------------------------------------------------
    def _medir(self, diagrama):
        """Fija el alto y ancho real de cada caja segun su texto.

        Solo el pase de autolayout mide el texto: sin el, todas las cajas
        conservan el alto por defecto y se solapan al apilarlas.
        """
        items = list(diagrama.get_all_items())
        for item in items:
            if hasattr(item, "update_shapes"):
                item.update_shapes()
        self.autolayout.layout(diagrama)
        diagrama.update_now(items)

    @staticmethod
    def _mover(item, x, y):
        """Lleva un item a una posicion absoluta (su matriz es una traslacion pura)."""
        item.matrix.translate(x - item.matrix[4], y - item.matrix[5])

    def diagrama_jerarquico(self, clase, nombre, paquete, dibujar, nota=None):
        """Diagrama acomodado por graphviz: sirve para arboles de bloques."""
        diagrama = self.diagrama(clase, nombre, paquete)
        dibujar(diagrama)
        if nota is not None:
            self.item(self.nota(nota), diagrama)
        self._medir(diagrama)
        return diagrama

    def diagrama_bipartito(self, clase, nombre, paquete, clase_linea, pares, nota=None):
        """Diagrama de dos columnas: origenes a la izquierda, relacionados a la derecha.

        Graphviz estira estos diagramas en una fila de varios miles de pixeles, asi
        que se acomodan a mano. Las lineas se trazan al final, cuando cada caja ya
        esta en su sitio, para que se conecten por el lado que corresponde.
        """
        diagrama = self.diagrama(clase, nombre, paquete)
        for izquierda, derecha in pares:
            self.item(izquierda, diagrama)
            self.item(derecha, diagrama)
        item_nota = self.item(self.nota(nota), diagrama) if nota is not None else None
        self._medir(diagrama)

        grupos = {}
        for izquierda, derecha in pares:
            grupos.setdefault(izquierda, [])
            if derecha not in grupos[izquierda]:
                grupos[izquierda].append(derecha)
        colocados = set()
        y = 0.0
        for izquierda, derechas in grupos.items():
            item_izquierda = self.item(izquierda, diagrama)
            pendientes = [d for d in derechas if d.id not in colocados]
            inicio = y
            for derecha in pendientes:
                item_derecha = self.item(derecha, diagrama)
                self._mover(item_derecha, COLUMNA_DERECHA_X, y)
                colocados.add(derecha.id)
                y += item_derecha.height + SEPARACION_VERTICAL
            if pendientes:
                alto_del_grupo = y - SEPARACION_VERTICAL - inicio
                if item_izquierda.height > alto_del_grupo:
                    # El origen es mas alto que su grupo (un requisito largo con un solo
                    # caso de prueba): el grupo se centra en el y la fila ocupa su alto.
                    desplazamiento = (item_izquierda.height - alto_del_grupo) / 2
                    for derecha in pendientes:
                        self.item(derecha, diagrama).matrix.translate(0, desplazamiento)
                    y = inicio + item_izquierda.height + SEPARACION_VERTICAL
                centro = (inicio + y - SEPARACION_VERTICAL) / 2
                self._mover(item_izquierda, COLUMNA_IZQUIERDA_X, centro - item_izquierda.height / 2)
            else:
                self._mover(item_izquierda, COLUMNA_IZQUIERDA_X, y)
                y += item_izquierda.height + SEPARACION_VERTICAL
            y += SEPARACION_ENTRE_GRUPOS
        if item_nota is not None:
            self._mover(item_nota, COLUMNA_IZQUIERDA_X, y)

        for izquierda, derecha in pares:
            self._linea(clase_linea, diagrama,
                        self.item(izquierda, diagrama), self.item(derecha, diagrama),
                        anclar="horizontal")
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    def diagrama_de_instrumentacion(self, nombre, paquete, nodo_base, nota=None):
        """Cada nodo con su instrumentacion en una columna debajo.

        Graphviz pone los doce sensores en una sola fila; como cada caja muestra
        su magnitud y su valor, las cajas crecen, se solapan y el texto se corta.
        Aqui se acomodan a mano: una columna por nodo, y dentro de la columna los
        sensores apilados.
        """
        diagrama = self.diagrama(sysml.BlockDefinitionDiagram, nombre, paquete)
        item_subsistema = self.item(self.bloques["Subsistema de Sensado"], diagrama)
        item_base = self.item(nodo_base, diagrama)
        columnas = [
            (
                self.item(self.bloques[nodo], diagrama),
                [self.item(self.bloques[sensor], diagrama) for sensor in sensores],
            )
            for nodo, sensores in NODOS.items()
        ]
        item_nota = self.item(self.nota(nota), diagrama) if nota is not None else None

        items = [item_subsistema, item_base]
        for item_nodo, items_sensores in columnas:
            items.append(item_nodo)
            items.extend(items_sensores)
        if item_nota is not None:
            items.append(item_nota)

        # Primero medir: solo el pase de autolayout ajusta el alto y el ancho de
        # cada caja a su texto. Despues se recolocan a mano.
        for item in items:
            if hasattr(item, "update_shapes"):
                item.update_shapes()
        self.autolayout.layout(diagrama)
        diagrama.update_now(items)

        anchos = [
            max([item_nodo.width] + [INDENTACION_DE_SENSORES + i.width for i in items_sensores])
            for item_nodo, items_sensores in columnas
        ]
        ancho_total = sum(anchos) + SEPARACION_ENTRE_COLUMNAS * (len(anchos) - 1)

        y = 0.0
        x_subsistema = (ancho_total - item_subsistema.width) / 2
        if item_nota is not None:
            self._mover(item_nota, 0, 0)
            # La nota comparte fila con el bloque del subsistema si cabe; si no,
            # se queda encima y todo lo demas baja.
            if item_nota.width + SEPARACION_ENTRE_COLUMNAS > x_subsistema:
                y = item_nota.height + SEPARACION_ENTRE_FILAS
        self._mover(item_subsistema, x_subsistema, y)
        y += item_subsistema.height + SEPARACION_ENTRE_FILAS
        self._mover(item_base, (ancho_total - item_base.width) / 2, y)
        y += item_base.height + SEPARACION_ENTRE_FILAS

        alto_de_los_nodos = max(item_nodo.height for item_nodo, _ in columnas)
        x = 0.0
        for ancho, (item_nodo, items_sensores) in zip(anchos, columnas):
            self._mover(item_nodo, x + (ancho - item_nodo.width) / 2, y)
            y_sensor = y + alto_de_los_nodos + SEPARACION_ENTRE_FILAS
            for item_sensor in items_sensores:
                self._mover(item_sensor, x + INDENTACION_DE_SENSORES, y_sensor)
                y_sensor += item_sensor.height + SEPARACION_ENTRE_SENSORES
            x += ancho + SEPARACION_ENTRE_COLUMNAS

        # Las lineas se trazan al final, con cada caja ya en su sitio, para que
        # salgan por el borde que toca.
        self.composicion(diagrama, self.bloques["Subsistema de Sensado"], nodo_base,
                         anclar="vertical")
        for nodo, sensores in NODOS.items():
            self.generalizacion(diagrama, self.bloques[nodo], nodo_base, anclar="vertical")
            for sensor in sensores:
                self.composicion(diagrama, self.bloques[nodo], self.bloques[sensor],
                                 anclar="columna")
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    def _centrar_fila(self, items, ancho_total, y):
        """Pone una fila de cajas centrada en `ancho_total` y devuelve su alto."""
        ancho_fila = (sum(item.width for item in items)
                      + SEPARACION_ENTRE_COLUMNAS * (len(items) - 1))
        x = (ancho_total - ancho_fila) / 2
        for item in items:
            self._mover(item, x, y)
            x += item.width + SEPARACION_ENTRE_COLUMNAS
        return max(item.height for item in items)

    @staticmethod
    def _punto_repartido(item, lado, orden, total):
        """El punto `orden` de `total` repartidos a lo largo del lado izquierdo o derecho."""
        x = item.matrix[4] + (item.width if lado == "derecho" else 0)
        return x, item.matrix[5] + item.height * (orden + 1) / (total + 1)

    def diagrama_de_ra(self, nombre, paquete, clase_linea, ras, relaciones, ra_es_cabeza,
                       nota=None):
        """Los RA en la columna del medio y lo que se relaciona con ellos a los costados.

        `relaciones` es {elemento: [RA...]}. El elemento que se relaciona con todos los RA
        (el evaluador, CP-10) va a la derecha, tan alto como la columna, con una linea recta
        por RA. Los demas van a la izquierda, cada uno a la altura media de sus RA, y sus
        lineas se reparten a lo largo de cada lado: con muchos a muchos, el bipartito
        las junta todas en un punto y no se lee.
        """
        diagrama = self.diagrama(sysml.RequirementDiagram, nombre, paquete)
        comunes = [e for e, lista in relaciones.items() if set(lista) == set(ras)]
        if len(comunes) > 1:
            raise RuntimeError(f"{nombre}: más de un elemento se relaciona con todos los RA")
        comun = comunes[0] if comunes else None
        laterales = {e: [r for r in ras if r in lista]
                     for e, lista in relaciones.items() if e is not comun}
        items_ra = {r: self.item(r, diagrama, mostrar_texto=False) for r in ras}
        items_lateral = {e: self.item(e, diagrama, mostrar_texto=False) for e in laterales}
        item_comun = self.item(comun, diagrama, mostrar_texto=False) if comun else None
        item_nota = self.item(self.nota(nota), diagrama) if nota is not None else None
        self._medir(diagrama)

        x_ra = max(i.width for i in items_lateral.values()) + HUECO_ENTRE_COLUMNAS_IBD
        y = 0.0
        for item in items_ra.values():
            self._mover(item, x_ra, y)
            y += item.height + SEPARACION_VERTICAL
        alto = y - SEPARACION_VERTICAL

        def altura_media(elemento):
            centros = [items_ra[r].matrix[5] + items_ra[r].height / 2 for r in laterales[elemento]]
            return sum(centros) / len(centros)

        y_libre = 0.0
        for elemento in sorted(laterales, key=altura_media):
            item = items_lateral[elemento]
            y_elemento = max(altura_media(elemento) - item.height / 2, y_libre)
            self._mover(item, 0, y_elemento)
            y_libre = y_elemento + item.height + SEPARACION_VERTICAL
        ancho_ra = max(i.width for i in items_ra.values())
        if item_comun is not None:
            item_comun.height = alto
            self._mover(item_comun, x_ra + ancho_ra + HUECO_ENTRE_COLUMNAS_IBD, 0)
        if item_nota is not None:
            self._mover(item_nota, 0, max(alto, y_libre) + SEPARACION_ENTRE_GRUPOS)

        def trazar(item_ra, item_otro, punto_ra, punto_otro):
            if ra_es_cabeza:
                self._linea(clase_linea, diagrama, item_ra, item_otro, anclar=(punto_ra, punto_otro))
            else:
                self._linea(clase_linea, diagrama, item_otro, item_ra, anclar=(punto_otro, punto_ra))

        # Lado izquierdo de cada RA: quien le llega, ordenado de arriba abajo para no cruzarse.
        llegadas = {r: sorted((e for e in laterales if r in laterales[e]),
                              key=lambda e: items_lateral[e].matrix[5]) for r in ras}
        for elemento, lista in laterales.items():
            for orden, r in enumerate(lista):
                trazar(items_ra[r], items_lateral[elemento],
                       self._punto_repartido(items_ra[r], "izquierdo",
                                             llegadas[r].index(elemento), len(llegadas[r])),
                       self._punto_repartido(items_lateral[elemento], "derecho",
                                             orden, len(lista)))
        if item_comun is not None:
            for item in items_ra.values():
                y_medio = item.matrix[5] + item.height / 2
                trazar(item, item_comun, (item.matrix[4] + item.width, y_medio),
                       (item_comun.matrix[4], y_medio))
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    def diagrama_de_diagnostico(self, nombre, paquete, requisito, texto):
        """El RA y, a su lado, la nota con su grafo causal y la ruta de la figura."""
        diagrama = self.diagrama(sysml.RequirementDiagram, nombre, paquete)
        item_requisito = self.item(requisito, diagrama)
        nota = self.nota(texto)
        item_nota = self.item(nota, diagrama, ancho=ANCHO_DE_NOTA_DE_DIAGNOSTICO)
        self._medir(diagrama)
        self._mover(item_requisito, 0, 0)
        self._mover(item_nota, item_requisito.width + HUECO_ENTRE_RA_Y_NOTA, 0)
        self.anclar_nota(diagrama, nota, requisito)
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    def diagrama_de_cajas(self, nombre, paquete, nota):
        """Las siete cajas: partes comunes arriba, y por nodo su sensor y la foto debajo.

        Graphviz pondria los siete sensores (con sus campos) en una fila sin orden;
        aqui cada nodo es una columna, para leer de arriba abajo caja, sensor y foto.
        """
        diagrama = self.diagrama(sysml.BlockDefinitionDiagram, nombre, paquete)
        b = self.bloques
        item_nota = self.item(self.nota(nota), diagrama)
        nota_esp32 = self.nota(texto_de_foto(ESP32_DEVKIT, FOTO_DEL_ESP32))
        fila_de_partes = [self.item(nota_esp32, diagrama, ancho=ANCHO_DE_SENSOR_OFICIAL)]
        fila_de_partes += [self.item(b[parte], diagrama, mostrar_atributos=False)
                           for parte in PARTES_DE_LA_CAJA]
        item_caja = self.item(b[CAJA_DE_NODO], diagrama, mostrar_atributos=False)
        columnas = []
        for nodo in NODOS_OFICIALES:
            item_nodo = self.item(b[nodo.bloque], diagrama, mostrar_atributos=False)
            item_sensor = self.item(b[nodo.sensor], diagrama, mostrar_atributos=True,
                                    ancho=ANCHO_DE_SENSOR_OFICIAL)
            nota_foto = self.nota(texto_de_foto(nodo.sensor, nodo.foto))
            item_foto = self.item(nota_foto, diagrama, ancho=ANCHO_DE_SENSOR_OFICIAL)
            columnas.append((nodo, item_nodo, item_sensor, item_foto, nota_foto))
        self._medir(diagrama)

        ancho_columna = max(max(i.width for i in fila[1:4]) for fila in columnas)
        ancho_total = (ancho_columna * len(columnas)
                       + SEPARACION_ENTRE_COLUMNAS * (len(columnas) - 1))
        self._mover(item_nota, 0, 0)
        y = item_nota.height + SEPARACION_ENTRE_FILAS
        y += self._centrar_fila(fila_de_partes, ancho_total, y) + SEPARACION_ENTRE_FILAS
        # La caja abarca la fila de sus partes: cada composicion baja recta y los rombos
        # no se apilan en un solo punto.
        primera, ultima = fila_de_partes[1], fila_de_partes[-1]
        item_caja.width = ultima.matrix[4] + ultima.width - primera.matrix[4]
        self._mover(item_caja, primera.matrix[4], y)
        y += item_caja.height + SEPARACION_ENTRE_FILAS
        for fila in (1, 2, 3):
            alto = 0.0
            for indice, columna in enumerate(columnas):
                item = columna[fila]
                x = indice * (ancho_columna + SEPARACION_ENTRE_COLUMNAS)
                self._mover(item, x + (ancho_columna - item.width) / 2, y)
                alto = max(alto, item.height)
            y += alto + SEPARACION_ENTRE_FILAS

        for parte in PARTES_DE_LA_CAJA:
            self.composicion(diagrama, b[CAJA_DE_NODO], b[parte], anclar="enfrentadas")
        self.anclar_nota(diagrama, nota_esp32, b[ESP32_DEVKIT])
        for nodo, _, _, _, nota_foto in columnas:
            self.generalizacion(diagrama, b[nodo.bloque], b[CAJA_DE_NODO], anclar="vertical")
            self.composicion(diagrama, b[nodo.bloque], b[nodo.sensor], anclar="vertical")
            self.anclar_nota(diagrama, nota_foto, b[nodo.sensor])
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    def diagrama_de_flujo(self, nombre, nota):
        """IBD del flujo de datos, de izquierda a derecha como viaja el dato.

        Columnas: sensores, ESP32 de cada caja, Gateway, Mosquitto (con el simulador
        debajo), Telegraf, InfluxDB con el servicio debajo, y a la derecha Grafana y
        los clientes del servicio. Graphviz no respeta ese orden, asi que va a mano.
        """
        b = self.bloques
        contexto = b[CONTEXTO_DEL_FLUJO]
        diagrama = self.factory.create(sysml.InternalBlockDiagram)
        diagrama.name = nombre
        # Del bloque cuelga el diagrama: el marco dice "ibd [block] Cadena de datos".
        contexto.ownedDiagram = diagrama

        sensores = [self.parte(contexto, f"sensor{n.id}", b[n.sensor]) for n in NODOS_OFICIALES]
        placas = [self.parte(contexto, f"nodo{n.id}", b[ESP32_DEVKIT]) for n in NODOS_OFICIALES]
        gateway = self.parte(contexto, "gateway", b[GATEWAY])
        broker = self.parte(contexto, "broker", b[MOSQUITTO])
        simulador = self.parte(contexto, "simulador", b[SIMULADOR])
        telegraf = self.parte(contexto, "telegraf", b[TELEGRAF])
        base = self.parte(contexto, "bd", b[INFLUXDB])
        grafana = self.parte(contexto, "grafana", b[GRAFANA])
        servicio = self.parte(contexto, "servicio", b[SERVICIO_GEMELO])
        clientes = [self.parte(contexto, "tablero", b[TABLERO]),
                    self.parte(contexto, "gaphor", b[GAPHOR_EN_VIVO]),
                    self.parte(contexto, "copiloto", b[COPILOTO])]
        for parte in sensores + placas + [gateway, broker, simulador, telegraf, base,
                                          grafana, servicio] + clientes:
            self.item(parte, diagrama, ancho=ANCHO_DE_PARTE_IBD)
        item_nota = self.item(self.nota(nota), diagrama)
        self._medir(diagrama)

        def it(parte):
            return self.item(parte, diagrama)

        def alto_apilado(partes):
            return (sum(it(parte).height for parte in partes)
                    + SEPARACION_ENTRE_PARTES * (len(partes) - 1))

        def apilar(partes, x, y):
            for parte in partes:
                self._mover(it(parte), x, y)
                y += it(parte).height + SEPARACION_ENTRE_PARTES
            return y - SEPARACION_ENTRE_PARTES

        def centrar_en(parte, x, centro):
            self._mover(it(parte), x, centro - it(parte).height / 2)

        def ancho(partes):
            return max(it(parte).width for parte in partes)

        alto_de_los_nodos = apilar(sensores, 0, 0)
        centro = alto_de_los_nodos / 2
        # El Gateway y el servicio miden lo mismo que la columna que les llega: asi los
        # conectores entran horizontales, cada uno a su altura.
        it(gateway).height = alto_de_los_nodos
        it(servicio).height = alto_apilado(clientes)
        x = ancho(sensores) + HUECO_ENTRE_COLUMNAS_IBD
        apilar(placas, x, 0)
        x += ancho(placas) + HUECO_ENTRE_COLUMNAS_IBD
        centrar_en(gateway, x, centro)
        x += it(gateway).width + HUECO_ENTRE_COLUMNAS_IBD
        centrar_en(broker, x, centro)
        self._mover(it(simulador), x, alto_de_los_nodos - it(simulador).height)
        x += ancho([broker, simulador]) + HUECO_ENTRE_COLUMNAS_IBD
        self._mover(it(telegraf), x, 0)
        x += it(telegraf).width + HUECO_ENTRE_COLUMNAS_IBD
        self._mover(it(base), x, 0)
        centrar_en(servicio, x, centro)
        x += ancho([base, servicio]) + HUECO_ENTRE_COLUMNAS_IBD
        self._mover(it(grafana), x, 0)
        apilar(clientes, x, centro - alto_apilado(clientes) / 2)
        self._mover(item_nota, 0, alto_de_los_nodos + SEPARACION_ENTRE_FILAS)

        for nodo, sensor, placa in zip(NODOS_OFICIALES, sensores, placas):
            self.flujo(diagrama, sensor, placa, nodo.interfaz, "lectura", b[SENAL])
            self.flujo(diagrama, placa, gateway, "ESP-NOW", "paquete", b[PAQUETE_ESPNOW])
        self.flujo(diagrama, gateway, broker, "Wi-Fi / MQTT :1883", "mensaje", b[JSON_GATEWAY])
        self.flujo(diagrama, simulador, broker, "MQTT (grupo sim)", "mensaje", b[JSON_GATEWAY])
        self.flujo(diagrama, broker, telegraf, "MQTT (7 tipos)", "mensaje", b[JSON_GATEWAY])
        self.flujo(diagrama, telegraf, base, "HTTP :8086", "punto", b[PUNTO_INFLUX])
        self.flujo(diagrama, base, grafana, "Flux", "serie", b[SERIE])
        self.flujo(diagrama, broker, servicio, "MQTT (en vivo)", "mensaje", b[JSON_GATEWAY])
        self.flujo(diagrama, base, servicio, "Flux (histórico)", "serie", b[SERIE])
        for cliente, conector in zip(clientes, ["HTTP :8000 (REST + SSE)", "HTTP /api/estado",
                                                "HTTP (pendiente)"]):
            self.flujo(diagrama, servicio, cliente, conector, "estado", b[ESTADO_JSON])
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    # -- comportamiento: geometria de flechas -----------------------------------
    @staticmethod
    def _centrar(item, x, y):
        item.matrix.translate(x - item.width / 2 - item.matrix[4],
                              y - item.height / 2 - item.matrix[5])

    @staticmethod
    def _es_barra(item):
        return isinstance(item, ForkNodeItem)

    @staticmethod
    def _extremos_de_barra(item):
        """(x_izquierdo, x_derecho, y) de una barra de bifurcacion o de reunion."""
        (x0, y), (x1, _) = (item.matrix.transform_point(float(h.pos.x), float(h.pos.y))
                            for h in item.handles()[:2])
        return min(x0, x1), max(x0, x1), y

    def _poner_barra(self, item, x_centro, y, ancho):
        """Barra horizontal de `ancho` centrada en `x_centro`.

        Gaphor guarda una barra de fork o de join solo con su matriz y su largo, y la dibuja
        vertical. Una barra horizontal es esa misma barra girada un cuarto de vuelta: cambiar
        las restricciones de sus asas funciona en memoria, pero se pierde al guardar y abrir.
        """
        item.handles()[1].pos = (0, ancho)
        item.matrix.set(0.0, -1.0, 1.0, 0.0, x_centro - ancho / 2, y)

    def _centro(self, item):
        if self._es_barra(item):
            izquierda, derecha, y = self._extremos_de_barra(item)
            return (izquierda + derecha) / 2, y
        return item.matrix[4] + item.width / 2, item.matrix[5] + item.height / 2

    def _ancla(self, item, lado, referencia):
        """Punto del borde de `item`: en el lado dado, o en el que mira a `referencia`.

        `lado` es "n", "s", "e", "o" o (lado, fraccion a lo largo de ese lado). En una barra,
        el punto cae sobre la barra, a la altura x de la referencia.
        """
        if self._es_barra(item):
            izquierda, derecha, y = self._extremos_de_barra(item)
            return min(max(referencia[0], izquierda), derecha), y
        x, y, ancho, alto = item.matrix[4], item.matrix[5], item.width, item.height
        if lado is None:
            dx, dy = referencia[0] - (x + ancho / 2), referencia[1] - (y + alto / 2)
            horizontal = abs(dx) / ancho > abs(dy) / alto
            lado = (comp.ESTE if dx > 0 else comp.OESTE) if horizontal else (
                comp.SUR if dy > 0 else comp.NORTE)
        nombre, fraccion = lado if isinstance(lado, tuple) else (lado, 0.5)
        return {comp.NORTE: (x + ancho * fraccion, y), comp.SUR: (x + ancho * fraccion, y + alto),
                comp.OESTE: (x, y + alto * fraccion),
                comp.ESTE: (x + ancho, y + alto * fraccion)}[nombre]

    def _anclas_de_flecha(self, origen, destino, sale, entra, via):
        """Puntos de salida y de llegada de una flecha, con los lados pedidos o los que se miran."""
        hay_barra = self._es_barra(origen) or self._es_barra(destino)
        if sale is None and entra is None and not via and not hay_barra:
            return self._anclas_enfrentadas(origen, destino)
        if self._es_barra(origen):
            punto_entra = self._ancla(destino, entra or self._lado_hacia_la_barra(destino, origen),
                                      self._centro(origen))
            return self._ancla(origen, None, punto_entra), punto_entra
        referencia_sale = via[0] if via else self._centro(destino)
        if self._es_barra(destino):
            punto_sale = self._ancla(origen, sale or self._lado_hacia_la_barra(origen, destino),
                                     referencia_sale)
            return punto_sale, self._ancla(destino, None, via[-1] if via else punto_sale)
        referencia_entra = via[-1] if via else self._centro(origen)
        punto_sale = self._ancla(origen, sale, referencia_sale)
        punto_entra = self._ancla(destino, entra, referencia_entra)
        return self._alinear(origen, destino, sale, entra, punto_sale, punto_entra, via)

    def _lado_hacia_la_barra(self, item, barra):
        """Lado de `item` por el que se llega a una barra horizontal: arriba o abajo de ella."""
        return comp.NORTE if self._centro(barra)[1] < self._centro(item)[1] else comp.SUR

    @staticmethod
    def _alinear(origen, destino, sale, entra, punto_sale, punto_entra, via):
        """Dos lados laterales que se miran salen en linea recta aunque las cajas difieran en alto.

        Un estado compuesto es mucho mas alto que el estado al que va: sin esto, la linea sale en
        diagonal. Se toma la altura del punto de la caja mas baja, si cae dentro de la otra.
        """
        def nombre(lado):
            return lado[0] if isinstance(lado, tuple) else lado

        lateral = (comp.ESTE, comp.OESTE)
        if via or nombre(sale) not in lateral or nombre(entra) not in lateral:
            return punto_sale, punto_entra
        if abs(punto_sale[1] - punto_entra[1]) < 1:
            return punto_sale, punto_entra

        def cabe(item, y):
            return (item.matrix[5] + HOLGURA_DE_ALINEACION <= y
                    <= item.matrix[5] + item.height - HOLGURA_DE_ALINEACION)

        if origen.height >= destino.height and cabe(origen, punto_entra[1]):
            return (punto_sale[0], punto_entra[1]), punto_entra
        if destino.height > origen.height and cabe(destino, punto_sale[1]):
            return punto_sale, (punto_entra[0], punto_sale[1])
        return punto_sale, punto_entra

    def _flecha(self, diagrama, clase, origen, destino, etiqueta="", sale=None, entra=None,
                via=()):
        """Flecha entre dos items con el nombre de la guarda y, si hace falta, puntos intermedios."""
        puntos = self._anclas_de_flecha(origen, destino, sale, entra, via)
        linea = self._linea(clase, diagrama, origen, destino, anclar=puntos)
        for orden, punto in enumerate(via):
            asa = Handle()
            asa.pos = punto
            linea.insert_handle(1 + orden, asa)
        if etiqueta:
            linea.subject.name = etiqueta
        return linea

    def _nota_de_comportamiento(self, diagrama, texto, x, y):
        item = self.item(self.nota(texto), diagrama, ancho=ANCHO_DE_NOTA_DE_COMPORTAMIENTO)
        item.update_shapes()
        diagrama.update_now([item])
        self._mover(item, x, y)
        return item

    # -- comportamiento: actividades ----------------------------------------------
    def diagrama_de_actividad(self, definicion, paquete):
        """Actividad con carriles: cada paso va a su celda de la grilla y las flechas se anclan a mano."""
        actividad = self.factory.create(uml.Activity)
        actividad.name = definicion.nombre
        actividad.owningPackage = paquete
        diagrama = self.diagrama(sysml.ActivityDiagram, definicion.diagrama, paquete)
        diagrama.element = actividad

        def x_de(columna):
            return columna * PASO_DE_COLUMNA

        def y_de(fila):
            return fila * PASO_DE_FILA

        # Los carriles se crean primero para que queden debajo de los pasos.
        fondo = max(y_de(paso.fila) for paso in definicion.pasos) + MARGEN_INFERIOR_DEL_CARRIL
        carriles = []
        for orden, carril in enumerate(definicion.carriles):
            elemento = self.factory.create(uml.ActivityPartition)
            elemento.name = carril.nombre
            elemento.activity = actividad
            item = drop(elemento, diagrama, 0, 0)
            izquierda = (x_de(carril.columna_inicial) - PASO_DE_COLUMNA / 2
                         - (MARGEN_EXTREMO_DEL_CARRIL if orden == 0 else 0))
            if orden > 0:
                anterior = definicion.carriles[orden - 1]
                izquierda = x_de((anterior.columna_final + carril.columna_inicial) / 2)
            if orden < len(definicion.carriles) - 1:
                siguiente = definicion.carriles[orden + 1]
                derecha = x_de((carril.columna_final + siguiente.columna_inicial) / 2)
            else:
                derecha = (x_de(carril.columna_final) + PASO_DE_COLUMNA / 2
                           + MARGEN_EXTREMO_DEL_CARRIL)
            item.width, item.height = derecha - izquierda, fondo + MARGEN_SUPERIOR_DEL_CARRIL
            self._mover(item, izquierda, -MARGEN_SUPERIOR_DEL_CARRIL)
            carriles.append((carril, elemento))

        def carril_de(paso):
            for carril, elemento in carriles:
                if carril.columna_inicial <= paso.columna <= carril.columna_final:
                    return elemento
            return None

        clases = {comp.INICIO: uml.InitialNode, comp.FIN: uml.ActivityFinalNode,
                  comp.FIN_DE_FLUJO: uml.FlowFinalNode, comp.ACCION: uml.Action,
                  comp.DECISION: uml.DecisionNode, comp.UNION: uml.MergeNode,
                  comp.BIFURCACION: uml.ForkNode, comp.REUNION: uml.JoinNode}
        items = {}
        for paso in definicion.pasos:
            nodo = self.factory.create(clases[paso.tipo])
            nodo.activity = actividad
            if paso.texto:
                nodo.name = paso.texto
            if paso.tipo not in (comp.BIFURCACION, comp.REUNION):
                nodo.inPartition = carril_de(paso)
            if paso.tipo == comp.UNION:
                # Gaphor no arrastra un nodo de union: se dibuja con el rombo de la decision.
                item = diagrama.create(DecisionNodeItem, subject=nodo)
            else:
                item = drop(nodo, diagrama, 0, 0)
            if paso.tipo == comp.ACCION:
                item.width, item.height = ANCHO_DE_ACCION, ALTO_DE_ACCION
            if paso.tipo in (comp.BIFURCACION, comp.REUNION):
                self._poner_barra(item, x_de(paso.columna), y_de(paso.fila),
                                  paso.ancho_en_columnas * PASO_DE_COLUMNA)
            else:
                self._centrar(item, x_de(paso.columna), y_de(paso.fila))
            items[paso.clave] = item

        for flujo in definicion.flujos:
            puntos = tuple((x_de(c), y_de(f)) for c, f in flujo.via)
            self._flecha(diagrama, ControlFlowItem, items[flujo.origen], items[flujo.destino],
                         flujo.etiqueta, flujo.sale, flujo.entra, puntos)
        self._nota_de_comportamiento(
            diagrama, definicion.nota,
            x_de(definicion.carriles[0].columna_inicial) - PASO_DE_COLUMNA / 2
            - MARGEN_EXTREMO_DEL_CARRIL, fondo + SEPARACION_DE_LA_NOTA)
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    # -- comportamiento: maquinas de estados ----------------------------------------
    def diagrama_de_maquina_de_estados(self, definicion, paquete):
        maquina = self.factory.create(uml.StateMachine)
        maquina.name = definicion.nombre
        maquina.owningPackage = paquete
        diagrama = self.diagrama(sysml.StateMachineDiagram, definicion.diagrama, paquete)
        diagrama.element = maquina
        region_raiz = self.factory.create(uml.Region)
        region_raiz.stateMachine = maquina

        def x_de(columna):
            return columna * PASO_DE_COLUMNA_DE_ESTADOS

        def y_de(fila):
            return fila * PASO_DE_FILA_DE_ESTADOS

        elementos = {}
        region_de = {estado.clave: region_raiz for estado in definicion.estados}
        for estado in definicion.estados:
            elemento = self.factory.create(uml.State)
            elemento.name = estado.nombre
            elementos[estado.clave] = elemento
        for estado in definicion.estados:
            if estado.contiene:
                interna = self.factory.create(uml.Region)
                interna.state = elementos[estado.clave]
                for hijo in estado.contiene:
                    region_de[hijo] = interna
                for inicio, _, _, destino in definicion.inicios:
                    if destino in estado.contiene:
                        region_de[inicio] = interna
        for estado in definicion.estados:
            elementos[estado.clave].container = region_de[estado.clave]
        for clave, _, _, _ in definicion.inicios:
            inicial = self.factory.create(uml.Pseudostate)
            inicial.kind = "initial"
            inicial.container = region_de.get(clave, region_raiz)
            elementos[clave] = inicial

        items = {}
        # Un estado compuesto se coloca lejos al principio: soltar un estado donde ya hay otro
        # lo anida, y aqui cada anidamiento ya esta declarado en `contiene`.
        for estado in definicion.estados:
            if estado.contiene:
                items[estado.clave] = drop(elementos[estado.clave], diagrama, -10000, -10000)
        for estado in definicion.estados:
            if not estado.contiene:
                item = drop(elementos[estado.clave], diagrama, 0, 0)
                item.width, item.height = ANCHO_DE_ESTADO, ALTO_DE_ESTADO
                self._centrar(item, x_de(estado.columna), y_de(estado.fila))
                items[estado.clave] = item
        for clave, columna, fila, _ in definicion.inicios:
            item = drop(elementos[clave], diagrama, 0, 0)
            self._centrar(item, x_de(columna), y_de(fila))
            items[clave] = item
        for estado in definicion.estados:
            if estado.contiene:
                hijos = [items[h] for h in estado.contiene] + [
                    items[inicio] for inicio, _, _, destino in definicion.inicios
                    if destino in estado.contiene]
                izquierda = min(h.matrix[4] for h in hijos) - RELLENO_DEL_ESTADO_COMPUESTO
                derecha = max(h.matrix[4] + h.width for h in hijos) + RELLENO_DEL_ESTADO_COMPUESTO
                arriba = (min(h.matrix[5] for h in hijos) - RELLENO_DEL_ESTADO_COMPUESTO
                          - ENCABEZADO_DEL_ESTADO_COMPUESTO)
                abajo = max(h.matrix[5] + h.height for h in hijos) + RELLENO_DEL_ESTADO_COMPUESTO
                compuesto = items[estado.clave]
                compuesto.width, compuesto.height = derecha - izquierda, abajo - arriba
                self._mover(compuesto, izquierda, arriba)

        for transicion in definicion.transiciones:
            puntos = tuple((x_de(c), y_de(f)) for c, f in transicion.via)
            self._flecha(diagrama, TransitionItem, items[transicion.origen],
                         items[transicion.destino], transicion.etiqueta, transicion.sale,
                         transicion.entra, puntos)
        fondo = max(i.matrix[5] + i.height for i in items.values())
        izquierda = min(i.matrix[4] for i in items.values())
        self._nota_de_comportamiento(diagrama, definicion.nota, izquierda,
                                     fondo + SEPARACION_DE_LA_NOTA)
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    # -- comportamiento: casos de uso -------------------------------------------------
    def diagrama_de_casos_de_uso(self, paquete, frontera):
        """Actores a los costados, la frontera del sistema al centro y los casos dentro."""
        diagrama = self.diagrama(sysml.UseCaseDiagram, "6 uc [Comportamiento] Casos de uso del aula",
                                 paquete)

        def y_de(fila):
            return fila * PASO_DE_FILA_DE_CASOS

        columnas = CENTRO_DE_LA_COLUMNA_DE_CASOS
        izquierda = columnas[0] - ANCHO_DEL_ESCENARIO / 2 - MARGEN_DE_LA_FRONTERA
        derecha = columnas[2] + ANCHO_DEL_ESCENARIO / 2 + MARGEN_DE_LA_FRONTERA
        ultima = max(c.fila for c in comp.CASOS_DE_USO)
        # El nombre del sistema se dibuja en el centro de la frontera: con seis filas de casos
        # compartidos, queda en el hueco entre la tercera y la cuarta.
        arriba = y_de(0) - ALTO_DEL_CASO / 2 - MARGEN_DE_LA_FRONTERA
        abajo = y_de(ultima) + ALTO_DEL_CASO / 2 + MARGEN_DE_LA_FRONTERA
        item_frontera = self.item(frontera, diagrama, mostrar_atributos=False)
        for atributo in ("show_parts", "show_references", "show_operations", "show_values",
                         "show_constraints", "show_ports", "show_stereotypes"):
            if hasattr(item_frontera, atributo):
                setattr(item_frontera, atributo, False)
        item_frontera.width, item_frontera.height = derecha - izquierda, abajo - arriba
        self._mover(item_frontera, izquierda, arriba)

        items = {}
        for actor in comp.ACTORES:
            elemento = self.factory.create(uml.Actor)
            elemento.name = actor.nombre
            elemento.owningPackage = paquete
            item = drop(elemento, diagrama, 0, 0)
            self._centrar(item, X_DE_LOS_ACTORES[int(actor.columna)], y_de(actor.fila))
            items[actor.clave] = item
        for caso in comp.CASOS_DE_USO:
            elemento = self.factory.create(uml.UseCase)
            elemento.name = caso.nombre
            elemento.owningPackage = paquete
            elemento.subject = frontera
            item = drop(elemento, diagrama, 0, 0)
            ancho = ANCHO_DEL_ESCENARIO if caso.escenario else ANCHO_DEL_CASO_COMPARTIDO
            item.width, item.height = ancho, ALTO_DEL_CASO
            self._centrar(item, columnas[int(caso.columna)], y_de(caso.fila))
            items[caso.clave] = item

        for relacion in comp.RELACIONES_DE_USO:
            origen, destino = items[relacion.origen], items[relacion.destino]
            if relacion.clase == "asociacion":
                self._linea(AssociationItem, diagrama, origen, destino, anclar="enfrentadas")
            elif relacion.clase == "include":
                # La flecha va del caso que incluye al incluido y termina en la cabeza.
                self._linea(IncludeItem, diagrama, destino, origen, anclar="enfrentadas")
            else:
                self._linea(ExtendItem, diagrama, destino, origen, anclar="enfrentadas")
        self._nota_de_comportamiento(diagrama, comp.NOTA_DE_CASOS_DE_USO, izquierda,
                                     abajo + SEPARACION_DE_LA_NOTA)
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    def guardar(self, ruta):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as archivo:
            save(archivo, self.factory)


def construir():
    modelo = ModeloCampusTwin()
    raiz = modelo.paquete("Campus Twin L-419")
    pkg_vista = modelo.paquete("00 Vista general", raiz)
    pkg_requisitos = modelo.paquete("01 Requisitos", raiz)
    pkg_estructura = modelo.paquete("02 Estructura", raiz)
    pkg_verificacion = modelo.paquete("03 Verificación", raiz)

    # ---- elementos de requisitos
    for identificador, nombre, texto in NECESIDADES:
        modelo.requisito(identificador, nombre, texto, pkg_requisitos)
    for identificador, nombre, texto, _ in REQUISITOS_FUNCIONALES + REQUISITOS_NO_FUNCIONALES:
        modelo.requisito(identificador, nombre, texto, pkg_requisitos)
    for identificador, nombre, _, estado in CASOS_DE_PRUEBA:
        caso = modelo.caso_de_prueba(identificador, nombre, pkg_verificacion)
        caso.note = f"Estado al 10/11/2026: {estado}"

    # ---- elementos de estructura
    sistema = modelo.bloque(SISTEMA, pkg_estructura)
    for nombre in SUBSISTEMAS + ACTORES_EXTERNOS + SERVICIOS_SERVIDOR + PARTES_COPILOTO + PARTES_NODO_AUDIO:
        modelo.bloque(nombre, pkg_estructura)
    nodo_base = modelo.bloque(NODO_BASE, pkg_estructura, abstracto=True)
    for nodo, sensores in NODOS.items():
        modelo.bloque(nodo, pkg_estructura)
        for sensor in sensores:
            modelo.bloque(sensor, pkg_estructura)
    for nombre in TIPOS_DE_VALOR:
        modelo.tipo_de_valor(nombre, pkg_estructura)
    for nombre_bloque, propiedades in PROPIEDADES_DE_VALOR.items():
        for nombre_propiedad, nombre_tipo in propiedades:
            modelo.propiedad_de_valor(modelo.bloques[nombre_bloque], nombre_propiedad,
                                      modelo.tipos[nombre_tipo])

    # ---- vista general: todo el sistema en un solo diagrama
    def dibujar_vista_general(diagrama):
        for nombre in SUBSISTEMAS:
            modelo.composicion(diagrama, sistema, modelo.bloques[nombre])
        for nombre in ACTORES_EXTERNOS:
            modelo.asociacion(diagrama, sistema, modelo.bloques[nombre])
        modelo.composicion(diagrama, modelo.bloques["Subsistema de Sensado"], nodo_base)
        for nodo, sensores in NODOS.items():
            modelo.generalizacion(diagrama, modelo.bloques[nodo], nodo_base)
            for sensor in sensores:
                modelo.composicion(diagrama, modelo.bloques[nodo], modelo.bloques[sensor])
        for nombre in SERVICIOS_SERVIDOR:
            modelo.composicion(diagrama, modelo.bloques["Servidor Campus Twin"], modelo.bloques[nombre])
        for nombre in PARTES_COPILOTO:
            modelo.composicion(diagrama, modelo.bloques["Copiloto de Voz"], modelo.bloques[nombre])
        for nombre in PARTES_NODO_AUDIO:
            modelo.composicion(diagrama, modelo.bloques[NODO_AUDIO], modelo.bloques[nombre])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "1 bdd [Vista general] Campus Twin de un vistazo",
        pkg_vista, dibujar_vista_general,
        nota="Todo el sistema en un diagrama: el bloque Campus Twin L-419, sus seis "
             "subsistemas, los cinco actores externos, los cuatro tipos de nodo con su "
             "instrumentación (seis nodos físicos: dos de ocupación), los ocho servicios "
             "del servidor y las partes del copiloto de voz.\n\n"
             "Debajo de cada nodo van sus sensores, y dentro de cada sensor la magnitud "
             "que entrega con su unidad: de ahí sale cada dato del sistema. La demo de "
             "demo/ escribe esos valores en vivo.\n\n"
             "Los diagramas de 02 Estructura muestran lo mismo por partes.")

    # ---- req: necesidades de los stakeholders
    def dibujar_necesidades(diagrama):
        for identificador, _, _ in NECESIDADES:
            modelo.item(modelo.requisitos[identificador], diagrama)

    modelo.diagrama_jerarquico(
        sysml.RequirementDiagram, "1 req [Requisitos] Necesidades de los stakeholders",
        pkg_requisitos, dibujar_necesidades,
        nota="Necesidades levantadas en la pre-formulación y detalladas en "
             "docs/00-idea-principal.md (revisión v2 del 10/09/2026). Cada necesidad se "
             "descompone en requisitos funcionales (RF) y no funcionales (RNF).")

    # ---- req: derivacion de requisitos
    def pares_de_derivacion(requisitos):
        return [(modelo.requisitos[origen], modelo.requisitos[identificador])
                for identificador, _, _, origenes in requisitos for origen in origenes]

    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "2 req [Vista general] Mapa de requisitos",
        pkg_vista, DeriveReqtItem,
        pares_de_derivacion(REQUISITOS_FUNCIONALES + REQUISITOS_NO_FUNCIONALES),
        nota="Todas las necesidades (NS) con los requisitos funcionales (RF) y no "
             "funcionales (RNF) que derivan de ellas. La cobertura por bloque y por caso "
             "de prueba está en los diagramas de 01 Requisitos y 03 Verificación.")

    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "2 req [Requisitos] Requisitos funcionales",
        pkg_requisitos, DeriveReqtItem, pares_de_derivacion(REQUISITOS_FUNCIONALES))
    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "3 req [Requisitos] Requisitos no funcionales y restricciones",
        pkg_requisitos, DeriveReqtItem, pares_de_derivacion(REQUISITOS_NO_FUNCIONALES))

    # ---- req: verificacion (uno por familia, para que se lean)
    def pares_de_verificacion(prefijo):
        return [(modelo.requisitos[requisito], modelo.casos[identificador])
                for identificador, _, requisitos, _ in CASOS_DE_PRUEBA
                for requisito in requisitos if requisito.startswith(prefijo)]

    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "1 req [Verificación] Casos de prueba de requisitos funcionales",
        pkg_verificacion, VerifyItem, pares_de_verificacion("RF-"))
    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "2 req [Verificación] Casos de prueba de requisitos no funcionales",
        pkg_verificacion, VerifyItem, pares_de_verificacion("RNF-"))

    # ---- bdd: arquitectura del sistema
    def dibujar_arquitectura(diagrama):
        for nombre in SUBSISTEMAS:
            modelo.composicion(diagrama, sistema, modelo.bloques[nombre])
        for nombre in ACTORES_EXTERNOS:
            modelo.asociacion(diagrama, sistema, modelo.bloques[nombre])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "1 bdd [Estructura] Arquitectura del sistema",
        pkg_estructura, dibujar_arquitectura,
        nota="Cadena de datos: sensores -> ESP32 -> Wi-Fi -> Raspberry Pi 5 -> LAN -> "
             "dashboard y app de voz en el teléfono. Todo opera sin internet. "
             "Instrumentación y costos por módulo: docs/02-instrumentacion-l419.md.")

    # ---- bdd: nodos e instrumentacion
    modelo.diagrama_de_instrumentacion(
        "2 bdd [Estructura] Nodos e instrumentación", pkg_estructura, nodo_base,
        nota="Cada sensor declara la magnitud que entrega a su nodo, con su unidad.\n\n"
             "El SCD41 también mide temperatura y humedad, pero el sistema usa las del "
             "SHT31, que es más exacto: por eso aquí solo aparece el CO2.\n\n"
             "El PIR entrega movimiento y no presencia: con gente quieta se apaga, y de "
             "ahí que el nodo lleve además el radar (RF-03).\n\n"
             "La demo de demo/ escribe estos valores en vivo.")

    # ---- bdd: servidor y software
    def dibujar_servidor(diagrama):
        servidor = modelo.bloques["Servidor Campus Twin"]
        copiloto = modelo.bloques["Copiloto de Voz"]
        for nombre in SERVICIOS_SERVIDOR:
            modelo.composicion(diagrama, servidor, modelo.bloques[nombre])
        for nombre in PARTES_COPILOTO:
            modelo.composicion(diagrama, copiloto, modelo.bloques[nombre])
        for nombre in PARTES_NODO_AUDIO:
            modelo.composicion(diagrama, modelo.bloques[NODO_AUDIO], modelo.bloques[nombre])
        modelo.asociacion(diagrama, modelo.bloques["Dashboard Web"], modelo.bloques["API REST"])
        modelo.asociacion(diagrama, copiloto, modelo.bloques["Servicio de Voz STT/TTS"])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "3 bdd [Estructura] Servidor y software",
        pkg_estructura, dibujar_servidor)

    # ---- bdd: tipos de valor (catalogo de definiciones)
    def dibujar_tipos(diagrama):
        for nombre in TIPOS_DE_VALOR:
            modelo.item(modelo.tipos[nombre], diagrama)

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "4 bdd [Estructura] Tipos de valor y magnitudes",
        pkg_estructura, dibujar_tipos,
        nota="Catálogo de tipos de valor del modelo. Cada nodo declara sus propiedades "
             "de valor con estos tipos (ver el bdd de nodos e instrumentación).")

    construir_arquitectura_oficial(modelo, pkg_estructura)
    # ---- req: trazabilidad requisito - bloque (apunta a la arquitectura oficial)
    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "4 req [Requisitos] Trazabilidad a la arquitectura",
        pkg_requisitos, SatisfyItem,
        [(modelo.requisitos[identificador], modelo.bloques[nombre_bloque])
         for nombre_bloque, requisitos in TRAZABILIDAD.items() for identificador in requisitos],
        nota="Bloques de la arquitectura oficial (02 Estructura › 0 Arquitectura oficial EC3) "
             "que satisfacen cada RF y RNF, según docs/00-idea-principal.md, sección 8.2.\n\n"
             "Regla del equipo: todo RF debe tener al menos un bloque que lo satisface "
             "(satisfy) y al menos un caso de prueba que lo verifica (verify).")

    # Despues de la arquitectura oficial: los RA los satisfacen sus nodos y el evaluador.
    construir_requisitos_ra(modelo, raiz, pkg_requisitos, pkg_verificacion)
    construir_comportamiento(modelo, raiz)

    modelo.guardar(MODEL_PATH)
    return modelo


def construir_requisitos_ra(modelo, raiz, pkg_requisitos, pkg_verificacion):
    """RA-01..10 con derivacion, satisfy y verify, y el paquete 05 con su grafo causal."""
    requisitos_ra = leer_requisitos_ra()
    if set(requisitos_ra) != set(VERIFICACION_DE_RA):
        raise RuntimeError(f"VERIFICACION_DE_RA no cubre los mismos RA que "
                           f"config/requisitos_ra.yaml: {sorted(requisitos_ra)}")
    bloque_de_nodo = {nodo.id: nodo.bloque for nodo in NODOS_OFICIALES}
    for ident, requisito in requisitos_ra.items():
        elemento = modelo.requisito(ident, requisito["nombre"], texto_de_ra(requisito),
                                    pkg_requisitos)
        modelo.figuras_de_ra[ident] = rutas_de_figura(requisito)
        elemento.note = "Grafo causal: " + " y ".join(modelo.figuras_de_ra[ident])

    ras = [modelo.requisitos[ident] for ident in requisitos_ra]

    def relaciones(nombres_por_ra, buscar):
        """{elemento: [RA...]} a partir de {RA: [nombres]}."""
        resultado = {}
        for ident, nombres in nombres_por_ra.items():
            for nombre in nombres:
                resultado.setdefault(buscar(nombre), []).append(modelo.requisitos[ident])
        return resultado

    modelo.diagrama_de_ra(
        "5 req [Requisitos] Requisitos de alto nivel RA-01..10", pkg_requisitos,
        DeriveReqtItem, ras,
        relaciones({i: r["requisitos"] for i, r in requisitos_ra.items()},
                   modelo.requisitos.__getitem__),
        ra_es_cabeza=False,
        nota="Requisitos de condición del salón, nuevos para la EC3. Cada RA deriva del "
             "requisito funcional que concreta en umbrales; la fuente es "
             "config/requisitos_ra.yaml. El texto completo de cada RA (magnitud, umbrales y "
             "norma) se ve en 05 Diagnóstico causal, junto con su grafo.\n\n"
             "Cuando el código del docente ya define el umbral, se usa el mismo (origen "
             "docente).")

    modelo.diagrama_de_ra(
        "6 req [Requisitos] Trazabilidad de los RA a la arquitectura oficial", pkg_requisitos,
        SatisfyItem, ras,
        relaciones({i: [bloque_de_nodo[n] for n in r["nodos"]] + [EVALUADOR_DE_RA]
                    for i, r in requisitos_ra.items()}, modelo.bloques.__getitem__),
        ra_es_cabeza=True,
        nota="Cada RA lo satisfacen los nodos que miden su magnitud (campo nodos de "
             "config/requisitos_ra.yaml) y el evaluador de RA del servicio del grupo, que "
             "convierte la medición en nominal, alerta, crítico o desconocido.")

    modelo.diagrama_de_ra(
        "3 req [Verificación] Casos de prueba de los RA", pkg_verificacion,
        VerifyItem, ras, relaciones(VERIFICACION_DE_RA, modelo.casos.__getitem__),
        ra_es_cabeza=True,
        nota="CP-10 prueba con datos simulados la evaluación y el diagnóstico causal de los "
             "diez RA. Los demás CP ensayan con hardware el sensor o la función que usa cada "
             "RA y están pendientes (S15).\n\n"
             "RA-05 (gas) no tiene ensayo con hardware: el MQ-2 no figura en ningún CP físico.")

    paquete = modelo.paquete(PAQUETE_DIAGNOSTICO, raiz)
    # Dos digitos: el arbol de Gaphor ordena por nombre y RA-10 quedaria segundo.
    for indice, (ident, requisito) in enumerate(requisitos_ra.items(), start=1):
        modelo.diagrama_de_diagnostico(
            f"{indice:02d} req [Diagnóstico] {ident} {requisito['nombre']}", paquete,
            modelo.requisitos[ident], texto_de_diagnostico(requisito))


def _crear_elementos_oficiales(modelo, paquete, pkg_tipos):
    """Bloques, notas y propiedades de valor de la arquitectura oficial."""
    for nombre in TIPOS_DE_VALOR_OFICIALES:
        modelo.tipo_de_valor(nombre, pkg_tipos)
    nombres = ([SISTEMA_OFICIAL, RED_DE_NODOS, GATEWAY, RED_WIFI, LAPTOP, STACK_DOCENTE,
                SERVICIOS_DEL_GRUPO, AULA, CONTEXTO_DEL_FLUJO]
               + PARTES_DE_LA_CAJA + PARTES_DEL_STACK + PARTES_DE_LOS_SERVICIOS
               + MODULOS_DEL_SERVICIO + list(OBJETOS_DEL_AULA) + ITEMS_DE_FLUJO)
    for nombre in nombres:
        if nombre in modelo.bloques:
            raise RuntimeError(f"El bloque {nombre!r} ya existe en el modelo de septiembre")
        modelo.bloque(nombre, paquete)
    modelo.bloque(CAJA_DE_NODO, paquete, abstracto=True)

    for nodo in NODOS_OFICIALES:
        bloque = modelo.bloque(nodo.bloque, paquete)
        bloque.note = (f"Programa: {nodo.programa}. Publica en "
                       f"utec/gemelo/<grupo>/nodo{nodo.id}/{nodo.tipo}.")
        sensor = modelo.bloque(nodo.sensor, paquete)
        sensor.note = f"Interfaz con el ESP32: {nodo.interfaz}.\n{texto_de_foto(nodo.sensor, nodo.foto)}"
        for campo, tipo in MAGNITUDES_OFICIALES[nodo.sensor]:
            modelo.propiedad_de_valor(sensor, campo, modelo.tipos[tipo])
    for objeto, propiedades in OBJETOS_DEL_AULA.items():
        for nombre, tipo in propiedades:
            modelo.propiedad_de_valor(modelo.bloques[objeto], nombre, modelo.tipos[tipo])

    notas = {
        ESP32_DEVKIT: texto_de_foto(ESP32_DEVKIT, FOTO_DEL_ESP32),
        REGULADOR: "Pendiente de definir: la 18650 da de 3.0 a 4.2 V. Opciones: LDO de 3.3 V, "
                   "o elevador a 5 V con TP4056 (docs/02-instrumentacion-l419.md, sección 4).",
        GATEWAY: "gateway.ino del docente. Publica en utec/gemelo/<grupo>/nodo<id>/<tipo> y su "
                 "estado por LWT en utec/gemelo/<grupo>/gateway/estado.",
        STACK_DOCENTE: "vendor/gemelo_iot_profesor/servidor_iot: se usa sin modificarlo.",
        SERVICIO_GEMELO: "demo/servidor/gemelo (Grupo 1).",
        TABLERO: "demo/tablero (Grupo 1), servido por el servicio en :8000.",
        GAPHOR_EN_VIVO: "demo/gaphor-vivo (Grupo 1). Hoy escribe en los bloques del modelo de "
                        "septiembre; pasarlo a los 7 nodos es la tarea D7.",
        COPILOTO: "Pendiente: todavía no hay código.",
        SIMULADOR: "Publica en utec/gemelo/sim/... con el mismo JSON del Gateway. Todos los "
                   "datos actuales salen de aquí: son simulados.",
    }
    for nombre, nota in notas.items():
        modelo.bloques[nombre].note = nota


def construir_arquitectura_oficial(modelo, pkg_estructura):
    """Diagramas de la arquitectura oficial (EC3), sin tocar los de septiembre."""
    paquete = modelo.paquete(PAQUETE_OFICIAL, pkg_estructura)
    _crear_elementos_oficiales(modelo, paquete, pkg_estructura)
    b = modelo.bloques

    def colocar(diagrama, nombres, valores=False):
        # Antes de trazar lineas: con las composiciones el bloque ya tiene atributos, y
        # sin esto mostraria un compartimento de valores vacio.
        for nombre in nombres:
            modelo.item(b[nombre], diagrama, mostrar_atributos=valores)

    def dibujar_sistema(diagrama):
        nodos = [nodo.bloque for nodo in NODOS_OFICIALES]
        colocar(diagrama, [SISTEMA_OFICIAL, RED_DE_NODOS, GATEWAY, RED_WIFI, LAPTOP,
                           STACK_DOCENTE, SERVICIOS_DEL_GRUPO, AULA] + nodos)
        for nombre in [RED_DE_NODOS, GATEWAY, RED_WIFI, LAPTOP]:
            modelo.composicion(diagrama, b[SISTEMA_OFICIAL], b[nombre])
        modelo.asociacion(diagrama, b[SISTEMA_OFICIAL], b[AULA], nombre="monitorea")
        for nombre in nodos:
            modelo.composicion(diagrama, b[RED_DE_NODOS], b[nombre])
        for nombre in [STACK_DOCENTE, SERVICIOS_DEL_GRUPO]:
            modelo.composicion(diagrama, b[LAPTOP], b[nombre])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "1 bdd [Arquitectura oficial] Gemelo digital del L-419",
        paquete, dibujar_sistema,
        nota="Arquitectura oficial del curso (EC3). Siete cajas a batería envían por ESP-NOW "
             "al Gateway ESP32 v4, que publica por Wi-Fi y MQTT en la laptop con Docker.\n\n"
             "Autoría: firmware de los nodos (salvo el MQ-2), Gateway y stack del servidor, "
             "docente (J. F. Figueroa); MQ-2.ino y servicios, Grupo 1.\n\n"
             "Estado al 11/11/2026: ningún nodo está armado. Los datos de hoy son simulados.")

    modelo.diagrama_de_cajas(
        "2 bdd [Arquitectura oficial] Cajas de los 7 nodos", paquete,
        nota="Cada caja hereda de Caja de nodo el ESP32 DevKit V1, la protoboard, la 18650 con "
             "su porta-batería y el regulador, y agrega su sensor. Cada sensor declara los "
             "campos que entrega en el JSON del Gateway (docs/CONTRATO_DATOS.md).\n\n"
             "El regulador está pendiente: la 18650 da de 3.0 a 4.2 V. Las notas de abajo "
             f"apuntan a las fotos de las etiquetas con QR de la {ORDEN_DE_COMPRA}.")

    def dibujar_laptop(diagrama):
        colocar(diagrama, [LAPTOP, STACK_DOCENTE, SERVICIOS_DEL_GRUPO] + PARTES_DEL_STACK
                + PARTES_DE_LOS_SERVICIOS + MODULOS_DEL_SERVICIO)
        for nombre in [STACK_DOCENTE, SERVICIOS_DEL_GRUPO]:
            modelo.composicion(diagrama, b[LAPTOP], b[nombre])
        for nombre in PARTES_DEL_STACK:
            modelo.composicion(diagrama, b[STACK_DOCENTE], b[nombre])
        for nombre in PARTES_DE_LOS_SERVICIOS:
            modelo.composicion(diagrama, b[SERVICIOS_DEL_GRUPO], b[nombre])
        for nombre in MODULOS_DEL_SERVICIO:
            modelo.composicion(diagrama, b[SERVICIO_GEMELO], b[nombre])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram,
        "3 bdd [Arquitectura oficial] Laptop: stack del docente y servicios del grupo",
        paquete, dibujar_laptop,
        nota="La laptop corre el stack del docente (Mosquitto, Telegraf, InfluxDB y Grafana) "
             "sin modificar su docker-compose.yml, y los servicios del Grupo 1, que levanta "
             "deploy/levantar.sh.\n\n"
             "El copiloto de voz está pendiente. Gaphor en vivo todavía escribe en el modelo "
             "de septiembre (tarea D7).")

    def dibujar_aula(diagrama):
        colocar(diagrama, [AULA] + [nodo.bloque for nodo in NODOS_OFICIALES])
        for objeto, propiedades in OBJETOS_DEL_AULA.items():
            modelo.item(b[objeto], diagrama, mostrar_atributos=bool(propiedades),
                        ancho=ANCHO_DE_SENSOR_OFICIAL if propiedades else None)
            modelo.composicion(diagrama, b[AULA], b[objeto])
        for nodo, objeto in OBSERVACIONES:
            modelo.asociacion(diagrama, b[nodo], b[objeto], nombre="observa")

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "4 bdd [Arquitectura oficial] Objetos del aula",
        paquete, dibujar_aula,
        nota="Objetos del aula y qué nodo observa cada uno. Las cantidades y potencias están "
             "en config/aula_l419.yaml y son supuestas hasta medir en el aula.\n\n"
             "Sin PZEM, el consumo se estima por proxy con ese inventario: luces (nodo 4), "
             "aula vacía (nodo 5) y aire acondicionado por su ruido (nodo 2).")

    modelo.diagrama_de_flujo(
        "5 ibd [Arquitectura oficial] Flujo de datos",
        nota="Del sensor al tablero. Cada nodo envía al Gateway un paquete binario (paquetes.h). Telegraf guarda los mensajes del Gateway en InfluxDB "
             "(measurement = tipo). El servicio del grupo los recibe en vivo por MQTT, consulta "
             "el histórico con Flux y escribe en InfluxDB campustwin_evento y campustwin_ra.\n\n"
             "Hoy todo el flujo corre con el simulador (grupo sim): no hay mediciones reales. "
             "Pendiente: NTP local, porque sin hora Telegraf descarta los mensajes del Gateway.")


def construir_comportamiento(modelo, raiz):
    """Paquete 04: tres actividades, dos maquinas de estados y los casos de uso del aula."""
    paquete = modelo.paquete(PAQUETE_COMPORTAMIENTO, raiz)
    for actividad in comp.ACTIVIDADES:
        modelo.diagrama_de_actividad(actividad, paquete)
    for maquina in comp.MAQUINAS_DE_ESTADOS:
        modelo.diagrama_de_maquina_de_estados(maquina, paquete)
    modelo.diagrama_de_casos_de_uso(paquete, modelo.bloques[SISTEMA_OFICIAL])
    return paquete


def verificar_comportamiento(modelo):
    """Comprueba que las flechas del paquete 04 esten conectadas y que su semantica sea la esperada."""
    diagramas = modelo.factory.lselect(
        lambda e: isinstance(e, sysml.SysMLDiagram) and "[Comportamiento]" in (e.name or ""))
    print(f"\nDiagramas de {PAQUETE_COMPORTAMIENTO}: {len(diagramas)}")
    for diagrama in sorted(diagramas, key=lambda d: d.name):
        print(f"  - {diagrama.name}: {len(list(diagrama.get_all_items()))} items")

    flujos = modelo.factory.lselect(lambda e: isinstance(e, uml.ControlFlow))
    sueltos = [f for f in flujos if f.source is None or f.target is None]
    print(f"Flujos de control: {len(flujos)}; sin conectar: {len(sueltos) or 'ninguno'}")
    for actividad in modelo.factory.lselect(lambda e: isinstance(e, uml.Activity)):
        if not actividad.node:
            continue  # los casos de prueba son Activity vacias
        iniciales = [n for n in actividad.node if isinstance(n, uml.InitialNode)]
        finales = [n for n in actividad.node if isinstance(n, uml.ActivityFinalNode)]
        aislados = [n.name or type(n).__name__ for n in actividad.node
                    if not n.incoming and not n.outgoing]
        print(f"  {actividad.name}: {len(actividad.node)} nodos, {len(iniciales)} inicio, "
              f"{len(finales)} fin, aislados: {aislados or 'ninguno'}")

    transiciones = modelo.factory.lselect(lambda e: isinstance(e, uml.Transition))
    sin_extremo = [t for t in transiciones if t.source is None or t.target is None]
    print(f"Transiciones: {len(transiciones)}; sin conectar: {len(sin_extremo) or 'ninguna'}")
    for estado in modelo.factory.lselect(lambda e: isinstance(e, uml.State)):
        if not estado.incoming and not estado.outgoing:
            print(f"  estado sin transiciones: {estado.name}")

    print("Casos de uso incluidos (incluye -> incluido):")
    for inclusion in modelo.factory.lselect(lambda e: isinstance(e, uml.Include)):
        print(f"  {inclusion.includingCase.name} -> {inclusion.addition.name}")
    sin_actor = [c.name for c in modelo.factory.lselect(lambda e: isinstance(e, uml.UseCase))
                 if not c.subject]
    print("Casos de uso sin sistema como sujeto:", sin_actor or "ninguno")


def verificar(modelo):
    """Imprime la semantica de las relaciones creadas para revisarla a ojo."""
    print(f"Modelo guardado en {MODEL_PATH}")
    diagramas = modelo.factory.lselect(lambda e: isinstance(e, sysml.SysMLDiagram))
    print(f"\nDiagramas ({len(diagramas)}):")
    for diagrama in sorted(diagramas, key=lambda d: d.name):
        print(f"  - {diagrama.name}: {len(list(diagrama.get_all_items()))} items")
    print("\nDerivaciones (requisito -> origen):")
    for identificador, requisito in sorted(modelo.requisitos.items()):
        if requisito.derivedFrom:
            print(f"  {identificador} deriva de "
                  f"{', '.join(sorted(r.externalId for r in requisito.derivedFrom))}")
    print("\nSatisfaccion (requisito <- bloque):")
    for identificador, requisito in sorted(modelo.requisitos.items()):
        if requisito.satisfiedBy:
            print(f"  {identificador} satisfecho por "
                  f"{', '.join(b.name for b in requisito.satisfiedBy)}")
    print("\nVerificacion (requisito <- caso de prueba):")
    for identificador, requisito in sorted(modelo.requisitos.items()):
        if requisito.verifiedBy:
            print(f"  {identificador} verificado por "
                  f"{', '.join(c.name for c in requisito.verifiedBy)}")
    sin_bloque = [i for i, r in sorted(modelo.requisitos.items())
                  if i.startswith("RF-") and not r.satisfiedBy]
    sin_prueba = [i for i, r in sorted(modelo.requisitos.items())
                  if i.startswith(("RF-", "RNF-")) and not r.verifiedBy]
    print("\nRF sin bloque que lo satisface:", sin_bloque or "ninguno")
    print("RF/RNF sin caso de prueba:", sin_prueba or "ninguno")
    print("\nGeneralizaciones (especifico -> general):")
    for g in modelo.factory.lselect(lambda e: type(e).__name__ == "Generalization"):
        print(f"  {g.specific.name} -> {g.general.name}")
    # Las partes del IBD tambien son compuestas, pero no salen de una asociacion.
    compuestas = [p for p in modelo.factory.lselect(lambda e: isinstance(e, Property))
                  if p.aggregation == "composite" and p.association is not None]
    print(f"\nComposiciones (todo <>- parte): {len(compuestas)}")
    for propiedad in compuestas:
        otros = [e for e in propiedad.association.memberEnd if e is not propiedad]
        todo = otros[0].type.name if otros and otros[0].type else "?"
        print(f"  {todo} <>- {propiedad.type.name if propiedad.type else '?'}")
    verificar_arquitectura_oficial(modelo)
    verificar_requisitos_ra(modelo)
    verificar_comportamiento(modelo)


def verificar_requisitos_ra(modelo):
    """Todo RA debe tener bloque que lo satisface, caso de prueba y figura de su grafo."""
    ras = {i: r for i, r in modelo.requisitos.items() if i.startswith("RA-")}
    print(f"\nRA en el modelo: {len(ras)}")
    print("RA sin bloque que lo satisface:", [i for i, r in sorted(ras.items()) if not r.satisfiedBy] or "ninguno")
    print("RA sin caso de prueba:", [i for i, r in sorted(ras.items()) if not r.verifiedBy] or "ninguno")
    faltan = [ruta for rutas in modelo.figuras_de_ra.values() for ruta in rutas
              if not (RAIZ_DEL_REPO / ruta).is_file()]
    print("Figuras de grafo que no existen:", faltan or "ninguna")
    diagnosticos = modelo.factory.lselect(
        lambda e: isinstance(e, sysml.SysMLDiagram)
        and getattr(e.element, "name", None) == PAQUETE_DIAGNOSTICO)
    print(f"Diagramas en {PAQUETE_DIAGNOSTICO}: {len(diagnosticos)}")


def verificar_arquitectura_oficial(modelo):
    """Compara los nodos con config/nodos.yaml y comprueba que las fotos existan.

    El interprete de Gaphor no trae PyYAML: basta una expresion regular, porque
    nodos.yaml escribe cada nodo en una linea `<id>: {tipo: <tipo>, ...}`.
    """
    flujos = modelo.factory.lselect(lambda e: isinstance(e, sysml.ItemFlow))
    print(f"\nFlujos de item del IBD: {len(flujos)}")
    for flujo in flujos:
        print(f"  {flujo.informationSource.name} -> {flujo.informationTarget.name}: "
              f"{flujo.realizingConnector.name} ({flujo.itemProperty.type.name})")
    try:
        texto = NODOS_YAML.read_text(encoding="utf-8")
    except OSError as error:
        print(f"\nNo se pudo leer {NODOS_YAML}: {error}")
    else:
        en_yaml = {int(i): tipo for i, tipo in
                   re.findall(r"^\s+(\d+):\s*\{tipo:\s*(\w+)", texto, re.MULTILINE)}
        en_modelo = {nodo.id: nodo.tipo for nodo in NODOS_OFICIALES}
        print("\nNodos frente a config/nodos.yaml:",
              "coinciden" if en_yaml == en_modelo else f"DIFIEREN: {en_yaml} != {en_modelo}")
    raiz = NODOS_YAML.parents[1]
    fotos = [nodo.foto for nodo in NODOS_OFICIALES if nodo.foto] + [FOTO_DEL_ESP32]
    faltan = [foto for foto in fotos if not (raiz / CARPETA_DE_FOTOS / foto).is_file()]
    print("Fotos referenciadas que no existen:", faltan or "ninguna")


if __name__ == "__main__":
    verificar(construir())
