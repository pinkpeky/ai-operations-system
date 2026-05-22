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
