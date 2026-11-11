# Servidor del grupo

Hay dos paquetes:

| Paquete | Qué es | Estado |
|---|---|---|
| `gemelo/` | **Servicio actual (EC3).** Lee el formato del Gateway del docente (MQTT), evalúa RA-01..10 (`config/requisitos_ra.yaml`), diagnostica con los grafos causales (`grafos/`, motor SymCure), estima el consumo fantasma, lleva el log de eventos y sirve la API y el tablero (`demo/tablero`). Incluye el simulador de los 7 nodos oficiales | En uso |
| `campus_twin_demo/` | La demo de septiembre, con la arquitectura anterior | Histórico: se conserva con sus pruebas |

## Correr el servicio

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # una vez
.venv/bin/python -m gemelo --simular              # con Mosquitto del stack (deploy/levantar.sh lo hace todo)
.venv/bin/python -m gemelo --simular --sin-broker # sin Docker: todo en memoria
.venv/bin/python -m gemelo --grupo grupoX         # datos reales del Gateway, sin simulador
.venv/bin/python -m gemelo.figuras                # figuras de los grafos en grafos/figuras/
.venv/bin/python -m pytest                        # pruebas (ambos paquetes)
```

Módulos de `gemelo/`:

| Módulo | Qué hace |
|---|---|
| `gateway.py` | Formato exacto de los mensajes del Gateway (tópico, campos, anomalías) |
| `simulador.py` | Los 7 nodos con la lógica de anomalías del código del docente y los escenarios de la demo |
| `estado.py` | Últimas lecturas, salud y variables derivadas (aula vacía, luces, horario, minutos de consumo fantasma) |
| `requisitos.py` | Evaluadores de RA-01..10 con histéresis |
| `razonamiento.py` | Motor SymCure: V, F, S y D; entrada OR, AND, N/M o IF; salida AND u OR; propagación aguas arriba y aguas abajo |
| `grafos.py` | Carga de `grafos/*.yaml` y evaluación de los eventos observables |
| `fantasma.py` | Consumo fantasma por proxy (inventario × tiempo) |
| `bitacora.py` | Log de eventos `logs/events.jsonl` y exportación a CSV |
| `transporte.py` | MQTT (paho) o bus en memoria |
| `servicio.py` | El ciclo que une todo |
| `api.py` | API REST, SSE y tablero |

Todo valor del aula sale de `config/aula_l419.yaml` (con la marca `supuesto`): el jueves se edita
ese archivo y todo se recalcula, sin tocar código.

---

## Demo de septiembre (`campus_twin_demo/`)

# Servidor de la demo

Simula los seis nodos del L-419 y expone los datos por la misma API que tendrá el
servidor de la Raspberry Pi.

## Correrlo

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m campus_twin_demo --puerto 8000 --velocidad 240
```

| Opción | Qué hace |
|---|---|
| `--velocidad` | Segundos simulados por segundo real. 60 = un día en 24 min; 240 = un día en 6 min; 1 = tiempo real |
| `--puerto`, `--host` | Dónde escucha |
| `--semilla` | Semilla del simulador, para repetir exactamente la misma jornada |

Si `../frontend/dist` existe, el tablero se sirve en `/`. Si no, `/` explica cómo
construirlo y la API sigue funcionando.

## Endpoints

| Ruta | Devuelve |
|---|---|
| `GET /api/estado` | Instantánea completa: reloj, resumen, nodos, alertas, salud, consumo fantasma, últimos mensajes |
| `GET /api/resumen` | Versión corta de lo anterior |
| `GET /api/historico?nodo=&magnitud=&limite=` | Serie temporal de una magnitud |
| `GET /api/alertas`, `/api/salud`, `/api/fantasma` | Cada sección por separado |
| `GET /api/configuracion` | Umbrales, horario, tarifa, factor de emisión y escenarios |
| `GET /api/stream` | Flujo SSE con el estado cada 0,5 s |
| `POST /api/demo/escenario/{nombre}` | Fuerza un escenario |
| `POST /api/demo/velocidad/{valor}` | Cambia la velocidad del día simulado |
| `POST /api/demo/pausa` | Pausa o reanuda el reloj |

## Los módulos

| Archivo | Responsabilidad |
|---|---|
| `configuracion.py` | Todas las constantes: nodos, periodos, umbrales, horario, tarifa. Nada de números mágicos repartidos por el código |
| `contrato.py` | La forma de un mensaje: tópico `l419/<nodo>/<magnitud>`, valor, unidad, marca de tiempo, secuencia y origen |
| `bus.py` | Bus en proceso. Es el punto exacto donde entra Mosquitto cuando haya nodos de verdad |
| `simulador.py` | El guion del día del laboratorio y el modelo físico de cada magnitud |
| `almacen.py` | Último valor, histórico en memoria, salud por nodo y descarte de duplicados |
| `reglas.py` | Motor de alertas (RF-08) y auditoría de consumo fantasma (RF-10) |
| `gemelo.py` | Junta todo y produce la instantánea que consumen el tablero y Gaphor |
| `api.py` | FastAPI: REST, SSE y los estáticos del tablero |

## Detalles que importan

**Secuencia y duplicados.** Cada muestra lleva un número por nodo y magnitud. El
almacén descarta lo repetido y calcula las muestras perdidas por los huecos de esa
secuencia, no por reloj: así la métrica vale igual con el día acelerado.

**Nodo caído.** Un nodo se da por caído tras tres periodos sin reportar, con un
mínimo de cinco minutos. El nodo de puerta late cada 30 minutos porque duerme
(RNF-04), así que su umbral es de 90 minutos.

**Movimiento y presencia son cosas distintas.** El radar publica `presencia` y el
PIR publica `movimiento`: con un grupo sentado y quieto el PIR se apaga y el radar
no. Es la razón por la que el nodo lleva los dos (RF-03), y en el modelo SysML se
ve como dos magnitudes separadas.

**El nodo de puerta reporta al instante.** Su latido normal es de 30 minutos
porque duerme (RNF-04), pero ante una apertura o un golpe despierta y publica
`estadoPuerta` y `vibracion` en el mismo tick, que es lo que pide RF-04.

**Consumo fantasma.** Solo cuenta la energía que corre tras 15 minutos seguidos
sin presencia, y la separa por franja horaria y por carga. La tarifa y el factor
de emisión están en `configuracion.py` y hay que confirmarlos con Servicios
Generales (preguntas 6 y 11 del documento maestro).

## Pruebas

```bash
.venv/bin/python -m pytest
```
