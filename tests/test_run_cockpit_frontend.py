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
    assert "linkedWorkflowCandidates" in text
    assert "linkedWorkflowSource" in text
    assert "linkedWorkflowFocusState" in text
    assert "Linked workflow" in text
    assert "Workflow source" in text
    assert "Workflow focus" in text
    assert "Loading linked workflow details." in text
    assert "No workflow context found on the selected task, selected thread playbook runs, or linked artifacts." in text
    assert "Open Workflows" in text
    assert "Open Replay Center" in text
    assert "targetWorkflowRunId" in text
    assert "Replay context: Run Cockpit handoff" in text
    assert "UiLanguage" in text
    assert "languageStorageKey" in text
    assert "pageLabels" in text
    assert "uiText" in text
    assert "readUiLanguage" in text
    assert "writeUiLanguage" in text
    assert "language-switch" in text
    assert "运行驾驶舱" in text
    assert "中文" in text
    assert "English" in text
    assert "RAG 文档操作台简洁化" in text
    assert "OverviewPersona" in text
    assert "overview-command-center" in text
    assert "overview-mode-switch" in text
    assert "overview-action-grid" in text
    assert "工作站人员" in text
    assert "服务器维护" in text
    assert "工作站运行入口" in text
    assert "服务器维护入口" in text
    assert "conversation-command-center" in text
    assert "conversation-mode-grid" in text
    assert "对话运行台" in text
    assert "rag-command-center" in text
    assert "rag-flow-grid" in text
    assert "知识库操作台" in text


def test_run_cockpit_docs_track_rag_documents_slice() -> None:
    """Recovery docs should point to the active RAG documents simplification slice."""

    docs = [
        ROOT / "docs/RUN_COCKPIT_FOUNDATION.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/PROJECT_OVERVIEW.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/en/PROJECT_STATUS.md",
        ROOT / "docs/zh/PROJECT_STATUS.md",
    ]

    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "phase-60-rag-documents-simplification" in text or "RAG Documents" in text, path


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


def test_run_cockpit_phase_index_tracks_phase_60_rag_documents_slice() -> None:
    """Phase 60C should be merged and Phase 60D should be the active RAG documents slice."""

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
    assert "#32" in phase_59_lines["59B"]
    assert "phase-59-run-cockpit-workflow-handoff" in phase_59_lines["59B"]
    assert "Merged to main" in phase_59_lines["59B"]
    assert "TBD" not in phase_59_lines["59B"]
    assert "In progress" not in phase_59_lines["59B"]

    assert "59C" in phase_59_lines
    assert "#33" in phase_59_lines["59C"]
    assert "phase-59-run-cockpit-workflow-focus" in phase_59_lines["59C"]
    assert "Merged to main" in phase_59_lines["59C"]
    assert "TBD" not in phase_59_lines["59C"]
    assert "In progress" not in phase_59_lines["59C"]

    phase_60_lines = {
        line.split("|")[1].strip(): line
        for line in text.splitlines()
        if line.startswith("| 60")
    }

    assert "60A" in phase_60_lines
    assert "#34" in phase_60_lines["60A"]
    assert "phase-60-frontend-i18n-foundation" in phase_60_lines["60A"]
    assert "Merged to main" in phase_60_lines["60A"]
    assert "TBD" not in phase_60_lines["60A"]
    assert "In progress" not in phase_60_lines["60A"]

    assert "60B" in phase_60_lines
    assert "#35" in phase_60_lines["60B"]
    assert "phase-60-overview-persona-simplification" in phase_60_lines["60B"]
    assert "Merged to main" in phase_60_lines["60B"]
    assert "TBD" not in phase_60_lines["60B"]
    assert "In progress" not in phase_60_lines["60B"]

    assert "60C" in phase_60_lines
    assert "#36" in phase_60_lines["60C"]
    assert "phase-60-conversation-operator-simplification" in phase_60_lines["60C"]
    assert "Merged to main" in phase_60_lines["60C"]
    assert "TBD" not in phase_60_lines["60C"]
    assert "In progress" not in phase_60_lines["60C"]

    assert "60D" in phase_60_lines
    assert "phase-60-rag-documents-simplification" in phase_60_lines["60D"]
    assert "TBD" in phase_60_lines["60D"]
    assert "In progress" in phase_60_lines["60D"]
