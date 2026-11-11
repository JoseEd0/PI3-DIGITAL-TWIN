# Plan completo — EC3 (13/11) y cierre del proyecto

> **Versión del 10/11/2026.** Reemplaza al plan corto de la mañana.
> Las tareas, responsables y fechas viven en Asana y se reflejan en [03-plan.md](03-plan.md). Este
> documento es **el cómo**:
>
> - qué se construye y con qué diseño;
> - cuándo está terminado cada entregable;
> - en qué orden se hace;
> - qué falta preguntar.
>
> Bases: la [auditoría](AUDITORIA.md), el [contrato de datos](CONTRATO_DATOS.md), las
> [pautas de la EC3](curso/texto/ec3-pautas.md) y el [brief](curso/brief-ec3.md).

## 0. Resumen en una pantalla

- **Calendario (confirmado por José el 10/11):**
  - **S14 (09–13/11):** EC3, con todo el software funcionando con datos simulados y el reporte;
  - **S15 (16–20/11):** ensamblaje y pruebas con hardware;
  - **S16 (23–27/11):** demo final. El 27/11 es una fecha supuesta.
- **Objetivo de la EC3:** el viernes 13/11 a las 23:59 se entrega **un solo archivo** con el reporte. El sistema debe correr de punta a punta con la arquitectura del
  docente:

  ```
  nodos → Gateway → MQTT → InfluxDB → servicios del grupo → dashboard y Gaphor
  ```

  Mientras no haya nodos armados, los datos son simulados y se rotulan como tales.
- **Estado al 10/11 por la tarde:**
  - el stack del docente (Mosquitto, Telegraf, InfluxDB y Grafana) **ya corre en Docker** en la
    laptop de José, y un mensaje en formato Gateway llega a InfluxDB (comprobado);
  - todo el material está centralizado y Asana está reorganizado.
- **El aporte del grupo** es lo que le falta al sistema del docente:
  1. la condición del salón frente a cada requisito de alto nivel (RA);
  2. el diagnóstico causal con recomendaciones;
  3. el log de eventos;
  4. el consumo fantasma;
  5. el dashboard propio;
  6. el gemelo en Gaphor;
  7. el simulador;
  8. el programa `MQ-2.ino`.
- **Camino crítico:**

  ```
  simulador en formato Gateway → servicio del grupo (RA + motor causal + log)
    → dashboard → capturas → reporte
  ```

  Gaphor, el `.ino` y la energía de las cajas van en paralelo.

## 1. Arquitectura objetivo

```
                     ┌──────────── laptop (Docker) ─────────────────────────────────────┐
Nodos ESP32 ─ESP-NOW─► Gateway ─MQTT─►  Mosquitto :1883 ──► Telegraf ──► InfluxDB :8086  │
(o simulador ──MQTT, grupo "sim")     │      │                               │           │
                                      │      ▼                               ▼           │
                                      │  servicio del grupo (FastAPI, :8000)            │
                                      │   · estado vivo por MQTT                         │
                                      │   · evaluador de RA (config/)                    │
                                      │   · motor causal (grafos/)                       │
                                      │   · consumo fantasma (proxy)                     │
                                      │   · log events.jsonl + measurement "evento"      │
                                      │   · API REST + SSE + dashboard React             │
                                      │  Grafana :3000 (tableros del docente)            │
                                      └──────────────────────────────────────────────────┘
         ▲ cualquier laptop por Wi-Fi: http://<ip>:8000 (dashboard) y :3000 (Grafana)
         ▲ Gaphor en vivo (lee la API) · copiloto PWA en el celular (lee la API)
```

### Decisiones de diseño

