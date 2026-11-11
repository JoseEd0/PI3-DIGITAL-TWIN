# Pruebas del sistema

Cada caso de prueba (CP) del documento maestro, con su rótulo: **real** (hardware o revisión del
repo), **simulado** (datos del simulador) o **pendiente**.

| CP | Qué verifica | Rótulo | Dónde |
|---|---|---|---|
| CP-06 | Consumo fantasma estimado frente a la verdad simulada (3 escenarios) | Simulado | [CP-06-consumo-fantasma.md](CP-06-consumo-fantasma.md), que se regenera con `python -m gemelo.auditoria` |
| CP-09 / CP-10 | API, tablero, reglas, RA y diagnóstico causal | Simulado | `demo/servidor/pruebas/` (`pytest`) |
| CP-11 | Simulador en formato Gateway, grabación y reproducción | Simulado | `test_gemelo.py` (pruebas de grabación) y la prueba de punta a punta de abajo |
| CP-14 | Costos, configuración y credenciales del repositorio | Real (revisión del repo) | [CP-14-auditoria-repositorio.md](CP-14-auditoria-repositorio.md) |
| CP-12 | Privacidad (RNF-02) e instalación no invasiva (RNF-01) | Privacidad: **real** (revisión de código). Instalación: **pendiente** (S15) | [CP-12-privacidad.md](CP-12-privacidad.md) |
| CP-13 | Autonomía de las cajas con 18650 | Estimación de hoja de datos (**no es una medición**). Medición: **pendiente** (S15) | [docs/06-energia-cajas.md](../06-energia-cajas.md) |
| CP-02, 03, 07, 08 | Conteo, resiliencia, ambiente y puerta | **Pendiente** (S15, con hardware) | Plan en `docs/05-plan-cierre.md` |
| CP-04, 05 | Copiloto de voz y maratón de 72 h | **Pendiente** (S16) | — |

## CP-11 · grabación y reproducción de punta a punta (10/11/2026, simulado)

Se generó una grabación de 12 minutos del aula con el guion clase → gas (min 4) → restablecer
(min 10) → Gateway caído (min 12). Son 1372 mensajes. Luego se reprodujo a ×60 por Mosquitto, con
Telegraf e InfluxDB del docente, en el grupo `rep`.

- **InfluxDB recibió los 1372 mensajes**, la misma cantidad por tipo que la grabación: audio 720,
  co2 144, gas 144, térmico 144, ambiente 72, luz 72 y magnético 74.
- El log en `campustwin_evento` tiene la secuencia del guion:
  - Gateway en línea;
  - entradas y puerta;
  - GAS_DETECTADO a las 09:04;
  - RA-05 crítico a las 09:04:30;
  - RA-05 vuelve a nominal a las 09:10:30;
  - Gateway desconectado y RA-10 crítico a las 09:12.
- La prueba encontró un **bug** que ya está corregido: dos procesos usaban el mismo `client_id`
  MQTT, Mosquitto los desconectaba por turnos cada segundo y se perdía la mitad de los mensajes.
  Ahora cada proceso usa un identificador distinto.
