# Prueba en el salón con el Gateway real (paso a paso, desde cero)

Este instructivo sirve para que **cualquier integrante**, en **su propia laptop**, conecte todo el
sistema del grupo a los sensores instalados en el L-419 y lo pruebe. Se sigue en orden: la
parte 1 se hace **en casa, con internet**; la parte 2, **en el salón**, sin internet.

## Qué hay en el aula y cómo se conecta

Desde el 17/11/2026 el Gateway del aula es `gateway_ap.ino` (de otro grupo del curso,
[vendor/gateway_ap_l419/](../vendor/gateway_ap_l419/)). **No usa MQTT:** crea su propia red Wi-Fi,
`GEMELO-L419`, y sirve los datos por HTTP en `192.168.4.1`. El **puente** del grupo
(`demo/servidor/gemelo/puente_gateway.py`) pide esos datos y los publica en el Mosquitto de la
laptop con el formato oficial. Desde ahí todo funciona igual: Telegraf, InfluxDB, Grafana, el
servicio del grupo, el tablero y Gaphor en vivo. Detalle técnico en
[CONTRATO_DATOS.md §10](CONTRATO_DATOS.md).

```
nodos ──ESP-NOW──► Gateway (red GEMELO-L419, 192.168.4.1) ──HTTP──► laptop
laptop: puente ──MQTT──► Mosquitto ──► Telegraf ──► InfluxDB ──► Grafana :3000
                             └──► servicio :8000 ──► tablero y Gaphor en vivo
```

**Estado al 25/11/2026:** probado de punta a punta con el Gateway falso, en la laptop de José y en un
clon nuevo del repositorio con un `.env` nuevo (datos **simulados**). Llegan los 7 nodos al servicio
y los 7 tipos a InfluxDB. El puente le da la hora al Gateway, y una caída del Gateway se diagnostica
como tal (RA-10). **Con el Gateway real está pendiente:** eso es lo que se prueba en el salón.

---

## Parte 1. En casa, con internet (unos 20 minutos)

### 1.1 Programas que hacen falta

| Programa | Versión | Para qué | Cómo comprobarlo |
|---|---|---|---|
| Git | cualquiera | Bajar el repositorio | `git --version` |
| Python | 3.11 o más (se probó 3.12) | Servicio, puente y simulador | `python3 --version` |
| Node.js | 20 o más (se probó 24) | Construir el tablero | `node --version` |
| Docker Desktop | reciente, **abierto** | Mosquitto, Telegraf, InfluxDB y Grafana | `docker --version` |
| Gaphor | 3.x (opcional) | Gaphor en vivo | Abrir la app |
| Arduino IDE o `arduino-cli` con el núcleo `esp32` (opcional) | — | Solo si se va a flashear el nodo MQ-2 | — |

Los comandos de este instructivo son para **macOS o Linux**, en la terminal. En **Windows** se usa
Git Bash o WSL para `levantar.sh`, o se arranca todo a mano como dice la §2.6. Ahí la ruta de Python
del entorno es `demo\servidor\.venv\Scripts\python` en vez de `demo/servidor/.venv/bin/python`.

### 1.2 Bajar el repositorio

El repositorio es **privado**: José tiene que haberte agregado como colaborador en GitHub.

```bash
git clone https://github.com/JoseEd0/PI3-DIGITAL-TWIN.git
```

```bash
cd PI3-DIGITAL-TWIN
```

Todos los comandos que siguen se corren **desde esta carpeta** (la raíz del repositorio).

### 1.3 Crear las claves locales (`deploy/.env`)

Son las claves de **tu** InfluxDB y **tu** Grafana. No se suben a git y no son las del docente. Este
comando crea el archivo con valores al azar:

```bash
printf 'INFLUX_PASSWORD=%s\nINFLUX_TOKEN=%s\nGRAFANA_PASSWORD=%s\n' "$(openssl rand -hex 12)" "$(openssl rand -hex 32)" "$(openssl rand -hex 8)" > deploy/.env
```

Si no tienes `openssl`, copia `deploy/.env.example` a `deploy/.env` y escribe tres valores
inventados, de **8 caracteres o más** (InfluxDB rechaza claves más cortas). Tu clave de Grafana
es la línea `GRAFANA_PASSWORD` de ese archivo.

### 1.4 Instalar el servicio (Python)

```bash
python3 -m venv demo/servidor/.venv
```

```bash
demo/servidor/.venv/bin/pip install -r demo/servidor/requirements.txt
```

Comprobación (deben pasar todas, 121 al 25/11):

```bash
cd demo/servidor && .venv/bin/python -m pytest -q && cd ../..
```

### 1.5 Construir el tablero (Node)

```bash
cd demo/tablero && npm ci && npm run build && cd ../..
```

Debe terminar con `✓ built in …` y dejar `demo/tablero/dist/index.html`.

### 1.6 Bajar las imágenes de Docker

En el salón no hay internet, así que las imágenes se bajan ahora. Con Docker Desktop **abierto**:

