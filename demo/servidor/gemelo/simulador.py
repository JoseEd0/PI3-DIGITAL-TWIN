"""Simulador de los 7 nodos oficiales del L-419 (RF-11).

Publica exactamente lo que publicaría el Gateway del docente (módulo `gateway`), en el grupo
`sim`, con los periodos de cada .ino y las mismas reglas de anomalía que calcula cada nodo
(umbrales, histéresis y confirmaciones copiados del código del docente). Así Telegraf, InfluxDB,
Grafana y el servicio del grupo funcionan igual con datos simulados que con datos reales.

El modelo físico es deliberadamente simple: que cada magnitud se mueva por la razón correcta.
Todos sus parámetros del aula salen de config/aula_l419.yaml.
"""

from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import gateway
from .configuracion import ZONA_HORARIA, Aula, Nodo, cargar_aula, cargar_nodos

# --- Constantes del código del docente (vendor/gemelo_iot_profesor/nodo_*.ino) -----------------
CO2_ALERTA_PPM, CO2_CRITICO_PPM, CO2_HISTERESIS, CO2_CONFIRMACIONES = 1000, 1500, 100, 3
CO2_CALENTAMIENTO_S, CO2_PICO_SUBIDA_PPM = 180, 300
CONFORT_T_MIN, CONFORT_T_MAX, HIST_T = 20.0, 26.0, 0.5
HUM_ALTA, HIST_HUM, CAMBIO_T_MAX, VENTANA_CAMBIO_MIN = 70.0, 5.0, 1.5, 5
FACTOR_MESA, ILUM_BAJA, HIST_ILUM = 0.482, 300.0, 30.0
ABIERTA_PROLONGADA_MIN = 10
CAMPO_PUERTA_CERRADA, CAMPO_PUERTA_ABIERTA = 700, 2600
OFFSET_SPL_DB = 120.0

# --- Parámetros del modelo físico (no son datos del aula: son del simulador) -------------------
CO2_EXTERIOR_PPM = 420.0
CO2_POR_PERSONA_M3_H = 0.018  # ~5 L/min de CO2 exhalado por un adulto sentado
TEMPERATURA_BASE_C = 20.5
AMPLITUD_DIARIA_C = 3.0
CALOR_POR_PERSONA_C = 0.12
CALOR_POR_KW_C = 0.8
ENFRIAMIENTO_DEL_AIRE_C = 3.5
CONSTANTE_TERMICA_MIN = 20.0
HUMEDAD_BASE_HR = 62.0
PRESION_BASE_HPA = 1011.5
RUIDO_FONDO_DB = 38.0
RUIDO_CLASE_DB = 58.0
RUIDO_SOBREAFORO_DB = 74.0
RS_R0_AIRE_LIMPIO = 1.0
RS_R0_CON_HUMO = 0.40
GAS_DETECTADO_RS_R0 = 0.70
GAS_CALENTAMIENTO_S = 60
FRACCION_DE_AFORO_EN_CLASE = 0.55
PROBABILIDAD_DE_OLVIDAR_LUCES = 0.6
PERSONAS_PARA_EL_PROYECTOR = 6
PERSONAS_PARA_EL_AIRE = 8
AIRE_ENCIENDE_C, AIRE_APAGA_C = 24.5, 23.0
GRUPO_SIMULADO = "sim"

ESCENARIOS = {
    "normal": "Sigue el horario de clases sin forzar nada",
    "clase": "Entra un grupo ahora (60 % del aforo, puerta cerrada)",
    "vacio-con-luces": "Todos salen y dejan las luces y los PC encendidos",
    "aire-averiado": "Clase con el aire acondicionado encendido pero sin enfriar",
    "sobreaforo": "Entran más personas que el aforo del aula",
    "intrusion-nocturna": "Se adelanta el reloj a las 23:30 y alguien abre la puerta",
    "gas": "El MQ-2 detecta humo o gas",
    "falla-sensor": "El BME280 del nodo ambiente deja de responder",
    "nodo-sin-bateria": "El nodo térmico (5) deja de transmitir",
    "gateway-caido": "El Gateway se desconecta: ningún nodo llega",
    "restablecer": "Vuelve al horario normal y repara todo",
}


