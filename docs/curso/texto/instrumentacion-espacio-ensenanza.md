# Instrumentación de un Espacio de Enseñanza (aula laboratorio).pdf

> Texto extraído automáticamente de `docs/curso/originales/Instrumentación de un Espacio de Enseñanza (aula laboratorio).pdf` (no versionado) el 10/11/2026.
> Entregable del grupo del 27/08 (arquitectura y BOM originales, con Raspberry Pi y sensores propios). Histórico. Para figuras y tablas, abrir el original.

Cómo funciona
Cada sensor se conecta a un microcontrolador ESP32, que envía los datos por Wi-Fi o
Bluetooth. Todos los datos llegan a una Raspberry Pi que actúa como servidor, y desde ahí
el dashboard se ve en cualquier computadora de la red. Los comandos viajan en sentido
contrario por la misma vía.

Sensores → ESP32 → Wi-Fi/BLE → Raspberry Pi (servidor) → Red → PC con dashboard

Ningún sensor usa cable de datos hacia la computadora. La instalación no requiere perforar
paredes ni intervenir el tablero eléctrico.

1. Procesadores
 Elemento Especificaciones Comunicación Dónde Cant S/ Total
 comprar . c/u

 ESP32 240 MHz, 520 KB Wi-Fi + Naylamp 4 40 160
 DevKit V1 RAM, 4 MB flash, 3.3 Bluetooth BLE Mechatronics
 V

 ESP32-C3 160 MHz, muy bajo Wi-Fi + BLE Naylamp 1 28 28
 SuperMini consumo, ideal con 5.0
 batería

 Raspberry Servidor local: Wi-Fi + BLE + Naylamp 1 55 550
 Pi 5 (4 GB) guarda datos y corre Ethernet 0
 el dashboard

 microSD Almacenamiento del — Retail local 1 45 45
 64 GB servidor
 Clase 10

 Case con Evita — Naylamp 1 90 90
 ventilador sobrecalentamiento
 para Pi 5

Se eligió el ESP32 porque trae Wi-Fi y Bluetooth incluidos, sin necesidad de módulos extra.
2. Sensores
Consumo de energía
 Elemento Especificaciones Dónde comprar Cant. S/ Total
 c/
 u

 PZEM-004T v3.0 Mide voltaje, corriente, Naylamp, Grupo 1 85 85
 con pinza 100 A potencia y energía. 80-260 V, Electrostore
 precisión ±0.5 %

 Pinza no invasiva 30 A, se abraza al cable sin Naylamp 2 40 80
 SCT-013-030 cortarlo

 Enchufe Mide equipos individuales Mercado Libre 2 70 140
 inteligente con (proyector, PC). 220 V / 16 A, Perú
 medición Wi-Fi

El PZEM da la mejor medición, pero necesita acceso al tablero. Si no lo autorizan, los
enchufes inteligentes sirven como reemplazo y no requieren permiso.

Ambiente
 Elemento Especificaciones Dónde Cant. S/ Total
 comprar c/u

 Sensor de CO₂ 400-5000 ppm. También mide Naylamp 1 190 190
 SCD41 temperatura y humedad

 Sensor SHT31 Temperatura ±0.3 °C, humedad ±2 Naylamp 2 48 96
 %

 Sensor de luz 1-65535 lux. Detecta luces Naylamp 2 18 36
 BH1750 encendidas sin gente

El CO₂ sube cuando entran personas, así que sirve para confirmar la ocupación medida por
el radar.

Ocupación
 Elemento Especificaciones Dónde Cant. S/ Total
 comprar c/u
 Radar de presencia 24 GHz, alcance 6 m, ángulo Naylamp 2 55 110
 HLK-LD2410C 60°. Bluetooth integrado

 Sensor de Alcance 3-7 m, ángulo 120° Naylamp 3 12 36
 movimiento PIR
 HC-SR501

 Sensor de distancia Láser, 4 m. En la puerta Naylamp 2 60 120
 VL53L1X cuenta entradas y salidas

El radar detecta a personas sentadas y quietas, que es donde falla el PIR. No usa cámara,
así que no hay problema de datos personales.