```bash
docker compose -p campustwin --env-file deploy/.env -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml -f deploy/docker-compose.override.yml pull
```

Comprobación (deben salir `eclipse-mosquitto:2`, `influxdb:2.7`, `telegraf:1.32` y `grafana/grafana:11.3.0`):

```bash
docker images
```

### 1.7 Ensayo general con el Gateway falso

El Gateway falso imita la API del Gateway del aula con datos del simulador. Si esto funciona, en el
salón solo cambia la red.

```bash
deploy/levantar.sh ensayo
```

Espera a que salga `Uvicorn running on http://0.0.0.0:8000` y abre http://localhost:8000. En 30 s
deben aparecer los 7 nodos con datos y la franja **DATOS SIMULADOS**. Grafana:
http://localhost:3000/d/gemelo-l418-completo?var-grupo=sim, con usuario `admin` y la clave de §1.3.

Cierra con `Ctrl+C`, que detiene también el puente y el Gateway falso.

### 1.8 Para llevar

- La laptop cargada y su cargador.
- La **clave de la red `GEMELO-L419`**, que está en la guía del Gateway (punto 5 de
  `Guia_gateway_AP.docx`, en el anuncio del docente del 17/11). No está en el repositorio.
- Un cable micro-USB, solo si se va a flashear el MQ-2 (§2.5).

---

## Parte 2. En el salón (sin internet)

### 2.1 Conectarse a la red del Gateway

1. Abrir Docker Desktop.
2. Conectar el Wi-Fi a **`GEMELO-L419`** con la clave de la guía. El sistema dirá "Sin conexión a
   Internet": es normal.
3. Para que la laptop no se cambie sola a otra red: en macOS, Ajustes del Sistema → Wi-Fi → en las
   otras redes conocidas, desactivar "Conectarse automáticamente" mientras dure la prueba.
4. Comprobar que el Gateway responde:

   ```bash
   curl http://192.168.4.1/api/estado
   ```

   Debe devolver un JSON con `"modo":"AP"`. También puedes abrir http://192.168.4.1 en el navegador:
   es la página del propio Gateway, con el último dato de cada sensor. Si no responde, ver la §4.

### 2.2 Levantar todo

```bash
deploy/levantar.sh salon
```

Debe decir `Gateway encontrado en http://192.168.4.1`. El puente corre de fondo. En **otra
terminal**, también desde la raíz del repositorio, mira su registro:

```bash
tail -f demo/servidor/logs/puente.log
```

Deben aparecer `Se le dio la hora de la laptop al Gateway` (si no la tenía) y
`Gateway en línea en http://192.168.4.1`.

### 2.3 Ver el sistema

| Qué | Dónde |
|---|---|
| Tablero del grupo | http://localhost:8000. **Ya no debe decir "DATOS SIMULADOS":** la fuente es `l419`, datos reales |
| Grafana | http://localhost:3000/d/gemelo-l418-completo?var-grupo=l419 (usuario `admin`, clave en `deploy/.env`) |
| Página del Gateway, para comparar | http://192.168.4.1 |
| Gaphor en vivo (opcional, macOS) | `demo/gaphor-vivo/lanzar.sh` |

### 2.4 Grabar la sesión

Así los datos reales se pueden volver a analizar sin el hardware (RF-11). En otra terminal, mientras
todo corre:

```bash
cd demo/servidor && .venv/bin/python -m gemelo.grabacion grabar --grupo l419 --minutos 30 --salida grabaciones/salon-$(date +%Y-%m-%d).jsonl
```

### 2.5 Flashear el nodo MQ-2 (solo si el docente lo permite)

El MQ-2 (nodo 3) es el programa propio del grupo y ya apunta a este Gateway: busca la red
`GEMELO-L419` y envía a la MAC `58:2A:BD:72:03:DC`. Hay dos formas:

- **Arduino IDE:** abrir `firmware/MQ-2/MQ-2.ino`, elegir la placa "ESP32 Dev Module" y el puerto
  USB, y presionar "Subir".
- **arduino-cli:**

  ```bash
  arduino-cli upload --fqbn esp32:esp32:esp32 -p /dev/cu.usbserial-XXXX firmware/MQ-2
  ```

En el Monitor Serie (115200 baudios), la última columna (`envio_ok`) debe valer 1. El nodo aparece en
el tablero como nodo 3 (gas) tras su minuto de calentamiento. Si la compilación falla en una Mac
con chip Apple, ver `firmware/README.md`.

### 2.6 Sin `levantar.sh` (Windows, o si el script falla)

Son cuatro pasos, cada proceso en su propia terminal, todas en la raíz del repositorio:

```bash
docker compose -p campustwin --env-file deploy/.env -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml -f deploy/docker-compose.override.yml up -d
```

```bash
cd demo/servidor && .venv/bin/python -m gemelo.puente_gateway
```

