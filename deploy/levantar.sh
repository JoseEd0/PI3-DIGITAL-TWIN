#!/usr/bin/env bash
# Levanta todo el sistema en la laptop: stack del docente (Docker) + servicio del grupo + tablero.
#
#   deploy/levantar.sh            # con el simulador (datos "sim")
#   deploy/levantar.sh salon      # Gateway real con red propia (gateway_ap.ino): la laptop debe
#                                 # estar conectada a la red GEMELO-L419; ver docs/07-prueba-en-el-salon.md
#   deploy/levantar.sh ensayo     # igual que "salon" pero con el Gateway falso (datos simulados)
#   deploy/levantar.sh grupoX     # Gateway MQTT (gateway.ino del docente) del grupo indicado
#
# Requisitos: Docker Desktop abierto, deploy/.env creado (ver deploy/README.md),
# demo/servidor/.venv instalado y el tablero construido (demo/tablero: npm install && npm run build).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="$RAIZ/vendor/gemelo_iot_profesor/servidor_iot/docker-compose.yml"
SERVIDOR="$RAIZ/demo/servidor"
PYTHON="$SERVIDOR/.venv/bin/python"
LOGS="$SERVIDOR/logs"
PUERTO_GATEWAY_FALSO=8090
MODO="${1:-simulador}"

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
cd "$SERVIDOR"
mkdir -p "$LOGS"

# Procesos que acompañan al servicio (puente, Gateway falso): se cierran junto con él.
ACOMPANANTES=()
cerrar_acompanantes() {
  for pid in "${ACOMPANANTES[@]:-}"; do
    [[ -n "$pid" ]] && kill "$pid" 2>/dev/null || true
  done
}
trap cerrar_acompanantes EXIT INT TERM

arrancar() {  # arrancar <nombre-del-log> <argumentos de python...>
  local nombre="$1"; shift
  "$PYTHON" "$@" > "$LOGS/$nombre.log" 2>&1 &
  ACOMPANANTES+=("$!")
  echo "  $nombre: pid $!, log en demo/servidor/logs/$nombre.log"
}

grupo_del_aula() {
  "$PYTHON" -c "from gemelo.configuracion import cargar_gateway_ap; print(cargar_gateway_ap().grupo)"
}

case "$MODO" in
  simulador)
    exec "$PYTHON" -m gemelo --simular
    ;;
  salon)
    URL="$("$PYTHON" -c "from gemelo.configuracion import cargar_gateway_ap; print(cargar_gateway_ap().url)")"
    GRUPO="$(grupo_del_aula)"
    if curl -s -m 3 -o /dev/null "$URL/api/estado"; then
      echo "Gateway encontrado en $URL"
    else
      echo "AVISO: el Gateway no responde en $URL. ¿La laptop está conectada a la red GEMELO-L419?" >&2
      echo "       El puente sigue intentando y avisará 'online' en cuanto lo encuentre." >&2
    fi
    arrancar puente -m gemelo.puente_gateway
    "$PYTHON" -m gemelo --grupo "$GRUPO"
    ;;
  ensayo)
    arrancar gateway_falso -m gemelo.gateway_falso --puerto "$PUERTO_GATEWAY_FALSO"
    sleep 1
    # Grupo "sim": el ensayo usa datos simulados y así lo rotulan el tablero, Grafana y el log.
    arrancar puente -m gemelo.puente_gateway --url "http://localhost:$PUERTO_GATEWAY_FALSO" --grupo sim
    "$PYTHON" -m gemelo --grupo sim
    ;;
  *)
    exec "$PYTHON" -m gemelo --grupo "$MODO"
    ;;
esac
