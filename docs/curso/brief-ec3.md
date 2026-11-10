# Campus Twin — Brief maestro para Claude Code (PI3, UTEC 2026-2) · v3

> **Para Claude Code:** este documento es la fuente de verdad del proyecto. Consolida:
> - los dos reportes del grupo: el **Entregable de la Semana 7** (detallado, 13/16) y la **EC2** (genérica, 12/16);
> - los documentos y **anuncios** del docente en Canvas;
> - el **código oficial del docente** (carpeta de Drive "Gemelo_IoT", que viene en un ZIP);
> - el estado real de Asana.
>
> Todo el material está en `docs/curso/`. Ya existe una carpeta con trabajo previo (Gaphor en código y quizá más): **audítala primero** (sección 3) y amplía lo existente.
>
> El objetivo es **terminar el proyecto**, no solo la EC3. Según el usuario, hoy no hay código propio funcional.

---

## 0. Reglas de trabajo

1. **La EC3 vence el viernes 13 de noviembre de 2026 a las 23:59 (hora de Lima).** El cronograma del grupo en Asana también fija para el 13/11 la entrega final, con demo.
2. **La base técnica es el reporte de la Semana 7, no la EC2.** De la EC2 solo se reutilizan los interesados, la introducción y la bibliografía.
3. **La arquitectura y el hardware oficiales son los del docente** (secciones 5 y 6): siete nodos ESP32 que usan **ESP-NOW** hacia un **Gateway ESP32**, que publica por **MQTT** a un servidor en una **laptop** con Mosquitto, Telegraf, InfluxDB y Grafana. **No se reinventa esa arquitectura**: el trabajo del grupo se monta encima. Hay que migrar el plan propio de la Semana 7 (otros sensores, Raspberry Pi 5) en el modelo, el código, Asana y el reporte.
4. **Honestidad.** El reporte de la Semana 7 describe en presente cosas que no existen ("seis nodos con ESP32 miden...", el script de Gaphor en vivo). La EC3 distingue entre lo **real**, lo **simulado** y lo **pendiente**. Además, el código de los nodos y del servidor es **del docente**: el reporte debe decir que **se reutiliza y se integra**, y presentar como aporte del grupo solo lo que el grupo hizo.
5. Umbrales en archivos de configuración. Todo en español; los identificadores pueden ir en inglés.

---

## 1. Datos del grupo

- **Curso:** PI3103, Teoría 8, 2026-2. **Sección 8.**
- **Docente:** Jorge Fernando Figueroa Núñez del Prado (jfigueroan@utec.edu.pe, oficina P333).
- **Grupo:** **Grupo 1** (en Canvas, "PI3-2 1").
- **Proyecto:** Campus Twin L-419.
- **Salón piloto:** **L-419**. El PNG de arquitectura del docente dice "L418", pero su dashboard de Grafana dice "L419": se asume L-419.

| Integrante | Carrera | Rol (Semana 7 y Asana) |
|---|---|---|
| Huamani Ñaupas, José Eduardo | Ciencias de la Computación | Servidor, API, reglas, dashboard e integración. Administra Asana. |
| Sotomayor Reyna, Esteban Matías | Ciencias de la Computación | Ocupación y puerta, copiloto de voz, póster y presentación. |
| Landeo Quispe, Luhana Victoria | Bioingeniería | SysML, documentación, nodo ambiental, pruebas e informe final. |
| Dávila Cabezas, Carlos Víctor Duamel | Ciencias de la Computación | Red y TI, banco de pruebas, firmware base, nodo de energía y ensayo de la demo. **Agregarlo a la tabla de roles de la EC3.** |

---

## 2. Historial de entregas en Canvas

| Entrega | Fecha | Estado o nota |
|---|---|---|
| Instrumentación de un espacio de enseñanza | 27/08 | 0 pts (tarea sin puntaje) |
| C1 (individual) | 13/09 | Figura sin entregar en la cuenta del usuario: que lo verifique. |
| Entregable Semana 7 | 26/09 | **13/16** (es la base técnica) |
| Diseño de la caja | 23/10 | Lo subió otro integrante. Pedir los archivos. |
| EC2 | 23/10 | **12/16**, sin comentarios del docente |
| Logotipo para sensores y procesador | 26/10 | Figura sin entregar: verificar. |
| **EC3** | **13/11** | Pendiente. **Subir un solo archivo por grupo.** |

---

## 3. Auditoría inicial obligatoria

