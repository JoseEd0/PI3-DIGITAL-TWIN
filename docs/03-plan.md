# Plan y seguimiento — Campus Twin L-419

> Espejo local del proyecto [PI3 — Campus Twin L-419](https://app.asana.com/1/1218151758126339/project/1218156351516043)
> en Asana. **Asana es la fuente de verdad** de fechas y responsables; este archivo existe para
> ver y avanzar el plan sin salir del repo.
> Última sincronización desde Asana: **03/09/2026** · 6 de 60 tareas completadas.
> **Revisión local del 10/09/2026, pendiente de subir a Asana**: 70 tareas (10 nuevas, 14
> renombradas). La lista exacta de cambios está al final, en [Pendiente de subir a Asana](#pendiente-de-subir-a-asana-10092026).

## Cómo se actualiza

- Dile a Claude *"ya terminamos el nodo de energía"* y él marca la casilla aquí **y** cierra la
  tarea en Asana en la misma pasada.
- O marca la casilla a mano y pídele que sincronice: lo que esté con `[x]` aquí lo cierra allá.
- Si cambian fechas o responsables, se cambian en Asana y se vuelve a bajar este archivo, para
  que no queden dos verdades distintas.
- Si cambian los requisitos, primero se cambia [00-idea-principal.md](00-idea-principal.md) y el
  modelo SysML, luego este archivo, y al final se suben las tareas nuevas a Asana.

Los identificadores entre paréntesis son los del documento maestro
([00-idea-principal.md](00-idea-principal.md)) y del modelo SysML.

## Estado por fase

| Fase | Fechas | Tareas | Estado |
|---|---|---|---|
| S4 · Formulación y modelado | 31/08–06/09 | 7 | 6 hechas, falta el hito |
| S5–S6 · Especificación, permisos, compras y simulador | 07/09–20/09 | 14 | en curso |
| S7 · Firmware base y servidor | 21/09–27/09 | 6 | pendiente |
| S8–S9 · Integración de nodos | 28/09–11/10 | 12 | pendiente |
| S10–S11 · API, reglas, salud y dashboard | 12/10–25/10 | 9 | pendiente |
| S12 · Copiloto de voz | 26/10–01/11 | 7 | pendiente |
| S13 · Pruebas de sistema | 02/11–08/11 | 7 | pendiente |
| S14 · Entrega final | 09/11–13/11 | 5 | pendiente |
| Gestión y transversales | todo el ciclo | 3 | en curso |

Responsables: **J** = José Eduardo · **C** = Carlos Dávila · **E** = Esteban Sotomayor · **L** = Luhana Landeo.

## S4 · Formulación y modelado (31/08–06/09)

- [x] Consolidar la idea principal, requisitos y plan — **J** · 31/08 → 03/09
- [x] Documentar instrumentación y costos del L-419 — **L** · 31/08 → 02/09
- [x] Crear el proyecto SysML en Gaphor (paquetes y estructura) — **L** · 02/09 → 03/09
- [x] Diagramas de requisitos (req) en Gaphor — **L** · 02/09 → 03/09
- [x] Diagramas de definición de bloques (bdd) en Gaphor — **J** · 02/09 → 03/09
- [x] Crear el proyecto en Asana con fases, tareas y responsables — **J** · 03/09
- [ ] 🏁 **Hito S4** · Formulación y modelado entregados — **J** · 04/09

## S5–S6 · Especificación, permisos, compras y simulador (07/09–20/09)

- [ ] Entrevistar a los stakeholders del laboratorio con las 14 preguntas de 00 §15 — **L** · 07/09 → 11/09
- [ ] Cerrar permiso de instalación y de apertura de la tapa del tablero con Servicios Generales (RNF-01, RF-01) — **L** · 07/09 → 11/09
- [ ] Definir con TI el acceso de los nodos a la red y el uso de router propio (RNF-05, NS-6) — **C** · 07/09 → 11/09
- [ ] Autorización de Seguridad y del contratista para entrevistar y probar con el vigilante (riesgo 9) — **L** · 07/09 → 11/09
- [ ] Definir horario oficial, calendario de excepciones y umbrales de alerta (RF-08, RF-10) — **E** · 09/09 → 11/09
- [ ] Simulador de datos sintéticos, servidor y tablero de demostración en laptop (RF-11) — **J** · 09/09 → 16/09
      *Ya está en `demo/` con 45 pruebas en verde; falta cerrar la tarea en Asana. Ver [04-demo.md](04-demo.md).*
- [ ] Cerrar cotización final y orden de compra, con enchufes compatibles con Tasmota/ESPHome (RNF-03, RF-12) — **L** · 11/09 → 14/09
- [ ] Comprar y recibir componentes — **L** · 14/09 → 18/09
- [ ] Levantar la estructura del repositorio (RNF-07) — **J** · 14/09 → 17/09
- [ ] Definir el contrato de datos: tópicos MQTT, esquema, secuencia e idempotencia (RF-05, RF-06) — **J** · 14/09 → 18/09
- [ ] Armar banco de pruebas y verificar cada sensor por separado — **C** · 16/09 → 20/09
- [ ] Banco de pruebas de voz: micrófono del navegador por HTTPS, STT y TTS locales medidos (RF-09, riesgo 8) — **E** · 16/09 → 20/09
- [ ] Verificar los enchufes con firmware local publicando por MQTT sin internet (RF-12, RNF-05) — **C** · 18/09 → 20/09
- [ ] 🏁 **Hito S6** · Componentes en mano, contrato de datos definido y simulador corriendo — **L** · 18/09

## S7 · Firmware base y servidor (21/09–27/09)

- [ ] Firmware base ESP32: Wi-Fi con reconexión, MQTT QoS 1, buffer local, secuencia y NTP (RF-05) — **C** · 21/09 → 25/09
- [ ] Servidor en Raspberry Pi 5 (o laptop si la Pi no llegó): migrar el Docker Compose, broker con credenciales y arranque automático (RNF-08) — **J** · 21/09 → 24/09
- [ ] Servidor NTP local y batería de RTC en la Pi (RNF-05) — **C** · 23/09 → 24/09
- [ ] Base de datos de series temporales con retención de 60 días (RF-06) — **J** · 24/09 → 27/09
- [ ] Ingesta a la base de datos con descarte de duplicados y conteo de muestras perdidas (RF-05, RF-13) — **J** · 25/09 → 27/09
- [ ] 🏁 **Hito S7** · Un nodo publicando y el servidor almacenando — **J** · 25/09

## S8–S9 · Integración de nodos (28/09–11/10)

- [ ] Nodo de energía: PZEM-004T con caja de toma de tensión y SCT-013 (RF-01, RNF-01) — **C** · 28/09 → 02/10
- [ ] Enchufes inteligentes instalados en proyector y PC principal (RF-12) — **C** · 30/09 → 02/10
- [ ] CP-01 Ensayo de exactitud de energía, PZEM y enchufes — **C** · 02/10 → 03/10
- [ ] Nodo ambiental: SHT31, BH1750 y SCD41 (RF-02) — **L** · 28/09 → 02/10
- [ ] CP-07 Verificación de consistencia ambiental — **L** · 02/10 → 03/10
- [ ] Nodos de ocupación ×2: radar LD2410C, PIR y conteo ToF en la puerta (RF-03) — **E** · 05/10 → 09/10
- [ ] CP-02 Ensayo de presencia con personas quietas y conteo en la puerta — **E** · 08/10 → 09/10
- [ ] Nodo de puerta a batería: ESP32-C3, magnético, SW-420 y latido (RF-04, RNF-04) — **E** · 05/10 → 08/10
- [ ] CP-08 Ensayo de eventos de puerta — **E** · 09/10
- [ ] CP-13 Consumo del nodo de puerta medido y proyección a 30 días (RNF-04) — **E** · 09/10 → 10/10
- [ ] Instalación definitiva de los seis nodos en el L-419 (RNF-01) — **C** · 09/10 → 10/10
- [ ] 🏁 **Hito S9** · Los seis nodos instalados y midiendo — **C** · 09/10

## S10–S11 · API, reglas, salud y dashboard (12/10–25/10)

- [ ] API REST de consulta por rango, magnitud y agregación (RF-06) — **J** · 12/10 → 16/10
- [ ] Motor de reglas y alertas configurables, con silencio y nodo caído (RF-08) — **J** · 14/10 → 17/10
- [ ] Supervisor de salud de nodos y servidor (RF-13) — **J** · 15/10 → 17/10
- [ ] Reporte de consumo fantasma con ahorro en S/ y kg CO₂ (RF-10) — **J** · 16/10 → 18/10
- [ ] Dashboard web: estado en vivo con refresco de 5 s (RF-07) — **J** · 19/10 → 23/10
- [ ] Dashboard: históricos, plano 2D, panel de salud y reporte de ahorro (RF-07, RF-10) — **J** · 21/10 → 25/10
- [ ] Inicio de sesión del dashboard y HTTPS con certificado propio (RNF-08) — **J** · 22/10 → 23/10
- [ ] CP-09, CP-10 y CP-15: ensayos de API, dashboard, reglas y supervisión — **L** · 22/10 → 24/10
- [ ] 🏁 **Hito S11** · Dashboard operativo con datos reales — **J** · 23/10

## S12 · Copiloto de voz (26/10–01/11)

- [ ] App de voz (PWA) en el teléfono: captura por botón, envío al servidor y reproducción de la respuesta (RF-09) — **E** · 26/10 → 28/10
- [ ] Servicio de voz: STT y TTS locales en español sobre la API (RF-09, RNF-02) — **E** · 26/10 → 30/10
- [ ] Briefing automático de inicio de ronda (RF-09) — **E** · 29/10 → 31/10
- [ ] Intenciones cerradas y respuesta de "no entendí, repite" (RF-09) — **E** · 29/10 → 31/10
- [ ] Nodo de audio fijo: INMP441, MAX98357A y parlante (opcional, solo si el hito S12 ya se cumplió) — **E** · 31/10 → 01/11
- [ ] CP-04 Ensayo del copiloto de voz con 2 hablantes y ruido de pasillo — **L** · 31/10 → 01/11
- [ ] 🏁 **Hito S12** · Copiloto de voz respondiendo desde el teléfono en el laboratorio — **E** · 30/10

## S13 · Pruebas de sistema (02/11–08/11)

- [ ] CP-03 Ensayo de resiliencia de red y operación sin internet (RF-05, RNF-05) — **C** · 02/11 → 03/11
- [ ] CP-05 Maratón de 72 h sin intervención, con corte de energía provocado (RNF-06) — **L** · 02/11 → 05/11
- [ ] Grabar un día de datos reales y modo demostración por nodo, CP-11 (RF-11) — **J** · 03/11 → 05/11
- [ ] CP-06 Auditoría de consumo fantasma (RF-10) — **J** · 05/11 → 06/11
- [ ] CP-12 Revisión de instalación, seguridad eléctrica y privacidad (RNF-01, RNF-02) — **E** · 05/11 → 06/11
- [ ] CP-14 Auditoría de costos, configuración y credenciales (RNF-03, RNF-07, RNF-08) — **L** · 06/11 → 07/11
- [ ] 🏁 **Hito S13** · Todos los casos de prueba ejecutados — **L** · 06/11

## S14 · Entrega final (09/11–13/11)

- [ ] Informe final de resultados — **L** · 09/11 → 11/11
- [ ] Actualizar docs/ y el modelo SysML con el estado final — **J** · 09/11 → 11/11
- [ ] Póster y presentación — **E** · 09/11 → 12/11
- [ ] Ensayo completo de la demo (con plan B en modo demostración) — **C** · 11/11 → 12/11
- [ ] 🏁 **ENTREGA FINAL** · Presentación y demo en vivo — **J** · 13/11

## Gestión y transversales

- [ ] Reunión semanal de avance y actualización del tablero — **J** · viernes, 04/09 → 13/11
- [ ] Registro de riesgos: revisar mitigaciones cada dos semanas — **L** · 07/09 → 06/11
- [ ] Bitácora de mediciones y calibraciones — **L** · 28/09 → 07/11

## Pendiente de subir a Asana (10/09/2026)

Cambios locales de la revisión técnica v2 que todavía no están en el tablero. Al subirlos, se
borra esta sección y se actualiza la fecha de sincronización.

**Tareas nuevas (10):**

| Fase | Tarea | Resp. | Fechas |
|---|---|---|---|
| S5–S6 | Autorización de Seguridad y del contratista para entrevistar y probar con el vigilante | L | 07/09 → 11/09 |
| S5–S6 | Simulador de datos sintéticos, servidor y tablero de demostración en laptop (RF-11) | J | 09/09 → 16/09 |
| S5–S6 | Banco de pruebas de voz: micrófono por HTTPS, STT y TTS locales medidos (RF-09) | E | 16/09 → 20/09 |
| S5–S6 | Verificar los enchufes con firmware local publicando por MQTT sin internet (RF-12, RNF-05) | C | 18/09 → 20/09 |
| S7 | Servidor NTP local y batería de RTC en la Pi (RNF-05) | C | 23/09 → 24/09 |
| S8–S9 | Enchufes inteligentes instalados en proyector y PC principal (RF-12) | C | 30/09 → 02/10 |
| S8–S9 | CP-13 Consumo del nodo de puerta medido y proyección a 30 días (RNF-04) | E | 09/10 → 10/10 |
| S10–S11 | Supervisor de salud de nodos y servidor (RF-13) | J | 15/10 → 17/10 |
| S10–S11 | Inicio de sesión del dashboard y HTTPS con certificado propio (RNF-08) | J | 22/10 → 23/10 |
| S12 | Intenciones cerradas y respuesta de "no entendí, repite" (RF-09) | E | 29/10 → 31/10 |

**Tareas renombradas o con alcance ampliado (14):** entrevistas (14 preguntas), permiso de
tablero, acceso a red y router propio, horario y calendario de excepciones, cotización con
enchufes flasheables, contrato de datos con idempotencia, firmware base con NTP, servidor con
credenciales, ingesta con duplicados y muestras perdidas, nodo de energía con caja de toma de
tensión, nodos de ocupación ×2, nodo de puerta con ESP32-C3 y latido, instalación de seis nodos,
motor de reglas con silencio y nodo caído.

**Tareas reemplazadas (2):** "Nodo de audio" pasa a opcional al final de S12; "Consultas orales
con audífono Bluetooth" se reemplaza por "App de voz (PWA) en el teléfono".

**Tareas movidas (1):** CP-13 pasa de S13 a S9, junto al nodo de puerta; la tarea de S13
"CP-12 y CP-13" queda solo como CP-12.

**Hitos renombrados (3):** S6 agrega "simulador corriendo"; S9 dice "seis nodos"; S12 dice
"desde el teléfono".

**Tareas ya terminadas que falta cerrar en Asana (1):** el simulador, el servidor
de demostración y el tablero web están hechos y probados en `demo/`. Al sincronizar,
marcar la casilla aquí y cerrar la tarea allá en la misma pasada.
