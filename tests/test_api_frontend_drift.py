import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_api_frontend_drift_checker_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_api_frontend_drift.py", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert {item["name"] for item in payload["checks"]} >= {
        "openapi-key-routes",
        "admin-dashboard-api-client",
        "worker-console-api-client",
        "desktop-console-api-client",
    }
