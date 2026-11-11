# Instrumentación del aula laboratorio L-419 — arquitectura oficial

> **Historial:** reescrito el **10/11/2026** para la arquitectura oficial del curso. La lista de
> materiales propia del grupo (v2 del 10/09/2026, S/ 2808) queda resumida en la
> [sección 6](#6-histórico-propuesta-original-del-grupo-reemplazada); la versión completa está en
> git y en [data/instrumentacion-l419.csv](data/instrumentacion-l419.csv).
>
> Fuentes: el código del docente en [vendor/gemelo_iot_profesor/](../vendor/README.md), el
> [contrato de datos](CONTRATO_DATOS.md), [config/nodos.yaml](../config/nodos.yaml),
> [config/aula_l419.yaml](../config/aula_l419.yaml) (`plano`) y la
> [lista de compra del curso](curso/texto/lista-de-compra.md).
>
> **Estado al 10/11/2026:** el hardware está en el L-414 y **ningún nodo está armado ni
> instalado**. No hay mediciones reales; las ubicaciones son supuestas hasta tomar el croquis del
> aula.

## 1. Cómo funciona

**Cadena de datos:** sensor → ESP32 → ESP-NOW → Gateway ESP32 → Wi-Fi/MQTT → laptop con Docker
(Mosquitto → Telegraf → InfluxDB → Grafana) → servicios del grupo → dashboard, Gaphor y copiloto.

| Aspecto | Descripción |
|---|---|
| Transporte | Cada nodo envía un paquete binario (`paquetes.h`, ≤ 250 B) por **ESP-NOW** a la MAC del Gateway. Los nodos no se conectan al Wi-Fi: solo lo escanean para hallar el canal del Gateway. |
| Gateway | Traduce cada paquete a JSON y lo publica en `utec/gemelo/<grupo>/nodo<id>/<tipo>`; su estado va por LWT en `.../gateway/estado`. Cuenta las muestras perdidas por huecos en `seq`. |
| Servidor | Una laptop con el stack Docker del docente. Los servicios del grupo se agregan con `docker-compose.override.yml`; cualquier laptop de la misma red abre el dashboard (`:8000`) y Grafana (`:3000`). |
| Instalación | Cajas a batería con montaje adhesivo: sin cable de datos, sin 220 V, sin perforar paredes ni tocar el tablero. |
| Sin internet | Todo corre en la red local, salvo la hora: el Gateway la toma de `pool.ntp.org` y sin ella Telegraf descarta los mensajes. Se resuelve con NTP local en la laptop (pendiente, S15). |
| Autoría | Firmware de los nodos y del Gateway y stack del servidor: **docente** (J. F. Figueroa). Nodo MQ-2 (`MQ-2.ino`): **grupo**. Cajas: otros grupos del curso. |

## 2. Los 7 nodos

Periodos de `PERIODO_MS` en cada `.ino` del docente (y de `config/nodos.yaml` para el MQ-2).
Anomalías: los bits que calcula cada nodo y el Gateway traduce a texto (contrato, §4). Son las
observaciones de entrada del motor causal. Coordenadas en metros desde la esquina de la puerta
(x a lo largo, y a lo ancho), todas **supuestas**.

| Nodo | `tipo` | Sensor | Magnitudes que envía | Interfaz y pines | Periodo | Anomalías que emite | Ubicación (x, y) y montaje | RA | Caja | Programa |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `co2` | MH-Z1911A (familia MH-Z19, NDIR) | `co2_ppm`, `delta_30s`, `temp_c`, `nivel` | UART2: RX 16, TX 17, 9600 baudios | 5 s | `FALLO_SENSOR`, `CO2_PICO_RAPIDO`, `CO2_ALERTA_VENTILACION`, `CO2_CRITICO` | (4.5, 6.5) pared del fondo, a 1.5 m (zona de respiración) | RA-03 | S1 G1 | `nodo_co2.ino` (docente) |
| 2 | `audio` | INMP441 | `leq_db`, `lmax_db`, `pico_db`, `base_db`, `freq_dom_hz`, `tonal` | I²S: SCK 26, WS 25, SD 33, a 16 kHz | 1 s | `FALLO_AUDIO`, `RUIDO_IMPACTO`, `RUIDO_FUERTE_SOSTENIDO`, `RUIDO_MECANICO_CONSTANTE` | (6.0, 3.5) techo, centro-fondo | RA-07 | S8 G4 | `nodo_audio.ino` (docente) |
| 3 | `gas` | MQ-2 | `v_ao`, `rs_r0`, `do_alarma`, `calentando` | Analógica + digital | 5 s | `FALLO_SENSOR`, `GAS_DETECTADO` | (3.0, 3.5) techo, lejos del aire acondicionado | RA-05 | S8 G2 | `MQ-2.ino` (**grupo**; compila, sin probar en hardware) |
| 4 | `luz` | BH1750 (GY-302) | `lux`, `lux_min`, `lux_max`, `lux_mesa_est`, `luces_cambio` | I²C: SDA 21, SCL 22 | 10 s, y en el acto si cambian las luces | `FALLO_SENSOR`, `ILUMINACION_BAJA` | (4.5, 3.5) techo, centro | RA-04, RA-08 | S9 G3 | `nodo_luz.ino` (docente) |
| 5 | `termico` | MLX90640 32×24 | `entradas`, `salidas`, `ocupacion_est`, `personas_en_vista`, `cruces_dudosos`, `t_fondo`, `t_max` | I²C: SDA 21, SCL 22 | 5 s, y en el acto tras un cruce | `FALLO_SENSOR`, `CONTEO_CORREGIDO`, `OBJETO_ESTATICO` | (0.6, 0.5) marco superior de la puerta, a 2.3 m | RA-06, RA-04, RA-08, RA-09 | S9 G5 | `nodo_termico.ino` (docente) |
| 6 | `magnetico` | KY-024 (Hall lineal SS49E) | `puerta_abierta`, `aperturas`, `seg_abierta`, `campo_raw` | Analógica en GPIO 34 | 10 s, y en el acto ante un cambio | `FALLO_SENSOR`, `PUERTA_ABIERTA_PROLONGADA` | (0.2, 0.5) marco de la puerta, imán en la hoja | RA-09, RA-06, RA-08 | S9 G2 | `nodo_magnetico.ino` (docente) |
| 7 | `ambiente` | BME280 (GY-BME280) | `temp_c`, `hum_pct`, `pres_hpa` | I²C: SDA 21, SCL 22 | 10 s | `FALLO_SENSOR`, `TEMP_FUERA_CONFORT`, `HUMEDAD_ALTA`, `CAMBIO_RAPIDO_TEMP` | (5.0, 3.5) techo, centro | RA-01, RA-02 | S1 G5 | `nodo_ambiente.ino` (docente) |

Todos los nodos usan un ESP32 DevKit V1 y la misma cabecera de paquete (`version`, `tipo`,
`nodo_id`, `seq`, `uptime_ms`). El RA-10 (salud del sistema) usa los siete y el Gateway.

Notas de cada sensor, tomadas del código del docente:

- **MH-Z1911A:** calienta 3 min; válido de 300 a 10000 ppm; alerta en 1000 ppm y crítico en 1500,
  con histéresis de 100 y 3 confirmaciones.
- **INMP441:** dB SPL ≈ dBFS + 120 (sin calibrar); calibra en silencio los primeros 5 s. **No
  guarda audio.**
- **MQ-2:** necesita precalentamiento y calibrar R0 en aire limpio; `rs_r0` ≈ 1 en aire limpio y
  baja con gas o humo. Su calefactor consume unos 150 mA. El código del docente no trae este nodo:
  lo escribe el grupo con la estructura de `nodo_co2.ino`.
- **BH1750:** estima la luz sobre la mesa como `lux × 0.482`; iluminación baja bajo 300 lx.
- **MLX90640:** el conteo se hace en el ESP32 (sustrae el fondo, sigue las cabezas y detecta el
  cruce de las líneas A y B) y **no envía la matriz**. Se coordina con el KY-024 de la puerta.
- **KY-024:** salida invertida (< 1200 es cerrada, > 1800 es abierta); antirrebote de 150 ms;
  apertura prolongada a los 10 min.
- **BME280:** confort de 20 a 26 °C; humedad alta desde 70 %; cambio rápido si varía más de
  1.5 °C en 5 min.

## 3. Gateway y servidor

| Equipo | Qué es | Dónde va | Configuración |
|---|---|---|---|
| **Gateway** | ESP32 v4 con `gateway.ino` del docente. Wi-Fi STA, cola de 32 mensajes, MQTT QoS 0 sin credenciales, estado por LWT | (8.5, 0.5) en el plano supuesto; lo opera S1 G1 (procesador central) | `GRUPO`, `SSID_ROUTER` y la clave del Wi-Fi. `gateway.ino` trae credenciales: está en `.gitignore` y se versiona `gateway.ino.example` |
| **Laptop** | Docker con Mosquitto `:1883`, Telegraf, InfluxDB 2.7 `:8086` (org `utec`, bucket `gemelo`) y Grafana `:3000` del docente, más el servicio del grupo `:8000` | En la misma red que el Gateway. Hoy, la laptop de José | `deploy/.env` (no versionado) y `deploy/levantar.sh`; el `docker-compose.yml` del docente no se toca |
| **Red local** | Router del aula o red "UTEC Proyectos" | — | Pendiente: NTP local en la laptop para que el Gateway tenga hora sin internet |

## 4. Hardware comprado por el curso

Orden de compra **OC-UTEC-004033-26** (Naylamp), transcrita de la planilla del curso y de las
etiquetas fotografiadas en [curso/imagenes/](curso/imagenes/). El grupo no compró hardware. Las
cantidades son las de la OC; donde no hay foto, no se conocen.

| N° | Categoría | Sensor o modelo | Interfaz | Cantidad en la OC | Uso en la arquitectura |
|---|---|---|---|---|---|
| 1 | Ruido | INMP441 | I²S | 2 | Nodo 2 |
| 2 | CO₂ | MH-Z19B pedido; llegó **MH-Z1911A** (Winsen) | UART | 2 | Nodo 1 |
| 3 | Temperatura, humedad y presión | BME280 | I²C | 2 | Nodo 7 |
| 4 | Luz | BH1750 (GY-302) | I²C | 2 | Nodo 4 |
| 5 | Ocupación térmica | MLX90640 32×24 | I²C | sin foto | Nodo 5 |
| 6 | Procesamiento | ESP32 DevKit V1 (NodeMCU-32, 30 pines) | Wi-Fi + Bluetooth | 2 | Nodos |
| 7 | Humo | Detector Wi-Fi Tuya | Wi-Fi (nube) | 1 | **Reemplazado por el MQ-2** (anuncio del 21/10) |
| 8 | Hall | KY-024 (SS49E, lineal) | Analógica + digital | 4 | Nodo 6 |
| 9 | Energía | PZEM-004T v3.0 (100 A + TC) | UART (Modbus) | sin foto | **No está en la arquitectura oficial.** La planilla lo rotula "Ocupación del ambiente", que parece un error. Pregunta abierta al docente: ¿nodo 8? |
| — | Gas y humo | MQ-2 | Analógica + digital | — (no figura en la planilla) | Nodo 3 |
| — | Alimentación | 18650 de 1600 mAh y porta-batería | — | — (no figura en la planilla) | Una por caja |
| — | Montaje | Protoboard de 170 puntos | — | — (no figura en la planilla) | Una por caja |

Cada caja lleva ESP32 DevKit V1, el sensor, la protoboard, la 18650 y su porta-batería. La 18650
entrega de 3.0 a 4.2 V, así que hace falta un regulador (LDO de 3.3 V o elevador a 5 V con
TP4056), y el MH-Z1911A y el MQ-2 consumen demasiado para pasar el día a batería. El análisis por
nodo va en [06-energia-cajas.md](06-energia-cajas.md) (en elaboración).

## 5. Qué no se mide directamente

| Magnitud | Por qué | Cómo se resuelve |
|---|---|---|
| Energía eléctrica | Sin PZEM ni enchufes en la arquitectura oficial | **Estimación por proxy**: luces (BH1750), aula vacía (MLX90640), aire acondicionado por ruido mecánico (INMP441) y horario, por el inventario de potencias de `config/aula_l419.yaml`. Se presenta como estimación (RF-01, RF-10, RF-12) |
| Batería e intensidad de señal de cada nodo | No vienen en el paquete del docente | Una batería agotada se ve como nodo sin datos (RA-10) |
| Vibración de la puerta | El SW-420 salió con la arquitectura oficial | Retirada de RF-04 |

## 6. Histórico: propuesta original del grupo (reemplazada)

Lista de materiales v2 del 10/09/2026 (precios del 27/08/2026), que el grupo armó antes de que el
curso fijara la arquitectura. **No se compró**: la reemplaza el hardware del curso. El detalle por
ítem (tienda, enlace, SKU y precio) está en [data/instrumentacion-l419.csv](data/instrumentacion-l419.csv)
y en la versión anterior de este archivo en git.

| Módulo | S/ | Contenido | Reemplazo oficial |
|---|---|---|---|
| Procesadores | 888 | 5 ESP32 DevKit, ESP32-C3, Raspberry Pi 5 con microSD, case y batería RTC | ESP32 DevKit por nodo y laptop con Docker |
| Energía | 355 | PZEM-004T, 2 pinzas SCT-013 y 2 enchufes Tasmota | Estimación por proxy (PZEM sin integrar) |
| Ambiente | 286 | SCD41, 2 SHT31 y 2 BH1750 | MH-Z1911A, BME280 y BH1750 |
| Ocupación | 266 | 2 LD2410C, 3 PIR y 2 VL53L1X | MLX90640 con KY-024 |
| Puerta y seguridad | 36 | 2 magnéticos y SW-420 | KY-024 (sin vibración) |
| Copiloto de voz | 98 | INMP441, MAX98357A y parlante (el teléfono, sin costo) | INMP441 como sensor de ruido; copiloto en el teléfono |
| Integración | 879 | Router, fuentes, LiPo, cajas, conversores, multímetro, cinta VHB y termohigrómetro | Cajas del curso con 18650 |
| **Total** | **2808** | Versión mínima: **S/ 580** (sin Pi, con laptop) | — |
