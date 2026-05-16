import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_superseded_pr_report_schema_json() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_superseded_pr_report.py", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    decisions = {item["pr"]: item for item in payload["decisions"]}
    assert 13 in decisions
    assert 14 in decisions
    assert 15 in decisions
    assert decisions[15]["recommendation"] == "keep as Phase 55 base"


def test_committed_superseded_report_covers_phase_chain() -> None:
    text = (ROOT / "release/reports/superseded_prs.md").read_text(encoding="utf-8")
    for token in ["#13", "#14", "#15", "supersede after RC accepted", "Do not close superseded PRs"]:
        assert token in text
