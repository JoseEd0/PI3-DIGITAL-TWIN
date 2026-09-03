# Modelo SysML — Campus Twin L-419

Modelo del sistema en [Gaphor](https://gaphor.org) (SysML). Fuente de verdad del modelo:
`campus-twin-l419.gaphor`. El contenido sale de [../docs/00-idea-principal.md](../docs/00-idea-principal.md)
y usa los mismos identificadores de requisito (NS, RF, RNF, CP).

## Abrir el modelo

```bash
open -a Gaphor modelo/campus-twin-l419.gaphor
```

Requiere Gaphor 3.x (probado con 3.3.2).

## Contenido

Paquetes: `01 Requisitos`, `02 Estructura`, `03 Verificación`.

### Diagramas de requisitos (req)

| Diagrama | Qué muestra |
|---|---|
| Necesidades de los stakeholders | Las 5 necesidades (NS-1 … NS-5) de las que cuelga todo |
| Requisitos funcionales | RF-01 … RF-11 con `deriveReqt` hacia su necesidad de origen |
| Requisitos no funcionales y restricciones | RNF-01 … RNF-07 con `deriveReqt` |
| Trazabilidad a la arquitectura | `satisfy` de cada bloque hacia el requisito que cumple |
| Casos de prueba de requisitos funcionales / no funcionales | `verify` de cada caso de prueba (CP-01 … CP-14) hacia el requisito |

### Diagramas de definición de bloques (bdd)

| Diagrama | Qué muestra |
|---|---|
| Arquitectura del sistema | `Campus Twin L-419` con sus seis subsistemas (composición) y los actores externos |
| Nodos e instrumentación | Taxonomía de nodos ESP32 y los sensores que compone cada uno, con sus propiedades de valor |
| Servidor y software | Servicios de la Raspberry Pi y partes del copiloto de voz |
| Tipos de valor y magnitudes | Catálogo de tipos de valor (`Temperatura [°C]`, `Potencia [W]`, …) |

Regla que el modelo mantiene: **todo RF tiene al menos un bloque que lo satisface (`satisfy`) y
al menos un caso de prueba que lo verifica (`verify`)**.

## Diagramas exportados

`export/` tiene los diagramas en SVG, regenerables con:

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
