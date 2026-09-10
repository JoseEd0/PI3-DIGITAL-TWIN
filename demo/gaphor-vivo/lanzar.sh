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

echo "Preparando la copia de demostración..."
MODELO="$MODELO" COPIA="$COPIA" "$GAPHOR" exec "$AQUI/preparar_modelo.py"

echo "Abriendo Gaphor. Cierra la ventana para terminar."
MODELO_DEMO="$COPIA" API="$API" PERIODO="$PERIODO" "$GAPHOR" exec "$AQUI/campus_twin_vivo.py"