Genera `docs/AUDITORIA.md`, clasificando cada elemento como **existe y funciona**, **existe incompleto** o **no existe**.

1. **Carpeta propia del grupo:**
   - el modelo Gaphor (12 diagramas en 4 paquetes, según la Semana 7);
   - el script de sincronización en vivo;
   - los requisitos NS, RF, RNF y CP;
   - el contrato de datos (marcado como hecho en Asana);
   - el simulador.
2. **Código oficial del docente** (`docs/curso/Gemelo_IoT*.zip`, a descomprimir en `vendor/gemelo_iot_profesor/`, **sin modificar el original**):
   - `gateway/` (`gateway.ino`, `paquetes.h`);
   - `nodo_ambiente/`, `nodo_audio/`, `nodo_co2/`, `nodo_luz/`, `nodo_magnetico/`, `nodo_termico/`;
   - `servidor_iot/` (`docker-compose.yml`, `.env`, `mosquitto/`, `telegraf/`, `grafana/`, `dashboard_gemelo_iot.json`, `dashboard_gemelo_L419_7sensores.json`);
   - `arquitectura_iot_gemelo_digital_L418.png`.

   Documenta en `docs/CONTRATO_DATOS.md`:
   - la **estructura de paquetes ESP-NOW** (`paquetes.h`);
   - los **tópicos MQTT y el formato** que publica el Gateway;
   - los **measurements y campos en InfluxDB** (configuración de Telegraf);
   - los **niveles y bits de anomalía** que calcula cada nodo;
   - los paneles del Grafana del docente.

   **Ojo:** el ZIP no tiene una carpeta para el nodo de gas MQ-2 (nodo 3), aunque aparece en la arquitectura. Verifica si el nodo está dentro de otra carpeta o si falta.
3. **`.env` del servidor del docente:** puede contener credenciales. **No publicarlo ni copiarlo al reporte ni al repositorio público.**

---

## 4. Qué pide el docente (documentos y anuncios de Canvas)

### Del proyecto (PI3 - Proyecto.docx)

- Instrumentar aulas para "salón autónomo" + **gemelo digital**; proceso de **Ingeniería de Sistemas NASA**.
- Definir **eventos** nominales y no nominales.
- Modelar en **Gaphor**.
- **Simulación** para generar datos.
- **Footprint** con un **log de eventos**.
- Demo, reporte y presentación.
- **Gestión en ASANA.**

### Anuncio del 06/11 (asignación de cajas)

Los sensores envían al procesador central. **Cualquier persona puede usar una laptop para conectarse por Wi-Fi al procesador central y acceder a las mediciones.** Las mediciones se muestran en la **interfaz (dashboard) que diseña cada grupo**, comunicando el cumplimiento de los requisitos de los interesados (por ejemplo, confort para el dictado de clases o el CO2 frente a la normativa). La interfaz debe incluir:
1. las **mediciones**;
2. las **condiciones** relacionadas con los requisitos (por ejemplo, "la temperatura está por encima de las normas");
3. las **causas y consecuencias de las anomalías, con sugerencias de solución**.

### Anuncio del 02/11, actualizado (programación de los ESP32)

- La comunicación sensor → procesador central es **Wi-Fi con ESP-Now** (no Bluetooth).
- Los programas se entregan en formato **.ino (Arduino IDE)** y se nombran con el código del sensor (por ejemplo, `GY-BME280`).
- **Los grupos que no montan sensores también deben desarrollar sus propios programas**, aunque no se instalen.
- El nodo de CO2 es el ejemplo de referencia y ya se comunica con el Gateway.
- Carpeta para subir los .ino: https://drive.google.com/drive/folders/1k37tweXGhZ7qIf61guPyIminIqS6Kkvy
- Código oficial del Gateway y de todos los nodos: https://drive.google.com/drive/folders/1tf4S0765deHpeeRLdqpPgcSakwKKSSzv (ya descargado en el ZIP).

### Otros anuncios

- **Nuevo sensor de humo (21/10):** se compró un **MQ-2** para **reemplazar el detector comercial Tuya**, que era difícil de integrar. Se comunica por ESP32 como los demás.
- **Cajas listas (29/10):** en cada clase, uno o dos grupos voluntarios ensamblan una caja.
- **Acceso al hardware (14/10):** en el **Laboratorio L-414**, con cita en horario de Open Lab (código QR en la puerta). Hay que pedir la "caja de partes de PI3, secciones 1, 8 y 9" y devolverla al salir.
- **Imágenes de identificación (11/10, Semana 10, IMG_8423–8429.jpeg):** nombres y **códigos QR** con las especificaciones y dimensiones de cada sensor y del procesador. Hay que **ingresarlas al modelo de Gaphor** y adjuntarlas en **Asana**.

