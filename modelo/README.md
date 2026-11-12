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

Paquetes: `00 Vista general`, `01 Requisitos`, `02 Estructura` (con el subpaquete
`0 Arquitectura oficial EC3`), `03 Verificación`, `04 Comportamiento` y `05 Diagnóstico causal`.
36 diagramas: 20 de requisitos (req), 9 de definición de bloques (bdd), 1 interno de bloque (ibd),
3 de actividad (act), 2 de máquina de estados (stm) y 1 de casos de uso (uc).

Los **requisitos** (NS, RF, RNF, RA) y los **casos de prueba** siguen la versión del 10/11/2026 de
`docs/00-idea-principal.md` §8, migrada a la arquitectura oficial; el `satisfy` de los RF y RNF
apunta a los bloques oficiales. Los 5 bdd de septiembre (`00 Vista general › 1 bdd` y `02
Estructura › 1..4 bdd`) siguen describiendo la **propuesta original** del grupo (Raspberry Pi,
PZEM, SHT31, radar...): se conservan tal cual porque `demo/gaphor-vivo` escribe en sus bloques, y
ya no satisfacen ningún requisito. La **arquitectura oficial** del curso está en `02 Estructura ›
0 Arquitectura oficial EC3`.

### 00 Vista general

| Diagrama | Qué muestra |
|---|---|
| 1 bdd — Campus Twin de un vistazo | **Todo el sistema en un solo diagrama**: el bloque del sistema, sus seis subsistemas, los cinco actores externos, los cuatro tipos de nodo con su instrumentación, los ocho servicios del servidor y las partes del copiloto de voz. Debajo de cada nodo van sus sensores, y **dentro de cada sensor la magnitud que entrega** con su unidad |
| 2 req — Mapa de requisitos | **Todos los requisitos en un solo diagrama**: las 7 necesidades con los 13 RF y 8 RNF que derivan de ellas |

### 01 Requisitos (req)

| Diagrama | Qué muestra |
|---|---|
| 1 req — Necesidades de los stakeholders | Las 7 necesidades (NS-1 … NS-7) de las que cuelga todo |
| 2 req — Requisitos funcionales | RF-01 … RF-13 con `deriveReqt` hacia su necesidad de origen |
| 3 req — Requisitos no funcionales y restricciones | RNF-01 … RNF-08 con `deriveReqt` |
| 4 req — Trazabilidad a la arquitectura | `satisfy` de los bloques de la arquitectura oficial hacia cada RF y RNF (columna "Bloque que lo satisface" del documento maestro, §8.2) |
| 5 req — Requisitos de alto nivel RA-01..10 | Los 10 RA de la EC3, cada uno con `deriveReqt` hacia el RF que concreta en umbrales (campo `requisitos` de `config/requisitos_ra.yaml`) |
| 6 req — Trazabilidad de los RA a la arquitectura oficial | `satisfy` de los nodos que miden cada RA (campo `nodos`) y del evaluador de RA, que satisface los diez |

Los RA salen de `config/requisitos_ra.yaml`: su texto dice la magnitud, los nodos, el evaluador,
los umbrales y la norma, y su campo *Note* apunta a la figura del grafo. En los diagramas de
resumen (5 y 6, y el 3 de verificación) los RA muestran solo id y nombre; el texto completo se ve
en `05 Diagnóstico causal`.

### 02 Estructura (bdd)

| Diagrama | Qué muestra |
|---|---|
| 1 bdd — Arquitectura del sistema | `Campus Twin L-419` con sus seis subsistemas (composición) y los actores externos |
| 2 bdd — Nodos e instrumentación | Taxonomía de nodos ESP32 y, debajo de cada nodo, sus sensores con **la magnitud que entrega cada uno** y su unidad. Es el diagrama que responde "¿de dónde sale este dato?" |
| 3 bdd — Servidor y software | Los ocho servicios de la Raspberry Pi (broker, base de series, API, reglas, voz, salud, simulador, NTP) y las partes del copiloto de voz (app PWA y nodo de audio opcional) |
| 4 bdd — Tipos de valor y magnitudes | Catálogo de tipos de valor (`Temperatura [°C]`, `Potencia [W]`, …) |

