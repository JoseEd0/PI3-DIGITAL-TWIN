# Plan y seguimiento — Campus Twin L-419

> Espejo local del proyecto [PI3 — Campus Twin L-419](https://app.asana.com/1/1218151758126339/project/1218156351516043)
> en Asana. **Asana es la fuente de verdad** de fechas y responsables. Este archivo sirve para ver y
> avanzar el plan sin salir del repo.
> Última sincronización desde Asana: **12/11/2026**. Van **47 de 71 tareas** completadas (66 %).
> La estrategia, el diseño y el orden de trabajo están en [05-plan-cierre.md](05-plan-cierre.md).

## Calendario

| Semana | Fechas | Qué se hace |
|---|---|---|
| **S14** | 09–13/11 | **EC3:** todo el software funcionando con datos simulados y rotulados, y el reporte (viernes 13/11, 23:59) |
| **S15** | 16–20/11 | Ensamblaje de las cajas, pruebas con hardware en el L-414 e instalación en el L-419 |
| **S16** | 23–27/11 | Copiloto, ensayo y **demo final**. El 27/11 es una fecha supuesta: se ajusta cuando el curso la confirme |

Si se termina lo planificado para la S14 (las 25 tareas con fecha hasta el 13/11), el viernes el
tablero queda en **52 de 71 (≈ 73 %)**. Al 11/11 ya van 45. Lo que queda después es el trabajo con hardware y la demo
final.

## Cómo se actualiza

- Cuando se termina una tarea, se marca la casilla aquí **y** se cierra en Asana, en la misma pasada.
- Si cambian fechas o responsables, se cambian en Asana y se vuelve a bajar este archivo.
- Si cambian los requisitos, primero se actualiza [00-idea-principal.md](00-idea-principal.md) y el
  modelo SysML, y después las tareas.

Responsables: **J** = José Eduardo · **C** = Carlos Dávila · **E** = Esteban Sotomayor · **L** = Luhana Landeo.

## Historial de cambios del tablero

- **10/11, mañana.** Adopción de la arquitectura oficial del curso:
  - se reabrió "Instalación definitiva de los nodos", que estaba cerrada sin que existieran nodos;
  - se cerraron 8 tareas por trabajo que ya existía;
  - se renombraron 30 tareas para quitar el hardware antiguo;
  - se agregaron 15 tareas nuevas.
- **10/11, noche.** Limpieza con el calendario real (EC3 en S14, hardware en S15 y demo en S16):
  - **Secciones renombradas:** S7–S14 Servidor, S10–S14 API, S14 EC3, S15 Hardware, S16 Demo final y
    Pruebas.
  - **Se eliminaron 4 tareas:**
    - "CP-01 Ensayo de exactitud de energía", porque el PZEM no está en la arquitectura oficial y el
      consumo se estima por proxy;
    - "Copiloto: voz del navegador", "Briefing automático" e "Hito · Copiloto", que se unieron en
      una sola tarea de copiloto.
  - **Se cerró** "Registro de riesgos", porque la revisión está en `05-plan-cierre.md` §8.
  - **Se movieron fechas:** la demo final, el póster y el ensayo pasan a S16.
  - **Fecha de fin del proyecto:** pasa al 27/11.

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

## S7–S14 · Servidor y datos (stack del docente en la laptop)

- [x] Estudiar y documentar el firmware del docente (ESP-NOW, paquetes.h, Gateway) — **J** · 10/11
- [x] Base de datos de series temporales: InfluxDB 2.7 del docente — **J** · 10/11
- [x] Componentes: los compró el curso (OC-UTEC-004033-26) — **L** · 10/11
- [x] Servidor en la laptop: stack Docker del docente + servicios del grupo (override) — **J** · 11/11
- [x] Ingesta: datos en formato Gateway llegando a InfluxDB (Telegraf del docente) — **J** · 11/11
- [x] 🏁 Hito · Datos simulados en formato Gateway visibles en InfluxDB y Grafana — **J** · 11/11

## S10–S14 · API, reglas y dashboard

- [x] Motor de reglas y alertas configurables (sobre el simulador) — **J** · septiembre
- [x] Reporte de consumo fantasma (sobre el simulador) — **J** · septiembre
- [x] Dashboard web: estado en vivo (sobre el simulador) — **J** · septiembre
- [x] Dashboard: plano 2D del laboratorio y reporte de ahorro (sobre el simulador) — **J** · septiembre
- [x] API del grupo sobre InfluxDB: estado, condición por RA, diagnósticos y log — **J** · 12/11
- [x] CP-09 y CP-10: ensayos de API, dashboard y reglas (con datos simulados) — **J** · 10/11
- [x] 🏁 Hito · Dashboard propio con los 3 mínimos de la EC3 — **J** · 12/11

## S14 · EC3: software completo con datos simulados (09/11–13/11)

- [x] Centralizar material del curso y auditar el repo — **J** · 10/11
- [x] Integrar las ramas `jose` y `main` (incluye los diagramas de Luhana) — **J** · 10/11
- [x] RA-01..10: requisitos de alto nivel con umbrales y normas (`config/`) — **J** · 10/11
- [x] Grafos causales por RA y sus figuras — **J** · 10/11
- [x] Motor de razonamiento causal (SymCure) con pruebas por tipo de lógica — **J** · 11/11
- [x] Consumo fantasma por proxy (BH1750 + MLX90640 + horario) y consulta al docente por el PZEM (RF-10) — **J** · 12/11
- [x] Log de eventos / footprint (`events.jsonl` + InfluxDB) con exportación a CSV — **J** · 12/11
- [x] Dashboard propio: mediciones, condición por RA y causas, efectos y recomendaciones — **J** · 12/11
- [x] Gaphor en vivo leyendo InfluxDB — **J** · 12/11 (simulado: lee la API del servicio, no InfluxDB directamente)
- [x] Gaphor: migrar al hardware oficial, IBD y paquetes 04 Comportamiento y 05 Razonamiento — **J** · 12/11
- [x] Actualizar el documento maestro y el plan al hardware y la arquitectura oficiales — **J** · 10/11
- [ ] Cargar las fotos con QR de los sensores en Gaphor y en Asana — **L** · 12/11
- [x] Programa propio del grupo: nodo de gas MQ-2 (`MQ-2.ino`) que compile — **J** · 11/11
- [x] Análisis de energía de las cajas (18650, regulador, consumo por nodo) — **J** · 11/11
- [ ] Cita en el L-414 (Open Lab) para probar el hardware con el código del docente — **C** · 12/11
- [ ] Logotipo de sensores y procesador (verificar la entrega en Canvas) — **E** · 12/11
- [ ] Reporte EC3: un solo archivo (.docx y .pdf) según las pautas — **L** · 13/11

## Pruebas del sistema (simuladas en S14, físicas en S15–S16)

- [x] RF-11 y CP-11: simulador en formato Gateway con grabación y reproducción — **J** · 11/11
- [x] CP-06 Auditoría de consumo fantasma (con datos simulados) — **J** · 12/11
- [ ] CP-12 y CP-13: privacidad (MLX90640, INMP441) y energía de las cajas (18650) — **E** · 12/11
- [x] CP-14 Auditoría de costos, configuración y credenciales del repositorio — **J** · 10/11
- [ ] CP-03 Resiliencia: Gateway caído, canal ESP-NOW y operación sin internet — **C** · 20/11
- [ ] 🏁 Hito · Casos de prueba ejecutados (simulados ahora, físicos después) — **L** · 26/11

## S15 · Ensamblaje, pruebas en el L-414 e instalación (16/11–20/11)

- [ ] NTP local en la laptop para que el Gateway funcione sin internet (RNF-05) — **C** · 18/11
- [ ] Probar en el L-414 los nodos ambiente (BME280), luz (BH1750) y CO₂ (MH-Z1911A) con el código del docente — **L** · 20/11
- [ ] Conteo de personas: MLX90640 + KY-024 con el código del docente, prueba en el L-414 — **E** · 20/11
- [ ] Validar el nodo de ruido INMP441 del docente (dB, sin guardar audio) — **E** · 20/11
- [ ] CP-02 Ensayo de conteo de personas (MLX90640 + KY-024) — **E** · 20/11
- [ ] CP-07 Verificación ambiental: BME280, MH-Z1911A y BH1750 contra referencia — **L** · 20/11
- [ ] CP-08 Ensayo de eventos de puerta (KY-024) — **E** · 20/11
- [ ] Instalación de los 7 nodos en el L-419 — **C** · 20/11
- [ ] 🏁 Hito · Siete nodos probados en el L-414 — **C** · 20/11

## S16 · Copiloto, ensayo y demo final (23/11–27/11)

- [ ] Copiloto de voz PWA: briefing de ronda y consultas orales (RF-09) — **E** · 25/11
- [ ] CP-04 Ensayo del copiloto de voz — **L** · 26/11
- [ ] CP-05 Maratón de 72 h sin intervención — **L** · 26/11
- [ ] Póster y presentación — **E** · 26/11
- [ ] Ensayo completo de la demo — **C** · 26/11
- [ ] 🏁 DEMO FINAL · Presentación y demo en vivo (fecha supuesta) — **J** · 27/11

## Gestión y transversales

- [x] Registro de riesgos: revisar mitigaciones cada dos semanas — **L** · 10/11
- [ ] Bitácora de mediciones y calibraciones — **L** · 20/11
- [ ] Reunión semanal de avance y actualización del tablero — **J** · 27/11
