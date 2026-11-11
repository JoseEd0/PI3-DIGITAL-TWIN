# firmware/ — programas propios del grupo para las cajas

El firmware oficial de los nodos 1, 2, 4, 5, 6 y 7 y del Gateway es **del docente** y está sin
cambios en [vendor/gemelo_iot_profesor/](../vendor/gemelo_iot_profesor/). Aquí va solo lo que el
grupo escribió o adaptó.

| Carpeta | Qué es | Autor | Estado |
|---|---|---|---|
| [MQ-2/](MQ-2/) | Nodo 3 (gas y humo, MQ-2) → ESP-NOW → Gateway | `MQ-2.ino`: Grupo 1 (S8). `espnow_nodo.h` y `paquetes.h`: **docente, copiados sin cambios** | Compila. **Sin probar en hardware** |
| [energia/](energia/) | `autonomia.py`: recalcula la tabla de consumo y autonomía de las cajas desde [config/energia_nodos.yaml](../config/energia_nodos.yaml) | Grupo 1 | Estimado, sin medición real |

## Nodo 3 — `MQ-2/MQ-2.ino`

Sigue la estructura de `nodo_co2.ino`, `nodo_luz.ino` y `nodo_magnetico.ino` del docente: el mismo
`espnow_nodo.h`, el `PaqueteGas` de `paquetes.h` tal cual (`v_ao`, `rs_r0`, `do_alarma`,
`calentando`, `anomalias`) y los bits `GAS_BIT_FALLO` y `GAS_BIT_GAS_DETECTADO`. El Gateway del
docente ya lo decodifica y lo publica en `utec/gemelo/<grupo>/nodo3/gas`.

- **Fases:** calienta 60 s (como `GAS_CALENTAMIENTO_S` del simulador); en los últimos 10 s promedia
  Rs en aire limpio y fija R0. Si el aire no estuvo estable (variación > 10 %), repite la
  calibración y sigue con `calentando = 1`. Con `R0_FIJO_KOHM > 0` usa un R0 medido y no calibra.
- **Índice:** `rs_r0 = Rs / R0`, con R0 = Rs en el aire limpio del aula (1 = aire limpio, como dice
  `paquetes.h`). La RL del módulo se cancela en el cociente.
- **Anomalías:** `GAS_DETECTADO` cuando `rs_r0 < 0.70` (el umbral del simulador), con 3 lecturas de
  confirmación y se apaga sobre 0.80. `FALLO_SENSOR` tras 5 lecturas inválidas (AO cerca de 0 V:
  módulo desconectado o calefactor apagado). Los niveles de alerta 0.75 y crítico 0.50 de RA-05
  los evalúa el servicio, no el nodo.
- **Envío:** lee cada 1 s y envía cada 5 s, y en el acto si cambia el gas, el DO o el fallo.

### Conexión (supuesta: confirmar con el módulo real)

| Módulo MQ-2 | ESP32 DevKit V1 | Por qué |
|---|---|---|
| VCC | VIN (5 V) | El calefactor necesita 5 V ± 0.1 V (hoja de datos Hanwei) |
| GND | GND | |
| AO | divisor 10 k (arriba) / 15 k (abajo) → GPIO 34 | AO llega a 5 V y el ESP32 tolera 3.3 V. GPIO 34 es ADC1: ADC2 no funciona con la radio activa |
| DO | divisor 22 k / 47 k → GPIO 27 | El pull-up del LM393 del módulo va a 5 V |

### Compilar

```bash
arduino-cli core install esp32:esp32          # núcleo oficial de Espressif (se probó la 3.3.12)
arduino-cli compile --fqbn esp32:esp32:esp32 firmware/MQ-2
arduino-cli upload  --fqbn esp32:esp32:esp32 -p /dev/cu.usbserial-XXXX firmware/MQ-2
arduino-cli monitor -p /dev/cu.usbserial-XXXX -c baudrate=115200
```

La placa del curso es el **ESP32 DevKit V1 (NodeMCU-32, 30 pines)**, que corresponde a
`esp32:esp32:esp32` (ESP32 Dev Module). No hace falta ninguna biblioteca externa.

**En Mac con Apple Silicon sin Rosetta**, el `ctags` que trae arduino-cli es x86_64 y la
compilación falla con `bad CPU type in executable`. Hay dos salidas: instalar Rosetta
(`softwareupdate --install-rosetta`) o usar `universal-ctags` (Homebrew) a través de una envoltura
que cambia `typeref:typename:` por `returntype:` y pasarla con
`--build-property "tools.ctags.path=<carpeta de la envoltura>"`. Con la envoltura los prototipos
quedan bien formados pero en otra línea, lo que no afecta a `MQ-2.ino`, porque define cada función
antes de usarla. Se comprobó compilando el mismo código como `.cpp`, sin prototipos generados, y
salió el mismo binario: 897 464 B.

Antes de flashear hay que cambiar `SSID_ROUTER` por la red donde está el Gateway, que solo se usa
para hallar el canal, y verificar `MAC_GATEWAY`, que hoy tiene la del ESP32 v4 del docente, igual
que sus nodos. El nodo no se conecta al Wi-Fi y no lleva claves.

### Sin probar en hardware

Hoy **no hay ninguna medición real** del nodo. Queda pendiente para cuando haya acceso al módulo:

1. Confirmar la RL del módulo (resistencia SMD "102" = 1 k u otra), si el DO es activo en bajo y el
   pull-up del LM393.
2. Ver por el monitor serie el `v_ao` en aire limpio y ajustar `V_AO_MIN_VALIDO` (0.10 V) si hace falta.
3. Medir R0 en el aula tras 24 h de precalentamiento (hoja de datos) y anotarlo en `R0_FIJO_KOHM`.
4. Probar el umbral 0.70 con un encendedor apagado (gas butano) a distancia, no con llama.