class Reloj:
    """Reloj virtual del aula. Con velocidad 1 coincide con la hora real."""

    def __init__(self, inicio: datetime | None = None, velocidad: float = 1.0) -> None:
        self.momento = (inicio or datetime.now(ZONA_HORARIA)).astimezone(ZONA_HORARIA)
        self.velocidad = velocidad
        self.pausado = False

    def avanzar(self, segundos_reales: float) -> float:
        if self.pausado:
            return 0.0
        simulados = segundos_reales * self.velocidad
        self.momento += timedelta(seconds=simulados)
        return simulados

    def saltar_a(self, hora: float) -> None:
        objetivo = self.momento.replace(hour=int(hora), minute=int(hora % 1 * 60), second=0, microsecond=0)
        if objetivo <= self.momento:
            objetivo += timedelta(days=1)
        self.momento = objetivo

    @property
    def hora(self) -> float:
        return self.momento.hour + self.momento.minute / 60 + self.momento.second / 3600

    @property
    def ts_ms(self) -> int:
        return int(self.momento.timestamp() * 1000)


@dataclass
class EstadoDelAula:
    """La verdad física del aula simulada (lo que los sensores intentan medir)."""

    personas: int = 0
    luces: bool = False
    pcs_encendidos: int = 0
    proyector: bool = False
    aire: bool = False
    aire_averiado: bool = False
    puerta_abierta: bool = False
    minutos_puerta_abierta: float = 0.0
    co2: float = CO2_EXTERIOR_PPM
    temperatura: float = TEMPERATURA_BASE_C
    humedad: float = HUMEDAD_BASE_HR
    presion: float = PRESION_BASE_HPA
    lux_mesa: float = 0.0
    ruido_db: float = RUIDO_FONDO_DB
    rs_r0: float = RS_R0_AIRE_LIMPIO
    cruces_pendientes: list[int] = field(default_factory=list)  # +1 entra, -1 sale
    aperturas_pendientes: int = 0
    portazos_pendientes: int = 0

    def potencia_w(self, aula: Aula) -> float:
        """Potencia eléctrica real (el sistema no la mide: es la verdad para validar el proxy)."""
        potencia = aula.potencia_w("base")
        potencia += aula.potencia_luces_w if self.luces else 0.0
        potencia += self.pcs_encendidos * aula.potencia_w("pcs")
        potencia += (aula.cantidad("pcs") - self.pcs_encendidos) * aula.espera_w("pcs")
        potencia += aula.potencia_w("proyector") if self.proyector else aula.espera_w("proyector")
        potencia += aula.potencia_w("aire_acondicionado") if self.aire else 0.0
        return potencia


class NodoSimulado:
    """Un ESP32 con su sensor. Cada subclase replica la lógica de su .ino."""

    def __init__(self, config: Nodo, azar: random.Random) -> None:
        self.config = config
        self.azar = azar
        self.seq = 0
        self.uptime_s = 0.0
        self.desde_el_ultimo_envio = math.inf
        self.encendido = True
        self.sensor_falla = False

    @property
    def mac(self) -> str:
        return f"02:00:00:00:04:1{self.config.id}"

    def avanzar(self, segundos: float, aula: EstadoDelAula, momento: datetime) -> None:
        self.uptime_s += segundos
        self.desde_el_ultimo_envio += segundos
        self.observar(segundos, aula, momento)

    def toca_enviar(self) -> bool:
        return self.encendido and self.desde_el_ultimo_envio >= self.config.periodo_s

    def emitir(self, grupo: str, ts_ms: int) -> tuple[str, str]:
        campos, bits, nivel = self.leer()
        self.seq += 1
        self.desde_el_ultimo_envio = 0.0
        texto = gateway.mensaje(
            nodo=self.config.id, mac=self.mac, seq=self.seq, ts_ms=ts_ms,
            uptime_ms=int(self.uptime_s * 1000), perdidos=0, tipo=self.config.tipo,
            campos=campos, anom_bits=bits, nivel=nivel,
        )
        return gateway.topico(grupo, self.config.id, self.config.tipo), texto

    # Las subclases implementan:
    def observar(self, segundos: float, aula: EstadoDelAula, momento: datetime) -> None:
        """Integra lo que el sensor ve entre dos envíos."""

    def leer(self) -> tuple[dict, int, str | None]:
        raise NotImplementedError


