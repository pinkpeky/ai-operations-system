#!/usr/bin/env sh
set -eu

PROFILE="${1:-client-worker}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT/worker_console"
echo "Starting Worker Console for profile: $PROFILE"
npm install
npm run dev

