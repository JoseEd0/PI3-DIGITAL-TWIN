# Prueba en el salón con el Gateway real (gateway_ap.ino)

Instructivo para conectar todo el sistema del grupo a los sensores instalados en el L-419. Desde el
17/11/2026 el Gateway del aula es `gateway_ap.ino` ([vendor/gateway_ap_l419/](../vendor/gateway_ap_l419/)):
crea su propia red Wi-Fi y sirve los datos por HTTP, sin MQTT. El puente del grupo
(`demo/servidor/gemelo/puente_gateway.py`) los lleva a Mosquitto con el formato oficial, y desde ahí
todo funciona igual: Telegraf, InfluxDB, Grafana, el servicio, el tablero y Gaphor en vivo. Detalle
técnico en [CONTRATO_DATOS.md §10](CONTRATO_DATOS.md).

```
nodos ──ESP-NOW──► Gateway (red GEMELO-L419, 192.168.4.1) ──HTTP──► laptop
laptop: puente ──MQTT──► Mosquitto ──► Telegraf ──► InfluxDB ──► Grafana :3000
                             └──► servicio :8000 ──► tablero y Gaphor en vivo
```

**Estado al 25/11/2026:** el puente se probó de punta a punta con el Gateway falso (datos
**simulados**): llegan los 7 nodos al servicio y los 7 tipos a InfluxDB, la hora se le da al Gateway
y una caída del Gateway se diagnostica como tal (RA-10). **Con el Gateway real está pendiente**: eso es
lo que se prueba en el salón.

## 1. Antes de salir (con internet)

1. Abrir Docker Desktop y comprobar que las imágenes del stack ya están descargadas. En el salón no
   hay internet para bajarlas:

   ```bash
   docker images | grep -E "mosquitto|telegraf|influxdb|grafana"
   ```

   Deben salir las cuatro. Si falta alguna, correr `deploy/levantar.sh` una vez con internet.
2. Ensayar todo con el Gateway falso (2 minutos):

   ```bash
   deploy/levantar.sh ensayo
   ```

   Abrir http://localhost:8000: deben aparecer los 7 nodos con datos y la franja "DATOS SIMULADOS".
   Cerrar con `Ctrl+C`. Si esto funciona, en el salón solo cambia la red.
3. Llevar el cable USB (por si hay que flashear el MQ-2) y la laptop cargada.

## 2. En el salón

1. **Conectar la laptop a la red `GEMELO-L419`.** La clave está en la guía del Gateway (punto 5 de
   `Guia_gateway_AP.docx`). macOS dirá "Sin conexión a Internet": es normal. Para que la Mac no se
   cambie sola a otra red, en Ajustes del Sistema → Wi-Fi, desactivar "Conectarse automáticamente"
   en las otras redes conocidas mientras dure la prueba.
2. **Comprobar el Gateway:**

   ```bash
   curl http://192.168.4.1/api/estado
   ```

   Debe devolver un JSON con `"modo":"AP"`. También se puede abrir http://192.168.4.1 en el
   navegador: es la página del Gateway, con el último dato de cada sensor. Si no responde, ver §4.
3. **Levantar todo:**

   ```bash
   deploy/levantar.sh salon
   ```

   Debe decir `Gateway encontrado en http://192.168.4.1`. El puente corre de fondo y su registro
   queda en `demo/servidor/logs/puente.log`. En otra terminal:

   ```bash
   tail -f demo/servidor/logs/puente.log
   ```

   Deben aparecer `Se le dio la hora de la laptop al Gateway` (si no la tenía) y
   `Gateway en línea en http://192.168.4.1`.
4. **Ver el sistema:**

   | Qué | Dónde |
   |---|---|
   | Tablero del grupo | http://localhost:8000. Ya **no** debe decir "DATOS SIMULADOS": la fuente es `l419`, real |
   | Grafana | http://localhost:3000/d/gemelo-l418-completo?var-grupo=l419 (usuario `admin`, clave en `deploy/.env`) |
   | Gaphor en vivo | `demo/gaphor-vivo/lanzar.sh` |
   | Página del Gateway (para comparar) | http://192.168.4.1 |

5. **Grabar la sesión** para analizarla después sin el hardware (RF-11). En otra terminal, mientras
   todo corre:

   ```bash
   cd demo/servidor && .venv/bin/python -m gemelo.grabacion grabar --grupo l419 --minutos 30 --salida grabaciones/salon-2026-11-25.jsonl
   ```

## 3. Qué comprobar y anotar

