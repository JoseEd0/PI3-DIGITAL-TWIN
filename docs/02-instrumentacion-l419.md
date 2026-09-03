# Instrumentación de un espacio de enseñanza — Aula laboratorio L-419

> Fuente: `Instrumentacion_L419 (1).xlsx`, hoja `Instrumentacion L-419`.
> Datos crudos en [data/instrumentacion-l419.csv](data/instrumentacion-l419.csv).
> Lista de materiales por módulo · Moneda: Soles (S/) · Precios consultados el **27/08/2026**.

## 1. Cómo funciona

**Cadena de datos:** Sensores → ESP32 → Wi-Fi/BLE → Raspberry Pi (servidor) → Red → PC con dashboard

| Aspecto | Descripción |
|---|---|
| Transporte | Cada sensor se conecta a un ESP32 que envía los datos por Wi-Fi o Bluetooth. Los comandos viajan en sentido contrario por la misma vía. |
| Servidor | Todos los datos llegan a una Raspberry Pi que actúa como servidor, y desde ahí el dashboard se ve en cualquier computadora de la red. |
| Instalación | Ningún sensor usa cable de datos hacia la computadora. La instalación no requiere perforar paredes ni intervenir el tablero eléctrico. |

## 2. Lista de materiales

Convenciones de la hoja original:

- **Enlace** — *Ficha del producto* abre la página exacta del artículo; *Ver en la categoría*
  abre el listado de la tienda donde se encuentra.
- **Precio** — *Verificado 27/08/26* = precio consultado ese día en la tienda;
  *Por cotizar* = aún sin confirmar.

### Procesadores

