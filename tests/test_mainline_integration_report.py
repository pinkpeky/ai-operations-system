import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_mainline_report_generation_to_temp_outputs(tmp_path: Path) -> None:
    json_output = tmp_path / "mainline.json"
    md_output = tmp_path / "mainline.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_mainline_integration_report.py",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(md_output),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    report = json.loads(json_output.read_text(encoding="utf-8"))
    assert report["source_branch"] == "codex/phase-55-mainline-integration-release-candidate"
    assert report["target_branch"] == "main"
    assert "rollback_plan" in report
    assert md_output.exists()


def test_mainline_generated_reports_are_git_hygiene_forbidden() -> None:
    text = (ROOT / "scripts/check_runtime_hygiene.py").read_text(encoding="utf-8")
    assert "release/reports/mainline_integration_report.json" in text
    assert "release/reports/mainline_integration_report.md" in text