class NodoCO2(NodoSimulado):
    def __init__(self, config: Nodo, azar: random.Random) -> None:
        super().__init__(config, azar)
        self.nivel = 0
        self.candidato, self.confirmaciones = -1, 0
        self.historial: deque[float] = deque(maxlen=6)  # 6 lecturas de 5 s = 30 s
        self.ppm = CO2_EXTERIOR_PPM
        self.temp_interna = TEMPERATURA_BASE_C

    def observar(self, segundos, aula, momento):
        self.ppm = aula.co2 + self.azar.gauss(0, 8)
        self.temp_interna = aula.temperatura + 2

    def _nivel_candidato(self, ppm: float) -> int:
        if ppm >= CO2_CRITICO_PPM:
            return 2
        if ppm >= CO2_ALERTA_PPM:
            return 2 if self.nivel == 2 and ppm >= CO2_CRITICO_PPM - CO2_HISTERESIS else 1
        if self.nivel >= 1 and ppm >= CO2_ALERTA_PPM - CO2_HISTERESIS:
            return 1
        return 0

    def leer(self):
        if self.sensor_falla:
            return {"co2_ppm": -1, "delta_30s": 0, "temp_c": None, "calentando": 0}, 1, "SIN_DATO"
        ppm = int(self.ppm)
        if self.uptime_s < CO2_CALENTAMIENTO_S:
            campos = {"co2_ppm": ppm, "delta_30s": 0, "temp_c": int(self.temp_interna), "calentando": 1}
            return campos, 0, "CALENTANDO"
        delta = int(ppm - self.historial[0]) if len(self.historial) == self.historial.maxlen else 0
        self.historial.append(ppm)
        candidato = self._nivel_candidato(ppm)
        if candidato == self.nivel:
            self.candidato, self.confirmaciones = -1, 0
        else:
            self.confirmaciones = self.confirmaciones + 1 if candidato == self.candidato else 1
            self.candidato = candidato
            if self.confirmaciones >= CO2_CONFIRMACIONES:
                self.nivel, self.candidato, self.confirmaciones = candidato, -1, 0
        bits = (1 << 1) if delta >= CO2_PICO_SUBIDA_PPM else 0
        bits |= {1: 1 << 2, 2: 1 << 3}.get(self.nivel, 0)
        campos = {"co2_ppm": ppm, "delta_30s": delta, "temp_c": int(self.temp_interna), "calentando": 0}
        return campos, bits, gateway.NIVELES_CO2[self.nivel]


class NodoAudio(NodoSimulado):
    def __init__(self, config, azar):
        super().__init__(config, azar)
        self.leq = RUIDO_FONDO_DB
        self.impacto = False
        self.mecanico = False

    def observar(self, segundos, aula, momento):
        self.leq = aula.ruido_db + self.azar.gauss(0, 1.5)
        self.impacto = aula.portazos_pendientes > 0
        self.mecanico = aula.aire

    def leer(self):
        if self.sensor_falla:
            return {"calibrando": 0}, 1, None
        base = RUIDO_FONDO_DB + (3 if self.mecanico else 0)
        lmax = self.leq + abs(self.azar.gauss(4, 1.5)) + (20 if self.impacto else 0)
        fuertes = max(0, min(31, int((self.leq - 60) * 2))) if self.leq > 60 else 0
        bits = 0
        bits |= (1 << 1) if self.impacto else 0
        bits |= (1 << 2) if self.leq > 70 else 0
        bits |= (1 << 3) if self.mecanico and self.leq < 50 else 0
        campos = {
            "leq_db": self.leq, "lmax_db": lmax, "pico_db": lmax + 6, "base_db": base,
            "freq_dom_hz": 120 if self.mecanico else 450 + self.azar.gauss(0, 60),
            "tonal": 0.6 if self.mecanico else 0.15, "bloques_fuertes": fuertes,
            "calibrando": 1 if self.uptime_s < 5 else 0,
        }
        self.impacto = False
        return campos, bits, None


