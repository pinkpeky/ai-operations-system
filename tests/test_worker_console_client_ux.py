"""Phase 62I workstation/customer client frontend UX checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_MAIN = ROOT / "worker_console/src/main.tsx"
WEB_STYLES = ROOT / "worker_console/src/styles.css"
WEB_KNOWLEDGE_CLIENT = ROOT / "worker_console/src/api/knowledgeBaseClient.ts"
WEB_COMMERCIAL_OPERATION_CLIENT = ROOT / "worker_console/src/api/commercialOperationClient.ts"
WEB_COMFYUI_RUNTIME_CLIENT = ROOT / "worker_console/src/api/comfyuiRuntimeClient.ts"
WEB_DIGITAL_HUMAN_CLIENT = ROOT / "worker_console/src/api/digitalHumanClient.ts"
DESKTOP_MAIN = ROOT / "worker_console_desktop/src/main.tsx"
DESKTOP_STYLES = ROOT / "worker_console_desktop/src/styles.css"
DESKTOP_KNOWLEDGE_CLIENT = ROOT / "worker_console_desktop/src/api/knowledgeBaseClient.ts"
DESKTOP_COMMERCIAL_OPERATION_CLIENT = ROOT / "worker_console_desktop/src/api/commercialOperationClient.ts"
DESKTOP_COMFYUI_RUNTIME_CLIENT = ROOT / "worker_console_desktop/src/api/comfyuiRuntimeClient.ts"
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
            "Enter an operating goal, for example:",
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


def test_worker_consoles_scope_knowledge_and_lock_approved_operation_plan() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "项目知识库",
            "Project knowledge base",
            "当前项目知识",
            "已批准方案为冻结版本",
            "查看实现任务",
            "Open implementation",
            "runSimplePlanPrimaryAction",
            'openSimpleProductionDetailsAndScroll("client-project-section-tasks")',
            "添加项目资料",
            "Add project material",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        assert ".simple-plan-boundary-note" in styles


def test_worker_consoles_split_planning_and_implementation_into_large_pages() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "simpleWorkspacePage",
            "activeSimpleWorkspacePage",
            "simpleWorkspaceImplementationReady",
            "hasSimpleProjectContext",
            "Phase 73Z Client Large Workspace Pages",
            "Phase 74B Client Project Overview and Stage Tabs",
            "simple-workspace-page-tabs",
            "simple-workspace-page-tab",
            "Phase 73Z Client Implementation Page",
            "simple-implementation-page-head",
            'setSimpleWorkspacePage("text")',
            'data-simple-workspace-page={activeSimpleWorkspacePage}',
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-workspace-page-tabs",
            ".simple-workspace-page-tab",
            ".simple-implementation-page-head",
            '[data-simple-workspace-page="planning"] .simple-approval-workbench',
            '[data-simple-workspace-page="planning"] .simple-production-details-drawer',
            ':not([data-simple-workspace-page="planning"]) .simple-conversation-workspace',
            '[data-simple-workspace-page="text"] .simple-production-guide-step',
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_74b_project_overview_stage_tabs_and_back_path() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 74B Client Project Overview Page",
            "Phase 74B Project Status List",
            "Phase 74B Client Project Overview and Stage Tabs",
            "simpleProjectOverviewStats",
            "simple-project-overview-page",
            "simple-project-overview-card",
            "hasSimpleProjectContext",
            "simpleWorkspacePageForTarget",
            "openSimpleProductionDetailsAndScroll",
            'setSimpleWorkspacePage("overview")',
            'setSimpleWorkspacePage("planning")',
            'setSimpleWorkspacePage("text")',
            'setSimpleWorkspacePage("media")',
            'setSimpleWorkspacePage("outputs")',
            'setSimpleWorkspacePage("publish")',
            "onBackToWorkspace",
            "Back to workbench",
            "返回工作台",
            "data-guide-step={step.key}",
            'open={activeSimpleWorkspacePage !== "overview" && activeSimpleWorkspacePage !== "planning"}',
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            "padding: 12px 12px 12px 272px",
            "position: absolute",
            ".simple-project-overview-page",
            ".simple-project-overview-stats",
            ".simple-project-overview-card",
            ".simple-project-overview-empty",
            '[data-simple-workspace-page="overview"] .simple-project-entry',
            '[data-simple-workspace-page="text"] #client-project-section-publish',
            '[data-simple-workspace-page="media"] #client-project-section-tasks',
            '[data-simple-workspace-page="outputs"] #client-project-section-workflows',
            '[data-simple-workspace-page="publish"] #client-project-section-outputs',
            '[data-guide-step="task"]',
            '[data-guide-step="workflow"]',
            '[data-guide-step="output"]',
            '[data-guide-step="publish"]',
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_74d_design_preview_alignment() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 74D Preview Inspired Sidebar Brand",
            "Phase 74D Preview Inspired Top Bar",
            "Phase 74D Preview Inspired Project Context",
            "Phase 74D Preview Inspired Current Action",
            "Phase 74D Project Resource Navigation",
            "simple-design-topbar",
            "simple-design-project-switcher",
            "simple-design-action-hero",
            "simple-resource-page-links",
            "simpleWorkspaceNavItems",
            "simpleResourceNavItems",
            "simpleActiveWorkspaceLabel",
            "runSimpleCurrentAction",
            "AI Ops Workbench",
            "运营项目闭环工作台",
            "当前项目上下文",
            "当前主动作",
            "项目知识库",
            "工作流候选",
            "审批中心",
            "本机运行时",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-design-sidebar-brand",
            ".simple-design-topbar",
            ".simple-design-search",
            ".simple-design-project-switcher",
            ".simple-design-action-hero",
            ".simple-resource-page-links",
            ".codex-simple-client .client-task-workbench::before",
            "width: min(1440px, calc(100vw - 48px))",
            "border: 12px solid rgba(255, 255, 255, 0.64)",
            "content: \"当前项目阶段\"",
            ".simple-project-overview-list",
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_74e_inner_panel_alignment() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert 'data-simple-inner-layout="phase-74e-preview-panels"' in text
        for token in [
            "simple-reference-stage-workspace",
            "Phase 74E Strict Reference Inner Workspace",
            'data-reference-page="feedback"',
            'setSimpleWorkspacePage("feedback")',
            "refreshDailyMetricPullbackHandoff",
            "runDailyMetricAnalysisSchedule",
            "capturePublishExecutionResultFromClient",
            "decideProjectMetricSnapshot",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            "Phase 74E Client Inner Panel Alignment",
            "Phase 74E Strict Reference Inner Workspace",
            '.client-task-workbench[data-simple-inner-layout="phase-74e-preview-panels"]',
            ".simple-reference-stage-workspace",
            ".simple-reference-page-panel",
            '[data-reference-page="planning"]',
            '[data-reference-page="media"]',
            '[data-reference-page="feedback"]',
            ".simple-reference-chat-surface",
            ".simple-reference-copy-card",
            ".simple-reference-material-card",
            ".simple-reference-review-card",
            ".simple-reference-publish-card",
            ".simple-reference-feedback-grid",
            ".simple-reference-feedback-card",
            ".simple-reference-data-list",
            "height: min(900px, calc(100vh - 96px))",
            "height: clamp(430px, calc(100vh - 390px), 620px)",
            "overflow-y: auto",
            "grid-template-areas:",
            "\"chat review\"",
            ".simple-plan-rag-row",
            ".simple-plan-detail-grid",
            ".simple-production-guide-step",
            ".simple-approval-output-preview",
            ".simple-production-details-body",
            "repeat(auto-fit, minmax(210px, 1fr))",
        ]:
            assert token in styles
        assert styles.index("Phase 74E Client Inner Panel Alignment") > styles.index(".simple-design-action-hero")


def test_worker_consoles_expose_phase_74a_content_production_start_guide() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "simpleProductionGuideSteps",
            "simpleOutputCandidateDraftTitle",
            "simpleOutputCandidateDraftValue",
            "Phase 74A Client Production Start Guide",
            "Phase 74A Inline Output Registration",
            "simple-production-guide",
            "simple-production-output-form",
            "Content production guide",
            "Import project material",
            "Approve production task",
            "Select ComfyUI workflow",
            "Register content output",
            "Confirm output and prepare publish",
            "registerProjectMaterialFromClient",
            "decideProjectTask",
            "createManualWorkflowSelection",
            "registerOutputCandidateFromClient",
            "decideProjectOutputCandidate",
            "decideProjectFinalSelection",
            "createPublishPackageFromClient",
            "useBlueprintDefaults",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-production-guide",
            ".simple-production-guide-head",
            ".simple-production-guide-grid",
            ".simple-production-guide-step",
            ".simple-production-guide-step.needs-action",
            ".simple-production-guide-step.current",
            ".simple-production-guide-step.done",
            '[data-guide-step="task"]',
            ".simple-production-guide-actions",
            ".simple-production-output-form",
            ".simple-production-output-form input",
            ".simple-production-output-form textarea",
            '[data-simple-workspace-page="planning"] .simple-production-guide',
        ]:
            assert token in styles
        responsive_index = styles.rindex("@media")
        responsive_guide_index = styles.index(".simple-production-guide-grid", responsive_index)
        responsive_header_index = styles.index(".simple-production-guide-head", responsive_index)
        assert responsive_index < responsive_guide_index < responsive_header_index


def test_worker_consoles_expose_phase_68x_production_runtime_alignment() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_env = (ROOT / "worker_console/.env.example").read_text(encoding="utf-8")
    web_conversation_client = (ROOT / "worker_console/src/api/conversationClient.ts").read_text(encoding="utf-8")
    web_browser_runtime_client = (ROOT / "worker_console/src/api/browserRuntimeClient.ts").read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_env = (ROOT / "worker_console_desktop/.env.example").read_text(encoding="utf-8")
    desktop_conversation_client = (ROOT / "worker_console_desktop/src/api/conversationClient.ts").read_text(encoding="utf-8")
    desktop_browser_runtime_client = (ROOT / "worker_console_desktop/src/api/browserRuntimeClient.ts").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68X Production Runtime Alignment",
            "production-runtime-strip",
            "client-production-runtime-panel",
            "productionRuntimeTitle",
            "productionRuntimeWorkspace",
            "productionRuntimeWorker",
            "productionRuntimeHeartbeat",
            "productionRuntimeScheduler",
            "localWorkerStatus={status}",
            "production-workspace",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".production-runtime-strip",
            ".production-runtime-grid",
            ".client-production-runtime-panel",
            ".client-production-runtime-grid",
            ".client-production-runtime-card",
        ]:
            assert token in styles

    for env_example in (web_env, desktop_env):
        assert "VITE_AI_SERVER_API=http://127.0.0.1:8000" in env_example
        assert "VITE_WORKSPACE_ID=production-workspace" in env_example
        assert "VITE_USER_ID=production-operator" in env_example

    for client in (web_conversation_client, desktop_conversation_client, web_browser_runtime_client, desktop_browser_runtime_client):
        assert "production-workspace" in client
        assert "production-operator" in client
        assert "http://127.0.0.1:8000" in client
    for browser_client in (web_browser_runtime_client, desktop_browser_runtime_client):
        assert "normalizeApiBase" in browser_client
        assert 'trimmed.endsWith("/api/v1")' in browser_client


def test_phase_68x_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68X_CUSTOMER_FRONTEND_PRODUCTION_ALIGNMENT.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68X" in text
        assert "production-workspace" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "client-production-runtime-panel" in text


def test_phase_68x_local_worker_cors_allows_production_frontend_ports() -> None:
    for relative in ("worker/main.py", "worker_client/runtime.py"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for origin in (
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5180",
            "http://127.0.0.1:5181",
        ):
            assert origin in text


def test_worker_consoles_expose_phase_68y_production_closed_loop_readiness() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperationProductionClosedLoopReadiness",
            "productionClosedLoopReadiness",
            "refreshProductionClosedLoopReadiness",
            "Phase 68Y Production Closed-Loop E2E Readiness",
            "client-production-closed-loop-readiness",
            "closedLoopReadinessTitle",
            "closedLoopReadinessCustomerExecution",
            "closedLoopReadinessMetricFeedback",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopReadiness",
            "CommercialOperationProductionClosedLoopStage",
            "productionClosedLoopReadiness",
            "/production-closed-loop/readiness",
            "force_metric_due",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-closed-loop-readiness",
            ".client-production-closed-loop-grid",
            ".client-production-closed-loop-rail",
            ".client-production-closed-loop-footer",
        ]:
            assert token in styles


def test_phase_68y_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Y_PRODUCTION_CLOSED_LOOP_E2E_READINESS.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Y" in text
        assert "production-closed-loop/readiness" in text
        assert "CommercialOperationProductionClosedLoopReadinessResponse" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "production_closed_loop_e2e_readiness" in text or "client-production-closed-loop-readiness" in text


def test_worker_consoles_expose_phase_68z_production_closed_loop_next_action() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperationProductionClosedLoopNextAction",
            "productionClosedLoopNextAction",
            "refreshProductionClosedLoopNextAction",
            "Phase 68Z Production Closed-Loop Controlled Next Action",
            "client-production-next-action-panel",
            "closedLoopNextActionTitle",
            "closedLoopNextActionEndpoint",
            "closedLoopNextActionEvidence",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopNextAction",
            "CommercialOperationProductionClosedLoopAction",
            "productionClosedLoopNextAction",
            "/production-closed-loop/next-action",
            "force_metric_due",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-next-action-panel",
            ".client-production-next-action-header",
            ".client-production-next-action-grid",
            ".client-production-next-action-footer",
        ]:
            assert token in styles


def test_phase_68z_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z_PRODUCTION_CLOSED_LOOP_NEXT_ACTION.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z" in text
        assert "production-closed-loop/next-action" in text
        assert "CommercialOperationProductionClosedLoopNextActionResponse" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "production_closed_loop_next_action" in text or "client-production-next-action-panel" in text


def test_worker_consoles_expose_phase_68z1_production_closed_loop_action_audit() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperationProductionClosedLoopActionAuditList",
            "productionClosedLoopActionAudits",
            "recordProductionClosedLoopActionConfirmation",
            "refreshProductionClosedLoopActionAudits",
            "Phase 68Z1 Controlled Action Audit",
            "client-production-action-audit-panel",
            "closedLoopActionAuditTitle",
            "closedLoopActionAuditConfirm",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopActionAuditRequest",
            "CommercialOperationProductionClosedLoopActionAuditRecord",
            "CommercialOperationProductionClosedLoopActionAuditList",
            "productionClosedLoopActionAudits",
            "recordProductionClosedLoopActionAudit",
            "/production-closed-loop/next-action/audit-records",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-action-audit-panel",
            ".client-production-action-audit-header",
            ".client-production-action-audit-grid",
            ".client-production-action-audit-footer",
        ]:
            assert token in styles


def test_phase_68z1_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z1_PRODUCTION_CLOSED_LOOP_ACTION_AUDIT.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z1" in text
        assert "production-closed-loop/next-action/audit-records" in text
        assert "CommercialOperationProductionClosedLoopActionAuditListResponse" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "production_closed_loop_next_action_audit" in text or "client-production-action-audit-panel" in text


def test_worker_consoles_expose_phase_68z2_production_closed_loop_action_result_binding() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "bindProductionClosedLoopActionResultFromLatest",
            "closedLoopActionResultBinding",
            "closedLoopActionResultBind",
            "result_binding_status",
            "target_record_id",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopActionResultBindingRequest",
            "CommercialOperationProductionClosedLoopActionResultBinding",
            "bindProductionClosedLoopActionResult",
            "/result-binding",
            "result_record_type",
            "result_record_id",
        ]:
            assert token in client


def test_phase_68z2_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z2_PRODUCTION_CLOSED_LOOP_ACTION_RESULT_BINDING.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z2" in text
        assert "result-binding" in text
        assert "CommercialOperationProductionClosedLoopActionResultBindingResponse" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "production_closed_loop_action_result_binding" in text


def test_worker_consoles_expose_phase_68z3_production_closed_loop_action_readiness_refresh() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "refreshProductionClosedLoopActionReadinessAfterBinding",
            "closedLoopActionReadinessRefresh",
            "closedLoopActionReadinessRefreshButton",
            "readiness_refresh_status",
            "setProductionClosedLoopNextAction(refresh.next_action)",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopActionReadinessRefreshRequest",
            "CommercialOperationProductionClosedLoopActionReadinessRefresh",
            "refreshProductionClosedLoopActionReadinessAfterResultBinding",
            "/result-binding/readiness-refresh",
            "stage_completed_after_binding",
        ]:
            assert token in client


def test_phase_68z3_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z3_PRODUCTION_CLOSED_LOOP_ACTION_READINESS_REFRESH.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z3" in text
        assert "readiness-refresh" in text
        assert "CommercialOperationProductionClosedLoopActionReadinessRefreshResponse" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "production_closed_loop_action_result_readiness_refresh" in text


def test_worker_consoles_expose_phase_68z4_production_closed_loop_action_record_validation() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "validateProductionClosedLoopActionResultRecordFromLatest",
            "closedLoopActionRecordValidation",
            "closedLoopActionRecordValidate",
            "result_record_validation_status",
            "customer_console_controlled_action_record_validation",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopActionResultRecordValidationRequest",
            "CommercialOperationProductionClosedLoopActionResultRecordValidation",
            "validateProductionClosedLoopActionResultRecord",
            "/result-binding/record-validation",
            "record_exists",
        ]:
            assert token in client


def test_phase_68z4_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z4_PRODUCTION_CLOSED_LOOP_ACTION_RESULT_RECORD_VALIDATION.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z4" in text
        assert "record-validation" in text
        assert "CommercialOperationProductionClosedLoopActionResultRecordValidationResponse" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "production_closed_loop_action_result_record_validation" in text


def test_worker_consoles_expose_phase_68z5_production_closed_loop_action_record_gate() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "closedLoopActionReadinessRefreshRecordBlocked",
            "需先通过记录校验",
            "Verify the bound record first",
            "result_record_validation_status !== \"record_verified\"",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "underlying_refresh_status",
            "record_validation_gate_status",
            "record_validation_required",
            "record_validation_passed",
            "record_validation_blocking_reasons",
        ]:
            assert token in client


def test_phase_68z5_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z5_PRODUCTION_CLOSED_LOOP_ACTION_RESULT_RECORD_GATE.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z5" in text
        assert "production_closed_loop_action_result_record_validation_gate" in text
        assert "CommercialOperationProductionClosedLoopActionReadinessRefreshResponse" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_phase_68z6_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z6_PRODUCTION_CLOSED_LOOP_VERIFIED_RESULT_RECORD_PASS.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z6" in text
        assert "record_verified" in text
        assert "record_validation_gate_status=record_validation_passed" in text
        assert "record_validation_required=false" in text
        assert "mark_optimization_decision_ready" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_phase_68z7_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z7_PRODUCTION_CLOSED_LOOP_OPTIMIZATION_DECISION_LIFECYCLE.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z7" in text
        assert "mark_optimization_decision_ready" in text
        assert "approve_optimization_decision" in text
        assert "ready_for_next_cycle" in text
        assert "stage_completed" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_phase_68z8_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_68Z8_PRODUCTION_CLOSED_LOOP_NEXT_CYCLE_DRAFT.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 68Z8" in text
        assert "production-closed-loop/next-cycle-draft" in text
        assert "CommercialOperationNextCycleDraftResponse" in text
        assert "OperationPlan" in text
        assert "ProductionTask" in text
        assert "ready_for_review" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_phase_69a_plan_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69A_CUSTOMER_MACHINE_PUBLISH_EXECUTION_STATUS.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69A" in text
        assert "publish-packages/{publish_package_id}/execution-status" in text
        assert "CommercialOperationPublishExecutionStatusResponse" in text
        assert "customer_machine_publish_execution_status" in text
        assert "queued" in text
        assert "running" in text
        assert "needs_operator" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text


def test_worker_consoles_expose_phase_69b_publish_execution_status_controls() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69B Customer-Machine Publish Execution Status",
            "publishExecutionStatusRecord",
            "publishExecutionStatusLoading",
            "updatePublishExecutionStatusFromClient",
            "publishExecutionLatestAttempt",
            "publishExecutionLatestProgress",
            "publishExecutionStatusTitle",
            "queued",
            "running",
            "needs_operator",
            "succeeded",
            "failed",
            "commercialOperationClient.updatePublishExecutionStatus",
            "client-publish-execution-panel",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationPublishExecutionStatus",
            "CommercialOperationPublishExecutionStatusValue",
            "updatePublishExecutionStatus",
            "/execution-status",
            "operator_confirmed",
            "customer_machine_id",
            "execution_status",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-publish-execution-panel",
            ".client-publish-execution-actions",
            ".client-publish-execution-grid",
            "repeat(auto-fit, minmax(180px, 1fr))",
            ".client-publish-execution-grid article.ready",
            ".client-publish-execution-grid article.blocked",
        ]:
            assert token in styles


def test_phase_69b_publish_execution_status_controls_are_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69B_CUSTOMER_CONSOLE_PUBLISH_EXECUTION_STATUS_CONTROLS.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69B" in text
        assert "CommercialOperationPublishExecutionStatus" in text
        assert "CommercialOperationPublishExecutionStatusValue" in text
        assert "updatePublishExecutionStatus" in text
        assert "client-publish-execution-panel" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_phase_69c_publish_execution_status_readiness_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69C_PRODUCTION_CLOSED_LOOP_PUBLISH_EXECUTION_STATUS_READINESS.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69C" in text
        assert "latest_records.publish_execution_status" in text
        assert "counts.publish_execution_statuses" in text
        assert "metadata.latest_publish_execution_status" in text
        assert "publish_execution_status_tracks_customer_machine_progress_before_result_capture" in text
        assert "record_customer_machine_publish_execution_status" in text
        assert "update_customer_machine_publish_execution_status" in text
        assert "execution_status=succeeded" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_worker_consoles_expose_phase_69d_publish_execution_readiness_visibility() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69D Publish Execution Status Visibility",
            "productionClosedLoopPublishExecutionStatusRecord",
            "productionClosedLoopPublishExecutionStatus",
            "productionClosedLoopPublishExecutionProgress",
            "productionClosedLoopPublishExecutionBlockingReason",
            "productionClosedLoopPublishExecutionStatusBlocked",
            "latest_records.publish_execution_status",
            "client-production-closed-loop-grid",
            "publishExecutionStatusTitle",
            "package_status",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-closed-loop-grid article.ready",
            ".client-production-closed-loop-grid article.blocked",
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_69f_action_audit_guided_validation() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69F Action Audit Guided Validation",
            "expectedActionResultStatusValue",
            "actionResultEndpointFor",
            "execution_status",
            "productionClosedLoopActionRecordValidationReady",
            "productionClosedLoopActionReadinessRefreshReady",
            "!productionClosedLoopActionRecordValidationReady",
            "!productionClosedLoopActionReadinessRefreshReady",
        ]:
            assert token in text


def test_worker_consoles_expose_phase_69g_action_audit_operator_checklist() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69G Action Audit Operator Checklist",
            "productionClosedLoopActionAuditChecklist",
            "productionClosedLoopActionAuditChecklistNext",
            "client-production-action-audit-checklist",
            "confirm",
            "bind",
            "validate",
            "refresh",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-action-audit-checklist",
            ".client-production-action-audit-checklist article.done",
            ".client-production-action-audit-checklist article.next",
            ".client-production-action-audit-checklist article.blocked",
        ]:
            assert token in styles


def test_worker_consoles_consume_phase_69h_server_action_audit_checklist_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_client, desktop_client):
        assert "operator_checklist: Record<string, unknown>[]" in text

    for text in (web_main, desktop_main):
        for token in [
            "productionClosedLoopServerActionAuditChecklist",
            "productionClosedLoopLocalActionAuditChecklist",
            "operator_checklist",
            "productionClosedLoopActionAuditChecklist",
        ]:
            assert token in text


def test_worker_consoles_expose_phase_69i_action_audit_primary_step() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69I Action Audit Primary Step",
            "productionClosedLoopActionAuditPrimaryStep",
            "recordProductionClosedLoopActionConfirmation",
            "bindProductionClosedLoopActionResultFromLatest",
            "validateProductionClosedLoopActionResultRecordFromLatest",
            "refreshProductionClosedLoopActionReadinessAfterBinding",
            "primary-action",
        ]:
            assert token in text


def test_worker_consoles_consume_phase_69j_server_action_audit_primary_step_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_client, desktop_client):
        assert "primary_step?: Record<string, unknown> | null" in text

    for text in (web_main, desktop_main):
        for token in [
            "productionClosedLoopServerActionAuditPrimaryStep",
            "primary_step",
            "productionClosedLoopActionAuditPrimaryStep",
            "productionClosedLoopActionAuditChecklist.find",
            "recordProductionClosedLoopActionConfirmation",
            "bindProductionClosedLoopActionResultFromLatest",
            "validateProductionClosedLoopActionResultRecordFromLatest",
            "refreshProductionClosedLoopActionReadinessAfterBinding",
        ]:
            assert token in text


def test_phase_69d_publish_execution_readiness_visibility_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69D_CUSTOMER_CONSOLE_PUBLISH_EXECUTION_READINESS_VISIBILITY.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69D" in text
        assert "productionClosedLoopPublishExecutionStatusRecord" in text
        assert "productionClosedLoopPublishExecutionStatus" in text
        assert "productionClosedLoopPublishExecutionProgress" in text
        assert "productionClosedLoopPublishExecutionBlockingReason" in text
        assert "productionClosedLoopPublishExecutionStatusBlocked" in text
        assert "client-production-closed-loop-grid" in text
        assert "package_status" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_phase_69e_publish_execution_status_record_validation_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69E_PRODUCTION_CLOSED_LOOP_PUBLISH_EXECUTION_STATUS_RECORD_VALIDATION.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69E" in text
        assert "PublishExecutionStatus" in text
        assert "metadata_record_key" in text
        assert "publish_execution_status" in text
        assert "package_metadata" in text
        assert "record_summary" in text
        assert "metadata_record" in text
        assert "metadata_record_missing" in text
        assert "record_verified" in text
        assert "customer_machine_publish_execution_status" in text
        assert "production_closed_loop_action_result_record_validation" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_phase_69f_action_audit_guided_validation_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69F_CUSTOMER_CONSOLE_ACTION_AUDIT_GUIDED_VALIDATION.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69F" in text
        assert "Phase 69F Action Audit Guided Validation" in text
        assert "expectedActionResultStatusValue" in text
        assert "actionResultEndpointFor" in text
        assert "execution_status" in text
        assert "productionClosedLoopActionRecordValidationReady" in text
        assert "productionClosedLoopActionReadinessRefreshReady" in text
        assert "record_verified" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_phase_69g_action_audit_operator_checklist_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69G_CUSTOMER_CONSOLE_ACTION_AUDIT_OPERATOR_CHECKLIST.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69G" in text
        assert "Phase 69G Action Audit Operator Checklist" in text
        assert "productionClosedLoopActionAuditChecklist" in text
        assert "productionClosedLoopActionAuditChecklistNext" in text
        assert "client-production-action-audit-checklist" in text
        assert ".client-production-action-audit-checklist article.done" in text
        assert ".client-production-action-audit-checklist article.next" in text
        assert ".client-production-action-audit-checklist article.blocked" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_phase_69h_action_audit_operator_checklist_contract_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69H_PRODUCTION_CLOSED_LOOP_ACTION_AUDIT_OPERATOR_CHECKLIST_CONTRACT.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69H" in text
        assert "CommercialOperationProductionClosedLoopActionAuditListResponse.operator_checklist" in text
        assert "CommercialOperationService._production_closed_loop_action_operator_checklist" in text
        assert "production_closed_loop_action_audit_operator_checklist" in text
        assert "operator_checklist_contract" in text
        assert "productionClosedLoopServerActionAuditChecklist" in text
        assert "productionClosedLoopLocalActionAuditChecklist" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_phase_69i_action_audit_primary_step_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69I_CUSTOMER_CONSOLE_ACTION_AUDIT_PRIMARY_STEP.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69I" in text
        assert "Phase 69I Action Audit Primary Step" in text
        assert "productionClosedLoopActionAuditPrimaryStep" in text
        assert "recordProductionClosedLoopActionConfirmation" in text
        assert "bindProductionClosedLoopActionResultFromLatest" in text
        assert "validateProductionClosedLoopActionResultRecordFromLatest" in text
        assert "refreshProductionClosedLoopActionReadinessAfterBinding" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


def test_phase_69j_action_audit_primary_step_contract_is_documented() -> None:
    docs = [
        ROOT / "docs/PHASE_69J_PRODUCTION_CLOSED_LOOP_ACTION_AUDIT_PRIMARY_STEP_CONTRACT.md",
        ROOT / "docs/PHASE_INDEX.md",
        ROOT / "docs/CURRENT_NEXT_PHASE.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/PROJECT_STATUS.md",
        ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 69J" in text
        assert "CommercialOperationProductionClosedLoopActionAuditListResponse.primary_step" in text
        assert "primary_step_contract" in text
        assert "production_closed_loop_action_audit_primary_step" in text
        assert "productionClosedLoopServerActionAuditPrimaryStep" in text
        assert "productionClosedLoopActionAuditPrimaryStep" in text
        assert "confirm" in text
        assert "bind" in text
        assert "validate" in text
        assert "refresh" in text
        assert "OpenClaw" in text
        assert "Playwright" in text


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
            "data-has-work={simpleMaintenanceCount > 0 ? \"true\" : \"false\"}",
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


def test_phase_71s_client_operator_ui_simplification_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71S_CLIENT_OPERATOR_UI_SIMPLIFICATION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "client-home-detail-drawer",
            "client-operation-desk-drawer",
            "production-runtime-strip",
            "simple-operator-workbench",
            "simple-goal-box",
            "simple-progress-card",
            "operationDetailsHint",
            "client-operation-desk",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-home-detail-drawer",
            ".client-operation-desk-drawer",
            ".client-task-workbench",
            "flex-direction: column",
            "order: 1",
            "order: 5",
            ".production-runtime-head::-webkit-details-marker",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71S Client Operator UI Simplification" in text
        assert "client-operation-desk-drawer" in text
        assert "simple-operator-workbench" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_71t_client_codex_minimal_ui_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71T_CLIENT_CODEX_MINIMAL_UI.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "codex-simple-client",
            "simpleFocusStats",
            "simpleMaintenanceCount",
            "simple-focus-strip",
            "data-has-work={simpleMaintenanceCount > 0 ? \"true\" : \"false\"}",
            'const [input, setInput] = useState("");',
            "告诉我今天要推进什么",
            "输入运营目标，例如：为商 K 活动生成一条短视频方案，并先进入审批。",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".chat-panel.codex-simple-client",
            "width: min(900px, calc(100vw - 24px))",
            ".simple-focus-strip",
            ".simple-focus-item",
            "overflow-x: auto",
            ".maintenance-drawer[data-has-work=\"true\"]",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71T Client Codex Minimal UI" in text
        assert "codex-simple-client" in text
        assert "simple-focus-strip" in text
        assert "maintenance-drawer" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_71u_client_codex_focus_shell_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71U_CLIENT_CODEX_FOCUS_SHELL.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "client-runtime-companion",
            "client-runtime-summary",
            "client-runtime-summary-actions",
            "client-home-detail-drawer",
            "operator-status-grid",
            "production-runtime-strip",
            "simple-focus-strip",
            "simple-progress-card",
            "status.runtime_running",
            "status.heartbeat_running",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".operator-home.client-runtime-companion",
            ".client-runtime-summary",
            ".client-runtime-summary-actions",
            ".operator-home.client-runtime-companion .client-home-detail-drawer",
            ".operator-home.client-runtime-companion .client-status-rail",
            "width: min(760px, 100%)",
            "display: inline-flex",
            "border-top: 1px solid #e6ebf2",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71U Client Codex Focus Shell" in text
        assert "client-runtime-companion" in text
        assert "client-runtime-summary" in text
        assert "client-home-detail-drawer" in text
        assert "simple-focus-strip" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_71v_client_action_inbox_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71V_CLIENT_ACTION_INBOX.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "simpleInboxItems",
            "SimpleInboxItem",
            "simple-action-inbox",
            "simple-action-inbox-item",
            "openClientDetailPanel",
            "commercial-approvals-panel",
            "tasks-panel",
            "outputs-panel",
            "client-project-workbench",
            "simpleInboxApprovals",
            "simpleInboxRecovery",
            "simpleInboxOutputs",
            "simpleInboxActive",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-action-inbox",
            ".simple-action-inbox-head",
            ".simple-action-inbox-list",
            ".simple-action-inbox-item",
            ".simple-action-inbox-item.needs-action",
            ".simple-action-inbox-item.current",
            ".simple-action-inbox-item.done",
            "grid-template-columns: minmax(60px, 0.5fr) auto minmax(0, 1fr) auto",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71V Client Action Inbox" in text
        assert "simpleInboxItems" in text
        assert "simple-action-inbox" in text
        assert "openClientDetailPanel" in text
        assert "client-project-workbench" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_71w_client_creation_review_shortcuts_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71W_CLIENT_CREATION_REVIEW_SHORTCUTS.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "simpleReviewCards",
            "SimpleReviewCard",
            "simple-review-strip",
            "simple-review-card-row",
            "simple-review-card",
            "simpleReviewWorkflow",
            "simpleReviewOutput",
            "pendingWorkflowSelections",
            "approvedWorkflowSelections",
            "pendingOutputCandidates",
            "selectedOutputCandidates",
            "openClientDetailPanel(\"client-project-workbench\")",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-review-strip",
            ".simple-review-strip-head",
            ".simple-review-card-row",
            ".simple-review-card",
            ".simple-review-card.needs-action",
            ".simple-review-card.current",
            ".simple-review-card.done",
            "grid-template-columns: repeat(2, minmax(0, 1fr))",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71W Client Creation Review Shortcuts" in text
        assert "simpleReviewCards" in text
        assert "simple-review-strip" in text
        assert "simple-review-card" in text
        assert "client-project-workbench" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_71x_client_first_screen_priority_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71X_CLIENT_FIRST_SCREEN_PRIORITY.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        inbox_index = text.index('<div className="simple-action-inbox"')
        review_index = text.index('<div className="simple-review-strip"')
        progress_index = text.index('<div className={`simple-progress-card ${simpleCurrentStage.status}`}')
        assert inbox_index < review_index < progress_index
        assert "client-project-workbench" in text
        assert "openClientDetailPanel(\"client-project-workbench\")" in text

    for styles in (web_styles, desktop_styles):
        assert ".simple-action-inbox {\n  order: 3;" in styles
        assert ".simple-review-strip {\n  order: 4;" in styles
        assert ".simple-progress-card {\n  order: 5;" in styles
        assert ".simple-goal-box textarea {\n  min-height: 54px;" in styles
        assert "min-height: 34px;\n  padding: 7px 10px;" in styles
        assert ".codex-simple-client .simple-operator-header p {\n  display: none;" in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71X Client First Screen Priority" in text
        assert "simple-action-inbox" in text
        assert "simple-review-strip" in text
        assert "simple-progress-card" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_71y_client_project_focus_navigation_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71Y_CLIENT_PROJECT_FOCUS_NAVIGATION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "clientProjectFocusCards",
            "ClientProjectFocusCard",
            "client-project-focus-strip",
            "client-project-focus-grid",
            "client-project-focus-card",
            "scrollClientProjectFocus",
            "projectFocusTitle",
            "projectFocusApproval",
            "projectFocusData",
            "client-project-section-plans",
            "client-project-section-materials",
            "client-project-section-workflows",
            "client-project-section-outputs",
            "client-project-section-publish",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-project-focus-strip",
            ".client-project-focus-head",
            ".client-project-focus-grid",
            ".client-project-focus-card",
            ".client-project-focus-card.needs-action",
            ".client-project-focus-card.current",
            ".client-project-focus-card.done",
            "grid-template-columns: repeat(6, minmax(0, 1fr))",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71Y Client Project Focus Navigation" in text
        assert "clientProjectFocusCards" in text
        assert "client-project-focus-strip" in text
        assert "scrollClientProjectFocus" in text
        assert "client-project-section-workflows" in text
        assert "client-project-section-outputs" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_71z_client_project_support_diagnostics_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_71Z_CLIENT_PROJECT_SUPPORT_DIAGNOSTICS_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        focus_index = text.index('<div className="client-project-focus-strip"')
        support_index = text.index("client-project-support-drawer")
        actions_index = text.index('<div className="client-project-actions">')
        assert focus_index < support_index < actions_index
        for token in [
            "clientProjectSupportAttention",
            "clientProjectSupportStatus",
            "client-project-support-drawer",
            "client-project-support-grid",
            "data-has-attention",
            "projectSupportTitle",
            "projectSupportNeedsReview",
            "projectSupportQuiet",
            "client-production-runtime-panel",
            "client-production-intervention-panel",
            "client-production-closed-loop-readiness",
            "client-production-next-action-panel",
            "client-production-action-audit-panel",
            "client-server-pressure-panel",
            "client-project-process-panel",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-project-support-drawer",
            ".client-project-support-drawer > summary",
            ".client-project-support-drawer[data-has-attention=\"true\"]",
            ".client-project-support-drawer[open] > summary",
            ".client-project-support-grid",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 71Z Client Project Support Diagnostics Drawer" in text
        assert "clientProjectSupportAttention" in text
        assert "clientProjectSupportStatus" in text
        assert "client-project-support-drawer" in text
        assert "client-project-support-grid" in text
        assert "data-has-attention" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72a_client_project_primary_action_lane_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72A_CLIENT_PROJECT_PRIMARY_ACTION_LANE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        support_index = text.index("client-project-support-drawer")
        primary_index = text.index("client-project-primary-actions")
        action_drawer_index = text.index("client-project-action-drawer")
        actions_index = text.index('<div className="client-project-actions">')
        project_grid_index = text.index('<div className="client-project-grid">')
        assert support_index < primary_index < action_drawer_index < actions_index < project_grid_index
        for token in [
            "ClientProjectPrimaryAction",
            "clientProjectPrimaryActions",
            "clientProjectPrimaryReadyCount",
            "client-project-primary-actions",
            "client-project-primary-action-grid",
            "client-project-primary-action",
            "client-project-action-drawer",
            "projectPrimaryActionTitle",
            "projectPrimaryActionReady",
            "projectPrimaryActionOpen",
            "projectActionDrawerTitle",
            "projectActionDrawerSummary",
            "scrollClientProjectFocus(\"client-project-section-workflows\")",
            "scrollClientProjectFocus(\"client-project-section-outputs\")",
            "scrollClientProjectFocus(\"client-project-section-publish\")",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-project-primary-actions",
            ".client-project-primary-actions-head",
            ".client-project-primary-action-grid",
            ".client-project-primary-action",
            ".client-project-primary-action.needs-action",
            ".client-project-primary-action.current",
            ".client-project-primary-action.done",
            ".client-project-action-drawer",
            ".client-project-action-drawer > summary",
            ".client-project-action-drawer[open] > summary",
            ".client-project-action-drawer:not([open]) .client-project-actions",
            ".client-project-action-drawer .client-project-actions",
            ".client-operation-desk-drawer:not([open]) .client-operation-desk",
            ".client-home-detail-drawer:not([open]) .operator-support-grid",
            ".maintenance-drawer:not([open]) > :not(summary)",
            "grid-template-columns: repeat(6, minmax(0, 1fr))",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72A Client Project Primary Action Lane" in text
        assert "ClientProjectPrimaryAction" in text
        assert "clientProjectPrimaryActions" in text
        assert "clientProjectPrimaryReadyCount" in text
        assert "client-project-primary-actions" in text
        assert "client-project-primary-action-grid" in text
        assert "client-project-action-drawer" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72b_client_project_decision_queue_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72B_CLIENT_PROJECT_DECISION_QUEUE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        primary_index = text.index("client-project-primary-actions")
        decision_index = text.index("client-project-decision-lane")
        action_drawer_index = text.index("client-project-action-drawer")
        records_drawer_index = text.index('className="client-project-records-drawer" open={activeSimpleWorkspacePage !== "overview" && activeSimpleWorkspacePage !== "planning"}')
        project_grid_index = text.index('<div className="client-project-grid">')
        assert primary_index < decision_index < action_drawer_index < records_drawer_index < project_grid_index
        for token in [
            "ClientProjectDecisionCard",
            "clientProjectDecisionCandidates",
            "clientProjectDecisionCards",
            "clientProjectDecisionTotalCount",
            "client-project-decision-lane",
            "client-project-decision-grid",
            "client-project-decision-card",
            "openClientProjectRecordsAndScroll",
            "client-project-records-drawer",
            "projectDecisionTitle",
            "projectDecisionReady",
            "projectDecisionOpen",
            "projectRecordsTitle",
            "projectRecordsSummary",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-project-decision-lane",
            ".client-project-decision-lane[data-has-decision=\"true\"]",
            ".client-project-decision-head",
            ".client-project-decision-grid",
            ".client-project-decision-card",
            ".client-project-decision-empty",
            ".client-project-records-drawer",
            ".client-project-records-drawer > summary",
            ".client-project-records-drawer:not([open]) .client-project-grid",
            ".client-project-records-drawer:not([open]) .client-project-boundary",
            ".client-project-records-drawer .client-project-grid",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72B Client Project Decision Queue" in text
        assert "ClientProjectDecisionCard" in text
        assert "clientProjectDecisionCandidates" in text
        assert "clientProjectDecisionCards" in text
        assert "clientProjectDecisionTotalCount" in text
        assert "client-project-decision-lane" in text
        assert "client-project-records-drawer" in text
        assert "openClientProjectRecordsAndScroll" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72c_client_project_current_decision_focus_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72C_CLIENT_PROJECT_CURRENT_DECISION_FOCUS.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        focus_index = text.index("client-project-decision-focus")
        action_drawer_index = text.index("client-project-action-drawer")
        records_drawer_index = text.index('className="client-project-records-drawer" open={activeSimpleWorkspacePage !== "overview" && activeSimpleWorkspacePage !== "planning"}')
        assert focus_index < action_drawer_index < records_drawer_index
        for token in [
            "clientProjectCurrentDecision",
            "clientProjectSecondaryDecisionCards",
            "client-project-decision-focus",
            "client-project-decision-focus-actions",
            "projectDecisionCurrent",
            "projectDecisionDetail",
            "primaryLabel",
            "primaryDisabled",
            "onPrimary",
            "secondaryLabel",
            "secondaryDisabled",
            "onSecondary",
            "approveMaterial",
            "rejectMaterial",
            "rejectFinal",
            "rejectPublish",
            "rejectMetric",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-project-decision-focus",
            ".client-project-decision-focus > div:first-child",
            ".client-project-decision-focus strong",
            ".client-project-decision-focus p",
            ".client-project-decision-focus-actions",
            ".client-project-decision-focus span",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72C Client Project Current Decision Focus" in text
        assert "clientProjectCurrentDecision" in text
        assert "clientProjectSecondaryDecisionCards" in text
        assert "client-project-decision-focus" in text
        assert "client-project-decision-focus-actions" in text
        assert "projectDecisionCurrent" in text
        assert "projectDecisionDetail" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72d_client_attention_current_task_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72D_CLIENT_ATTENTION_CURRENT_TASK.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        current_index = text.index("simple-action-current")
        review_index = text.index('<div className="simple-review-strip"')
        maintenance_index = text.index('<details className="maintenance-drawer"')
        assert current_index < review_index < maintenance_index
        for token in [
            "simpleCurrentInboxItem",
            "simpleSecondaryInboxItems",
            "simpleInboxTotalCount",
            "simple-action-current-stack",
            "simple-action-current",
            "simple-action-secondary-list",
            "simpleInboxCurrent",
            "simpleInboxMore",
            "maintenanceCurrent",
            "workbenchCopy.maintenanceCurrent",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-action-current-stack",
            ".simple-action-current",
            ".simple-action-current > div:first-child",
            ".simple-action-current strong",
            ".simple-action-current.needs-action",
            ".simple-action-current.current",
            ".simple-action-current.done",
            ".simple-action-secondary-list",
            ".maintenance-drawer > summary em",
            "grid-template-columns: minmax(0, 1fr) auto",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72D Client Attention Current Task" in text
        assert "simpleCurrentInboxItem" in text
        assert "simpleSecondaryInboxItems" in text
        assert "simpleInboxTotalCount" in text
        assert "simple-action-current" in text
        assert "simple-action-secondary-list" in text
        assert "maintenanceCurrent" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72e_client_creation_current_review_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72E_CLIENT_CREATION_CURRENT_REVIEW.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        review_index = text.index('<div className="simple-review-strip"')
        current_review_index = text.index("simple-review-current")
        progress_index = text.index('<div className={`simple-progress-card ${simpleCurrentStage.status}`}')
        assert review_index < current_review_index < progress_index
        for token in [
            "simpleReviewStatePriority",
            "simpleCurrentReviewCard",
            "simpleSecondaryReviewCards",
            "simpleReviewAttentionCount",
            "simple-review-current-stack",
            "simple-review-current",
            "simple-review-secondary-list",
            "simpleReviewCurrent",
            "simpleReviewMore",
            "simpleReviewStatePriority[card.state]",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-review-strip-head",
            ".simple-review-strip-head strong",
            ".simple-review-current-stack",
            ".simple-review-current",
            ".simple-review-current > div:first-child",
            ".simple-review-current strong",
            ".simple-review-current.needs-action",
            ".simple-review-current.current",
            ".simple-review-current.done",
            ".simple-review-secondary-list",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72E Client Creation Current Review" in text
        assert "simpleReviewStatePriority" in text
        assert "simpleCurrentReviewCard" in text
        assert "simpleSecondaryReviewCards" in text
        assert "simpleReviewAttentionCount" in text
        assert "simple-review-current" in text
        assert "simple-review-secondary-list" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72f_client_progress_current_stage_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72F_CLIENT_PROGRESS_CURRENT_STAGE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        progress_index = text.index('<div className={`simple-progress-card ${simpleCurrentStage.status}`}')
        current_progress_index = text.index("simple-progress-current")
        trail_index = text.index('aria-label={workbenchCopy.simpleProgressTrail}')
        assert progress_index < current_progress_index < trail_index
        for token in [
            "simpleProgressDoneCount",
            "simpleProgressCurrentSummary",
            "simpleProgressCurrent",
            "simpleProgressTrail",
            "simple-progress-current",
            "goalStatusStateLabels[simpleCurrentStage.status]",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-progress-current",
            ".simple-progress-current > div:first-child",
            ".simple-progress-current strong",
            ".simple-progress-current.current",
            ".simple-progress-current.done",
            ".simple-progress-current.needs-action",
            "overflow-x: auto",
            "scrollbar-width: thin",
            ".simple-progress-stage {\n  flex: 0 0 auto;",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72F Client Progress Current Stage" in text
        assert "simpleProgressDoneCount" in text
        assert "simpleProgressCurrentSummary" in text
        assert "simpleProgressCurrent" in text
        assert "simpleProgressTrail" in text
        assert "simple-progress-current" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72g_client_first_viewport_action_priority_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72G_CLIENT_FIRST_VIEWPORT_ACTION_PRIORITY.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        start_drawer_index = text.index('<details className="simple-start-drawer">')
        goal_box_index = text.index('<div className="chat-input-row command-input-row simple-goal-box">')
        action_index = text.index('<div className="simple-action-inbox"')
        assert start_drawer_index < goal_box_index < action_index
        for token in [
            "simpleContextTitle",
            "simpleContextSummary",
            "simple-start-drawer",
            "simple-start-drawer-body",
            "simple-focus-strip",
            "simple-template-row",
            "selectedGoalTemplate.title",
            "workbenchCopy.simpleContextSummary",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-start-drawer",
            ".simple-start-drawer > summary",
            ".simple-start-drawer > summary span",
            ".simple-start-drawer > summary strong",
            ".simple-start-drawer[open] > summary",
            ".simple-start-drawer:not([open]) .simple-start-drawer-body",
            ".simple-start-drawer-body",
            "text-overflow: ellipsis",
            "white-space: nowrap",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72G Client First Viewport Action Priority" in text
        assert "simpleContextTitle" in text
        assert "simpleContextSummary" in text
        assert "simple-start-drawer" in text
        assert "simple-start-drawer-body" in text
        assert "simple-focus-strip" in text
        assert "simple-template-row" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72h_client_single_focus_context_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72H_CLIENT_SINGLE_FOCUS_CONTEXT_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        action_index = text.index('<div className="simple-action-inbox"')
        context_index = text.index('<details className="simple-project-context-drawer">')
        context_body_index = text.index('<div className="simple-project-context-body">')
        review_index = text.index('<div className="simple-review-strip"', context_body_index)
        progress_index = text.index("simple-progress-card ${simpleCurrentStage.status}", context_body_index)
        detail_index = text.index('<details className="operator-detail-drawer">')
        assert action_index < context_index < detail_index
        assert context_index < context_body_index < review_index < progress_index
        for token in [
            "simpleProjectContextTitle",
            "simpleProjectContextSummary",
            "simpleProjectContextReview",
            "simpleProjectContextProgress",
            "simple-project-context-drawer",
            "simple-project-context-body",
            "simple-review-strip",
            "simple-progress-card",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-project-context-drawer",
            ".simple-project-context-drawer > summary",
            ".simple-project-context-drawer > summary span",
            ".simple-project-context-drawer > summary strong",
            ".simple-project-context-drawer[open] > summary",
            ".simple-project-context-drawer:not([open]) .simple-project-context-body",
            ".simple-project-context-body",
            ".simple-project-context-body .simple-review-strip",
            ".simple-project-context-body .simple-progress-card",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72H Client Single Focus Context Drawer" in text
        assert "simpleProjectContextTitle" in text
        assert "simpleProjectContextSummary" in text
        assert "simpleProjectContextReview" in text
        assert "simpleProjectContextProgress" in text
        assert "simple-project-context-drawer" in text
        assert "simple-project-context-body" in text
        assert "simple-review-strip" in text
        assert "simple-progress-card" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text


def test_phase_72j_client_delivery_audit_focus_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72J_CLIENT_DELIVERY_AUDIT_FOCUS.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        inbox_index = text.index('<div className="simple-action-inbox"')
        audit_index = text.index('className={`simple-delivery-audit-card ${simpleDeliveryAuditState}`}')
        context_index = text.index('<details className="simple-project-context-drawer">')
        assert inbox_index < audit_index < context_index
        for token in [
            "simpleDeliveryAuditTitle",
            "simpleDeliveryAuditReady",
            "simpleDeliveryAuditBlocked",
            "simpleDeliveryAuditWaiting",
            "simpleDeliveryAuditExternal",
            "simpleDeliveryAuditOperator",
            "simpleDeliveryAuditBlockers",
            "simpleDeliveryAuditActions",
            "simpleDeliveryAuditNext",
            "simpleDeliveryAuditRefresh",
            "simpleDeliveryAuditLoaded",
            "simpleDeliveryAuditBlockerCount",
            "simpleDeliveryAuditExternalCount",
            "simpleDeliveryAuditOperatorCount",
            "simpleDeliveryAuditPrimaryAction",
            "productionClosedLoopDeliveryAuditNextActionPlan",
            "productionClosedLoopDeliveryAuditOperatorQueue",
            "refreshProductionClosedLoopReadiness",
            "Phase 72J Client Delivery Audit Focus",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-delivery-audit-card",
            ".simple-delivery-audit-card.needs-action",
            ".simple-delivery-audit-card.current",
            ".simple-delivery-audit-card.waiting",
            ".simple-delivery-audit-card.done",
            ".simple-delivery-audit-main",
            ".simple-delivery-audit-stats",
            ".simple-delivery-audit-next",
            "grid-template-columns: minmax(0, 0.95fr) auto minmax(220px, 1fr)",
            "white-space: normal",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72J Client Delivery Audit Focus" in text
        assert "simple-delivery-audit-card" in text
        assert "simpleDeliveryAuditTitle" in text
        assert "productionClosedLoopDeliveryAuditNextActionPlan" in text
        assert "productionClosedLoopDeliveryAuditOperatorQueue" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72k_client_delivery_audit_quick_action_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72K_CLIENT_DELIVERY_AUDIT_QUICK_ACTION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72K Client Delivery Audit Quick Action" in text
        audit_index = text.index('className={`simple-delivery-audit-card ${simpleDeliveryAuditState}`}')
        record_button_index = text.index("recordClientDeliveryAuditOperatorQueueInProgress", audit_index)
        refresh_index = text.index("refreshProductionClosedLoopReadiness", audit_index)
        detail_index = text.index('openClientDetailPanel("client-project-workbench")', audit_index)
        assert audit_index < record_button_index < refresh_index < detail_index
        for token in [
            "simpleDeliveryAuditRecordAction",
            "simpleDeliveryAuditRecordingAction",
            "simpleDeliveryAuditInProgress",
            "simpleDeliveryAuditQueueItem",
            "simpleDeliveryAuditRecordStatus",
            "simpleDeliveryAuditRecordInProgress",
            "simpleDeliveryAuditRecordDisabled",
            "simpleDeliveryAuditRecordLabel",
            "deliveryAuditOperatorQueueRecordLoading",
            "recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)",
            "productionClosedLoopDeliveryAuditOperatorQueue?.first_item",
            "production_closed_loop_delivery_audit_operator_queue_record",
        ]:
            assert token in text

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72K Client Delivery Audit Quick Action" in text
        assert "simpleDeliveryAuditRecordAction" in text
        assert "simpleDeliveryAuditQueueItem" in text
        assert "recordClientDeliveryAuditOperatorQueueInProgress" in text
        assert "production_closed_loop_delivery_audit_operator_queue_record" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72l_client_runbook_evidence_quick_path_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72L_CLIENT_RUNBOOK_EVIDENCE_QUICK_PATH.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72L Client Runbook Evidence Quick Path" in text
        audit_index = text.index('className={`simple-delivery-audit-card ${simpleDeliveryAuditState}`}')
        evidence_index = text.index("recordClientDeliveryAuditBlockerRunbookEvidence", audit_index)
        refresh_index = text.index("refreshProductionClosedLoopReadiness", audit_index)
        detail_index = text.index('openClientDetailPanel("client-project-workbench")', audit_index)
        assert audit_index < evidence_index < refresh_index < detail_index
        for token in [
            "simpleDeliveryAuditEvidence",
            "simpleDeliveryAuditRecordEvidence",
            "simpleDeliveryAuditRecordingEvidence",
            "simpleDeliveryAuditRunbookPackage",
            "simpleDeliveryAuditRunbookMissingCount",
            "simpleDeliveryAuditRunbookBlockedCount",
            "simpleDeliveryAuditRunbookEvidenceCount",
            "simpleDeliveryAuditRunbookCoverageStatus",
            "simpleDeliveryAuditEvidenceDisabled",
            "simpleDeliveryAuditEvidenceLabel",
            "deliveryAuditBlockerRunbookEvidenceLoading",
            "recordClientDeliveryAuditBlockerRunbookEvidence(simpleDeliveryAuditRunbookPackage)",
            "productionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage",
            "productionClosedLoopDeliveryAuditBlockerRunbookPackages",
            "production_closed_loop_delivery_audit_blocker_runbook_evidence",
        ]:
            assert token in text

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72L Client Runbook Evidence Quick Path" in text
        assert "simpleDeliveryAuditEvidence" in text
        assert "simpleDeliveryAuditRunbookPackage" in text
        assert "recordClientDeliveryAuditBlockerRunbookEvidence" in text
        assert "production_closed_loop_delivery_audit_blocker_runbook_evidence" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72m_client_runbook_evidence_submission_form_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72M_CLIENT_RUNBOOK_EVIDENCE_SUBMISSION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72M client runbook evidence submission" in text
        refresh_index = text.index("refreshClientDeliveryAuditBlockerRunbookEvidenceReadiness")
        form_index = text.index('className="client-production-delivery-audit-runbook-evidence-form"')
        list_index = text.index('className="client-production-delivery-audit-runbook-list"')
        assert refresh_index < form_index < list_index
        for token in [
            "ClientRunbookEvidenceStatus",
            "ClientRunbookEvidenceDraft",
            "initialClientRunbookEvidenceDraft",
            "clientRunbookEvidenceDraft",
            "setClientRunbookEvidenceDraft",
            "submitClientDeliveryAuditBlockerRunbookEvidence",
            "operator_confirmation_required_for_runbook_evidence",
            "evidence_summary_or_link_required_for_runbook_evidence",
            "evidence_links: evidenceLinks",
            "evidence_status: evidenceStatus",
            "operator_confirmed: confirmationRequired ? true : clientRunbookEvidenceDraft.operatorConfirmed",
            "Submitted from worker_console",
            "runbook_evidence_control: \"operator_submission_form\"",
            "recordProductionClosedLoopDeliveryAuditBlockerRunbookEvidence",
            "production_closed_loop_delivery_audit_blocker_runbook_evidence",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-delivery-audit-runbook-evidence-form",
            ".client-production-delivery-audit-runbook-evidence-form input",
            ".client-production-delivery-audit-runbook-evidence-form select",
            ".client-production-delivery-audit-runbook-evidence-form textarea",
            ".client-production-delivery-audit-runbook-evidence-form .confirmation",
            ".client-production-delivery-audit-runbook-evidence-form .actions",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72M Client Runbook Evidence Submission" in text
        assert "client-production-delivery-audit-runbook-evidence-form" in text
        assert "submitClientDeliveryAuditBlockerRunbookEvidence" in text
        assert "operator_confirmation_required_for_runbook_evidence" in text
        assert "evidence_summary_or_link_required_for_runbook_evidence" in text
        assert "production_closed_loop_delivery_audit_blocker_runbook_evidence" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72n_client_runbook_readiness_refresh_gate_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72N_CLIENT_RUNBOOK_READINESS_REFRESH_GATE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72N Client Runbook Readiness Refresh Gate" in text
        for token in [
            "clientDeliveryAuditBlockerRunbookPackageCount",
            "clientDeliveryAuditBlockerRunbookResolvedCount",
            "clientDeliveryAuditBlockerRunbookMissingEvidenceCount",
            "clientDeliveryAuditBlockerRunbookBlockedCount",
            "clientDeliveryAuditBlockerRunbookNeedsFollowUpCount",
            "clientDeliveryAuditBlockerRunbookDismissedCount",
            "clientDeliveryAuditBlockerRunbookSubmittedCount",
            "clientDeliveryAuditBlockerRunbookRefreshReady",
            "clientDeliveryAuditBlockerRunbookRefreshRequired",
            "clientDeliveryAuditBlockerRunbookRefreshGateReason",
            "clientDeliveryAuditBlockerRunbookRefreshDisabled",
            "clientDeliveryAuditBlockerRunbookRefreshLabel",
            "runbook_evidence_readiness_refresh_blocked",
            "resolved_evidence_ready_for_refresh",
            "Resolve evidence before refresh",
            "client-production-delivery-audit-runbook-refresh-gate",
            "refresh-gate:{clientDeliveryAuditBlockerRunbookRefreshGateReason}",
            "disabled={clientDeliveryAuditBlockerRunbookRefreshDisabled}",
            "production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        assert ".client-production-delivery-audit-runbook-refresh-gate" in styles
        assert "overflow-wrap: anywhere" in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72N Client Runbook Readiness Refresh Gate" in text
        assert "clientDeliveryAuditBlockerRunbookRefreshReady" in text
        assert "clientDeliveryAuditBlockerRunbookRefreshGateReason" in text
        assert "runbook_evidence_readiness_refresh_blocked" in text
        assert "production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72o_client_codex_minimal_workspace_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72O_CLIENT_CODEX_MINIMAL_WORKSPACE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72O Client Codex Minimal Workspace" in text
        for token in [
            "simpleServerPressureState",
            "SimpleMinimalStatusCard",
            "simpleMinimalStatusCards",
            "server-pressure",
            "project-progress",
            "creation-review",
            "delivery-readiness",
            "simple-command-status-strip",
            "simple-command-status-pill",
            "projectWorkbenchCopy.serverPressureTitle",
            "serverPressureLabel",
            "serverPressureScore",
            "clientObjectiveCompletionPercent",
            "openClientDetailPanel(card.panelId)",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-command-status-strip",
            ".simple-command-status-pill",
            ".simple-command-status-pill.current",
            ".simple-command-status-pill.done",
            ".simple-command-status-pill.needs-action",
            ".codex-simple-client .simple-start-drawer",
            ".codex-simple-client .simple-delivery-audit-stats",
            ".simple-action-secondary-list",
            "grid-template-columns: repeat(2, minmax(0, 1fr))",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72O Client Codex Minimal Workspace" in text
        assert "simpleMinimalStatusCards" in text
        assert "simple-command-status-strip" in text
        assert "simple-command-status-pill" in text
        assert "serverPressureScore" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72p_client_session_controls_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72P_CLIENT_SESSION_CONTROLS_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72P Client Session Controls Drawer" in text
        title_actions_index = text.index("client-session-title-actions")
        maintenance_index = text.index('<details className="maintenance-drawer"')
        session_drawer_index = text.index('className="simple-session-drawer"')
        assert title_actions_index < maintenance_index < session_drawer_index
        for token in [
            "client-session-title-actions",
            "simple-session-drawer",
            "simple-session-actions",
            "createThread",
            "refreshConversation",
            "workbenchCopy.createThread",
            "workbenchCopy.refreshWork",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".codex-simple-client .client-session-title-actions",
            "display: none",
            ".simple-session-drawer",
            ".simple-session-actions",
            ".simple-session-actions .refresh-button",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72P Client Session Controls Drawer" in text
        assert "client-session-title-actions" in text
        assert "simple-session-drawer" in text
        assert "simple-session-actions" in text
        assert "createThread" in text
        assert "refreshConversation" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72q_client_mode_switch_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72Q_CLIENT_MODE_SWITCH_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72Q Client Mode Switch Drawer" in text
        assert 'className="operator-page-tabs operator-page-mode-drawer"' in text
        for token in [
            "operator-page-mode-drawer",
            "operator-page-tab-actions",
            "Current mode",
            "当前模式",
            'setOperatorPage("operations")',
            'setOperatorPage("knowledge")',
            "copy.pageOperations",
            "copy.pageKnowledge",
            "KnowledgeBasePanel",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".operator-page-tabs > summary",
            ".operator-page-tabs > summary::-webkit-details-marker",
            ".operator-page-tabs > summary strong",
            ".operator-page-tabs[open] > summary",
            ".operator-page-tab-actions",
            ".operator-page-mode-drawer:not([open]) .operator-page-tab-actions",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72Q Client Mode Switch Drawer" in text
        assert "operator-page-mode-drawer" in text
        assert "operator-page-tab-actions" in text
        assert "setOperatorPage" in text
        assert "knowledge base" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72r_client_runtime_action_compression_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72R_CLIENT_RUNTIME_ACTION_COMPRESSION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72R Client Runtime Controls Drawer" in text
        assert "Phase 72R Client Delivery Audit Secondary Actions" in text
        runtime_drawer_index = text.index('className="client-runtime-controls-drawer"')
        runtime_actions_index = text.index('className="client-runtime-summary-actions"')
        audit_primary_index = text.index('className="simple-delivery-audit-primary-row"')
        audit_more_index = text.index('className="simple-delivery-audit-more"')
        audit_more_actions_index = text.index('className="simple-delivery-audit-more-actions"')
        assert runtime_drawer_index < runtime_actions_index
        assert audit_primary_index < audit_more_index < audit_more_actions_index
        for token in [
            "copy.connectionCard",
            "copy.connected",
            "nextStep",
            'onRunControl("startRuntime")',
            'onRunControl("startHeartbeat")',
            "onRefresh",
            "recordClientDeliveryAuditOperatorQueueInProgress",
            "recordClientDeliveryAuditBlockerRunbookEvidence",
            "refreshProductionClosedLoopReadiness",
            'openClientDetailPanel("client-project-workbench")',
            "More actions",
            "更多操作",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-runtime-controls-drawer",
            ".client-runtime-controls-drawer > summary",
            ".client-runtime-controls-drawer > summary::-webkit-details-marker",
            ".client-runtime-controls-drawer .client-runtime-summary-actions",
            ".client-runtime-controls-drawer:not([open]) .client-runtime-summary-actions",
            ".simple-delivery-audit-primary-row",
            ".simple-delivery-audit-more",
            ".simple-delivery-audit-more > summary",
            ".simple-delivery-audit-more-actions",
            ".simple-delivery-audit-more:not([open]) .simple-delivery-audit-more-actions",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72R Client Runtime Action Compression" in text
        assert "client-runtime-controls-drawer" in text
        assert "client-runtime-summary-actions" in text
        assert "simple-delivery-audit-primary-row" in text
        assert "simple-delivery-audit-more" in text
        assert "simple-delivery-audit-more-actions" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72s_client_compact_shell_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72S_CLIENT_COMPACT_SHELL.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72S Client Compact Shell" in text
        assert "Phase 72S Client Shell Diagnostics Drawer" in text
        topbar_index = text.index('className="topbar client-shell-topbar"')
        title_index = text.index('className="client-shell-title"')
        diagnostics_index = text.index('className="client-shell-diagnostics-drawer"')
        body_index = text.index('className="client-shell-diagnostics-body"')
        assert topbar_index < title_index < diagnostics_index < body_index
        for token in [
            "client-shell-topbar",
            "client-shell-title",
            "client-shell-diagnostics-drawer",
            "client-shell-diagnostics-body",
            "AI 运营工作台",
            "AI Operations Workspace",
            "客户机任务工作台",
            "Customer Task Workspace",
            "StatusBadge label={copy.runtimeLabel}",
            "StatusBadge label={copy.heartbeatLabel}",
        ]:
            assert token in text

    for token in [
        "Desktop Runtime Foundation",
        "connection-state connection-${connectionState}",
        "Server / Client environment boundary",
        "apiUnreachable",
    ]:
        assert token in desktop_main

    for styles in (web_styles, desktop_styles):
        for token in [
            ".topbar.client-shell-topbar",
            ".client-shell-title",
            ".client-shell-title h1",
            ".client-shell-diagnostics-drawer",
            ".client-shell-diagnostics-drawer > summary",
            ".client-shell-diagnostics-drawer > summary::-webkit-details-marker",
            ".client-shell-diagnostics-body",
            ".client-shell-diagnostics-drawer:not([open]) .client-shell-diagnostics-body",
            ".client-shell-diagnostics-drawer .topbar-status",
            "max-width: 100%",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72S Client Compact Shell" in text
        assert "client-shell-topbar" in text
        assert "client-shell-title" in text
        assert "client-shell-diagnostics-drawer" in text
        assert "client-shell-diagnostics-body" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72t_client_delivery_next_action_focus_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72T_CLIENT_DELIVERY_NEXT_ACTION_FOCUS.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72T Client Delivery Next Action Focus" in text
        for token in [
            "simpleDeliveryFocusTitle",
            "simpleDeliveryFocusHeadline",
            "simpleDeliveryFocusDetail",
            "simpleDeliveryFocusNextLabel",
            "simple-delivery-next-action-focus",
            "simple-delivery-focus-detail",
            "Current blockers",
            "Recommended action",
            "simpleDeliveryAuditBlockerCount",
            "simpleDeliveryAuditActionCount",
            "simpleDeliveryAuditExternalCount",
            "simpleDeliveryAuditOperatorCount",
            "simpleDeliveryAuditRunbookEvidenceCount",
            "clientObjectiveCompletionNextFocus",
            "productionClosedLoopDeliveryAuditNextActionPlan",
            "productionClosedLoopDeliveryAuditOperatorQueue",
            "recordClientDeliveryAuditOperatorQueueInProgress",
            "recordClientDeliveryAuditBlockerRunbookEvidence",
            "refreshProductionClosedLoopReadiness",
        ]:
            assert token in text
        focus_index = text.index('className="simple-delivery-audit-main simple-delivery-next-action-focus"')
        detail_index = text.index('className="simple-delivery-focus-detail"')
        action_index = text.index("{simpleDeliveryFocusNextLabel}", detail_index)
        assert focus_index < detail_index < action_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-delivery-next-action-focus strong",
            ".simple-delivery-focus-detail",
            ".simple-delivery-audit-next > span",
            "overflow-wrap: anywhere",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72T Client Delivery Next Action Focus" in text
        assert "simpleDeliveryFocusTitle" in text
        assert "simpleDeliveryFocusHeadline" in text
        assert "simpleDeliveryFocusDetail" in text
        assert "simpleDeliveryFocusNextLabel" in text
        assert "simple-delivery-next-action-focus" in text
        assert "simple-delivery-focus-detail" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72u_client_delivery_blocker_deep_link_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72U_CLIENT_DELIVERY_BLOCKER_DEEP_LINK.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    delivery_targets = [
        "client-production-delivery-audit-blocker-clearance",
        "client-production-delivery-audit-runbooks",
        "client-production-delivery-audit-next-action-plan",
        "client-production-delivery-audit-operator-queue",
        "client-production-delivery-audit-openclaw-provider-handoff",
    ]

    for text in (web_main, desktop_main):
        assert "Phase 72U Client Delivery Blocker Deep Link" in text
        for token in [
            "simpleDeliveryFocusPanelId",
            "clientProjectDeliveryAuditPanelIds",
            "clientProjectDetailPanelIds",
            "projectSupportDrawer",
            "clientProjectDetailPanelIds.has(panelId)",
            "clientProjectDeliveryAuditPanelIds.has(panelId)",
            "panelId: simpleDeliveryFocusPanelId",
            "openClientDetailPanel(simpleDeliveryFocusPanelId)",
            "window.requestAnimationFrame",
            "simpleDeliveryAuditExternalCount > 0",
            "simpleDeliveryAuditRunbookEvidenceCount > 0",
            "simpleDeliveryAuditOperatorCount > 0",
            "simpleDeliveryAuditActionCount > 0",
            "simpleDeliveryAuditBlockerCount > 0",
        ]:
            assert token in text
        for target in delivery_targets:
            assert f'id="{target}"' in text
            assert f'"{target}"' in text
        focus_index = text.index("const simpleDeliveryFocusPanelId")
        status_index = text.index("panelId: simpleDeliveryFocusPanelId")
        detail_index = text.index("openClientDetailPanel(simpleDeliveryFocusPanelId)")
        assert focus_index < status_index < detail_index

    for styles in (web_styles, desktop_styles):
        for target in delivery_targets:
            assert f".{target}" in styles
        assert "scroll-margin-top: 18px" in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72U Client Delivery Blocker Deep Link" in text
        assert "simpleDeliveryFocusPanelId" in text
        assert "clientProjectDeliveryAuditPanelIds" in text
        assert "clientProjectDetailPanelIds" in text
        assert "projectSupportDrawer" in text
        assert "openClientDetailPanel(simpleDeliveryFocusPanelId)" in text
        assert "panelId: simpleDeliveryFocusPanelId" in text
        assert "window.requestAnimationFrame" in text
        assert "scroll-margin-top: 18px" in text
        for target in delivery_targets:
            assert target in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72v_client_unified_current_work_panel_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72V_CLIENT_UNIFIED_CURRENT_WORK_PANEL.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72V Client Unified Current Work Panel" in text
        assert "Phase 72V Client Unified Current Work Secondary Actions" in text
        for token in [
            "SimpleCurrentWorkItem",
            "simpleCurrentWorkItems",
            "simpleCurrentWorkItem",
            "simpleSecondaryWorkItems",
            "simpleCurrentWorkTitle",
            "simpleCurrentWorkMoreLabel",
            "simpleCurrentWorkOpenPanelId",
            "simpleCurrentWorkIsDelivery",
            "simpleReviewStatePriority[item.state]",
            "simple-current-work-panel",
            "simple-current-work-main",
            "simple-current-work-metrics",
            "simple-current-work-actions",
            "simple-current-work-more",
            "simple-current-work-more-actions",
            "simple-current-work-secondary",
            "simpleCurrentInboxItem",
            "simpleDeliveryFocusPanelId",
            "simpleCurrentReviewCard",
            "openClientDetailPanel(simpleCurrentWorkOpenPanelId)",
            "recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)",
            "recordClientDeliveryAuditBlockerRunbookEvidence(simpleDeliveryAuditRunbookPackage)",
            "refreshProductionClosedLoopReadiness",
        ]:
            assert token in text
        panel_index = text.index('aria-label="Phase 72V Client Unified Current Work Panel"')
        legacy_inbox_index = text.index('className="simple-action-inbox"', panel_index)
        legacy_delivery_index = text.index('className={`simple-delivery-audit-card ${simpleDeliveryAuditState}`}', legacy_inbox_index)
        assert panel_index < legacy_inbox_index < legacy_delivery_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-current-work-panel",
            ".simple-current-work-panel.needs-action",
            ".simple-current-work-panel.current",
            ".simple-current-work-main",
            ".simple-current-work-metrics",
            ".simple-current-work-actions",
            ".simple-current-work-more",
            ".simple-current-work-more-actions",
            ".simple-current-work-more:not([open]) .simple-current-work-more-actions",
            ".simple-current-work-secondary",
            ".codex-simple-client .simple-action-inbox",
            ".codex-simple-client .simple-delivery-audit-card",
            ".simple-current-work-panel,",
            "grid-template-columns: minmax(0, 1fr) minmax(220px, 0.7fr)",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72V Client Unified Current Work Panel" in text
        assert "SimpleCurrentWorkItem" in text
        assert "simpleCurrentWorkItems" in text
        assert "simpleCurrentWorkItem" in text
        assert "simpleSecondaryWorkItems" in text
        assert "simple-current-work-panel" in text
        assert "simple-current-work-more" in text
        assert "simple-action-inbox" in text
        assert "simple-delivery-audit-card" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72w_client_essential_status_strip_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72W_CLIENT_ESSENTIAL_STATUS_STRIP.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72W Client Essential Status Strip" in text
        for token in [
            "simpleVisibleStatusCards",
            'card.key === "server-pressure"',
            'card.key === "project-progress"',
            "simpleVisibleStatusCards.map((card)",
            "simpleMinimalStatusCards",
            'key: "creation-review"',
            'key: "delivery-readiness"',
            "simple-current-work-panel",
            "Phase 72W Client Essential Status Strip / Phase 72O Client Codex Minimal Workspace",
            "openClientDetailPanel(card.panelId)",
        ]:
            assert token in text
        data_index = text.index("const simpleMinimalStatusCards")
        visible_index = text.index("const simpleVisibleStatusCards", data_index)
        strip_index = text.index("simpleVisibleStatusCards.map((card)", visible_index)
        work_index = text.index('aria-label="Phase 72V Client Unified Current Work Panel"', strip_index)
        assert data_index < visible_index < strip_index < work_index

    for styles in (web_styles, desktop_styles):
        strip_index = styles.index(".simple-command-status-strip")
        two_column_index = styles.index("grid-template-columns: repeat(2, minmax(0, 1fr))", strip_index)
        assert strip_index < two_column_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72W Client Essential Status Strip" in text
        assert "simpleVisibleStatusCards" in text
        assert "simpleMinimalStatusCards" in text
        assert "server-pressure" in text
        assert "project-progress" in text
        assert "creation-review" in text
        assert "delivery-readiness" in text
        assert "simple-command-status-strip" in text
        assert "simple-current-work-panel" in text
        assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72x_client_command_run_options_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72X_CLIENT_COMMAND_RUN_OPTIONS_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72X Client Command Run Options Drawer" in text
        for token in [
            "simple-run-options-drawer",
            "simple-run-options-actions",
            "submitSimpleOperationGoal",
            "sendBackgroundConversation",
            "plan_first_goal_submit",
            "workbenchCopy.backgroundRun",
            "运行选项",
            "Run options",
        ]:
            assert token in text
        goal_box_index = text.index('<div className="chat-input-row command-input-row simple-goal-box">')
        primary_index = text.index("submitSimpleOperationGoal", goal_box_index)
        drawer_index = text.index('className="simple-run-options-drawer"', primary_index)
        background_index = text.index("sendBackgroundConversation", drawer_index)
        work_panel_index = text.index('aria-label="Phase 72V Client Unified Current Work Panel"', background_index)
        assert goal_box_index < primary_index < drawer_index < background_index < work_panel_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-run-options-drawer",
            ".simple-run-options-drawer > summary",
            ".simple-run-options-drawer > summary::-webkit-details-marker",
            ".simple-run-options-actions",
            ".simple-run-options-drawer:not([open]) .simple-run-options-actions",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72X Client Command Run Options Drawer" in text
        assert "simple-run-options-drawer" in text
        assert "simple-run-options-actions" in text
        assert "sendBackgroundConversation" in text
        assert "sendBackgroundConversation" in text
        assert "run-options" in text
        assert "background" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72y_client_current_work_single_action_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72Y_CLIENT_CURRENT_WORK_SINGLE_ACTION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72Y Client Current Work Single Action" in text
        assert "Phase 72V Client Unified Current Work Secondary Actions" in text
        assert 'className={`refresh-button ${simpleCurrentWorkIsDelivery ? "" : "primary-action"}`}' not in text
        for token in [
            "simple-current-work-actions",
            "simple-current-work-more",
            "simple-current-work-more-actions",
            "simpleCurrentWorkIsDelivery ? (",
            "recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)",
            "openClientDetailPanel(simpleCurrentWorkOpenPanelId)",
            "simpleSecondaryWorkItems.map((item)",
            "recordClientDeliveryAuditBlockerRunbookEvidence(simpleDeliveryAuditRunbookPackage)",
            "refreshProductionClosedLoopReadiness",
        ]:
            assert token in text

        actions_index = text.index('className="simple-current-work-actions"')
        delivery_primary_index = text.index("simpleCurrentWorkIsDelivery ? (", actions_index)
        record_index = text.index(
            "recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)",
            delivery_primary_index,
        )
        non_delivery_open_index = text.index("openClientDetailPanel(simpleCurrentWorkOpenPanelId)", record_index)
        drawer_index = text.index(
            'aria-label="Phase 72Y Client Current Work Single Action / Phase 72V Client Unified Current Work Secondary Actions"',
            non_delivery_open_index,
        )
        drawer_delivery_index = text.index("simpleCurrentWorkIsDelivery ? (", drawer_index)
        drawer_open_index = text.index("openClientDetailPanel(simpleCurrentWorkOpenPanelId)", drawer_delivery_index)
        secondary_index = text.index("simpleSecondaryWorkItems.map((item)", drawer_open_index)
        assert actions_index < delivery_primary_index < record_index < non_delivery_open_index
        assert non_delivery_open_index < drawer_index < drawer_delivery_index < drawer_open_index < secondary_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72Y Client Current Work Single Action" in text
        assert "simple-current-work-panel" in text
        assert "simple-current-work-more" in text
        assert "simple-current-work-more-actions" in text
        assert "recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)" in text
        assert "openClientDetailPanel(simpleCurrentWorkOpenPanelId)" in text
        assert "Phase 72V Client Unified Current Work Secondary Actions" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_72z_client_current_work_metrics_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_72Z_CLIENT_CURRENT_WORK_METRICS_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 72Z Client Current Work Metrics Drawer" in text
        for token in [
            "simple-current-work-panel",
            "simple-current-work-actions",
            "simple-current-work-more",
            "simple-current-work-more-actions",
            "simple-current-work-metrics simple-current-work-more-metrics",
            "simpleInboxTotalCount",
            "simpleReviewAttentionCount",
            "clientObjectiveCompletionPercent",
        ]:
            assert token in text
        actions_index = text.index('className="simple-current-work-actions"')
        drawer_index = text.index('className="simple-current-work-more"', actions_index)
        drawer_actions_index = text.index('className="simple-current-work-more-actions"', drawer_index)
        metrics_index = text.index('aria-label="Phase 72Z Client Current Work Metrics Drawer"', drawer_actions_index)
        secondary_index = text.index("simpleSecondaryWorkItems.map((item)", metrics_index)
        assert actions_index < drawer_index < drawer_actions_index < metrics_index < secondary_index

    for styles in (web_styles, desktop_styles):
        panel_index = styles.index(".simple-current-work-panel")
        two_column_index = styles.index(
            "grid-template-columns: minmax(0, 1fr) minmax(220px, 0.7fr)",
            panel_index,
        )
        more_metrics_index = styles.index(".simple-current-work-more-metrics", two_column_index)
        assert panel_index < two_column_index < more_metrics_index
        assert ".simple-current-work-more-metrics span" in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 72Z Client Current Work Metrics Drawer" in text
        assert "simple-current-work-metrics" in text
        assert "simple-current-work-more-metrics" in text
        assert "simple-current-work-more-actions" in text
        assert "grid-template-columns: minmax(0, 1fr) minmax(220px, 0.7fr)" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73a_client_secondary_panels_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73A_CLIENT_SECONDARY_PANELS_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 73A Client Secondary Panels Drawer" in text
        for token in [
            "simple-secondary-panels-drawer",
            "simple-secondary-panels-body",
            "simple-project-context-drawer",
            "operator-detail-drawer",
            "workbenchCopy.simpleProjectContextTitle",
            "workbenchCopy.detailDrawerTitle",
            "更多面板",
            "More panels",
        ]:
            assert token in text
        current_work_index = text.index('aria-label="Phase 72V Client Unified Current Work Panel"')
        secondary_drawer_index = text.index('aria-label="Phase 73A Client Secondary Panels Drawer"', current_work_index)
        secondary_body_index = text.index('className="simple-secondary-panels-body"', secondary_drawer_index)
        context_index = text.index('<details className="simple-project-context-drawer">', secondary_body_index)
        detail_index = text.index('<details className="operator-detail-drawer">', context_index)
        maintenance_index = text.index('<details className="maintenance-drawer"', detail_index)
        assert current_work_index < secondary_drawer_index < secondary_body_index < context_index < detail_index < maintenance_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-secondary-panels-drawer",
            ".simple-secondary-panels-drawer > summary",
            ".simple-secondary-panels-drawer > summary span",
            ".simple-secondary-panels-drawer > summary strong",
            ".simple-secondary-panels-drawer[open] > summary",
            ".simple-secondary-panels-drawer:not([open]) .simple-secondary-panels-body",
            ".simple-secondary-panels-body",
            ".simple-secondary-panels-body .simple-project-context-drawer",
            ".simple-secondary-panels-body .operator-detail-drawer",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73A Client Secondary Panels Drawer" in text
        assert "simple-secondary-panels-drawer" in text
        assert "simple-secondary-panels-body" in text
        assert "simple-project-context-drawer" in text
        assert "operator-detail-drawer" in text
        assert "project context" in text or "project-context" in text
        assert "plan/status" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73b_client_top_utility_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73B_CLIENT_TOP_UTILITY_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 73B Client Top Utility Drawer" in text
        assert text.count('className="client-top-utility-drawer"') == 1
        assert text.count('className="client-shell-diagnostics-drawer"') == 1
        assert text.count('className="operator-page-tabs operator-page-mode-drawer"') == 1
        for token in [
            "client-top-utility-body",
            "Workspace tools",
            "工作区工具",
            "runtime ready",
            "check runtime",
            "Phase 72S Client Shell Diagnostics Drawer",
            "Phase 72Q Client Mode Switch Drawer",
            "operator-page-tab-actions",
            'setOperatorPage("operations")',
            'setOperatorPage("knowledge")',
            "StatusBadge label={copy.runtimeLabel}",
            "StatusBadge label={copy.heartbeatLabel}",
        ]:
            assert token in text
        topbar_index = text.index('className="topbar client-shell-topbar"')
        title_index = text.index('className="client-shell-title"', topbar_index)
        utility_index = text.index('aria-label="Phase 73B Client Top Utility Drawer"', title_index)
        utility_body_index = text.index('className="client-top-utility-body"', utility_index)
        diagnostics_index = text.index('className="client-shell-diagnostics-drawer"', utility_body_index)
        mode_index = text.index('className="operator-page-tabs operator-page-mode-drawer"', diagnostics_index)
        workstation_index = text.index("<WorkstationHome", mode_index)
        assert topbar_index < title_index < utility_index < utility_body_index < diagnostics_index < mode_index < workstation_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-top-utility-drawer",
            ".client-top-utility-drawer > summary",
            ".client-top-utility-drawer > summary::-webkit-details-marker",
            ".client-top-utility-drawer > summary span",
            ".client-top-utility-drawer > summary strong",
            ".client-top-utility-drawer[open] > summary",
            ".client-top-utility-drawer:not([open]) .client-top-utility-body",
            ".client-top-utility-body",
            ".client-top-utility-body .client-shell-diagnostics-drawer",
            ".client-top-utility-body .operator-page-tabs",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73B Client Top Utility Drawer" in text
        assert "client-top-utility-drawer" in text
        assert "client-top-utility-body" in text
        assert "client-shell-diagnostics-drawer" in text
        assert "operator-page-mode-drawer" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73c_client_runtime_companion_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73C_CLIENT_RUNTIME_COMPANION_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 73C Client Runtime Companion Drawer" in text
        assert text.count('className="client-runtime-companion-drawer"') == 1
        assert text.count('className="client-runtime-companion-body"') == 1
        assert text.count('id="operator-home-title"') == 1
        for token in [
            "client-runtime-summary",
            "client-runtime-controls-drawer",
            "client-home-detail-drawer",
            "Phase 72R Client Runtime Controls Drawer",
            'onRunControl("startRuntime")',
            'onRunControl("startHeartbeat")',
            "onLanguageChange",
            "copy.advancedSummary",
            "Client ready",
            "客户机已就绪",
        ]:
            assert token in text
        section_index = text.index("client-runtime-companion ${productionReady")
        drawer_index = text.index('aria-label="Phase 73C Client Runtime Companion Drawer"', section_index)
        body_index = text.index('className="client-runtime-companion-body"', drawer_index)
        runtime_summary_index = text.index('className="client-runtime-summary"', body_index)
        controls_index = text.index('className="client-runtime-controls-drawer"', runtime_summary_index)
        detail_index = text.index('className="client-home-detail-drawer"', controls_index)
        next_function_index = min(
            index
            for index in [
                text.find("function ChatPanel", detail_index),
                text.find("function buildTrayTooltip", detail_index),
            ]
            if index != -1
        )
        assert section_index < drawer_index < body_index < runtime_summary_index < controls_index < detail_index < next_function_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-runtime-companion-drawer",
            ".client-runtime-companion-drawer > summary",
            ".client-runtime-companion-drawer > summary::-webkit-details-marker",
            ".client-runtime-companion-drawer > summary span",
            ".client-runtime-companion-drawer > summary strong",
            ".client-runtime-companion-drawer[open] > summary",
            ".client-runtime-companion-drawer:not([open]) .client-runtime-companion-body",
            ".client-runtime-companion-body",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73C Client Runtime Companion Drawer" in text
        assert "client-runtime-companion-drawer" in text
        assert "client-runtime-companion-body" in text
        assert "client-runtime-summary" in text
        assert "client-runtime-controls-drawer" in text
        assert "client-home-detail-drawer" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73m_client_runtime_utility_consolidation_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73M_CLIENT_RUNTIME_UTILITY_CONSOLIDATION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 73M Client Runtime Utility Consolidation" in text
        assert text.count("<WorkstationHome") == 1
        assert text.count('className="client-top-utility-body"') == 1
        assert text.count('className="client-runtime-companion-drawer"') == 1
        assert text.count('className="client-runtime-companion-body"') == 1
        utility_index = text.index('aria-label="Phase 73B Client Top Utility Drawer"')
        body_index = text.index('className="client-top-utility-body"', utility_index)
        diagnostics_index = text.index('className="client-shell-diagnostics-drawer"', body_index)
        mode_index = text.index('className="operator-page-tabs operator-page-mode-drawer"', diagnostics_index)
        workstation_index = text.index("<WorkstationHome", mode_index)
        api_unreachable_index = text.index("{apiUnreachable ? (", workstation_index)
        page_host_index = text.index('className="operator-page-host"', api_unreachable_index)
        chat_panel_index = text.index("<ChatPanel", page_host_index)
        assert utility_index < body_index < diagnostics_index < mode_index < workstation_index < api_unreachable_index < page_host_index < chat_panel_index
        assert 'hidden={operatorPage !== "knowledge"}' in text
        assert 'hidden={operatorPage !== "operations"}' in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-top-utility-body .operator-home.client-runtime-companion",
            ".client-top-utility-body .client-runtime-companion-drawer",
            ".client-top-utility-drawer:not([open]) .client-top-utility-body",
            ".client-runtime-companion-drawer:not([open]) .client-runtime-companion-body",
        ]:
            assert token in styles

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73M Client Runtime Utility Consolidation" in text
        assert "client-top-utility-body" in text
        assert "client-runtime-companion-drawer" in text
        assert "WorkstationHome" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73n_client_production_detail_drawer_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73N_CLIENT_PRODUCTION_DETAIL_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 73N Client Production Detail Drawer",
            "simple-production-details-drawer",
            "simple-production-details-body",
            "simpleProductionDetailCount",
            "simpleProductionDetailOutputCount",
            "detailsAncestor",
            "target.closest(\"details\")",
            "simple-secondary-panels-drawer",
            "maintenance-drawer",
            "client-operation-desk-drawer",
        ]:
            assert token in text
        workbench_index = text.index('className="client-task-workbench"')
        current_work_index = text.index('aria-label="Phase 72V Client Unified Current Work Panel"', workbench_index)
        production_drawer_index = text.index('aria-label="Phase 73N Client Production Detail Drawer"', current_work_index)
        production_body_index = text.index('className="simple-production-details-body"', production_drawer_index)
        secondary_index = text.index('className="simple-secondary-panels-drawer"', production_body_index)
        maintenance_index = text.index('aria-label="Phase 73F Client Approval Output Focus"', secondary_index)
        chat_panel_end_index = text.index("function BrowserSessionsPanel", maintenance_index)
        assert current_work_index < production_drawer_index < production_body_index < secondary_index
        assert secondary_index < maintenance_index < chat_panel_end_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-production-details-drawer",
            ".simple-production-details-drawer > summary",
            ".simple-production-details-drawer:not([open]) .simple-production-details-body",
            ".simple-production-details-body",
            ".codex-simple-client .simple-production-details-body .simple-secondary-panels-drawer",
            ".codex-simple-client .simple-production-details-body .maintenance-drawer",
            ".codex-simple-client .client-operation-desk-drawer:not([open])",
        ]:
            assert token in styles
        production_rule_index = styles.index(".simple-production-details-drawer {")
        body_hidden_index = styles.index(
            ".simple-production-details-drawer:not([open]) .simple-production-details-body",
            production_rule_index,
        )
        nested_secondary_index = styles.index(
            ".codex-simple-client .simple-production-details-body .simple-secondary-panels-drawer",
            body_hidden_index,
        )
        hidden_operation_index = styles.index(".codex-simple-client .client-operation-desk-drawer:not([open])")
        assert production_rule_index < body_hidden_index < nested_secondary_index
        assert hidden_operation_index < production_rule_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73N Client Production Detail Drawer" in text
        assert "simple-production-details-drawer" in text
        assert "simple-production-details-body" in text
        assert "simple-secondary-panels-drawer" in text
        assert "maintenance-drawer" in text
        assert "client-operation-desk-drawer" in text
        assert "detailsAncestor" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73o_client_production_index_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73O_CLIENT_PRODUCTION_INDEX.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 73O Client Production Index",
            "simple-production-index",
            "simple-production-index-head",
            "simple-production-index-grid",
            "simple-production-index-card",
            "clientProjectFocusCards.map",
            "openClientDetailPanel(card.targetId)",
            "client-project-section-materials",
            "client-project-section-workflows",
            "client-project-section-outputs",
            "client-project-section-publish",
        ]:
            assert token in text
        production_body_index = text.index('className="simple-production-details-body"')
        production_index_index = text.index('aria-label="Phase 73O Client Production Index"', production_body_index)
        secondary_index = text.index('className="simple-secondary-panels-drawer"', production_index_index)
        maintenance_index = text.index('aria-label="Phase 73F Client Approval Output Focus"', secondary_index)
        assert production_body_index < production_index_index < secondary_index < maintenance_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-production-index",
            ".simple-production-index-head",
            ".simple-production-index-grid",
            ".simple-production-index-card",
            ".simple-production-index-card:hover",
            ".simple-production-index-card.needs-action",
            ".simple-production-index-card.current",
            ".simple-production-index-card.done",
            "grid-template-columns: repeat(3, minmax(0, 1fr))",
        ]:
            assert token in styles
        index_rule_index = styles.index(".simple-production-index {")
        grid_rule_index = styles.index(".simple-production-index-grid", index_rule_index)
        card_rule_index = styles.index(".simple-production-index-card", grid_rule_index)
        assert index_rule_index < grid_rule_index < card_rule_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73O Client Production Index" in text
        assert "simple-production-index" in text
        assert "clientProjectFocusCards" in text
        assert "openClientDetailPanel(card.targetId)" in text
        assert "client-project-section-materials" in text
        assert "client-project-section-workflows" in text
        assert "client-project-section-outputs" in text
        assert "client-project-section-publish" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73q_client_production_action_summary_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73Q_CLIENT_PRODUCTION_ACTION_SUMMARY.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 73Q Client Production Action Summary",
            "simple-production-action-summary",
            "simple-production-action-head",
            "simple-production-action-current",
            "simple-production-action-buttons",
            "simple-production-action-secondary",
            "simple-production-action-chip",
            "clientProjectCurrentDecision",
            "clientProjectSecondaryDecisionCards",
            "clientProjectDecisionTotalCount",
            "clientProjectCurrentDecision.onPrimary",
            "clientProjectCurrentDecision.onSecondary",
            "openClientDetailPanel(clientProjectCurrentDecision.targetId)",
        ]:
            assert token in text
        production_body_index = text.index('className="simple-production-details-body"')
        action_summary_index = text.index('aria-label="Phase 73Q Client Production Action Summary"', production_body_index)
        production_index_index = text.index('aria-label="Phase 73O Client Production Index"', action_summary_index)
        assert production_body_index < action_summary_index < production_index_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-production-action-summary",
            ".simple-production-action-head",
            ".simple-production-action-current",
            ".simple-production-action-buttons",
            ".simple-production-action-secondary",
            ".simple-production-action-chip",
            "grid-template-columns: repeat(2, minmax(0, 1fr))",
        ]:
            assert token in styles
        summary_rule_index = styles.index(".simple-production-action-summary {")
        index_rule_index = styles.index(".simple-production-index {", summary_rule_index)
        assert summary_rule_index < index_rule_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73Q Client Production Action Summary" in text
        assert "simple-production-action-summary" in text
        assert "clientProjectDecisionCards" in text
        assert "clientProjectCurrentDecision" in text
        assert "clientProjectSecondaryDecisionCards" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73d_client_workbench_first_action_focus_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73D_CLIENT_WORKBENCH_FIRST_ACTION_FOCUS.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            'className="panel-title logs-title"',
            "client-task-workbench",
            "simple-operator-workbench",
            "simple-operator-header",
            "simple-command-status-strip",
            "simple-goal-box",
            "client-operation-desk-drawer",
            "client-operation-desk",
        ]:
            assert token in text
        workbench_index = text.index('className="client-task-workbench"')
        operation_drawer_index = text.index('className="client-operation-desk-drawer"', workbench_index)
        simple_workbench_index = text.index('className="simple-operator-workbench"', operation_drawer_index)
        status_strip_index = text.index('className="simple-command-status-strip"', simple_workbench_index)
        goal_box_index = text.index('className="chat-input-row command-input-row simple-goal-box"', status_strip_index)
        current_work_index = text.index('aria-label="Phase 72V Client Unified Current Work Panel"', goal_box_index)
        assert workbench_index < operation_drawer_index < simple_workbench_index < status_strip_index < goal_box_index < current_work_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".chat-panel.codex-simple-client > .panel-title",
            ".codex-simple-client .simple-operator-workbench",
            ".codex-simple-client .simple-operator-header",
            ".client-operation-desk-drawer",
            "order: 6",
            "padding-top: 8px",
            "border-bottom: 0",
        ]:
            assert token in styles
        title_rule_index = styles.index(".chat-panel.codex-simple-client > .panel-title")
        title_hidden_index = styles.index("display: none", title_rule_index)
        header_rule_index = styles.index(".codex-simple-client .simple-operator-header")
        header_hidden_index = styles.index("display: none", header_rule_index)
        operation_rule_index = styles.index(".client-operation-desk-drawer")
        operation_order_index = styles.index("order: 6", operation_rule_index)
        assert title_rule_index < title_hidden_index
        assert header_rule_index < header_hidden_index
        assert operation_rule_index < operation_order_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73D Client Workbench First Action Focus" in text
        assert "panel-title" in text
        assert "simple-operator-header" in text
        assert "client-operation-desk-drawer" in text
        assert "simple-command-status-strip" in text
        assert "simple-goal-box" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73e_client_quiet_maintenance_entry_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73E_CLIENT_QUIET_MAINTENANCE_ENTRY.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        assert "Phase 73E Client Quiet Maintenance Entry" in text
        assert 'className="advanced-diagnostics"' in text
        assert "copy.advancedSummary" in text
        for token in [
            "Maintenance",
            "Logs and diagnostics",
            "维护",
            "日志与诊断",
            "layout-grid",
            "Dashboard",
            "Runtime Control",
            "BrowserSessionsPanel",
            "logs-panel",
        ]:
            assert token in text
        advanced_index = text.index('aria-label="Phase 73E Client Quiet Maintenance Entry"')
        summary_index = text.index("title={copy.advancedSummary}", advanced_index)
        body_index = text.index('className="layout-grid"', summary_index)
        assert advanced_index < summary_index < body_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".advanced-diagnostics",
            "order: 7",
            "align-self: flex-end",
            "width: fit-content",
            ".advanced-diagnostics > summary span",
            ".advanced-diagnostics > summary small",
            ".chat-settings-panel > summary",
            ".advanced-diagnostics[open]",
            ".advanced-diagnostics[open] > summary",
            ".advanced-diagnostics:not([open]) .layout-grid",
        ]:
            assert token in styles
        advanced_rule_index = styles.index(".advanced-diagnostics {")
        quiet_order_index = styles.index("order: 7", advanced_rule_index)
        quiet_width_index = styles.index("width: fit-content", advanced_rule_index)
        folded_rule_index = styles.index(".advanced-diagnostics:not([open]) .layout-grid")
        chat_settings_index = styles.index(".chat-settings-panel > summary")
        assert advanced_rule_index < quiet_order_index < quiet_width_index < folded_rule_index
        assert chat_settings_index < folded_rule_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73E Client Quiet Maintenance Entry" in text
        assert "advanced-diagnostics" in text
        assert "Maintenance" in text
        assert "Logs and diagnostics" in text
        assert "layout-grid" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73f_client_codex_quiet_workbench_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73F_CLIENT_CODEX_QUIET_WORKBENCH.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 73F Client Quiet Status Rail",
            "Phase 73F Client Quiet Operation Detail Entry",
            "Phase 73F Client Quiet Secondary Panels",
            "Phase 73F Client Approval Output Focus",
            "simple-command-status-strip",
            "simple-goal-box",
            "simple-current-work-panel",
            "client-operation-desk-drawer",
            "simple-secondary-panels-drawer",
            "maintenance-drawer",
        ]:
            assert token in text
        workbench_index = text.index('className="client-task-workbench"')
        quiet_status_index = text.index("Phase 73F Client Quiet Status Rail", workbench_index)
        goal_box_index = text.index('className="chat-input-row command-input-row simple-goal-box"', quiet_status_index)
        current_work_index = text.index('aria-label="Phase 72V Client Unified Current Work Panel"', goal_box_index)
        quiet_secondary_index = text.index("Phase 73F Client Quiet Secondary Panels", current_work_index)
        approval_focus_index = text.index("Phase 73F Client Approval Output Focus", quiet_secondary_index)
        assert workbench_index < quiet_status_index < goal_box_index < current_work_index < quiet_secondary_index < approval_focus_index

    for styles in (web_styles, desktop_styles):
        for token in [
            ".codex-simple-client .simple-command-status-strip",
            "display: grid",
            "grid-template-columns: 1fr",
            "min-height: 38px",
            ".codex-simple-client .simple-command-status-pill svg",
            ".codex-simple-client .client-operation-desk-drawer",
            "width: auto",
            ".codex-simple-client .client-operation-desk-drawer[open]",
            ".codex-simple-client .simple-secondary-panels-drawer",
            ".codex-simple-client .simple-secondary-panels-drawer[open]",
            ".codex-simple-client .maintenance-drawer",
            "box-shadow: none",
        ]:
            assert token in styles
        status_rule_index = styles.index(".codex-simple-client .simple-command-status-strip")
        status_grid_index = styles.index("display: grid", status_rule_index)
        status_pill_index = styles.index(".codex-simple-client .simple-command-status-pill", status_rule_index)
        status_height_index = styles.index("min-height: 38px", status_pill_index)
        operation_rule_index = styles.index(".codex-simple-client .client-operation-desk-drawer")
        operation_width_index = styles.index("width: auto", operation_rule_index)
        operation_open_index = styles.index(".codex-simple-client .client-operation-desk-drawer[open]", operation_rule_index)
        secondary_rule_index = styles.index(".codex-simple-client .simple-secondary-panels-drawer")
        secondary_open_index = styles.index(".codex-simple-client .simple-secondary-panels-drawer[open]", secondary_rule_index)
        assert status_rule_index < status_grid_index < status_pill_index < status_height_index
        assert operation_rule_index < operation_width_index
        assert operation_rule_index < operation_open_index
        assert secondary_rule_index < secondary_open_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73F Client Codex Quiet Workbench" in text
        assert "simple-command-status-strip" in text
        assert "client-operation-desk-drawer" in text
        assert "simple-secondary-panels-drawer" in text
        assert "maintenance-drawer" in text
        assert "Codex-like" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73s_client_codex_single_focus_ui_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73S_CLIENT_CODEX_SINGLE_FOCUS_UI.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "simpleProductionDetailSummary",
            "simpleProductionDetailFullSummary",
            "summary title={simpleProductionDetailFullSummary}",
            "Production flow",
            "simple-current-work-panel",
            "simple-goal-box",
            "client-top-utility-drawer",
            "simple-production-details-drawer",
        ]:
            assert token in text
        assert "reviews ${simpleMaintenanceCount} · materials" in text
        assert "outputs ${simpleProductionDetailOutputCount}/${outputCandidates.length}" in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-top-utility-drawer:hover",
            ".client-top-utility-drawer[open]",
            ".client-top-utility-drawer[open] > summary strong",
            ".simple-current-work-panel",
            ".simple-goal-box",
            ".simple-production-details-drawer[open]",
            "width: fit-content",
            "max-width: calc(100% - 32px)",
        ]:
            assert token in styles
        goal_rule_index = styles.index(".simple-goal-box {")
        goal_order_index = styles.index("order: 2", goal_rule_index)
        current_rule_index = styles.index(".simple-current-work-panel {")
        current_order_index = styles.index("order: 4", current_rule_index)
        production_rule_index = styles.index(".simple-production-details-drawer {")
        production_order_index = styles.index("order: 5", production_rule_index)
        utility_rule_index = styles.index(".client-top-utility-drawer {")
        utility_quiet_index = styles.index("border: 1px solid transparent", utility_rule_index)
        utility_open_index = styles.index(".client-top-utility-drawer[open]", utility_quiet_index)
        assert goal_rule_index < goal_order_index
        assert current_rule_index < current_order_index
        assert production_rule_index < production_order_index
        assert utility_rule_index < utility_quiet_index < utility_open_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73S Client Codex Single Focus UI" in text
        assert "simpleProductionDetailSummary" in text
        assert "simpleProductionDetailFullSummary" in text
        assert "simple-current-work-panel" in text
        assert "simple-goal-box" in text
        assert "client-top-utility-drawer" in text
        assert "simple-production-details-drawer" in text
        assert "Codex" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73u_client_visual_approval_workbench_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73U_CLIENT_VISUAL_APPROVAL_WORKBENCH.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 73U Client Visual Approval Workbench",
            "simpleApprovalDeskPlan",
            "simpleApprovalDeskWorkflow",
            "simpleApprovalDeskOutputCandidates",
            "simpleApprovalDeskKnowledgeState",
            "simple-approval-workbench",
            "simple-approval-workbench-grid",
            "simple-approval-output-preview",
            "<img src={previewUri} alt={candidate.title} />",
            "<video src={previewUri} controls />",
            "<audio src={previewUri} controls />",
            "decideProjectPlan",
            "decideProjectWorkflowSelection",
            "decideProjectOutputCandidate",
            "onOpenKnowledge",
            "client-project-section-plans",
            "client-project-section-outputs",
            "client-project-section-workflows",
            "client-project-section-materials",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-approval-workbench",
            ".simple-approval-workbench-head",
            ".simple-approval-workbench-grid",
            ".simple-approval-card",
            ".simple-approval-card.needs-action",
            ".simple-approval-output-list",
            ".simple-approval-output-preview",
            ".simple-approval-output-preview img",
            ".simple-approval-output-preview video",
            ".simple-approval-output-preview audio",
        ]:
            assert token in styles
        goal_rule_index = styles.index(".simple-goal-box {")
        goal_order_index = styles.index("order: 2", goal_rule_index)
        approval_rule_index = styles.index(".simple-approval-workbench {")
        approval_order_index = styles.index("order: 3", approval_rule_index)
        current_rule_index = styles.index(".simple-current-work-panel {")
        current_order_index = styles.index("order: 4", current_rule_index)
        production_rule_index = styles.index(".simple-production-details-drawer {")
        production_order_index = styles.index("order: 5", production_rule_index)
        responsive_index = styles.rindex("@media")
        responsive_approval_index = styles.index(".simple-approval-workbench-grid", responsive_index)
        responsive_goal_index = styles.index(".simple-goal-box", responsive_index)
        assert goal_rule_index < goal_order_index
        assert approval_rule_index < approval_order_index
        assert current_rule_index < current_order_index
        assert production_rule_index < production_order_index
        assert responsive_index < responsive_goal_index < responsive_approval_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73U Client Visual Approval Workbench" in text
        assert "simple-approval-workbench" in text
        assert "operation plan" in text
        assert "ComfyUI image/video" in text
        assert "workflow selection" in text
        assert "RAG knowledge" in text
        assert "visual approval" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


def test_phase_73v_client_project_conversation_workspace_contract() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73V_CLIENT_PROJECT_CONVERSATION_WORKSPACE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperation",
            "commercialOperations",
            "simpleSelectedCommercialOperation",
            "simpleProjectOptions",
            "simpleConversationMessages",
            "simplePlanReviewState",
            "simpleNewProjectDraftActive",
            "simplePendingDeleteOperationId",
            "shouldKeepNewProjectDraft",
            "operationIdWasProvided",
            "listedOperationIds",
            "requestedOperationId",
            "hasActiveCommercialOperation",
            "submitSimpleOperationGoal",
            "deleteCommercialOperationFromSimpleWorkspace",
            "commercialOperationClient.delete",
            "regenerateOperationPlanFromSimpleWorkspace",
            "selectCommercialOperationFromSimpleWorkspace",
            "compactPlanValue",
            "friendlyPlanChannel",
            "friendlyPlanContentSummary",
            "friendlyPlanMaterial",
            "friendlyPlanKpi",
            "friendlyPlanRisk",
            "friendlyPlanTitle",
            "operationPlanDetailSections",
            "simpleApprovalDeskPlanSections",
            "simpleApprovalDeskPlanTitle",
            "内容主线：开场吸引用户注意",
            "审批边界：生产任务、ComfyUI 生成",
            "startSimpleNewOperationProject",
            "Phase 73V Client Project Conversation Workspace",
            "Phase 73V Client Large Plan Chat",
            "simple-project-entry",
            "simple-conversation-workspace",
            "simple-conversation-log",
            "simple-plan-rag-row",
            "simple-plan-review-card",
            "simple-plan-detail-grid",
            "simple-plan-detail-section",
            "simple-rag-context-card",
            "simple-project-delete",
            'simplePendingDeleteOperationId ? "confirm"',
            "simple-project-select",
            "Trash2",
            "advanceMainAgentProjectStep",
            "onOpenKnowledge",
            "worker_console_simple_project_chat",
            "plan_first_goal_submit",
            'onClick={() => void submitSimpleOperationGoal()}',
            'language === "zh-CN" ? "生成方案" : "Generate plan"',
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".simple-project-entry",
            ".simple-project-entry-head",
            ".simple-project-list",
            ".simple-project-option",
            ".simple-project-option.selected",
            ".simple-project-select",
            ".simple-project-delete",
            ".simple-project-delete.confirm",
            ".simple-conversation-workspace",
            ".simple-conversation-log",
            ".simple-conversation-message",
            ".simple-plan-rag-row",
            ".simple-plan-review-card",
            ".simple-plan-detail-grid",
            ".simple-plan-detail-section",
            ".simple-rag-context-card",
            ".simple-conversation-workspace .simple-goal-box",
        ]:
            assert token in styles
        conversation_rule_index = styles.index(".simple-conversation-workspace {")
        conversation_order_index = styles.index("order: 2", conversation_rule_index)
        project_list_rule_index = styles.index(".simple-project-list")
        project_list_order_index = styles.index("order: 2", project_list_rule_index)
        conversation_goal_rule_index = styles.index(".simple-conversation-workspace .simple-goal-box")
        conversation_goal_order_index = styles.index("order: 3", conversation_goal_rule_index)
        plan_rag_rule_index = styles.index(".simple-plan-rag-row")
        plan_rag_order_index = styles.index("order: 4", plan_rag_rule_index)
        approval_rule_index = styles.index(".simple-approval-workbench {")
        approval_order_index = styles.index("order: 3", approval_rule_index)
        responsive_index = styles.rindex("@media")
        responsive_plan_index = styles.index(".simple-plan-rag-row", responsive_index)
        assert conversation_rule_index < conversation_order_index
        assert project_list_rule_index < project_list_order_index
        assert conversation_goal_rule_index < conversation_goal_order_index
        assert plan_rag_rule_index < plan_rag_order_index
        assert approval_rule_index < approval_order_index
        assert responsive_index < responsive_plan_index

    for text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73V Client Project Conversation Workspace" in text
        assert "project selection" in text
        assert "large chat" in text
        assert "RAG" in text
        assert "overall operation plan" in text
        assert "regenerate" in text
        assert "manual approval" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "does not" in text
        assert "bypass approval" in text


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


def test_worker_consoles_expose_phase_68d_customer_project_workbench() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68D Customer Project Workbench",
            "projectWorkbenchCopy",
            "client-project-workbench",
            "client-project-stats",
            "client-output-candidate-grid",
            "advanceMainAgentProjectStep",
            "registerProjectMaterialFromClient",
            "createManualWorkflowSelection",
            "selectProjectOutputCandidate",
            "operationPlans",
            "projectMaterials",
            "productionTasks",
            "workflowSelections",
            "outputCandidates",
            "finalSelections",
            "publishPackages",
            "platformMetricSnapshots",
            "listOperationPlans",
            "listProjectMaterials",
            "listProductionTasks",
            "listWorkflowSelections",
            "listOutputCandidates",
            "listFinalSelections",
            "listPublishPackages",
            "listPlatformMetricSnapshots",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationPlan",
            "CommercialOperationProjectMaterial",
            "CommercialOperationProductionTask",
            "CommercialOperationWorkflowSelection",
            "CommercialOperationOutputCandidate",
            "CommercialOperationFinalSelection",
            "CommercialOperationPublishPackage",
            "CommercialOperationPlatformMetricSnapshot",
            "CommercialOperationMainAgentAdvance",
            "advanceMainAgentLoop",
            "/main-agent/advance-loop",
            "/operation-plans",
            "/project-materials",
            "/production-tasks",
            "/workflow-selections",
            "/output-candidates",
            "/final-selections",
            "/publish-packages",
            "/platform-metric-snapshots",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-project-workbench",
            ".client-project-workbench-header",
            ".client-project-stats",
            ".client-project-actions",
            ".client-project-grid",
            ".client-project-section",
            ".client-project-record",
            ".client-output-candidate-grid",
            ".client-output-preview",
            ".client-project-boundary",
        ]:
            assert token in styles


def test_phase_68d_customer_project_workbench_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68D_CUSTOMER_PROJECT_WORKBENCH.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68D Customer Project Workbench" in text
        assert "worker_console/src/main.tsx" in text
        assert "worker_console_desktop/src/main.tsx" in text
        assert "OperationPlan" in text
        assert "ProjectMaterial" in text
        assert "ProductionTask" in text
        assert "WorkflowSelection" in text
        assert "OutputCandidate" in text
        assert "FinalSelection" in text
        assert "PublishPackage" in text
        assert "PlatformMetricSnapshot" in text


def test_worker_consoles_expose_phase_68d1_server_pressure_project_process() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_comfyui_client = WEB_COMFYUI_RUNTIME_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_comfyui_client = DESKTOP_COMFYUI_RUNTIME_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68D1 Server Pressure and Project Process",
            "refreshServerPressure",
            "serverPressureCards",
            "serverPressureLevel",
            "serverPressureScore",
            "projectProcessStages",
            "projectProcessScore",
            "client-server-pressure-panel",
            "client-project-process-panel",
            "client-project-process-rail",
            "comfyuiRuntimeClient.videoResourcePlan",
            "comfyuiQueueRunningCount",
            "pendingProjectReviewCount",
        ]:
            assert token in text

    for text in (web_comfyui_client, desktop_comfyui_client):
        for token in [
            "ComfyUIRuntimeHealth",
            "ComfyUIRuntimeDiagnostics",
            "ComfyUIRuntimeQueueStatus",
            "ComfyUIRuntimeVideoResourcePlan",
            "/comfyui-runtime/health",
            "/comfyui-runtime/diagnostics",
            "/comfyui-runtime/queue",
            "/comfyui-runtime/video-resource-plans",
            "server_pressure",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-server-pressure-panel",
            ".client-pressure-meter",
            ".client-server-pressure-grid",
            ".client-server-pressure-card",
            ".client-project-process-panel",
            ".client-project-process-rail",
            ".client-project-process-step",
            ".client-project-process-step.needs-action",
        ]:
            assert token in styles


def test_phase_68d1_server_pressure_project_process_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68D1_CLIENT_PRESSURE_PROCESS_VISUALIZATION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68D1 Client Server Pressure and Project Process Visualization" in text
        assert "worker_console/src/api/comfyuiRuntimeClient.ts" in text
        assert "worker_console_desktop/src/api/comfyuiRuntimeClient.ts" in text
        assert "server pressure" in text
        assert "project process" in text
        assert "ComfyUI queue" in text
        assert "video GPU admission" in text


def test_worker_consoles_expose_phase_68e_workflow_library_candidates() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68E Workflow Library Candidate Selection",
            "workflowCandidates",
            "workflowCandidateTaskId",
            "workflowCandidateTaskHasSelection",
            "refreshWorkflowCandidates",
            "selectWorkflowCandidate",
            "workflowCandidateRuntime",
            "client-workflow-candidate-panel",
            "client-workflow-candidate-grid",
            "commercialOperationClient.listWorkflowCandidates",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationWorkflowCandidate",
            "CommercialOperationWorkflowCandidateList",
            "listWorkflowCandidates",
            "/workflow-candidates",
            "runtime_readiness",
            "model_refs_missing",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-workflow-candidate-panel",
            ".client-workflow-candidate-header",
            ".client-workflow-candidate-query",
            ".client-workflow-candidate-grid",
            ".client-workflow-candidate-card",
            ".client-workflow-candidate-tags",
        ]:
            assert token in styles


def test_phase_68e_workflow_library_candidates_are_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68E_WORKFLOW_LIBRARY_CANDIDATE_SELECTION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68E Workflow Library Candidate Selection" in text
        assert "workflow-candidates" in text
        assert "CommercialOperationWorkflowCandidate" in text
        assert "WorkflowSelection" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68f_output_candidate_delivery() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68F Output Candidate Delivery",
            "outputPrepPackage",
            "outputPrepTaskId",
            "outputPrepTask",
            "refreshOutputPrepPackage",
            "registerOutputCandidateFromClient",
            "productionTaskOutputType",
            "guessOutputMimeType",
            "client-output-prep-panel",
            "client-output-prep-grid",
            "commercialOperationClient.createOutputCandidate",
            "commercialOperationClient.getOutputPrepPackage",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationOutputPrepPackage",
            "createOutputCandidate",
            "getOutputPrepPackage",
            "/output-prep-package",
            "available_output_candidates",
            "existing_final_selections",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-output-prep-panel",
            ".client-output-prep-header",
            ".client-output-prep-actions",
            ".client-output-prep-grid",
            ".client-output-prep-grid article.ready",
            ".client-output-prep-grid article.blocked",
        ]:
            assert token in styles


def test_phase_68f_output_candidate_delivery_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68F_OUTPUT_CANDIDATE_DELIVERY.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68F Output Candidate Delivery" in text
        assert "output-prep-package" in text
        assert "CommercialOperationOutputPrepPackage" in text
        assert "OutputCandidate" in text
        assert "FinalSelection" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68g_publish_package_preparation() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68G Publish Package Preparation",
            "publishPrepPackage",
            "publishPrepFinalSelectionId",
            "finalReadyForPublish",
            "publishPrepFinalSelection",
            "refreshPublishPrepPackage",
            "createPublishPackageFromClient",
            "parseHashtagInput",
            "client-publish-prep-panel",
            "client-publish-prep-grid",
            "commercialOperationClient.createPublishPackage",
            "commercialOperationClient.getPublishPrepPackage",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationPublishPrepPackage",
            "createPublishPackage",
            "getPublishPrepPackage",
            "/publish-prep-package",
            "package_blueprints",
            "existing_publish_packages",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-publish-prep-panel",
            ".client-publish-prep-header",
            ".client-publish-prep-actions",
            ".client-publish-prep-grid",
            ".client-publish-prep-grid article.ready",
            ".client-publish-prep-grid article.blocked",
        ]:
            assert token in styles


def test_phase_68g_publish_package_preparation_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68G_PUBLISH_PACKAGE_PREPARATION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68G Publish Package Preparation" in text
        assert "publish-prep-package" in text
        assert "CommercialOperationPublishPrepPackage" in text
        assert "FinalSelection" in text
        assert "PublishPackage" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68h_customer_machine_publish_execution_handoff() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68H Customer-Machine Publish Execution Handoff",
            "publishExecutionHandoff",
            "publishExecutionPackageId",
            "publishPackageReadyForExecution",
            "publishExecutionPackage",
            "refreshPublishExecutionHandoff",
            "preparePublishPackageForClientExecution",
            "client-publish-execution-panel",
            "client-publish-execution-grid",
            "commercialOperationClient.getPublishExecutionHandoff",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationPublishExecutionHandoff",
            "getPublishExecutionHandoff",
            "/client-execution-handoff",
            "client_execution_payload",
            "metric_pullback_plan",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-publish-execution-panel",
            ".client-publish-execution-header",
            ".client-publish-execution-actions",
            ".client-publish-execution-grid",
            ".client-publish-execution-grid article.ready",
            ".client-publish-execution-grid article.blocked",
        ]:
            assert token in styles


def test_phase_68h_customer_machine_publish_execution_handoff_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68H_CUSTOMER_MACHINE_PUBLISH_EXECUTION_HANDOFF.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68H Customer-Machine Publish Execution Handoff" in text
        assert "client-execution-handoff" in text
        assert "CommercialOperationPublishExecutionHandoff" in text
        assert "PublishPackage" in text
        assert "OpenClaw" in text
        assert "Playwright" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68i_publish_result_capture() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68I Customer-Machine Publish Result Capture",
            "publishExecutionResult",
            "publishExecutionResultStatus",
            "publishPackageReadyForResult",
            "publishExecutionResultPackage",
            "capturePublishExecutionResultFromClient",
            "commercialOperationClient.capturePublishExecutionResult",
            "client-publish-result-capture-panel",
            "client-publish-result-capture-grid",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationPublishExecutionResult",
            "capturePublishExecutionResult",
            "/execution-result",
            "publish_succeeded",
            "created_metric_snapshot",
            "execution_result",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-publish-result-capture-panel",
            ".client-publish-result-capture-header",
            ".client-publish-result-capture-grid",
            ".client-publish-result-capture-grid article.ready",
            ".client-publish-result-capture-grid article.blocked",
        ]:
            assert token in styles


def test_phase_68i_publish_result_capture_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68I_CUSTOMER_MACHINE_PUBLISH_RESULT_CAPTURE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68I Customer-Machine Publish Result Capture" in text
        assert "execution-result" in text
        assert "CommercialOperationPublishExecutionResult" in text
        assert "PublishPackage" in text
        assert "PlatformMetricSnapshot" in text
        assert "OpenClaw" in text
        assert "Playwright" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68j_configurable_daily_metric_analysis_schedule() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 68J Configurable Daily Metric Analysis Schedule",
            "metricAnalysisSchedule",
            "metricAnalysisScheduleStatus",
            "metricAnalysisScheduleLabel",
            "configureDailyMetricAnalysisSchedule",
            "commercialOperationClient.configureMetricAnalysisSchedule",
            "dailyAnalysisScheduleAction",
            "client-daily-analysis-panel",
            "client-daily-analysis-grid",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricAnalysisSchedule",
            "getMetricAnalysisSchedule",
            "configureMetricAnalysisSchedule",
            "/metric-analysis-schedule",
            "local_time",
            "timezone",
            "next_run_at",
        ]:
            assert token in client

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-daily-analysis-panel",
            ".client-daily-analysis-header",
            ".client-daily-analysis-grid",
            ".client-daily-analysis-grid article.ready",
            ".client-daily-analysis-grid article.blocked",
        ]:
            assert token in styles


def test_phase_68j_configurable_daily_metric_analysis_schedule_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68J_CONFIGURABLE_DAILY_METRIC_ANALYSIS_SCHEDULE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68J Configurable Daily Metric Analysis Schedule" in text
        assert "metric-analysis-schedule" in text
        assert "CommercialOperationMetricAnalysisSchedule" in text
        assert "local_time" in text
        assert "timezone" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68k_scheduled_metric_analysis_runner() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricAnalysisRun",
            "metricAnalysisRunStatus",
            "runDailyMetricAnalysisSchedule",
            "commercialOperationClient.runMetricAnalysisSchedule",
            "dailyAnalysisRunAction",
            "dailyAnalysisRunReady",
            "phase_68k_scheduled_metric_analysis_runner",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricAnalysisRun",
            "runMetricAnalysisSchedule",
            "/metric-analysis-schedule/run",
            "created_metric_snapshots",
            "usable_metric_snapshots",
            "analysis_package",
        ]:
            assert token in client


def test_phase_68k_scheduled_metric_analysis_runner_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68K_SCHEDULED_METRIC_ANALYSIS_RUNNER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68K Scheduled Metric Analysis Runner" in text
        assert "metric-analysis-schedule/run" in text
        assert "CommercialOperationMetricAnalysisRun" in text
        assert "created_metric_snapshots" in text
        assert "usable_metric_snapshots" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68l_customer_machine_metric_pullback_handoff() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricPullbackHandoff",
            "metricPullbackStatus",
            "refreshDailyMetricPullbackHandoff",
            "commercialOperationClient.getMetricPullbackHandoff",
            "dailyMetricPullbackAction",
            "dailyMetricPullbackReady",
            "phase_68l_customer_machine_metric_pullback_handoff",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricPullbackHandoff",
            "getMetricPullbackHandoff",
            "/metric-analysis-schedule/pullback-handoff",
            "pullback_tasks",
            "target_metric_keys",
            "client_adapter_plan",
            "analysis_run_request_template",
        ]:
            assert token in client


def test_phase_68l_customer_machine_metric_pullback_handoff_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68L_CUSTOMER_MACHINE_METRIC_PULLBACK_HANDOFF.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68L Customer-Machine Metric Pullback Handoff" in text
        assert "metric-analysis-schedule/pullback-handoff" in text
        assert "CommercialOperationMetricPullbackHandoff" in text
        assert "pullback_tasks" in text
        assert "target metric keys" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68m_customer_machine_metric_pullback_result_intake() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricPullbackSubmission",
            "metricPullbackSubmitStatus",
            "submitDailyMetricPullbackResult",
            "commercialOperationClient.submitMetricPullbackResult",
            "dailyMetricSubmitAction",
            "dailyMetricSubmitReady",
            "phase_68m_customer_machine_metric_pullback_result_intake",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricPullbackSubmission",
            "submitMetricPullbackResult",
            "/metric-analysis-schedule/pullback-handoff/submit-result",
            "accepted_metrics",
            "rejected_metrics",
            "metric_analysis_run",
        ]:
            assert token in client


def test_phase_68m_customer_machine_metric_pullback_result_intake_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68M_CUSTOMER_MACHINE_METRIC_PULLBACK_RESULT_INTAKE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68M Customer-Machine Metric Pullback Result Intake" in text
        assert "metric-analysis-schedule/pullback-handoff/submit-result" in text
        assert "CommercialOperationMetricPullbackResult" in text
        assert "accepted/rejected metric" in text
        assert "evidence-link" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68n_douyin_metric_adapter_profile() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricPullbackAdapterProfile",
            "metricPullbackAdapterStatus",
            "refreshDouyinMetricAdapterProfile",
            "commercialOperationClient.getMetricPullbackAdapterProfile",
            "dailyMetricAdapterAction",
            "dailyMetricAdapterReady",
            "phase_68n_douyin_metric_adapter_profile",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricPullbackAdapterProfile",
            "getMetricPullbackAdapterProfile",
            "/metric-analysis-schedule/pullback-handoff/adapter-profile",
            "field_aliases",
            "browser_assist_plan",
            "export_import_contract",
            "submission_template",
        ]:
            assert token in client


def test_phase_68n_douyin_metric_adapter_profile_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68N_DOUYIN_METRIC_ADAPTER_PROFILE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68N Douyin Metric Adapter Profile" in text
        assert "adapter-profile" in text
        assert "CommercialOperationMetricPullbackAdapterProfile" in text
        assert "field aliases" in text
        assert "browser assist" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68o_customer_machine_metric_export_import_parser() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricExportImportPreview",
            "metricExportImportStatus",
            "importMetricPullbackExportFile",
            "commercialOperationClient.previewMetricPullbackExportImport",
            "dailyMetricExportImportAction",
            "dailyMetricExportImportReady",
            "phase_68o_customer_machine_metric_export_import_parser",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricPullbackExportImportPreview",
            "previewMetricPullbackExportImport",
            "/metric-analysis-schedule/pullback-handoff/adapter-profile/parse-export",
            "submission_payload",
            "accepted_metrics",
            "rejected_rows",
        ]:
            assert token in client


def test_phase_68o_customer_machine_metric_export_import_parser_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68O_CUSTOMER_MACHINE_METRIC_EXPORT_IMPORT_PARSER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68O Customer-Machine Metric Export Import Parser" in text
        assert "parse-export" in text
        assert "CommercialOperationMetricPullbackExportImportPreview" in text
        assert "field aliases" in text
        assert "68M submission payload" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68p_customer_machine_browser_assist_metric_pullback() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricBrowserAssistSession",
            "metricBrowserAssistStatus",
            "prepareMetricBrowserAssistSession",
            "commercialOperationClient.createMetricPullbackBrowserAssistSession",
            "dailyMetricBrowserAssistAction",
            "dailyMetricBrowserAssistReady",
            "phase_68p_customer_machine_browser_assist_metric_pullback",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricPullbackBrowserAssistSession",
            "createMetricPullbackBrowserAssistSession",
            "/metric-analysis-schedule/pullback-handoff/adapter-profile/browser-assist-session",
            "navigation_targets",
            "extraction_fields",
            "forbidden_actions",
            "operator_checklist",
        ]:
            assert token in client


def test_phase_68p_customer_machine_browser_assist_metric_pullback_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68P_CUSTOMER_MACHINE_BROWSER_ASSIST_METRIC_PULLBACK.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68P Customer-Machine Browser Assist Metric Pullback" in text
        assert "browser-assist-session" in text
        assert "CommercialOperationMetricPullbackBrowserAssistSession" in text
        assert "navigation targets" in text
        assert "forbidden actions" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68q_metric_analysis_dispatch_queue() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricDispatchQueue",
            "metricDispatchStatus",
            "refreshMetricAnalysisDispatchQueue",
            "commercialOperationClient.getMetricAnalysisDispatchQueue",
            "dailyMetricDispatchAction",
            "dailyMetricDispatchReady",
            "phase_68q_metric_analysis_dispatch_queue",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricAnalysisDispatchQueue",
            "getMetricAnalysisDispatchQueue",
            "/metric-analysis-dispatch",
            "ready_dispatch_count",
            "customer_machine_actions",
            "scheduler_poll_contract",
        ]:
            assert token in client


def test_phase_68q_metric_analysis_dispatch_queue_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68Q_METRIC_ANALYSIS_DISPATCH_QUEUE.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68Q Metric Analysis Dispatch Queue" in text
        assert "metric-analysis-dispatch" in text
        assert "CommercialOperationMetricAnalysisDispatchQueue" in text
        assert "dispatch queue" in text
        assert "customer-machine action" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68r_customer_machine_metric_dispatch_claim() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricDispatchClaim",
            "metricDispatchClaimList",
            "claimMetricAnalysisDispatchTask",
            "updateMetricAnalysisDispatchClaimStatus",
            "commercialOperationClient.claimMetricAnalysisDispatch",
            "dailyMetricClaimAction",
            "dailyMetricClaimStatusAction",
            "phase_68r_customer_machine_metric_dispatch_claim",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricDispatchClaim",
            "CommercialOperationMetricDispatchClaimList",
            "claimMetricAnalysisDispatch",
            "updateMetricAnalysisDispatchClaim",
            "listMetricAnalysisDispatchClaims",
            "/metric-analysis-dispatch/claims",
            "lease_expires_at",
            "active_count",
            "completed_count",
        ]:
            assert token in client


def test_phase_68r_customer_machine_metric_dispatch_claim_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68R_CUSTOMER_MACHINE_METRIC_DISPATCH_CLAIM.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68R Customer-Machine Metric Dispatch Claim" in text
        assert "metric-analysis-dispatch/claims" in text
        assert "CommercialOperationMetricDispatchClaim" in text
        assert "lease" in text
        assert "heartbeat" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68s_customer_machine_metric_dispatch_poller() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricDispatchCustomerPoll",
            "metricDispatchPollStatus",
            "pollMetricAnalysisDispatchForCustomerMachine",
            "commercialOperationClient.pollMetricAnalysisDispatchForCustomerMachine",
            "dailyMetricPollAction",
            "dailyMetricPollReady",
            "phase_68s_customer_machine_metric_dispatch_poller",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricDispatchCustomerPoll",
            "pollMetricAnalysisDispatchForCustomerMachine",
            "/metric-analysis-dispatch/customer-poll",
            "poll_interval_seconds",
            "assigned_claims",
            "expired_claims",
            "redispatch_candidates",
        ]:
            assert token in client


def test_phase_68s_customer_machine_metric_dispatch_poller_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68S_CUSTOMER_MACHINE_METRIC_DISPATCH_POLLER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68S Customer-Machine Metric Dispatch Poller" in text
        assert "metric-analysis-dispatch/customer-poll" in text
        assert "CommercialOperationMetricDispatchCustomerPoll" in text
        assert "redispatch candidates" in text
        assert "auto claim" in text
        assert "operator approval" in text


def test_worker_consoles_expose_phase_68t_customer_machine_metric_dispatch_poll_scheduler() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricDispatchPollScheduler",
            "metricDispatchPollSchedulerStatus",
            "scheduleMetricDispatchCustomerPoll",
            "commercialOperationClient.scheduleMetricDispatchCustomerPoll",
            "dailyMetricPollScheduleAction",
            "dailyMetricPollScheduleReady",
            "phase_68t_customer_machine_metric_dispatch_poll_scheduler",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationMetricDispatchPollScheduler",
            "scheduleMetricDispatchCustomerPoll",
            "/metric-analysis-dispatch/customer-poll/scheduler",
            "notification_events",
            "client_timer_payload",
            "recommended_poll_interval_seconds",
            "next_poll_at",
        ]:
            assert token in client


def test_phase_68t_customer_machine_metric_dispatch_poll_scheduler_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68T_CUSTOMER_MACHINE_METRIC_DISPATCH_POLL_SCHEDULER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68T Customer-Machine Metric Dispatch Poll Scheduler" in text
        assert "metric-analysis-dispatch/customer-poll/scheduler" in text
        assert "CommercialOperationMetricDispatchPollScheduler" in text
        assert "notification bridge" in text
        assert "client_timer_payload" in text
        assert "operator approval" in text


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


def test_worker_consoles_expose_phase_69v_client_production_intervention_visibility() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_client, desktop_client):
        for token in [
            "CommercialOperationRoutingDecision",
            "routing_decision: CommercialOperationRoutingDecision",
            "production_intervention_queue: Record<string, unknown>",
            "production_intervention_required",
            "production_intervention_recommended_action",
            "production_intervention_queue_summary",
        ]:
            assert token in text

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69V Client Production Intervention Visibility",
            "clientProductionInterventionQueue",
            "clientProductionInterventionQueueSummary",
            "clientProductionInterventionRecommendedAction",
            "clientProductionInterventionRequired",
            "clientProductionInterventionActionKey",
            "clientProductionInterventionOperatorConfirmedRequired",
            "client-production-intervention-panel",
            "client-production-intervention-grid",
            "OpenClaw/Playwright",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-intervention-panel",
            ".client-production-intervention-panel.ready",
            ".client-production-intervention-panel.blocked",
            ".client-production-intervention-grid",
            ".client-production-intervention-grid article.ready",
            ".client-production-intervention-grid article.blocked",
            ".client-production-intervention-footer",
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_69w_client_intervention_acknowledgement() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopInterventionAcknowledgement",
            "CommercialOperationProductionClosedLoopInterventionAcknowledgementList",
            "productionClosedLoopInterventionAcknowledgements",
            "createProductionClosedLoopInterventionAcknowledgement",
            "/production-closed-loop/intervention-queue/acknowledgements",
        ]:
            assert token in text

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69W Client Intervention Acknowledgement",
            "acknowledgeClientProductionIntervention",
            "clientProductionInterventionAcknowledgementStatus",
            "clientProductionInterventionAcknowledgementLoading",
            "createProductionClosedLoopInterventionAcknowledgement",
            "recommended_action_key: clientProductionInterventionActionKey",
            "operator_confirmed: true",
            "记录已接手",
            "Acknowledge",
        ]:
            assert token in text
    assert "worker_console_project_workbench" in web_main
    assert "worker_console_desktop_project_workbench" in desktop_main


def test_worker_consoles_expose_phase_69x_client_intervention_acknowledgement_history() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperationProductionClosedLoopInterventionAcknowledgementList",
            "clientProductionInterventionAcknowledgements",
            "clientProductionInterventionAcknowledgementHistoryStatus",
            "clientProductionInterventionAcknowledgementHistoryLoading",
            "refreshClientProductionInterventionAcknowledgements",
            "productionClosedLoopInterventionAcknowledgements(nextOperationId",
            "Phase 69X Client Intervention Acknowledgement History",
            "clientProductionInterventionAcknowledgementLatestText",
            "clientProductionInterventionAcknowledgementHistoryItems",
            "local_projection_from_acknowledgement",
            "Refresh history",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-intervention-history",
            ".client-production-intervention-history-head",
            ".client-production-intervention-history-list",
            ".client-production-intervention-actions",
            ".client-production-intervention-history-list li.empty",
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_69y_client_intervention_status_controls() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69Y Client Intervention Status Controls",
            "recordClientProductionInterventionAcknowledgementStatus",
            "markClientProductionInterventionInProgress",
            "dismissClientProductionIntervention",
            '"in_progress"',
            '"dismissed"',
            'phase: "69Y"',
            "operator_confirmed: true",
            "In progress",
            "Dismiss",
            "client-production-intervention-actions",
        ]:
            assert token in text


def test_worker_consoles_expose_phase_69z_client_intervention_sla_visibility() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 69Z Client Intervention SLA Visibility",
            "clientProductionInterventionAcknowledgementSla",
            "clientProductionInterventionAcknowledgementSlaStatus",
            "clientProductionInterventionWaitingSeconds",
            "clientProductionInterventionReminderRecommended",
            "clientProductionInterventionReminderCooldownStatus",
            "clientProductionInterventionReminderDispatchStatus",
            "acknowledgement_sla",
            "reminder_recommended",
            "reminder_dispatch_cooldown",
            "reminder_dispatch_status",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-intervention-sla-grid",
            ".client-production-intervention-sla-grid article.ready",
            ".client-production-intervention-sla-grid article.blocked",
            ".client-production-intervention-sla-grid article.overdue",
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_70a_intervention_pressure_overview() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "productionInterventionPressureQueue",
            "productionInterventionPressureSummary",
            "productionInterventionPressureRequired",
            "productionInterventionPressureQueueCount",
            "productionInterventionPressureSlaStatus",
            "productionInterventionPressureReminderRecommended",
            "productionInterventionPressureLevel",
            "productionInterventionPressureScore",
            "productionInterventionPressureLabel",
            "intervention_pressure",
            "Intervention",
            "productionInterventionPressureScore +",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        assert "repeat(7, minmax(0, 1fr))" in styles
        assert "repeat(10, minmax(0, 1fr))" in styles


def test_worker_consoles_expose_phase_70g_client_objective_completion_score() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperationProductionClosedLoopAcceptanceSummary",
            "productionClosedLoopAcceptanceSummary",
            "setProductionClosedLoopAcceptanceSummary",
            "productionClosedLoopAcceptanceStatus",
            "commercialOperationClient.productionClosedLoopAcceptanceSummary",
            "clientObjectiveCompletionPercent",
            "clientObjectiveCompletionLevel",
            "clientObjectiveCompletionNextFocus",
            "clientObjectiveRemainingGates",
            "clientObjectiveScoreBreakdown",
            "serverOpenClawProviderReadiness",
            "serverOpenClawProviderStatus",
            "Phase 70G client objective completion score",
            "client-production-objective-completion",
            "client-production-objective-meter",
            "client-production-objective-gates",
            "production_closed_loop_completion_score",
            "real_publish_provider_ready",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-objective-completion",
            ".client-production-objective-meter",
            ".client-production-objective-gates",
        ]:
            assert token in styles

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopAcceptanceSummary",
            "productionClosedLoopAcceptanceSummary",
            "/commercial-operations/production-closed-loop/acceptance-summary",
            "openclaw_provider_readiness",
            "force_metric_due",
            "scan_limit",
        ]:
            assert token in client


def test_worker_consoles_expose_phase_70u_delivery_plan() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = WEB_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = DESKTOP_COMMERCIAL_OPERATION_CLIENT.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "CommercialOperationProductionClosedLoopDeliveryPlan",
            "CommercialOperationProductionClosedLoopDeliveryActionEvidenceList",
            "CommercialOperationProductionClosedLoopDeliveryActionPackages",
            "CommercialOperationProductionClosedLoopDeliveryRemediationMap",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderList",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage",
            "productionClosedLoopDeliveryPlan",
            "setProductionClosedLoopDeliveryPlan",
            "productionClosedLoopDeliveryActionPackages",
            "setProductionClosedLoopDeliveryActionPackages",
            "productionClosedLoopDeliveryRemediationMap",
            "setProductionClosedLoopDeliveryRemediationMap",
            "productionClosedLoopDeliveryAuditBlockerClearancePlan",
            "setProductionClosedLoopDeliveryAuditBlockerClearancePlan",
            "productionClosedLoopDeliveryRemediationWorkOrders",
            "setProductionClosedLoopDeliveryRemediationWorkOrders",
            "productionClosedLoopDeliveryRemediationWorkOrderCoverage",
            "setProductionClosedLoopDeliveryRemediationWorkOrderCoverage",
            "productionClosedLoopDeliveryActionEvidence",
            "setProductionClosedLoopDeliveryActionEvidence",
            "deliveryRemediationWorkOrderStatus",
            "deliveryRemediationWorkOrderLoading",
            "deliveryRemediationWorkOrderAssignmentStatus",
            "deliveryRemediationWorkOrderAssignmentLoading",
            "deliveryActionEvidenceSubmitStatus",
            "deliveryActionEvidenceSubmitLoading",
            "commercialOperationClient.productionClosedLoopDeliveryPlan",
            "commercialOperationClient.productionClosedLoopDeliveryAuditBlockerClearancePlan",
            "commercialOperationClient.productionClosedLoopDeliveryActionPackages",
            "commercialOperationClient.productionClosedLoopDeliveryRemediationMap",
            "commercialOperationClient.productionClosedLoopDeliveryRemediationWorkOrders",
            "commercialOperationClient.productionClosedLoopDeliveryRemediationWorkOrderCoverage",
            "commercialOperationClient.productionClosedLoopDeliveryRemediationWorkOrderExecutionPrep",
            "commercialOperationClient.completeProductionClosedLoopDeliveryRemediationWorkOrder",
            "commercialOperationClient.refreshProductionClosedLoopDeliveryRemediationWorkOrderReadiness",
            "commercialOperationClient.assignMissingProductionClosedLoopDeliveryRemediationWorkOrders",
            "commercialOperationClient.recordProductionClosedLoopDeliveryRemediationWorkOrder",
            "commercialOperationClient.productionClosedLoopDeliveryActionEvidenceRecords",
            "commercialOperationClient.recordProductionClosedLoopDeliveryActionEvidence",
            "recordClientDeliveryRemediationInProgress",
            "assignMissingClientDeliveryRemediationWorkOrders",
            "completeClientDeliveryRemediationWorkOrder",
            "refreshClientDeliveryRemediationWorkOrderReadiness",
            "recordClientDeliveryBlockedEvidence",
            "clientDeliveryImmediateActions",
            "clientDeliveryOpenGates",
            "clientDeliveryVisibleGates",
            "clientDeliveryAuditBlockerClearanceStatus",
            "clientDeliveryAuditBlockerClearanceVisibleItems",
            "clientDeliveryVisibleActionPackages",
            "clientDeliveryActionPackageStatus",
            "clientDeliveryVisibleRemediations",
            "clientDeliveryRemediationStatus",
            "clientDeliveryLatestWorkOrder",
            "clientDeliveryWorkOrderStatus",
            "clientDeliveryWorkOrderCoverageStatus",
            "clientDeliveryWorkOrderCoverageVisibleItems",
            "clientDeliveryWorkOrderExecutionPrepStatus",
            "clientDeliveryWorkOrderExecutionPrepVisibleItems",
            "deliveryRemediationWorkOrderCompletionStatus",
            "deliveryRemediationWorkOrderReadinessRefreshStatus",
            "clientDeliveryLatestEvidence",
            "clientDeliveryEvidenceStatus",
            "clientDeliveryStatus",
            "clientDeliveryNextFocus",
            "Phase 70U client production closed-loop delivery plan",
            "Phase 71G client delivery audit blocker clearance plan",
            "Phase 71G Blocker Clearance",
            "Assign blocker work orders",
            "clientDeliveryAuditBlockerAssignableCount",
            "Phase 71I client delivery audit blocker runbook handoff",
            "Phase 71I Runbook Handoff",
            "clientDeliveryAuditBlockerRunbookStatus",
            "clientDeliveryAuditBlockerRunbookEvidenceStatus",
            "clientDeliveryAuditBlockerRunbookEvidenceCoverageStatus",
            "clientDeliveryAuditBlockerRunbookReadinessRefreshStatus",
            "productionClosedLoopDeliveryAuditNextActionPlan",
            "setProductionClosedLoopDeliveryAuditNextActionPlan",
            "clientDeliveryAuditNextActionPlanStatus",
            "clientDeliveryAuditNextActionPlanVisibleActions",
            "productionClosedLoopDeliveryAuditOperatorQueue",
            "setProductionClosedLoopDeliveryAuditOperatorQueue",
            "clientDeliveryAuditOperatorQueueStatus",
            "clientDeliveryAuditOperatorQueueRecordStatus",
            "clientDeliveryAuditOperatorQueueVisibleGroups",
            "productionClosedLoopDeliveryAuditOpenClawProviderHandoff",
            "setProductionClosedLoopDeliveryAuditOpenClawProviderHandoff",
            "clientDeliveryAuditOpenClawProviderHandoffStatus",
            "clientDeliveryAuditOpenClawProviderHandoffVisibleItems",
            "deliveryAuditOperatorQueueRecordStatus",
            "recordClientDeliveryAuditOperatorQueueInProgress",
            "Phase 71Q operator queue control",
            "Record runbook evidence",
            "Refresh runbook readiness",
            "Phase 71O client production delivery audit next action plan",
            "Phase 71P client production delivery audit operator queue",
            "Phase 71R client production delivery audit OpenClaw provider handoff",
            "Phase 71R OpenClaw Provider Handoff",
            "Phase 70W client delivery action packages",
            "Phase 70Z client delivery remediation map",
            "Phase 71A client delivery remediation work orders",
            "Phase 71B client delivery remediation work-order coverage",
            "Phase 71D client delivery remediation work-order execution prep",
            "Phase 70X client delivery action evidence",
            "Assign missing work orders",
            "Mark in progress",
            "Record completion evidence",
            "Refresh readiness after completion",
            "Record blocked evidence",
            "client-production-delivery-plan",
            "client-production-delivery-plan-list",
            "client-production-delivery-audit-blocker-clearance",
            "client-production-delivery-audit-blocker-clearance-list",
            "client-production-delivery-audit-runbooks",
            "client-production-delivery-audit-runbook-list",
            "client-production-delivery-audit-runbook-coverage-list",
            "client-production-delivery-audit-next-action-plan",
            "client-production-delivery-audit-next-action-list",
            "client-production-delivery-audit-operator-queue",
            "client-production-delivery-audit-operator-queue-list",
            "client-production-delivery-audit-openclaw-provider-handoff",
            "client-production-delivery-audit-openclaw-provider-handoff-list",
            "client-production-delivery-action-packages",
            "client-production-delivery-action-package-list",
            "client-production-delivery-remediation-map",
            "client-production-delivery-remediation-list",
            "client-production-delivery-remediation-work-orders",
            "client-production-delivery-remediation-work-order-coverage",
            "client-production-delivery-remediation-work-order-coverage-list",
            "client-production-delivery-remediation-work-order-execution-prep",
            "client-production-delivery-remediation-work-order-execution-prep-list",
            "client-production-delivery-action-evidence",
            "production_closed_loop_delivery_plan",
            "production_closed_loop_delivery_audit_blocker_clearance_plan",
            "production_closed_loop_delivery_audit_blocker_work_order_assignment",
            "production_closed_loop_delivery_audit_blocker_runbook_handoff",
            "production_closed_loop_delivery_audit_blocker_runbook_evidence",
            "production_closed_loop_delivery_audit_blocker_runbook_evidence_coverage",
            "production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh",
            "production_closed_loop_delivery_audit_next_action_plan",
            "production_closed_loop_delivery_audit_operator_queue",
            "production_closed_loop_delivery_audit_operator_queue_record",
            "production_closed_loop_delivery_audit_openclaw_provider_handoff",
            "openclaw_provider_handoff_waiting",
            "production_closed_loop_delivery_action_packages",
            "production_closed_loop_delivery_remediation_map",
            "production_closed_loop_delivery_remediation_work_order",
            "production_closed_loop_delivery_remediation_work_order_coverage",
            "production_closed_loop_delivery_remediation_work_order_assignment",
            "production_closed_loop_delivery_remediation_work_order_execution_prep",
            "production_closed_loop_delivery_remediation_work_order_completion",
            "production_closed_loop_delivery_remediation_work_order_readiness_refresh",
            "production_closed_loop_delivery_action_evidence",
            "delivery_action_packages_only_no_external_execution",
            "delivery_remediation_map_only_no_external_execution",
            "delivery_remediation_work_order_only_no_external_execution",
            "delivery_remediation_work_order_coverage_only_no_external_execution",
            "delivery_remediation_work_order_execution_prep_only_no_external_execution",
            "delivery_remediation_work_order_completion_ready",
            "delivery_remediation_work_order_readiness_refresh_ready",
            "delivery_remediation_work_order_assignment_ready",
            "delivery_audit_blocker_work_order_assignment_ready",
            "delivery_audit_operator_queue_record_failed",
            "delivery_action_evidence_only_no_external_execution",
            "delivery_remediation_work_order_ready",
            "delivery_evidence_submit_ready",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-production-delivery-plan",
            ".client-production-delivery-plan-header",
            ".client-production-delivery-plan-list",
            ".client-production-delivery-audit-blocker-clearance",
            ".client-production-delivery-audit-blocker-clearance-list",
            ".client-production-delivery-audit-runbooks",
            ".client-production-delivery-audit-runbook-list",
            ".client-production-delivery-audit-runbook-coverage-list",
            ".client-production-delivery-audit-next-action-plan",
            ".client-production-delivery-audit-next-action-list",
            ".client-production-delivery-audit-operator-queue",
            ".client-production-delivery-audit-operator-queue-list",
            ".client-production-delivery-audit-openclaw-provider-handoff",
            ".client-production-delivery-audit-openclaw-provider-handoff-list",
            ".client-production-delivery-action-packages",
            ".client-production-delivery-action-package-list",
            ".client-production-delivery-remediation-map",
            ".client-production-delivery-remediation-list",
            ".client-production-delivery-remediation-work-orders",
            ".client-production-delivery-remediation-work-order-coverage",
            ".client-production-delivery-remediation-work-order-coverage-list",
            ".client-production-delivery-remediation-work-order-execution-prep",
            ".client-production-delivery-remediation-work-order-execution-prep-list",
            ".client-production-delivery-action-evidence",
            "article.critical",
        ]:
            assert token in styles

    for client in (web_client, desktop_client):
        for token in [
            "CommercialOperationProductionClosedLoopDeliveryPlan",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearanceItem",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignment",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentRequest",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackage",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackages",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceList",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecord",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRequest",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItem",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefresh",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRequest",
            "CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRecord",
            "CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlan",
            "CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanAction",
            "CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueue",
            "CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItem",
            "CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueGroup",
            "CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoff",
            "CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffConfigItem",
            "CommercialOperationProductionClosedLoopDeliveryPlanGate",
            "CommercialOperationProductionClosedLoopDeliveryActionPackages",
            "CommercialOperationProductionClosedLoopDeliveryActionPackage",
            "CommercialOperationProductionClosedLoopDeliveryActionStep",
            "CommercialOperationProductionClosedLoopDeliveryRemediationMap",
            "CommercialOperationProductionClosedLoopDeliveryRemediation",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderList",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRequest",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItem",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignment",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItem",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletion",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionRequest",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefresh",
            "CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest",
            "CommercialOperationProductionClosedLoopDeliveryActionEvidenceList",
            "CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecord",
            "CommercialOperationProductionClosedLoopDeliveryActionEvidenceRequest",
            "productionClosedLoopDeliveryPlan",
            "productionClosedLoopDeliveryAuditBlockerClearancePlan",
            "assignProductionClosedLoopDeliveryAuditBlockerWorkOrders",
            "productionClosedLoopDeliveryAuditBlockerRunbookPackages",
            "productionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecords",
            "recordProductionClosedLoopDeliveryAuditBlockerRunbookEvidence",
            "productionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage",
            "refreshProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadiness",
            "productionClosedLoopDeliveryAuditNextActionPlan",
            "productionClosedLoopDeliveryAuditOperatorQueue",
            "productionClosedLoopDeliveryAuditOpenClawProviderHandoff",
            "productionClosedLoopDeliveryActionPackages",
            "productionClosedLoopDeliveryRemediationMap",
            "productionClosedLoopDeliveryRemediationWorkOrders",
            "productionClosedLoopDeliveryRemediationWorkOrderCoverage",
            "productionClosedLoopDeliveryRemediationWorkOrderExecutionPrep",
            "completeProductionClosedLoopDeliveryRemediationWorkOrder",
            "refreshProductionClosedLoopDeliveryRemediationWorkOrderReadiness",
            "assignMissingProductionClosedLoopDeliveryRemediationWorkOrders",
            "recordProductionClosedLoopDeliveryRemediationWorkOrder",
            "productionClosedLoopDeliveryActionEvidenceRecords",
            "recordProductionClosedLoopDeliveryActionEvidence",
            "/commercial-operations/production-closed-loop/delivery-plan",
            "/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan",
            "/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan/assign-work-orders",
            "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages",
            "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records",
            "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage",
            "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh",
            "/commercial-operations/production-closed-loop/delivery-audit/next-action-plan",
            "/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue",
            "/commercial-operations/production-closed-loop/delivery-audit/openclaw-provider-handoff",
            "/commercial-operations/production-closed-loop/delivery-action-packages",
            "/commercial-operations/production-closed-loop/delivery-remediation-map",
            "/commercial-operations/production-closed-loop/delivery-remediation-map/work-orders",
            "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage",
            "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage/assign-missing",
            "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep",
            "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep/complete",
            "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-completion/readiness-refresh",
            "/commercial-operations/production-closed-loop/delivery-action-packages/evidence-records",
            "delivery_status",
            "clearance_status",
            "external_dependency_required",
            "immediate_actions",
            "immediate_action_packages",
            "action_package_status",
            "work_order_status",
            "coverage_status",
            "coverage_percent",
            "assignment_status",
            "prep_status",
            "ready_count",
            "completion_status",
            "readiness_refresh_next_action",
            "next_action_key",
            "created_count",
            "assignee",
            "evidence_status",
            "operator_confirmed",
            "critical_gate_count",
            "resolution_mode",
            "operator_next_step",
            "primary_console",
        ]:
            assert token in client


def test_worker_consoles_expose_phase_70h_client_publish_openclaw_dry_run_bridge() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = (ROOT / "worker_console/src/api/localWorkerClient.ts").read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = (ROOT / "worker_console_desktop/src/api/localWorkerClient.ts").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 70H Client Publish OpenClaw Dry-Run Bridge",
            "runPublishExecutionDryRunFromClient",
            "publishExecutionDryRunStatus",
            "publishExecutionDryRunLoading",
            "publishExecutionDryRunResult",
            "localWorkerClient.executeOpenClawAction",
            "client_publish_execution_dry_run_bridge",
            "phase_70h_client_publish_openclaw_dry_run_bridge",
            "publish_dry_run",
            "no_real_publish",
            "client-publish-dry-run-status",
            "client-publish-dry-run-result",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-publish-dry-run-status",
            ".client-publish-dry-run-result.ready",
        ]:
            assert token in styles

    for client in (web_client, desktop_client):
        for token in [
            "LocalWorkerOpenClawActionResponse",
            "openClawHealth",
            "openClawCapabilities",
            "executeOpenClawAction",
            "/openclaw/actions",
            "/openclaw/health",
            "/openclaw/capabilities",
        ]:
            assert token in client


def test_worker_consoles_expose_phase_70j_client_publish_submit_bridge() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 70J Client Publish Submit Bridge",
            "runPublishExecutionSubmitFromClient",
            "publishExecutionSubmitStatus",
            "publishExecutionSubmitLoading",
            "publishExecutionSubmitResult",
            "localWorkerClient.executeOpenClawAction",
            "client_publish_execution_submit_bridge",
            "phase_70j_client_publish_submit_bridge",
            "publish_submit_guarded",
            "actual_publish_performed",
            "operator_final_submit_confirmed",
            "client-publish-submit-status",
            "client-publish-submit-result",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-publish-submit-status",
            ".client-publish-submit-result.ready",
        ]:
            assert token in styles


def test_worker_consoles_expose_phase_70l_publish_provider_readiness_gate() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_styles = WEB_STYLES.read_text(encoding="utf-8")
    web_client = (ROOT / "worker_console/src/api/localWorkerClient.ts").read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_styles = DESKTOP_STYLES.read_text(encoding="utf-8")
    desktop_client = (ROOT / "worker_console_desktop/src/api/localWorkerClient.ts").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 70L Client Publish Provider Readiness Gate",
            "refreshPublishProviderReadiness",
            "publishProviderReadinessStatus",
            "publishProviderReadinessLoading",
            "LocalWorkerOpenClawHealth",
            "LocalWorkerOpenClawCapabilities",
            "client_publish_provider_readiness_gate",
            "phase_70l_client_publish_provider_readiness_gate",
            "real_publish_provider_not_configured",
            "real_publish_provider_ready",
            "real_publish_submit",
            "publish_submit_guarded",
            "client-publish-provider-readiness-status",
            "client-publish-provider-readiness",
        ]:
            assert token in text

    for styles in (web_styles, desktop_styles):
        for token in [
            ".client-publish-provider-readiness-status",
            ".client-publish-provider-readiness.ready",
        ]:
            assert token in styles

    for client in (web_client, desktop_client):
        for token in [
            "LocalWorkerOpenClawHealth",
            "LocalWorkerOpenClawCapabilities",
            "openClawHealth",
            "openClawCapabilities",
            "/openclaw/health",
            "/openclaw/capabilities",
        ]:
            assert token in client


def test_worker_consoles_expose_phase_70q_openclaw_provider_config_preflight() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    web_client = (ROOT / "worker_console/src/api/localWorkerClient.ts").read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    desktop_client = (ROOT / "worker_console_desktop/src/api/localWorkerClient.ts").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "Phase 70Q",
            "phase_70q_openclaw_provider_config_preflight",
            "client-openclaw-provider-diagnostics",
            "localOpenClawProviderDiagnostics",
            "provider_diagnostics_pending",
            "localOpenClawProviderMissingConfig",
            "localOpenClawProviderNextActions",
        ]:
            assert token in text

    for client in (web_client, desktop_client):
        for token in [
            "LocalWorkerOpenClawProviderDiagnostics",
            "openClawProviderDiagnostics",
            "/openclaw/provider-diagnostics",
            "openclaw_provider_configuration_preflight",
        ]:
            assert token in client


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
            "ingestLatestDigitalHumanVideoOutput",
            "client-digital-human-progress",
            "Digital human video",
            "digitalHumanWorkflowBindingText",
            "digitalHumanWorkflowReadinessText",
            "digitalHumanIngestionText",
            "digitalHumanDeliveryText",
            "Workflow pending",
            "Real workflow not checked",
            "ComfyUI linked",
            "Ingest video",
        ]:
            assert token in text

    for text in (web_client, desktop_client):
        for token in [
            "listVideoJobs",
            "refreshVideoJob",
            "ingestComfyuiOutput",
            '"/digital-humans/video-jobs?limit=5"',
            "`/digital-humans/video-jobs/${encodeURIComponent(jobId)}/refresh`",
            "`/digital-humans/video-jobs/${encodeURIComponent(jobId)}/comfyui-output-ingestion`",
            "progress_percent",
            "linked_comfyui_video_job_id",
            "selected_workflow_template_id",
            "workflow_binding_status",
            "workflow_readiness_status",
            "workflow_asset_upload_status",
            "workflow_output_watch_status",
            "comfyui_output_ingestion_status",
            "delivery_asset_status",
            "delivery_output_count",
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


def test_phase_68u_local_metric_dispatch_scheduler_client_surface() -> None:
    web_main = WEB_MAIN.read_text(encoding="utf-8")
    desktop_main = DESKTOP_MAIN.read_text(encoding="utf-8")
    web_client = (ROOT / "worker_console/src/api/localWorkerClient.ts").read_text(encoding="utf-8")
    desktop_client = (ROOT / "worker_console_desktop/src/api/localWorkerClient.ts").read_text(encoding="utf-8")

    for text in (web_main, desktop_main):
        for token in [
            "metricDispatchLocalScheduler",
            "tickMetricDispatchLocalScheduler",
            "configureMetricDispatchScheduler",
            "dailyMetricLocalSchedulerAction",
            "phase_68u_local_metric_dispatch_scheduler",
            "本机轮询",
        ]:
            assert token in text

    for text in (web_client, desktop_client):
        for token in [
            "MetricDispatchLocalSchedulerState",
            "/local/metric-dispatch-scheduler/configure",
            "tickMetricDispatchScheduler",
            "startMetricDispatchScheduler",
            "notification_records",
        ]:
            assert token in text


def test_phase_68u_local_metric_dispatch_scheduler_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68U_LOCAL_METRIC_DISPATCH_SCHEDULER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68U Local Metric Dispatch Scheduler" in text
        assert "client_timer_payload" in text
        assert "worker_client" in text
        assert "customer-poll" in text
