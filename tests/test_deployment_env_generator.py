import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_generate_env_creates_output_and_applies_overrides(tmp_path: Path) -> None:
    override = tmp_path / "override.json"
    output = tmp_path / ".env.generated"
    override.write_text(json.dumps({"API_PORT": "18000", "APP_ENV": "server-docker-test"}), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "deployment/scripts/generate_env.py"),
            "--profile",
            "server-docker",
            "--output",
            str(output),
            "--override-json",
            str(override),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "API_PORT=18000" in text
    assert "APP_ENV=server-docker-test" in text
    assert "server-docker" in result.stdout


def test_generate_env_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    output = tmp_path / ".env.generated"
    output.write_text("APP_ENV=old\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "deployment/scripts/generate_env.py"),
            "--profile",
            "local-dev",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Refusing to overwrite" in result.stderr or "Refusing to overwrite" in result.stdout

