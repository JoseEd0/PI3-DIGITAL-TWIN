"""El servicio del grupo: une ingesta, requisitos, razonamiento, consumo fantasma y log.

En cada ciclo:
1. si hay simulador en el proceso, lo avanza y publica sus mensajes (por MQTT, igual que el Gateway);
2. lee los mensajes del grupo configurado y actualiza el estado del aula;
3. evalúa RA-01..10 y, para cada uno en alerta o crítico, corre su grafo causal;
4. registra en el log los cambios (RA, puerta, cruces, anomalías, nodos, Gateway);
5. acumula el consumo fantasma estimado y publica sus propias salidas en
   utec/gemelo/<grupo>/campustwin/... sin tocar los tópicos del Gateway;
6. si hay InfluxDB, escribe ahí también el log y la condición de cada RA.

La fuente local puede ser el simulador o el reproductor de una grabación: los dos dan un reloj
del aula y los mensajes a publicar, con la misma interfaz.
"""

from __future__ import annotations

import dataclasses
import json
import logging
from collections import deque
from datetime import datetime, timedelta

from . import gateway
from .bitacora import Bitacora
from .configuracion import ZONA_HORARIA, cargar_aula, cargar_fuente, cargar_nodos, cargar_requisitos
from .estado import EstadoDelAula
from .fantasma import EstimadorDeConsumoFantasma
from .grafos import Razonador, cargar_grafos
from .influx import RegistroDeSalidas
from .requisitos import ALERTA, CRITICO, DESCONOCIDO, GRAVEDAD, EvaluadorDeRequisitos
from .simulador import Simulador
from .transporte import Transporte

log = logging.getLogger(__name__)

PUNTOS_DE_TENDENCIA = 360
PERIODO_DE_SALIDAS_S = 10
CICLOS_DE_LATENCIA = 2
MARGEN_SOBRE_EL_RETRASO = 1.5
SALTO_HACIA_ATRAS_S = 60  # un nodo que retrocede más que esto en el tiempo delata a otra fuente
OLVIDO_DEL_RETRASO = 0.98  # el máximo observado decae despacio para seguir mejoras de la red
# Magnitud principal de cada tipo de nodo: la que se grafica como tendencia en el dashboard.
MAGNITUD_PRINCIPAL = {
    "co2": ("co2_ppm", "ppm"), "audio": ("leq_db", "dB"), "gas": ("rs_r0", "Rs/R0"),
    "luz": ("lux_mesa_est", "lx"), "termico": ("ocupacion_est", "personas"),
    "magnetico": ("puerta_abierta", ""), "ambiente": ("temp_c", "°C"),
}
SEVERIDAD_POR_NIVEL = {ALERTA: "alerta", CRITICO: "critico"}


def _hora_del_aula(momento: datetime) -> str:
    """El Gateway fecha en UTC; la API y el tablero muestran la hora de Lima, con su desfase."""
    return momento.astimezone(ZONA_HORARIA).isoformat(timespec="seconds")