| # | Decisión | Por qué |
|---|---|---|
| D1 | El servicio del grupo vive en `demo/servidor/` y no se mueve. Se renombra después de la EC3, si hace falta. | Las 51 pruebas, la API y el tablero ya existen. Moverlo cuesta horas sin aportar nada a la nota. |
| D2 | El estado en vivo se lee de **MQTT** y el histórico de **InfluxDB**. | Latencia mínima para el dashboard, y además se usa la base del docente, como pide la arquitectura. |
| D3 | El simulador publica **exactamente** el JSON del Gateway en `utec/gemelo/sim/...`. | Grafana, Telegraf y el servicio del grupo no distinguen la fuente. Para pasar a datos reales basta cambiar el grupo. |
| D4 | Las salidas del grupo van en **tópicos y measurements propios**: `utec/gemelo/<grupo>/campustwin/{ra,diagnostico,evento}` y los measurements `ra`, `diagnostico` y `evento`. | No se toca el contrato del docente, y Grafana también puede mostrar el diagnóstico. |
| D5 | Los RA, los grafos y el inventario están en **YAML** dentro de `config/` y `grafos/`. | Así lo piden el brief y `CLAUDE.md`: sin números mágicos y editable por Esteban sin tocar código. |
| D6 | El motor causal sigue **SymCure** tal como lo enseña el docente: valores V, F, S (sospechoso) y D (desconocido); entrada OR, AND, N/M o IF; salida AND u OR; propagación aguas arriba y aguas abajo. | Es exactamente lo que evalúa el bloque 2 de la pauta. |
| D7 | El consumo fantasma se estima por **proxy** (luces y equipos según el inventario, sin ocupación y fuera de horario). El reporte lo presenta como estimación. | El PZEM no está en la arquitectura oficial. |
| D8 | El `.ino` propio es el **nodo MQ-2 (nodo 3)**. | Es el único nodo sin programa, y su paquete y su tópico ya existen. |
| D9 | Para la demo, la hora la pone el simulador (`ts` propio). El **NTP local** se resuelve antes de instalar en el L-419. | Sin `ts`, Telegraf descarta todo el mensaje (ver el contrato, §1). |

## 2. Paquetes de trabajo

**Criterio general de "hecho":** el entregable existe en el repo, sus pruebas pasan (si tiene
código), está rotulado como real o simulado, y está cerrado en Asana y marcado en `03-plan.md`.

### Bloque A — Infraestructura de datos (mié 11/11, J)

| ID | Entregable | Hecho cuando |
|---|---|---|
| A1 ✅ | Stack del docente en Docker con credenciales propias en `deploy/.env` | `docker compose ps` muestra 4 servicios arriba y un mensaje de prueba llega a InfluxDB |
| A2 | `deploy/docker-compose.override.yml` con el servicio del grupo y el simulador, y los tableros del docente cargados en Grafana | Un solo comando levanta todo y Grafana muestra "Gemelo digital L418 — 7 sensores" con datos `sim` |
| A3 | Simulador migrado a 7 nodos en formato Gateway (paho-mqtt) | Publica co2, audio, gas, luz, térmico, magnético, ambiente y el estado del Gateway, con los periodos reales (5, 1, 10, 10, 5, 10 y 10 s) y los mismos niveles y bits de anomalía que calcula el código del docente. Hay pruebas de formato contra el JSON del contrato |
| A4 | Escenarios nuevos del simulador | Clase normal, salón vacío con luces (fantasma), aire acondicionado averiado (calor), sobreaforo, puerta abierta fuera de horario, gas o humo, nodo caído (falla o batería) y Gateway caído (LWT `offline`). Se activan desde la API y el dashboard |
| A5 | Grabación y reproducción (RF-11) | `--grabar archivo.jsonl` y `--reproducir archivo.jsonl` producen el mismo flujo MQTT |

### Bloque B — Requisitos de alto nivel y razonamiento (mié 11/11, E con J)

