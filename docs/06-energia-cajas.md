# Energía de las cajas (nodos 1-7 y Gateway)

> **Estimado, sin medición real: pendiente para S15 con multímetro (CP-13).** Cada valor sale de
> una hoja de datos o de la lectura del código del docente, y su fuente está en
> [config/energia_nodos.yaml](../config/energia_nodos.yaml). Lo que se mida en S15 se cambia allí, y
> la tabla se regenera con:
>
> ```bash
> demo/servidor/.venv/bin/python firmware/energia/autonomia.py
> ```
>
> El análisis y el script son del Grupo 1. El firmware que se analiza es del docente, salvo el nodo
> 3 (`firmware/MQ-2/MQ-2.ino`, del grupo).

## 1. Qué hay en cada caja

Según la [lista de compra](curso/texto/lista-de-compra.md), el [brief de la EC3](curso/brief-ec3.md)
y las fotos de `curso/imagenes/`, cada caja lleva:

- un **ESP32 DevKit V1** (NodeMCU-32, 30 pines, micro-USB). Trae un regulador AMS1117-3.3, un LED de
  encendido y un puente USB-serie;
- el sensor;
- una **18650 de 1600 mAh** con su porta-batería;
- una protoboard de 170 puntos.

**No se compró ningún regulador ni ningún cargador.** La [guía de cajas](curso/texto/caja-instrumentos.md)
pide manejar la energía, un interruptor y, de preferencia, recarga con luz ambiental.

### El problema de conectar la 18650

La celda entrega de 4.2 V (llena) a 3.0 V (vacía), y ninguna de las dos conexiones directas sirve:

| Conexión | Qué pasa |
|---|---|
| Directa al pin **3V3** | El ESP32 admite de 3.0 a 3.6 V (hoja de datos). Con 4.2 V queda fuera de especificación y se puede dañar. |
| Al pin **VIN** (pasa por el AMS1117 del DevKit) | El AMS1117 cae unos 1.1 V. El riel queda en ~2.6 V con 3.7 V de batería: el ESP32 se reinicia por *brownout* en los picos de transmisión (240 mA). Los sensores de 5 V (MQ-2, MH-Z1911A) tampoco reciben su voltaje. |

Hay dos soluciones, y ninguna está comprada:

- **A. LDO de 3.3 V de baja caída** (ME6211 o AP2112K, de 500 mA o más) al pin 3V3. Sirve solo para
  los nodos cuyos sensores van a 3.3 V. Al ser lineal, la batería entrega la misma corriente que
  consume la carga. Deja de regular hacia los 3.4-3.5 V, y se supone que aprovecha el 85 % de la
  carga.
- **B. Elevador a 5 V** (MT3608, o un módulo que integre cargador TP4056 y elevador) al pin VIN.
  Sirve para todos los nodos y es obligatorio para el MQ-2 y el MH-Z1911A. Se supone un 85 % de
  eficiencia. Además, el riel de 3.3 V vuelve a pasar por el AMS1117 del DevKit, que pierde
  (5 − 3.3) V y tiene 5 mA de reposo.

Para recargar la celda dentro de la caja hace falta un **TP4056 con protección** (DW01), que
tampoco se compró.

## 2. Consumo del ESP32 con el firmware del docente

Del código de `vendor/gemelo_iot_profesor/`:

- Ningún nodo usa *deep sleep*, *light sleep* ni `esp_wifi_set_ps`. `espnow_nodo.h` hace
  `WiFi.mode(WIFI_STA)` y `WiFi.disconnect()`, y el `loop()` es un sondeo de `millis()` sin pausa.
  Como no se asocia a un punto de acceso, el *modem sleep* no actúa: **la radio queda escuchando
  todo el tiempo**. Según la hoja de datos del ESP32-WROOM-32, eso son 95-100 mA. Se usan 100 mA.
- Los envíos casi no cuentan. Un paquete ESP-NOW de 19-38 B a 1 Mbps dura menos de 1 ms a 240 mA:
  con un envío por segundo (audio), suma unos 0.24 mA.
- Si fallan 10 envíos seguidos, se vuelve a escanear el canal (unos 2 s). Es raro y no se cuenta.
- A eso se suma el DevKit: el LED de encendido y el puente USB-serie, unos 3 mA (supuesto).
- El Gateway hace `WiFi.setSleep(false)` (en `gateway.ino.example`) para no perder paquetes: su
  radio también está siempre encendida, y además transmite MQTT. Se estiman 110 mA.

## 3. Presupuesto por nodo

Corriente de cada sensor, según su hoja de datos:

