# Contrato de datos — arquitectura oficial del curso

> Fuente: código del docente en [vendor/gemelo_iot_profesor/](../vendor/gemelo_iot_profesor/),
> leído el 10/11/2026. Si el docente publica una versión nueva, se compara contra esta.
> **Todo lo que el grupo construya (simulador, motor causal, dashboard, enlace con Gaphor) lee y
> escribe este formato al pie de la letra.** El contrato propio de la demo (`l419/<nodo>/<magnitud>`,
> en `demo/servidor/campus_twin_demo/contrato.py`) queda reemplazado por este.

## 1. Flujo

```
Nodo ESP32 + sensor ──ESP-NOW (paquete binario)──► Gateway ESP32 v4 ──Wi-Fi/MQTT (JSON)──►
Mosquitto :1883 ──► Telegraf ──► InfluxDB 2.7 :8086 (org utec, bucket gemelo) ──► Grafana :3000
```

- Los nodos **no** se conectan al Wi-Fi: solo lo escanean para saber en qué canal está el Gateway
  (`buscarCanal(SSID_ROUTER)`) y le envían por ESP-NOW a su MAC (`MAC_GATEWAY`).
- El Gateway sí se conecta al Wi-Fi, traduce cada paquete a JSON y lo publica en Mosquitto.
- El Gateway toma la hora de `pool.ntp.org`. **Sin internet, `ts` sale `null` y Telegraf descarta
  el mensaje completo.** Se comprobó el 10/11/2026 en el stack local: el error es
  `'json_time_key' could not be found` y no llega nada a InfluxDB. Es decir, sin NTP no se pierde
  solo la hora, se pierden todos los datos. Esto choca con RNF-05 (operación sin internet). Las
  salidas posibles son un servidor NTP en la laptop o un `json_time_key` opcional en Telegraf.

## 2. Nodos

| Nodo | `tipo` | Sensor | Interfaz y pines | Envío | Notas del código |
|---|---|---|---|---|---|
| 1 | `co2` | MH-Z1911A (familia MH-Z19, NDIR) | UART2: RX 16, TX 17, 9600 baudios | cada 5 s | Calienta 3 min. Alerta en 1000 ppm, crítico en 1500, histéresis de 100 y 3 confirmaciones. Válido de 300 a 10000 ppm. Marca un pico si sube ≥ 300 ppm en 30 s. |
| 2 | `audio` | INMP441 | I²S: SCK 26, WS 25, SD 33, a 16 kHz | cada 1 s | dB SPL ≈ dBFS + 120 (`OFFSET_SPL_DB`, sin calibrar). **No guarda audio.** Calibra durante los primeros 5 s, en silencio. |
| 3 | `gas` | MQ-2 | analógica + digital | — | **No hay código del nodo en el ZIP.** El paquete y el Gateway ya existen. |
| 4 | `luz` | BH1750 (GY-302) | I²C: SDA 21, SCL 22 | cada 10 s, y en el acto si cambian las luces | Estimación sobre la mesa: `lux_mesa_est = lux × 0.482`. Iluminación baja por debajo de 300 lx, con histéresis de 30. |
| 5 | `termico` | MLX90640 32×24 | I²C: SDA 21, SCL 22 | cada 5 s, y en el acto tras un cruce | **El conteo se hace en el ESP32**: sustrae el fondo, sigue las cabezas y detecta el cruce de las líneas A y B. Solo envía entradas y salidas, **no la matriz**. Se monta en el marco superior de la puerta, a 2.3 m. |
| 6 | `magnetico` | KY-024 (Hall SS49E, lineal) | analógica en GPIO 34 | cada 10 s, y en el acto ante un cambio | La salida es invertida: lectura < 1200 es puerta cerrada y > 1800 es puerta abierta. Antirrebote de 150 ms. Marca la puerta como abierta prolongada a los 10 min. |
| 7 | `ambiente` | BME280 (GY-BME280) | I²C: SDA 21, SCL 22 | cada 10 s | Confort de 20 a 26 °C con histéresis de 0.5. Humedad alta desde 70 %, con histéresis de 5. Cambio rápido si varía más de 1.5 °C en 5 min. |
| GW | — | ESP32 v4 | Wi-Fi STA | — | Cola de 32 mensajes. Cuenta las muestras perdidas por huecos en `seq`. |