| ID | Entregable | Hecho cuando |
|---|---|---|
| B1 | `config/requisitos_ra.yaml`: RA-01..10 con nominal, alerta, crítico, fuente, sensor y requisito relacionado | Los 10 están definidos, cada umbral cita su norma o el código del docente, y el evaluador los carga |
| B2 | `config/aula_l419.yaml`: aforo, dimensiones, plano (coordenadas de los 7 nodos y de los objetos), inventario de potencias, horario y tarifa | Tiene valores reales, o supuestos marcados `# SUPUESTO` hasta que lleguen los datos (ver §6) |
| B3 | `grafos/ra-XX-*.yaml`: un grafo por RA (10, más uno de salud del sistema si conviene separarlo) | Cada nodo tiene id, texto, tipo (causa raíz, intermedio, síntoma o efecto), observable (sensor y condición) o inferido, lógica de entrada y salida, y una recomendación para cada causa raíz. Pasa la validación (sin ciclos y sin referencias rotas) |
| B4 | Figuras de los grafos generadas con Graphviz (`grafos/figuras/*.svg` y `.png`) | Las 10 figuras existen, con la leyenda de lógica y observabilidad |
| B5 | Motor causal `razonamiento.py` | Propaga aguas abajo y aguas arriba con lógicas OR, AND, N/M e IF y valores V, F, S y D, y lo observado prevalece sobre lo inferido. Hay **pruebas por cada tipo de lógica**, basadas en los ejemplos de las diapositivas de SymCure |
| B6 | Evaluador de RA, que convierte el estado en vivo en condición por RA | Cada RA sale nominal, alerta, crítico o desconocido (sin datos), con histéresis y duración mínima (por ejemplo, fantasma > 10 min) |
| B7 | Diagnóstico | Ante una violación de RA, el motor devuelve las causas sospechosas o confirmadas, los efectos esperados y las recomendaciones, y lo publica en el log, MQTT e InfluxDB |

### Bloque C — Servicio, log e interfaz (jue 12/11, J)

| ID | Entregable | Hecho cuando |
|---|---|---|
| C1 | Ingesta MQTT en el servicio del grupo (reemplaza el bus en memoria) | El estado se actualiza con datos `sim` y, cuando existan, con datos reales, sin tocar el código |
| C2 | Log de eventos (footprint) | `logs/events.jsonl` y el measurement `evento` guardan, en cada línea, `ts`, tipo, severidad, RA, nodo, causas, recomendación y origen (`sim` o real). Hay filtros y exportación a CSV desde la API |
| C3 | API | `/api/estado`, `/api/ra`, `/api/diagnosticos`, `/api/eventos` (+`.csv`), `/api/historico` (Flux), `/api/salud`, `/api/fantasma`, `/api/grafos/{ra}` y `/api/demo/escenario/{n}` |
| C4 | Dashboard propio: **los 3 mínimos de la pauta** | (1) mediciones de los 7 nodos con valor, unidad y tendencia; (2) semáforo de RA-01..10; (3) por cada violación, sus causas, efectos y recomendaciones |
| C5 | Dashboard: interactividad | Plano 2D del L-419 con los 7 nodos (clic para ver detalle, batería y señal), grafo causal activo (Cytoscape.js), log con filtros, salud de nodos y Gateway, consumo fantasma en S/ y kg CO₂, panel de escenarios y la franja **DATOS SIMULADOS** siempre visible cuando la fuente es `sim` |
| C6 | Acceso desde cualquier laptop por Wi-Fi | El servidor escucha en `0.0.0.0` y desde otra laptop de la misma red se abren `http://<ip>:8000` y `:3000`. Hay una captura |
| C7 | Pruebas | Las pruebas existentes se adaptan y se agregan las del simulador, el evaluador, el motor y la API. Todas pasan |

### Bloque D — Gemelo digital en Gaphor (jue 12/11, L con J)

| ID | Entregable | Hecho cuando |
|---|---|---|
| D1 | `build_model.py` migrado al hardware oficial | El BDD tiene los 7 nodos. Cada caja tiene ESP32 DevKit, sensor, protoboard, 18650, porta-batería y regulador. Están el Gateway ESP32 v4, la laptop con Mosquitto, Telegraf, InfluxDB y Grafana, los servicios del grupo y los objetos del aula (puerta, ventanas, aire acondicionado, luminarias, PC, proyector y tablero) |
| D2 | IBD del flujo | sensor → ESP32 (I²C, UART, I²S o analógico) → ESP-NOW → Gateway → MQTT → Telegraf → InfluxDB → servicio, dashboard y Gaphor |
| D3 | 01 Requisitos | RA-01..10 y los requisitos de las cajas (montaje, operación, dimensiones y energía), con RF y RNF actualizados y sus relaciones «satisfy» y «verify» |
| D4 | Paquete 04 Comportamiento | Actividades: telemetría de un nodo, entrada y salida de personas (Hall con MLX90640) y detección, diagnóstico y alerta. Estados del salón y de un nodo. Casos de uso: clase, mantenimiento, limpieza, administrador, ronda del vigilante y emergencia |
| D5 | Paquete 05 Razonamiento | Cada RA enlazado con su grafo, con las figuras de B4 y las notas |
| D6 | Fotos con QR en el modelo | Las 7 fotos de `docs/curso/imagenes/` están referenciadas en los bloques del sensor que corresponde |
| D7 | Gaphor en vivo con el nuevo modelo | El enlace escribe los valores de los 7 nodos y colorea los bloques según la condición de su RA |
| D8 | Exportación y tabla de cambios | Todos los diagramas están en SVG y PNG, y hay una tabla de cambios frente a la Semana 7 en `modelo/README.md` |

