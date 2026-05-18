import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_generate_release_report_writes_json(tmp_path: Path) -> None:
    output = tmp_path / "release_readiness_report.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_release_report.py",
            "--profile",
            "server-docker",
            "--output",
            str(output),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    report = json.loads(output.read_text(encoding="utf-8"))
    assert payload["success"] is True
    assert report["phase"] == "56"
    assert report["baseline_phase"] == "55"
    assert report["status"] == "ci_readiness_snapshot"
    assert "mainline_state" in report
    assert "remaining_risks" in report


def test_release_report_generated_output_is_ignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "/release/reports/release_readiness_report.json" in gitignore
    assert "/release/reports/ci/" in gitignore
