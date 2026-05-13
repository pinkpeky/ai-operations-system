#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:9100}"
echo "[worker-client] Stopping heartbeat and runtime through local API: ${BASE_URL}"
curl -fsS -X POST "${BASE_URL}/local/heartbeat/stop" >/dev/null || true
curl -fsS -X POST "${BASE_URL}/local/runtime/stop" >/dev/null
echo "[worker-client] Stop request sent."
