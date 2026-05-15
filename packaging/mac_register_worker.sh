#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-worker_client/worker_config.yaml}"
FORCE="${2:-}"
echo "[worker-client] Registering worker with config: ${CONFIG_PATH}"
if [[ "${FORCE}" == "--force" ]]; then
  python -m worker_client.cli --config "${CONFIG_PATH}" register --force
else
  python -m worker_client.cli --config "${CONFIG_PATH}" register
fi
