#!/usr/bin/env bash
# Abre el modelo SysML en Gaphor y lo mantiene al día con el gemelo simulado.
#
#   ./lanzar.sh                    # usa http://127.0.0.1:8000
#   API=http://otra-maquina:8000 ./lanzar.sh
#
# Trabaja siempre sobre una copia: el entregable modelo/campus-twin-l419.gaphor
# no se toca, así nadie guarda lecturas simuladas dentro del modelo del curso.

set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"

GAPHOR="${GAPHOR:-/Applications/Gaphor.app/Contents/MacOS/gaphor}"
MODELO="${MODELO:-$RAIZ/modelo/campus-twin-l419.gaphor}"
COPIA="${COPIA:-$AQUI/campus-twin-l419-demo.gaphor}"
API="${API:-http://127.0.0.1:8000}"
PERIODO="${PERIODO:-1}"

if [ ! -x "$GAPHOR" ]; then
  echo "No encuentro Gaphor en $GAPHOR" >&2
  echo "Instálalo desde https://gaphor.org o exporta GAPHOR con la ruta correcta." >&2
  exit 1
fi

if [ ! -f "$MODELO" ]; then
  echo "No encuentro el modelo en $MODELO" >&2
  exit 1
fi

if ! curl -s -o /dev/null -m 3 "$API/api/estado"; then
  echo "Aviso: el servidor de la demo no responde en $API." >&2
  echo "Levántalo con: cd $RAIZ/demo/servidor && .venv/bin/python -m campus_twin_demo" >&2
  echo "Gaphor se abrirá igual y se conectará solo cuando el servidor esté listo." >&2
fi

# Gaphor guarda un diario de recuperación por sesión. Si una sesión se cerró de
# golpe, al abrir intenta recuperarla contra el modelo regenerado y falla con
# "Invalid ID for reference". Se borran solo los diarios de esta copia.
SESIONES="${XDG_CACHE_HOME:-$HOME/.cache}/gaphor/sessions"
# Sin tubería y comprobando cada archivo: con `set -e` y `pipefail`, un grep sin
# coincidencias abortaría el script antes de hacer nada.
if [ -d "$SESIONES" ]; then
  for diario in "$SESIONES"/*.recovery "$SESIONES"/*.recovery.bak; do
    [ -f "$diario" ] || continue
    if grep -qF "$COPIA" "$diario" 2>/dev/null; then
      rm -f "$diario"
    fi
  done
fi

echo "Preparando la copia de demostración..."
MODELO="$MODELO" COPIA="$COPIA" "$GAPHOR" exec "$AQUI/preparar_modelo.py"

echo "Abriendo Gaphor. Cierra la ventana para terminar."
MODELO_DEMO="$COPIA" API="$API" PERIODO="$PERIODO" "$GAPHOR" exec "$AQUI/campus_twin_vivo.py"
