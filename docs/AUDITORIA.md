# Auditoría del proyecto — Campus Twin L-419

> Hecha el **09–10/11/2026** (semana 14). La EC3 vence el viernes 13/11 a las 23:59.
> Compara lo que afirman el [brief](curso/brief-ec3.md), el reporte de la Semana 7 y Asana con lo
> que hay de verdad en el repositorio (rama `jose`, commit `b69ba2a`), en el código del docente
> (`vendor/gemelo_iot_profesor/`) y en Asana. Cada fila dice cómo se comprobó.

Clasificación: **Existe y funciona** · **Existe incompleto** · **No existe**.

## 1. Resumen

1. **La arquitectura oficial la puso el docente y hay que adoptarla.** Tiene 7 nodos ESP32 que
   envían por ESP-NOW a un Gateway ESP32, que publica por MQTT en una laptop con Docker (Mosquitto,
   Telegraf, InfluxDB y Grafana). El código de los nodos, del Gateway y del servidor existe y está en
   `vendor/`. El formato está en [CONTRATO_DATOS.md](CONTRATO_DATOS.md).
2. **El grupo sí tiene código propio que funciona,** aunque el brief diga lo contrario. `demo/` tiene
   simulador, API, reglas, consumo fantasma, tablero React y sincronización en vivo con Gaphor. Las
   51 pruebas pasan y el servidor arranca. Se hizo entre el 10/09 y el 23/09, pero **todo es
   simulado y usa la arquitectura vieja**: 6 nodos con sensores propios, MQTT directo y una
   Raspberry Pi.
3. **Lo que dice la Semana 7 es cierto, pero solo en simulación.** El script de Gaphor en vivo y el
   hallazgo del nodo de puerta existen. En la EC3 se rotulan "simulado"; no se presentan como
   mediciones reales.
4. **No hay nada físico.** No hay nodos armados ni mediciones reales. El hardware está en el L-414.
5. **Lo nuevo que pide la EC3 no existe todavía:**
   - los requisitos de alto nivel RA;
   - los grafos causales y su motor;
   - el log de eventos;
   - el dashboard con condiciones, causas y recomendaciones;
   - los paquetes de comportamiento en Gaphor;
   - el programa .ino propio del grupo;
   - el reporte EC3.
6. **Hay un hueco natural para el .ino del grupo: el nodo de gas MQ-2 (nodo 3).** Está en la
   arquitectura, en `paquetes.h` y en el Gateway, pero el ZIP no trae su programa.
7. **Las ramas están separadas.** `main` no tiene la demo, y `origin/main` tiene 8 commits de Luhana
   que no están en `jose`. Se comprobó que la fusión sale limpia.

## 2. Código del docente (`vendor/gemelo_iot_profesor/`)

| Elemento | Estado | Evidencia |
|---|---|---|
| `gateway/` (`gateway.ino`, `paquetes.h`) | **Existe** (sin probar en hardware) | Recibe por ESP-NOW y publica JSON en `utec/gemelo/<grupo>/nodo<id>/<tipo>`. Su estado va por LWT. Toma la hora por NTP de internet. |
| `nodo_co2` (1), `nodo_audio` (2), `nodo_luz` (4), `nodo_termico` (5), `nodo_magnetico` (6), `nodo_ambiente` (7) | **Existen** (sin compilar aquí) | Cada uno calcula sus propios niveles y bits de anomalía. Los 7 `paquetes.h` son idénticos, y los `espnow_nodo.h` también. |
| `nodo_gas` (3, MQ-2) | **No existe** | El ZIP no lo trae, aunque el paquete y el Gateway ya lo soportan. |
| Nodo de energía (PZEM-004T) | **No existe** | No está en la arquitectura ni en `paquetes.h`. |
| `servidor_iot/` (docker-compose, Mosquitto, Telegraf, Grafana) | **Existe** (sin levantar aquí) | Usa InfluxDB 2.7 con org `utec` y bucket `gemelo`. Telegraf toma el measurement de `tipo` y las tags de `nodo`, `mac` y `grupo`. |
| Dashboards de Grafana | **Existen** | "Gemelo digital L418 — 7 sensores" (36 paneles) y la versión anterior (CO₂ y audio). No muestran la condición frente a requisitos ni causas o recomendaciones. |
| Credenciales | **Aisladas** | `servidor_iot/.env` y `gateway/gateway.ino` traen claves. Quedan fuera de git; se versionan sus `.example`. |
| `arquitectura_iot_gemelo_digital_L418.png` | **Existe** | Dice "L418"; el grupo trabaja con L-419. |

## 3. Trabajo propio del grupo

