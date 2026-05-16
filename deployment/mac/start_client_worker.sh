#!/usr/bin/env sh
set -eu

PROFILE="${1:-client-worker}"
CONFIG="${2:-worker_client/worker_config.yaml}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
if [ ! -f "$CONFIG" ]; then
  echo "Missing worker config: $CONFIG. Copy worker_config.example.yaml first." >&2
  exit 1
fi
echo "Starting client worker for profile: $PROFILE"
python -m worker_client.cli --config "$CONFIG" start