Gaphor 3 trae diagramas de actividad, de máquina de estados, de casos de uso y el IBD de SysML.
Se generan desde código, igual que los actuales.

### Bloque E — Hardware y firmware (jue 12/11, C)

| ID | Entregable | Hecho cuando |
|---|---|---|
| E1 | `firmware/MQ-2/MQ-2.ino`, con la estructura de `nodo_co2.ino` | Calienta (unos 60 s; el datasheet pide más para la primera vez), calibra R0 en aire limpio, calcula `rs_r0`, `do_alarma` y los bits `GAS_*`, y envía `PaqueteGas` cada 5 s. **Compila con `arduino-cli`** (núcleo esp32). Sin hardware se declara "compila, sin probar" |
| E2 | Análisis de energía de las cajas | Tabla por nodo con consumo estimado, autonomía con una 18650 de 1600 mAh y la recomendación (batería, USB o recarga). Problema de la 18650 directo al pin de 3.3 V y solución con LDO o elevador más TP4056 |
| E3 | Cita en el L-414 | Cita pedida. Si se consigue antes del viernes, se carga el código del docente en al menos 1 o 2 nodos y se toma evidencia **real** |
| E4 | Logotipo | Verificado en Canvas. Si falta, se hace y se usa en el dashboard |

### Bloque F — Reporte, presentación y demo (vie 13/11, L, E y C)

| ID | Entregable | Hecho cuando |
|---|---|---|
| F1 | Reporte EC3 (`reporte/ec3.md`, que se convierte a .docx y .pdf) | Sigue la estructura de la §4. Cada afirmación lleva figura, tabla o código y su rótulo real, simulado o pendiente. Se redacta sin condicional |
| F2 | Capturas reales | Dashboard (los 3 mínimos e interactividad), Grafana, Gaphor en vivo, Asana (tablero y una tarea con historial) y el acceso desde una segunda laptop |
| F3 | Presentación y póster | Diapositivas con la misma estructura del reporte y el guion de la demo |
| F4 | Ensayo de la demo | Guion de la §5 cronometrado y con un plan B (video grabado) |
| F5 | Entrega | Un integrante sube **un único archivo** a Canvas antes de las 23:59 |

## 3. Cronograma hora a hora

| Día | Mañana | Tarde | Noche (verificación) |
|---|---|---|---|
| **Mar 10** | ✅ Auditoría, contrato, Asana y material | ✅ Commits, merge y Docker arriba | Preguntas al docente y al equipo (§6) |
| **Mié 11** | A2, A3 (simulador en formato Gateway) | B1, B3 (Esteban), B5 y B6 (José) | A4, B4. Datos `sim` en Grafana y motor con pruebas |
| **Jue 12** | C1, C2, C3 | C4, C5, D1–D5 (Luhana y José) | E1, E2, C6, D7, D8 y las capturas |
| **Vie 13** | F1 (reporte), F3 | F4 (ensayo), copiloto si sobra tiempo | **F5: entrega antes de las 23:59** |

**Orden de recorte si no alcanza el tiempo**, de lo primero a lo último que se corta:

1. copiloto de voz;
2. grabación y reproducción (A5);
3. IBD detallado;
4. figuras pulidas de los grafos (se dejan las automáticas);
5. Gaphor en vivo con el modelo nuevo (se deja el actual).

**Nunca se recortan:** los 3 mínimos del dashboard, los grafos por RA, el motor con pruebas, el
log ni el reporte.

## 4. Reporte EC3: estructura y fuente de cada sección

