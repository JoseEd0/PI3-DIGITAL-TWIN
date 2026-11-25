<!-- Texto extraído de Guia_gateway_AP.docx (anuncio del docente del 17/11/2026; repositorio
     josecarita/Gemelo-digital-L419-Gateway, commit 67cccfe). La clave de la red Wi-Fi se omite:
     está en la guía original y en vendor/gateway_ap_l419/gateway_ap/gateway_ap.ino (ignorado por git). -->

# Guía: cómo usar el gateway y leer los datos de los sensores

## 1. Qué es esto

Cada sensor está conectado a una placa ESP32 (a esto le llamamos "nodo"). Los nodos envían sus mediciones por radio a otra placa ESP32 llamada "gateway".

El gateway guarda las mediciones y crea su propia red Wi-Fi llamada GEMELO-L419. Cuando una laptop se conecta a esa red, puede leer los datos de todos los sensores.

No se necesita internet, ni router, ni instalar programas especiales.

## 2. Archivos que se entregan

Para el gateway solo se necesitan estos dos archivos:

| Archivo | Para qué sirve |
|---|---|
| gateway_ap.ino | Es el programa del gateway. |
| paquetes.h | Define cómo viajan los datos. Debe ser exactamente el mismo archivo que usan los nodos de los sensores. |

Opcional: simulador_gateway.py. Sirve para probar la interfaz en una laptop sin tener las placas (ver punto 6).

## 3. Paso 1: subir el programa al gateway

1. Crear una carpeta llamada gateway_ap y poner dentro los dos archivos.

2. Abrir gateway_ap.ino con Arduino IDE.

3. Elegir la placa "ESP32 Dev Module" y el puerto USB donde está conectada.

4. Presionar "Subir" (la flecha).

5. Abrir el Monitor Serie (velocidad 115200). Aparecerá una línea como esta:

Listo. MAC STA (para los nodos)=58:2A:BD:72:03:DC

Anoten esa dirección (MAC). Los nodos la necesitan para saber a quién enviar los datos.

## 4. Paso 2: cambiar el nombre de la red en cada sensor

En el programa de cada sensor hay que cambiar una sola línea: el nombre de la red. Debe quedar así:

const char* SSID_ROUTER = "GEMELO-L419";

No se pone contraseña. Los sensores no se conectan a la red, solo la buscan para saber en qué canal está el gateway.

El nombre debe escribirse exactamente igual: mayúsculas y guion incluidos.

| Sensor | Archivo | Línea a cambiar |
|---|---|---|
| CO2 | nodo_co2.ino | const char* SSID_ROUTER = "GEMELO-L419"; |
| Audio (ruido) | nodo_audio.ino | const char* SSID_ROUTER = "GEMELO-L419"; |
| Luz | nodo_luz.ino | const char* SSID_ROUTER = "GEMELO-L419"; |
| Conteo de personas (térmico) | nodo_termico.ino | const char* SSID_ROUTER = "GEMELO-L419"; |
| Puerta (magnético) | nodo_magnetico.ino | const char* SSID_ROUTER = "GEMELO-L419"; |
| Temperatura y humedad (ambiente) | nodo_ambiente.ino | const char* SSID_ROUTER = "GEMELO-L419"; |

Además, revisar la línea MAC_GATEWAY. Debe tener la MAC que anotaron en el paso 1. Por ejemplo, si la MAC es 58:2A:BD:72:03:DC, la línea queda así:

uint8_t MAC_GATEWAY[6] = {0x58, 0x2A, 0xBD, 0x72, 0x03, 0xDC};

(Se pone "0x" delante de cada par de letras o números.)

Después de cambiar estas líneas, subir el programa a la placa de cada sensor.

Para comprobar: en el Monitor Serie del sensor, el último número de cada línea debe ser 1. Si es 0, el gateway no está recibiendo.

## 5. Paso 3: conectar la laptop al gateway

1. En la laptop, abrir la lista de redes Wi-Fi.

2. Conectarse a la red GEMELO-L419. La contraseña es: (ver la guía original)

## 3. Abrir el navegador y entrar a: http://192.168.4.1

Ahí se ve el último dato de cada sensor y se actualiza solo.

Importante: mientras la laptop esté conectada a GEMELO-L419 no tendrá internet. Es normal. Para volver a tener internet, conectarse de nuevo a la red de siempre.

## 6. Paso 4: leer los datos desde su propia interfaz

Su interfaz (página web, programa en Python, etc.) pide los datos a estas direcciones. La laptop debe estar conectada a la red GEMELO-L419.

| Dirección | Qué devuelve |
|---|---|
| http://192.168.4.1/api/ultimos | El último mensaje de cada sensor. Usar para mostrar el estado actual (pedirlo cada 2 segundos). |
| http://192.168.4.1/api/datos?desde=0 | Todos los mensajes guardados, uno por línea. Usar para gráficas o historial. Para pedir solo los nuevos, cambiar el 0 por el último "id" recibido. |
| http://192.168.4.1/api/hora?epoch_ms=HORA | Sirve para darle la hora al gateway (no tiene internet). Llamarlo una vez al abrir la interfaz, poniendo la hora actual de la laptop en milisegundos. |

Para probar la interfaz sin las placas: ejecutar en la laptop "python simulador_gateway.py" y usar http://localhost:8000 en lugar de http://192.168.4.1. Los mensajes son iguales.

## 7. El mensaje que van a recibir

Cada medición llega como un texto en formato JSON. Ejemplo de un mensaje del sensor de CO2:

