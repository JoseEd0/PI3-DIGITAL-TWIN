# vendor/ — código de terceros

## gemelo_iot_profesor/

Código oficial del docente (J. F. Figueroa) para los nodos ESP32, el Gateway y el servidor
(Mosquitto → Telegraf → InfluxDB → Grafana). Carpeta de Drive "Gemelo_IoT", descargada el
10/11/2026 como `Gemelo_IoT-20261110T200041Z-1-001.zip` (copia en `docs/curso/originales/`).

Reglas:

- **No se modifica.** Es la referencia contra la que se comparan los cambios del grupo. Lo que el
  grupo adapte va en su propia carpeta (`firmware/`, `servidor/`, …) y se cita como derivado.
- **Dos archivos traen credenciales y no se versionan:** `servidor_iot/.env` (claves de InfluxDB y
  Grafana) y `gateway/gateway.ino` (clave del Wi-Fi). Están en `.gitignore`. En su lugar se
  versionan `servidor_iot/.env.example` y `gateway/gateway.ino.example`, idénticos salvo por los
  valores secretos. Para compilar el Gateway: copiar el `.example` a `gateway.ino` y poner la clave.
- El nodo de **gas MQ-2 (nodo 3) no viene en el ZIP**, aunque `paquetes.h` y el Gateway ya lo
  soportan (`PaqueteGas`, tópico `.../gas`).

El formato de los datos está documentado en [docs/CONTRATO_DATOS.md](../docs/CONTRATO_DATOS.md).
