"""Genera el modelo SysML base de Campus Twin (aula laboratorio L-419).

Se ejecuta con el interprete embebido de Gaphor:

    /Applications/Gaphor.app/Contents/MacOS/gaphor exec modelo/tools/build_model.py

Reconstruye por completo `modelo/campus-twin-l419.gaphor` a partir de los datos
declarados en este archivo. El contenido sale de docs/00-idea-principal.md; los
identificadores de requisito (NS-x, RF-xx, RNF-xx, CP-xx) son los mismos en el
documento, en el modelo y en las tareas de Asana.

Una vez que el modelo se edita a mano en Gaphor, el .gaphor pasa a ser la fuente de
verdad y este script queda como registro reproducible del modelo base.
"""

from pathlib import Path

from gaphor.core.modeling import ElementFactory, StyleSheet
from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import connect
from gaphor.plugins.autolayout import AutoLayout
from gaphor.storage.save import save
from gaphor.SysML import sysml
from gaphor.SysML.requirements.relationships import DeriveReqtItem, SatisfyItem, VerifyItem
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.uml import Activity, Comment, Package, Property

MODEL_PATH = Path(__file__).resolve().parents[1] / "campus-twin-l419.gaphor"
GRID_STEP = 220  # separacion inicial entre items; el layout la recalcula
COMMENT_WIDTH = 360  # ancho de las notas, para que el texto no quede en una columna
REQUIREMENT_WIDTH = 250  # sin ancho fijo, el texto del requisito queda en una columna

# Los diagramas de derivacion, trazabilidad y verificacion son bipartitos: graphviz
# los estira en una sola fila de varios miles de pixeles, asi que se acomodan a mano
# en dos columnas (origen a la izquierda, elementos relacionados a la derecha).
COLUMNA_IZQUIERDA_X = 0.0
COLUMNA_DERECHA_X = 470.0
SEPARACION_VERTICAL = 30.0
SEPARACION_ENTRE_GRUPOS = 60.0

# --- Requisitos -------------------------------------------------------------
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
]

# (id, nombre, texto, necesidades de las que deriva)
REQUISITOS_FUNCIONALES = [
    ("RF-01", "Medición de energía",
     "El sistema debe medir tensión, corriente, potencia y energía acumulada del laboratorio cada 10 s o menos.",
     ["NS-2"]),
    ("RF-02", "Medición ambiental",
     "El sistema debe medir temperatura, humedad, CO2 e iluminancia cada 60 s o menos.",
     ["NS-3"]),
    ("RF-03", "Estimación de ocupación",
     "El sistema debe estimar presencia y conteo de personas sin cámaras, con latencia menor a 30 s.",
     ["NS-1", "NS-3"]),
    ("RF-04", "Eventos de puerta",
     "El sistema debe detectar apertura y vibración de la puerta y registrar el evento en menos de 10 s.",
     ["NS-4"]),
    ("RF-05", "Transporte de datos",
     "Los nodos deben enviar datos al servidor por Wi-Fi o BLE, con reintento y buffer local de 15 min.",
     ["NS-5"]),
    ("RF-06", "Histórico y consulta",
     "El servidor debe almacenar series temporales por 60 días y exponer una API de consulta.",
     ["NS-2"]),
    ("RF-07", "Dashboard web",
     "El dashboard debe mostrar el estado en vivo con refresco de 5 s, históricos y reporte de ahorro.",
     ["NS-2"]),
    ("RF-08", "Alertas por reglas",
     "El sistema debe generar alertas configurables por consumo, CO2 alto y puerta fuera de horario.",
     ["NS-1", "NS-4"]),
    ("RF-09", "Copiloto de voz",
     "El copiloto debe dar el briefing de turno y responder consultas orales en español en menos de 5 s.",
     ["NS-1"]),
    ("RF-10", "Detección de consumo fantasma",
     "El sistema debe reportar la energía consumida con el laboratorio desocupado cruzando energía, luz y ocupación.",
     ["NS-2"]),
    ("RF-11", "Modo demostración",
     "El sistema debe reproducir un día de datos grabados para sostener la demo si falla el hardware.",
     ["NS-5"]),
]

