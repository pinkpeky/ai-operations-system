#!/usr/bin/env sh
set -eu

OUTPUT_DIR="${1:-release/build/frontends}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
TARGET="$REPO_ROOT/$OUTPUT_DIR"

mkdir -p "$TARGET"

for frontend in admin_dashboard worker_console worker_console_desktop; do
  echo "Building $frontend"
  cd "$REPO_ROOT/$frontend"
  npm install
  npm run build
  if [ ! -d "$REPO_ROOT/$frontend/dist" ]; then
    echo "Missing frontend dist: $frontend/dist" >&2
    exit 1
  fi
  rm -rf "$TARGET/$frontend"
  cp -R "$REPO_ROOT/$frontend/dist" "$TARGET/$frontend"
done

echo "Frontend build bundles complete."

