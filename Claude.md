# PI3 — Campus Twin (gemelo digital del aula L-419)

Proyecto del curso PI3 (UTEC 2026-2), **Sección 8, Grupo 1**. Docente: J. F. Figueroa.
Gemelo digital del aula L-419 sobre la **arquitectura oficial del curso**:

```
7 nodos ESP32 + sensor ──ESP-NOW──► Gateway ESP32 ──Wi-Fi/MQTT──► laptop con Docker
(Mosquitto → Telegraf → InfluxDB → Grafana) + servicios del grupo (motor causal, dashboard,
log de eventos, consumo fantasma, simulador, Gaphor en vivo, copiloto de voz)
```

**Al grupo no le tocó caja.** Su aporte es la integración: el estado del salón frente a los
requisitos, el diagnóstico causal, la interfaz y el gemelo en Gaphor. Además programa un .ino
propio: el nodo MQ-2.
**Fechas:** la EC3 y la entrega final con demo son el **viernes 13/11/2026 a las 23:59** (semana
14). Las pruebas con hardware real van después.

## Por dónde empezar

| Documento | Contenido |
|---|---|
| [docs/05-plan-cierre.md](docs/05-plan-cierre.md) | **Qué se hace hasta el 13/11 y después**: decisiones, orden de trabajo y mapa de la EC3 |
| [docs/AUDITORIA.md](docs/AUDITORIA.md) | Qué existe y qué no: código del docente, trabajo propio y Asana. Incluye las correcciones al brief |
| [docs/CONTRATO_DATOS.md](docs/CONTRATO_DATOS.md) | Paquetes ESP-NOW, tópicos y JSON del Gateway, measurements de InfluxDB y bits de anomalía |
| [docs/curso/README.md](docs/curso/README.md) | Material del docente y reportes entregados: qué sirve para qué. El texto de cada uno está en `docs/curso/texto/` |
| [docs/curso/brief-ec3.md](docs/curso/brief-ec3.md) | Brief de la EC3 (v3): requisitos RA, grafos, dashboard, Gaphor y estructura del reporte |
| [docs/00-idea-principal.md](docs/00-idea-principal.md) | Documento maestro: problema, stakeholders, requisitos NS/RF/RNF/CP, RA-01..10 con sus grafos, y riesgos, sobre la arquitectura oficial (migrado el 10/11) |
| [docs/01-preformulacion.md](docs/01-preformulacion.md) | Histórico: la idea original |
| [docs/02-instrumentacion-l419.md](docs/02-instrumentacion-l419.md) | Instrumentación oficial: los 7 nodos, el Gateway, la laptop y el hardware que compró el curso ([lista](docs/curso/texto/lista-de-compra.md)). El BOM propio de S/ 2808 queda al final como histórico |
| [docs/03-plan.md](docs/03-plan.md) | Espejo local de Asana: 71 tareas con responsable, fecha y casilla |
| [docs/04-demo.md](docs/04-demo.md) | La demo simulada de septiembre (arquitectura anterior) |
| [modelo/README.md](modelo/README.md) | Modelo SysML en Gaphor: diagramas, exportación y regeneración |
| [demo/README.md](demo/README.md) | Cómo levantar el simulador, el tablero y el modelo en vivo |
| [vendor/README.md](vendor/README.md) | Código oficial del docente y sus reglas |

## Reglas del proyecto

### Honestidad

- Todo resultado se rotula como **real** (medido con hardware), **simulado** (datos del
  simulador) o **pendiente**. Nunca se inventan mediciones ni resultados de pruebas físicas.
  Hoy **no hay ninguna medición real**.
- El firmware de los nodos, el Gateway y el stack del servidor son **del docente**. Se reutilizan y
  se integran, y así se citan. Como aporte del grupo solo se presenta lo que el grupo hizo.
- Asana refleja lo que realmente pasó. Una tarea se cierra cuando el entregable existe, y en la nota
  se dice si fue sobre datos simulados.

### Arquitectura y datos

- **El formato lo define el Gateway del docente** ([docs/CONTRATO_DATOS.md](docs/CONTRATO_DATOS.md)).
  El simulador y todos los servicios del grupo lo respetan al pie de la letra.
- Los datos simulados van en el grupo `sim` (`utec/gemelo/sim/nodo<id>/<tipo>`). Los datos propios
  del grupo (diagnósticos, eventos) van en tópicos o measurements nuevos. **Nunca se cambian los
  tópicos ni los campos del Gateway.**
- Los servicios del grupo se agregan con un `docker-compose.override.yml`, sin tocar el del docente.
- El contrato viejo de la demo (`l419/<nodo>/<magnitud>`) queda reemplazado por este.

### Requisitos y trazabilidad

