# Instrumentación para gemelo digital de ambiente — PI3 — Compra.xlsx

> Transcrito de `docs/curso/originales/Instrumentacion para gemelo digital de ambiente - PI3 - Compra.xlsx`
> (una sola hoja, sin cantidades ni precios) el 10/11/2026. Las cantidades salen de las etiquetas de la
> orden de compra **OC-UTEC-004033-26** (Naylamp) fotografiadas en `docs/curso/imagenes/`.

| N° | Categoría | Sensor / modelo | Propósito (según la planilla) | Proveedor | Conectividad | Evento | Cantidad en la OC |
|---|---|---|---|---|---|---|---|
| 1 | Ruido | INMP441 | Actividad acústica del aula; relacionar ruido con horario, ocupación y eventos | SAI SAC – Paruro | ESP32 con I²S | Ruido elevado / actividad acústica | 2 |
| 2 | Calidad de aire / CO₂ | MH-Z19B (llegó **MH-Z1911A**, Winsen) | CO₂ por NDIR, ventilación | MTLab Perú (llegó de Naylamp) | ESP32 con UART/PWM | CO₂ elevado / ventilación insuficiente | 2 |
| 3 | Termodinámica | BME280 | Temperatura, humedad y presión | Naylamp | ESP32 con I²C/SPI | Fuera de rango | 2 |
| 4 | Lumínico | BH1750 (GY-302) | Iluminancia; uso innecesario de luminarias | Naylamp | ESP32 con I²C | Iluminación insuficiente / excesiva / luz sin ocupación | 2 |
| 5 | Ocupación / mapeo térmico | MLX90640 32×24 | Matriz térmica de 768 puntos sin imágenes convencionales | Mouser Perú | ESP32 con I²C | Presencia / cambio de ocupación | sin foto |
| 6 | Procesamiento / IoT | ESP32 DevKit V1 (NodeMCU-32, 30 pines, micro-USB) | Adquisición y envío al procesador central | Naylamp | Wi-Fi + Bluetooth | Pérdida o recuperación de conexión | 2 |
| 7 | Humo | Detector de humo Wi-Fi Tuya (ID 4365) | — | — | Wi-Fi (nube Tuya) | — | 1 · **reemplazado por MQ-2** (anuncio del 21/10) |
| 8 | Hall | Módulo KY-024 (SS49E, lineal) | Detectar si la puerta está cerrada | Naylamp | Analógica + digital | — | 4 |
| 9 | Energía | PZEM-004T v3.0 (100 A + TC) | La planilla dice "Ocupación del ambiente" (parece un error: mide energía) | — | UART (Modbus) | — | sin foto · **no está en la arquitectura oficial** |

No figuran en la planilla, pero sí en la arquitectura del docente o en los anuncios: **MQ-2** (gas/humo,
nodo 3), **18650 de 1600 mAh**, **porta-batería** y **protoboard de 170 puntos**.
