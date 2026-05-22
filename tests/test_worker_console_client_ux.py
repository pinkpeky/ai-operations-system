"""Phase 62I workstation/customer client frontend UX checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_MAIN = ROOT / "worker_console/src/main.tsx"
WEB_STYLES = ROOT / "worker_console/src/styles.css"
WEB_KNOWLEDGE_CLIENT = ROOT / "worker_console/src/api/knowledgeBaseClient.ts"
DESKTOP_MAIN = ROOT / "worker_console_desktop/src/main.tsx"
DESKTOP_STYLES = ROOT / "worker_console_desktop/src/styles.css"
DESKTOP_KNOWLEDGE_CLIENT = ROOT / "worker_console_desktop/src/api/knowledgeBaseClient.ts"


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
            "open={pendingApprovals.length > 0 || failedTaskRuns.length > 0}",
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