Los identificadores son los mismos en `docs/00-idea-principal.md`, en el modelo de `modelo/` y en
las tareas de [Asana](https://app.asana.com/1/1218151758126339/project/1218156351516043):

- **NS-1..7**: necesidades de los stakeholders;
- **RF-01..13**: requisitos funcionales;
- **RNF-01..08**: requisitos no funcionales;
- **CP-01..15**: casos de prueba;
- **RA-01..10**: requisitos de alto nivel de condición del salón, nuevos para la EC3. Cada uno tiene
  su propio grafo causal.

Si cambias un requisito, actualiza los tres lugares. Los umbrales de los RA se alinean con los del
código del docente cuando existen. El modelo se regenera con `modelo/tools/build_model.py`.

### Seguimiento del avance

`docs/03-plan.md` es el espejo local del tablero de Asana. Cuando una tarea se termina, se marca la
casilla en ese archivo **y** se cierra la tarea en Asana; nunca solo una de las dos. Asana manda en
fechas y responsables: si algo cambia allá, se vuelve a bajar el archivo. El plan de Asana es el
gratuito: no admite fecha de inicio ni proyectos públicos.

Responsables: **J** José Eduardo Huamani (administra Asana: servidor, API, reglas, dashboard e
integración), **C** Carlos Dávila (red, firmware, energía y ensayo de la demo), **E** Esteban
Sotomayor (ocupación y puerta, RA y grafos, copiloto y presentación), **L** Luhana Landeo (SysML,
documentación, pruebas y reporte).

## Cómo trabajar en este repo

### Código

- El código y los comentarios van en español, igual que la documentación. Los identificadores
  de dominio también (`consumo_fantasma`, no `ghost_consumption`).
- Buenas prácticas siempre: nombres descriptivos, funciones cortas y con una sola
  responsabilidad, sin duplicación.
- Sin números mágicos: pines, umbrales, intervalos y endpoints van en constantes o en archivos de
  configuración. Los umbrales de los RA van en `config/`.
- Nunca hardcodear credenciales (Wi-Fi, tokens, API keys). Usar variables de entorno o un archivo
  local ignorado por git, y dejar un `.example` versionado.
- Manejar errores de verdad: reintentos y timeouts en red y serial, nunca `except: pass`.
- Comentar el *por qué*, no el *qué*. Código autoexplicativo antes que comentarios.
- Seguir el estilo de cada carpeta antes de introducir uno nuevo.
- Firmware, backend y frontend en carpetas separadas, cada una con su README breve.
- Lo que se toca en `demo/` se prueba antes de darlo por terminado:
  `cd demo/servidor && .venv/bin/python -m pytest`.

### Carpetas con reglas propias

- **`vendor/gemelo_iot_profesor/`** es el código del docente y **no se modifica**. Lo que se adapte
  va en una carpeta propia y se cita como derivado. `servidor_iot/.env` y `gateway/gateway.ino`
  traen credenciales: están en `.gitignore` y se versionan sus `.example`. Nunca se copian
  credenciales al reporte, a Asana ni a un commit.
- **`docs/curso/`**: los originales del curso (`originales/`) no se versionan. Se versiona el texto
  extraído (`texto/`) y las fotos reducidas (`imagenes/`).
- **`config/`** es la única fuente de datos del aula y de los umbrales:
  - `aula_l419.yaml`: cada valor lleva `supuesto` y `fuente`. Cuando se mide algo en el aula, se
    cambia aquí y nada más;
  - `requisitos_ra.yaml`: RA-01..10 con su evaluador, sus umbrales y su norma;
  - `nodos.yaml`: los 7 nodos y la fuente de datos (`grupo`).
- **`grafos/`** tiene un YAML por RA, con el formato que explica `grafos/README.md`. Las figuras de
  `grafos/figuras/` se regeneran con `python -m gemelo.figuras`.
- **`demo/servidor/gemelo/`** es el servicio actual (EC3): sigue el contrato oficial, corre el
  motor SymCure, lleva el log y sirve la API. **`demo/tablero/`** es su dashboard.
  `deploy/levantar.sh` levanta todo con un comando.
- **`demo/`**, además, guarda el sistema simulado de septiembre: `servidor/campus_twin_demo/`,
  `frontend/` y `gaphor-vivo/`. Es histórico y se conserva con sus pruebas.
  - Umbrales, periodos, tarifa y horario viven en `configuracion.py`.
  - El enlace con Gaphor solo puede usar la biblioteca estándar, porque corre en el intérprete de
    Gaphor, que no tiene pip.
  - `modelo/campus-twin-l419.gaphor` no se modifica desde la demo: el lanzador trabaja sobre una
    copia ignorada por git.

### Commits

Conventional Commits, **en inglés**, cortos (≤ 72 caracteres en el asunto), en imperativo y en
minúscula. Un commit es un cambio lógico.

```
feat(dashboard): add energy consumption chart
fix(esp32): handle wifi reconnection timeout
docs: add L-419 instrumentation list
chore: add gitignore
refactor(api): extract sensor reader
```

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`.

### Atribución

Los commits y PRs llevan **solo** al autor humano. No agregar `Co-Authored-By: Claude`, ni
`Generated with Claude Code`, ni ninguna referencia a asistentes de IA en mensajes de commit,
descripciones de PR o comentarios de código.

### Git

- No commitear ni pushear sin que se pida explícitamente.
- Nada de binarios pesados ni datasets grandes en el repo. Si hace falta, guardar el CSV o MD
  derivado y documentar de dónde salió.
- La rama de trabajo es `jose`. Desde el 10/11 `main` sigue a `jose` (se integraron los diagramas
  de Luhana): al subir, se actualizan las dos.