### Asignación de cajas

| Sección / Grupo | Caja |
|---|---|
| S8 G4 | Micrófono |
| S8 G2 | Humo |
| S9 G2 | Hall |
| S9 G3 | Iluminación |
| S9 G5 | Infrarrojo |
| S1 G1 | **Procesador central** + CO2 |
| S1 G5 | Temperatura |

**El Grupo 1 de la Sección 8 no tiene caja asignada.** Su aporte es la integración: **dashboard propio** (la interfaz que pide el docente), **razonamiento causal**, **gemelo digital en Gaphor conectado a InfluxDB**, simulación, copiloto y gestión. Igual debe escribir **su propio programa .ino** (por ejemplo, el de la puerta o el de ocupación), como exige el anuncio del 02/11.

### Estrategia del docente para la puerta

El **sensor magnético** indica si la puerta está abierta o cerrada. La **MLX90640** indica el sentido del cruce. Ambos se coordinan para contar entradas y salidas.

---

## 5. Hardware oficial final (arquitectura del docente, 07/11)

| Nodo | Variable | Hardware | Notas |
|---|---|---|---|
| 1 | CO2 | ESP32 DevKit V1 + **MH-Z1911A** (familia MH-Z19, NDIR, UART) | Código del docente de referencia: alerta en 1000 ppm, crítico en 1500, histéresis de 100, 3 confirmaciones, 3 minutos de calentamiento, rango válido de 300 a 10000 ppm, detección de picos y bit de falla del sensor. |
| 2 | Audio / ruido | ESP32 + **INMP441** (I²S) | Solo **nivel en dB, sin guardar audio** (privacidad). dB SPL ≈ dBFS + 120 (aproximado, hay que calibrar). |
| 3 | Gas / humo | ESP32 + **MQ-2** | Sensor analógico de GLP, gas natural y humo. Necesita precalentamiento y calibración (R0 en aire limpio). Reemplaza al Tuya. |
| 4 | Luz | ESP32 + **BH1750** | I²C, en lux. |
| 5 | Conteo de personas | ESP32 + **MLX90640** (32×24) | Matriz térmica: **no forma imágenes identificables**. |
| 6 | Puerta | ESP32 + **KY-024** (Hall lineal, con salida analógica y digital) | Imán en la hoja de la puerta. |
| 7 | Ambiente | ESP32 + **GY-BME280** | Temperatura, humedad y presión, por I²C. |
| Gateway | — | **ESP32 v4** | Recibe por ESP-NOW y publica por Wi-Fi a MQTT. |
| Servidor | — | **Laptop** con Docker: **Mosquitto, Telegraf, InfluxDB y Grafana** | Además: dashboard público de diagnóstico de anomalías, exportación a CSV y gemelo digital que lee de InfluxDB. |
| Caja | — | ESP32, protoboard de 170 puntos, **18650 de 1600 mAh** y porta-batería | Diseño propio de cada grupo; el docente elige cuáles se imprimen. |

### Medición de energía (PZEM-004T)

**El PZEM-004T figura en la lista de compra, pero no en la arquitectura oficial.** El eje del grupo, el **consumo fantasma**, depende de él. Opciones:
- **(a)** Preguntar al docente si el PZEM se integrará (sería el nodo 8).
- **(b)** Mientras tanto, estimar el consumo fantasma por **proxy**: luces encendidas (BH1750 por encima de la luz natural esperada) con ocupación cero (MLX90640) y fuera de horario, multiplicado por la **potencia nominal** de las luminarias y equipos del L-419 (inventario manual) para obtener kWh, soles y kg de CO2.

El reporte debe decir explícitamente que es una estimación.

### Migración desde el plan de la Semana 7

| Plan del grupo | Reemplazo oficial |
|---|---|
| SHT31 | BME280 |
| SCD41 | MH-Z1911A |
| LD2410C + PIR + ToF VL53L1X | MLX90640 |
| Sensor magnético + SW-420 + LiPo | KY-024 (se elimina el SW-420) |
| Nodo de audio para el copiloto (INMP441 + MAX98357A + parlante) | INMP441 como sensor de ruido. El copiloto pasa a una PWA en el celular. |
| PZEM + SCT-013 + Tasmota | Ver la nota de energía. SCT-013 y Tasmota quedan fuera. |
| Raspberry Pi 5 | Laptop con el stack Docker del docente |
| MQTT directo desde los nodos | ESP-NOW hacia el Gateway |
| — | Nuevo: **MQ-2** (gas y humo) |

