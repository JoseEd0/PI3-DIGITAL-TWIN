# Plan y seguimiento — Campus Twin L-419

> Espejo local del proyecto [PI3 — Campus Twin L-419](https://app.asana.com/1/1218151758126339/project/1218156351516043)
> en Asana. **Asana es la fuente de verdad** de fechas y responsables; este archivo existe para
> ver y avanzar el plan sin salir del repo.
> Última sincronización: **03/09/2026** · 6 de 60 tareas completadas.

## Cómo se actualiza

- Dile a Claude *"ya terminamos el nodo de energía"* y él marca la casilla aquí **y** cierra la
  tarea en Asana en la misma pasada.
- O marca la casilla a mano y pídele que sincronice: lo que esté con `[x]` aquí lo cierra allá.
- Si cambian fechas o responsables, se cambian en Asana y se vuelve a bajar este archivo, para
  que no queden dos verdades distintas.

Los identificadores entre paréntesis son los del documento maestro
([00-idea-principal.md](00-idea-principal.md)) y del modelo SysML.

## Estado por fase

| Fase | Fechas | Tareas | Estado |
|---|---|---|---|
| S4 · Formulación y modelado | 31/08–06/09 | 7 | 6 hechas, falta el hito |
| S5–S6 · Especificación, permisos y compras | 07/09–20/09 | 10 | pendiente |
| S7 · Firmware base y servidor | 21/09–27/09 | 5 | pendiente |
| S8–S9 · Integración de nodos | 28/09–11/10 | 10 | pendiente |
| S10–S11 · API, reglas y dashboard | 12/10–25/10 | 7 | pendiente |
| S12 · Copiloto de voz | 26/10–01/11 | 6 | pendiente |
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

## S5–S6 · Especificación, permisos y compras (07/09–20/09)

- [ ] Entrevistar a los stakeholders del laboratorio — **L** · 07/09 → 11/09
- [ ] Cerrar permiso de instalación con Servicios Generales (RNF-01) — **L** · 07/09 → 11/09
- [ ] Definir con TI el acceso de los nodos a la red (RNF-05) — **C** · 07/09 → 11/09
- [ ] Definir horario oficial del L-419 y umbrales de alerta (RF-08) — **E** · 09/09 → 11/09
- [ ] Cerrar cotización final y orden de compra (RNF-03) — **L** · 11/09 → 14/09
- [ ] Comprar y recibir componentes — **L** · 14/09 → 18/09
- [ ] Armar banco de pruebas y verificar cada sensor por separado — **C** · 16/09 → 20/09
- [ ] Definir el contrato de datos: tópicos MQTT, esquema y unidades (RF-05, RF-06) — **J** · 14/09 → 18/09
- [ ] Levantar la estructura del repositorio (RNF-07) — **J** · 14/09 → 17/09
- [ ] 🏁 **Hito S6** · Componentes en mano y contrato de datos definido — **L** · 18/09

## S7 · Firmware base y servidor (21/09–27/09)

- [ ] Firmware base ESP32: Wi-Fi con reconexión, MQTT y buffer local (RF-05) — **C** · 21/09 → 25/09
- [ ] Servidor en Raspberry Pi 5: sistema, broker MQTT y arranque automático — **J** · 21/09 → 24/09
- [ ] Base de datos de series temporales con retención de 60 días (RF-06) — **J** · 24/09 → 27/09
- [ ] Ingesta a la base de datos y monitoreo de muestras perdidas — **J** · 25/09 → 27/09
- [ ] 🏁 **Hito S7** · Un nodo publicando y el servidor almacenando — **J** · 25/09

## S8–S9 · Integración de nodos (28/09–11/10)

- [ ] Nodo de energía: PZEM-004T, SCT-013 y enchufes inteligentes (RF-01) — **C** · 28/09 → 02/10
- [ ] CP-01 Ensayo de exactitud de energía — **C** · 02/10 → 03/10
- [ ] Nodo ambiental: SHT31, BH1750 y SCD41 (RF-02) — **L** · 28/09 → 02/10
- [ ] CP-07 Calibración ambiental contra instrumento patrón — **L** · 02/10 → 03/10
- [ ] Nodo de ocupación: radar LD2410C, PIR y conteo ToF en la puerta (RF-03) — **E** · 05/10 → 09/10
- [ ] CP-02 Ensayo de ocupación con personas quietas — **E** · 08/10 → 09/10
- [ ] Nodo de puerta a batería: magnético y SW-420 (RF-04, RNF-04) — **E** · 05/10 → 08/10
- [ ] CP-08 Ensayo de eventos de puerta — **E** · 09/10
- [ ] Instalación definitiva de los nodos en el L-419 (RNF-01) — **C** · 09/10 → 10/10
- [ ] 🏁 **Hito S9** · Los cuatro nodos instalados y midiendo — **C** · 09/10

## S10–S11 · API, reglas y dashboard (12/10–25/10)

- [ ] API REST de consulta por rango, magnitud y agregación (RF-06) — **J** · 12/10 → 16/10
- [ ] Motor de reglas y alertas configurables (RF-08) — **J** · 14/10 → 17/10
- [ ] Reporte de consumo fantasma (RF-10) — **J** · 16/10 → 18/10
- [ ] Dashboard web: estado en vivo con refresco de 5 s (RF-07) — **J** · 19/10 → 23/10
- [ ] Dashboard: históricos, plano 2D del laboratorio y reporte de ahorro (RF-07, RF-10) — **J** · 21/10 → 25/10
- [ ] CP-09 y CP-10: ensayos de API, dashboard y reglas de alerta — **L** · 22/10 → 24/10
- [ ] 🏁 **Hito S11** · Dashboard operativo con datos reales — **J** · 23/10

## S12 · Copiloto de voz (26/10–01/11)

- [ ] Nodo de audio: INMP441, MAX98357A y parlante — **E** · 26/10 → 28/10
- [ ] Servicio de voz: STT y TTS en español sobre la API (RF-09, RNF-02) — **E** · 26/10 → 30/10
- [ ] Briefing automático de inicio de ronda (RF-09) — **E** · 29/10 → 31/10
- [ ] Consultas orales con audífono Bluetooth (RF-09) — **E** · 30/10 → 01/11
- [ ] CP-04 Ensayo del copiloto de voz — **L** · 31/10 → 01/11
- [ ] 🏁 **Hito S12** · Copiloto de voz respondiendo en el laboratorio — **E** · 30/10

## S13 · Pruebas de sistema (02/11–08/11)

- [ ] CP-03 Ensayo de resiliencia de red (RF-05, RNF-05) — **C** · 02/11 → 03/11
- [ ] CP-05 Maratón de 72 h sin intervención (RNF-06) — **L** · 02/11 → 05/11
- [ ] RF-11 y CP-11: modo demostración con datos grabados — **J** · 03/11 → 05/11
- [ ] CP-06 Auditoría de consumo fantasma (RF-10) — **J** · 05/11 → 06/11
- [ ] CP-12 y CP-13: revisión de instalación, privacidad y autonomía (RNF-01, RNF-02, RNF-04) — **E** · 05/11 → 06/11
- [ ] CP-14 Auditoría de costos y de configuración (RNF-03, RNF-07) — **L** · 06/11 → 07/11
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