| § | Sección | Contenido y fuente |
|---|---|---|
| 1 | Portada | Grupo 1, Sección 8, nombres completos y carreras: Huamani Ñaupas, José Eduardo (CS); Sotomayor Reyna, Esteban Matías (CS); Landeo Quispe, Luhana Victoria (Bioingeniería); Dávila Cabezas, Carlos Víctor Duamel (CS). Docente y fecha |
| 2 | Abstracto e introducción | Se parte de la Semana 7, con el consumo fantasma y el L-419. El marco viene de [semana-1](curso/texto/semana-1-introduccion.md): sistemas autónomos y NASA SE |
| 3 | Avance desde la EC2 | Tabla de estado: diseñado, implementado, probado en simulación o pendiente en hardware. Explica la **adopción de la arquitectura oficial** y la migración desde el plan de la Semana 7 ([auditoría](AUDITORIA.md)) |
| 4 | Sensores y procesadores | Los 7 sensores (principio, rango, interfaz, limitaciones y pines, según el [contrato](CONTRATO_DATOS.md)). ESP-NOW y el Gateway (`paquetes.h`). El `MQ-2.ino` propio. Arquitectura final y protocolos. Acceso desde una laptop por Wi-Fi. Energía de las cajas (E2). **Reconocimiento explícito del código del docente** |
| 5 | Razonamiento lógico | Tabla de RA-01..10 con sus normas. Metodología SymCure. Un grafo por RA (B4). Un ejemplo de propagación aguas abajo y aguas arriba sobre un escenario simulado (por ejemplo, "vacío con luces" o "CO₂ alto con puerta cerrada") |
| 6 | Interfaz | Capturas de C4, C5 y C6 explicando cómo cumple cada mínimo |
| 7 | Simulación, footprint y log | Escenarios, extracto de `events.jsonl` y gráficas de Grafana, rotuladas como simuladas |
| 8 | Gemelo digital en Gaphor | Diagramas nuevos y modificados con la tabla de cambios (D8). Usos del modelo: monitoreo en vivo, análisis y decisiones |
| 9 | Gestión en Asana | Capturas reales. Reorganización del 10/11 con la explicación de por qué. Cómo se usó desde la EC2 |
| 10 | Conclusiones y próximos pasos | Pruebas en el L-414, instalación en el L-419, NTP local y coordinación con S1 G1 y con los grupos de las cajas |
| 11 | Bibliografía (APA) | La de la Semana 7 y la EC2, más los datasheets de los 7 sensores, ASHRAE 55 y 62.1, EN 12464-1, ANSI S12.60, el RNE A.040 y EM.110, Kapadia (2003) SymCure, y la documentación de ESP-NOW, Mosquitto, Telegraf, InfluxDB y Grafana |

Herramienta: el reporte se escribe en Markdown y se convierte a .docx y .pdf con pandoc (hay que
instalarlo: `brew install pandoc`). Las figuras salen del repo.

## 5. Guion de la demo (7–8 min)

1. **Arquitectura (1 min):** el diagrama de la §1 y el IBD en Gaphor.
2. **Clase normal (1 min):** los 7 nodos reportando en el dashboard y en Grafana, todo en verde, con
   la franja DATOS SIMULADOS visible.
3. **CO₂ alto con la puerta cerrada (1.5 min):** el RA-03 pasa a alerta. El grafo marca como causas
   sospechosas la ventilación insuficiente y la puerta cerrada (observada), recomienda abrir la
   puerta, y queda la línea en el log.
4. **Vacío con luces (1.5 min):** el RA-08 detecta consumo fantasma, el contador de S/ y kg de CO₂
   sube y el vigilante recibe el aviso.
5. **Gas detectado (1 min):** el RA-05 pasa a crítico, se muestra el conteo de ocupantes para la
   evacuación y la recomendación.
6. **Gateway caído (1 min):** el RA-10 detecta que todos los nodos dejaron de reportar a la vez. La
   lógica N/M diagnostica "Gateway" y no "7 sensores rotos".
7. **Gaphor en vivo y acceso desde otra laptop (1 min).**

Plan B: un video del mismo guion, grabado el jueves en la noche.

## 6. Lo que falta saber: preguntas concretas

### Supuestos de trabajo (decididos el 10/11, mientras el docente responde)

