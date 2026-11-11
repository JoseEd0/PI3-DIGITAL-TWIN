"""Estado del aula según lo que llega del Gateway: últimas lecturas, salud y variables derivadas.

Las variables derivadas (`derivado.*`) son lo que ningún sensor mide solo y el servicio infiere
combinando nodos: si el aula está vacía, si las luces quedaron prendidas, si es fuera de horario,
cuántos minutos lleva el consumo fantasma. Los grafos causales y los evaluadores de RA leen de
aquí con rutas "<tipo>.<campo>" o "derivado.<nombre>".
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime

from .configuracion import ZONA_HORARIA, Aula, Nodo
from .gateway import Lectura

# Las luces se dan por encendidas si la luz sobre la mesa supera a la natural esperada en esta
# fracción de lo que aportan todas las luminarias juntas (proxy calibrable con el nodo de luz).
FRACCION_DE_LUZ_ARTIFICIAL_PARA_LUCES = 0.5
HORAS_DE_LUZ_NATURAL = (6.0, 18.0)


@dataclass
class EstadoDeNodo:
    config: Nodo
    ultima: Lectura | None = None
    recibido: datetime | None = None
    mensajes: int = 0

    def segundos_sin_datos(self, ahora: datetime) -> float:
        return math.inf if self.recibido is None else max(0.0, (ahora - self.recibido).total_seconds())


@dataclass
class EstadoDelAula:
    aula: Aula
    nodos: dict[int, EstadoDeNodo]
    tolerancia_periodos: float = 3
    tolerancia_minima_s: float = 30
    gateway_en_linea: bool | None = None
    ahora: datetime | None = None
    luces_por_cambio: bool | None = None
    inicio_fantasma: datetime | None = None
    ultima_apertura: datetime | None = None
    puerta_cerrada_desde: datetime | None = None
    niveles_ra: dict[str, int] = field(default_factory=dict)

    @classmethod
    def nuevo(cls, aula: Aula, nodos: dict[int, Nodo], periodos_tolerados: float, minimo_s: float):
        return cls(aula, {i: EstadoDeNodo(n) for i, n in nodos.items()}, periodos_tolerados, minimo_s)

    # -- ingesta --------------------------------------------------------------------------------
    def registrar(self, lectura: Lectura, recibido: datetime) -> None:
        nodo = self.nodos.get(lectura.nodo)
        if nodo is None or nodo.config.tipo != lectura.tipo:
            return
        nodo.ultima, nodo.recibido = lectura, recibido
        nodo.mensajes += 1
        self.ahora = max(self.ahora or recibido, recibido)
        if lectura.tipo == "luz" and lectura.campos.get("luces_cambio"):
            self.luces_por_cambio = lectura.campos["luces_cambio"] > 0
        if lectura.tipo == "magnetico":
            self._registrar_puerta(lectura, recibido)
        self._actualizar_fantasma(recibido)

    def _registrar_puerta(self, lectura: Lectura, momento: datetime) -> None:
        abierta = bool(lectura.campos.get("puerta_abierta"))
        if abierta or lectura.campos.get("aperturas"):
            self.ultima_apertura = momento
            self.puerta_cerrada_desde = None if abierta else momento
        elif self.puerta_cerrada_desde is None:
            self.puerta_cerrada_desde = momento

    def _actualizar_fantasma(self, momento: datetime) -> None:
        if self.luces_encendidas() and self.aula_vacia():
            self.inicio_fantasma = self.inicio_fantasma or momento
        else:
            self.inicio_fantasma = None

    def marcar_reloj(self, ahora: datetime) -> None:
        """Avanza el 'ahora' aunque no lleguen mensajes (para detectar silencios)."""
        self.ahora = max(self.ahora or ahora, ahora)

    # -- lecturas -------------------------------------------------------------------------------
    def campo(self, tipo: str, nombre: str):
        for nodo in self.nodos.values():
            if nodo.config.tipo == tipo and nodo.ultima is not None and self._vigente(nodo):
                return nodo.ultima.campos.get(nombre)
        return None

    def anomalias(self, tipo: str) -> tuple[str, ...] | None:
        """Anomalías del último mensaje vigente; None si el nodo no tiene datos (desconocido)."""
        for nodo in self.nodos.values():
            if nodo.config.tipo == tipo and nodo.ultima is not None and self._vigente(nodo):
                return nodo.ultima.anomalias
        return None

    def _vigente(self, nodo: EstadoDeNodo) -> bool:
        return self.ahora is None or not self.nodo_caido(nodo)

    def tolerancia_s(self, nodo: EstadoDeNodo) -> float:
        return max(self.tolerancia_minima_s, nodo.config.periodo_s * self.tolerancia_periodos)

    def nodo_caido(self, nodo: EstadoDeNodo) -> bool:
        return self.ahora is not None and nodo.segundos_sin_datos(self.ahora) > self.tolerancia_s(nodo)

    # -- derivados ------------------------------------------------------------------------------
    def ocupacion(self) -> int | None:
        valor = self.campo("termico", "ocupacion_est")
        return None if valor is None else int(valor)

    def aula_vacia(self) -> bool | None:
        ocupacion = self.ocupacion()
        return None if ocupacion is None else ocupacion == 0

    def hora(self) -> float | None:
        if self.ahora is None:
            return None
        local = self.ahora.astimezone(ZONA_HORARIA)
        return local.hour + local.minute / 60

    def lux_natural_esperada(self) -> float | None:
        hora = self.hora()
        if hora is None:
            return None
        inicio, fin = HORAS_DE_LUZ_NATURAL
        fase = max(0.0, math.sin(math.pi * (hora - inicio) / (fin - inicio)))
        return fase * self.aula.valor("ambiente.lux_mesa_natural_maxima")

    def luces_encendidas(self) -> bool | None:
        mesa = self.campo("luz", "lux_mesa_est")
        natural = self.lux_natural_esperada()
        if mesa is None or natural is None:
            return self.luces_por_cambio
        aporte_total = self.aula.cantidad("luminarias") * self.aula.valor("ambiente.lux_mesa_por_luminaria")
        return mesa - natural >= FRACCION_DE_LUZ_ARTIFICIAL_PARA_LUCES * aporte_total

    def fuera_de_horario(self) -> bool | None:
        if self.ahora is None:
            return None
        local = self.ahora.astimezone(ZONA_HORARIA)
        return not self.aula.dentro_de_horario(local.weekday(), local.hour + local.minute / 60)

    def minutos(self, desde: datetime | None) -> float:
        if desde is None or self.ahora is None:
            return 0.0
        return max(0.0, (self.ahora - desde).total_seconds() / 60)

    def _sin_datos(self, nodo: EstadoDeNodo) -> bool | None:
        if self.ahora is None:
            return None
        return nodo.recibido is None or self.nodo_caido(nodo)

    def nodos_sin_datos(self) -> list[int]:
        return [i for i, nodo in self.nodos.items() if self._sin_datos(nodo)]

    def derivados(self) -> dict:
        ocupacion = self.ocupacion()
        aforo = self.aula.aforo
        puerta = self.campo("magnetico", "puerta_abierta")
        return {
            "ocupacion": ocupacion,
            "ocupacion_fraccion": None if ocupacion is None else ocupacion / aforo,
            "aula_vacia": self.aula_vacia(),
            "luces_encendidas": self.luces_encendidas(),
            "lux_natural_esperada": self.lux_natural_esperada(),
            "fuera_de_horario": self.fuera_de_horario(),
            "puerta_abierta": None if puerta is None else bool(puerta),
            "minutos_puerta_cerrada": self.minutos(self.puerta_cerrada_desde),
            "minutos_fantasma": self.minutos(self.inicio_fantasma),
            "nodos_sin_datos": len(self.nodos_sin_datos()),
            "caidos": {str(i): self._sin_datos(n) for i, n in self.nodos.items()},
            "fraccion_nodos_sin_datos": len(self.nodos_sin_datos()) / len(self.nodos),
            "gateway_offline": self.gateway_en_linea is False,
            "hora": self.hora(),
            "ra": dict(self.niveles_ra),
        }

    def valor(self, ruta: str):
        """Lee 'tipo.campo', 'tipo.anomalias' o 'derivado.nombre' (y 'derivado.ra.RA-03')."""
        partes = ruta.split(".")
        if partes[0] == "derivado":
            valor = self.derivados()
            for parte in partes[1:]:
                if not isinstance(valor, dict):
                    return None
                valor = valor.get(parte)
            return valor
        tipo, nombre = partes[0], ".".join(partes[1:])
        if nombre == "anomalias":
            return self.anomalias(tipo)
        return self.campo(tipo, nombre)

    def salud(self) -> list[dict]:
        filas = []
        for ident, nodo in self.nodos.items():
            ultima = nodo.ultima
            filas.append({
                "nodo": ident, "tipo": nodo.config.tipo, "sensor": nodo.config.sensor,
                "programa": nodo.config.programa, "periodoS": nodo.config.periodo_s,
                "toleranciaS": self.tolerancia_s(nodo),
                "segundosSinDatos": None if self.ahora is None or nodo.recibido is None
                else round(nodo.segundos_sin_datos(self.ahora), 1),
                "caido": self.nodo_caido(nodo) or nodo.recibido is None,
                "perdidos": ultima.perdidos if ultima else None,
                "seq": ultima.seq if ultima else None,
                "falla": bool(ultima and any(a.startswith("FALLO") for a in ultima.anomalias)),
                "anomalias": list(ultima.anomalias) if ultima else [],
                "mensajes": nodo.mensajes,
            })
        return filas