| Nodo | Sensor | Alimentación | Corriente | Fuente |
|---|---|---|---|---|
| 1 co2 | MH-Z1911A | 5 V (4.5-5.5 V) | 60 mA de promedio, 150 mA de pico | Hoja de datos Winsen MH-Z19B; **falta confirmarlo con la del MH-Z1911A** |
| 2 audio | INMP441 | 3.3 V | 1.4 mA | Hoja de datos TDK InvenSense |
| 3 gas | MQ-2 | 5 V ± 0.1 | 150 mA del calefactor (33 Ω), más ~3 mA del LED y el LM393 | Hoja de datos Hanwei MQ-2 |
| 4 luz | BH1750 (GY-302) | 3.3 V | 0.12 mA (0.19 máx.), más el regulador del módulo | Hoja de datos ROHM |
| 5 térmico | MLX90640 | 3.3 V | < 23 mA | Hoja de datos Melexis |
| 6 magnético | KY-024 (SS49E) | 3.3 V | 6 mA típ. (10 máx.), más el LM393 y el LED: ~8 mA | Hoja de datos Honeywell SS49E |
| 7 ambiente | BME280 | 3.3 V | 3.6 µA a 1 Hz en modo forzado: domina el regulador del módulo | Hoja de datos Bosch |

La tabla de autonomía es la salida de `firmware/energia/autonomia.py`, con una 18650 de
1600 mAh y 3.7 V:

| Nodo | Sensor | Riel del sensor | ESP32 + placa (mA, 3.3 V) | Sensor (mA) | Por USB/VIN (mA a 5 V) | Energía por día en USB (Wh) | 18650 + LDO 3.3 V | 18650 + elevador 5 V |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 co2 | MH-Z1911A | 5 V | 103.0 | 60 | 168 | 20.2 | no aplica (sensor a 5 V) | 5.7 h |
| 2 audio | INMP441 | 3.3 V | 103.2 | 1.4 | 110 | 13.2 | 13.0 h | 8.7 h |
| 3 gas | MQ-2 | 5 V | 103.0 | 153 | 261 | 31.3 | no aplica (sensor a 5 V) | 3.7 h |
| 4 luz | BH1750 (GY-302) | 3.3 V | 103.0 | 0.2 | 108 | 13.0 | 13.2 h | 8.8 h |
| 5 termico | MLX90640 | 3.3 V | 103.0 | 23 | 131 | 15.7 | 10.8 h | 7.3 h |
| 6 magnetico | KY-024 (SS49E) | 3.3 V | 103.0 | 8 | 116 | 13.9 | 12.2 h | 8.2 h |
| 7 ambiente | BME280 (GY-BME280) | 3.3 V | 103.0 | 0.1 | 108 | 13.0 | 13.2 h | 8.8 h |
| GW | ESP32 v4 (Wi-Fi + MQTT) | — | 113.5 | 0 | 118 | 14.2 | USB | 8.1 h |

Cómo se calcula:

- **18650 + LDO:** `1600 mAh × 0.85 / (I₃V₃ + Iq del LDO)`.
- **18650 + elevador:** `1600 mAh × 3.7 V × 0.95 / (5 V × I₅V / 0.85)`.
- **Por USB:** la corriente a 5 V que entra por VIN o por el micro-USB, incluido el AMS1117 del
  DevKit.

### Lectura de la tabla

- **Con el firmware actual, ninguna caja llega a un día con una 18650.** La radio del ESP32
  escuchando siempre se lleva unos 100 mA, que es casi todo el consumo de los nodos de 3.3 V.
- El **MQ-2 es el peor caso: 3.7 h**. El calefactor (150 mA a 5 V) consume más que el propio ESP32,
  y no se puede apagar entre lecturas: tras cada encendido necesita su precalentamiento.
- El **MH-Z1911A** (5.7 h) también necesita 5 V y su lámpara IR da picos de 150 mA. Para el
  regulador, hay que contar el pico, no el promedio.
- El **MLX90640** y el **INMP441** muestrean sin parar (8 cuadros/s y I²S a 16 kHz): no hay ciclo
  de trabajo que recortar.
- Toda la instalación por USB necesita unos **1.1 A a 5 V** (suma de la columna USB, con el
  Gateway), es decir, **unos 135 Wh al día**.

## 4. Escenario con *deep sleep* (hipotético, no implementado)

Solo los nodos de **luz** y **ambiente** hacen una lectura puntual y pueden dormir entre lecturas.
El escenario supone que el nodo despierta cada 60 s, mide, envía y vuelve a dormir en unos 0.3 s,
guardando el canal en la memoria RTC para no volver a escanear. Exige cambiar el firmware del
docente: sería un derivado del grupo, coordinado con él, porque cambia el periodo de 10 s.

| Nodo | Promedio con DevKit tal cual (mA) | Autonomía | Promedio sin LED ni USB-serie (mA) | Autonomía |
|---|---:|---:|---:|---:|
| 4 luz | 3.71 | 361 h (15 días) | 0.71 | 1780 h (74 días) |
| 7 ambiente | 3.61 | 371 h (15 días) | 0.61 | 2048 h (85 días) |