| Pregunta | Supuesto con el que se trabaja | Qué cambia si el docente dice otra cosa |
|---|---|---|
| PZEM | **Proxy sin PZEM** (luces + ocupación + horario × inventario) | Si se integra como nodo 8, cambia solo la fuente del consumo |
| .ino propio | **Nodo MQ-2 (nodo 3)**. Es un sensor oficial: reemplazó al Tuya el 21/10, está en `paquetes.h`, en el Gateway y en el Grafana del docente, pero no tiene programa en el ZIP | Si no lo acepta, se escribe otro nodo con la misma plantilla |
| Servidor | **Stack propio en la laptop con el mismo formato.** Para los datos reales nos suscribimos al Mosquitto de S1 G1, o S1 G1 publica también en el nuestro | Solo cambia el host o el grupo en la configuración |
| Hora sin internet | **NTP local en la laptop**, que se prueba en S15. José pregunta si "UTEC Proyectos" tiene internet (lo más probable es que sí) | Si hay internet, el NTP local queda como respaldo |
| Salón | **L-419**. El código del docente dice L418 por herencia | Solo cambia `config/aula_l419.yaml` |
| Interfaz | **Web propia + el Grafana del docente enlazado** (históricos y CSV) | — |
| Calendario | EC3 en S14, hardware en S15 y demo final en S16 | Se mueven las fechas en Asana |
| Datos del aula | **Un solo archivo, `config/aula_l419.yaml`.** Cada valor lleva `supuesto: true` y su fuente. Todo se calcula desde ahí: simulador, consumo fantasma, RA, plano, dashboard y reporte. El dashboard muestra cuántos valores siguen siendo supuestos | El jueves se edita ese archivo y todo se recalcula, sin tocar el código |

### Para el docente (por correo o en clase)

1. **PZEM-004T:** ¿se integrará como nodo 8? Si es así, ¿quién lo programa y qué `tipo` y paquete
   usará en `paquetes.h`? ¿Podemos proponerlo nosotros? Si no se integra, ¿acepta que el consumo
   fantasma se estime con luces, ocupación e inventario de potencias?
2. **Programa propio:** ¿es válido que nuestro .ino sea el **nodo de gas MQ-2 (nodo 3)**, que no está
   en la carpeta de Drive? ¿Hay que coordinarlo con el grupo de la caja de humo (S8 G2)?
3. **Procesador central:** ¿qué `GRUPO` y qué IP usará el Gateway real de S1 G1? ¿Nuestro dashboard
   debe conectarse a ese Mosquitto e InfluxDB, o cada grupo levanta su propio servidor y se
   suscribe al mismo Gateway?
4. **Hora sin internet:** ¿la red "UTEC Proyectos" tiene salida a internet para NTP? Si no, ¿se puede
   correr NTP en la laptop? Sin hora, Telegraf descarta los datos (lo comprobamos).
5. **Salón:** el diagrama de arquitectura dice L418 y el tablero de Grafana dice L419. ¿Cuál es?
6. **Entregas después del 13/11:** ¿hay presentación final, póster o informe final después de la
   EC3? ¿Dónde y cuándo es la demo en vivo?
7. **Rúbrica de la EC3:** ¿hay rúbrica publicada con criterios y puntajes?
8. **Interfaz:** ¿el dashboard puede ser una web propia o tiene que estar en Grafana?

### Datos del L-419 (los puede tomar cualquiera del grupo con una foto y una wincha)

1. **Aforo oficial**: el número de asientos o personas, que suele estar en un cartel en la puerta.
2. **Dimensiones**: largo × ancho × alto en metros (para el volumen del balance de CO₂).
3. **Croquis o foto del plano**: dónde están la puerta (o puertas), las ventanas (¿se abren?), el
   aire acondicionado, las luminarias, la pizarra, el proyector, las PC y el tablero eléctrico.
4. **Luminarias**: cuántas hay, de qué tipo (fluorescente o LED) y cuántos W cada una (está en el
   tubo o el panel). ¿Hay más de un circuito o interruptor?
5. **PC y monitores**: cuántos y de qué modelo (o W de la etiqueta). ¿Se quedan prendidos o en
   espera de noche?
6. **Proyector**: el modelo o los W de la etiqueta.
7. **Aire acondicionado**: modelo, BTU o W, y si tiene renovación de aire o solo recircula.
8. **Otros equipos siempre enchufados**: router, TV, cargadores, etc.
9. **Horario**: días y bloques de clase, limpieza, hora de cierre y ronda del vigilante. Si Esteban
   ya lo definió (estaba cerrado en Asana), ¿dónde está?
