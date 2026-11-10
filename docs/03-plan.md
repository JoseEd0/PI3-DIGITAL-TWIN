# Plan y seguimiento — Campus Twin L-419

> Espejo local del proyecto [PI3 — Campus Twin L-419](https://app.asana.com/1/1218151758126339/project/1218156351516043)
> en Asana. **Asana es la fuente de verdad** de fechas y responsables. Este archivo sirve para ver y
> avanzar el plan sin salir del repo.
> Última sincronización desde Asana: **10/11/2026**. Van **25 de 75 tareas** completadas.
> La estrategia de cierre (qué se hace hasta el 13/11 y qué después) está en
> [05-plan-cierre.md](05-plan-cierre.md).

## Cómo se actualiza

- Cuando se termina una tarea, se marca la casilla aquí **y** se cierra en Asana, en la misma pasada.
- Si cambian fechas o responsables, se cambian en Asana y se vuelve a bajar este archivo.
- Si cambian los requisitos, primero se actualiza [00-idea-principal.md](00-idea-principal.md) y el
  modelo SysML, y después las tareas.

Responsables: **J** = José Eduardo · **C** = Carlos Dávila · **E** = Esteban Sotomayor · **L** = Luhana Landeo.
Las fechas son de entrega. Asana gratuito no permite fecha de inicio.

## Reorganización del 10/11/2026

El curso fijó una **arquitectura oficial** el 07/11. Tiene 7 nodos ESP32 que envían por ESP-NOW a
un Gateway, y una laptop con Mosquitto, Telegraf, InfluxDB y Grafana. El código es del docente y
está en `vendor/`. El curso compró el hardware. Por eso el tablero se reorganizó así:

- **Se reabrió 1 tarea:** "Instalación definitiva de los nodos" figuraba como completada sin que
  existieran nodos.
- **Se cerraron 8 tareas por trabajo que ya existía:**
  - 4 de software hecho sobre el simulador entre el 10/09 y el 23/09 (`demo/`);
  - la tarea de componentes, porque los compró el curso;
  - la base de datos, que es la InfluxDB del docente;
  - el estudio del firmware del docente;
  - la centralización del material.
- **Se renombraron 30 tareas** para quitar el hardware antiguo (SHT31, SCD41, LD2410C, PIR, ToF,
  SW-420, SCT-013, Tasmota, Raspberry Pi y MAX98357A) y la arquitectura antigua.
- **Se agregaron 15 tareas:** las que pide la EC3 (RA, grafos, motor causal, log, dashboard propio,
  Gaphor y fotos con QR), el programa .ino propio, la cita en el L-414, la energía de las cajas, el
  NTP local y el logotipo.
- **Las pruebas con hardware real pasan al 20/11**, después de la EC3 y sujetas a una cita en el
  L-414. Esa fecha es supuesta: cámbienla si el curso fija otra.

## Estado por fase

| Fase en Asana | Tareas | Hechas | Lo que queda |
|---|---|---|---|
| S4 · Formulación y modelado | 7 | 7 | — |
| S5–S6 · Especificación, permisos y compras | 10 | 10 | — |
| S7 · Firmware base y servidor | 6 | 3 | Levantar el stack del docente con datos simulados (11/11) |
| S8–S9 · Integración de nodos | 10 | 0 | Consumo fantasma por proxy y MQ-2.ino (12/11). El resto, con hardware (20/11) |
| S10–S11 · API, reglas y dashboard | 7 | 4 | API sobre InfluxDB y dashboard EC3 (12/11) |
| S12 · Copiloto de voz | 6 | 0 | Es opcional (13/11) |
| S13 · Pruebas de sistema | 7 | 0 | Pruebas simuladas (11–12/11). Las físicas, el 20/11 |
| S14 · Entrega final | 19 | 1 | El núcleo de la EC3 (10–13/11) |
| Gestión y transversales | 3 | 0 | Siguen abiertas todo el ciclo |

## S4 · Formulación y modelado (31/08–06/09)

- [x] Consolidar la idea principal, requisitos y plan — **J** · 03/09
- [x] Documentar instrumentación y costos del L-419 — **L** · 02/09
- [x] Crear el proyecto SysML en Gaphor (paquetes y estructura) — **L** · 03/09
- [x] Diagramas de requisitos (req) en Gaphor — **L** · 03/09
- [x] Diagramas de definición de bloques (bdd) en Gaphor — **J** · 03/09
- [x] Crear el proyecto en Asana con fases, tareas y responsables — **J** · 03/09
- [x] 🏁 Hito S4 · Formulación y modelado entregados — **J** · 04/09

## S5–S6 · Especificación, permisos y compras (07/09–20/09)

- [x] Entrevistar a los stakeholders del laboratorio — **L** · 11/09
- [x] Definir horario oficial del L-419 y umbrales de alerta — **E** · 11/09
- [x] Definir con TI el acceso de los nodos a la red — **C** · 11/09
- [x] Cerrar permiso de instalación con Servicios Generales — **L** · 11/09
- [x] Cerrar cotización final y orden de compra — **L** · 14/09
- [x] Levantar la estructura del repositorio — **J** · 17/09
- [x] Definir el contrato de datos: tópicos MQTT, esquema y unidades — **J** · 18/09
- [x] Armar banco de pruebas y verificar cada sensor por separado — **C** · 20/09
- [x] Simulador, tablero y Gaphor en vivo sobre la arquitectura anterior (`demo/`) — **J** · 23/09
- [x] 🏁 Hito S6 · Componentes en mano y contrato de datos definido — **L** · 18/09

## S7 · Firmware base y servidor

- [x] Estudiar y documentar el firmware del docente (ESP-NOW, paquetes.h, Gateway) — **J** · hecho el 10/11
- [x] Base de datos de series temporales: InfluxDB 2.7 del docente — **J** · hecho el 10/11
- [x] Componentes: los compró el curso (OC-UTEC-004033-26) — **L** · hecho el 10/11
- [ ] Servidor en la laptop: stack Docker del docente + servicios del grupo (override) — **J** · 11/11
- [ ] Ingesta: datos en formato Gateway llegando a InfluxDB (Telegraf del docente) — **J** · 11/11
- [ ] 🏁 Hito · Datos simulados en formato Gateway visibles en InfluxDB y Grafana — **J** · 11/11

## S8–S9 · Integración de nodos

- [ ] Consumo fantasma por proxy (BH1750 + MLX90640 + horario) y consulta al docente por el PZEM (RF-10) — **J** · 12/11
- [ ] Programa propio del grupo: nodo de gas MQ-2 (`MQ-2.ino`) que compile — **C** · 12/11
- [ ] Probar en el L-414 los nodos ambiente (BME280), luz (BH1750) y CO₂ (MH-Z1911A) con el código del docente — **L** · 20/11
- [ ] Conteo de personas: MLX90640 + KY-024 con el código del docente, prueba en el L-414 (RF-03) — **E** · 20/11
- [ ] CP-01 Ensayo de exactitud de energía (si se integra el PZEM) — **C** · 20/11
- [ ] CP-02 Ensayo de conteo de personas (MLX90640 + KY-024) — **E** · 20/11
- [ ] CP-07 Verificación ambiental: BME280, MH-Z1911A y BH1750 contra referencia — **L** · 20/11
- [ ] CP-08 Ensayo de eventos de puerta (KY-024) — **E** · 20/11
- [ ] Instalación de los 7 nodos en el L-419 (después de la EC3) — **C** · 20/11
- [ ] 🏁 Hito · Siete nodos probados en el L-414 — **C** · 20/11

## S10–S11 · API, reglas y dashboard

- [x] Motor de reglas y alertas configurables (sobre el simulador) — **J** · hecho en septiembre
- [x] Reporte de consumo fantasma (sobre el simulador) — **J** · hecho en septiembre
- [x] Dashboard web: estado en vivo (sobre el simulador) — **J** · hecho en septiembre
- [x] Dashboard: plano 2D del laboratorio y reporte de ahorro (sobre el simulador) — **J** · hecho en septiembre
- [ ] API del grupo sobre InfluxDB: estado, condición por RA, diagnósticos y log — **J** · 12/11
- [ ] CP-09 y CP-10: ensayos de API, dashboard y reglas (con datos simulados) — **L** · 12/11
- [ ] 🏁 Hito · Dashboard propio con los 3 mínimos de la EC3 — **J** · 12/11

## S12 · Copiloto de voz (opcional para la EC3)

- [ ] Copiloto: voz del navegador (Web Speech API) en español sobre la API del grupo (RF-09) — **E** · 13/11
- [ ] Copiloto PWA: consultas orales desde el navegador del celular — **E** · 13/11
- [ ] Briefing automático de inicio de ronda — **E** · 13/11
- [ ] 🏁 Hito · Copiloto respondiendo en el celular (opcional) — **E** · 13/11
- [ ] Validar el nodo de ruido INMP441 del docente (dB, sin guardar audio) — **E** · 20/11
- [ ] CP-04 Ensayo del copiloto de voz — **L** · 20/11

## S13 · Pruebas de sistema

- [ ] RF-11 y CP-11: simulador en formato Gateway con grabación y reproducción — **J** · 11/11
- [ ] CP-06 Auditoría de consumo fantasma (con datos simulados) — **J** · 12/11
- [ ] CP-12 y CP-13: privacidad (MLX90640, INMP441) y energía de las cajas (18650) — **E** · 12/11
- [ ] CP-14 Auditoría de costos, configuración y credenciales del repositorio — **L** · 12/11
- [ ] CP-03 Resiliencia: Gateway caído, canal ESP-NOW y operación sin internet — **C** · 20/11
- [ ] CP-05 Maratón de 72 h sin intervención — **L** · 20/11
- [ ] 🏁 Hito · Casos de prueba ejecutados (simulados ahora, físicos después) — **L** · 20/11

## S14 · Entrega final (09/11–13/11)

- [x] Centralizar material del curso y auditar el repo (`docs/curso`, `vendor`, `AUDITORIA`, `CONTRATO_DATOS`) — **J** · 10/11
- [ ] Integrar las ramas `jose` y `main` (incluye los diagramas de Luhana) — **J** · 10/11
- [ ] RA-01..10: requisitos de alto nivel con umbrales y normas (`config/`) — **E** · 11/11
- [ ] Grafos causales por RA (`graphs/*.yaml`) y sus figuras — **E** · 11/11
- [ ] Motor de razonamiento causal (SymCure) con pruebas por tipo de lógica — **J** · 11/11
- [ ] Log de eventos / footprint (`events.jsonl` + InfluxDB) con exportación a CSV — **J** · 12/11
- [ ] Dashboard propio: mediciones, condición por RA y causas, efectos y recomendaciones — **J** · 12/11
- [ ] Gaphor en vivo leyendo InfluxDB — **J** · 12/11
- [ ] Gaphor: migrar al hardware oficial, IBD y paquetes 04 Comportamiento y 05 Razonamiento — **J** · 12/11
- [ ] Actualizar el documento maestro y el plan al hardware y la arquitectura oficiales — **L** · 12/11
- [ ] Cargar las fotos con QR de los sensores en Gaphor y en Asana — **L** · 12/11
- [ ] Cita en el L-414 (Open Lab) para probar el hardware con el código del docente — **C** · 12/11
- [ ] Análisis de energía de las cajas (18650, regulador, consumo por nodo) — **C** · 12/11
- [ ] Logotipo de sensores y procesador (verificar la entrega en Canvas) — **E** · 12/11
- [ ] Póster y presentación — **E** · 12/11
- [ ] Reporte EC3: un solo archivo (.docx y .pdf) según las pautas — **L** · 13/11
- [ ] Ensayo completo de la demo — **C** · 13/11
- [ ] 🏁 ENTREGA FINAL · Presentación y demo en vivo — **J** · 13/11
- [ ] NTP local en la laptop para que el Gateway funcione sin internet (RNF-05) — **C** · 20/11

## Gestión y transversales

- [ ] Reunión semanal de avance y actualización del tablero — **J** · 13/11
- [ ] Registro de riesgos: revisar mitigaciones cada dos semanas — **L** · 13/11
- [ ] Bitácora de mediciones y calibraciones — **L** · 20/11
