#!/usr/bin/env sh
set -eu

PROFILE="${1:-local-dev}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT/admin_dashboard"
echo "Starting Admin Dashboard for profile: $PROFILE"
npm install
npm run dev

