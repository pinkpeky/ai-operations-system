"""Phase 62I workstation/customer client frontend UX checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_MAIN = ROOT / "worker_console/src/main.tsx"
WEB_STYLES = ROOT / "worker_console/src/styles.css"
WEB_KNOWLEDGE_CLIENT = ROOT / "worker_console/src/api/knowledgeBaseClient.ts"
WEB_COMMERCIAL_OPERATION_CLIENT = ROOT / "worker_console/src/api/commercialOperationClient.ts"
WEB_DIGITAL_HUMAN_CLIENT = ROOT / "worker_console/src/api/digitalHumanClient.ts"
DESKTOP_MAIN = ROOT / "worker_console_desktop/src/main.tsx"
DESKTOP_STYLES = ROOT / "worker_console_desktop/src/styles.css"
DESKTOP_KNOWLEDGE_CLIENT = ROOT / "worker_console_desktop/src/api/knowledgeBaseClient.ts"
DESKTOP_COMMERCIAL_OPERATION_CLIENT = ROOT / "worker_console_desktop/src/api/commercialOperationClient.ts"
DESKTOP_DIGITAL_HUMAN_CLIENT = ROOT / "worker_console_desktop/src/api/digitalHumanClient.ts"


def test_worker_console_web_exposes_phase_62i_operator_home() -> None:
    text = WEB_MAIN.read_text(encoding="utf-8")
    styles = WEB_STYLES.read_text(encoding="utf-8")

    for token in [
        "Phase 62I",
        "Workstation Operator Home",
        "工作站操作入口",
        "workerConsoleLanguage",
        "language-switch",
        "operator-status-grid",
        "operator-support-grid",
        "local Worker on the current customer machine",
        "不会直接调用 ComfyUI、OpenClaw、真实平台账号",
        'href="#approvals-panel"',
        'href="#tasks-panel"',
        'id="logs-panel"',
    ]:
        assert token in text

    for token in [
        ".operator-home",
        ".language-switch",
        ".operator-status-card",
        ".quick-link-grid",
        ".recovery-list",
    ]:
        assert token in styles


def test_worker_console_desktop_exposes_phase_62i_operator_home() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")
    styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for token in [
        "Phase 62I",
        "Customer-Machine Operator Home",
        "客户机操作入口",
        "desktopConsoleLanguage",
        "language-switch",
        "operator-status-grid",
        "operator-support-grid",
        "Use Start Runtime to launch worker_client on this machine.",
        "Desktop Console 只控制当前客户机/工作站的本机 Worker",
        'href="#approvals-panel"',
        'href="#tasks-panel"',
        'id="logs-panel"',
    ]:
        assert token in text

    for token in [
        ".operator-home",
        ".language-switch",
        ".operator-status-card",
        ".quick-link-grid",
        ".recovery-list",
    ]:
        assert token in styles


def test_phase_62i_plan_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (phase_index, current_next, project_status, en_status, zh_status, en_console, zh_console):
        assert "Phase 62I Workstation/Customer Client Frontend UX Alignment" in text
        assert "codex/phase-62i-workstation-client-ux" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "Chinese/English language switching" in text


def test_worker_consoles_expose_phase_62k_codex_like_surface() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "codex-like-client-shell",
            "client-command-center",
            "What should this client machine do?",
            "Tell this client machine what to do...",
            "Advanced maintenance and diagnostics",
            "chat-settings-panel",
            "advanced-diagnostics",
            "command-input-row",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-status-rail",
            ".client-command-box",
            ".client-next-step",
            ".advanced-diagnostics",
            ".chat-settings-panel",
            ".command-input-row",
            ".primary-action",
        ]:
            assert token in styles


def test_worker_consoles_fold_advanced_commercial_controls() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Common actions",
            "Advanced execution and recovery",
            "client-operation-guided-actions",
            "client-operation-advanced-controls",
            "operationGuidedActionsTitle",
            "operationAdvancedActionsHint",
            "Move from left to right: goal, knowledge, content, approval, and loop delivery.",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-operation-guided-actions",
            ".client-operation-advanced-controls",
            ".client-operation-advanced-controls summary",
        ]:
            assert token in styles


def test_phase_62k_plan_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (phase_index, current_next, project_status, en_status, zh_status, en_console, zh_console):
        assert "Phase 62K Customer Console Codex-like UX Simplification" in text
        assert "codex/phase-62k-customer-console-codex-ux" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62l_task_workbench() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "TaskWorkbenchCopy",
            "Client Task Workbench",
            "客户机任务工作台",
            "client-task-workbench",
            "workbench-next-action",
            "workbench-metrics",
            "pendingApprovals",
            "activeTaskRuns",
            "failedTaskRuns",
            "open={pendingApprovals.length > 0}",
            "open={failedTaskRuns.length > 0 || activeTaskRuns.length > 0}",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-task-workbench",
            ".workbench-next-action",
            ".workbench-metrics",
            ".workbench-run-details",
            ".workbench-detail",
            ".approval-card",
        ]:
            assert token in styles


def test_phase_62l_plan_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62L Customer Console Task Workbench" in text
        assert "codex/phase-62l-client-task-workbench" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62m_goal_templates() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "WorkbenchGoalTemplate",
            "workbenchGoalTemplates",
            "Goal templates",
            "launch_content",
            "rag_evidence",
            "asset_brief",
            "page_report",
            "selectedGoalTemplateId",
            "applyGoalTemplate",
            "setSelectedPlaybookName(template.playbookName)",
            "workbench-template-grid",
            "workbench-template-card",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".workbench-template-strip",
            ".workbench-template-header",
            ".workbench-template-grid",
            ".workbench-template-card",
            ".workbench-template-card.selected",
        ]:
            assert token in styles


def test_phase_62m_plan_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62M Customer Console Goal Templates" in text
        assert "codex/phase-62m-client-goal-templates" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62n_goal_plan_preview() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "planTitle",
            "planSteps",
            "reviewGate",
            "outcome",
            "Plan preview",
            "Approval boundary",
            "workbench-plan-preview",
            "workbench-plan-steps",
            "workbench-plan-gate",
            "selectedGoalTemplate.planSteps.map",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".workbench-plan-preview",
            ".workbench-plan-header",
            ".workbench-plan-steps",
            ".workbench-plan-steps li",
            ".workbench-plan-gate",
        ]:
            assert token in styles


def test_phase_62n_plan_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62N Customer Console Goal Plan Preview" in text
        assert "codex/phase-62n-client-goal-plan-preview" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62o_goal_status_tracker() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "GoalStatusStage",
            "GoalStatusStageState",
            "goalStatusStages",
            "statusTrackerTitle",
            "statusStageNeedsAction",
            "workbench-status-tracker",
            "workbench-status-stages",
            "pendingApprovals.length > 0",
            "activeTaskRuns.length > 0",
            "failedTaskRuns.length > 0",
            "artifacts.length > 0",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".workbench-status-tracker",
            ".workbench-status-header",
            ".workbench-status-stages",
            ".workbench-status-stage",
            ".workbench-status-stage.needs-action",
            ".workbench-status-stage.done",
            ".workbench-status-stage.current",
        ]:
            assert token in styles


def test_phase_62o_goal_status_tracker_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62O Customer Console Goal Status Tracker" in text
        assert "codex/phase-62o-client-goal-status-tracker" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62p_simple_operator_and_knowledge_page() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_KNOWLEDGE_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_KNOWLEDGE_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "KnowledgeBasePanel",
            "knowledge-base-panel",
            "operator-page-tabs",
            "pageKnowledge",
            "Knowledge Base Upload and Edit",
            "知识库修改与上传",
            "simple-operator-workbench",
            "simple-template-chip",
            "simple-progress-card",
            "operator-detail-drawer",
            "maintenance-drawer",
            "simpleCurrentStage",
            "open={pendingCommercialApprovals.length > 0 || pendingApprovals.length > 0 || failedTaskRuns.length > 0}",
            "knowledge-upload-drop",
            "knowledge-document-card",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for client in (web_client, desktop_client):
        for token in [
            "knowledgeBaseClient",
            "uploadFile",
            "ingestText",
            "reingestText",
            '"/files/upload"',
            '"/rag/ingest"',
            '"/documents/reingest"',
            "FormData",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".operator-page-tabs",
            ".simple-operator-workbench",
            ".simple-template-chip",
            ".simple-progress-card",
            ".operator-detail-drawer",
            ".maintenance-drawer",
            ".knowledge-base-panel",
            ".knowledge-upload-drop",
            ".knowledge-flow-grid",
            ".knowledge-document-card",
        ]:
            assert token in styles


def test_phase_62p_simple_operator_mode_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62P Customer Console Simple Operator Mode" in text
        assert "codex/phase-62p-client-simple-operator-mode" in text
        assert "knowledge base upload/edit page" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62q_knowledge_upload_readiness() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "KNOWLEDGE_MAX_FILE_SIZE_BYTES",
            "SUPPORTED_KNOWLEDGE_EXTENSIONS",
            "knowledgeFileExtension",
            "readinessCards",
            "retryableFailedCount",
            "totalUploadableFileCount",
            "clearCompletedKnowledgeFiles",
            "removeKnowledgeQueueItem",
            "retryable",
            "unsupportedFile",
            "fileTooLarge",
            "retryFailed",
            "clearCompleted",
            "knowledge-readiness-strip",
            "knowledge-next-step-card",
            "knowledge-file-rules",
            "knowledge-button-row",
            "knowledge-file-remove",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for styles in (web_styles, desktop_styles):
        for token in [
            ".knowledge-readiness-strip",
            ".knowledge-readiness-card",
            ".knowledge-readiness-card.good",
            ".knowledge-readiness-card.warn",
            ".knowledge-next-step-card",
            ".knowledge-next-step-card.ready",
            ".knowledge-next-step-card.warn",
            ".knowledge-file-rules",
            ".knowledge-button-row",
            ".knowledge-file-remove",
        ]:
            assert token in styles


def test_phase_62q_knowledge_upload_readiness_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62Q Customer Console Knowledge Upload Readiness" in text
        assert "codex/phase-62q-knowledge-upload-readiness" in text
        assert "knowledge upload readiness" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62r_knowledge_activity_timeline() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "KnowledgeActivityItem",
            "KnowledgeActivityTone",
            "knowledgeActivityId",
            "activities",
            "setActivities",
            "addKnowledgeActivity",
            "activityTitle",
            "activityUploadTitle",
            "activityTextSavedTitle",
            "activityRefreshTitle",
            "activityRemovedTitle",
            "activityClearedTitle",
            "clearActivity",
            "knowledge-activity-panel",
            "knowledge-activity-list",
            "knowledge-activity-item",
            "knowledge-activity-dot",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for styles in (web_styles, desktop_styles):
        for token in [
            ".knowledge-activity-panel",
            ".knowledge-activity-header",
            ".knowledge-activity-list",
            ".knowledge-activity-item",
            ".knowledge-activity-item.good",
            ".knowledge-activity-item.warn",
            ".knowledge-activity-dot",
        ]:
            assert token in styles


def test_phase_62r_knowledge_activity_timeline_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62R Customer Console Knowledge Activity Timeline" in text
        assert "codex/phase-62r-knowledge-activity-timeline" in text
        assert "knowledge activity timeline" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62s_knowledge_document_details() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "knowledgeDocumentKey",
            "knowledgeDocumentStatusTone",
            "selectedDocumentKey",
            "selectedDocument",
            "readyDocumentCount",
            "reviewDocumentCount",
            "documentOverviewTitle",
            "documentOverviewReady",
            "documentOverviewNeedsReview",
            "detailTitle",
            "detailHealthReady",
            "detailHealthNeedsReview",
            "viewDetails",
            "useForUpdate",
            "knowledge-document-overview",
            "knowledge-document-workspace",
            "knowledge-document-detail-panel",
            "knowledge-detail-health",
            "knowledge-detail-list",
            "knowledge-document-actions",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for styles in (web_styles, desktop_styles):
        for token in [
            ".knowledge-document-overview",
            ".knowledge-document-overview-card",
            ".knowledge-document-workspace",
            ".knowledge-document-card.selected",
            ".knowledge-document-actions",
            ".knowledge-document-detail-panel",
            ".knowledge-detail-health",
            ".knowledge-detail-list",
        ]:
            assert token in styles


def test_phase_62s_knowledge_document_details_are_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62S Customer Console Knowledge Document Details" in text
        assert "codex/phase-62s-knowledge-document-details" in text
        assert "knowledge document details" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62t_knowledge_search_validation() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_KNOWLEDGE_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_KNOWLEDGE_CLIENT.read_text(encoding="utf-8")

    for client in (web_client, desktop_client):
        for token in [
            "KnowledgeSearchMode",
            "KnowledgeSearchResult",
            "KnowledgeSearchResponse",
            "search:",
            '"/rag/search"',
            "search_mode",
            "collection_name",
            "top_k",
        ]:
            assert token in client

    for text in (web_main, desktop_main):
        for token in [
            "validationQuery",
            "validationMode",
            "validationState",
            "validationResults",
            "validationSummary",
            "runKnowledgeValidation",
            "knowledgeSearchSourceLabel",
            "knowledgeSearchScore",
            "formatKnowledgeSearchScore",
            "validationTitle",
            "validationAction",
            "validationSearchTitle",
            "validationFailedTitle",
            "knowledge-validation-panel",
            "knowledge-validation-form",
            "knowledge-validation-results",
            "knowledge-validation-result-card",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for styles in (web_styles, desktop_styles):
        for token in [
            ".knowledge-validation-panel",
            ".knowledge-validation-header",
            ".knowledge-validation-form",
            ".knowledge-validation-summary",
            ".knowledge-validation-results",
            ".knowledge-validation-result-card",
            ".knowledge-validation-result-main",
            ".knowledge-validation-result-meta",
        ]:
            assert token in styles


def test_phase_62t_knowledge_search_validation_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62T Customer Console Knowledge Search Validation" in text
        assert "codex/phase-62t-knowledge-search-validation" in text
        assert "knowledge search validation" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62u_knowledge_ingestion_status_loop() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_KNOWLEDGE_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_KNOWLEDGE_CLIENT.read_text(encoding="utf-8")

    for client in (web_client, desktop_client):
        for token in [
            "KnowledgeUploadResponse",
            "ingest_status",
            "ingest_error",
            "error_message",
            "metadata",
            "skipped_duplicate",
            "chunk_ids",
        ]:
            assert token in client

    for text in (web_main, desktop_main):
        for token in [
            "KnowledgeIngestionStage",
            "knowledgeDocumentIngestionStage",
            "knowledgeIngestionProgressForQueue",
            "knowledgeIngestionProgressForDocument",
            "processingDocumentCount",
            "ingestionNeedsActionCount",
            "ingestionPanelTone",
            "ingestionPipelineSteps",
            "selectedDocumentIngestLabel",
            "ingestionTitle",
            "ingestionNextAction",
            "ingestionSkipped",
            "ingestionSelectedStatus",
            "knowledge-ingestion-panel",
            "knowledge-ingestion-stats",
            "knowledge-ingestion-pipeline",
            "knowledge-ingestion-item",
            "knowledge-ingestion-progress",
            "knowledge-ingestion-meta",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for styles in (web_styles, desktop_styles):
        for token in [
            ".knowledge-ingestion-panel",
            ".knowledge-ingestion-panel.good",
            ".knowledge-ingestion-panel.warn",
            ".knowledge-ingestion-header",
            ".knowledge-ingestion-actions",
            ".knowledge-ingestion-stats",
            ".knowledge-ingestion-stat-card",
            ".knowledge-ingestion-pipeline",
            ".knowledge-ingestion-step",
            ".knowledge-ingestion-step.done",
            ".knowledge-ingestion-step.current",
            ".knowledge-ingestion-step.needs-action",
            ".knowledge-ingestion-list",
            ".knowledge-ingestion-item",
            ".knowledge-ingestion-progress",
            ".knowledge-ingestion-meta",
        ]:
            assert token in styles


def test_phase_62u_knowledge_ingestion_status_loop_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62U Customer Console Knowledge Ingestion Status Loop" in text
        assert "codex/phase-62u-knowledge-ingestion-status" in text
        assert "knowledge ingestion status loop" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62v_knowledge_validation_guidance() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "KnowledgeValidationSuggestion",
            "knowledgeValidationQuestion",
            "latestUploadedQueueItem",
            "validationSuggestions",
            "selectedDocumentValidationSuggestion",
            "latestUploadValidationSuggestion",
            "applyKnowledgeValidationSuggestion",
            "validationGuidanceTitle",
            "validationSuggestionAppliedTitle",
            "validationUseSuggestion",
            "validationRunForItem",
            "validationSuggestionSummaryQuery",
            "validationSuggestionRiskQuery",
            "validationSuggestionActionQuery",
            "knowledge-validation-guidance",
            "knowledge-validation-targets",
            "knowledge-validation-suggestions",
            "knowledge-validation-suggestion-card",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for styles in (web_styles, desktop_styles):
        for token in [
            ".knowledge-validation-guidance",
            ".knowledge-validation-guidance-header",
            ".knowledge-validation-targets",
            ".knowledge-validation-target-card",
            ".knowledge-validation-suggestions",
            ".knowledge-validation-suggestion-card",
            ".knowledge-validation-suggestion-card:hover",
        ]:
            assert token in styles


def test_phase_62v_knowledge_validation_guidance_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62V Customer Console Knowledge Validation Guidance" in text
        assert "codex/phase-62v-knowledge-validation-guidance" in text
        assert "knowledge validation guidance" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62w_knowledge_validation_outcomes() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "validationOutcomeTitle",
            "validationOutcomeReady",
            "validationOutcomeNeedsEvidence",
            "validationOutcomeNeedsReview",
            "validationOutcomeMarkedTitle",
            "validationOutcomeMaterialLabel",
            "validationOutcomeTone",
            "validationOutcomeStats",
            "validationOutcomeActionLabel",
            "confirmKnowledgeValidationOutcome",
            "knowledge-validation-outcome",
            "knowledge-validation-outcome-main",
            "knowledge-validation-outcome-stats",
            "knowledge-validation-outcome-action",
        ]:
            assert token in text
        knowledge_panel = text.split("function KnowledgeBasePanel", 1)[1].split("function App", 1)[0]
        assert "<pre" not in knowledge_panel
        assert "<code" not in knowledge_panel

    for styles in (web_styles, desktop_styles):
        for token in [
            ".knowledge-validation-outcome",
            ".knowledge-validation-outcome.good",
            ".knowledge-validation-outcome.warn",
            ".knowledge-validation-outcome-main",
            ".knowledge-validation-outcome-stats",
            ".knowledge-validation-outcome-stat",
            ".knowledge-validation-outcome-action",
        ]:
            assert token in styles


def test_phase_62w_knowledge_validation_outcomes_are_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62W Customer Console Knowledge Validation Outcomes" in text
        assert "codex/phase-62w-knowledge-validation-outcomes" in text
        assert "knowledge validation outcomes" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_62x_client_operation_desk() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "OperationLoopStepCopy",
            "OperationDeliverableCopy",
            "operationDeskTitle",
            "operationLoopSteps",
            "operationDeliverables",
            "operationStageStatus",
            "operationLoopStages",
            "operationCurrentStage",
            "operationResultSummary",
            "openOutputDetails",
            "onOpenKnowledge",
            "client-operation-desk",
            "client-operation-loop",
            "client-operation-controls",
            "client-operation-deliverables",
            "OpenClaw/Playwright",
            "Product operation desk",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-operation-desk",
            ".client-operation-header",
            ".client-operation-status",
            ".client-operation-current",
            ".client-operation-controls",
            ".client-operation-loop",
            ".client-operation-step",
            ".client-operation-deliverables",
            ".client-operation-deliverable",
            ".client-operation-knowledge-card",
        ]:
            assert token in styles


def test_phase_62x_client_operation_desk_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 62X Customer Console Product Operation Desk" in text
        assert "codex/phase-62x-client-operation-desk" in text
        assert "product operation desk" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63a_operation_loop_protocol_binding() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for client in (web_client, desktop_client):
        for token in [
            "commercialOperationClient",
            "CommercialOperationLoopSummary",
            "CommercialOperationLoopStage",
            '"/commercial-operations"',
            "/operation-loop",
            "normalizeApiBase",
            "X-Workspace-Id",
        ]:
            assert token in client

    for text in (web_main, desktop_main):
        for token in [
            "refreshCommercialOperationLoop",
            "createCommercialOperationLoop",
            "operationLoopStatusToGoalState",
            "operationLoopTitleFromGoal",
            "operationLoopSourceText",
            "operationLoopLoaded",
            "operationLoopDisconnected",
            "operationStartLoop",
            "operationRefreshLoop",
            "selectedCommercialOperationId",
            "target_audience",
            "client execution through OpenClaw/Playwright after approval",
        ]:
            assert token in text


def test_phase_63a_operation_loop_protocol_binding_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63A Customer Console Loop Protocol Binding" in text
        assert "codex/phase-63a-client-loop-protocol-binding" in text
        assert "operation-loop" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63b_first_draft_bootstrap() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for client in (web_client, desktop_client):
        for token in [
            "planDraft",
            "createContentDraft",
            "readyContentDraft",
            "createApproval",
            "CommercialOperationContentDraft",
            "CommercialOperationApproval",
            "/plan-draft",
            "/content-drafts",
            "/approvals",
        ]:
            assert token in client

    for text in (web_main, desktop_main):
        for token in [
            "firstDraftContentBody",
            "prepareFirstDraftPackage",
            "firstDraftBootstrapStatus",
            "operationPrepareDraft",
            "operationFirstDraftReady",
            "准备首版产物",
            "First draft is ready for approval",
            "content_production",
            "human_review",
            "worker_console",
            "first_draft_bootstrap",
            "no ComfyUI job is created in this phase",
        ]:
            assert token in text


def test_phase_63b_first_draft_bootstrap_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63B Customer Console First Draft Bootstrap" in text
        assert "codex/phase-63b-client-first-draft-bootstrap" in text
        assert "first draft" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63c_approval_execution_prep() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for client in (web_client, desktop_client):
        for token in [
            "listApprovals",
            "approveApproval",
            "rejectApproval",
            "approveContentDraft",
            "rejectContentDraft",
            "createDeliverable",
            "readyDeliverable",
            "approveDeliverable",
            "packageDeliverable",
            "createExecutionRequest",
            "readyExecutionRequest",
            "/execution-requests",
            "/deliverables",
        ]:
            assert token in client

    for text in (web_main, desktop_main):
        for token in [
            "commercialApprovals",
            "resolveCommercialApprovalDraft",
            "approveCommercialApprovalAndPrepareExecution",
            "rejectCommercialApproval",
            "operationApproveAndPrepare",
            "operationRejectDraft",
            "operationExecutionPrepReady",
            "openclaw",
            "metadata_only",
            "customer_machine_playwright",
            "worker_console_approval_execution_prep",
            "human_review",
        ]:
            assert token in text


def test_phase_63c_approval_execution_prep_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63C Customer Console Approval and Execution Prep" in text
        assert "codex/phase-63c-client-approval-execution-prep" in text
        assert "execution prep" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63d_execution_run_review() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationExecutionRun",
            "listExecutionRequests",
            "approveExecutionRequest",
            "prepareExecutionRequest",
            "createExecutionRun",
            "listExecutionRuns",
            "startExecutionRun",
            "failExecutionRun",
            "retryExecutionRun",
            "/execution-runs",
            "/start",
            "/fail",
            "/retry",
        ]:
            assert token in client

    for text in (web_main, desktop_main):
        for token in [
            "commercialExecutionRequests",
            "commercialExecutionRuns",
            "resolveExecutionRequestForRun",
            "reviewExecutionRequestAndQueueRun",
            "startCommercialExecutionRun",
            "failCommercialExecutionRun",
            "retryCommercialExecutionRun",
            "operationReviewAndQueueRun",
            "operationStartRun",
            "operationFailRun",
            "operationRetryRun",
            "worker_console_execution_run_review",
            "metadata-only; no external runtime call",
            "63D",
        ]:
            assert token in text


def test_phase_63d_execution_run_review_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63D Customer Console Execution Run Review" in text
        assert "codex/phase-63d-client-execution-run-review" in text
        assert "execution run" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63e_result_feedback_loop() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationResult",
            "CommercialOperationMonitoringObservation",
            "CommercialOperationOptimizationDecision",
            "succeedExecutionRun",
            "createResult",
            "listResults",
            "readyResult",
            "approveResult",
            "createMonitoringObservation",
            "listMonitoringObservations",
            "readyMonitoringObservation",
            "approveMonitoringObservation",
            "createOptimizationDecision",
            "listOptimizationDecisions",
            "readyOptimizationDecision",
            "approveOptimizationDecision",
            "/succeed",
            "/results",
            "/monitoring-observations",
            "/optimization-decisions",
        ]:
            assert token in client

    for text in (web_main, desktop_main):
        for token in [
            "commercialResults",
            "commercialMonitoringObservations",
            "commercialOptimizationDecisions",
            "completeCommercialResultFeedbackLoop",
            "operationCompleteFeedbackLoop",
            "operationFeedbackLoopComplete",
            "operationResultRecordPending",
            "operationObservationPending",
            "operationOptimizationPending",
            "worker_console_result_feedback_loop",
            "manual_pending",
            "next_cycle_ready",
            "63E",
        ]:
            assert token in text


def test_phase_63e_result_feedback_loop_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63E Customer Console Result Feedback Loop" in text
        assert "codex/phase-63e-client-result-feedback-loop" in text
        assert "minimum usable closed loop" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63f_next_cycle_content_drafts() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "nextCycleContentBody",
            "prepareNextCycleDraftFromDecision",
            "nextCycleDraftStatus",
            "nextCycleDraftLoading",
            "operationPrepareNextCycleDraft",
            "operationNextCycleDraftReady",
            "operationNextCycleDecisionMissing",
            "approvedCommercialOptimizationDecision",
            "next_cycle_content_draft",
            "next_cycle_copy",
            "next_iteration",
            "optimization_decision_id",
            "Approve next-cycle operation content",
            "63F",
        ]:
            assert token in text


def test_phase_63f_next_cycle_content_drafts_are_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63F Customer Console Next-Cycle Content Drafts" in text
        assert "codex/phase-63f-next-cycle-content-drafts" in text
        assert "next-cycle content draft" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63g_next_cycle_execution_prep() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "isNextCycleApproval",
            "pendingNextCycleCommercialApproval",
            "operationApproveNextCycleAndPrepare",
            "operationNextCycleApprovalPreparing",
            "operationNextCycleExecutionPrepReady",
            "operationRejectNextCycleDraft",
            "next_cycle_approval_execution_prep",
            "next_cycle_content_package",
            "next-cycle approval execution prep",
            "optimization_decision_id",
            "cycle: approvalIsNextCycle ? \"next_iteration\" : \"first_iteration\"",
            "63G",
        ]:
            assert token in text


def test_phase_63g_next_cycle_execution_prep_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63G Customer Console Next-Cycle Execution Prep" in text
        assert "codex/phase-63g-next-cycle-execution-prep" in text
        assert "next-cycle execution prep" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63h_next_cycle_execution_run_review() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "isNextCycleExecutionRequest",
            "pendingNextCycleExecutionRequest",
            "operationReviewAndQueueNextCycleRun",
            "operationNextCycleExecutionRunQueuing",
            "operationNextCycleExecutionRunReady",
            "next_cycle_execution_run_review",
            "requestIsNextCycle",
            "executionRunPhase = requestIsNextCycle ? \"63H\" : \"63D\"",
            "cycle: requestIsNextCycle ? \"next_iteration\" : \"first_iteration\"",
            "optimization_decision_id",
            "63H",
        ]:
            assert token in text


def test_phase_63h_next_cycle_execution_run_review_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63H Customer Console Next-Cycle Execution Run Review" in text
        assert "codex/phase-63h-next-cycle-execution-run-review" in text
        assert "next-cycle execution run" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63i_next_cycle_result_feedback_loop() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "isNextCycleExecutionRun",
            "pendingNextCycleFeedbackExecutionRun",
            "operationCompleteNextCycleFeedbackLoop",
            "operationNextCycleFeedbackLoopCompleting",
            "operationNextCycleFeedbackLoopComplete",
            "next_cycle_result_feedback_loop",
            "runIsNextCycle",
            "feedbackPhase = runIsNextCycle ? \"63I\" : \"63E\"",
            "feedbackCycle = runIsNextCycle ? \"next_iteration\" : \"first_iteration\"",
            "previous_optimization_decision_id",
            "63I",
        ]:
            assert token in text


def test_phase_63i_next_cycle_result_feedback_loop_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63I Customer Console Next-Cycle Result Feedback Loop" in text
        assert "codex/phase-63i-next-cycle-result-feedback-loop" in text
        assert "next-cycle result feedback" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63j_client_runtime_preflight() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = (ROOT / "worker_console/src/api/commercialOperationClient.ts").read_text(encoding="utf-8")
    desktop_client = (ROOT / "worker_console_desktop/src/api/commercialOperationClient.ts").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "preflightClientRuntimeExecutionRun",
            "runtimePreflightCandidateExecutionRun",
            "operationRuntimePreflight",
            "operationRuntimePreflightChecking",
            "operationRuntimePreflightReady",
            "client_runtime_preflight",
            "runtime_preflight_status",
            "worker_api_reachable",
            "openclaw_enabled",
            "browser_enabled",
            "actual_openclaw_execution_performed: false",
            "phase: \"63J\"",
        ]:
            assert token in text

    for text in (web_client, desktop_client):
        assert "updateExecutionRun" in text
        assert "method: \"PATCH\"" in text
        assert "/execution-runs/${encodeURIComponent(executionRunId)}" in text


def test_phase_63j_client_runtime_preflight_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63J Customer Console Client Runtime Preflight" in text
        assert "codex/phase-63j-client-runtime-preflight" in text
        assert "client runtime preflight" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63k_guarded_adapter_dispatch_handoff() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "prepareGuardedAdapterDispatchHandoff",
            "guardedDispatchCandidateExecutionRun",
            "operationGuardedDispatchHandoff",
            "operationGuardedDispatchHandingOff",
            "operationGuardedDispatchReady",
            "isClientRuntimePreflightReady",
            "guarded_adapter_dispatch_handoff",
            "guarded_adapter_dispatch_status",
            "guarded_metadata_only_handoff",
            "client_runtime_preflight_ready",
            "external_execution_performed: false",
            "actual_openclaw_execution_performed: false",
            "playwright_run_performed: false",
            "phase: \"63K\"",
        ]:
            assert token in text


def test_phase_63k_guarded_adapter_dispatch_handoff_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63K Customer Console Guarded Adapter Dispatch Handoff" in text
        assert "codex/phase-63k-guarded-adapter-dispatch-handoff" in text
        assert "guarded adapter dispatch handoff" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63l_63n_execution_and_approval_loop() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = (ROOT / "worker_console/src/styles.css").read_text(encoding="utf-8")
    desktop_styles = (ROOT / "worker_console_desktop/src/styles.css").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "runGuardedAdapterDryRun",
            "adapterDryRunCandidateExecutionRun",
            "operationAdapterDryRun",
            "operationAdapterDryRunRunning",
            "operationAdapterDryRunSucceeded",
            "isGuardedAdapterDispatchReady",
            "guarded_adapter_dry_run",
            "guarded_adapter_dry_run_status",
            "guarded_dry_run_only",
            "dry_run_only",
            "actual_adapter_invocation_performed: false",
            "external_execution_performed: false",
            "actual_openclaw_execution_performed: false",
            "playwright_run_performed: false",
            "phase: \"63L\"",
            "commercial-approvals-panel",
            "operationApprovalCenterSummary",
            "operationApprovalCenterApprove",
            "operationApprovalCenterReject",
            "client-execution-queue",
            "visibleCommercialExecutionRuns",
            "activeCommercialExecutionRunCount",
        ]:
            assert token in text

    for text in (web_styles, desktop_styles):
        for token in [
            ".client-execution-queue",
            ".client-execution-run-list",
            ".client-execution-run.run-status-running",
            ".client-execution-run.run-status-succeeded",
        ]:
            assert token in text


def test_phase_63l_63n_execution_and_approval_loop_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63L-63N Customer Console Execution and Approval Loop" in text
        assert "codex/phase-63l-63n-execution-approval-loop" in text
        assert "guarded adapter dry-run" in text
        assert "client execution queue" in text
        assert "commercial approval center" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63o_63q_publish_result_observation_loop() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = (ROOT / "worker_console/src/styles.css").read_text(encoding="utf-8")
    desktop_styles = (ROOT / "worker_console_desktop/src/styles.css").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "prepareGuardedPublishHandoff",
            "captureManualPublishResult",
            "recordManualMetricObservation",
            "operationPublishPanelTitle",
            "operationPublishHandoff",
            "operationCapturePublishResult",
            "operationRecordMetricObservation",
            "isPublishHandoffResult",
            "isManualPublishResult",
            "isManualMetricObservation",
            "guarded_publish_handoff",
            "manual_publish_result",
            "manual_publish_metrics",
            "client-publish-loop",
            "client-publish-step",
            "phase: \"63O\"",
            "phase: \"63P\"",
            "phase: \"63Q\"",
            "live_adapter_execution_performed: false",
            "external_execution_performed: false",
            "actual_openclaw_execution_performed: false",
            "playwright_run_performed: false",
        ]:
            assert token in text

    for text in (web_styles, desktop_styles):
        for token in [
            ".client-publish-loop",
            ".client-publish-loop-grid",
            ".client-publish-step",
        ]:
            assert token in text


def test_phase_63o_63q_publish_result_observation_loop_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63O-63Q Customer Console Publish Result Observation Loop" in text
        assert "codex/phase-63o-63q-publish-result-observation-loop" in text
        assert "guarded publish handoff" in text
        assert "manual publish result" in text
        assert "manual metric observation" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63r_63t_publish_metric_improvement_loop() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = (ROOT / "worker_console/src/styles.css").read_text(encoding="utf-8")
    desktop_styles = (ROOT / "worker_console_desktop/src/styles.css").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "analyzeManualPublishMetrics",
            "operationAnalyzePublishMetrics",
            "operationPublishImprovementLabel",
            "operationPrepareImprovedDraft",
            "isManualPublishImprovementDecision",
            "manual_publish_improvement",
            "publish_metric_analysis",
            "publish_metric_next_cycle_draft",
            "publish_metric_next_cycle_copy",
            "manual_publish_metrics",
            "client-publish-improvement-step",
            "client-publish-step-actions",
            "phase: \"63R\"",
            "\"63S\"",
            "automated_optimization_performed: false",
            "automated_publishing_performed: false",
            "platform_analytics_ingested: false",
        ]:
            assert token in text

    assert "worker_console_manual_publish_improvement" in web_main
    assert "worker_console_publish_metric_next_cycle_draft" in web_main
    assert "worker_console_desktop_manual_publish_improvement" in desktop_main
    assert "worker_console_desktop_publish_metric_next_cycle_draft" in desktop_main

    for text in (web_styles, desktop_styles):
        for token in [
            ".client-publish-improvement-step",
            ".client-publish-step-actions",
            "grid-template-columns: repeat(4",
        ]:
            assert token in text


def test_phase_63r_63t_publish_metric_improvement_loop_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63R-63T Customer Console Publish Metric Improvement Loop" in text
        assert "codex/phase-63r-63t-publish-metric-improvement-loop" in text
        assert "manual publish metric improvement" in text
        assert "publish metric next-cycle draft" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63u_63w_improved_draft_reexecution_loop() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "isPublishMetricNextCycleApproval",
            "isPublishMetricReexecutionRequest",
            "isPublishMetricReexecutionRun",
            "pendingPublishMetricNextCycleCommercialApproval",
            "pendingPublishMetricReexecutionRequest",
            "operationApproveImprovedDraftAndPrepare",
            "operationImprovedApprovalPreparing",
            "operationImprovedExecutionPrepReady",
            "operationReviewAndQueueImprovedRun",
            "operationImprovedExecutionRunQueuing",
            "operationImprovedExecutionRunReady",
            "publish_metric_reexecution_prep",
            "publish_metric_reexecution_run_review",
            "publish_metric_next_cycle_content_package",
            "publish_metric_improvement",
            "manual publish metric improvement linked",
            "publish metric next-cycle draft approved",
            "publish metric re-execution prep",
            "manual publish metric improvement approved",
            "\"63V\"",
            "\"63W\"",
        ]:
            assert token in text

    assert "worker_console_publish_metric_reexecution_prep" in web_main
    assert "worker_console_publish_metric_reexecution_run_review" in web_main
    assert "worker_console_desktop_publish_metric_reexecution_prep" in desktop_main
    assert "worker_console_desktop_publish_metric_reexecution_run_review" in desktop_main


def test_phase_63u_63w_improved_draft_reexecution_loop_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63U-63W Customer Console Improved Draft Re-execution Loop" in text
        assert "codex/phase-63u-63w-improved-draft-reexecution-loop" in text
        assert "improved draft re-execution" in text
        assert "publish metric re-execution prep" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_63x_64b_closed_loop_delivery_pass() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = (ROOT / "worker_console/src/styles.css").read_text(encoding="utf-8")
    desktop_styles = (ROOT / "worker_console_desktop/src/styles.css").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "completeClientClosedLoopDeliveryPass",
            "closedLoopDeliveryStatus",
            "closedLoopDeliveryLoading",
            "closedLoopDeliveryAvailable",
            "operationClosedLoopDeliveryTitle",
            "operationClosedLoopDeliveryAction",
            "operationClosedLoopDeliveryRunning",
            "operationClosedLoopDeliveryReady",
            "operationClosedLoopDeliveryBoundary",
            "operationClosedLoopDeliverySteps",
            "preflightClientRuntimeExecutionRun",
            "prepareGuardedAdapterDispatchHandoff",
            "runGuardedAdapterDryRun",
            "prepareGuardedPublishHandoff",
            "captureManualPublishResult",
            "recordManualMetricObservation",
            "analyzeManualPublishMetrics",
            "prepareNextCycleDraftFromDecision",
            "client closed loop delivery pass",
            "client-operation-guided-actions",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        assert "client-operation-guided-actions" in styles
        assert "client-operation-support-drawer" in styles
        assert "client-closed-loop-delivery" not in styles


def test_worker_consoles_expose_phase_64c_agent_skill_orchestration() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperationAgentSkillOrchestration",
            "agentSkillOrchestration",
            "agentSkillStatus",
            "agentSkillLoading",
            "refreshAgentSkillOrchestration",
            "operationAgentSkillTitle",
            "operationAgentSkillBoundary",
            "currentAgentSkill",
            "visibleAgentSkills",
            "agentSkillControllerName",
            "client-agent-skill-panel",
            "client-agent-skill-item",
        ]:
            assert token in text

    for text in (web_client, desktop_client):
        assert "CommercialOperationAgentSkillOrchestration" in text
        assert "CommercialOperationAgentSkill" in text
        assert "agent-skill-orchestration" in text
        assert "agent-skill-orchestration/refresh" in text

    for styles in (web_styles, desktop_styles):
        assert "client-agent-skill-panel" in styles
        assert "client-agent-skill-list" in styles
        assert "client-agent-skill-next" in styles
        assert "client-agent-skill-item.needs_review" in styles


def test_worker_consoles_expose_digital_human_video_progress() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    web_client = WEB_DIGITAL_HUMAN_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_DIGITAL_HUMAN_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "digitalHumanClient",
            "DigitalHumanVideoJob",
            "digitalHumanVideoJobs",
            "refreshDigitalHumanVideos",
            "refreshLatestDigitalHumanVideo",
            "client-digital-human-progress",
            "Digital human video",
            "ComfyUI linked",
        ]:
            assert token in text

    for text in (web_client, desktop_client):
        for token in [
            "listVideoJobs",
            "refreshVideoJob",
            '"/digital-humans/video-jobs?limit=5"',
            "`/digital-humans/video-jobs/${encodeURIComponent(jobId)}/refresh`",
            "progress_percent",
            "linked_comfyui_video_job_id",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-digital-human-progress",
            ".client-digital-human-meta",
        ]:
            assert token in styles


def test_phase_63x_64b_closed_loop_delivery_pass_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 63X-64B Customer Console Closed Loop Delivery Pass" in text
        assert "codex/phase-63x-64b-client-closed-loop-delivery" in text
        assert "client closed-loop delivery" in text
        assert "OpenClaw/Playwright handoff" in text
        assert "publish result capture" in text
        assert "next draft generation" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_phase_64c_commercial_agent_skill_orchestration_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    docs = (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    )
    for text in docs:
        assert "Phase 64C Commercial Agent/Skill Orchestration" in text
        assert "codex/phase-64c-commercial-agent-skill-orchestration" in text
        assert "Agent/Skill" in text
        assert "admin_dashboard" in text
        assert "worker_console" in text
    all_docs = "\n".join(docs)
    assert "agent-skill-orchestration" in all_docs
    assert "commercial_operation_agent" in all_docs


def test_phase_64d_frontend_operability_optimization_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    docs = (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    )
    for text in docs:
        assert "Phase 64D Server/Client Frontend Operability Optimization" in text
        assert "codex/phase-64d-frontend-operability-optimization" in text
        assert "maintenance cockpit" in text
        assert "admin_dashboard" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
    assert "execution/recovery" in "\n".join(docs)


def test_phase_64e_layout_declutter_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_overview = (ROOT / "docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (
        phase_index,
        current_next,
        project_status,
        en_status,
        zh_status,
        current_runtime,
        project_overview,
        en_console,
        zh_console,
    ):
        assert "Phase 64E Layout Declutter" in text
        assert "codex/phase-64e-layout-declutter" in text
        assert "client-operation-support-drawer" in text
        assert "commercial-action-result-drawer" in text
        assert "remove the duplicate closed-loop delivery panel" in text