class NodoGas(NodoSimulado):
    def __init__(self, config, azar):
        super().__init__(config, azar)
        self.rs_r0 = RS_R0_AIRE_LIMPIO

    def observar(self, segundos, aula, momento):
        self.rs_r0 = max(0.05, aula.rs_r0 + self.azar.gauss(0, 0.02))

    def leer(self):
        if self.sensor_falla:
            return {"v_ao": None, "rs_r0": None, "do_alarma": 0, "calentando": 0}, 1, None
        calentando = self.uptime_s < GAS_CALENTAMIENTO_S
        # Divisor del módulo con RL=5k a 5 V: v_ao = 5 / (1 + Rs/RL); con R0 ≈ RL en aire limpio.
        v_ao = 5.0 / (1.0 + self.rs_r0)
        rs_r0 = None if calentando else self.rs_r0
        detectado = not calentando and self.rs_r0 < GAS_DETECTADO_RS_R0
        campos = {"v_ao": v_ao, "rs_r0": rs_r0, "do_alarma": int(detectado), "calentando": int(calentando)}
        return campos, (1 << 1) if detectado else 0, None


class NodoLuz(NodoSimulado):
    def __init__(self, config, azar):
        super().__init__(config, azar)
        self.muestras: list[float] = []
        self.baja = False
        self.luces_antes: bool | None = None
        self.luces_ahora = False

    def observar(self, segundos, aula, momento):
        techo = max(0.0, aula.lux_mesa / FACTOR_MESA + self.azar.gauss(0, 3))
        self.muestras.append(techo)
        self.luces_ahora = aula.luces

    def leer(self):
        if self.sensor_falla or not self.muestras:
            return {}, 1, None
        lux = sum(self.muestras) / len(self.muestras)
        mesa = lux * FACTOR_MESA
        if mesa < ILUM_BAJA:
            self.baja = True
        elif mesa > ILUM_BAJA + HIST_ILUM:
            self.baja = False
        cambio = 0
        if self.luces_antes is not None and self.luces_ahora != self.luces_antes:
            cambio = 1 if self.luces_ahora else -1
        self.luces_antes = self.luces_ahora
        campos = {"lux": lux, "lux_min": min(self.muestras), "lux_max": max(self.muestras),
                  "lux_mesa_est": mesa, "luces_cambio": cambio}
        self.muestras = []
        return campos, (1 << 1) if self.baja else 0, None


class NodoTermico(NodoSimulado):
    def __init__(self, config, azar):
        super().__init__(config, azar)
        self.entradas = self.salidas = 0
        self.ocupacion = 0
        self.en_vista = 0
        self.t_fondo = 22.0

    def observar(self, segundos, aula, momento):
        for sentido in aula.cruces_pendientes:
            if sentido > 0:
                self.entradas += 1
            else:
                self.salidas += 1
            self.ocupacion = max(0, self.ocupacion + sentido)
        self.en_vista = max(self.en_vista, min(2, len(aula.cruces_pendientes)))
        self.t_fondo = aula.temperatura + 1.0

    def leer(self):
        if self.sensor_falla:
            return {"calibrando": 0}, 1, None
        campos = {
            "entradas": self.entradas, "salidas": self.salidas, "ocupacion_est": self.ocupacion,
            "personas_en_vista": self.en_vista, "cruces_dudosos": 0, "t_fondo": self.t_fondo,
            "t_max": self.t_fondo + (11.0 if self.en_vista else 0.6), "calibrando": 1 if self.uptime_s < 3 else 0,
        }
        self.entradas = self.salidas = self.en_vista = 0
        return campos, 0, None


class NodoMagnetico(NodoSimulado):
    def __init__(self, config, azar):
        super().__init__(config, azar)
        self.abierta = False
        self.aperturas = 0
        self.segundos_abierta = 0.0
        self.minutos_abierta = 0.0
        self.cambio = False

    def observar(self, segundos, aula, momento):
        self.cambio = aula.puerta_abierta != self.abierta or aula.aperturas_pendientes > 0
        self.aperturas += aula.aperturas_pendientes
        self.abierta = aula.puerta_abierta
        self.minutos_abierta = aula.minutos_puerta_abierta
        if aula.puerta_abierta:
            self.segundos_abierta += segundos

    def toca_enviar(self) -> bool:
        # El nodo del docente envía de inmediato ante un cambio, además del periódico.
        return self.encendido and (self.cambio or super().toca_enviar())

    def leer(self):
        if self.sensor_falla:
            return {"campo_raw": 4095}, 1, None
        raw = (CAMPO_PUERTA_ABIERTA if self.abierta else CAMPO_PUERTA_CERRADA) + int(self.azar.gauss(0, 40))
        campos = {"puerta_abierta": int(self.abierta), "aperturas": self.aperturas,
                  "seg_abierta": self.segundos_abierta, "campo_raw": raw}
        bits = (1 << 1) if self.abierta and self.minutos_abierta >= ABIERTA_PROLONGADA_MIN else 0
        self.aperturas, self.segundos_abierta, self.cambio = 0, 0.0, False
        return campos, bits, None


