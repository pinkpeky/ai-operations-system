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


def test_migration_continuity_parses_phase_61m_head() -> None:
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

    phase_61i = (
        ROOT / "alembic/versions/20260520_0043_phase61i_commercial_operation_execution_runs.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0043_phase61i_exec_runs\"" in phase_61i
    assert "down_revision = \"0042_phase61h_exec_requests\"" in phase_61i

    phase_61j = (
        ROOT / "alembic/versions/20260520_0044_phase61j_commercial_operation_results.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0044_phase61j_results\"" in phase_61j
    assert "down_revision = \"0043_phase61i_exec_runs\"" in phase_61j

    phase_61k = (
        ROOT / "alembic/versions/20260520_0045_phase61k_commercial_operation_monitoring_observations.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0045_phase61k_observations\"" in phase_61k
    assert "down_revision = \"0044_phase61j_results\"" in phase_61k

    phase_61l = (
        ROOT / "alembic/versions/20260520_0046_phase61l_commercial_operation_optimization_decisions.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0046_phase61l_opt_decisions\"" in phase_61l
    assert "down_revision = \"0045_phase61k_observations\"" in phase_61l

    phase_61m = (
        ROOT / "alembic/versions/20260520_0047_phase61m_commercial_operation_evidence_snapshots.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0047_phase61m_evidence_snapshots\"" in phase_61m
    assert "down_revision = \"0046_phase61l_opt_decisions\"" in phase_61m

    phase_61q = (
        ROOT / "alembic/versions/20260520_0048_phase61q_commercial_operation_comfyui_handoffs.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0048_phase61q_comfyui_handoff\"" in phase_61q
    assert "down_revision = \"0047_phase61m_evidence_snapshots\"" in phase_61q

    phase_61r = (
        ROOT / "alembic/versions/20260520_0049_phase61r_commercial_operation_comfyui_preflights.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0049_phase61r_comfyui_preflights\"" in phase_61r
    assert "down_revision = \"0048_phase61q_comfyui_handoff\"" in phase_61r

    phase_61s = (
        ROOT / "alembic/versions/20260520_0050_phase61s_commercial_operation_comfyui_adapter_configs.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0050_phase61s_comfyui_configs\"" in phase_61s
    assert "down_revision = \"0049_phase61r_comfyui_preflights\"" in phase_61s

    phase_61t = (
        ROOT / "alembic/versions/20260520_0051_phase61t_commercial_operation_comfyui_job_requests.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0051_phase61t_comfyui_jobs\"" in phase_61t
    assert "down_revision = \"0050_phase61s_comfyui_configs\"" in phase_61t

    phase_61u = (
        ROOT / "alembic/versions/20260521_0052_phase61u_commercial_operation_comfyui_execution_plans.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0052_phase61u_comfyui_plans\"" in phase_61u
    assert "down_revision = \"0051_phase61t_comfyui_jobs\"" in phase_61u

    phase_61v = (
        ROOT / "alembic/versions/20260521_0053_phase61v_commercial_operation_comfyui_connection_probes.py"
    ).read_text(encoding="utf-8")
    assert "revision = \"0053_phase61v_comfyui_probes\"" in phase_61v
    assert "down_revision = \"0052_phase61u_comfyui_plans\"" in phase_61v


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