REQUISITOS_NO_FUNCIONALES = [
    ("RNF-01", "Instalación no invasiva",
     "La instalación no debe perforar paredes ni intervenir el tablero eléctrico del laboratorio.",
     ["NS-5"]),
    ("RNF-02", "Privacidad por diseño",
     "El sistema no debe usar cámaras ni almacenar audio; los datos de ocupación deben ser agregados.",
     ["NS-4"]),
    ("RNF-03", "Presupuesto acotado",
     "El costo del prototipo no debe exceder S/ 2713, con una versión mínima operativa de S/ 653.",
     ["NS-5"]),
    ("RNF-04", "Autonomía de nodos",
     "Los nodos alimentados con batería deben operar 30 días sin recarga.",
     ["NS-4"]),
    ("RNF-05", "Red autónoma",
     "El sistema debe operar sobre una red local propia si la red del campus bloquea los dispositivos.",
     ["NS-5"]),
    ("RNF-06", "Disponibilidad para la demo",
     "El sistema debe operar 72 h continuas sin intervención antes de la presentación final.",
     ["NS-5"]),
    ("RNF-07", "Configurabilidad",
     "Pines, umbrales, intervalos y endpoints deben ser configurables y sin credenciales en el repositorio.",
     ["NS-5"]),
]

# (id, nombre, requisitos que verifica)
CASOS_DE_PRUEBA = [
    ("CP-01", "Ensayo de exactitud de energía", ["RF-01"]),
    ("CP-02", "Ensayo de ocupación con personas quietas", ["RF-03"]),
    ("CP-03", "Ensayo de resiliencia de red", ["RF-05", "RNF-05"]),
    ("CP-04", "Ensayo del copiloto de voz", ["RF-09"]),
    ("CP-05", "Maratón de 72 horas", ["RNF-06"]),
    ("CP-06", "Auditoría de consumo fantasma", ["RF-10"]),
    ("CP-07", "Calibración ambiental contra instrumento patrón", ["RF-02"]),
    ("CP-08", "Ensayo de eventos de puerta", ["RF-04"]),
    ("CP-09", "Ensayo de histórico, API y dashboard", ["RF-06", "RF-07"]),
    ("CP-10", "Ensayo de reglas de alerta", ["RF-08"]),
    ("CP-11", "Ensayo del modo demostración", ["RF-11"]),
    ("CP-12", "Revisión de instalación no invasiva y privacidad", ["RNF-01", "RNF-02"]),
    ("CP-13", "Ensayo de autonomía del nodo de puerta", ["RNF-04"]),
    ("CP-14", "Auditoría de costos y configuración", ["RNF-03", "RNF-07"]),
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
ACTORES_EXTERNOS = ["Vigilante Nocturno", "Administrador de Infraestructura", "Laboratorio L-419"]

NODO_BASE = "Nodo Sensor ESP32"
NODOS = {
    "Nodo de Energía": ["PZEM-004T v3.0", "Pinza SCT-013", "Enchufe Inteligente"],
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
]
PARTES_COPILOTO = ["Nodo de Audio", "Audífono Bluetooth"]
PARTES_NODO_AUDIO = ["Micrófono INMP441", "Amplificador MAX98357A", "Parlante 4 ohm 3 W"]

TIPOS_DE_VALOR = [
    "Temperatura [°C]",
    "Humedad [%HR]",
    "CO2 [ppm]",
    "Iluminancia [lx]",
    "Potencia [W]",
    "Energía acumulada [kWh]",
    "Ocupación [personas]",
    "Latencia [s]",
    "Nivel de batería [%]",
]

# bloque -> [(nombre de la propiedad, tipo de valor)]
PROPIEDADES_DE_VALOR = {
    "Nodo Ambiental": [
        ("temperatura", "Temperatura [°C]"),
        ("humedad", "Humedad [%HR]"),
        ("co2", "CO2 [ppm]"),
        ("iluminancia", "Iluminancia [lx]"),
    ],
    "Nodo de Energía": [
        ("potencia", "Potencia [W]"),
        ("energia", "Energía acumulada [kWh]"),
    ],
    "Nodo de Ocupación": [("ocupacion", "Ocupación [personas]")],
    "Nodo de Puerta": [("bateria", "Nivel de batería [%]")],
    "Servidor Campus Twin": [("latenciaDeConsulta", "Latencia [s]")],
}

# bloque -> requisitos que satisface
TRAZABILIDAD = {
    "Nodo de Energía": ["RF-01"],
    "Nodo Ambiental": ["RF-02"],
    "Nodo de Ocupación": ["RF-03"],
    "Nodo de Puerta": ["RF-04", "RNF-04"],
    "Red Local": ["RF-05", "RNF-05"],
    "Base de Datos de Series Temporales": ["RF-06"],
    "Dashboard Web": ["RF-07"],
    "Motor de Reglas y Alertas": ["RF-08", "RF-10"],
    "Copiloto de Voz": ["RF-09"],
    "Servidor Campus Twin": ["RF-11"],
}


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

    # -- presentaciones ------------------------------------------------------
    def item(self, elemento, diagrama):
        """Coloca un elemento en un diagrama (una sola vez por diagrama)."""
        clave = (diagrama.id, elemento.id)
        if clave not in self._items:
            indice = self._siguiente_posicion.get(diagrama.id, 0)
            self._siguiente_posicion[diagrama.id] = indice + 1
            item = drop(elemento, diagrama, (indice % 5) * GRID_STEP, (indice // 5) * GRID_STEP)
            if item is None:
                raise RuntimeError(f"Gaphor no tiene item de diagrama para {elemento}")
            if hasattr(item, "show_attributes"):
                # el compartimento solo aporta si el bloque declara propiedades de valor
                item.show_attributes = bool(getattr(elemento, "ownedAttribute", ()))
            if isinstance(elemento, sysml.Requirement):
                item.width = REQUIREMENT_WIDTH
            elif isinstance(elemento, Comment):
                item.width = COMMENT_WIDTH
            self._items[clave] = item
        return self._items[clave]

    @staticmethod
    def _centro_derecho(item):
        return item.matrix[4] + item.width, item.matrix[5] + item.height / 2

    @staticmethod
    def _centro_izquierdo(item):
        return item.matrix[4], item.matrix[5] + item.height / 2

    def _linea(self, clase, diagrama, item_cabeza, item_cola, anclar=False):
        linea = diagrama.create(clase)
        cabeza, cola = linea.handles()[0], linea.handles()[-1]
        if anclar:
            # El conector engancha la linea al puerto mas cercano al handle, y un handle
            # recien creado esta en el origen: sin esto, todas las lineas se pegan al
            # borde izquierdo y cruzan por encima de las cajas.
            cabeza.pos = self._centro_derecho(item_cabeza)
            cola.pos = self._centro_izquierdo(item_cola)
        connect(linea, cabeza, item_cabeza)
        connect(linea, cola, item_cola)
        if linea.subject is None:
            raise RuntimeError(f"No se pudo crear la relacion {clase.__name__}")
        return linea

    # -- relaciones ----------------------------------------------------------
    # La direccion de cada relacion se comprueba en verificar(): la cabeza es el
    # extremo del que cuelga la semantica (origen de la derivacion, requisito
    # satisfecho o verificado, elemento especifico de la generalizacion).
    def generalizacion(self, diagrama, especifico, general):
        return self._linea(GeneralizationItem, diagrama,
                           self.item(especifico, diagrama), self.item(general, diagrama))

    def composicion(self, diagrama, todo, parte):
        """Asociacion compuesta: el rombo queda del lado del todo."""
        linea = self._linea(AssociationItem, diagrama,
                            self.item(todo, diagrama), self.item(parte, diagrama))
        linea.tail_subject.aggregation = "composite"
        return linea

    def asociacion(self, diagrama, origen, destino):
        return self._linea(AssociationItem, diagrama,
                           self.item(origen, diagrama), self.item(destino, diagrama))

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
                        anclar=True)
        diagrama.update_now(list(diagrama.get_all_items()))
        return diagrama

    def guardar(self, ruta):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as archivo:
            save(archivo, self.factory)


def construir():
    modelo = ModeloCampusTwin()
    raiz = modelo.paquete("Campus Twin L-419")
    pkg_requisitos = modelo.paquete("01 Requisitos", raiz)
    pkg_estructura = modelo.paquete("02 Estructura", raiz)
    pkg_verificacion = modelo.paquete("03 Verificación", raiz)

    # ---- elementos de requisitos
    for identificador, nombre, texto in NECESIDADES:
        modelo.requisito(identificador, nombre, texto, pkg_requisitos)
    for identificador, nombre, texto, _ in REQUISITOS_FUNCIONALES + REQUISITOS_NO_FUNCIONALES:
        modelo.requisito(identificador, nombre, texto, pkg_requisitos)
    for identificador, nombre, _ in CASOS_DE_PRUEBA:
        modelo.caso_de_prueba(identificador, nombre, pkg_verificacion)

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

    # ---- req: necesidades de los stakeholders
    def dibujar_necesidades(diagrama):
        for identificador, _, _ in NECESIDADES:
            modelo.item(modelo.requisitos[identificador], diagrama)

    modelo.diagrama_jerarquico(
        sysml.RequirementDiagram, "req [Requisitos] Necesidades de los stakeholders",
        pkg_requisitos, dibujar_necesidades,
        nota="Necesidades levantadas en la pre-formulación y detalladas en "
             "docs/00-idea-principal.md. Cada necesidad se descompone en requisitos "
             "funcionales (RF) y no funcionales (RNF).")

    # ---- req: derivacion de requisitos
    def pares_de_derivacion(requisitos):
        return [(modelo.requisitos[origen], modelo.requisitos[identificador])
                for identificador, _, _, origenes in requisitos for origen in origenes]

    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "req [Requisitos] Requisitos funcionales",
        pkg_requisitos, DeriveReqtItem, pares_de_derivacion(REQUISITOS_FUNCIONALES))
    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "req [Requisitos] Requisitos no funcionales y restricciones",
        pkg_requisitos, DeriveReqtItem, pares_de_derivacion(REQUISITOS_NO_FUNCIONALES))

    # ---- req: trazabilidad requisito - bloque
    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "req [Requisitos] Trazabilidad a la arquitectura",
        pkg_requisitos, SatisfyItem,
        [(modelo.requisitos[identificador], modelo.bloques[nombre_bloque])
         for nombre_bloque, requisitos in TRAZABILIDAD.items() for identificador in requisitos],
        nota="Regla del equipo: todo RF debe tener al menos un bloque que lo satisface "
             "(satisfy) y al menos un caso de prueba que lo verifica (verify).")

    # ---- req: verificacion (uno por familia, para que se lean)
    def pares_de_verificacion(prefijo):
        return [(modelo.requisitos[requisito], modelo.casos[identificador])
                for identificador, _, requisitos in CASOS_DE_PRUEBA
                for requisito in requisitos if requisito.startswith(prefijo)]

    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "req [Verificación] Casos de prueba de requisitos funcionales",
        pkg_verificacion, VerifyItem, pares_de_verificacion("RF-"))
    modelo.diagrama_bipartito(
        sysml.RequirementDiagram, "req [Verificación] Casos de prueba de requisitos no funcionales",
        pkg_verificacion, VerifyItem, pares_de_verificacion("RNF-"))

    # ---- bdd: arquitectura del sistema
    def dibujar_arquitectura(diagrama):
        for nombre in SUBSISTEMAS:
            modelo.composicion(diagrama, sistema, modelo.bloques[nombre])
        for nombre in ACTORES_EXTERNOS:
            modelo.asociacion(diagrama, sistema, modelo.bloques[nombre])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "bdd [Estructura] Arquitectura del sistema",
        pkg_estructura, dibujar_arquitectura,
        nota="Cadena de datos: sensores -> ESP32 -> Wi-Fi/BLE -> Raspberry Pi 5 -> LAN -> "
             "dashboard y copiloto de voz. Instrumentación y costos por módulo: "
             "docs/02-instrumentacion-l419.md.")

    # ---- bdd: nodos e instrumentacion
    def dibujar_nodos(diagrama):
        modelo.composicion(diagrama, modelo.bloques["Subsistema de Sensado"], nodo_base)
        for nodo, sensores in NODOS.items():
            modelo.generalizacion(diagrama, modelo.bloques[nodo], nodo_base)
            for sensor in sensores:
                modelo.composicion(diagrama, modelo.bloques[nodo], modelo.bloques[sensor])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "bdd [Estructura] Nodos e instrumentación",
        pkg_estructura, dibujar_nodos)

    # ---- bdd: servidor y software
    def dibujar_servidor(diagrama):
        servidor = modelo.bloques["Servidor Campus Twin"]
        copiloto = modelo.bloques["Copiloto de Voz"]
        for nombre in SERVICIOS_SERVIDOR:
            modelo.composicion(diagrama, servidor, modelo.bloques[nombre])
        for nombre in PARTES_COPILOTO:
            modelo.composicion(diagrama, copiloto, modelo.bloques[nombre])
        for nombre in PARTES_NODO_AUDIO:
            modelo.composicion(diagrama, modelo.bloques["Nodo de Audio"], modelo.bloques[nombre])
        modelo.asociacion(diagrama, modelo.bloques["Dashboard Web"], modelo.bloques["API REST"])
        modelo.asociacion(diagrama, copiloto, modelo.bloques["Servicio de Voz STT/TTS"])

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "bdd [Estructura] Servidor y software",
        pkg_estructura, dibujar_servidor)

    # ---- bdd: tipos de valor (catalogo de definiciones)
    def dibujar_tipos(diagrama):
        for nombre in TIPOS_DE_VALOR:
            modelo.item(modelo.tipos[nombre], diagrama)

    modelo.diagrama_jerarquico(
        sysml.BlockDefinitionDiagram, "bdd [Estructura] Tipos de valor y magnitudes",
        pkg_estructura, dibujar_tipos,
        nota="Catálogo de tipos de valor del modelo. Cada nodo declara sus propiedades "
             "de valor con estos tipos (ver el bdd de nodos e instrumentación).")

    modelo.guardar(MODEL_PATH)
    return modelo


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
    compuestas = [p for p in modelo.factory.lselect(lambda e: isinstance(e, Property))
                  if p.aggregation == "composite"]
    print(f"\nComposiciones (todo <>- parte): {len(compuestas)}")
    for propiedad in compuestas:
        otros = [e for e in propiedad.association.memberEnd if e is not propiedad]
        todo = otros[0].type.name if otros and otros[0].type else "?"
        print(f"  {todo} <>- {propiedad.type.name if propiedad.type else '?'}")


if __name__ == "__main__":
    verificar(construir())
