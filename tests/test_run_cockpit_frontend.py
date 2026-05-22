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
    assert "商业运营项目中心" in text
    assert "Commercial operations center" in text
    assert "commercial-command-center" in text
    assert "commercial-flow-grid" in text
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
    assert "rag-live-loop" in text
    assert "rag-operations-grid" in text
    assert "知识库操作台" in text
    assert "操作闭环" in text
    assert "workflow-observability-command-center" in text
    assert "workflow-observability-flow-grid" in text
    assert "workflow-trace-toolbar" in text
    assert "工作流观测台" in text


def test_run_cockpit_docs_track_commercial_operations_slice() -> None:
    """Recovery docs should point to the active ComfyUI runtime config request slice."""

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
        assert (
            "phase-62f-comfyui-config-change-requests" in text
            or "ComfyUI Runtime Configuration Change Requests" in text
            or "configuration change requests" in text
        ), path
        assert "/comfyui-runtime/health" in text, path
        assert "/comfyui-runtime/capabilities" in text, path
        assert "/comfyui-runtime/diagnostics" in text, path
        assert "/comfyui-runtime/maintenance-runbook" in text, path
        assert "/comfyui-runtime/config-change-requests" in text, path
        assert "/comfyui-runtime/diagnostic-snapshots" in text, path
        assert "config_mutation_performed" in text or "change_status" in text or "requested_changes" in text, path
        assert "comfyui-operations" in text or "dedicated Admin Dashboard ComfyUI tab" in text or "Admin Dashboard ComfyUI page" in text or "独立 ComfyUI 页签" in text, path


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


