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


def test_migration_continuity_parses_phase_61h_head() -> None:
    previous = (ROOT / "alembic/versions/20260519_0037_phase61c_commercial_operation_approvals.py").read_text(encoding="utf-8")
    assert "revision = \"0037_phase61c_op_approvals\"" in previous
    assert "down_revision = \"0036_phase61b_commercial_links\"" in previous

    text = (ROOT / "alembic/versions/20260519_0038_phase61d_commercial_operation_dry_runs.py").read_text(encoding="utf-8")
    assert "revision = \"0038_phase61d_op_dry_runs\"" in text
    assert "down_revision = \"0037_phase61c_op_approvals\"" in text

    head = (ROOT / "alembic/versions/20260519_0039_phase61e_commercial_operation_content_drafts.py").read_text(encoding="utf-8")
    assert "revision = \"0039_phase61e_content_drafts\"" in head
    assert "down_revision = \"0038_phase61d_op_dry_runs\"" in head

    next_head = (ROOT / "alembic/versions/20260519_0040_phase61f_commercial_operation_asset_requests.py").read_text(encoding="utf-8")
    assert "revision = \"0040_phase61f_asset_requests\"" in next_head
    assert "down_revision = \"0039_phase61e_content_drafts\"" in next_head

    phase_61g = (ROOT / "alembic/versions/20260520_0041_phase61g_commercial_operation_deliverables.py").read_text(encoding="utf-8")
    assert "revision = \"0041_phase61g_deliverables\"" in phase_61g
    assert "down_revision = \"0040_phase61f_asset_requests\"" in phase_61g

    phase_61h = (
        ROOT / "alembic/versions/20260520_0042_phase61h_commercial_operation_execution_requests.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0042_phase61h_exec_requests\"" in phase_61h
    assert "down_revision = \"0041_phase61g_deliverables\"" in phase_61h


def test_migration_revision_ids_fit_alembic_version_column() -> None:
    for path in (ROOT / "alembic/versions").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("revision = "):
                revision = line.split("\"")[1]
                assert len(revision) <= 32, f"{path.name} revision is too long for alembic_version.version_num"


def test_migration_continuity_keeps_phase_61c_revision_short() -> None:
    text = (ROOT / "alembic/versions/20260519_0037_phase61c_commercial_operation_approvals.py").read_text(encoding="utf-8")
    assert "revision = \"0037_phase61c_op_approvals\"" in text
    assert "down_revision = \"0036_phase61b_commercial_links\"" in text