class NodoAmbiente(NodoSimulado):
    def __init__(self, config, azar):
        super().__init__(config, azar)
        self.temp = TEMPERATURA_BASE_C
        self.hum = HUMEDAD_BASE_HR
        self.pres = PRESION_BASE_HPA
        self.fuera_de_confort = False
        self.humedad_alta = False
        self.historial: deque[float] = deque()

    def observar(self, segundos, aula, momento):
        self.temp = aula.temperatura + self.azar.gauss(0, 0.05)
        self.hum = aula.humedad + self.azar.gauss(0, 0.3)
        self.pres = aula.presion + self.azar.gauss(0, 0.05)

    def leer(self):
        if self.sensor_falla:
            return {"temp_c": None, "hum_pct": None, "pres_hpa": None}, 1, None
        t = self.temp
        if t < CONFORT_T_MIN or t > CONFORT_T_MAX:
            self.fuera_de_confort = True
        elif CONFORT_T_MIN + HIST_T <= t <= CONFORT_T_MAX - HIST_T:
            self.fuera_de_confort = False
        if self.hum >= HUM_ALTA:
            self.humedad_alta = True
        elif self.hum < HUM_ALTA - HIST_HUM:
            self.humedad_alta = False
        self.historial.append(t)
        lecturas_en_ventana = int(VENTANA_CAMBIO_MIN * 60 / self.config.periodo_s)
        while len(self.historial) > lecturas_en_ventana:
            self.historial.popleft()
        cambio_rapido = max(self.historial) - min(self.historial) > CAMBIO_T_MAX
        bits = ((1 << 1) if self.fuera_de_confort else 0) | ((1 << 2) if self.humedad_alta else 0)
        bits |= (1 << 3) if cambio_rapido else 0
        return {"temp_c": t, "hum_pct": self.hum, "pres_hpa": self.pres}, bits, None


CLASES_DE_NODO = {
    "co2": NodoCO2, "audio": NodoAudio, "gas": NodoGas, "luz": NodoLuz,
    "termico": NodoTermico, "magnetico": NodoMagnetico, "ambiente": NodoAmbiente,
}