Cada resultado se anota con la hora y se rotula **real**. Una captura del tablero y de Grafana por
prueba sirve como evidencia para el reporte.

| Prueba | Qué hacer | Qué debe pasar | CP |
|---|---|---|---|
| Llegan los nodos | Mirar "Salud de nodos" en el tablero | Cada nodo instalado con datos recientes. Los que no están instalados aparecen caídos y RA-10 lo dice (esperado) | CP-15 |
| Puerta | Abrir y cerrar la puerta | `puerta_abierta` cambia y el log registra "Puerta abierta/cerrada" | CP-08 |
| Conteo | Entrar y salir de a uno, contando a mano | `entradas`, `salidas` y `ocupacion_est` del nodo térmico coinciden con lo contado | CP-02 |
| Luces | Apagar y encender las luces | `luces_cambio` vale −1 y luego 1; el log registra el cambio | CP-07 |
| CO₂ | Respirar cerca del MH-Z1911A (después de sus 3 min de calentamiento) | `co2_ppm` sube | CP-07 |
| Ambiente | Comparar `temp_c` y `hum_pct` con un termohigrómetro, si hay | Diferencia anotada | CP-07 |
| Gateway caído | Pedir que desenchufen el Gateway 30 s, o alejarse de su red | El puente avisa "Gateway desconectado" y RA-10 diagnostica el Gateway, no siete sensores; al volver, "Gateway en línea" | CP-03 |
| Datos en InfluxDB | Grafana con `var-grupo=l419` | Los paneles muestran las series del aula | CP-09 |

Además conviene anotar los datos del aula que hoy son supuestos (`config/aula_l419.yaml`): aforo,
dimensiones, luminarias, equipos y horario.

## 4. Problemas comunes

| Problema | Qué revisar |
|---|---|
| `curl` a `192.168.4.1` no responde | La laptop no está en `GEMELO-L419` (la Mac pudo volver a otra red) o el Gateway está apagado. También probar `http://gemelo-gateway.local` |
| El puente dice "Gateway en línea" pero el tablero no muestra nodos | Los nodos no le están enviando al Gateway. En http://192.168.4.1, `hace_s` de cada sensor debe ser pequeño. En el Monitor Serie de un nodo, el último número de cada línea debe ser 1 |
| `levantar.sh` falla en `docker compose` | Docker Desktop no está abierto |
| El puerto 8000 está ocupado | Quedó un servicio anterior: `lsof -ti tcp:8000 \| xargs kill -9` |
| Grafana no muestra datos | Cambiar el selector `grupo` a `l419` y la ventana de tiempo a "Last 15 minutes" |
| Hora rara en los datos | El puente le da la hora al Gateway al arrancar y cada vez que la pierde; revisar `puente.log` |

## 5. Flashear el nodo MQ-2 (si el docente lo permite)

El MQ-2 (nodo 3) es el programa propio del grupo y ya está configurado para este Gateway
(`firmware/MQ-2/`, compilado el 25/11). Con el ESP32 del nodo conectado por USB:

```bash
arduino-cli upload --fqbn esp32:esp32:esp32 -p /dev/cu.usbserial-XXXX firmware/MQ-2
arduino-cli monitor -p /dev/cu.usbserial-XXXX -c baudrate=115200
```

En el monitor, la última columna (`envio_ok`) debe valer 1, y el nodo aparece en el tablero como
nodo 3 (gas) tras su minuto de calentamiento. Si en este Mac el upload pide compilar de nuevo y
falla por `ctags`, ver `firmware/README.md`.

## 6. Al terminar

1. `Ctrl+C` en la terminal de `levantar.sh` (cierra también el puente) y en la de la grabación.
2. Apagar el stack:

   ```bash
   docker compose -p campustwin --env-file deploy/.env -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml -f deploy/docker-compose.override.yml down
   ```

3. Volver a la red de siempre.
4. Opcional: el Gateway guarda en su flash todo lo que recibió (~1,2 MB). Para pasar ese historial a
   InfluxDB, conectado otra vez a `GEMELO-L419` y con el stack arriba pero **sin** el servicio:

   ```bash
   cd demo/servidor && .venv/bin/python -m gemelo.puente_gateway --desde 0
   ```

   Se detiene con `Ctrl+C` cuando el log deja de mostrar mensajes nuevos.
5. Pasar las capturas, la grabación y las notas para actualizar los casos de prueba (CP-02, 03, 07,
   08, 15) a **real** en `docs/00-idea-principal.md`, `docs/pruebas/` y Asana.
