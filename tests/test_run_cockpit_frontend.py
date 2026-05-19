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
    assert "DeepLinkTarget" in text
    assert "pageFromLocation" in text
    assert "targetFromLocation" in text
    assert "updateLocation" in text
    assert "targetThreadId" in text
    assert "targetTaskRunId" in text
    assert "targetArtifactId" in text
    assert "thread_id" in text
    assert "task_run_id" in text
    assert "artifact_id" in text
    assert "lastRefreshAtMs" in text
    assert "refreshClockMs" in text
    assert "Refresh state" in text
    assert "Next refresh" in text
    assert "stale data" in text
    assert "setState((current) => ({" in text
    assert "targetThreadId" in text
    assert "visibleRuns" in text
    assert "Thread context" in text
    assert "Open linked conversation" in text
    assert "Show all runs" in text
    assert "No playbook runs for linked thread." in text
    assert "targetTaskRunId" in text
    assert "visibleArtifacts" in text
    assert "Artifact context" in text
    assert "Open linked task run" in text
    assert "Show all artifacts" in text
    assert "No output artifacts for linked run context." in text
    assert "cockpitQuery" in text
    assert "filteredThreads" in text
    assert "filteredTasks" in text
    assert "filteredArtifacts" in text
    assert "Search hits" in text
    assert "Clear search" in text
    assert "No task runs match the cockpit search." in text
    assert "workflowRunId" in text
    assert "workflow_run_id" in text
    assert "linkedWorkflowRunId" in text
    assert "Linked workflow" in text
    assert "Open Workflows" in text
    assert "Open Replay Center" in text
    assert "targetWorkflowRunId" in text
    assert "Replay context: Run Cockpit handoff" in text


def test_run_cockpit_docs_track_workflow_handoff_slice() -> None:
    """Recovery docs should point to the active Run Cockpit workflow-handoff slice."""

    docs = [
        ROOT / "docs/RUN_COCKPIT_FOUNDATION.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/PROJECT_OVERVIEW.md",
        ROOT / "docs/PHASE_INDEX.md",
    ]

    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "phase-59-run-cockpit-workflow-handoff" in text or "Run Cockpit Workflow" in text, path


def test_run_cockpit_phase_index_marks_merged_slices_complete() -> None:
    """Merged run cockpit slices should not remain marked as active or missing a PR."""

    text = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    phase_lines = {
        line.split("|")[1].strip(): line
        for line in text.splitlines()
        if line.startswith("| 57") and "Run Cockpit" in line
    }

    assert "57C" in phase_lines
    assert "#24" in phase_lines["57C"]
    assert "Merged to main" in phase_lines["57C"]
    assert "TBD" not in phase_lines["57C"]
    assert "In progress" not in phase_lines["57C"]

    assert "57D" in phase_lines
    assert "#25" in phase_lines["57D"]
    assert "phase-57-run-cockpit-closeout" in phase_lines["57D"]
    assert "Merged to main" in phase_lines["57D"]
    assert "TBD" not in phase_lines["57D"]
    assert "In progress" not in phase_lines["57D"]


def test_run_cockpit_phase_index_tracks_phase_59_workflow_handoff_slice() -> None:
    """Phase 59A should be merged and Phase 59B should be the active workflow-handoff slice."""

    text = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    phase_lines = {
        line.split("|")[1].strip(): line
        for line in text.splitlines()
        if line.startswith("| 58") and "Run Cockpit" in line
    }

    assert "58A" in phase_lines
    assert "#26" in phase_lines["58A"]
    assert "phase-58-run-cockpit-deep-links" in phase_lines["58A"]
    assert "Merged to main" in phase_lines["58A"]
    assert "TBD" not in phase_lines["58A"]
    assert "In progress" not in phase_lines["58A"]

    assert "58B" in phase_lines
    assert "#27" in phase_lines["58B"]
    assert "phase-58-run-cockpit-refresh-ux" in phase_lines["58B"]
    assert "Merged to main" in phase_lines["58B"]
    assert "TBD" not in phase_lines["58B"]
    assert "In progress" not in phase_lines["58B"]

    assert "58C" in phase_lines
    assert "#28" in phase_lines["58C"]
    assert "phase-58-playbook-thread-context" in phase_lines["58C"]
    assert "Merged to main" in phase_lines["58C"]
    assert "TBD" not in phase_lines["58C"]
    assert "In progress" not in phase_lines["58C"]

    assert "58D" in phase_lines
    assert "#29" in phase_lines["58D"]
    assert "phase-58-output-library-context" in phase_lines["58D"]
    assert "Merged to main" in phase_lines["58D"]
    assert "TBD" not in phase_lines["58D"]
    assert "In progress" not in phase_lines["58D"]

    assert "58E" in phase_lines
    assert "#30" in phase_lines["58E"]
    assert "phase-58-run-cockpit-closeout" in phase_lines["58E"]
    assert "Merged to main" in phase_lines["58E"]
    assert "TBD" not in phase_lines["58E"]
    assert "In progress" not in phase_lines["58E"]

    text = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    phase_59_lines = {
        line.split("|")[1].strip(): line
        for line in text.splitlines()
        if line.startswith("| 59") and "Run Cockpit" in line
    }

    assert "59A" in phase_59_lines
    assert "#31" in phase_59_lines["59A"]
    assert "phase-59-run-cockpit-search-density" in phase_59_lines["59A"]
    assert "Merged to main" in phase_59_lines["59A"]
    assert "TBD" not in phase_59_lines["59A"]
    assert "In progress" not in phase_59_lines["59A"]

    assert "59B" in phase_59_lines
    assert "phase-59-run-cockpit-workflow-handoff" in phase_59_lines["59B"]
    assert "In progress" in phase_59_lines["59B"]
