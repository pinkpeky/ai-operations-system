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


def test_migration_continuity_parses_phase_61b_head() -> None:
    text = (ROOT / "alembic/versions/20260519_0036_phase61b_commercial_operation_links.py").read_text(encoding="utf-8")
    assert "revision = \"0036_phase61b_commercial_links\"" in text
    assert "down_revision = \"0035_phase61a_commercial_ops\"" in text
