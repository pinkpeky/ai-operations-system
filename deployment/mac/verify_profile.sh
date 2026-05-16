#!/usr/bin/env sh
set -eu

PROFILE="${1:-server-docker}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
python deployment/scripts/check_dependencies.py --profile "$PROFILE"
python deployment/scripts/check_ports.py --profile "$PROFILE"
python deployment/scripts/verify_environment.py --profile "$PROFILE"

