import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_port_checker_json_mode() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "deployment/scripts/check_ports.py"),
            "--profile",
            "local-dev",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    assert payload["profile"] == "local-dev"
    assert any(check["name"] == "api" for check in payload["checks"])

