# Modelo SysML — Campus Twin L-419

Modelo del sistema en [Gaphor](https://gaphor.org) (SysML). Fuente de verdad del modelo:
`campus-twin-l419.gaphor`. El contenido sale de [../docs/00-idea-principal.md](../docs/00-idea-principal.md)
y usa los mismos identificadores de requisito (NS, RF, RNF, CP).

## Abrir el modelo

```bash
open -a Gaphor modelo/campus-twin-l419.gaphor
```

Requiere Gaphor 3.x (probado con 3.3.2).

**Gaphor no abre ningún diagrama solo**: al cargar el modelo muestra el mensaje *"Open a
Diagram"*. Los diagramas están en el árbol de la izquierda, dentro de cada paquete, y se abren
con **doble clic**. Empiezan con un número para que aparezcan al inicio de cada paquete, antes
de los requisitos y los bloques.

Para ver todo de golpe, empieza por el paquete **00 Vista general**.

## Contenido

Paquetes: `00 Vista general`, `01 Requisitos`, `02 Estructura`, `03 Verificación`.
12 diagramas: 7 de requisitos (req) y 5 de definición de bloques (bdd).

### 00 Vista general

| Diagrama | Qué muestra |
|---|---|
| 1 bdd — Campus Twin de un vistazo | **Todo el sistema en un solo diagrama**: el bloque del sistema, sus seis subsistemas, los cinco actores externos, los cuatro tipos de nodo con su instrumentación, los ocho servicios del servidor y las partes del copiloto de voz |
| 2 req — Mapa de requisitos | **Todos los requisitos en un solo diagrama**: las 7 necesidades con los 13 RF y 8 RNF que derivan de ellas |

### 01 Requisitos (req)

| Diagrama | Qué muestra |
|---|---|
| 1 req — Necesidades de los stakeholders | Las 7 necesidades (NS-1 … NS-7) de las que cuelga todo |
| 2 req — Requisitos funcionales | RF-01 … RF-13 con `deriveReqt` hacia su necesidad de origen |
| 3 req — Requisitos no funcionales y restricciones | RNF-01 … RNF-08 con `deriveReqt` |
| 4 req — Trazabilidad a la arquitectura | `satisfy` de cada bloque hacia el requisito que cumple |

### 02 Estructura (bdd)

| Diagrama | Qué muestra |
|---|---|
| 1 bdd — Arquitectura del sistema | `Campus Twin L-419` con sus seis subsistemas (composición) y los actores externos |
| 2 bdd — Nodos e instrumentación | Taxonomía de nodos ESP32 y los sensores que compone cada uno, con sus propiedades de valor |
| 3 bdd — Servidor y software | Los ocho servicios de la Raspberry Pi (broker, base de series, API, reglas, voz, salud, simulador, NTP) y las partes del copiloto de voz (app PWA y nodo de audio opcional) |
| 4 bdd — Tipos de valor y magnitudes | Catálogo de tipos de valor (`Temperatura [°C]`, `Potencia [W]`, …) |

### 03 Verificación (req)

| Diagrama | Qué muestra |
|---|---|
| 1 req — Casos de prueba de requisitos funcionales | `verify` de CP-01 … CP-11 y CP-15 hacia los RF |
| 2 req — Casos de prueba de requisitos no funcionales | `verify` de CP-03, CP-05, CP-12 … CP-14 hacia los RNF |

Regla que el modelo mantiene: **todo RF tiene al menos un bloque que lo satisface (`satisfy`) y
al menos un caso de prueba que lo verifica (`verify`)**; todo RNF tiene caso de prueba.

Los textos de requisito del modelo son la versión corta de los criterios de aceptación de
`docs/00-idea-principal.md` §8; el criterio completo vive en el documento.

## Diagramas exportados

`export/` tiene los 12 diagramas en SVG, regenerables con:

```bash
/Applications/Gaphor.app/Contents/MacOS/gaphor export -f svg -u -o modelo/export modelo/campus-twin-l419.gaphor
```

Cambia `-f svg` por `pdf` o `png` según se necesite para el informe o la presentación.

## Regenerar el modelo base

`tools/build_model.py` construye el modelo completo desde cero con la API de Gaphor:

```bash
/Applications/Gaphor.app/Contents/MacOS/gaphor exec modelo/tools/build_model.py
```

Al terminar imprime la trazabilidad (derivaciones, `satisfy`, `verify`, generalizaciones y
composiciones) y avisa si algún RF quedó sin bloque o sin caso de prueba.

**Ojo:** el script *sobrescribe* `campus-twin-l419.gaphor`. Sirve para regenerar el modelo base
cuando cambian los requisitos en `docs/00-idea-principal.md`; las ediciones hechas a mano en
Gaphor se pierden. Si el modelo ya se editó a mano, edita el `.gaphor` y deja el script como
registro del modelo base.
