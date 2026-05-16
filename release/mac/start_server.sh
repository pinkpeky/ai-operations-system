#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if [ "${1:-}" = "--build" ]; then
  docker compose up --build -d
else
  docker compose up -d
fi

echo "AI Server started via docker compose. This is a release foundation helper, not production HA orchestration."

