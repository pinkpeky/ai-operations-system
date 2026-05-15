#!/usr/bin/env sh
set -eu

OUTPUT_DIR="${1:-release/build/server}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
TARGET="$REPO_ROOT/$OUTPUT_DIR"

echo "Building server deployment bundle at $TARGET"
rm -rf "$TARGET"
mkdir -p "$TARGET"

for path in \
  app \
  alembic \
  worker \
  worker_client \
  docs/CURRENT_RUNTIME.md \
  requirements.txt \
  Dockerfile \
  docker-compose.yml \
  alembic.ini \
  .env.example \
  release/manifest.json \
  release/version.json \
  release/env/aiops.release.env.template
do
  if [ ! -e "$REPO_ROOT/$path" ]; then
    echo "Missing bundle source: $path" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$TARGET/$path")"
  cp -R "$REPO_ROOT/$path" "$TARGET/$path"
done

echo "Server bundle complete. This is not a production HA package."

