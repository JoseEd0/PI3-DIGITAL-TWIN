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

## gateway_ap_l419/

Gateway con red propia (`gateway_ap.ino`, "Gateway ESP32 v5 — Opción B") y los seis nodos
actualizados, adaptados por otro grupo del curso (el del Gemelo Digital L419) a partir del código
del docente. Es el que está instalado en el aula desde el 17/11/2026. Fuente:
<https://github.com/josecarita/Gemelo-digital-L419-Gateway>, commit `67cccfe` (20/11/2026),
compartido por el docente en el anuncio del 17/11. La guía de uso está en
[docs/curso/texto/guia-gateway-ap.md](../docs/curso/texto/guia-gateway-ap.md).

Qué cambia frente a `gemelo_iot_profesor/`:

- **El Gateway ya no usa MQTT.** Crea la red Wi-Fi `GEMELO-L419` (canal 1, IP `192.168.4.1`),
  guarda cada mensaje en su flash y lo sirve por HTTP (`/api/ultimos`, `/api/datos?desde=<id>`,
  `/api/hora`, `/api/estado`, `/api/borrar`). El JSON es el mismo, más `id` y `gw_ms`. El grupo lo
  conecta a su stack con el puente `demo/servidor/gemelo/puente_gateway.py`.
- **`paquetes.h` es idéntico** al del docente.
- **Nodos:** `espnow_nodo.h` v2 (potencia máxima, radio sin ahorro de energía, re-escaneo de canal
  como mucho cada 30 s y watchdog del loop) y `SSID_ROUTER = "GEMELO-L419"`. El nodo térmico baja
  el I²C a 400 kHz y el de audio se reinicia si falla el I²S. **`nodo_co2/` quedó igual al del
  docente** (sigue buscando `UTEC-Proyectos` y usa el helper viejo): funciona porque, si no
  encuentra la red, usa el canal 1, que es el del Gateway.

Las mismas reglas: no se modifica, y `gateway_ap/gateway_ap.ino` (trae la clave de su red) está en
`.gitignore`; se versiona `gateway_ap.ino.example`, idéntico salvo por `AP_PASS`. La guía original
(`Guia_gateway_AP.docx`) no se versiona: su texto está en `docs/curso/texto/`.