{"id":15,"nodo":1,"mac":"24:6F:28:AB:12:01","seq":2,"ts":1794950267527,"gw_ms":10024,"uptime_ms":13024,"perdidos":0,"tipo":"co2","co2_ppm":845,"delta_30s":12,"temp_c":24,"calentando":0,"nivel":"NORMAL","anomalias":"NINGUNA","anom_bits":0}

Ejemplo de un mensaje del sensor de luz:

{"id":18,"nodo":4,"mac":"24:6F:28:AB:12:04","seq":1,"ts":1794950267527,"gw_ms":10024,"uptime_ms":13024,"perdidos":0,"tipo":"luz","lux":486.3,"lux_min":482.3,"lux_max":490.3,"lux_mesa_est":234.4,"luces_cambio":0,"anomalias":"ILUMINACION_BAJA","anom_bits":2}

En /api/ultimos cada sensor viene así (el mensaje completo va dentro de "msg"):

{"nodo":1,"tipo":"co2","hace_s":2,"anomalias":"NINGUNA","msg":{ ...mensaje completo... }}

"hace_s" son los segundos desde el último dato. Si pasa de 60, ese sensor probablemente está apagado o desconectado.

Datos que vienen en todos los mensajes

| Dato | Qué significa |
|---|---|
| id | Número del mensaje (1, 2, 3...). Sirve para pedir solo los nuevos. |
| nodo | Qué sensor es: 1 CO2, 2 audio, 3 gas, 4 luz, 5 conteo de personas, 6 puerta, 7 temperatura y humedad. |
| tipo | Lo mismo, en texto: co2, audio, gas, luz, termico, magnetico, ambiente. |
| ts | Fecha y hora en milisegundos (igual que Date.now() en JavaScript). Puede venir null si el gateway todavía no tiene hora. |
| anomalias | Problemas detectados (por ejemplo "CO2_CRITICO"). Si no hay ninguno dice "NINGUNA". |
| mac, seq, gw_ms, uptime_ms, perdidos, anom_bits | Datos técnicos. Se pueden ignorar en la interfaz. |

Datos de cada sensor

| tipo | Datos principales | Anomalías posibles |
|---|---|---|
| co2 | co2_ppm (CO2 en ppm), nivel (NORMAL, ALERTA, CRITICO, CALENTANDO), calentando (1 = el sensor aún se está calentando, los primeros 3 minutos) | CO2_PICO_RAPIDO, CO2_ALERTA_VENTILACION, CO2_CRITICO, FALLO_SENSOR |
| audio | leq_db (nivel de ruido en dB), lmax_db (ruido máximo), pico_db, base_db (ruido de fondo) | RUIDO_IMPACTO, RUIDO_FUERTE_SOSTENIDO, RUIDO_MECANICO_CONSTANTE, FALLO_AUDIO |
| gas | rs_r0 (1 = aire limpio; si baja, hay gas o humo), do_alarma (1 = alarma) | GAS_DETECTADO, FALLO_SENSOR |
| luz | lux (luz medida), lux_mesa_est (luz estimada sobre la mesa), luces_cambio (1 se encendieron, -1 se apagaron, 0 sin cambio) | ILUMINACION_BAJA, FALLO_SENSOR |
| termico | ocupacion_est (personas dentro del aula), entradas y salidas (desde el mensaje anterior) | CONTEO_CORREGIDO, OBJETO_ESTATICO, FALLO_SENSOR |
| magnetico | puerta_abierta (1 abierta, 0 cerrada), aperturas (veces que se abrió), seg_abierta (segundos abierta) | PUERTA_ABIERTA_PROLONGADA, FALLO_SENSOR |
| ambiente | temp_c (temperatura en °C), hum_pct (humedad en %), pres_hpa (presión en hPa) | TEMP_FUERA_CONFORT, HUMEDAD_ALTA, CAMBIO_RAPIDO_TEMP, FALLO_SENSOR |

Si un sensor falla, sus valores pueden venir como null.

Ejemplo mínimo para leer los datos (JavaScript)

fetch("http://192.168.4.1/api/hora?epoch_ms=" + Date.now());

setInterval(async () => {

const sensores = await (await fetch("http://192.168.4.1/api/ultimos")).json();

for (const s of sensores) {

if (s.tipo === "co2") console.log("CO2:", s.msg.co2_ppm, "ppm");

if (s.tipo === "ambiente") console.log("Temperatura:", s.msg.temp_c, "°C");

}

}, 2000);

## 8. Problemas comunes

| Problema | Solución |
|---|---|
| No aparece la red GEMELO-L419 | Revisar que el gateway esté encendido y con el programa gateway_ap.ino cargado. |
| La página http://192.168.4.1 no abre | Revisar que la laptop esté conectada a GEMELO-L419 y escribir http:// (no https://). |
| Un sensor no aparece | Revisar en ese sensor el nombre de la red (SSID_ROUTER) y la MAC del gateway (MAC_GATEWAY). En su Monitor Serie el último número debe ser 1. |
| La interfaz no carga gráficos o librerías | La red del gateway no tiene internet. Las librerías de la interfaz deben estar descargadas en la laptop. |
| "ts" viene null | Llamar a /api/hora al abrir la interfaz (ver punto 6). |

## 9. Créditos

El formato de los datos (paquetes.h) y el programa base del gateway provienen del código de otro grupo del curso PI3. El gateway con red propia (gateway_ap.ino) fue adaptado por el grupo del Gemelo Digital L419.
