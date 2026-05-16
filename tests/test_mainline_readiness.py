import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_mainline_readiness_supports_required_flags() -> None:
    text = (ROOT / "scripts/mainline_readiness.py").read_text(encoding="utf-8")
    for flag in [
        "--profile",
        "--json",
        "--strict",
        "--offline",
        "--skip-docker",
        "--skip-build",
        "--skip-docs",
        "--skip-pytest",
        "--skip-github",
        "--skip-frontend",
        "--skip-smoke",
    ]:
        assert flag in text


def test_mainline_readiness_fast_offline_path_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/mainline_readiness.py",
            "--profile",
            "server-docker",
            "--offline",
            "--json",
            "--skip-docker",
            "--skip-build",
            "--skip-docs",
            "--skip-pytest",
            "--skip-smoke",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    checks = {item["name"]: item for item in payload["checks"]}
    assert checks["runtime-hygiene"]["blocking"] is True
    assert checks["conflict-surface-detection"]["blocking"] is False
    assert "branch-lineage" in checks


def test_mainline_readiness_documents_blocking_rules() -> None:
    text = (ROOT / "scripts/mainline_readiness.py").read_text(encoding="utf-8")
    for required in [
        "migration-continuity",
        "runtime-hygiene",
        "docs-verifier",
        "release-preflight",
        "integration-preflight",
        "api-frontend-drift",
    ]:
        assert required in text