def test_run_cockpit_phase_index_tracks_phase_61_commercial_operations_slice() -> None:
    """Phase 61A-61P should be merged and Phase 62F should be the active ComfyUI config request slice."""

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
    assert "#37" in phase_60_lines["60D"]
    assert "phase-60-rag-documents-simplification" in phase_60_lines["60D"]
    assert "Merged to main" in phase_60_lines["60D"]
    assert "TBD" not in phase_60_lines["60D"]
    assert "In progress" not in phase_60_lines["60D"]

    assert "60E" in phase_60_lines
    assert "#38" in phase_60_lines["60E"]
    assert "phase-60-rag-operations-ui" in phase_60_lines["60E"]
    assert "Merged to main" in phase_60_lines["60E"]
    assert "TBD" not in phase_60_lines["60E"]
    assert "In progress" not in phase_60_lines["60E"]

    assert "60F" in phase_60_lines
    assert "#39" in phase_60_lines["60F"]
    assert "phase-60-workflow-observability-simplification" in phase_60_lines["60F"]
    assert "Merged to main" in phase_60_lines["60F"]
    assert "TBD" not in phase_60_lines["60F"]
    assert "In progress" not in phase_60_lines["60F"]

    assert "60G" in phase_60_lines
    assert "phase-60-rag-live-validation" in phase_60_lines["60G"]
    assert "#40" in phase_60_lines["60G"]
    assert "Merged to main" in phase_60_lines["60G"]
    assert "TBD" not in phase_60_lines["60G"]
    assert "In progress" not in phase_60_lines["60G"]

    phase_61_lines = {
        line.split("|")[1].strip(): line
        for line in text.splitlines()
        if line.startswith("| 61")
    }

    assert "61A" in phase_61_lines
    assert "phase-60g-closeout-61a-operations-foundation" in phase_61_lines["61A"]
    assert "Commercial Operations Foundation" in phase_61_lines["61A"]
    assert "#41" in phase_61_lines["61A"]
    assert "Merged to main" in phase_61_lines["61A"]
    assert "TBD" not in phase_61_lines["61A"]
    assert "In progress" not in phase_61_lines["61A"]

    assert "61B" in phase_61_lines
    assert "phase-61b-commercial-operation-links" in phase_61_lines["61B"]
    assert "Commercial Operation Evidence" in phase_61_lines["61B"]
    assert "#42" in phase_61_lines["61B"]
    assert "Merged to main" in phase_61_lines["61B"]
    assert "TBD" not in phase_61_lines["61B"]
    assert "In progress" not in phase_61_lines["61B"]

    assert "61C" in phase_61_lines
    assert "phase-61c-commercial-operation-approvals" in phase_61_lines["61C"]
    assert "Commercial Operation Approval" in phase_61_lines["61C"]
    assert "#43" in phase_61_lines["61C"]
    assert "Merged to main" in phase_61_lines["61C"]
    assert "TBD" not in phase_61_lines["61C"]
    assert "In progress" not in phase_61_lines["61C"]

    assert "61D" in phase_61_lines
    assert "phase-61d-commercial-operation-dry-runs" in phase_61_lines["61D"]
    assert "Commercial Operation Safe Dry-Runs" in phase_61_lines["61D"]
    assert "#44" in phase_61_lines["61D"]
    assert "Merged to main" in phase_61_lines["61D"]
    assert "TBD" not in phase_61_lines["61D"]
    assert "In progress" not in phase_61_lines["61D"]

    assert "61E" in phase_61_lines
    assert "phase-61e-commercial-operation-content-drafts" in phase_61_lines["61E"]
    assert "Commercial Operation Content Drafts" in phase_61_lines["61E"]
    assert "#45" in phase_61_lines["61E"]
    assert "Merged to main" in phase_61_lines["61E"]
    assert "TBD" not in phase_61_lines["61E"]
    assert "In progress" not in phase_61_lines["61E"]

    assert "61F" in phase_61_lines
    assert "phase-61f-commercial-operation-asset-requests" in phase_61_lines["61F"]
    assert "Commercial Operation Asset Requests" in phase_61_lines["61F"]
    assert "#46" in phase_61_lines["61F"]
    assert "Merged to main" in phase_61_lines["61F"]
    assert "TBD" not in phase_61_lines["61F"]
    assert "In progress" not in phase_61_lines["61F"]

    assert "61G" in phase_61_lines
    assert "phase-61g-commercial-operation-deliverables" in phase_61_lines["61G"]
    assert "Commercial Operation Deliverables" in phase_61_lines["61G"]
    assert "#47" in phase_61_lines["61G"]
    assert "Merged to main" in phase_61_lines["61G"]
    assert "TBD" not in phase_61_lines["61G"]
    assert "In progress" not in phase_61_lines["61G"]

    assert "61H" in phase_61_lines
    assert "phase-61h-commercial-operation-execution-requests" in phase_61_lines["61H"]
    assert "Commercial Operation Execution Requests" in phase_61_lines["61H"]
    assert "#48" in phase_61_lines["61H"]
    assert "Merged to main" in phase_61_lines["61H"]
    assert "TBD" not in phase_61_lines["61H"]
    assert "In progress" not in phase_61_lines["61H"]

    assert "61I" in phase_61_lines
    assert "phase-61i-commercial-operation-execution-runs" in phase_61_lines["61I"]
    assert "Commercial Operation Execution Runs" in phase_61_lines["61I"]
    assert "#49" in phase_61_lines["61I"]
    assert "Merged to main" in phase_61_lines["61I"]
    assert "TBD" not in phase_61_lines["61I"]
    assert "In progress" not in phase_61_lines["61I"]

    assert "61J" in phase_61_lines
    assert "phase-61j-commercial-operation-results" in phase_61_lines["61J"]
    assert "Commercial Operation Results" in phase_61_lines["61J"]
    assert "#50" in phase_61_lines["61J"]
    assert "Merged to main" in phase_61_lines["61J"]
    assert "TBD" not in phase_61_lines["61J"]
    assert "In progress" not in phase_61_lines["61J"]

    assert "61K" in phase_61_lines
    assert "phase-61k-commercial-monitoring-observations" in phase_61_lines["61K"]
    assert "Commercial Operation Monitoring Observations" in phase_61_lines["61K"]
    assert "#51" in phase_61_lines["61K"]
    assert "Merged to main" in phase_61_lines["61K"]
    assert "TBD" not in phase_61_lines["61K"]
    assert "In progress" not in phase_61_lines["61K"]

    assert "61L" in phase_61_lines
    assert "phase-61l-commercial-optimization-decisions" in phase_61_lines["61L"]
    assert "Commercial Operation Optimization Decisions" in phase_61_lines["61L"]
    assert "#52" in phase_61_lines["61L"]
    assert "Merged to main" in phase_61_lines["61L"]
    assert "TBD" not in phase_61_lines["61L"]
    assert "In progress" not in phase_61_lines["61L"]

    assert "61M" in phase_61_lines
    assert "phase-61m-commercial-evidence-snapshots" in phase_61_lines["61M"]
    assert "Commercial Operation Evidence Snapshots" in phase_61_lines["61M"]
    assert "#53" in phase_61_lines["61M"]
    assert "Merged to main" in phase_61_lines["61M"]
    assert "Draft PR" not in phase_61_lines["61M"]
    assert "TBD" not in phase_61_lines["61M"]
    assert "In progress" not in phase_61_lines["61M"]

    assert "61N" in phase_61_lines
    assert "phase-61n-commercial-rag-evidence-generation" in phase_61_lines["61N"]
    assert "Commercial Operation RAG Evidence Generation" in phase_61_lines["61N"]
    assert "#54" in phase_61_lines["61N"]
    assert "Merged to main" in phase_61_lines["61N"]
    assert "Draft PR" not in phase_61_lines["61N"]
    assert "TBD" not in phase_61_lines["61N"]
    assert "In progress" not in phase_61_lines["61N"]

    assert "61O" in phase_61_lines
    assert "phase-61o-commercial-rag-content-drafts" in phase_61_lines["61O"]
    assert "Commercial Operation RAG Content Draft Generation" in phase_61_lines["61O"]
    assert "#55" in phase_61_lines["61O"]
    assert "Merged to main" in phase_61_lines["61O"]
    assert "Draft PR" not in phase_61_lines["61O"]
    assert "TBD" not in phase_61_lines["61O"]
    assert "In progress" not in phase_61_lines["61O"]

    assert "61P" in phase_61_lines
    assert "phase-61p-commercial-rag-asset-briefs" in phase_61_lines["61P"]
    assert "Commercial Operation RAG Asset Brief Generation" in phase_61_lines["61P"]
    assert "#56" in phase_61_lines["61P"]
    assert "Merged to main" in phase_61_lines["61P"]
    assert "Draft PR" not in phase_61_lines["61P"]
    assert "TBD" not in phase_61_lines["61P"]
    assert "In progress" not in phase_61_lines["61P"]

    assert "61Q" in phase_61_lines
    assert "phase-61q-commercial-comfyui-handoffs" in phase_61_lines["61Q"]
    assert "Commercial Operation ComfyUI Handoffs" in phase_61_lines["61Q"]
    assert "#57" in phase_61_lines["61Q"]
    assert "Draft PR" in phase_61_lines["61Q"]
    assert "TBD" not in phase_61_lines["61Q"]
    assert "In progress" not in phase_61_lines["61Q"]

    assert "61R" in phase_61_lines
    assert "phase-61r-commercial-comfyui-preflight" in phase_61_lines["61R"]
    assert "Commercial Operation ComfyUI Preflights" in phase_61_lines["61R"]
    assert "#58" in phase_61_lines["61R"]
    assert "Draft PR" in phase_61_lines["61R"]
    assert "TBD" not in phase_61_lines["61R"]
    assert "In progress" not in phase_61_lines["61R"]

    assert "61S" in phase_61_lines
    assert "phase-61s-commercial-comfyui-adapter-configs" in phase_61_lines["61S"]
    assert "Commercial Operation ComfyUI Adapter Configs" in phase_61_lines["61S"]
    assert "#59" in phase_61_lines["61S"]
    assert "Draft PR" in phase_61_lines["61S"]
    assert "TBD" not in phase_61_lines["61S"]
    assert "In progress" not in phase_61_lines["61S"]

    assert "61T" in phase_61_lines
    assert "phase-61t-commercial-comfyui-job-requests" in phase_61_lines["61T"]
    assert "Commercial Operation ComfyUI Job Requests" in phase_61_lines["61T"]
    assert "#60" in phase_61_lines["61T"]
    assert "Draft PR" in phase_61_lines["61T"]
    assert "TBD" not in phase_61_lines["61T"]
    assert "In progress" not in phase_61_lines["61T"]

    assert "61U" in phase_61_lines
    assert "phase-61u-commercial-comfyui-execution-plans" in phase_61_lines["61U"]
    assert "Commercial Operation ComfyUI Execution Plans" in phase_61_lines["61U"]
    assert "#61" in phase_61_lines["61U"]
    assert "Draft PR" in phase_61_lines["61U"]
    assert "TBD" not in phase_61_lines["61U"]
    assert "In progress" not in phase_61_lines["61U"]

    assert "61V" in phase_61_lines
    assert "phase-61v-commercial-comfyui-connection-probes" in phase_61_lines["61V"]
    assert "Commercial Operation ComfyUI Connection Probes" in phase_61_lines["61V"]
    assert "#62" in phase_61_lines["61V"]
    assert "Draft PR" in phase_61_lines["61V"]
    assert "TBD" not in phase_61_lines["61V"]
    assert "In progress" not in phase_61_lines["61V"]

    assert "61W" in phase_61_lines
    assert "phase-61w-commercial-comfyui-adapter-dispatches" in phase_61_lines["61W"]
    assert "Commercial Operation ComfyUI Adapter Dispatches" in phase_61_lines["61W"]
    assert "#63" in phase_61_lines["61W"]
    assert "Draft PR" in phase_61_lines["61W"]
    assert "TBD" not in phase_61_lines["61W"]
    assert "In progress" not in phase_61_lines["61W"]

    assert "61X" in phase_61_lines
    assert "phase-61x-commercial-comfyui-runtime-gates" in phase_61_lines["61X"]
    assert "Commercial Operation ComfyUI Runtime Gates" in phase_61_lines["61X"]
    assert "#64" in phase_61_lines["61X"]
    assert "Draft PR" in phase_61_lines["61X"]
    assert "TBD" not in phase_61_lines["61X"]
    assert "In progress" not in phase_61_lines["61X"]

    assert "61Y" in phase_61_lines
    assert "phase-61y-commercial-comfyui-runtime-dry-runs" in phase_61_lines["61Y"]
    assert "Commercial Operation ComfyUI Runtime Dry-Runs" in phase_61_lines["61Y"]
    assert "#65" in phase_61_lines["61Y"]
    assert "Draft PR" in phase_61_lines["61Y"]
    assert "TBD" not in phase_61_lines["61Y"]
    assert "In progress" not in phase_61_lines["61Y"]

    assert "61Z" in phase_61_lines
    assert "phase-61z-commercial-comfyui-runtime-activations" in phase_61_lines["61Z"]
    assert "Commercial Operation ComfyUI Runtime Activations" in phase_61_lines["61Z"]
    assert "#66" in phase_61_lines["61Z"]
    assert "Draft PR" in phase_61_lines["61Z"]
    assert "TBD" not in phase_61_lines["61Z"]
    assert "In progress" not in phase_61_lines["61Z"]

    phase_62_lines = {
        line.split("|")[1].strip(): line
        for line in text.splitlines()
        if line.startswith("| 62")
    }

    assert "62A" in phase_62_lines
    assert "phase-62a-comfyui-runtime-adapter-contract" in phase_62_lines["62A"]
    assert "ComfyUI Runtime Adapter Contract" in phase_62_lines["62A"]
    assert "/api/v1/comfyui-runtime/health" in phase_62_lines["62A"]
    assert "/api/v1/comfyui-runtime/capabilities" in phase_62_lines["62A"]
    assert "#67" in phase_62_lines["62A"]
    assert "Draft PR" in phase_62_lines["62A"]
    assert "TBD" not in phase_62_lines["62A"]
    assert "In progress" not in phase_62_lines["62A"]

    assert "62B" in phase_62_lines
    assert "phase-62b-comfyui-guarded-readonly-probe" in phase_62_lines["62B"]
    assert "ComfyUI Guarded Read-Only Probe" in phase_62_lines["62B"]
    assert "COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED" in phase_62_lines["62B"]
    assert "COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS" in phase_62_lines["62B"]
    assert "#68" in phase_62_lines["62B"]
    assert "Draft PR" in phase_62_lines["62B"]
    assert "TBD" not in phase_62_lines["62B"]
    assert "In progress" not in phase_62_lines["62B"]

    assert "62C" in phase_62_lines
    assert "phase-62c-comfyui-runtime-diagnostics" in phase_62_lines["62C"]
    assert "ComfyUI Runtime Diagnostics" in phase_62_lines["62C"]
    assert "/api/v1/comfyui-runtime/diagnostics" in phase_62_lines["62C"]
    assert "readiness_status" in phase_62_lines["62C"]
    assert "#69" in phase_62_lines["62C"]
    assert "Draft PR" in phase_62_lines["62C"]
    assert "TBD" not in phase_62_lines["62C"]
    assert "In progress" not in phase_62_lines["62C"]

    assert "62D" in phase_62_lines
    assert "phase-62d-comfyui-runtime-diagnostic-snapshots" in phase_62_lines["62D"]
    assert "ComfyUI Runtime Diagnostic Snapshots" in phase_62_lines["62D"]
    assert "/api/v1/comfyui-runtime/diagnostic-snapshots" in phase_62_lines["62D"]
    assert "comfyui_runtime_diagnostic_snapshots" in phase_62_lines["62D"]
    assert "#70" in phase_62_lines["62D"]
    assert "Draft PR" in phase_62_lines["62D"]
    assert "TBD" not in phase_62_lines["62D"]
    assert "In progress" not in phase_62_lines["62D"]

    assert "62E" in phase_62_lines
    assert "phase-62e-comfyui-maintenance-console" in phase_62_lines["62E"]
    assert "ComfyUI Runtime Maintenance Runbook" in phase_62_lines["62E"]
    assert "/api/v1/comfyui-runtime/maintenance-runbook" in phase_62_lines["62E"]
    assert "next_operator_action" in phase_62_lines["62E"]
    assert "#71" in phase_62_lines["62E"]
    assert "Draft PR" in phase_62_lines["62E"]
    assert "TBD" not in phase_62_lines["62E"]
    assert "In progress" not in phase_62_lines["62E"]

    assert "62F" in phase_62_lines
    assert "phase-62f-comfyui-config-change-requests" in phase_62_lines["62F"]
    assert "ComfyUI Runtime Configuration Change Requests" in phase_62_lines["62F"]
    assert "/api/v1/comfyui-runtime/config-change-requests" in phase_62_lines["62F"]
    assert "comfyui_runtime_config_change_requests" in phase_62_lines["62F"]
    assert "config_mutation_performed" in phase_62_lines["62F"]
    assert "#72" in phase_62_lines["62F"]
    assert "Draft PR" in phase_62_lines["62F"]
    assert "TBD" not in phase_62_lines["62F"]
    assert "In progress" not in phase_62_lines["62F"]
