"""Bus de mensajes en proceso.

En el laboratorio real este bus es Mosquitto: los nodos publican por MQTT y el
servidor se suscribe (docs/00-idea-principal.md seccion 6.1). En la demo no hay
broker que instalar, asi que el simulador publica en este bus con exactamente el
mismo contrato de topicos. Cambiar a MQTT es reemplazar este archivo por un
cliente paho que llame a los mismos suscriptores.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable

from .contrato import Evento, Muestra

log = logging.getLogger(__name__)

SuscriptorDeMuestras = Callable[[Muestra], None]
SuscriptorDeEventos = Callable[[Evento], None]


class Bus:
    def __init__(self) -> None:
        self._de_muestras: list[SuscriptorDeMuestras] = []
        self._de_eventos: list[SuscriptorDeEventos] = []

    def suscribir_muestras(self, suscriptor: SuscriptorDeMuestras) -> None:
        self._de_muestras.append(suscriptor)

    def suscribir_eventos(self, suscriptor: SuscriptorDeEventos) -> None:
        self._de_eventos.append(suscriptor)

    def publicar_muestras(self, muestras: Iterable[Muestra]) -> None:
        for muestra in muestras:
            for suscriptor in self._de_muestras:
                self._entregar(suscriptor, muestra)

    def publicar_eventos(self, eventos: Iterable[Evento]) -> None:
        for evento in eventos:
            for suscriptor in self._de_eventos:
                self._entregar(suscriptor, evento)

    @staticmethod
    def _entregar(suscriptor, mensaje) -> None:
        # Un suscriptor que falla no puede tumbar la ingesta de los demas: es el
        # mismo criterio que en el servidor real, donde el motor de reglas y el
        # almacen son independientes.
        try:
            suscriptor(mensaje)
        except Exception:
            log.exception("El suscriptor %r fallo procesando %r", suscriptor, mensaje)
