# Reporte de la EC3

El reporte se edita en **Google Docs**. Este archivo solo explica de dónde salió el primer
borrador, para poder regenerarlo si hiciera falta.

- `plantilla.html`: el texto del reporte, con la sección de Gaphor desde el 12/11/2026. Las
  figuras se marcan como `{{img:ruta|pie de figura}}`.
- `armar.py` escribe dos versiones desde la plantilla:
  - `reporte-ec3.html` incrusta las figuras (unos 6 MB, ignorado por git). Google Drive convierte
    ese HTML en un Google Doc con las imágenes.
  - [`reporte-ec3.md`](reporte-ec3.md) es la versión que GitHub muestra renderizada, con las
    figuras enlazadas desde el repositorio. Se genera; no se edita a mano.
- `seccion-gaphor.md`: la sección del gemelo en Gaphor (figuras 17 a 24) por separado. Sus
  figuras salen de `modelo/export/` y de `figuras/gaphor-en-vivo-gas.png`.
- `figuras/`: capturas del tablero con datos simulados (escenarios vacio-con-luces, gas y
  nodo-sin-bateria). Los grafos salen de `grafos/figuras/`.

```bash
python3 docs/reporte-ec3/armar.py
```

Una vez que el grupo empieza a editar el Google Doc, la versión buena es esa. La plantilla no se
vuelve a subir encima, para no perder los cambios.
