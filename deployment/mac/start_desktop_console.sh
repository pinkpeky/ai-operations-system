#!/usr/bin/env sh
set -eu

PROFILE="${1:-desktop-client}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT/worker_console_desktop"
echo "Starting Worker Console Desktop for profile: $PROFILE"
echo "This controls only the worker runtime on this local machine."
npm install
npm run tauri dev

