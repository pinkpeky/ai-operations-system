import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_integration_preflight_supports_required_flags() -> None:
    text = (ROOT / "scripts/integration_preflight.py").read_text(encoding="utf-8")
    for flag in [
        "--from-phase",
        "--to-phase",
        "--profile",
        "--json",
        "--strict",
        "--skip-docker",
        "--skip-build",
        "--skip-docs",
        "--skip-pytest",
        "--skip-github",
        "--offline",
    ]:
        assert flag in text


def test_integration_preflight_fast_json_path_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/integration_preflight.py",
            "--profile",
            "server-docker",
            "--json",
            "--skip-pytest",
            "--skip-build",
            "--skip-docker",
            "--skip-docs",
            "--offline",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert {item["name"] for item in payload["checks"]} >= {
        "release-preflight",
        "release-smoke-matrix",
        "api-frontend-drift",
        "pr-chain-inventory",
        "conflict-surface-detection",
    }