class Servicio:
    def __init__(self, transporte: Transporte, simulador: Simulador | None = None,
                 bitacora: Bitacora | None = None, grupo: str | None = None,
                 registro: RegistroDeSalidas | None = None) -> None:
        self.transporte = transporte
        self.simulador = simulador  # o un gemelo.grabacion.Reproductor
        self.bitacora = bitacora or Bitacora()
        self.registro = registro
        self.aula = cargar_aula()
        self.nodos = cargar_nodos()
        self.requisitos = cargar_requisitos()
        self.grupo = grupo or (simulador.grupo if simulador else cargar_fuente().grupo)
        salud = self.requisitos["RA-10"]
        self.estado = EstadoDelAula.nuevo(self.aula, self.nodos, salud["periodos_tolerados"], salud["minimo_tolerancia_s"])
        self.evaluador = EvaluadorDeRequisitos(self.requisitos)
        self.razonador = Razonador(cargar_grafos())
        self.fantasma = EstimadorDeConsumoFantasma(self.aula, self.requisitos["RA-08"]["alerta_min"])
        self.condiciones: dict = {}
        self.diagnosticos: dict = {}
        self.tendencias = {i: deque(maxlen=PUNTOS_DE_TENDENCIA) for i in self.nodos}
        self.mensajes_recientes: deque[dict] = deque(maxlen=20)
        self._caidos_previos: set[int] = set()
        self._ultimas_salidas: datetime | None = None
        self._retraso_s = 0.0
        self._duplicados: set[int] = set()
        self.transporte.suscribir(f"{gateway.PREFIJO}/{self.grupo}/#")

    @property
    def origen(self) -> str:
        if self.simulador:
            return self.simulador.origen
        return "simulado" if self.grupo == "sim" else "real"

    def _latencia(self, segundos_reales: float) -> timedelta:
        """Lo que tarda un mensaje en llegar (Gateway → MQTT → servicio), en tiempo del aula.

        Se mide en cada mensaje. Con el simulador acelerado (×60) un ciclo de 0,5 s reales son
        30 s del aula y el broker puede entregar varios ciclos después: sin este margen los nodos
        "parpadean" como caídos, el estado pasa a desconocido y se reinician los contadores.
        """
        velocidad = self.simulador.reloj.velocidad if self.simulador else 1.0
        minimo = CICLOS_DE_LATENCIA * segundos_reales * velocidad
        return timedelta(seconds=max(minimo, MARGEN_SOBRE_EL_RETRASO * self._retraso_s))

    def ahora(self) -> datetime:
        return self.simulador.reloj.momento if self.simulador else datetime.now(ZONA_HORARIA)

    # -- ciclo ----------------------------------------------------------------------------------
    def ciclo(self, segundos_reales: float) -> None:
        if self.simulador:
            for topico, carga, retenido in self.simulador.avanzar(segundos_reales):
                self.transporte.publicar(topico, carga, retenido)
        for topico, carga in self.transporte.recibir_pendientes():
            self._procesar(topico, carga)
        self.estado.marcar_reloj(self.ahora() - self._latencia(segundos_reales))
        self._evaluar()
        self.fantasma.acumular(self.estado)
        self._publicar_salidas()

    def _procesar(self, topico: str, carga: bytes) -> None:
        if topico == gateway.topico_estado_gateway(self.grupo):
            self._registrar_gateway(carga.decode(errors="replace").strip())
            return
        if "/campustwin/" in topico:
            return  # nuestras propias salidas
        try:
            lectura = gateway.leer(topico, carga)
        except gateway.MensajeInvalido as error:
            log.warning("Mensaje descartado: %s", error)
            return
        if lectura.momento is None:
            # Igual que Telegraf, sin hora no se puede fechar; se usa la de llegada y se avisa.
            lectura = dataclasses.replace(lectura, momento=self.ahora())
        retraso = (self.ahora() - lectura.momento).total_seconds()
        self._retraso_s = max(retraso, self._retraso_s * OLVIDO_DEL_RETRASO)
        previa = self.estado.nodos[lectura.nodo].ultima if lectura.nodo in self.estado.nodos else None
        self._vigilar_fuente_duplicada(previa, lectura)
        self.estado.registrar(lectura, lectura.momento)
        self._eventos_de_lectura(previa, lectura)
        self._guardar_tendencia(lectura)
        self.mensajes_recientes.appendleft({"topico": topico, "carga": carga.decode(errors="replace")})

    def _vigilar_fuente_duplicada(self, previa: gateway.Lectura | None, lectura: gateway.Lectura) -> None:
        """Dos publicadores con el mismo grupo (dos simuladores, o simulador y Gateway real) mezclan
        horas y hacen parpadear a los nodos; se avisa en el log para que alguien apague uno."""
        if previa is None or previa.momento is None or lectura.momento is None:
            return
        if (previa.momento - lectura.momento).total_seconds() > SALTO_HACIA_ATRAS_S and lectura.nodo not in self._duplicados:
            self._duplicados.add(lectura.nodo)
            self._registrar("salud", "alerta", f"Nodo {lectura.nodo}: llegan mensajes de dos fuentes distintas "
                            f"(grupo «{self.grupo}»); hay otro simulador o Gateway publicando", nodo=lectura.nodo)

    def _registrar_gateway(self, estado: str) -> None:
        en_linea = estado == "online"
        if self.estado.gateway_en_linea is not None and self.estado.gateway_en_linea != en_linea:
            self._registrar("gateway", "info" if en_linea else "critico",
                            "Gateway en línea" if en_linea else "Gateway desconectado (LWT offline)")
        self.estado.gateway_en_linea = en_linea

    def _guardar_tendencia(self, lectura: gateway.Lectura) -> None:
        campo, _ = MAGNITUD_PRINCIPAL[lectura.tipo]
        valor = lectura.campos.get(campo)
        if valor is not None and lectura.momento is not None:
            self.tendencias[lectura.nodo].append((_hora_del_aula(lectura.momento), valor))

    # -- evaluación -----------------------------------------------------------------------------
    def _evaluar(self) -> None:
        previas = self.condiciones
        self.condiciones = self.evaluador.evaluar(self.estado)
        self.diagnosticos = {
            ra: self.razonador.diagnosticar(ra, self.estado)
            for ra, condicion in self.condiciones.items() if condicion.nivel in (ALERTA, CRITICO)
        }
        for ra, condicion in self.condiciones.items():
            anterior = previas.get(ra)
            if anterior is None or anterior.nivel == condicion.nivel or condicion.nivel == DESCONOCIDO:
                continue
            if condicion.nivel in SEVERIDAD_POR_NIVEL:
                diagnostico = self.diagnosticos[ra]
                causas = [c["texto"] for c in diagnostico.causas_confirmadas + diagnostico.causas_sospechosas]
                self._registrar("requisito", SEVERIDAD_POR_NIVEL[condicion.nivel],
                                f"{ra} {condicion.nombre}: {condicion.mensaje}", ra=ra,
                                causas=causas, recomendaciones=diagnostico.recomendaciones)
            elif GRAVEDAD[anterior.nivel] > 0:
                self._registrar("requisito", "info", f"{ra} {condicion.nombre} volvió a nominal", ra=ra)
        self._eventos_de_salud()

    def _eventos_de_lectura(self, previa: gateway.Lectura | None, actual: gateway.Lectura) -> None:
        campos = actual.campos
        if actual.tipo == "magnetico":
            abierta = bool(campos.get("puerta_abierta"))
            if previa is None or bool(previa.campos.get("puerta_abierta")) != abierta:
                fuera = self.estado.fuera_de_horario()
                self._registrar("puerta", "alerta" if fuera and abierta else "info",
                                ("Puerta abierta" if abierta else "Puerta cerrada") + (" fuera de horario" if fuera else ""),
                                nodo=actual.nodo)
        if actual.tipo == "termico" and (campos.get("entradas") or campos.get("salidas")):
            self._registrar("ocupacion", "info",
                            f"Entradas {campos.get('entradas', 0)}, salidas {campos.get('salidas', 0)} "
                            f"→ ocupación estimada {campos.get('ocupacion_est')}", nodo=actual.nodo)
        if actual.tipo == "luz" and campos.get("luces_cambio"):
            self._registrar("luces", "info", "Luces encendidas" if campos["luces_cambio"] > 0 else "Luces apagadas",
                            nodo=actual.nodo)
        nuevas = set(actual.anomalias) - set(previa.anomalias if previa else ())
        for anomalia in sorted(nuevas):
            severidad = "critico" if anomalia in ("GAS_DETECTADO", "CO2_CRITICO") else "alerta"
            self._registrar("anomalia_nodo", severidad, f"Nodo {actual.nodo} ({actual.tipo}): {anomalia}",
                            nodo=actual.nodo)

    def _eventos_de_salud(self) -> None:
        # Solo cuentan los nodos que ya habían reportado: al arrancar todos están "sin datos".
        caidos = {n for n in self.estado.nodos_sin_datos() if self.estado.nodos[n].recibido is not None}
        for nodo in sorted(caidos - self._caidos_previos):
            self._registrar("salud", "alerta", f"Nodo {nodo} sin datos", nodo=nodo)
        for nodo in sorted(self._caidos_previos - caidos):
            self._registrar("salud", "info", f"Nodo {nodo} volvió a reportar", nodo=nodo)
        self._caidos_previos = caidos

    def _registrar(self, tipo: str, severidad: str, mensaje: str, **extra) -> None:
        evento = self.bitacora.registrar(self.estado.ahora or self.ahora(), tipo, severidad, mensaje, self.origen, **extra)
        self.transporte.publicar(f"{gateway.PREFIJO}/{self.grupo}/campustwin/evento",
                                 json.dumps(evento.__dict__, ensure_ascii=False))
        if self.registro:
            self.registro.evento(evento, self.grupo)

    def _publicar_salidas(self) -> None:
        ahora = self.estado.ahora
        if ahora is None or (self._ultimas_salidas and (ahora - self._ultimas_salidas).total_seconds() < PERIODO_DE_SALIDAS_S):
            return
        self._ultimas_salidas = ahora
        cuerpo = {"ts": int(ahora.timestamp() * 1000), "origen": self.origen,
                  **{ra: GRAVEDAD[c.nivel] for ra, c in self.condiciones.items()}}
        self.transporte.publicar(f"{gateway.PREFIJO}/{self.grupo}/campustwin/ra", json.dumps(cuerpo))
        if self.registro:
            self.registro.requisitos(ahora, self.condiciones, self.grupo, self.origen)

    def cerrar(self) -> None:
        self.transporte.cerrar()
        if self.registro:
            self.registro.cerrar()

    # -- control --------------------------------------------------------------------------------
    def aplicar_escenario(self, nombre: str) -> None:
        if not self.simulador:
            raise RuntimeError("No hay simulador: el servicio está leyendo datos reales")
        self.simulador.aplicar_escenario(nombre)
        self._registrar("escenario", "info", f"Escenario de demostración: {self.simulador.escenarios[nombre]}")

    # -- lectura para la API ----------------------------------------------------------------------
    def _reproduccion(self) -> dict | None:
        avance = getattr(self.simulador, "avance", None)
        if avance is None:
            return None
        return {"archivo": self.simulador.ruta.name, "avance": round(avance, 3),
                "terminado": self.simulador.terminado, "descripcion": self.simulador.cabecera.descripcion}

    def mediciones(self) -> list[dict]:
        filas = []
        for ident, nodo in self.estado.nodos.items():
            ultima = nodo.ultima
            campo, unidad = MAGNITUD_PRINCIPAL[nodo.config.tipo]
            filas.append({
                "nodo": ident, "tipo": nodo.config.tipo, "sensor": nodo.config.sensor,
                "magnitud": campo, "unidad": unidad,
                "valor": ultima.campos.get(campo) if ultima else None,
                "campos": ultima.campos if ultima else {},
                "anomalias": list(ultima.anomalias) if ultima else [],
                "ts": _hora_del_aula(ultima.momento) if ultima and ultima.momento else None,
                "tendencia": list(self.tendencias[ident])[-60:],
            })
        return filas

    def instantanea(self) -> dict:
        ahora = self.estado.ahora or self.ahora()
        local = ahora.astimezone(ZONA_HORARIA)
        reloj = self.simulador.reloj if self.simulador else None
        return {
            "reloj": {
                "ts": local.isoformat(timespec="seconds"), "hora": local.strftime("%H:%M:%S"),
                "fecha": local.strftime("%d/%m/%Y"), "velocidad": reloj.velocidad if reloj else 1.0,
                "pausado": reloj.pausado if reloj else False, "fueraDeHorario": self.estado.fuera_de_horario(),
            },
            "fuente": {"grupo": self.grupo, "origen": self.origen, "simulado": self.origen != "real",
                       "escenario": self.simulador.escenario if self.simulador else None,
                       "escenarios": self.simulador.escenarios if self.simulador else {},
                       "reproduccion": self._reproduccion()},
            "aula": {"nombre": self.aula.nombre, "aforo": self.aula.aforo, "supuestos": self.aula.resumen_de_supuestos()},
            "mediciones": self.mediciones(),
            "derivados": self.estado.derivados(),
            "requisitos": [c.como_diccionario() | {"necesidad": self.requisitos[ra]["necesidad"],
                                                    "norma": self.requisitos[ra]["norma"],
                                                    "origenUmbral": self.requisitos[ra]["origen"]}
                           for ra, c in self.condiciones.items()],
            "diagnosticos": {ra: d.como_diccionario() for ra, d in self.diagnosticos.items()},
            "salud": self.estado.salud(),
            "gatewayEnLinea": self.estado.gateway_en_linea,
            "fantasma": self.fantasma.como_diccionario(),
            "eventos": self.bitacora.listar(limite=30),
            "mensajes": list(self.mensajes_recientes)[:8],
        }