10. **Tarifa eléctrica de UTEC** en S/ por kWh. Si no se consigue, se usa una tarifa de referencia y
    se dice.

### Para el equipo

1. **Esteban:** ¿qué umbrales definiste en septiembre? ¿Tienes el horario del L-419?
2. **Carlos:** ¿qué se probó en el "banco de pruebas" que figura cerrado? ¿Hay fotos o sketches?
   ¿Puedes pedir la cita en el L-414 (Open Lab, código QR en la puerta)?
3. **Diseño de la caja (23/10):** ¿quién lo subió? Necesitamos los .3MF o .DXF y las imágenes.
4. **Canvas:** ¿la C1 y el logotipo están entregados o no?
5. **Luhana:** ¿los diagramas que subiste a `main` (`BDD.gaphor` y `Diagrama de requisitos.gaphor`)
   se integran al modelo generado o eran pruebas?

### Lo que se puede revisar en Canvas con acceso desde el navegador

La rúbrica de la EC3, los anuncios completos (fechas posteriores al 13/11 y lugar de la demo), las
imágenes con QR IMG_8423–8429, la entrega del diseño de caja (23/10) y el estado de la C1 y del
logotipo.

## 7. Después de la EC3: terminar el proyecto

Las fechas son S15 (16–20/11) para el hardware y S16 (23–27/11) para el copiloto, la maratón y la
demo final.

| Paso | Qué | Hecho cuando |
|---|---|---|
| P1 | Cita en el L-414 y carga del código del docente y del `MQ-2.ino` | Cada nodo aparece en InfluxDB con el grupo real |
| P2 | NTP local (o el ajuste de Telegraf) | Los datos llegan sin internet (RNF-05, CP-03) |
| P3 | Ensayos con hardware: CP-02 (conteo con 10 cruces), CP-07 (BME280 y MH-Z1911A contra referencia), CP-08 (puerta) y CP-03 (Gateway caído) | Los resultados quedan en la bitácora y en el informe, rotulados como **reales** |
| P4 | Instalación en el L-419 coordinada con S1 G1 y con los grupos de cada caja | 7 nodos reportando desde el salón |
| P5 | Fuente de datos real | Se cambia `grupo` en la configuración, sin tocar el código, y el dashboard deja de mostrar DATOS SIMULADOS |
| P6 | Si el curso continúa: maratón de 72 h (CP-05) y auditoría de consumo fantasma con una semana de datos reales (CP-06) | Hay reporte con datos reales |
| P7 | Copiloto de voz (RF-09) si no entró en la EC3 | Briefing y consultas en el celular |
| P8 | Cierre | Documento maestro, modelo y Asana con el estado final, informe final, póster y presentación |

## 8. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| No alcanza el tiempo hasta el viernes | Alta | Seguir el orden de la §3 y recortar según la lista. El núcleo (A3, B, C4 y F1) va primero |
| Los datos del aula no llegan | Media | Usar valores supuestos marcados `SUPUESTO` en `config/aula_l419.yaml` y decirlo en el reporte |
| Docker falla en la laptop de la demo | Baja | Está probado en la de José. El servicio del grupo puede leer MQTT sin InfluxDB, y queda el video del plan B |
| Sin internet en el aula, el Gateway real no tiene hora | Alta en el L-419 | La demo de la EC3 usa el simulador (con `ts` propio). P2 lo resuelve después |
| El reporte promete cosas que no existen | Media | Rótulo real, simulado o pendiente en cada afirmación, y revisión cruzada el viernes en la mañana |
| Se filtran credenciales del docente | Baja | `.env` y `gateway.ino` están en `.gitignore` y se verificaron con grep |

## 9. Comandos

```bash
# levantar el stack del docente con credenciales propias (deploy/.env, no versionado)
docker compose -p campustwin --env-file deploy/.env \
  -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml up -d

# apagarlo
docker compose -p campustwin -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml down
```

Grafana queda en http://localhost:3000 (usuario `admin`, clave en `deploy/.env`) e InfluxDB en
http://localhost:8086. Con A2, todo pasa a un solo comando desde `deploy/`.