| Elemento | Qué afirma la Semana 7 | Estado | Evidencia |
|---|---|---|---|
| Modelo de Gaphor | 12 diagramas en 4 paquetes | **Existe y funciona, con hardware viejo** | Están `modelo/campus-twin-l419.gaphor`, los 12 SVG y `build_model.py`, que verifica la trazabilidad. No hay IBD, actividades, estados ni casos de uso. |
| Diagramas sueltos de Luhana | — | **Existe incompleto** | Solo están en `origin/main` (`BDD.gaphor`, `Diagrama de requisitos.gaphor` y sus PNG), fuera del modelo generado. |
| Sincronización en vivo con Gaphor | Escribe valores y colorea bloques | **Existe y funciona (simulado)** | Está en `demo/gaphor-vivo/` y lee de la API de la demo. Falta que lea de InfluxDB. |
| NS-1..7, RF-01..13, RNF-01..08, CP-01..15 | Medibles y con pruebas | **Existe, con hardware viejo** | `docs/00-idea-principal.md` §8. Son **RNF-01..08**, no RNF-01..06 como dice el brief. |
| RA-01..10 | — | **No existe** | — |
| Contrato de datos (José, cerrado en Asana) | — | **Existe, pero reemplazado** | El de la demo (`l419/<nodo>/<magnitud>`) cede ante el del Gateway del docente. |
| Horario oficial y umbrales (Esteban, cerrado en Asana) | — | **Existe incompleto** | En `configuracion.py` están marcados PENDIENTE. Los umbrales del docente coinciden en CO₂ (1000 y 1500) y en confort térmico (20–26 °C). |
| Simulador y modo demo (RF-11) | "Hicimos primero un simulador" | **Existe, formato viejo** | Tiene 7 escenarios. No publica en el formato del Gateway, no simula el MQ-2 ni el conteo térmico, y no graba ni reproduce. |
| Servidor, API y reglas (RF-08, RF-10, RF-13) | Planificado para S7–S11 | **Existe (simulado)** | FastAPI con bus y almacenamiento en memoria. Sin MQTT real ni InfluxDB. |
| Dashboard | Planificado para S10–S11 | **Existe incompleto** | El React de la demo tiene plano, energía, ambiente, ocupación, alertas, salud y consumo fantasma. Le faltan el semáforo por RA, las causas, efectos y recomendaciones, y el log. |
| Log de eventos (footprint) | — | **No existe** | Todo vive en memoria. |
| Grafos causales y motor | — | **No existe** | — |
| Firmware propio (.ino) | Planificado para S7 | **No existe** | El docente exige uno por grupo, aunque el grupo no monte caja. |
| Copiloto de voz | Planificado para S12 | **No existe** | — |
| Paquetes 04 Comportamiento y 05 Razonamiento en Gaphor | — | **No existe** | — |
| Presupuesto RNF-03 (S/ 2808) | — | **Desactualizado** | El hardware lo compró el curso. |
| Hardware físico | "Seis nodos con ESP32 miden" | **No existe** | El usuario lo confirmó. |
| Diseño de las cajas (23/10) | — | **Fuera del repo** | Lo subió otro integrante y faltan los archivos. |

## 4. Asana frente a la realidad (al 09/11, antes de reorganizarlo)

Había 60 tareas, de las cuales 17 estaban cerradas.

| Tarea | Problema | Qué se hizo el 10/11 |
|---|---|---|
| Instalación definitiva de los nodos en el L-419 | Estaba cerrada sin que existieran nodos | Se reabrió. |
| Hito S6 · Componentes en mano | Contradecía "Comprar y recibir componentes", que seguía abierta | Los componentes los compró el curso (OC-UTEC-004033-26) y están en el L-414. Se cerró "Comprar y recibir componentes" con esa nota. |
| Tareas de S7 a S13 | Redactadas con hardware y arquitectura viejos | Se renombraron o se cerraron según el caso. Ver `docs/03-plan.md`. |
| Simulador y modo demo | No estaba en Asana aunque está hecho | Se agregó. |

## 5. Correcciones al brief (v3) y a los reportes

1. **"Hoy no hay código propio funcional"** es falso. Ver la sección 3.
2. **"El script de Gaphor en vivo no existe"** es falso: existe, en simulación.
3. **RNF-01..06** son en realidad **RNF-01..08**. No se renumera.
4. **El nodo térmico del docente no envía la matriz**, sino que cuenta en el ESP32 y manda
   entradas, salidas y ocupación. Por eso el conteo en el servidor ya no hace falta. La "matriz
   sintética de 32×24" del simulador solo sirve para ilustrar.
5. **El Gateway necesita NTP de internet** para la marca de tiempo, lo que choca con RNF-05. Se
   propone NTP local en la laptop.
6. En la planilla de compra, el **PZEM figura como "Ocupación del ambiente"**. Parece un error.
7. El reporte de la Semana 7 omite a **Carlos** en la tabla de roles y escribe mal "Huamán" y
   "Luhana Landeo". Los nombres correctos son **Huamani Ñaupas, José Eduardo** y **Landeo Quispe,
   Luhana Victoria**.
8. La rúbrica de 4 × 4 puntos que cita el brief no está en ningún archivo del curso.
9. **RA-02 (humedad)**: el brief propone 30–60 %, pero el nodo ambiente del docente alerta con
   `HUM_ALTA = 70.0` y la regla del proyecto es alinear los umbrales con su código. Rige
   **30–70 %** (crítico < 20 o > 80 %), como en `config/requisitos_ra.yaml`, el documento maestro
   y el reporte. El 60 % de ASHRAE 62.1 queda citado como referencia, no como umbral.
10. **Los tableros de Grafana del docente** están exportados para importarse a mano: apuntan a la
    fuente `${DS_INFLUXDB}`, que el aprovisionamiento por archivos no resuelve, y todos sus paneles
    decían "No data". `deploy/grafana/derivar_tableros.py` genera una copia derivada que usa la
    fuente por defecto; el original no se toca.

## 6. Datos que faltan

- Aforo, plano e inventario de potencias del L-419 (luminarias, PC, proyector y aire
  acondicionado), que hacen falta para estimar el consumo fantasma por proxy.
- Si el PZEM se integra como nodo 8 (hay que preguntarlo al docente).
- Horario oficial del L-419 (Esteban).
- Archivos del diseño de caja y estado de la C1 y del logotipo en Canvas.
- Qué hacer con los diagramas sueltos de Luhana.
- El valor de `GRUPO` que usará el Gateway real de S1 G1 y la IP de su laptop.

## 7. Siguiente paso

El plan de cierre está en [05-plan-cierre.md](05-plan-cierre.md).
