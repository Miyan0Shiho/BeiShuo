#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.dev.yml"
ENV_FILE="${1:-$REPO_ROOT/.env.dev}"

if [[ ! -f "$ENV_FILE" ]]; then ENV_FILE="$REPO_ROOT/.env.sample"; fi

echo "[STEP] Stopping services backend & frontend"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down

echo "[DONE] Services stopped"