Todos los nodos tienen fijo `NODO_ID` y `MAC_GATEWAY`. Lo único que cambia de una instalación a
otra es `SSID_ROUTER`.

## 3. Paquete ESP-NOW (`paquetes.h`, `PROTO_VERSION 1`)

Todos los paquetes empiezan con la misma cabecera, empaquetada y de 11 bytes:

| Campo | Tipo | Significado |
|---|---|---|
| `version` | uint8 | `PROTO_VERSION` (1) |
| `tipo` | uint8 | 1 CO₂, 2 audio, 3 gas, 4 luz, 5 térmico, 6 magnético, 7 ambiente |
| `nodo_id` | uint8 | id único en todo el proyecto |
| `seq` | uint32 | contador. Si retrocede, el nodo se reinició |
| `uptime_ms` | uint32 | `millis()` del nodo |

Cuerpos (cada uno debe medir ≤ 250 bytes):

| Paquete | Campos después de la cabecera |
|---|---|
| `PaqueteCO2` (19 B) | `co2_ppm` (−1 sin respuesta, −2 error de checksum), `delta_30s`, `temp_c`, `calentando`, `nivel`, `anomalias` |
| `PaqueteAudio` (38 B) | `leq_db`, `lmax_db`, `pico_db`, `base_db`, `freq_dom_hz`, `tonal` (0 a 1), `bloques_fuertes`, `calibrando`, `anomalias` |
| `PaqueteTermico` (29 B) | `entradas`, `salidas`, `ocupacion_est` (≥ 0), `personas_en_vista`, `cruces_dudosos`, `t_fondo`, `t_max`, `calibrando`, `anomalias` |
| `PaqueteMagnetico` (21 B) | `puerta_abierta`, `aperturas`, `seg_abierta`, `campo_raw` (0 a 4095), `anomalias` |
| `PaqueteAmbiente` (24 B) | `temp_c` (NAN si falla), `hum_pct`, `pres_hpa`, `anomalias` |
| `PaqueteLuz` (29 B) | `lux`, `lux_min`, `lux_max`, `lux_mesa_est`, `luces_cambio` (+1, −1 o 0), `anomalias` |
| `PaqueteGas` (22 B) | `v_ao`, `rs_r0` (1 es aire limpio, menos indica gas; NAN si no está listo), `do_alarma`, `calentando`, `anomalias` |

## 4. Niveles y bits de anomalía

Cada nodo calcula sus propias anomalías y las envía como bits. El Gateway las traduce a texto. **Son
las observaciones de entrada del motor causal.**

| `tipo` | bit 0 | bit 1 | bit 2 | bit 3 |
|---|---|---|---|---|
| `co2` | FALLO_SENSOR | CO2_PICO_RAPIDO | CO2_ALERTA_VENTILACION | CO2_CRITICO |
| `audio` | FALLO_AUDIO | RUIDO_IMPACTO | RUIDO_FUERTE_SOSTENIDO | RUIDO_MECANICO_CONSTANTE |
| `termico` | FALLO_SENSOR | CONTEO_CORREGIDO | OBJETO_ESTATICO | — |
| `magnetico` | FALLO_SENSOR | PUERTA_ABIERTA_PROLONGADA | — | — |
| `ambiente` | FALLO_SENSOR | TEMP_FUERA_CONFORT | HUMEDAD_ALTA | CAMBIO_RAPIDO_TEMP |
| `luz` | FALLO_SENSOR | ILUMINACION_BAJA | — | — |
| `gas` | FALLO_SENSOR | GAS_DETECTADO | — | — |

El campo `nivel` del CO₂ toma los valores `NORMAL`, `ALERTA`, `CRITICO`, `CALENTANDO`, `SIN_DATO` o
`DESCONOCIDO`.

## 5. Mensaje MQTT que publica el Gateway

**Tópico:** `utec/gemelo/<grupo>/nodo<id>/<tipo>`, por ejemplo `utec/gemelo/grupoX/nodo1/co2`.
`<grupo>` es la constante `GRUPO` del Gateway y viene como `"grupoX"`.

