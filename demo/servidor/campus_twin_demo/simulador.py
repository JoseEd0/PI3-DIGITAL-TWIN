"""Simulador del laboratorio L-419.

Sustituye a los seis nodos fisicos mientras no llega la instrumentacion: genera
las mismas magnitudes, con los mismos periodos y el mismo contrato de topicos
que publicaran los ESP32 (RF-11, "simulador y modo demostracion").

El dia simulado corre acelerado, asi que en una demo de veinte minutos se ve una
jornada entera: la clase de la manana con el CO2 subiendo, el mediodia vacio, la
tarde, y sobre todo la noche con las luces olvidadas, que es de donde sale el
reporte de consumo fantasma (RF-10).

El modelo fisico es deliberadamente simple. No pretende predecir el laboratorio:
pretende que cada magnitud se mueva por la razon correcta, para que el tablero y
el modelo SysML muestren relaciones creibles antes de tener sensores.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import configuracion as cfg
from .contrato import Evento, Muestra

ESCENARIOS = {
    "normal": "Sigue el guion del dia sin forzar nada",
    "clase": "Entra un grupo al laboratorio ahora mismo",
    "vacio-con-luces": "Todos salen y dejan luces y PC encendidos",
    "apertura-fuera-de-horario": "Alguien abre la puerta fuera del horario oficial",
    "caida-de-nodo": "El nodo ambiental deja de reportar",
    "senal-debil": "El nodo de ocupacion del fondo pierde muestras por mala senal",
    "restablecer": "Vuelve al guion normal y levanta el nodo caido",
}


class RelojVirtual:
    """Reloj del laboratorio simulado, que corre mas rapido que el real."""

    def __init__(self, inicio: datetime, velocidad: float = cfg.VELOCIDAD_POR_DEFECTO) -> None:
        self.momento = inicio
        self.velocidad = velocidad
        self.pausado = False

    def avanzar(self, segundos_reales: float) -> float:
        """Avanza el reloj y devuelve cuantos segundos simulados pasaron."""
        if self.pausado:
            return 0.0
        simulados = segundos_reales * self.velocidad
        self.momento += timedelta(seconds=simulados)
        return simulados

    @property
    def hora_decimal(self) -> float:
        return self.momento.hour + self.momento.minute / 60 + self.momento.second / 3600

    @property
    def es_dia_de_clase(self) -> bool:
        return self.momento.weekday() < 5

    @property
    def dentro_del_horario_oficial(self) -> bool:
        desde, hasta = cfg.HORARIO_OFICIAL
        return desde <= self.hora_decimal < hasta


@dataclass
class EstadoDelLaboratorio:
    """Lo que esta pasando en el aula en este instante simulado."""

    personas: int = 0
    luces_encendidas: bool = False
    proyector_encendido: bool = False
    pcs_encendidos: int = 0
    aire_encendido: bool = False
    puerta_abierta: bool = False
    vibracion: bool = False
    minutos_desde_la_vibracion: float = 999.0
    movimiento: bool = False
    co2: float = cfg.CO2_EXTERIOR_PPM
    temperatura: float = cfg.TEMPERATURA_BASE_C
    humedad: float = cfg.HUMEDAD_BASE_HR
    iluminancia: float = 0.0
    potencia: float = cfg.POTENCIA_EN_REPOSO_W
    energia_total: float = 0.0
    energia_proyector: float = 0.0
    energia_pc: float = 0.0
    bateria: float = cfg.BATERIA_INICIAL
    conteo: int = 0
    minutos_vacio: float = 0.0
    nodos_caidos: set[str] = field(default_factory=set)

    @property
    def presencia(self) -> bool:
        return self.personas > 0


class Simulador:
    def __init__(self, reloj: RelojVirtual, semilla: int | None = None) -> None:
        self.reloj = reloj
        self.azar = random.Random(semilla)
        self.estado = EstadoDelLaboratorio()
        self.escenario = "normal"
        self._secuencias: dict[tuple[str, str], int] = {}
        self._proximo_envio: dict[tuple[str, str], datetime] = {}
        self._olvido_las_luces = False
        self._dia_del_olvido: int | None = None
        self._ronda_hecha_el_dia: int | None = None
        self._clase_forzada_hasta: datetime | None = None
        self._nodos_con_senal_debil: set[str] = set()

    # -- guion del dia -------------------------------------------------------
    def _personas_esperadas(self) -> int:
        """Cuanta gente deberia haber segun el horario de clases."""
        if self._clase_forzada_hasta and self.reloj.momento < self._clase_forzada_hasta:
            return int(cfg.AFORO_DEL_LABORATORIO * 0.7)
        if not self.reloj.es_dia_de_clase:
            return 0
        hora = self.reloj.hora_decimal
        for inicio, fin in cfg.BLOQUES_DE_CLASE:
            if inicio <= hora < fin:
                # entrada y salida escalonadas: la gente no aparece de golpe
                minutos_desde_inicio = (hora - inicio) * 60
                minutos_para_fin = (fin - hora) * 60
                llenado = min(1.0, minutos_desde_inicio / 8)
                vaciado = min(1.0, minutos_para_fin / 6)
                ocupacion = min(llenado, vaciado)
                return int(cfg.AFORO_DEL_LABORATORIO * 0.55 * ocupacion + 0.5)
        return 0

    def _actualizar_cargas(self, esperadas: int, minutos: float) -> list[Evento]:
        eventos: list[Evento] = []
        estado = self.estado
        hora = self.reloj.hora_decimal
        dia = self.reloj.momento.toordinal()

        # La gente entra y sale de a pocos, no de golpe.
        if esperadas > estado.personas:
            estado.personas = min(esperadas, estado.personas + max(1, int(minutos)))
        elif esperadas < estado.personas:
            estado.personas = max(esperadas, estado.personas - max(1, int(minutos)))

        hay_luz_natural = 7.5 <= hora < 17.5
        if estado.personas > 0:
            estado.luces_encendidas = not hay_luz_natural or estado.proyector_encendido
            estado.pcs_encendidos = min(cfg.PCS_DEL_LABORATORIO, max(2, estado.personas // 2))
            estado.proyector_encendido = estado.personas >= 6
            self._olvido_las_luces = False
        else:
            estado.proyector_encendido = False
            if self.escenario == "vacio-con-luces":
                estado.luces_encendidas = True
                estado.pcs_encendidos = cfg.PCS_DEL_LABORATORIO // 2
            elif self._olvido_las_luces:
                estado.luces_encendidas = True
                estado.pcs_encendidos = max(estado.pcs_encendidos, 4)
            else:
                estado.luces_encendidas = False
                estado.pcs_encendidos = 0

        # Al terminar la ultima clase del dia, a veces nadie apaga nada. Ese
        # olvido es el que el reporte de consumo fantasma tiene que encontrar.
        fin_de_la_ultima_clase = cfg.BLOQUES_DE_CLASE[-1][1]
        if (
            estado.personas == 0
            and fin_de_la_ultima_clase <= hora < fin_de_la_ultima_clase + 0.5
            and self._dia_del_olvido != dia
        ):
            self._dia_del_olvido = dia
            self._olvido_las_luces = self.azar.random() < 0.75

        # El vigilante pasa de madrugada, abre, y si ve luces las apaga.
        if (
            abs(hora - cfg.RONDA_DEL_VIGILANTE) < 0.05
            and self._ronda_hecha_el_dia != dia
        ):
            self._ronda_hecha_el_dia = dia
            eventos.append(self._evento_de_puerta("apertura", "ronda del vigilante"))
            eventos.append(self._evento_de_puerta("cierre", "ronda del vigilante"))
            if self._olvido_las_luces:
                self._olvido_las_luces = False
                estado.luces_encendidas = False
                estado.pcs_encendidos = 0

        # Con histeresis: enciende arriba de un umbral y apaga bien abajo, como
        # un termostato de verdad. Sin ella el aire prende y apaga cada minuto.
        if estado.personas < cfg.PERSONAS_PARA_ENCENDER_EL_AIRE:
            estado.aire_encendido = False
        elif estado.temperatura > cfg.TEMPERATURA_DE_ENCENDIDO_DEL_AIRE_C:
            estado.aire_encendido = True
        elif estado.temperatura < cfg.TEMPERATURA_DE_APAGADO_DEL_AIRE_C:
            estado.aire_encendido = False
        return eventos

    # -- fisica del ambiente -------------------------------------------------
    def _actualizar_ambiente(self, minutos: float) -> None:
        estado = self.estado
        hora = self.reloj.hora_decimal

        renovacion = (
            cfg.CO2_RENOVACION_PUERTA_ABIERTA
            if estado.puerta_abierta
            else cfg.CO2_RENOVACION_POR_MIN
        )
        aporte = estado.personas * cfg.CO2_POR_PERSONA_PPM_MIN * minutos
        perdida = (estado.co2 - cfg.CO2_EXTERIOR_PPM) * min(1.0, renovacion * minutos)
        estado.co2 = min(cfg.CO2_MAXIMO_PPM, max(cfg.CO2_EXTERIOR_PPM, estado.co2 + aporte - perdida))

        # curva diaria suave, mas calor a media tarde
        curva = 3.2 * math.sin(math.pi * max(0.0, (hora - 6.0)) / 14.0)
        objetivo = (
            cfg.TEMPERATURA_BASE_C
            + curva
            + estado.personas * cfg.TEMPERATURA_POR_PERSONA_C
            - (2.6 if estado.aire_encendido else 0.0)
        )
        estado.temperatura += (objetivo - estado.temperatura) * min(1.0, 0.08 * minutos)
        estado.humedad += (
            cfg.HUMEDAD_BASE_HR + estado.personas * 0.35 - (estado.temperatura - cfg.TEMPERATURA_BASE_C) * 1.4 - estado.humedad
        ) * min(1.0, 0.06 * minutos)

        luz_natural = max(0.0, math.sin(math.pi * (hora - 6.0) / 12.0)) * cfg.ILUMINANCIA_DIURNA_MAXIMA_LX
        luz_artificial = cfg.LUMINARIAS * cfg.ILUMINANCIA_POR_LUMINARIA_LX if estado.luces_encendidas else 0.0
        estado.iluminancia = max(0.0, luz_natural + luz_artificial + self.azar.gauss(0, 4))

    def _actualizar_energia(self, minutos: float) -> None:
        estado = self.estado
        potencia = cfg.POTENCIA_EN_REPOSO_W
        if estado.luces_encendidas:
            potencia += cfg.LUMINARIAS * cfg.POTENCIA_POR_LUMINARIA_W
        if estado.proyector_encendido:
            potencia += cfg.POTENCIA_DEL_PROYECTOR_W
        potencia += estado.pcs_encendidos * cfg.POTENCIA_POR_PC_W
        if estado.aire_encendido:
            potencia += cfg.POTENCIA_DEL_AIRE_W
        estado.potencia = max(0.0, potencia + self.azar.gauss(0, potencia * 0.012))

        horas = minutos / 60.0
        estado.energia_total += estado.potencia * horas / 1000.0
        if estado.proyector_encendido:
            estado.energia_proyector += cfg.POTENCIA_DEL_PROYECTOR_W * horas / 1000.0
        if estado.pcs_encendidos:
            estado.energia_pc += cfg.POTENCIA_POR_PC_W * horas / 1000.0

    def _actualizar_ocupacion(self, minutos: float) -> None:
        estado = self.estado
        # El PIR se apaga con gente quieta; el radar no. Es justamente la razon
        # por la que el nodo lleva los dos (RF-03).
        estado.movimiento = estado.presencia and (
            estado.puerta_abierta or self.azar.random() < cfg.DETECCION_DEL_PIR_CON_GENTE_QUIETA
        )
        if estado.presencia:
            estado.minutos_vacio = 0.0
            # el conteo del ToF es una estimacion: se desvia y no se corrige sola
            objetivo = estado.personas + self.azar.randint(-cfg.ERROR_DE_CONTEO, cfg.ERROR_DE_CONTEO)
            estado.conteo = max(0, objetivo)
        else:
            estado.minutos_vacio += minutos
            if estado.minutos_vacio >= cfg.MINUTOS_VACIO_PARA_REINICIAR_CONTEO:
                estado.conteo = 0

    def _actualizar_vibracion(self, minutos: float) -> None:
        self.estado.minutos_desde_la_vibracion += minutos
        self.estado.vibracion = self.estado.minutos_desde_la_vibracion < cfg.MINUTOS_DE_VIBRACION

    def _actualizar_bateria(self, minutos: float) -> None:
        por_minuto = cfg.BATERIA_INICIAL / (cfg.DIAS_DE_AUTONOMIA * 24 * 60)
        self.estado.bateria = max(0.0, self.estado.bateria - por_minuto * minutos)

    # -- puerta --------------------------------------------------------------
    def _evento_de_puerta(self, tipo: str, detalle: str) -> Evento:
        self.estado.puerta_abierta = tipo == "apertura"
        self.estado.minutos_desde_la_vibracion = 0.0
        self.estado.vibracion = True
        self.estado.bateria = max(0.0, self.estado.bateria - 0.02)
        return Evento(
            nodo=cfg.NODO_PUERTA,
            tipo=tipo,
            momento=self.reloj.momento,
            detalle=detalle,
            datos={"fueraDeHorario": not self.reloj.dentro_del_horario_oficial},
        )

    def _eventos_de_puerta_por_clase(self, personas_antes: int) -> list[Evento]:
        eventos: list[Evento] = []
        ahora = self.estado.personas
        if personas_antes == 0 and ahora > 0:
            eventos.append(self._evento_de_puerta("apertura", "entra el grupo"))
        elif personas_antes > 0 and ahora == 0:
            eventos.append(self._evento_de_puerta("apertura", "sale el grupo"))
            eventos.append(self._evento_de_puerta("cierre", "sale el grupo"))
        elif self.estado.puerta_abierta and ahora > 0 and self.azar.random() < 0.25:
            eventos.append(self._evento_de_puerta("cierre", "se cierra la puerta"))
        return eventos

    # -- emision de muestras -------------------------------------------------
    def _siguiente_secuencia(self, nodo: str, magnitud: str) -> int:
        clave = (nodo, magnitud)
        self._secuencias[clave] = self._secuencias.get(clave, 0) + 1
        return self._secuencias[clave]

    def _reportar_ya(self, nodo: str, *magnitudes: str) -> None:
        """Fuerza el envio de unas magnitudes en el tick actual."""
        for magnitud in magnitudes:
            self._proximo_envio.pop((nodo, magnitud), None)

    def _toca_enviar(self, nodo: str, magnitud: str) -> bool:
        clave = (nodo, magnitud)
        periodo = cfg.NODOS[nodo][2]
        proximo = self._proximo_envio.get(clave)
        if proximo is None or self.reloj.momento >= proximo:
            self._proximo_envio[clave] = self.reloj.momento + timedelta(seconds=periodo)
            return True
        return False

    def _muestra(self, nodo: str, magnitud: str, valor: float) -> Muestra:
        return Muestra(
            nodo=nodo,
            magnitud=magnitud,
            valor=round(float(valor), 3),
            momento=self.reloj.momento,
            secuencia=self._siguiente_secuencia(nodo, magnitud),
            unidad=cfg.UNIDADES.get(magnitud, ""),
        )

    def _lecturas_por_nodo(self) -> dict[str, dict[str, float]]:
        estado = self.estado
        corriente = estado.potencia / (cfg.TENSION_NOMINAL_V * cfg.FACTOR_DE_POTENCIA_TIPICO)
        return {
            cfg.NODO_ENERGIA: {
                "tension": cfg.TENSION_NOMINAL_V + self.azar.gauss(0, 1.4),
                "corriente": corriente,
                "potencia": estado.potencia,
                "factorDePotencia": cfg.FACTOR_DE_POTENCIA_TIPICO + self.azar.gauss(0, 0.01),
                "energia": estado.energia_total,
            },
            cfg.ENCHUFE_PROYECTOR: {
                "potencia": cfg.POTENCIA_DEL_PROYECTOR_W if estado.proyector_encendido else 0.4,
                "energia": estado.energia_proyector,
            },
            cfg.ENCHUFE_PC: {
                "potencia": cfg.POTENCIA_POR_PC_W if estado.pcs_encendidos else 1.1,
                "energia": estado.energia_pc,
            },
            cfg.NODO_AMBIENTAL: {
                "temperatura": estado.temperatura + self.azar.gauss(0, 0.06),
                "humedad": estado.humedad + self.azar.gauss(0, 0.3),
                "co2": estado.co2 + self.azar.gauss(0, 8),
                "iluminancia": estado.iluminancia,
            },
            cfg.NODO_OCUPACION_PUERTA: {
                "presencia": 1.0 if estado.presencia else 0.0,
                "movimiento": 1.0 if estado.movimiento else 0.0,
                "conteo": estado.conteo,
            },
            cfg.NODO_OCUPACION_FONDO: {
                "presencia": 1.0 if estado.presencia else 0.0,
                "movimiento": 1.0 if estado.movimiento else 0.0,
            },
            cfg.NODO_PUERTA: {
                "estadoPuerta": 1.0 if estado.puerta_abierta else 0.0,
                "vibracion": 1.0 if estado.vibracion else 0.0,
                "bateria": estado.bateria,
            },
            cfg.NODO_AUDIO: {},
        }

    # -- ciclo principal -----------------------------------------------------
    def avanzar(self, segundos_simulados: float) -> tuple[list[Muestra], list[Evento]]:
        if segundos_simulados <= 0:
            return [], []
        minutos = segundos_simulados / 60.0
        personas_antes = self.estado.personas

        eventos = self._actualizar_cargas(self._personas_esperadas(), minutos)
        self._actualizar_ambiente(minutos)
        self._actualizar_energia(minutos)
        self._actualizar_ocupacion(minutos)
        self._actualizar_vibracion(minutos)
        self._actualizar_bateria(minutos)
        eventos += self._eventos_de_puerta_por_clase(personas_antes)
        if eventos:
            # El nodo de puerta duerme y late cada 30 min, pero ante un evento
            # despierta y reporta enseguida: RF-04 pide registrarlo en 10 s.
            self._reportar_ya(cfg.NODO_PUERTA, "estadoPuerta", "vibracion")

        muestras: list[Muestra] = []
        for nodo, lecturas in self._lecturas_por_nodo().items():
            if nodo in self.estado.nodos_caidos:
                continue
            senal = cfg.SENAL_TIPICA_DBM + self.azar.gauss(0, 3)
            if nodo in self._nodos_con_senal_debil:
                senal = cfg.SENAL_DE_ENLACE_DEBIL_DBM + self.azar.gauss(0, 4)
            for magnitud, valor in list(lecturas.items()) + [("senal", senal)]:
                if not self._toca_enviar(nodo, magnitud):
                    continue
                muestra = self._muestra(nodo, magnitud, valor)
                # La muestra se numera igual aunque se pierda: el hueco de
                # secuencia es lo que deja ver el servidor que falto algo.
                if nodo in self._nodos_con_senal_debil and self.azar.random() < cfg.PERDIDA_CON_ENLACE_DEBIL:
                    continue
                muestras.append(muestra)
        return muestras, eventos

    # -- escenarios de demostracion -----------------------------------------
    def aplicar_escenario(self, nombre: str) -> list[Evento]:
        if nombre not in ESCENARIOS:
            raise ValueError(f"Escenario desconocido: {nombre}")
        self.escenario = nombre
        eventos: list[Evento] = []
        if nombre == "clase":
            self._clase_forzada_hasta = self.reloj.momento + timedelta(hours=1)
            self._olvido_las_luces = False
        elif nombre == "vacio-con-luces":
            self._clase_forzada_hasta = None
            self.estado.personas = 0
            self.estado.conteo = 0
            self._olvido_las_luces = True
        elif nombre == "apertura-fuera-de-horario":
            eventos.append(self._evento_de_puerta("apertura", "apertura forzada en la demo"))
            self._reportar_ya(cfg.NODO_PUERTA, "estadoPuerta", "vibracion")
        elif nombre == "caida-de-nodo":
            self.estado.nodos_caidos.add(cfg.NODO_AMBIENTAL)
        elif nombre == "senal-debil":
            self._nodos_con_senal_debil.add(cfg.NODO_OCUPACION_FONDO)
        elif nombre == "restablecer":
            self.estado.nodos_caidos.clear()
            self._nodos_con_senal_debil.clear()
            self._clase_forzada_hasta = None
            self._olvido_las_luces = False
            self.escenario = "normal"
        return eventos