Requisitos del grupo a actualizar:
- **RNF-02:** "sin cámaras ni audio guardado" se cumple, porque la MLX90640 no forma imágenes identificables y el INMP441 solo reporta dB.
- **RNF-03:** recalcular el costo.
- **RNF-05:** sin internet; ESP-NOW y la red local lo cumplen.
- RF-01 y RF-12 (energía) y RF-03 (ocupación), y las pruebas CP-01, CP-02, CP-07 y CP-08.
- RF-09 (copiloto).

### Problemas de diseño de las cajas (aporte técnico para el reporte)

- La 18650 entrega entre 3.0 y 4.2 V: hace falta un LDO de baja caída de 3.3 V (≥500 mA) o un elevador a 5 V con cargador TP4056, y opcionalmente un panel solar.
- El MH-Z19 y el MQ-2 (con su calefactor de unos 150 mA) necesitan 5 V y consumen mucho, así que no son viables con batería todo el día: recomendar USB.
- La MLX90640 y el INMP441 muestrean continuamente: también conviene USB o recarga diaria.
- ESP-NOW consume menos que Wi-Fi con MQTT, pero el nodo de puerta igual debe enviar **por evento** (interrupción) más un heartbeat.
- **Lección de la Semana 7:** la tolerancia de "nodo caído" debe configurarse según el periodo de cada nodo.

---

## 6. Arquitectura (oficial del docente, más los añadidos del grupo)

```
Nodos 1-7 (ESP32 + sensor) ──ESP-NOW──► Gateway ESP32 v4 ──Wi-Fi/MQTT──►
┌──────────────── Servidor (Laptop, Docker) ── stack del DOCENTE ─────────────────┐
│ Mosquitto → Telegraf → InfluxDB → Grafana                                       │
├──────────────── AÑADIDOS DEL GRUPO 1 (nuestro trabajo) ─────────────────────────┤
│ • Motor de reglas y RAZONAMIENTO CAUSAL (lee InfluxDB/MQTT, escribe eventos y   │
│   diagnósticos de vuelta en InfluxDB y en un tópico MQTT)                       │
│ • DASHBOARD PROPIO: mediciones, condiciones vs requisitos, causas, efectos y    │
│   recomendaciones (puede ser web propia o paneles de Grafana)                   │
│ • Conteo de personas (MLX90640 + puerta), consumo fantasma (proxy o PZEM)       │
│ • Log de eventos / footprint (archivo + InfluxDB) · exportación CSV             │
│ • Gemelo digital en Gaphor sincronizado leyendo InfluxDB                        │
│ • Simulador que publica en el MISMO formato MQTT del Gateway                    │
│ • Copiloto de voz (PWA en celular) sobre la API del grupo                       │
└─────────────────────────────────────────────────────────────────────────────────┘
        ▲ cualquier laptop por Wi-Fi (navegador)        ▲ celular del vigilante
```

- Todo se agrega como **servicios nuevos en un `docker-compose.override.yml`**, sin romper el `docker-compose.yml` del docente.
- **Contrato de datos:** el formato y los tópicos los define el Gateway del docente. Se documentan en `docs/CONTRATO_DATOS.md` y **el simulador y todos los servicios del grupo deben respetarlos al pie de la letra**.

---

## 7. Requisitos

### 7.1 Esquema del grupo (se conserva)

**NS-1..7, RF-01..13, RNF-01..06 y CP-01..15**, con el texto tomado del repositorio. Se actualizan según la sección 5.

### 7.2 Requisitos de alto nivel de condición del salón (RA), que exige la EC3

Cada RA tiene **su propio grafo causal**. Los valores son de referencia: verificarlos y citarlos (ASHRAE 55, ASHRAE 62.1, EN 12464-1, ANSI S12.60 y el RNE peruano A.040 y EM.110). **Si el código del docente usa otros umbrales, alinear con él**; en CO2 ya coinciden: 1000 de alerta y 1500 de crítico. También pueden estar en el repositorio los umbrales que definió Esteban.