Los dos diagramas muestran la magnitud de cada sensor, con distinta forma. La
**vista general** los pone en una fila, que es ancha pero deja ver el sistema
entero de arriba abajo. El de **instrumentación** los acomoda en una columna por
nodo, que es la versión compacta de lo mismo: graphviz los alinearía en una sola
fila y las cajas se solaparían.

Los bloques que muestran magnitudes llevan ancho fijo, para que no crezcan cuando
la demo escribe el valor y se salgan encima de la caja vecina.

### 02 Estructura › 0 Arquitectura oficial EC3 (bdd e ibd)

El hardware que compró el curso, el firmware y el stack del docente y los servicios del grupo,
según [../docs/02-instrumentacion-l419.md](../docs/02-instrumentacion-l419.md),
[../config/nodos.yaml](../config/nodos.yaml) y [../docs/CONTRATO_DATOS.md](../docs/CONTRATO_DATOS.md).

| Diagrama | Qué muestra |
|---|---|
| 1 bdd — Gemelo digital del L-419 | El sistema con la red de 7 nodos ESP-NOW, el Gateway ESP32 v4, la red Wi-Fi local y la laptop (stack del docente y servicios del grupo), y el aula que monitorea. Nota de autoría y de estado (datos simulados) |
| 2 bdd — Cajas de los 7 nodos | `Caja de nodo` (abstracta) con ESP32 DevKit V1, protoboard de 170 puntos, 18650 de 1600 mAh, porta-batería y regulador; cada nodo la especializa y agrega su sensor. **Cada sensor declara los campos que entrega en el JSON del Gateway** (`co2_ppm`, `leq_db`, `rs_r0`...) y lleva una nota con **la foto de su etiqueta con QR** en `docs/curso/imagenes/` |
| 3 bdd — Laptop: stack del docente y servicios del grupo | Mosquitto, Telegraf, InfluxDB 2.7 y Grafana (docente); servicio gemelo con sus 9 módulos, tablero web, Gaphor en vivo y copiloto de voz (pendiente) (grupo) |
| 4 bdd — Objetos del aula | Puerta, ventana, aire acondicionado, luminarias, PC, proyector, pizarra y tablero eléctrico, con qué nodo observa cada uno. Las cantidades y potencias quedan en `config/aula_l419.yaml` |
| 5 ibd — Flujo de datos | sensor → ESP32 (UART, I²S, I²C o analógico) → ESP-NOW → Gateway → Wi-Fi/MQTT → Mosquitto → Telegraf → InfluxDB → Grafana, y Mosquitto/InfluxDB → servicio gemelo → tablero, Gaphor en vivo y copiloto. Incluye el simulador, que hoy es la única fuente de datos |

El IBD cuelga del bloque `Cadena de datos L-419`: en el árbol aparece dentro de ese bloque.
Cada conector lleva el medio por el que viaja el dato y un flujo de item con su sentido
(`paquete: Paquete ESP-NOW`, `mensaje: JSON del Gateway`...).

Fotos referenciadas (además de la nota en el diagrama, cada bloque lo dice en su campo *Note*):

| Bloque | Foto |
|---|---|
| MH-Z1911A | `docs/curso/imagenes/1-mh-z1911a-co2.jpg` |
| KY-024 (Hall SS49E) | `docs/curso/imagenes/2-ky-024-hall-ss49e.jpg` |
| ESP32 DevKit V1 | `docs/curso/imagenes/3-esp32-devkit-v1.jpg` |
| BME280 (GY-BME280) | `docs/curso/imagenes/4-bme280.jpg` |
| BH1750 (GY-302) | `docs/curso/imagenes/5-gy-302-bh1750.jpg` |
| INMP441 | `docs/curso/imagenes/6-inmp441-microfono.jpg` |
| MQ-2 | Sin foto (no está en la orden de compra). La nota cita `7-tuya-detector-humo.jpg`, el detector que reemplaza |
| MLX90640 32x24 | Sin foto: la etiqueta no se fotografió |

Los bloques nuevos no repiten ningún nombre de septiembre; el script se detiene si eso pasa.

### 03 Verificación (req)

| Diagrama | Qué muestra |
|---|---|
| 1 req — Casos de prueba de requisitos funcionales | `verify` de CP-02 … CP-11 y CP-15 hacia los RF. CP-01 se retiró el 10/11 (energía contra PZEM) y no está en el modelo |
| 2 req — Casos de prueba de requisitos no funcionales | `verify` de CP-03, CP-05, CP-12 … CP-14 hacia los RNF |
| 3 req — Casos de prueba de los RA | `verify` de CP-10 hacia los diez RA y del CP con hardware de cada uno |