**Estado del Gateway:** `utec/gemelo/<grupo>/gateway/estado`, con `online` o `offline` retenidos. El
`offline` se publica solo, por LWT, si el Gateway se cae. Es la señal de "Gateway caído" para RA-10.

**Cuerpo:** JSON plano. Primero van los campos comunes y luego los del tipo:

```json
{"nodo":1,"mac":"AA:BB:CC:DD:EE:FF","seq":1234,"ts":1762800000000,"uptime_ms":3600000,
 "perdidos":2,"tipo":"co2","co2_ppm":812,"delta_30s":15,"temp_c":24,"calentando":0,
 "nivel":"NORMAL","anomalias":"NINGUNA","anom_bits":0}
```

- `ts` está en milisegundos Unix (UTC) y vale `null` si no hay NTP.
- `perdidos` es acumulado, calculado por el Gateway desde los huecos en `seq`.
- `anomalias` es texto con los nombres separados por `|`, o `NINGUNA`. `anom_bits` es el entero.
- Los NAN salen como `null`.
- QoS 0 y sin retención. Mosquitto acepta conexiones anónimas (`allow_anonymous true`), igual que el
  Gateway (`MQTT_USER` vacío).

## 6. InfluxDB (lo que escribe Telegraf)

| Concepto | Valor |
|---|---|
| Suscripción | `utec/gemelo/+/+/{co2,audio,termico,magnetico,ambiente,luz,gas}` con QoS 0 |
| Measurement | el campo `tipo`: `co2`, `audio`, `termico`, `magnetico`, `ambiente`, `luz` o `gas` |
| Tags | `nodo`, `mac`, `grupo` (sale del tópico) y `topic` (lo agrega Telegraf) |
| Campos de texto | `nivel`, `anomalias` |
| Campos numéricos | todos los demás, incluidos `seq`, `perdidos`, `uptime_ms` y `anom_bits` |
| Hora | `ts` (unix_ms) |
| Ubicación | org `utec`, bucket `gemelo` y consultas en Flux |

Ejemplo de consulta (Flux):

```flux
from(bucket: "gemelo") |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "co2" and r._field == "co2_ppm")
```

## 7. Grafana del docente

Hay dos tableros provisionables, en `servidor_iot/*.json`:

- **"Gemelo digital L418 — 7 sensores"** (`gemelo-l418-completo`, refresco de 10 s):
  - estado actual: ocupación, puerta, CO₂, índice de gas, Leq, temperatura, humedad y luz sobre la mesa;
  - salud: segundos desde el último dato y paquetes perdidos;
  - series de ocupación, entradas y salidas, línea de tiempo de la puerta, CO₂, Rs/R0,
    temperatura, humedad, presión, nivel sonoro e iluminancia;
  - tabla de anomalías;
  - tablas de datos crudos para exportar.
- **"Gemelo digital — Sensores IoT UTEC"** (`gemelo-iot-utec`, refresco de 5 s): la versión anterior,
  con solo CO₂ y audio.

Lo que el docente **no** cubre, y por eso es el aporte del grupo:

- la condición frente a cada requisito de alto nivel (RA);
- las causas, consecuencias y recomendaciones de cada anomalía (motor causal);
- el log de eventos;
- el consumo fantasma;
- el gemelo en Gaphor.

## 8. Reglas para el grupo

1. **No se cambia el formato.** Si el grupo necesita un dato más, lo publica en un tópico propio (por
   ejemplo `utec/gemelo/<grupo>/diagnostico/...`) o lo escribe en su propio measurement de InfluxDB.
   Los tópicos del Gateway no se tocan.
2. **Los datos simulados van con el grupo `sim`.** El simulador publica en `utec/gemelo/sim/nodo<id>/<tipo>`
   con el mismo JSON, así que todo lo que los consuma los distingue por la tag `grupo`, y el
   dashboard muestra "DATOS SIMULADOS".
3. **Nodo nuevo, `tipo` nuevo.** Si se agrega un nodo (por ejemplo, PZEM como nodo 8), lleva un `tipo`
   nuevo en `paquetes.h`. Ese cambio se coordina con el docente, porque el Gateway es común a todos.
