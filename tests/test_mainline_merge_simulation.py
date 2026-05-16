import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_merge_simulation_outputs_json_without_mutating_branch() -> None:
    before_branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    result = subprocess.run(
        [sys.executable, "scripts/simulate_mainline_merge.py", "--base", "main", "--head", "current", "--json", "--offline"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    after_branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    payload = json.loads(result.stdout)
    assert before_branch == after_branch
    assert payload["mutates_main"] is False
    assert "changed_file_summary" in payload
    assert "likely_superseded_prs" in payload


def test_merge_simulation_has_required_delta_categories() -> None:
    text = (ROOT / "scripts/simulate_mainline_merge.py").read_text(encoding="utf-8")
    for term in [
        "migration_delta",
        "release_deployment_delta",
        "docs_delta",
        "frontend_delta",
        "tests_delta",
    ]:
        assert term in text
