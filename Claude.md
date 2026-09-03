# PI3 — Campus Twin (Digital Twin, aula L-419)

Gemelo digital de un aula del campus UTEC: sensores → ESP32 → Wi-Fi/BLE → Raspberry Pi
(servidor) → dashboard web + copiloto de voz para el vigilante nocturno.
Este repo guarda **toda** la información del proyecto: idea, requerimientos, instrumentación,
código y entregables.

## Documentación

| Documento | Contenido |
|---|---|
| [docs/01-preformulacion.md](docs/01-preformulacion.md) | Idea, ODS, propuesta Campus Twin, requerimientos y MVP |
| [docs/02-instrumentacion-l419.md](docs/02-instrumentacion-l419.md) | BOM completo por módulo, costos (S/ 2713) y versión mínima (S/ 653) |
| [docs/data/instrumentacion-l419.csv](docs/data/instrumentacion-l419.csv) | Datos crudos del Excel de instrumentación |

Los documentos en `docs/` son la fuente de verdad. Si algo cambia (sensores, precios,
alcance), actualiza el `.md` en el mismo commit que el código.

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
