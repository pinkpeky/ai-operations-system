import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_migration_continuity_json_mode_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_migration_continuity.py", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    names = {check["name"] for check in payload["checks"]}
    assert {"revision-ids-unique", "down-revisions-exist", "single-root", "single-head", "downgrade-functions"} <= names


def test_migration_continuity_parses_phase_49_head() -> None:
    text = (ROOT / "alembic/versions/20260515_0034_phase49_workflow_observability.py").read_text(encoding="utf-8")
    assert "revision = \"0034_phase49_workflow_obs\"" in text
    assert "down_revision = \"0033_phase48_template_governance\"" in text
