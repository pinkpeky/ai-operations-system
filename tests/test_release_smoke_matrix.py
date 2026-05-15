import json
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]


def test_release_smoke_matrix_files_cover_profiles_and_groups() -> None:
    smoke = json.loads((ROOT / "release/smoke/smoke_matrix.json").read_text(encoding="utf-8"))
    profiles = json.loads((ROOT / "release/smoke/profile_matrix.json").read_text(encoding="utf-8"))
    runtime = json.loads((ROOT / "release/smoke/runtime_matrix.json").read_text(encoding="utf-8"))

    assert smoke["phase"] == "53"
    assert {item["name"] for item in smoke["groups"]} >= {"static", "docs", "frontend-build", "docker-runtime", "deployment"}
    assert set(profiles["profiles"]) >= {"server-docker", "local-dev", "desktop-client", "client-worker", "staging", "production-like"}
    assert {route["path"] for route in runtime["routes"]} >= {
        "/api/v1/health",
        "/api/v1/task-runs",
        "/api/v1/output-artifacts",
        "/api/v1/workflow-templates",
    }


def test_release_smoke_matrix_static_json_mode_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/release_smoke_matrix.py",
            "--json",
            "--skip-build",
            "--skip-docker",
            "--skip-docs",
            "--group",
            "static",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert {item["name"] for item in payload["results"]} >= {
        "runtime_hygiene",
        "migration_continuity",
        "release_packaging_validator",
    }


def test_release_smoke_matrix_uses_npm_cmd_on_windows(monkeypatch) -> None:
    spec = importlib.util.spec_from_file_location("release_smoke_matrix", ROOT / "scripts/release_smoke_matrix.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["release_smoke_matrix"] = module
    spec.loader.exec_module(module)

    captured: dict[str, list[str]] = {}

    def fake_run(command: list[str], **_: object) -> SimpleNamespace:
        captured["command"] = command
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    result = module.run_command("frontend-build", "worker_console_build", ["npm", "run", "build"])

    assert result.status == "PASS"
    assert captured["command"][0] == "npm.cmd"