| ID | Requisito | Nodo | Nominal | Alerta | Crítico | Requisito relacionado |
|---|---|---|---|---|---|---|
| RA-01 | Confort térmico | 7 (BME280) | 20–26 °C | <20 o >26 | <18 o >28 | RF-02 |
| RA-02 | Humedad | 7 | 30–60 % | <30 o >60 | >70 | RF-02 |
| RA-03 | Calidad de aire y ventilación | 1 (CO2) | <800 ppm | ≥1000 | ≥1500 | RF-02, RF-08 |
| RA-04 | Iluminación para clase | 4 + 5 | 300–750 lux con ocupación | <300 | <150 | RF-02 |
| RA-05 | Seguridad: gas o humo | 3 (MQ-2) | Nivel base | Por encima del umbral calibrado | Muy por encima, o subida rápida | Nuevo |
| RA-06 | Aforo | 5 + 6 | ≤ aforo | ≥90 % | > aforo | RF-03 |
| RA-07 | Ambiente acústico | 2 (INMP441) | Fondo de 35–45 dB(A) | >70 dB sostenido | >85 dB | Nuevo |
| RA-08 | **Consumo fantasma** | 4 + 5 + horario (+ PZEM, si existe) | Sin luces ni equipos con el salón vacío | Más de 10 min | Más de 30 min o de noche | RF-10, NS-2 |
| RA-09 | Seguridad física | 6 (puerta) + horario | Cerrada fuera de horario | Abierta fuera de horario | Abierta con ocupación nocturna | RF-04 |
| RA-10 | Salud del sistema | Todos y el Gateway | Todos reportando | Nodo sin datos por más de su tolerancia, bit de falla o batería baja | Gateway caído o varios nodos caídos | RF-13 |

---

## 8. Razonamiento lógico con grafos dirigidos (estilo SymCure, como enseña el docente)

### Metodología

Fuentes: `Razonamiento con Grafos dirigidos - Symcure - Figueroa ES-1.pptx` y `Razonamiento por Grafos de Causalidad.pdf`.
- Eventos con valor **verdadero, falso o desconocido**. Causas raíz (F) y síntomas (S), unidos por aristas `causa → efecto`.
- **Lógica de salida:** AND, OR o N/M. **Lógica de entrada:** OR, AND, N/M o IF.
- **Propagación aguas abajo** (predicción de efectos) y **aguas arriba** (diagnóstico de causas). Por ejemplo, si un efecto con entrada OR es verdadero, sus causas pasan a ser sospechosas. Si un efecto es falso y la salida de la causa es AND, esa causa se descarta.
- Lo observado prevalece sobre lo inferido.
- Actividad del docente: grafos para resolver problemas de **operación y del estado de salud del sistema**.

### Qué construir

- Un grafo por RA en `graphs/*.yaml`, que también genera las figuras (Graphviz o Mermaid) y la vista del dashboard.
- El motor `reasoning/`, con pruebas por cada tipo de lógica.
- Sus observaciones de entrada son las mediciones de InfluxDB más **los niveles y bits de anomalía que ya calculan los nodos del docente**.

### Contenido borrador de los grafos

- **RA-01, temperatura alta:**
  - Causas: calor exterior (inferido), sol directo (lux natural alto y hora), ventilación inadecuada (puerta cerrada según el nodo 6, aire acondicionado apagado o con falla) y alta ocupación (nodo 5).
  - Efectos: somnolencia, golpe de calor y más gasto en climatización.
  - Recomendaciones: ventilar y revisar el aire acondicionado.
- **RA-01, temperatura baja:**
  - Causas: aire acondicionado con setpoint bajo o encendido sin ocupación (lo que es consumo fantasma).
- **RA-02, humedad fuera de rango:**
  - Causas: ocupación sin ventilación o clima húmedo de Lima.
  - Efectos: condensación, moho y daño a equipos.
- **RA-03, CO2 alto:**
  - Causas: puerta cerrada por mucho tiempo, ventilación insuficiente y ocupación alta.
  - Efectos: fatiga y menor rendimiento.
  - Recomendaciones: abrir la puerta, hacer una pausa o reducir el aforo.
- **RA-04, iluminación insuficiente con ocupación:**
  - Causas: luces apagadas, luminaria dañada, poca luz natural o cortinas cerradas.
  - Efecto: fatiga visual.
- **RA-05, gas o humo (MQ-2):**
  - Causas: humo por incendio o cortocircuito, fuga de gas (GLP o gas natural) o falsa alarma (polvo, aerosoles, sensor sin calentar).
  - Efectos: riesgo a la vida y evacuación.
  - Acciones: alerta crítica, aviso al vigilante y conteo de ocupantes.
