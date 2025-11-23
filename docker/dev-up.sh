#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.dev.yml"
ENV_FILE="${1:-$REPO_ROOT/.env.dev}"

MIRRORS=(
  "https://docker.m.daocloud.io"
  "https://hub-mirror.c.163.com"
  "https://mirror.ccs.tencentyun.com"
)

function setup_registry_mirrors() {
  local daemon_json="$HOME/.docker/daemon.json"
  mkdir -p "$HOME/.docker" || true
  if [[ -f "$daemon_json" ]]; then
    cp "$daemon_json" "$daemon_json.bak.$(date +%s)"
  fi
  cat > "$daemon_json" <<JSON
{
  "registry-mirrors": [
    "${MIRRORS[0]}",
    "${MIRRORS[1]}",
    "${MIRRORS[2]}"
  ]
}
JSON
  echo "[INFO] Wrote registry mirrors to $daemon_json"
  echo "[INFO] Please restart Docker Desktop to apply mirrors (Settings → Docker Engine → Apply & Restart)"
}

if [[ "${SETUP_MIRRORS:-}" == "1" ]] || [[ "${2:-}" == "--setup-mirrors" ]]; then
  setup_registry_mirrors
fi

# Verbose mode
if [[ "${VERBOSE:-}" == "1" ]] || [[ "${2:-}" == "--verbose" ]]; then
  set -x
fi

echo "[INFO] Repo root: $REPO_ROOT"
echo "[INFO] Compose file: $COMPOSE_FILE"

if ! command -v docker &>/dev/null; then
  echo "[ERROR] Docker is not installed or not in PATH" >&2
  exit 1
fi

if ! docker info &>/dev/null; then
  echo "[ERROR] Docker daemon is not running. Please start Docker Desktop and retry." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[WARN] Env file '$ENV_FILE' not found. Falling back to '.env.sample'"
  ENV_FILE="$REPO_ROOT/.env.sample"
fi

echo "[INFO] Using env file: $ENV_FILE"

mkdir -p "$REPO_ROOT/data/faiss" || true

echo "[STEP] Pre-pulling base images (may take a few minutes)"
for img in "maven:3.9.6-eclipse-temurin-17" "eclipse-temurin:17-jre" "node:20-alpine"; do
  echo "[INFO] Pulling $img ..."
  if ! docker pull "$img"; then
    echo "[WARN] Pull failed for $img. Consider '--setup-mirrors' then restart Docker Desktop."
  fi
done

echo "[STEP] Building backend image (first time may take 3–8 minutes due to Maven deps)"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build backend

echo "[STEP] Starting backend"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d backend

echo "[STEP] Building frontend image"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build frontend

echo "[STEP] Starting frontend"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d frontend

echo "[DONE] Services started"
echo "[URL] Frontend:  http://localhost:5173"
echo "[URL] Backend:   http://localhost:8080"
echo "[TIP] View logs: docker compose -f $COMPOSE_FILE logs -f backend"
echo "[TIP] Stop:      docker compose -f $COMPOSE_FILE down"
echo "[TIP] If builds seem stuck: run 'bash docker/dev-up.sh --setup-mirrors' and restart Docker Desktop"