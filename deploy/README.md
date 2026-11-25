# deploy/ — levantar el servidor en la laptop

Aquí van la configuración local y, más adelante, el `docker-compose.override.yml` con los
servicios del grupo. El `docker-compose.yml` del docente no se toca: se usa desde `vendor/`.

## Primera vez

```bash
cp deploy/.env.example deploy/.env   # y poner claves propias (no las del docente)
```

## Todo con un comando

```bash
deploy/levantar.sh            # stack del docente + servicio del grupo con el simulador
deploy/levantar.sh salon      # Gateway del aula (gateway_ap.ino, red GEMELO-L419) por el puente HTTP->MQTT
deploy/levantar.sh ensayo     # lo mismo con el Gateway falso (datos simulados), para ensayar sin hardware
deploy/levantar.sh grupoX     # Gateway MQTT (gateway.ino del docente) del grupo indicado
```

Desde el 17/11/2026 el Gateway instalado en el L-419 es `gateway_ap.ino`, que no usa MQTT: crea su
propia red Wi-Fi y sirve los datos por HTTP. En los modos `salon` y `ensayo`, `levantar.sh` arranca
de fondo el puente (`python -m gemelo.puente_gateway`, log en `demo/servidor/logs/puente.log`), que
los publica en Mosquitto con el formato oficial, y lo cierra junto con el servicio. El paso a paso
para el aula está en [docs/07-prueba-en-el-salon.md](../docs/07-prueba-en-el-salon.md).

El tablero queda en http://localhost:8000 (o `http://<ip-de-la-laptop>:8000` desde otra laptop
de la red) y Grafana en http://localhost:3000, con los dos tableros del docente ya cargados
(`docker-compose.override.yml`). Se montan desde `grafana/tableros/`, una copia derivada que
resuelve la fuente de datos `${DS_INFLUXDB}` de la exportación del docente; sin ella todos los
paneles dicen "No data". Si el docente actualiza sus JSON, se regenera con
`python3 deploy/grafana/derivar_tableros.py`.

## Levantar y apagar solo el stack (desde la raíz del repo)

```bash
docker compose -p campustwin --env-file deploy/.env \
  -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml up -d
docker compose -p campustwin -f vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml down
```

| Servicio | Dirección | Notas |
|---|---|---|
| Mosquitto | `localhost:1883` | Acepta conexiones anónimas, como en la configuración del docente |
| InfluxDB | http://localhost:8086 | Org `utec`, bucket `gemelo`, token en `deploy/.env` |
| Grafana | http://localhost:3000 | Usuario `admin`, clave en `deploy/.env` |

Se comprobó el 10/11/2026: un mensaje en formato Gateway publicado en `utec/gemelo/sim/nodo1/co2`
llega a InfluxDB con las tags `grupo=sim`, `nodo` y `mac`. Un mensaje con `ts: null` se descarta
(ver `docs/CONTRATO_DATOS.md` §1).