- **RA-06, sobreaforo:**
  - Efectos: CO2 y temperatura altos, ruido y riesgo en una evacuación.
- **RA-07, ruido excesivo:**
  - Causas: actividad grupal, equipos o ruido exterior con la puerta abierta.
- **RA-08, consumo fantasma:**
  - Evento con lógica de entrada AND: luces o consumo encendidos, ocupación igual a 0 y duración mayor al umbral.
  - Efectos: soles y kg de CO2.
  - Acción: aviso al vigilante en su ronda.
- **RA-09, puerta abierta fuera de horario:**
  - Causas: olvido del cierre o acceso no autorizado (si hay ocupación térmica).
- **RA-10, nodo sin datos:**
  - Causas: batería agotada, Gateway caído (todos los nodos caen a la vez, lógica N/M), interferencia o canal ESP-NOW incorrecto, falla del sensor (bit de falla o valores fuera de rango) o caja apagada.
  - Efecto: los grafos dependientes pasan a "desconocido".

---

## 9. Dashboard propio (lo pide el anuncio del 06/11 y la pauta de la EC3) y copiloto

- **Contenido obligatorio:**
  1. Mediciones.
  2. Condición frente a cada RA (semáforo).
  3. **Causas, consecuencias y sugerencias** (salida del motor causal).
- **Opción A (rápida):** paneles nuevos en el Grafana del docente, más un panel de texto o tabla alimentado por los diagnósticos que el motor escribe en InfluxDB.
- **Opción B (recomendada para diferenciarse):** web propia con FastAPI y un frontend ligero que lee InfluxDB. Incluye:
  - plano 2D del L-419 con los 7 nodos;
  - vista del grafo causal activo (Cytoscape.js);
  - contador de ocupación;
  - consumo fantasma en soles y kg de CO2;
  - log de eventos con exportación a CSV;
  - salud de los nodos y del Gateway;
  - panel de escenarios de simulación;
  - etiqueta "DATOS SIMULADOS" siempre visible cuando corresponda.

  Se puede enlazar desde Grafana.
- **Accesible desde cualquier laptop por Wi-Fi.**
- **Copiloto de voz** (NS-1, RF-09): una PWA en el celular con la voz del navegador en español. Ofrece un briefing al inicio de la ronda, consultas y reporte oral de incidencias, que van al log. Es **secundario** frente a la EC3.

---

## 10. Simulación y modo demo (RF-11, requisito del docente)

- Publica en Mosquitto **con el mismo tópico y formato que el Gateway** (tomados del código del docente), de modo que Telegraf, InfluxDB, Grafana y nuestros servicios no distinguen la fuente. Agrega una marca `sim=true` si el formato lo permite.
- Modelo coherente con los 7 nodos:
  - horario de clases y ocupación;
  - CO2 por balance de masa;
  - temperatura y humedad según ocupación y aire acondicionado;
  - lux natural más artificial;
  - ruido según la actividad;
  - MQ-2 con su nivel base y eventos;
  - la puerta;
  - **matrices térmicas sintéticas de 32×24**;
  - niveles y bits de anomalía como los del código del docente.
- **Escenarios:** clase normal, consumo fantasma nocturno, aire acondicionado averiado, sobreaforo, puerta abierta fuera de horario, humo, batería agotada y Gateway caído.
- Tiempo acelerado, grabación y reproducción.

---

## 11. Firmware

- **El firmware oficial es del docente:** Arduino IDE, **.ino**, ESP-NOW con `paquetes.h` y `espnow_nodo.h`. **No se reescribe:** se estudia, se documenta y se reutiliza.
- **Entrega obligatoria del grupo:** **su propio programa .ino** (el anuncio del 02/11 lo exige también a los grupos sin caja), siguiendo la estructura del nodo de CO2. Candidatos naturales por los roles del grupo:
  - **nodo de puerta (KY-024)** con envío por interrupción y heartbeat;
  - **nodo de ocupación (MLX90640)** con el conteo coordinado con la puerta.

  Se nombra con el código del sensor (por ejemplo, `KY-024.ino`) y se sube a la carpeta de Drive del curso **solo cuando el usuario lo apruebe**.
- Debe compilar con `arduino-cli`, con el núcleo esp32 y las librerías necesarias, aunque no haya hardware.
- Conteo de ocupación: se recomienda procesarlo en el servidor. Hay que verificar si el nodo térmico del docente envía la matriz o solo un conteo: un paquete ESP-NOW tiene un máximo aproximado de 250 bytes, y la matriz de 768 floats no cabe en uno solo.

