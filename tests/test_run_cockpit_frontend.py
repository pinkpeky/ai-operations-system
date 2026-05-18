"""Run Cockpit frontend integration checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_run_cockpit_exposes_actions_and_feedback() -> None:
    """Run Cockpit should expose guarded actions without adding backend-only routes."""

    text = (ROOT / "admin_dashboard/src/main.tsx").read_text(encoding="utf-8")

    assert '"run-cockpit"' in text
    assert "mutateCockpitApproval" in text
    assert "mutateCockpitTask" in text
    assert "exportCockpitArtifact" in text
    assert "Last action result" in text
    assert "Action status" in text
    assert "Approved from Run Cockpit" in text
    assert "Manual recovery from Run Cockpit" in text
    assert "Export markdown" in text
    assert "Export JSON" in text
    assert "Task view" in text
    assert "Auto refresh" in text
    assert "Open Conversations" in text
    assert "Open Tasks" in text
    assert "Open Output Library" in text


def test_run_cockpit_docs_track_action_slice() -> None:
    """Recovery docs should point to the active Run Cockpit operator-controls slice."""

    docs = [
        ROOT / "docs/RUN_COCKPIT_FOUNDATION.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/PROJECT_OVERVIEW.md",
        ROOT / "docs/PHASE_INDEX.md",
    ]

    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "phase-57-run-cockpit-operator-controls" in text or "Run Cockpit Operator Controls" in text, path
