#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.dev.yml"
ENV_FILE="${1:-$REPO_ROOT/.env.dev}"
NO_CACHE=${NO_CACHE:-0}

if [[ ! -f "$ENV_FILE" ]]; then ENV_FILE="$REPO_ROOT/.env.sample"; fi

echo "[STEP] Pre-pulling base images"
for img in maven:3.9.6-eclipse-temurin-17 eclipse-temurin:17-jre node:20-alpine; do
  docker pull "$img" || true
done

echo "[STEP] Rebuilding backend"
if [[ "$NO_CACHE" == "1" ]]; then
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache backend
else
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build backend
fi

echo "[STEP] Rebuilding frontend"
if [[ "$NO_CACHE" == "1" ]]; then
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache frontend
else
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build frontend
fi

echo "[DONE] Build refreshed. Restart services if needed:"
echo "docker compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d backend frontend"