#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-worker_client/worker_config.yaml}"
echo "[worker-client] Installing Python requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo "[worker-client] Requirements installed. Config path: ${CONFIG_PATH}"
