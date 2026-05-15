import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_hygiene_json_mode_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_runtime_hygiene.py", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["checks"][0]["status"] == "PASS"


def test_runtime_hygiene_knows_forbidden_patterns() -> None:
    text = (ROOT / "scripts/check_runtime_hygiene.py").read_text(encoding="utf-8")
    for marker in [".env", "worker_state.json", "docs/rendered/", "node_modules", "runtime_state", "storage/output_artifacts/"]:
        assert marker in text