| N° | Elemento | Especificaciones | Tienda | Enlace | SKU | Cant. | S/ c/u | Total S/ | Estado precio |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ESP32 DevKit V1 | 240 MHz, 520 KB RAM, 4 MB flash, 3.3 V. Wi-Fi + Bluetooth BLE | Naylamp Mechatronics | [Ficha](https://naylampmechatronics.com/espressif-esp/384-esp32-devkit-v1-nodemcu-32-30-pin-esp32-wifi-micro-usb.html) | 000384 | 4 | 35 | 140 | Verificado 27/08/26 |
| 2 | ESP32-C3 SuperMini | 160 MHz, muy bajo consumo, ideal con batería. Wi-Fi + BLE 5.0 | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/84-espressif-esp) | — | 1 | 28 | 28 | Por cotizar |
| 3 | Raspberry Pi 5 (4 GB) | Servidor local: guarda datos y corre el dashboard. Wi-Fi + BLE + Ethernet | Naylamp Mechatronics | [Ficha](https://naylampmechatronics.com/raspberry-pi/1255-raspberry-pi-5-4gb.html) | 001255 | 1 | 550 | 550 | Por cotizar |
| 4 | microSD 64 GB Clase 10 | Almacenamiento del servidor | Retail local | [Categoría](https://naylampmechatronics.com/21-accesorios-raspberry) | — | 1 | 45 | 45 | Por cotizar |
| 5 | Case con ventilador para Pi 5 | Evita sobrecalentamiento | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/21-accesorios-raspberry) | 001325 | 1 | 70 | 70 | Verificado 27/08/26 |
| | **Subtotal Procesadores** | | | | | **8** | | **833** | |

> Se eligió el ESP32 porque trae Wi-Fi y Bluetooth incluidos, sin necesidad de módulos extra.

### Energía

| N° | Elemento | Especificaciones | Tienda | Enlace | SKU | Cant. | S/ c/u | Total S/ | Estado precio |
|---|---|---|---|---|---|---|---|---|---|
| 6 | PZEM-004T v3.0 con pinza 100 A | Mide voltaje, corriente, potencia y energía. 80-260 V, precisión ±0.5 % | Grupo Electrostore | [Ficha](https://grupoelectrostore.com/shop/sensores/corriente/modulo-sensor-de-corriente-ac-pzem-004t/) | — | 1 | 85 | 85 | Por cotizar |
| 7 | Pinza no invasiva SCT-013 | Transformador de corriente no invasivo, se abraza al cable sin cortarlo | Grupo Electrostore | [Ficha](https://grupoelectrostore.com/shop/sensores/corriente/sensor-de-corriente-no-invasivo-50a-sct-013-050-1v/) | — | 2 | 40 | 80 | Por cotizar |
| 8 | Enchufe inteligente con medición | Mide equipos individuales (proyector, PC). 220 V / 16 A, Wi-Fi | Mercado Libre Perú | [Categoría](https://listado.mercadolibre.com.pe/enchufe-medidor-de-consumo) | — | 2 | 70 | 140 | Por cotizar |
| | **Subtotal Energía** | | | | | **5** | | **305** | |

> El PZEM da la mejor medición, pero necesita acceso al tablero. Si no lo autorizan, los
> enchufes inteligentes sirven como reemplazo y no requieren permiso.

### Ambiente

| N° | Elemento | Especificaciones | Tienda | Enlace | SKU | Cant. | S/ c/u | Total S/ | Estado precio |
|---|---|---|---|---|---|---|---|---|---|
| 9 | Sensor de CO₂ SCD41 | 400-5000 ppm. También mide temperatura y humedad | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/36-sensores-gas) | — | 1 | 190 | 190 | Por cotizar |
| 10 | Sensor SHT31 | Temperatura ±0.3 °C, humedad ±2 % | Naylamp Mechatronics | [Ficha](https://naylampmechatronics.com/sensores-temperatura-y-humedad/363-sensor-de-temperatura-y-humedad-relativa-sht31.html) | 000363 | 2 | 30 | 60 | Verificado 27/08/26 |
| 11 | Sensor de luz BH1750 | 1-65535 lux. Detecta luces encendidas sin gente | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/39-sensores-luz-y-sonido) | — | 2 | 18 | 36 | Por cotizar |
| | **Subtotal Ambiente** | | | | | **5** | | **286** | |

> El CO₂ sube cuando entran personas, así que sirve para confirmar la ocupación medida por el radar.

### Ocupación

| N° | Elemento | Especificaciones | Tienda | Enlace | SKU | Cant. | S/ c/u | Total S/ | Estado precio |
|---|---|---|---|---|---|---|---|---|---|
| 12 | Radar de presencia HLK-LD2410C | 24 GHz, alcance 6 m, ángulo 60°. Bluetooth integrado | Naylamp Mechatronics | [Ficha](https://naylampmechatronics.com/sensores-proximidad/1080-sensor-de-presencia-radar-hlk-ld2410c.html) | 001080 | 2 | 55 | 110 | Por cotizar |
| 13 | Sensor de movimiento PIR HC-SR501 | Alcance 3-7 m, ángulo 120° | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/38-sensores-proximidad) | — | 3 | 12 | 36 | Por cotizar |
| 14 | Sensor de distancia VL53L1X | Láser, 4 m. En la puerta cuenta entradas y salidas | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/228-tof-time-of-flight) | — | 2 | 60 | 120 | Por cotizar |
| | **Subtotal Ocupación** | | | | | **7** | | **266** | |

> El radar detecta a personas sentadas y quietas, que es donde falla el PIR. No usa cámara,
> así que no hay problema de datos personales.

### Puerta y seguridad

| N° | Elemento | Especificaciones | Tienda | Enlace | SKU | Cant. | S/ c/u | Total S/ | Estado precio |
|---|---|---|---|---|---|---|---|---|---|
| 15 | Sensor magnético de puerta | Detecta apertura. Montaje adhesivo | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/48-sensores-varios) | — | 2 | 12 | 24 | Por cotizar |
| 16 | Sensor de vibración SW-420 | Detecta golpes o apertura forzada | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/48-sensores-varios) | — | 1 | 12 | 12 | Por cotizar |
| | **Subtotal Puerta y seguridad** | | | | | **3** | | **36** | |

> Funciona con batería y solo despierta cuando la puerta se mueve, así que dura meses sin recarga.

### Copiloto de voz