```bash
cd demo/servidor && .venv/bin/python -m gemelo --grupo l419
```

Para que el log de eventos también llegue a InfluxDB, antes del último comando hay que cargar las
variables de `deploy/.env`. En macOS o Linux:

```bash
set -a; source deploy/.env; set +a
```

Para el ensayo sin hardware, agregar antes el Gateway falso con
`.venv/bin/python -m gemelo.gateway_falso --puerto 8090`, y correr el puente con
`--url http://localhost:8090 --grupo sim` y el servicio con `--grupo sim`.

---

## 3. Qué comprobar y anotar

Cada resultado se anota con la **hora** y se rotula **real**. Una captura del tablero y otra de
Grafana por prueba sirven como evidencia para el reporte.

| Prueba | Qué hacer | Qué debe pasar | CP |
|---|---|---|---|
| Llegan los nodos | Mirar "Salud de nodos" en el tablero | Cada nodo instalado tiene datos recientes. Los que no están instalados aparecen caídos y RA-10 lo dice (esperado) | CP-15 |
| Puerta | Abrir y cerrar la puerta | `puerta_abierta` cambia y el log registra la apertura y el cierre | CP-08 |
| Conteo | Entrar y salir de a uno, contando a mano | `entradas`, `salidas` y `ocupacion_est` del nodo térmico coinciden con lo contado | CP-02 |
| Luces | Apagar y encender las luces | `luces_cambio` vale −1 y luego 1, y el log registra el cambio | CP-07 |
| CO₂ | Respirar cerca del MH-Z1911A, después de sus 3 min de calentamiento | `co2_ppm` sube | CP-07 |
| Ambiente | Comparar `temp_c` y `hum_pct` con un termohigrómetro, si hay | Anotar la diferencia | CP-07 |
| Gateway caído | Pedir que desenchufen el Gateway 30 s, o alejarse de su red | El puente avisa "Gateway desconectado" y RA-10 diagnostica el Gateway, no siete sensores. Al volver, "Gateway en línea" | CP-03 |
| Datos en InfluxDB | Grafana con `var-grupo=l419` | Los paneles muestran las series del aula | CP-09 |

También conviene anotar los datos del aula que hoy son supuestos (`config/aula_l419.yaml`): aforo,
medidas, número de luminarias y equipos, y horario.

## 4. Problemas comunes

| Problema | Qué revisar |
|---|---|
| `curl` a `192.168.4.1` no responde | La laptop no está en `GEMELO-L419` (pudo volver a otra red) o el Gateway está apagado. Probar también `http://gemelo-gateway.local` |
| El puente dice "Gateway en línea" pero el tablero no muestra nodos | Los nodos no le envían al Gateway. En http://192.168.4.1, `hace_s` de cada sensor debe ser pequeño (si pasa de 60, ese sensor está apagado o lejos) |
| `levantar.sh` falla en `docker compose` | Docker Desktop no está abierto, o faltan las imágenes (§1.6, necesita internet) |
| InfluxDB no arranca o rechaza la clave | `INFLUX_PASSWORD` tiene menos de 8 caracteres: corregir `deploy/.env` y empezar de nuevo con `down -v` (§5) |
| El puerto 8000 u 8090 está ocupado | Quedó un proceso anterior: `lsof -ti tcp:8000 \| xargs kill -9` (cambiar el puerto si es 8090) |
| Grafana no muestra datos | Cambiar el selector `grupo` a `l419` y la ventana de tiempo a "Last 15 minutes" |
| `Permission denied` al correr `deploy/levantar.sh` | `chmod +x deploy/levantar.sh demo/gaphor-vivo/lanzar.sh` |

## 5. Al terminar

1. `Ctrl+C` en la terminal de `levantar.sh` (cierra también el puente) y en la de la grabación.
2. Apagar el stack:

   ```bash
   docker compose -p campustwin --env-file deploy/.env -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml -f deploy/docker-compose.override.yml down
   ```

   Con `down -v` se borran también los datos de InfluxDB y Grafana de **esa** laptop. Úsalo solo para
   empezar de cero.
3. Volver a la red de siempre.
4. **Opcional:** el Gateway guarda en su flash todo lo que recibió, unos 1,2 MB. Para pasar ese
   historial a InfluxDB, conéctate otra vez a `GEMELO-L419` con el stack arriba pero **sin** el
   servicio, y corre:

   ```bash
   cd demo/servidor && .venv/bin/python -m gemelo.puente_gateway --desde 0
   ```

   Detenlo con `Ctrl+C` cuando el log deje de mostrar mensajes nuevos.
5. **Mandar a José**, para actualizar los casos de prueba a **real** en el documento maestro,
   `docs/pruebas/` y Asana:
   - las notas con las horas;
   - las capturas;
   - la grabación (`demo/servidor/grabaciones/salon-….jsonl`);
   - el log de eventos (`logs/events.jsonl`, en la raíz del repositorio);
   - el registro del puente (`demo/servidor/logs/puente.log`).
