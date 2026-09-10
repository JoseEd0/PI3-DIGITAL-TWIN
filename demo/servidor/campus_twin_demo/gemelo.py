"""El gemelo en vivo: junta reloj, simulador, bus, almacen y reglas.

Es el equivalente de demostracion del servidor de la Raspberry Pi: recibe
muestras, las guarda, evalua reglas y publica una instantanea que consumen el
tablero web y el modelo SysML de Gaphor. Cuando lleguen los nodos reales, lo
unico que cambia es de donde salen las muestras (Mosquitto en lugar del
simulador); el resto de la cadena queda igual.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import datetime, timedelta

from . import configuracion as cfg
from .almacen import Almacen
from .bus import Bus
from .contrato import Evento, Muestra
from .reglas import AuditorDeConsumoFantasma, MotorDeReglas
from .simulador import ESCENARIOS, RelojVirtual, Simulador

log = logging.getLogger(__name__)


def _lunes_a_las(hora: float) -> datetime:
    """Arranca el dia simulado un lunes, para que haya clases desde el inicio."""
    hoy = datetime.now().replace(minute=0, second=0, microsecond=0)
    lunes = hoy - timedelta(days=hoy.weekday())
    return lunes.replace(hour=int(hora), minute=int((hora % 1) * 60))


class GemeloEnVivo:
    def __init__(self, velocidad: float = cfg.VELOCIDAD_POR_DEFECTO, semilla: int | None = 419) -> None:
        self.reloj = RelojVirtual(_lunes_a_las(cfg.HORA_DE_INICIO), velocidad)
        self.simulador = Simulador(self.reloj, semilla=semilla)
        self.bus = Bus()
        self.almacen = Almacen()
        self.reglas = MotorDeReglas()
        self.auditor = AuditorDeConsumoFantasma()
        self.mensajes = deque(maxlen=14)
        self.alertas_nuevas = deque(maxlen=20)
        self._tarea: asyncio.Task | None = None

        self.bus.suscribir_muestras(self._al_recibir_muestra)
        self.bus.suscribir_eventos(self._al_recibir_evento)

    # -- ingesta -------------------------------------------------------------
    def _al_recibir_muestra(self, muestra: Muestra) -> None:
        if self.almacen.registrar_muestra(muestra):
            self.mensajes.appendleft(muestra.como_diccionario())

    def _al_recibir_evento(self, evento: Evento) -> None:
        self.almacen.registrar_evento(evento)

    # -- ciclo ---------------------------------------------------------------
    def paso(self, segundos_reales: float) -> None:
        simulados = self.reloj.avanzar(segundos_reales)
        if simulados <= 0:
            return
        muestras, eventos = self.simulador.avanzar(simulados)
        self.bus.publicar_muestras(muestras)
        self.bus.publicar_eventos(eventos)
        self.auditor.acumular(self.simulador.estado, self.reloj, simulados / 60.0)
        nuevas = self.reglas.evaluar(
            self.simulador.estado, self.reloj, self.almacen.salud_como_lista(self.reloj.momento)
        )
        for alerta in nuevas:
            self.alertas_nuevas.appendleft(alerta.como_diccionario())

    async def correr(self) -> None:
        log.info("Gemelo en vivo iniciado a %s (x%s)", self.reloj.momento, self.reloj.velocidad)
        while True:
            await asyncio.sleep(cfg.PERIODO_DE_TICK_S)
            try:
                self.paso(cfg.PERIODO_DE_TICK_S)
            except Exception:
                # Un fallo en un tick no puede matar la demo delante del publico.
                log.exception("Fallo un tick del simulador; se continua con el siguiente")

    def iniciar(self) -> None:
        if self._tarea is None or self._tarea.done():
            self._tarea = asyncio.create_task(self.correr())

    async def detener(self) -> None:
        if self._tarea and not self._tarea.done():
            self._tarea.cancel()
            try:
                await self._tarea
            except asyncio.CancelledError:
                pass

    # -- control de la demostracion -----------------------------------------
    def aplicar_escenario(self, nombre: str) -> None:
        eventos = self.simulador.aplicar_escenario(nombre)
        self.bus.publicar_eventos(eventos)

    def ajustar_velocidad(self, velocidad: float) -> float:
        self.reloj.velocidad = max(cfg.VELOCIDAD_MINIMA, min(cfg.VELOCIDAD_MAXIMA, velocidad))
        return self.reloj.velocidad

    def alternar_pausa(self, pausado: bool | None = None) -> bool:
        self.reloj.pausado = (not self.reloj.pausado) if pausado is None else pausado
        return self.reloj.pausado

    # -- lectura -------------------------------------------------------------
    def resumen(self) -> dict:
        """Las magnitudes que muestran el tablero y el modelo SysML."""
        estado = self.simulador.estado
        return {
            "potencia": round(estado.potencia, 1),
            "energia": round(estado.energia_total, 3),
            "tension": round(self.almacen.ultimo(cfg.NODO_ENERGIA, "tension") or cfg.TENSION_NOMINAL_V, 1),
            "corriente": round(self.almacen.ultimo(cfg.NODO_ENERGIA, "corriente") or 0.0, 2),
            "factorDePotencia": round(
                self.almacen.ultimo(cfg.NODO_ENERGIA, "factorDePotencia") or cfg.FACTOR_DE_POTENCIA_TIPICO, 2
            ),
            "temperatura": round(estado.temperatura, 1),
            "humedad": round(estado.humedad, 1),
            "co2": round(estado.co2),
            "iluminancia": round(estado.iluminancia),
            "presencia": estado.presencia,
            "conteo": estado.conteo,
            "personas": estado.personas,
            "puertaAbierta": estado.puerta_abierta,
            "bateria": round(estado.bateria, 1),
            "lucesEncendidas": estado.luces_encendidas,
            "proyectorEncendido": estado.proyector_encendido,
            "pcsEncendidos": estado.pcs_encendidos,
            "aireEncendido": estado.aire_encendido,
            "minutosVacio": round(estado.minutos_vacio),
        }

    def instantanea(self) -> dict:
        ahora = self.reloj.momento
        return {
            "reloj": {
                "ts": ahora.isoformat(timespec="seconds"),
                "hora": ahora.strftime("%H:%M:%S"),
                "fecha": ahora.strftime("%d/%m/%Y"),
                "velocidad": self.reloj.velocidad,
                "pausado": self.reloj.pausado,
                "dentroDeHorario": self.reloj.dentro_del_horario_oficial,
                "diaDeClase": self.reloj.es_dia_de_clase,
                "horarioOficial": list(cfg.HORARIO_OFICIAL),
            },
            "escenario": self.simulador.escenario,
            "escenarios": ESCENARIOS,
            "resumen": self.resumen(),
            "nodos": self.almacen.lecturas_por_nodo(),
            "catalogoDeNodos": {
                nodo: {"etiqueta": etiqueta, "requisito": requisito, "periodo": periodo}
                for nodo, (etiqueta, requisito, periodo) in cfg.NODOS.items()
            },
            "alertas": self.reglas.activas_como_lista(),
            "alertasRecientes": self.reglas.historial_como_lista(),
            "salud": self.almacen.salud_como_lista(ahora),
            "fantasma": self.auditor.como_diccionario(),
            "eventos": self.almacen.eventos_recientes(),
            "mensajes": list(self.mensajes),
            "umbrales": {
                "co2": cfg.UMBRAL_DE_CO2_PPM,
                "consumoConAulaVacia": cfg.UMBRAL_DE_CONSUMO_CON_AULA_VACIA_W,
                "bateriaBaja": cfg.UMBRAL_DE_BATERIA_BAJA,
                "aforo": cfg.AFORO_DEL_LABORATORIO,
            },
        }
