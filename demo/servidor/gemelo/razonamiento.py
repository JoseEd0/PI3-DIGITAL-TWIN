"""Razonamiento con grafos causales dirigidos, según la metodología SymCure que enseña el docente.

Fuente: docs/curso/texto/symcure-grafos-dirigidos.md (Figueroa, basado en Kapadia, 2003).

- Cada nodo es un evento discreto con valor verdadero (V), falso (F), sospechoso (S) o
  desconocido (D).
- Las aristas van de causa a efecto. Cada evento tiene lógica de **entrada** (OR, AND, N/M o IF:
  cómo lo producen sus causas) y lógica de **salida** (AND u OR: si produce siempre todos sus
  efectos o solo algunos).
- **Aguas arriba (diagnóstico):** de un efecto observado hacia sus causas posibles.
- **Aguas abajo (predicción):** de las causas hacia los efectos esperados.
- Lo observado (especificado) prevalece siempre sobre lo inferido.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum

MAXIMO_DE_ITERACIONES = 50


class Valor(str, Enum):
    VERDADERO = "V"
    FALSO = "F"
    SOSPECHOSO = "S"
    DESCONOCIDO = "D"


V, F, S, D = Valor.VERDADERO, Valor.FALSO, Valor.SOSPECHOSO, Valor.DESCONOCIDO
LOGICAS_DE_ENTRADA = {"OR", "AND", "NM", "IF"}
LOGICAS_DE_SALIDA = {"AND", "OR"}
# "condicion" es un contexto observado (aula vacía, fuera de horario): no es una causa a corregir.
CLASES = {"causa", "condicion", "intermedio", "sintoma", "efecto"}


@dataclass
class Evento:
    id: str
    texto: str
    clase: str = "intermedio"
    entrada: str = "OR"
    salida: str = "AND"
    fraccion: float = 0.5  # N/M: fracción de causas verdaderas que basta
    condicion: str | None = None  # IF: evento de contexto que habilita la propagación
    observable: dict | None = None
    recomendacion: str = ""
    causas: list[str] = field(default_factory=list)
    efectos: list[str] = field(default_factory=list)


class GrafoInvalido(ValueError):
    pass


@dataclass
class Grafo:
    id: str
    ra: str
    titulo: str
    evento_central: str
    eventos: dict[str, Evento]

    @classmethod
    def desde_diccionario(cls, identificador: str, datos: dict) -> "Grafo":
        eventos: dict[str, Evento] = {}
        for crudo in datos.get("eventos", []):
            evento = Evento(
                id=crudo["id"], texto=crudo["texto"], clase=crudo.get("clase", "intermedio"),
                entrada=str(crudo.get("entrada", "OR")).upper().replace("/", ""),
                salida=str(crudo.get("salida", "AND")).upper(),
                fraccion=float(crudo.get("fraccion", 0.5)), condicion=crudo.get("condicion"),
                observable=crudo.get("observable"), recomendacion=crudo.get("recomendacion", ""),
            )
            if evento.id in eventos:
                raise GrafoInvalido(f"{identificador}: evento repetido '{evento.id}'")
            eventos[evento.id] = evento
        for causa, efecto in datos.get("aristas", []):
            for extremo in (causa, efecto):
                if extremo not in eventos:
                    raise GrafoInvalido(f"{identificador}: la arista usa el evento inexistente '{extremo}'")
            eventos[causa].efectos.append(efecto)
            eventos[efecto].causas.append(causa)
        grafo = cls(identificador, datos["ra"], datos["titulo"], datos["evento_central"], eventos)
        grafo.validar()
        return grafo

    def validar(self) -> None:
        if self.evento_central not in self.eventos:
            raise GrafoInvalido(f"{self.id}: el evento central '{self.evento_central}' no existe")
        for evento in self.eventos.values():
            if evento.entrada not in LOGICAS_DE_ENTRADA:
                raise GrafoInvalido(f"{self.id}/{evento.id}: entrada '{evento.entrada}' no es OR, AND, NM ni IF")
            if evento.salida not in LOGICAS_DE_SALIDA:
                raise GrafoInvalido(f"{self.id}/{evento.id}: salida '{evento.salida}' no es AND ni OR")
            if evento.clase not in CLASES:
                raise GrafoInvalido(f"{self.id}/{evento.id}: clase '{evento.clase}' desconocida")
            if evento.entrada == "IF" and evento.condicion not in evento.causas:
                raise GrafoInvalido(f"{self.id}/{evento.id}: la condición IF debe ser una de sus causas")
            if evento.clase in ("causa", "condicion") and evento.causas:
                raise GrafoInvalido(f"{self.id}/{evento.id}: una causa raíz no puede tener causas")
        self.orden_topologico()  # lanza si hay ciclos

    def orden_topologico(self) -> list[str]:
        pendientes = {i: len(e.causas) for i, e in self.eventos.items()}
        cola = deque(i for i, n in pendientes.items() if n == 0)
        orden: list[str] = []
        while cola:
            actual = cola.popleft()
            orden.append(actual)
            for efecto in self.eventos[actual].efectos:
                pendientes[efecto] -= 1
                if pendientes[efecto] == 0:
                    cola.append(efecto)
        if len(orden) != len(self.eventos):
            raise GrafoInvalido(f"{self.id}: el grafo tiene ciclos")
        return orden


# --- Lógica de entrada (propagación aguas abajo), tablas de las diapositivas de SymCure ----------

def _entrada_or(valores: list[Valor]) -> Valor:
    if V in valores:
        return V
    if S in valores:
        return S
    if D in valores:
        return D
    return F


def _entrada_and(valores: list[Valor]) -> Valor:
    if all(v == V for v in valores):
        return V
    if F in valores:
        return F
    if all(v in (V, S) for v in valores):
        return S
    return D


def _entrada_nm(valores: list[Valor], fraccion: float) -> Valor:
    total = len(valores)
    verdaderos = valores.count(V)
    sospechosos = valores.count(S)
    desconocidos = valores.count(D)
    if verdaderos / total >= fraccion:
        return V
    if (verdaderos + sospechosos) / total >= fraccion:
        return S
    if (verdaderos + sospechosos + desconocidos) / total >= fraccion:
        return D
    return F


def valor_por_entrada(evento: Evento, valores_de_causas: dict[str, Valor]) -> Valor:
    if evento.entrada == "IF":
        condicion = valores_de_causas.get(evento.condicion or "", D)
        resto = [v for c, v in valores_de_causas.items() if c != evento.condicion]
        if condicion == F:
            return F
        propuesto = _entrada_or(resto) if resto else V
        if condicion == V:
            return propuesto
        return D if propuesto in (V, S) else propuesto
    valores = list(valores_de_causas.values())
    if evento.entrada == "AND":
        return _entrada_and(valores)
    if evento.entrada == "NM":
        return _entrada_nm(valores, evento.fraccion)
    return _entrada_or(valores)


# --- Motor ------------------------------------------------------------------------------------

@dataclass
class Diagnostico:
    grafo: str
    ra: str
    titulo: str
    valores: dict[str, Valor]
    especificados: set[str]
    causas_confirmadas: list[dict]
    causas_sospechosas: list[dict]
    causas_descartadas: list[dict]
    efectos_esperados: list[dict]
    recomendaciones: list[str]

    @property
    def activo(self) -> bool:
        return self.valores.get(self._central, D) == V

    _central: str = ""

    def como_diccionario(self) -> dict:
        return {
            "grafo": self.grafo, "ra": self.ra, "titulo": self.titulo, "activo": self.activo,
            "valores": {k: v.value for k, v in self.valores.items()},
            "observados": sorted(self.especificados),
            "causasConfirmadas": self.causas_confirmadas, "causasSospechosas": self.causas_sospechosas,
            "causasDescartadas": self.causas_descartadas, "efectosEsperados": self.efectos_esperados,
            "recomendaciones": self.recomendaciones,
        }


class Motor:
    """Propaga observaciones por un grafo hasta un punto fijo."""

    def __init__(self, grafo: Grafo) -> None:
        self.grafo = grafo

    def diagnosticar(self, observaciones: dict[str, bool | None]) -> Diagnostico:
        eventos = self.grafo.eventos
        valores: dict[str, Valor] = {i: D for i in eventos}
        especificados = {i for i, obs in observaciones.items() if obs is not None and i in eventos}
        for i in especificados:
            valores[i] = V if observaciones[i] else F

        orden = self.grafo.orden_topologico()
        for _ in range(MAXIMO_DE_ITERACIONES):
            antes = dict(valores)
            self._aguas_arriba(valores, especificados, list(reversed(orden)))
            self._aguas_abajo(valores, especificados, orden)
            if valores == antes:
                break
        return self._resumir(valores, especificados)

    @staticmethod
    def _proponer(valores: dict[str, Valor], especificados: set[str], evento: str, propuesto: Valor) -> None:
        # Se concilia con lo que ya se sabe: los desconocidos no pisan, y lo observado no se toca.
        if evento in especificados or propuesto == D:
            return
        actual = valores[evento]
        if actual in (V, F) and propuesto == S:
            return
        valores[evento] = propuesto

    def _aguas_arriba(self, valores, especificados, orden_inverso) -> None:
        for ident in orden_inverso:
            evento = self.grafo.eventos[ident]
            if not evento.causas:
                continue
            valor = valores[ident]
            if valor == V:
                self._explicar_verdadero(evento, valores, especificados)
            elif valor == F:
                for causa in evento.causas:
                    # Una causa con salida AND produce siempre todos sus efectos: si este efecto
                    # no ocurrió, esa causa queda descartada.
                    if self.grafo.eventos[causa].salida == "AND":
                        self._proponer(valores, especificados, causa, F)

    def _explicar_verdadero(self, evento: Evento, valores, especificados) -> None:
        causas = [c for c in evento.causas if c != evento.condicion]
        if evento.entrada == "IF" and evento.condicion:
            self._proponer(valores, especificados, evento.condicion, V)
        if evento.entrada == "AND":
            for causa in causas:
                self._proponer(valores, especificados, causa, V)
            return
        posibles = [c for c in causas if valores[c] != F]
        if len(posibles) == 1 and evento.entrada != "NM":
            # Única causa posible de un evento verdadero: tiene que ser verdadera.
            self._proponer(valores, especificados, posibles[0], V)
            return
        if not any(valores[c] == V for c in causas):
            for causa in posibles:
                self._proponer(valores, especificados, causa, S)

    def _aguas_abajo(self, valores, especificados, orden) -> None:
        for ident in orden:
            evento = self.grafo.eventos[ident]
            if not evento.causas or ident in especificados:
                continue
            propuesto = valor_por_entrada(evento, {c: valores[c] for c in evento.causas})
            if propuesto == F and valores[ident] == S:
                continue  # una sospecha de aguas arriba no se borra con causas falsas desconocidas
            self._proponer(valores, especificados, ident, propuesto)

    def _sintomas_explicados(self, ident: str, valores: dict[str, Valor], especificados: set[str]) -> int:
        vistos: set[str] = set()
        pendientes = list(self.grafo.eventos[ident].efectos)
        while pendientes:
            actual = pendientes.pop()
            if actual in vistos:
                continue
            vistos.add(actual)
            pendientes += self.grafo.eventos[actual].efectos
        return sum(1 for e in vistos if e in especificados and valores[e] == V)

    def _resumir(self, valores: dict[str, Valor], especificados: set[str]) -> Diagnostico:
        eventos = self.grafo.eventos

        def ficha(ident: str) -> dict:
            evento = eventos[ident]
            return {"id": ident, "texto": evento.texto, "valor": valores[ident].value,
                    "observado": ident in especificados, "recomendacion": evento.recomendacion,
                    "explica": self._sintomas_explicados(ident, valores, especificados)}

        causas = [i for i, e in eventos.items() if e.clase == "causa"]
        confirmadas = [ficha(i) for i in causas if valores[i] == V]
        # Parsimonia: primero la causa que explica más síntomas observados (un Gateway caído
        # explica los 7 nodos sin datos; la batería de un nodo explica solo uno).
        sospechosas = sorted((ficha(i) for i in causas if valores[i] == S), key=lambda f: -f["explica"])
        descartadas = [ficha(i) for i in causas if valores[i] == F]
        efectos = [ficha(i) for i, e in eventos.items() if e.clase == "efecto" and valores[i] in (V, S)]
        recomendaciones = [eventos[c["id"]].recomendacion for c in confirmadas + sospechosas
                           if eventos[c["id"]].recomendacion]
        diagnostico = Diagnostico(
            self.grafo.id, self.grafo.ra, self.grafo.titulo, valores, especificados,
            confirmadas, sospechosas, descartadas, efectos, recomendaciones,
        )
        diagnostico._central = self.grafo.evento_central
        return diagnostico