Qué CP verifica cada RA (`VERIFICACION_DE_RA` en el script; también en
`docs/00-idea-principal.md` §8.6):

| RA | CP | Rótulo hoy |
|---|---|---|
| RA-01, 02, 03, 04, 07 | CP-07 (consistencia ambiental), CP-10 | CP-10 simulado; CP-07 pendiente (S15) |
| RA-05 | CP-10 | Simulado. **Sin ensayo con hardware**: el MQ-2 no figura en ningún CP físico |
| RA-06 | CP-02 (conteo), CP-10 | CP-10 simulado; CP-02 pendiente (S15) |
| RA-08 | CP-06 (consumo fantasma), CP-10 | Simulado |
| RA-09 | CP-08 (puerta), CP-10 | CP-10 simulado; CP-08 pendiente (S15) |
| RA-10 | CP-03 (resiliencia), CP-15 (supervisión), CP-10 | Simulado; CP-03 en hardware pendiente |

Regla que el modelo mantiene: **todo RF y todo RA tienen al menos un bloque que los satisface
(`satisfy`) y al menos un caso de prueba que los verifica (`verify`)**; todo RNF tiene caso de
prueba.

### 04 Comportamiento (act, stm y uc)

Cómo se comporta el sistema, según el firmware del docente (`vendor/gemelo_iot_profesor/`), el
servicio del grupo (`demo/servidor/gemelo/`), [../docs/00-idea-principal.md](../docs/00-idea-principal.md)
§7 y §8.5 y el brief de la EC3 (§12), que fija los estados y los casos de uso. Cada diagrama lleva en
una nota su fuente y su estado: **todos son modelo del comportamiento, sin ninguna medición real**.
Los datos están en `tools/datos_comportamiento.py` y `build_model.py` los dibuja.

| Diagrama | Qué muestra |
|---|---|
| 1 act — Telemetría de un nodo | Del arranque del nodo al estado del aula, en tres carriles (nodo, Gateway, laptop): búsqueda del canal por SSID, lectura, decisión de lectura válida (`FALLO_SENSOR` tras 5 fallos), paquete con `seq`, envío por ESP-NOW y nueva búsqueda del canal tras 10 fallos, cola de 32 mensajes del Gateway, publicación en MQTT y reparto en paralelo a Telegraf y al servicio. Se dibuja el nodo de CO₂ (`nodo_co2.ino`) |
| 2 act — Entrada y salida de personas | Dos ramas en paralelo: el KY-024 (histéresis, antirrebote de 150 ms, latido cada 10 s) y la MLX90640 (fondo, cabezas, cruce de las líneas A y B, ocupación nunca negativa con `CONTEO_CORREGIDO`). Las junta el servicio, que deriva la presencia y evalúa RA-08 y RA-09 |
| 3 act — Detección, diagnóstico y alerta | Evaluación de RA-01..10, recorrido del grafo causal (SymCure) aguas arriba, recomendaciones y, solo si el RA cambió de nivel, registro en la bitácora y en InfluxDB, publicación por MQTT, tablero y voz (pendiente) |
| 4 stm — Estados del aula | Los seis estados del brief: Vacío, Ocupado, Sobreaforo, Luces sin ocupación (RA-08), Uso fuera de horario (RA-09) y Alarma de gas (RA-05). Los cinco primeros van dentro de «Operación normal», y el gas, que manda sobre todos, sale de ese estado compuesto y vuelve a él |
| 5 stm — Estados de un nodo | Calentando, Activo, Falla del sensor y Sin datos (el servicio lo decide tras tres periodos propios sin paquete, con mínimo de 30 s) |
| 6 uc — Casos de uso del aula | Seis escenarios (clase, mantenimiento, limpieza, emergencia, monitoreo del administrador y ronda del vigilante) con sus actores y, en la columna central, los casos que varios «incluyen»: condición de los RA, diagnóstico causal, salud de los nodos, registro de eventos, consumo fantasma y consulta por voz. La frontera es el bloque `Gemelo Digital L-419`, que es el sujeto de cada caso |