En ese escenario lo que más consume es la placa: el LED y el puente USB-serie, que no duermen.
Para pasar de semanas a meses hay que quitar el LED o usar un ESP32 sin puente USB. El **nodo
magnético no entra** aquí: el SS49E es lineal y consume ~6 mA continuos para vigilar la puerta. Con
batería, el piso es de unos 5 días (11 mA); el requisito anterior RNF-04 (≥ 30 días) pedía un
interruptor de lengüeta (*reed*), que consume microamperios.

## 5. Recomendaciones

| Caja | Recomendación | Motivo |
|---|---|---|
| GW | **USB fijo** (laptop o cargador de 5 V) | `WiFi.setSleep(false)` y transmisión MQTT constante. Si se cae, se pierde todo el aula (RA-10). |
| 3 gas (MQ-2) | **USB fijo de 5 V / 1 A** | 261 mA a 5 V: 3.7 h con batería. Además, el MQ-2 necesita el calefactor encendido sin cortes para que R0 siga siendo válido. |
| 1 co2 (MH-Z1911A) | **USB fijo de 5 V** | 5.7 h con batería y picos de 150 mA. Calienta 3 min en cada arranque. |
| 5 térmico (MLX90640) | **USB fijo** | Muestreo continuo: 7-11 h. Está sobre la puerta, a 2.3 m, donde cambiar la batería cuesta. |
| 2 audio (INMP441) | **USB fijo**, o batería con recarga diaria | Muestreo continuo: ~13 h con LDO, que alcanza para la jornada pero no para la noche. |
| 6 magnético (KY-024) | **USB**, o batería con recarga diaria | ~12 h. El SS49E no permite dormir: para meses habría que cambiar el sensor. |
| 4 luz, 7 ambiente | **Batería + LDO** ahora (~13 h, recarga diaria); con *deep sleep*, semanas | Son los únicos donde la batería tiene sentido. |

Otras recomendaciones:

- **Para la demo del 13/11, todo por USB** (power banks o cargadores). La 18650 queda como respaldo
  o para mostrar el diseño de la caja.
- Si la caja lleva batería: **TP4056 con protección**, más LDO (nodos de 3.3 V) o elevador (nodos
  de 5 V), más el **interruptor** que pide la guía. El elevador tiene que aguantar picos de
  300-400 mA en los nodos de 5 V.
- **La recarga con luz ambiental no alcanza.** Un panel pequeño bajo 300-500 lx de interior entrega
  del orden de milivatios, y cada caja consume entre 0.4 W (3.3 V con LDO) y 1.5 W (MQ-2, con
  elevador): faltan dos o tres órdenes de magnitud. Esto es una estimación y se puede comprobar en
  S15 midiendo la corriente del panel junto a la ventana.
- **El voltaje de batería no viaja en ningún paquete.** `paquetes.h` no tiene campo `bat_v`, así
  que el RA-10 no puede detectar "batería baja": solo ve "nodo sin datos". Agregarlo cambia
  `paquetes.h` y el Gateway, que son comunes a todo el curso, y hay que coordinarlo con el docente.

## 6. Cómo medirlo en S15 (CP-13)

**Material:** multímetro, medidor USB de corriente (si hay), la 18650 cargada, un cronómetro y el
monitor serie (`arduino-cli monitor -c baudrate=115200`).

1. **Corriente por USB, por nodo.** Con el medidor USB entre el cargador y el DevKit, anotar la
   corriente promedio en dos momentos:
   - durante el calentamiento (MQ-2: 60 s; MH-Z1911A: 3 min);
   - en régimen, después de un minuto.
   
   Se compara con la columna "Por USB/VIN (mA a 5 V)".
2. **Corriente desde la batería.** Poner el multímetro en serie entre la 18650 y el regulador. Usar
   la **escala de 10 A** para el MQ-2 y el MH-Z1911A: en la escala de mA, la caída en el shunt
   puede reiniciar el ESP32. El multímetro promedia: los picos de TX (240 mA, < 1 ms) no se ven, y
   está bien así, porque lo que importa es el promedio.
3. **Separar el ESP32 del sensor.** En un nodo de 3.3 V (luz), medir con y sin el sensor
   conectado. Así se obtiene el consumo real del ESP32 con ESP-NOW (`radio_escucha_ma` +
   `placa_ma`).
4. **Ensayo de descarga.** Un nodo de 3.3 V (luz o ambiente), con la 18650 llena (4.2 V) y el LDO:
   se deja funcionando y se anota la hora del último paquete que recibe el Gateway (`uptime_ms`, o
   el hueco en Grafana). Se compara con las ~13 h estimadas, y de paso se valida `capacidad_mah`
   y `fraccion_util_ldo`.
5. **Registrar.** Cada número medido va a [config/energia_nodos.yaml](../config/energia_nodos.yaml)
   con `supuesto: false` y la fuente ("medido en S15, multímetro X, fecha"). Después se regenera
   esta tabla y se actualiza el rótulo de este documento: estimado → real.

Criterio de aceptación de CP-13, propuesto: la autonomía medida queda dentro de ±25 % de la
estimada. Si no, se corrige el modelo, no el resultado.
