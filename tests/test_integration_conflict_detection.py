import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_conflict_surface_matrix_loads() -> None:
    matrix = json.loads((ROOT / "release/integration/conflict_surface_matrix.json").read_text(encoding="utf-8"))
    risks = {item["risk"] for item in matrix["high_risk_surfaces"]}
    assert "migration sequence risk" in risks
    assert "frontend client drift risk" in risks


def test_conflict_detection_json_no_write() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/detect_integration_conflicts.py", "--json", "--no-write"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["summary"]["finding_count"] >= 3