Puerta y seguridad
 Elemento Especificaciones Dónde Cant. S/ Total
 comprar c/u

 Sensor magnético Detecta apertura. Montaje Naylamp 2 12 24
 de puerta adhesivo

 Sensor de vibración Detecta golpes o apertura Naylamp 1 12 12
 SW-420 forzada

Funciona con batería y solo despierta cuando la puerta se mueve, así que dura meses sin
recarga.

Copiloto de voz
 Elemento Especificaciones Dónde Cant. S/ Total
 comprar c/u

 Micrófono INMP441 Micrófono digital, salida Naylamp 1 38 38
 I2S

 Amplificador 3.2 W, entrada digital Naylamp 1 42 42
 MAX98357A

 Parlante 4 Ω / 3 W Salida de audio Naylamp 1 18 18

 Audífono Bluetooth con Para el vigilante durante Retail local 1 90 90
 micrófono la ronda

Este es el componente de Interacción Humano-Computador del proyecto.
3. Elementos de integración
 Elemento Para qué sirve Dónde Cant. S/ Total
 comprar c/u

Router Wi-Fi TP-Link Red propia, si la red UTEC Retail local 1 110 110
TL-WR840N bloquea los dispositivos

Fuente 5 V / 3 A Alimenta los nodos fijos Naylamp 4 30 120
USB-C

Fuente oficial La Pi 5 necesita esta fuente Naylamp 1 95 95
Raspberry Pi 5 (27 W) específica

Batería LiPo 2000 Nodos sin tomacorriente Naylamp 2 45 90
mAh + cargador cerca
TP4056

Caja plástica ABS con Protege y monta cada nodo Naylamp 5 25 125
tapa

Convertidor de nivel Conecta sensores de 5 V al Naylamp 3 12 36
3.3 V ↔ 5 V ESP32

Adaptador USB-TTL Cargar y depurar el Naylamp 2 25 50
CP2102 programa

Kit de cables, Armado y conexiones Naylamp 1 80 80
protoboard y estaño

Multímetro digital Verificar voltajes en la Retail local 1 70 70
 instalación

Cinta 3M VHB y bridas Montaje sin perforar Ferretería 1 35 35
 paredes local

4. Software (gratuito)
 Programa Para qué sirve Dónde corre

Arduino IDE / ESPHome Programar los ESP32 PC del equipo

Mosquitto Recibe los datos de todos los sensores Raspberry Pi

Node-RED Reglas y alertas Raspberry Pi
 InfluxDB Guarda el historial Raspberry Pi

 Grafana Dashboard del administrador Raspberry Pi

 Vosk Reconocimiento de voz del copiloto Raspberry Pi

Todo es de código abierto y corre dentro del campus. Ningún dato del aula sale a internet.

5. Costos
 Bloque Total (S/)

 Procesadores 873

 Energía 305

 Ambiente 322

 Ocupación 266

 Puerta y seguridad 36

 Copiloto de voz 188

 Integración 811

 Total 2 801

Versión mínima (S/ ~680)

Si el presupuesto es limitado, esta versión mantiene la demo completa:

 Elemento Cant. S/

 ESP32 DevKit V1 2 80

 Enchufe inteligente 1 70

 SHT31 1 48

 BH1750 1 18

 Radar LD2410C 1 55

 Sensor de puerta 1 12
 Micrófono + amplificador + parlante 1 98

 Fuentes, cajas y cables — 190

 Router Wi-Fi 1 110

 Total 681

Se reemplaza la Raspberry Pi por una laptop del equipo. La desventaja es que no se
pueden tomar datos de noche ni durante días seguidos.

6. Puntos por confirmar
 Pregunta Qué pasa si la respuesta es no

 ¿Autorizan instalar sensores en L-419? El proyecto no puede avanzar

 ¿Dan acceso al tablero eléctrico? Se usan enchufes inteligentes

 ¿La red UTEC acepta dispositivos IoT? Se usa el router propio

 ¿Hay tomacorrientes cerca? Se usan nodos con batería

 ¿Ya hay sensores instalados? Se reduce la compra

 ●​ Los precios son referenciales. Conviene pedir cotización formal a Naylamp
 Mechatronics, que emite comprobante para pedidos institucionales.
