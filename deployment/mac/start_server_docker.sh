#!/usr/bin/env sh
set -eu

PROFILE="${1:-server-docker}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "Starting server Docker profile: $PROFILE"
docker compose up --build -d
echo "Next: python deployment/scripts/verify_environment.py --profile $PROFILE"

