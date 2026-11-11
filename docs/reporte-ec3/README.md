# Reporte de la EC3

El reporte se edita en **Google Docs**. Este archivo solo explica de dónde salió el primer
borrador, para poder regenerarlo si hiciera falta.

- `plantilla.html`: el texto del borrador del 11/11/2026. Las figuras se marcan como
  `{{img:ruta|pie de figura}}`.
- `armar.py`: incrusta las figuras y escribe `reporte-ec3.html`, que está ignorado por git
  (pesa unos 3.5 MB). Google Drive convierte ese HTML en un Google Doc con las imágenes.
- `figuras/`: capturas del tablero con datos simulados (escenarios vacio-con-luces, gas y
  nodo-sin-bateria). Los grafos salen de `grafos/figuras/`.

```bash
python3 docs/reporte-ec3/armar.py
```

Una vez que el grupo empieza a editar el Google Doc, la versión buena es esa. La plantilla no se
vuelve a subir encima, para no perder los cambios.