Lo que el modelo dice del código actual, y que conviene tener presente:

- El nodo térmico cuenta solo con la matriz y no mira al KY-024; el servicio los junta
  (`estado.py`). RF-03 habla de un conteo «coordinado», pero hoy esa coordinación es del servicio.
- El servicio registra un RA solo al cambiar de nivel. El silencio de 15 min que pide RF-08 no
  está implementado.
- Se publican los tópicos `campustwin/evento` y `campustwin/ra`; el `diagnostico` de la decisión D4
  todavía no: las causas y recomendaciones viajan dentro del evento.
- El firmware busca el canal del Gateway al arrancar **y otra vez tras 10 envíos fallidos**
  (`espnow_nodo.h`, idéntico en los seis programas). El §8.5 del documento maestro dice que solo
  lo hace al arrancar.

### 05 Diagnóstico causal (req)

Un diagrama por RA (`01` … `10`, con dos dígitos para que RA-10 quede al final). Cada uno tiene el
RA con su texto completo y, anclada, una nota con su grafo causal: título, causas raíz, efectos, la
ruta de la figura (`grafos/figuras/ra-XX-*.svg` y `.png`) y la del YAML (`grafos/ra-XX-*.yaml`).

Las figuras se **enlazan por ruta**, no se incrustan: incrustarlas sumaría unos 2 MB de base64 al
`.gaphor` y quedarían desactualizadas cada vez que se regeneran los grafos
(`python -m gemelo.figuras`).

Los textos de requisito del modelo son la versión corta de los criterios de aceptación de
`docs/00-idea-principal.md` §8; el criterio completo vive en el documento. Cada caso de prueba
lleva en su campo *Note* el estado al 10/11 (real, simulado o pendiente), tal como lo dice §8.4.

## Diagramas exportados

`export/` tiene los 36 diagramas en SVG, regenerables con:

```bash
/Applications/Gaphor.app/Contents/MacOS/gaphor export -f svg -u -o modelo/export modelo/campus-twin-l419.gaphor
```

Cambia `-f svg` por `pdf` o `png` según se necesite para el informe o la presentación.

## Regenerar el modelo base

`tools/build_model.py` construye el modelo completo desde cero con la API de Gaphor:

```bash
/Applications/Gaphor.app/Contents/MacOS/gaphor exec modelo/tools/build_model.py
```

Necesita el entorno virtual del servicio (`demo/servidor/.venv`, ver `demo/README.md`): el
intérprete de Gaphor no tiene PyYAML, así que el script le pide los RA y el resumen de cada grafo
a `tools/exportar_ra.py`, que corre con ese Python y usa los mismos cargadores que el servicio.
Otro intérprete se indica con `CAMPUSTWIN_PYTHON`.

Los datos del paquete 04 (pasos, flechas, estados y casos de uso) están en
`tools/datos_comportamiento.py`, solo declarados y sin Gaphor, y `build_model.py` los recorre
y los dibuja. Las actividades y las máquinas de estados se acomodan a mano en una grilla: las
flechas se anclan al lado que se indica y las barras de fork y join van giradas, porque Gaphor
las guarda solo con su matriz y su largo.

Al terminar imprime la trazabilidad (derivaciones, `satisfy`, `verify`, generalizaciones y
composiciones) y avisa si algún RF quedó sin bloque o sin caso de prueba. También lista los
flujos del IBD, compara los `tipo` de los nodos con `config/nodos.yaml`, avisa si falta alguna
foto referenciada, si algún RA quedó sin `satisfy` o sin `verify`, si falta la figura de algún
grafo y si alguna flecha, transición o caso de uso del paquete 04 quedó sin conectar.

Cada corrida genera ids nuevos, así que el `.gaphor` cambia entero aunque el contenido sea el
mismo. Al reexportar, los SVG de diagramas que no cambiaron solo difieren en ids internos de
cairo: se pueden descartar con `git checkout` para que el diff muestre solo lo nuevo.

**Ojo:** el script *sobrescribe* `campus-twin-l419.gaphor`. Sirve para regenerar el modelo base
cuando cambian los requisitos en `docs/00-idea-principal.md`; las ediciones hechas a mano en
Gaphor se pierden. Si el modelo ya se editó a mano, edita el `.gaphor` y deja el script como
registro del modelo base.
