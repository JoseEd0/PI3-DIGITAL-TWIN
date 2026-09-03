# PI3 — Campus Twin (Digital Twin, aula L-419)

Gemelo digital de un aula del campus UTEC: sensores → ESP32 → Wi-Fi/BLE → Raspberry Pi
(servidor) → dashboard web + copiloto de voz para el vigilante nocturno.
Este repo guarda **toda** la información del proyecto: idea, requerimientos, instrumentación,
código y entregables.

## Documentación

| Documento | Contenido |
|---|---|
| [docs/00-idea-principal.md](docs/00-idea-principal.md) | **Documento maestro**: problema, stakeholders, alcance, arquitectura, requisitos (NS/RF/RNF/CP), riesgos y plan S4-S14 |
| [docs/01-preformulacion.md](docs/01-preformulacion.md) | Idea, ODS, propuesta Campus Twin, requerimientos y MVP |
| [docs/02-instrumentacion-l419.md](docs/02-instrumentacion-l419.md) | BOM completo por módulo, costos (S/ 2713) y versión mínima (S/ 653) |
| [docs/data/instrumentacion-l419.csv](docs/data/instrumentacion-l419.csv) | Datos crudos del Excel de instrumentación |
| [docs/03-plan.md](docs/03-plan.md) | Plan y seguimiento: las 60 tareas del proyecto de Asana con responsable, fechas y casillas de avance |
| [modelo/README.md](modelo/README.md) | Modelo SysML en Gaphor: diagramas de requisitos y de bloques, exportación y regeneración |

Los documentos en `docs/` son la fuente de verdad. Si algo cambia (sensores, precios,
alcance), actualiza el `.md` en el mismo commit que el código.

Los identificadores de requisito (NS-x, RF-xx, RNF-xx, CP-xx) son los mismos en
`docs/00-idea-principal.md`, en el modelo SysML de `modelo/` y en las tareas del proyecto
[PI3 — Campus Twin L-419](https://app.asana.com/1/1218151758126339/project/1218156351516043)
en Asana. Si cambias un requisito, actualiza los tres.

### Seguimiento del avance

`docs/03-plan.md` es el espejo local del tablero de Asana. Cuando una tarea se termina, se
marca la casilla en ese archivo **y** se cierra la tarea en Asana; nunca solo una de las dos.
Asana manda en fechas y responsables: si algo cambia allá, se vuelve a bajar el archivo.

## Cómo trabajar en este repo

### Código

- Buenas prácticas siempre: nombres descriptivos, funciones cortas y con una sola
  responsabilidad, sin duplicación.
- Sin números mágicos: pines, umbrales, intervalos y endpoints van en constantes o archivos
  de configuración.
- Nunca hardcodear credenciales (Wi-Fi, tokens, API keys). Usar variables de entorno o un
  archivo local ignorado por git; dejar un `.example` versionado.
- Manejar errores de verdad: reintentos y timeouts en red/serial, no `except: pass`.
- Comentar el *por qué*, no el *qué*. Código autoexplicativo antes que comentarios.
- Seguir el estilo ya presente en cada carpeta antes de introducir uno nuevo.
- Firmware, backend y frontend en carpetas separadas, cada uno con su README breve.

### Commits

Conventional Commits, **en inglés**, cortos (≤ 72 caracteres en el asunto), imperativo y en
minúscula. Un commit = un cambio lógico.

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
- Nada de binarios pesados ni datasets grandes en el repo; si hace falta, guardar el CSV/MD
  derivado y documentar de dónde salió.
