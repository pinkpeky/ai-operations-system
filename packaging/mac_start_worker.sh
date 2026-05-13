#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-worker_client/worker_config.yaml}"
FORCE_REGISTER="${2:-}"
echo "[worker-client] Starting local runtime and heartbeat with config: ${CONFIG_PATH}"
if [[ "${FORCE_REGISTER}" == "--force-register" ]]; then
  python -m worker_client.cli --config "${CONFIG_PATH}" start --force-register
else
  python -m worker_client.cli --config "${CONFIG_PATH}" start
fi
