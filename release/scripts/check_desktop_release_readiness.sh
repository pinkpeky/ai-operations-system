#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
DESKTOP_ROOT="$REPO_ROOT/worker_console_desktop"
TAURI_CONFIG="$DESKTOP_ROOT/src-tauri/tauri.conf.json"
ICON="$DESKTOP_ROOT/src-tauri/icons/icon.ico"
PACKAGE_JSON="$DESKTOP_ROOT/package.json"

echo "Checking Worker Console Desktop release readiness"
for path in "$TAURI_CONFIG" "$ICON" "$PACKAGE_JSON"; do
  if [ ! -f "$path" ]; then
    echo "Missing desktop readiness file: $path" >&2
    exit 1
  fi
done

if [ ! -s "$ICON" ]; then
  echo "Desktop icon is empty: $ICON" >&2
  exit 1
fi

if ! grep -q '"icons/icon.ico"' "$TAURI_CONFIG"; then
  echo "tauri.conf.json bundle.icon must include icons/icon.ico" >&2
  exit 1
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "WARNING: cargo not found. Native Tauri release build is pending until Rust and platform toolchain are installed."
else
  echo "cargo found: $(command -v cargo)"
fi

echo "Desktop release readiness checks complete. This does not sign or package an installer."