class Simulador:
    """El aula, sus 7 nodos y el Gateway, en el formato oficial."""

    def __init__(self, reloj: Reloj | None = None, aula: Aula | None = None,
                 semilla: int | None = 419, grupo: str = GRUPO_SIMULADO) -> None:
        self.reloj = reloj or Reloj()
        self.aula = aula or cargar_aula()
        self.grupo = grupo
        self.azar = random.Random(semilla)
        self.estado = EstadoDelAula()
        self.nodos = {n.id: CLASES_DE_NODO[n.tipo](n, self.azar) for n in cargar_nodos().values()}
        self.escenario = "normal"
        self.gateway_en_linea = True
        self._clase_forzada: tuple[datetime, int] | None = None
        self._luces_olvidadas = False
        self._olvido_decidido_el: int | None = None
        self._estado_del_gateway_pendiente: str | None = "online"

    # -- horario y ocupación ------------------------------------------------------------------
    def _personas_esperadas(self) -> int:
        ahora = self.reloj.momento
        if self._clase_forzada and ahora < self._clase_forzada[0]:
            return self._clase_forzada[1]
        if self.escenario == "intrusion-nocturna":
            return 1
        if not self.aula.es_dia_de_clase(ahora.weekday()):
            return 0
        hora = self.reloj.hora
        for inicio, fin in self.aula.bloques_de_clase:
            if inicio <= hora < fin:
                llenado = min(1.0, (hora - inicio) * 60 / 8)
                vaciado = min(1.0, (fin - hora) * 60 / 6)
                return round(self.aula.aforo * FRACCION_DE_AFORO_EN_CLASE * min(llenado, vaciado))
        return 0

    def _mover_personas(self, objetivo: int, minutos: float) -> None:
        estado = self.estado
        paso = max(1, int(minutos * 2))
        diferencia = objetivo - estado.personas
        cruces = max(-paso, min(paso, diferencia))
        if cruces:
            if not estado.puerta_abierta:
                estado.puerta_abierta = True
                estado.aperturas_pendientes += 1
            estado.cruces_pendientes += [1 if cruces > 0 else -1] * abs(cruces)
            estado.personas += cruces
        elif estado.puerta_abierta and self.escenario not in ("intrusion-nocturna",):
            # La puerta se cierra sola al terminar de pasar la gente; a veces con portazo.
            estado.puerta_abierta = False
            if self.azar.random() < 0.2:
                estado.portazos_pendientes += 1

    # -- cargas eléctricas ----------------------------------------------------------------------
    def _actualizar_cargas(self) -> None:
        estado, aula = self.estado, self.aula
        dia = self.reloj.momento.toordinal()
        ultima_clase = aula.bloques_de_clase[-1][1]
        if estado.personas > 0:
            estado.luces = True
            estado.pcs_encendidos = min(aula.cantidad("pcs"), estado.personas // 2 + 2)
            estado.proyector = estado.personas >= PERSONAS_PARA_EL_PROYECTOR
            self._luces_olvidadas = False
        else:
            estado.proyector = False
            if self.escenario == "vacio-con-luces" or self._luces_olvidadas:
                estado.luces = True
                estado.pcs_encendidos = max(estado.pcs_encendidos, aula.cantidad("pcs") // 2)
            else:
                estado.luces = False
                estado.pcs_encendidos = 0
            if ultima_clase <= self.reloj.hora < ultima_clase + 0.5 and self._olvido_decidido_el != dia:
                self._olvido_decidido_el = dia
                self._luces_olvidadas = self.azar.random() < PROBABILIDAD_DE_OLVIDAR_LUCES
            if abs(self.reloj.hora - aula.ronda_del_vigilante) < 0.05:
                self._luces_olvidadas = False  # el vigilante apaga lo que encuentra
        if estado.personas < PERSONAS_PARA_EL_AIRE and self.escenario != "aire-averiado":
            estado.aire = False
        elif estado.temperatura > AIRE_ENCIENDE_C or self.escenario == "aire-averiado":
            estado.aire = True
        elif estado.temperatura < AIRE_APAGA_C:
            estado.aire = False

    # -- física -------------------------------------------------------------------------------
    def _actualizar_ambiente(self, minutos: float) -> None:
        estado, aula = self.estado, self.aula
        horas = minutos / 60
        renovaciones = aula.valor(
            "ambiente.renovaciones_por_hora_puerta_abierta" if estado.puerta_abierta
            else "ambiente.renovaciones_por_hora_puerta_cerrada"
        )
        generacion = estado.personas * CO2_POR_PERSONA_M3_H / aula.volumen_m3 * 1e6
        estado.co2 += (generacion - renovaciones * (estado.co2 - CO2_EXTERIOR_PPM)) * min(horas, 0.25)
        estado.co2 = max(CO2_EXTERIOR_PPM, estado.co2)

        hora = self.reloj.hora
        curva = AMPLITUD_DIARIA_C * math.sin(math.pi * max(0.0, hora - 6.0) / 14.0)
        enfria = estado.aire and not estado.aire_averiado
        objetivo = (TEMPERATURA_BASE_C + curva + estado.personas * CALOR_POR_PERSONA_C
                    + CALOR_POR_KW_C * estado.potencia_w(aula) / 1000
                    - (ENFRIAMIENTO_DEL_AIRE_C if enfria else 0.0))
        estado.temperatura += (objetivo - estado.temperatura) * min(1.0, minutos / CONSTANTE_TERMICA_MIN)
        humedad_objetivo = (HUMEDAD_BASE_HR + 0.4 * estado.personas
                            - 1.2 * (estado.temperatura - TEMPERATURA_BASE_C) - (6 if enfria else 0))
        estado.humedad += (humedad_objetivo - estado.humedad) * min(1.0, minutos / CONSTANTE_TERMICA_MIN)

        natural = max(0.0, math.sin(math.pi * (hora - 6.0) / 12.0)) * aula.valor("ambiente.lux_mesa_natural_maxima")
        artificial = aula.cantidad("luminarias") * aula.valor("ambiente.lux_mesa_por_luminaria") if estado.luces else 0
        estado.lux_mesa = natural + artificial

        if self.escenario == "sobreaforo":
            estado.ruido_db = RUIDO_SOBREAFORO_DB
        elif estado.personas > 0:
            estado.ruido_db = RUIDO_CLASE_DB + min(8.0, estado.personas * 0.3)
        else:
            estado.ruido_db = RUIDO_FONDO_DB + (4 if estado.aire else 0)

        estado.rs_r0 = RS_R0_CON_HUMO if self.escenario == "gas" else RS_R0_AIRE_LIMPIO
        estado.minutos_puerta_abierta = estado.minutos_puerta_abierta + minutos if estado.puerta_abierta else 0.0

    # -- ciclo ----------------------------------------------------------------------------------
    def avanzar(self, segundos_reales: float) -> list[tuple[str, str, bool]]:
        """Avanza el aula y devuelve los mensajes (tópico, json, retenido) a publicar."""
        segundos = self.reloj.avanzar(segundos_reales)
        if segundos <= 0:
            return []
        # Pasos de a lo más 5 s simulados para que la física y los periodos sigan siendo estables.
        pasos = max(1, math.ceil(segundos / 5))
        mensajes: list[tuple[str, str, bool]] = []
        for _ in range(pasos):
            mensajes += self._paso(segundos / pasos)
        if self._estado_del_gateway_pendiente:
            mensajes.append((gateway.topico_estado_gateway(self.grupo), self._estado_del_gateway_pendiente, True))
            self._estado_del_gateway_pendiente = None
        return mensajes

    def _paso(self, segundos: float) -> list[tuple[str, str, bool]]:
        minutos = segundos / 60
        self._mover_personas(self._personas_esperadas(), minutos)
        self._actualizar_cargas()
        self._actualizar_ambiente(minutos)
        momento = self.reloj.momento
        for nodo in self.nodos.values():
            nodo.avanzar(segundos, self.estado, momento)
        self.estado.cruces_pendientes.clear()
        self.estado.aperturas_pendientes = 0
        self.estado.portazos_pendientes = 0
        if not self.gateway_en_linea:
            return []
        return [(*nodo.emitir(self.grupo, self.reloj.ts_ms), False)
                for nodo in self.nodos.values() if nodo.toca_enviar()]

    # -- escenarios -----------------------------------------------------------------------------
    def aplicar_escenario(self, nombre: str) -> None:
        if nombre not in ESCENARIOS:
            raise ValueError(f"Escenario desconocido: {nombre}")
        ahora = self.reloj.momento
        if nombre == "restablecer":
            self._restablecer()
            return
        self.escenario = nombre
        aforo = self.aula.aforo
        if nombre in ("clase", "aire-averiado"):
            self._clase_forzada = (ahora + timedelta(hours=1), round(aforo * 0.6))
            self.estado.aire_averiado = nombre == "aire-averiado"
        elif nombre == "sobreaforo":
            self._clase_forzada = (ahora + timedelta(hours=1), aforo + 4)
        elif nombre == "vacio-con-luces":
            self._clase_forzada = (ahora + timedelta(hours=2), 0)
        elif nombre == "intrusion-nocturna":
            self._clase_forzada = None
            self.reloj.saltar_a(23.5)
        elif nombre == "falla-sensor":
            self.nodos[7].sensor_falla = True
        elif nombre == "nodo-sin-bateria":
            self.nodos[5].encendido = False
        elif nombre == "gateway-caido":
            self.gateway_en_linea = False
            self._estado_del_gateway_pendiente = "offline"

    def _restablecer(self) -> None:
        self.escenario = "normal"
        self._clase_forzada = None
        self._luces_olvidadas = False
        self.estado.aire_averiado = False
        for nodo in self.nodos.values():
            nodo.encendido, nodo.sensor_falla = True, False
        if not self.gateway_en_linea:
            self.gateway_en_linea = True
            self._estado_del_gateway_pendiente = "online"

    # -- verdad del simulador (para validar estimaciones, no para el dashboard) ------------------
    def verdad(self) -> dict:
        estado = self.estado
        return {
            "personas": estado.personas, "luces": estado.luces, "pcs": estado.pcs_encendidos,
            "proyector": estado.proyector, "aire": estado.aire, "aireAveriado": estado.aire_averiado,
            "puertaAbierta": estado.puerta_abierta, "potenciaW": round(estado.potencia_w(self.aula), 1),
        }