| N° | Elemento | Especificaciones | Tienda | Enlace | SKU | Cant. | S/ c/u | Total S/ | Estado precio |
|---|---|---|---|---|---|---|---|---|---|
| 17 | Micrófono INMP441 | Micrófono digital, salida I2S | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/39-sensores-luz-y-sonido) | — | 1 | 38 | 38 | Por cotizar |
| 18 | Amplificador MAX98357A | 3.2 W, entrada digital | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/39-sensores-luz-y-sonido) | — | 1 | 42 | 42 | Por cotizar |
| 19 | Parlante 4 Ω / 3 W | Salida de audio | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/39-sensores-luz-y-sonido) | — | 1 | 18 | 18 | Por cotizar |
| 20 | Audífono Bluetooth con micrófono | Para el vigilante durante la ronda | Mercado Libre Perú | [Categoría](https://listado.mercadolibre.com.pe/audifonos-bluetooth-con-microfono) | — | 1 | 90 | 90 | Por cotizar |
| | **Subtotal Copiloto de voz** | | | | | **4** | | **188** | |

> Este es el componente de Interacción Humano-Computador del proyecto.

### Integración

| N° | Elemento | Especificaciones | Tienda | Enlace | SKU | Cant. | S/ c/u | Total S/ | Estado precio |
|---|---|---|---|---|---|---|---|---|---|
| 21 | Router Wi-Fi TP-Link TL-WR840N | Red propia, si la red UTEC bloquea los dispositivos | Mercado Libre Perú | [Ficha](https://www.mercadolibre.com.pe/tp-link-tl-wr840n-router-wifi-n-24ghz-300mbps-4-puertos-10100-color-blanco/p/MPE15314118) | — | 1 | 110 | 110 | Por cotizar |
| 22 | Fuente 5 V / 3 A USB-C | Alimenta los nodos fijos | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/145-fuentes-usb) | — | 4 | 30 | 120 | Por cotizar |
| 23 | Fuente oficial Raspberry Pi 5 (27 W) | La Pi 5 necesita esta fuente específica | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/21-accesorios-raspberry) | — | 1 | 95 | 95 | Por cotizar |
| 24 | Batería LiPo 2000 mAh + cargador TP4056 | Nodos sin tomacorriente cerca | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/100-li-po) | — | 2 | 45 | 90 | Por cotizar |
| 25 | Caja plástica ABS con tapa | Protege y monta cada nodo | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/229-cajas) | — | 5 | 25 | 125 | Por cotizar |
| 26 | Conversor de nivel 3.3 V ↔ 5 V | Conecta sensores de 5 V al ESP32 | Naylamp Mechatronics | [Ficha](https://naylampmechatronics.com/conversores-ttl/67-conversor-de-nivel-logico-4ch-5v3v.html) | 000067 | 3 | 8 | 24 | Verificado 27/08/26 |
| 27 | Adaptador USB-TTL CP2102 | Cargar y depurar el programa | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/45-conversores-ttl) | — | 2 | 25 | 50 | Por cotizar |
| 28 | Kit de cables, protoboard y estaño | Armado y conexiones | Naylamp Mechatronics | [Categoría](https://naylampmechatronics.com/97-protoboard) | — | 1 | 80 | 80 | Por cotizar |
| 29 | Multímetro digital | Verificar voltajes en la instalación | Retail local | [Categoría](https://naylampmechatronics.com/112-multimetros) | — | 1 | 70 | 70 | Por cotizar |
| 30 | Cinta 3M VHB y bridas | Montaje sin perforar paredes | Mercado Libre / ferretería | [Categoría](https://listado.mercadolibre.com.pe/cinta-doble-contacto-3m-vhb) | — | 1 | 35 | 35 | Por cotizar |
| | **Subtotal Integración** | | | | | **21** | | **799** | |

> El ESP32 DevKit ya trae el chip CP2102 integrado, así que el adaptador USB-TTL puede ser prescindible.

### **TOTAL GENERAL DEL PROYECTO: S/ 2713**

## 3. Resumen de costos por módulo

| Módulo | Total (S/) | % del proyecto |
|---|---|---|
| Procesadores | 833 | 30.70 % |
| Energía | 305 | 11.24 % |
| Ambiente | 286 | 10.54 % |
| Ocupación | 266 | 9.80 % |
| Puerta y seguridad | 36 | 1.33 % |
| Copiloto de voz | 188 | 6.93 % |
| Integración | 799 | 29.45 % |
| **TOTAL** | **2713** | **100 %** |

## 4. Versión mínima

Si el presupuesto es limitado, esta versión mantiene la demo completa. Se reemplaza la
Raspberry Pi por una laptop del equipo.

| Elemento | Cant. | S/ c/u | Total (S/) |
|---|---|---|---|
| ESP32 DevKit V1 | 2 | 35 | 70 |
| Enchufe inteligente | 1 | 70 | 70 |
| Sensor SHT31 | 1 | 30 | 30 |
| Sensor de luz BH1750 | 1 | 18 | 18 |
| Radar LD2410C | 1 | 55 | 55 |
| Sensor de puerta | 1 | 12 | 12 |
| Micrófono + amplificador + parlante | 1 | 98 | 98 |
| Fuentes, cajas y cables | 1 | 190 | 190 |
| Router Wi-Fi | 1 | 110 | 110 |
| **TOTAL VERSIÓN MÍNIMA** | | | **653** |

> La desventaja es que no se pueden tomar datos de noche ni durante días seguidos.
