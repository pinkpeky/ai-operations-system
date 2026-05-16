import json
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]


def test_release_preflight_static_json_mode_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/release_preflight.py",
            "--profile",
            "server-docker",
            "--json",
            "--skip-pytest",
            "--skip-build",
            "--skip-docker",
            "--skip-docs",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    names = {check["name"] for check in payload["checks"]}
    assert "release-packaging-validator" in names
    assert "runtime-hygiene" in names
    assert "migration-continuity" in names


def test_release_preflight_supports_required_flags() -> None:
    text = (ROOT / "scripts/release_preflight.py").read_text(encoding="utf-8")
    for flag in ["--profile", "--json", "--strict", "--skip-docker", "--skip-build", "--skip-docs"]:
        assert flag in text


def test_release_preflight_uses_npm_cmd_on_windows(monkeypatch) -> None:
    spec = importlib.util.spec_from_file_location("release_preflight", ROOT / "scripts/release_preflight.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["release_preflight"] = module
    spec.loader.exec_module(module)

    captured: dict[str, list[str]] = {}

    def fake_run(command: list[str], **_: object) -> SimpleNamespace:
        captured["command"] = command
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    check = module.run_command("npm-build", ["npm", "run", "build"])

    assert check.status == "PASS"
    assert captured["command"][0] == "npm.cmd"
