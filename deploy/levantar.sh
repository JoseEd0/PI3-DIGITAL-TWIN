#!/usr/bin/env bash
# Levanta todo el sistema en la laptop: stack del docente (Docker) + servicio del grupo + tablero.
#
#   deploy/levantar.sh            # con el simulador (datos "sim")
#   deploy/levantar.sh grupoX     # leyendo el Gateway real del grupo indicado, sin simulador
#
# Requisitos: Docker Desktop abierto, deploy/.env creado (ver deploy/README.md),
# demo/servidor/.venv instalado y el tablero construido (demo/tablero: npm install && npm run build).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="$RAIZ/vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml"

if [[ ! -f "$RAIZ/deploy/.env" ]]; then
  echo "Falta deploy/.env: cópialo de deploy/.env.example y pon claves propias." >&2
  exit 1
fi
docker compose -p campustwin --env-file "$RAIZ/deploy/.env" -f "$COMPOSE" \
  -f "$RAIZ/deploy/docker-compose.override.yml" up -d

if [[ ! -f "$RAIZ/demo/tablero/dist/index.html" ]]; then
  (cd "$RAIZ/demo/tablero" && npm install && npm run build)
fi

set -a; source "$RAIZ/deploy/.env"; set +a
cd "$RAIZ/demo/servidor"
if [[ $# -ge 1 ]]; then
  exec .venv/bin/python -m gemelo --grupo "$1"
fi
exec .venv/bin/python -m gemelo --simular