---

## 12. Gaphor (gemelo digital)

**Lo existente** (según la Semana 7): 12 diagramas en 4 paquetes (00 Vista general, 01 Requisitos, 02 Estructura, 03 Verificación), con «satisfy» y «verify» y un script de sincronización en vivo. Verificar en la auditoría.

**Cambios para la EC3** (la pauta pide reportar "modificaciones y nuevos aumentos"):
1. **02 Estructura:** migrar a la arquitectura oficial (7 nodos con sus sensores, Gateway ESP32 v4, la laptop con Mosquitto, Telegraf, InfluxDB y Grafana, y los servicios del grupo). Cada caja lleva ESP32, protoboard, 18650, porta-batería y regulador. Se cargan **las especificaciones y dimensiones de las imágenes con QR** (IMG_8423–8429).
2. **IBD:** sensor → ESP32 (I²C, UART, I²S, analógico) → ESP-NOW → Gateway → Wi-Fi/MQTT → Mosquitto → Telegraf → InfluxDB → dashboard, Gaphor y copiloto.
3. **01 Requisitos:** agregar RA-01..10 y los requisitos de las cajas, y actualizar RF y RNF.
4. **03 Verificación:** actualizar los CP.
5. **Nuevo paquete 04 Comportamiento** (pedido en "Ejemplos de temas EC2"):
   - **Actividades:** telemetría de un nodo por ESP-NOW, entrada y salida de personas, y detección, diagnóstico y alerta.
   - **Estados** (guiarse por `Maquinas_de_Estado.pptx`): el salón (Vacío, Ocupado, Sobreaforo, Luces sin ocupación, Alarma de gas, Fuera de horario) y los nodos (Calentando, Activo, Sin datos, Falla).
   - **Casos de uso:** clase, mantenimiento, limpieza, monitoreo del administrador, ronda del vigilante y emergencia.
6. **Nuevo paquete 05 Razonamiento:** grafos causales o su vínculo con los RA.
7. El **script de sincronización en vivo** se adapta para **leer desde InfluxDB**, como en la arquitectura del docente ("Gemelo digital lee de InfluxDB").
8. Tabla de cambios del modelo frente a la Semana 7, y exportación de todos los diagramas a PNG o SVG.

---

## 13. Gestión en ASANA (estado al 09/11)

Proyecto **"PI3 — Campus Twin L-419"**, administrado por José Eduardo:
- **S4 a S6:** completadas.
- **S7 a S14:** pendientes y vencidas.
- **"Instalación definitiva de los nodos en el L-419"** figura como completada **sin haberse hecho: desmarcarla**.
- Las tareas mencionan el hardware antiguo.

**Acciones:**
1. Renombrar las tareas a la arquitectura oficial y agregar tareas nuevas:
   - estudio del código del docente;
   - programa .ino propio;
   - dashboard propio;
   - motor causal y grafos por RA;
   - simulador en formato Gateway;
   - Gaphor (migración y paquetes 04 y 05);
   - reporte EC3;
   - logotipo;
   - cita en el L-414 para probar el hardware.
2. Adjuntar las imágenes con QR y las especificaciones (lo pidió el docente).
3. Reprogramar las fechas con honestidad y explicar la replanificación en la EC3.
4. Para el reporte, capturas reales.

---

## 14. Reporte EC3 (viernes 13/11 · un solo archivo · .docx y .pdf)

La rúbrica tiene 4 criterios de 4 puntos cada uno: conocimientos, avance, presentación y entregas completas.

1. **Portada:** Grupo 1, Sección 8, nombres completos con carreras, docente y fecha.
2. **Abstracto e introducción:** se parte de la Semana 7, con el consumo fantasma y el L-419.
3. **Avance desde la EC2:** tabla de estado (real, simulado o pendiente) y **adopción de la arquitectura oficial del curso**, explicando la migración.
4. **Sensores y procesadores:**
   - operación y desempeño de los 7 sensores;
   - **ESP-NOW**: por qué se usa, cómo funcionan el Gateway y la estructura de paquetes;
   - el .ino propio del grupo;
   - arquitectura final: ESP-NOW, MQTT, Telegraf, InfluxDB y Grafana;
   - acceso desde la laptop por Wi-Fi;
   - energía de las cajas.

   **Reconocer explícitamente el código del docente.**
