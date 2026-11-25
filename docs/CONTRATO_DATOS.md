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
- **Desde el 17/11/2026 el Gateway del aula es otro** (`gateway_ap.ino`, §10): crea su propia red,
  no usa MQTT y sirve los mensajes por HTTP. El puente del grupo los lleva a este mismo flujo y le
  da la hora al Gateway.

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

## 9. Lo que publica y escribe el grupo

Todo va aparte del Gateway: en tópicos `campustwin/` y en measurements propios.

| Dónde | Nombre | Contenido |
|---|---|---|
| MQTT | `utec/gemelo/<grupo>/campustwin/evento` | Cada evento del log (JSON de `EventoDelAula`: ts, tipo, severidad, mensaje, origen, ra, nodo, causas, recomendaciones) |
| MQTT | `utec/gemelo/<grupo>/campustwin/ra` | Cada 10 s: `{"ts", "origen", "RA-01": nivel, …}`, con nivel -1 desconocido, 0 nominal, 1 alerta y 2 crítico |
| InfluxDB | `campustwin_evento` | Tags `grupo`, `origen`, `tipo`, `severidad`, `ra`, `nodo`. Fields `mensaje`, `severidad_num`, `causas` y `recomendaciones`. Lo escribe el servicio directamente, porque Telegraf solo escucha los 7 tipos |
| InfluxDB | `campustwin_ra` | Tags `grupo`, `origen`, `ra`. Fields `nivel` (−1..2) y `nivel_texto` |
| Archivo | `logs/events.jsonl` | El mismo log, una línea por evento. Es la copia que no depende de InfluxDB |

Grupos de datos:

- `sim`: el simulador;
- `rep`: la reproducción de una grabación (`gemelo/grabacion.py`), con el `ts` original. El campo
  `origen` dice "reproducido (simulado)" o "reproducido (real)";
- `l419`: los datos reales del aula, que el puente trae del Gateway con red propia (§10);
- el que use un Gateway MQTT real (`gateway.ino` del docente).

## 10. Gateway con red propia (`gateway_ap.ino`, en el aula desde el 17/11/2026)

> Fuente: [vendor/gateway_ap_l419/](../vendor/gateway_ap_l419/), adaptado por otro grupo del curso
> (repositorio `josecarita/Gemelo-digital-L419-Gateway`, commit `67cccfe`), y su
> [guía](curso/texto/guia-gateway-ap.md). Leído el 24/11/2026.

Es el Gateway que está instalado en el L-419. **No usa MQTT.** El flujo queda así:

```
Nodo ESP32 ──ESP-NOW──► Gateway v5 (red Wi-Fi propia GEMELO-L419, flash) ──HTTP──► laptop
  laptop: puente del grupo ──MQTT──► Mosquitto ──► Telegraf ──► InfluxDB ──► Grafana
                                          └──► servicio del grupo ──► tablero y Gaphor en vivo
```

- **Red:** el Gateway crea la red `GEMELO-L419` en el canal 1 (la clave está en la guía original y
  en `gateway_ap.ino`, que no se versiona). Su IP es `192.168.4.1`, también
  `http://gemelo-gateway.local`. La laptop que se conecta se queda sin internet mientras esté ahí.
- **Nodos:** buscan esa red para hallar el canal (`SSID_ROUTER = "GEMELO-L419"`) y envían a la MAC
  STA del Gateway, `58:2A:BD:72:03:DC` según la guía.
- **Paquetes:** `paquetes.h` es idéntico al del docente, `PROTO_VERSION 1`.
- **Almacenamiento:** cada mensaje se guarda en la flash (dos archivos de 600 KB que rotan, unos
  1,2 MB en total) con un `id` correlativo que sobrevive a los reinicios.

**API HTTP** (todas con `Access-Control-Allow-Origin: *`):

| Ruta | Devuelve |
|---|---|
| `/api/estado` | `gw_ms`, `ts` (0 sin hora), `hora_ok`, `id_ultimo`, uso de la flash, `descartados`, motivo del último reinicio, `laptops` conectadas y `modo` (`AP` o `STA`) |
| `/api/ultimos` | Una entrada por nodo: `{"nodo","tipo","hace_s","anomalias","msg":{…mensaje completo…}}`. `hace_s` = −1 si el dato es de antes del último reinicio |
| `/api/datos?desde=<id>&max=<n>` | Los mensajes guardados con `id > desde`, uno por línea (JSONL), como mucho `n` (2000 por defecto) |
| `/api/hora?epoch_ms=<ms>` | Le da al Gateway la hora de la laptop; sin internet no tiene NTP |
| `/api/borrar?confirmar=si` | Borra lo guardado |

**Mensaje:** el mismo JSON de §5, con dos campos más: `id` (primero) y `gw_ms` (el reloj interno
del Gateway al recibir, justo después de `ts`). Ejemplo de la guía:

```json
{"id":15,"nodo":1,"mac":"24:6F:28:AB:12:01","seq":2,"ts":1794950267527,"gw_ms":10024,
 "uptime_ms":13024,"perdidos":0,"tipo":"co2","co2_ppm":845,"delta_30s":12,"temp_c":24,
 "calentando":0,"nivel":"NORMAL","anomalias":"NINGUNA","anom_bits":0}
```

`ts` sigue siendo `null` mientras nadie le dé la hora al Gateway. No hay `gateway/estado` ni LWT:
que el Gateway esté caído se sabe porque deja de responder.

### El puente del grupo

`demo/servidor/gemelo/puente_gateway.py` conecta este Gateway con el resto del sistema sin cambiar
nada de lo demás. La configuración está en `gateway_ap` de `config/nodos.yaml`. Cada 2 s:

1. pide `/api/estado`; si `hora_ok` es falso, le da la hora de la laptop con `/api/hora`. Esto
   resuelve el problema de `ts: null` de §1 sin NTP local;
2. pide `/api/datos?desde=<último id publicado>` y publica cada mensaje en
   `utec/gemelo/l419/nodo<id>/<tipo>` **sin `id` ni `gw_ms`**, es decir, exactamente el formato de §5.
   Si algún mensaje llega con `ts` nulo, su hora se estima con `gw_ms` y la última hora del Gateway;
3. publica `online` u `offline` retenido en `utec/gemelo/l419/gateway/estado` según si el Gateway
   responde (`offline` tras 3 pedidos fallidos seguidos), y deja `offline` como testamento (LWT)
   por si el puente se cae. Así RA-10 sigue distinguiendo "Gateway caído" de "nodo caído".

Por defecto el puente empieza por lo que llega desde que arranca; `--desde 0` reenvía todo lo que el
Gateway tenga guardado. El grupo `l419` es distinto de `sim`, así que el servicio y el tablero lo
rotulan como **real**. Se ensaya con `gemelo/gateway_falso.py`, que imita esta API con datos del
simulador y publica en el grupo `sim` (ver [07-prueba-en-el-salon.md](07-prueba-en-el-salon.md)).