5. **Razonamiento lógico:** RA-01..10, metodología, un grafo por RA y un ejemplo de propagación.
6. **Interfaz:** capturas del dashboard (los tres mínimos y la interactividad).
7. **Simulación y log** (rotulados como simulados).
8. **Gaphor:** diagramas nuevos y modificados, con la tabla de cambios.
9. **Asana:** capturas reales.
10. **Conclusiones y próximos pasos:** pruebas en el L-414, instalación en el L-419 y coordinación con S1 G1 (procesador central y CO2) y con los grupos de las cajas.
11. **Bibliografía (APA):** la de la Semana 7 y la EC2, más los datasheets, las normas, SymCure y la documentación de ESP-NOW, InfluxDB y Grafana.

Redacción sin condicional. Toda afirmación va con evidencia.

---

## 15. Estructura de carpetas (adaptar a la existente)

```
campus-twin/
├── CLAUDE.md                     # este documento
├── docs/curso/                   # material del curso (pptx, docx, xlsx, pdf, imágenes QR, ZIP Gemelo_IoT, .ino CO2, reportes del grupo)
├── vendor/gemelo_iot_profesor/   # ZIP descomprimido, SIN modificar
├── docs/                         # AUDITORIA.md, CONTRATO_DATOS.md, arquitectura, energía, tabla de cambios Gaphor
├── config/                       # requirements.yaml (RA), nodes.yaml, room_L419.yaml (plano, inventario de potencias), schedule.yaml
├── deploy/                       # docker-compose.override.yml con los servicios del grupo
├── gaphor/                       # modelo, scripts, sincronización con InfluxDB, exports/
├── graphs/  reasoning/           # grafos YAML + motor + tests
├── services/                     # reglas, ocupación, consumo fantasma, salud, log, API
├── dashboard/  copilot/          # interfaz web propia, PWA de voz
├── simulator/                    # publica en formato Gateway
├── firmware/                     # .ino propio(s) del grupo
├── asana/  report/               # gestión, generador del reporte + figuras
└── logs/                         # events.jsonl
```

---

## 16. Plan (del martes 10 al viernes 13 de noviembre)

1. **Martes:**
   - auditoría;
   - descomprimir y estudiar el código del docente;
   - `CONTRATO_DATOS.md`;
   - levantar el `docker-compose` del docente en local;
   - RA en configuración;
   - grafos y motor causal con pruebas.
2. **Miércoles:**
   - simulador en formato Gateway, para ver datos en Grafana;
   - servicios de reglas, ocupación, consumo fantasma, salud y log;
   - dashboard propio.
3. **Jueves:**
   - Gaphor (migración, paquetes 04 y 05, sincronización con InfluxDB) y exportación de diagramas;
   - .ino propio que compile;
   - Asana actualizado con capturas;
   - borrador del reporte.
4. **Viernes:**
   - copiloto, si hay tiempo;
   - revisión contra la rúbrica;
   - ensayo de la demo;
   - **subir un solo archivo**.

**Después:** pruebas con hardware en el L-414 e instalación en el L-419.

---

## 17. Pendientes que debe aportar el usuario

- [ ] Contenido de la carpeta propia (lo audita Claude Code).
- [ ] Rol de la Sección 8.
- [ ] Archivos del diseño de caja.
- [ ] Aforo y plano del L-419, horario, ubicación de la puerta y las luminarias, e **inventario de potencias** (luminarias, PC, proyector, aire acondicionado) para el proxy de consumo fantasma.
- [ ] Si se integrará el PZEM (preguntar al docente).
- [ ] Si el grupo compró sus propios sensores en algún momento.
- [ ] Estado de la C1 y del logotipo.

---

## Fuentes

- **Canvas (curso 25574):**
  - EC3 - Pautas;
  - Instrucciones EC2;
  - Instrumentación ... Compra.xlsx;
  - IP3 Asignación de Sensores y Procesador;
  - Caja de instrumentos y procesador;
  - Ejemplos de temas EC2;
  - PI3 - Proyecto;
  - Razonamiento con Grafos dirigidos - SymCure ES-1;
  - Razonamiento por Grafos de Causalidad;
  - Máquinas de Estado;
  - IMG_8423–8429 (identificación con QR);
  - nodo_co2_ModelMH-Z1911A.ino;
  - anuncios del 11/10 al 06/11.
- **Drive del docente:** "Gemelo_IoT" (gateway, 6 carpetas de nodos, servidor_iot y la arquitectura en PNG), descargado el 10/11.
- **Reportes del grupo:** Semana 7 (13/16) y EC2 (12/16).
- **Asana:** "PI3 — Campus Twin L-419", consultado el 09/11.
