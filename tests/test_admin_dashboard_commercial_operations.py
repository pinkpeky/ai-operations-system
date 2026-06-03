"""Admin Dashboard commercial operations page checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "admin_dashboard/src/main.tsx"
CLIENT = ROOT / "admin_dashboard/src/api/client.ts"
STYLES = ROOT / "admin_dashboard/src/styles.css"


def test_admin_dashboard_exposes_commercial_operations_page() -> None:
    text = MAIN.read_text(encoding="utf-8")

    assert '"commercial-operations"' in text
    assert '"comfyui-operations"' in text
    assert "CommercialOperationsPage" in text
    assert 'surface="comfyui"' in text
    assert "isComfyuiPage" in text
    assert "商业运营" in text
    assert "Commercial Ops" in text
    assert "ComfyUI Ops" in text
    assert "ComfyUI 运行工作台" in text
    assert "Open ComfyUI tab" in text
    assert "商业运营项目中心" in text
    assert "Commercial operations center" in text
    assert "Agent / Skill orchestration" in text
    assert "commercialMaintenanceCopy" in text
    assert "Server maintenance cockpit" in text
    assert "Client frontend" in text
    assert "commercial-maintenance-cockpit" in text
    assert "commercial-action-result-drawer" in text
    assert "agentSkillState" in text
    assert "loadAgentSkillOrchestration" in text
    assert "refreshAgentSkillOrchestration" in text
    assert "controllerAgent" in text
    assert "agentSkills" in text
    assert "Phase 69K Server Primary Step Dashboard" in text
    assert "productionActionAuditState" in text
    assert "productionInterventionQueueState" in text
    assert "loadProductionActionAudits" in text
    assert "loadProductionClosedLoopInterventionQueue" in text
    assert "productionClosedLoopPrimaryStep" in text
    assert "productionClosedLoopPrimaryStepStaleness" in text
    assert "productionClosedLoopOperatorChecklist" in text
    assert "Phase 69N Production Closed-Loop Intervention Queue" in text
    assert "productionClosedLoopInterventionQueueItems" in text
    assert "productionClosedLoopInterventionQueueRows" in text
    assert "productionClosedLoopInterventionQueueCount" in text
    assert "acknowledgeProductionClosedLoopInterventionQueueItem" in text
    assert "createProductionClosedLoopInterventionAcknowledgement" in text
    assert "interventionAssignee" in text
    assert "interventionNotes" in text
    assert "ack_status" in text
    assert "productionClosedLoopInterventionReminderCount" in text
    assert "ack_sla_status" in text
    assert "ack_waiting_seconds" in text
    assert "reminder_recommended" in text
    assert "recordProductionClosedLoopInterventionReminderDispatch" in text
    assert "createProductionClosedLoopInterventionReminderDispatch" in text
    assert "interventionReminderChannel" in text
    assert "interventionReminderRecipient" in text
    assert "interventionReminderMessage" in text
    assert "reminder_dispatch_status" in text
    assert "reminder_dispatch_channel" in text
    assert "reminder_dispatch_cooldown" in text
    assert "reminder_cooldown_status" in text
    assert "next_reminder_allowed" in text
    assert "reminder_follow_up_recommended" in text
    assert "productionClosedLoopInterventionFollowUpCount" in text
    assert "productionClosedLoopInterventionQueueSummary" in text
    assert "acknowledgementSlaStatusCounts" in text
    assert "reminderDispatchStatusCounts" in text
    assert "reminderCooldownStatusCounts" in text
    assert "productionClosedLoopInterventionServerFollowUpCount" in text
    assert "productionClosedLoopInterventionOverdueCount" in text
    assert "productionClosedLoopInterventionRecommendedAction" in text
    assert "Phase 70B Server Intervention Pressure Overview" in text
    assert "productionClosedLoopInterventionPressureScore" in text
    assert "productionClosedLoopInterventionPressureLevel" in text
    assert "productionClosedLoopInterventionPressureLabel" in text
    assert "productionClosedLoopInterventionPressureDrivers" in text
    assert "productionClosedLoopInterventionPressureRecommendation" in text
    assert "productionClosedLoopInterventionPressureCards" in text
    assert "commercial-intervention-pressure-overview" in text
    assert "commercial-intervention-pressure-grid" in text
    assert "server_read_only_no_openclaw_no_playwright_no_publish" in text
    assert "productionInterventionAcknowledgementState" in text
    assert "loadProductionClosedLoopInterventionAcknowledgements" in text
    assert "productionClosedLoopInterventionAcknowledgementRecords" in text
    assert "productionClosedLoopInterventionLatestAcknowledgement" in text
    assert "recordProductionClosedLoopInterventionAcknowledgementStatus" in text
    assert "Phase 70C Server Intervention Acknowledgement History" in text
    assert "Phase 70C Server Intervention Status Controls" in text
    assert "commercial-intervention-ack-history" in text
    assert "commercial-intervention-ack-history-list" in text
    assert "commercial-intervention-status-actions" in text
    assert "Mark in progress" in text
    assert "Dismiss intervention" in text
    assert "in_progress" in text
    assert "dismissed" in text
    assert "productionClosedLoopProjectStageCounts" in text
    assert "productionClosedLoopProjectBlockerRows" in text
    assert "productionClosedLoopProjectBlockedCount" in text
    assert "productionClosedLoopProjectStageOverview" in text
    assert "Phase 70D Server Project Stage Blocking Overview" in text
    assert "commercial-project-stage-overview" in text
    assert "commercial-project-stage-grid" in text
    assert "commercial-project-blocker-list" in text
    assert "Closed-loop stage and blockers" in text
    assert "productionAcceptanceSummaryState" in text
    assert "loadProductionClosedLoopAcceptanceSummary" in text
    assert "productionClosedLoopAcceptanceSummary" in text
    assert "productionClosedLoopAcceptanceOperations" in text
    assert "productionClosedLoopAcceptanceTopBlockers" in text
    assert "productionClosedLoopAcceptanceStatus" in text
    assert "productionClosedLoopAcceptanceCards" in text
    assert "productionClosedLoopCompletionPercent" in text
    assert "productionClosedLoopCompletionLevel" in text
    assert "productionClosedLoopCompletionNextFocus" in text
    assert "productionClosedLoopRemainingGates" in text
    assert "productionClosedLoopScoreBreakdown" in text
    assert "productionClosedLoopOpenClawProviderReadiness" in text
    assert "productionClosedLoopOpenClawProviderStatus" in text
    assert "productionDeliveryPlanState" in text
    assert "productionDeliveryAuditBlockerClearancePlanState" in text
    assert "productionDeliveryActionPackagesState" in text
    assert "productionDeliveryRemediationMapState" in text
    assert "productionDeliveryRemediationWorkOrdersState" in text
    assert "productionDeliveryRemediationWorkOrderCoverageState" in text
    assert "productionDeliveryRemediationWorkOrderAssignmentState" in text
    assert "productionDeliveryRemediationWorkOrderExecutionPrepState" in text
    assert "productionDeliveryRemediationWorkOrderCompletionState" in text
    assert "productionDeliveryRemediationWorkOrderReadinessRefreshState" in text
    assert "productionDeliveryRemediationWorkOrderSubmitState" in text
    assert "productionDeliveryActionEvidenceState" in text
    assert "loadProductionClosedLoopDeliveryPlan" in text
    assert "loadProductionClosedLoopDeliveryAuditBlockerClearancePlan" in text
    assert "loadProductionClosedLoopDeliveryActionPackages" in text
    assert "loadProductionClosedLoopDeliveryRemediationMap" in text
    assert "loadProductionClosedLoopDeliveryRemediationWorkOrders" in text
    assert "loadProductionClosedLoopDeliveryRemediationWorkOrderCoverage" in text
    assert "loadProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep" in text
    assert "loadProductionClosedLoopDeliveryActionEvidenceRecords" in text
    assert "assignMissingProductionClosedLoopDeliveryRemediationWorkOrders" in text
    assert "completeProductionClosedLoopDeliveryRemediationWorkOrder" in text
    assert "refreshProductionClosedLoopDeliveryRemediationWorkOrderReadiness" in text
    assert "recordProductionClosedLoopDeliveryRemediationInProgress" in text
    assert "recordProductionClosedLoopDeliveryBlockedEvidence" in text
    assert "createProductionClosedLoopDeliveryRemediationWorkOrder" in text
    assert "createProductionClosedLoopDeliveryActionEvidenceRecord" in text
    assert "productionClosedLoopDeliveryPlan" in text
    assert "productionClosedLoopDeliveryAuditBlockerClearancePlan" in text
    assert "productionClosedLoopDeliveryActionPackages" in text
    assert "productionClosedLoopDeliveryRemediationMap" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrders" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrderCoverage" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrderExecutionPrep" in text
    assert "productionClosedLoopDeliveryActionEvidence" in text
    assert "productionClosedLoopVisibleRemediations" in text
    assert "productionClosedLoopDeliveryRemediationLatestWorkOrder" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrderStatus" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrderCoverageStatus" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrderCoverageVisibleItems" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrderExecutionPrepStatus" in text
    assert "productionClosedLoopDeliveryRemediationWorkOrderExecutionPrepVisibleItems" in text
    assert "productionDeliveryActionEvidenceSubmitState" in text
    assert "productionClosedLoopImmediateActions" in text
    assert "productionClosedLoopVisibleActionPackages" in text
    assert "productionClosedLoopDeliveryActionLatestEvidence" in text
    assert "productionClosedLoopOpenDeliveryGates" in text
    assert "productionClosedLoopDeliveryStatus" in text
    assert "productionClosedLoopDeliveryActionPackageStatus" in text
    assert "productionClosedLoopDeliveryRemediationStatus" in text
    assert "productionClosedLoopDeliveryActionEvidenceStatus" in text
    assert "Phase 70U Production Closed-Loop Delivery Plan" in text
    assert "Phase 71G Production Delivery Audit Blocker Clearance Plan" in text
    assert "Phase 71G Blocker Clearance" in text
    assert "Assign blocker work orders" in text
    assert "productionClosedLoopDeliveryAuditBlockerAssignmentStatus" in text
    assert "assignProductionClosedLoopDeliveryAuditBlockerWorkOrders" in text
    assert "Phase 71I Production Delivery Audit Blocker Runbook Handoff" in text
    assert "Phase 71I Runbook Handoff" in text
    assert "productionClosedLoopDeliveryAuditBlockerRunbookStatus" in text
    assert "productionClosedLoopDeliveryAuditBlockerRunbookEvidenceStatus" in text
    assert "productionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageStatus" in text
    assert "productionDeliveryAuditNextActionPlanState" in text
    assert "loadProductionClosedLoopDeliveryAuditNextActionPlan" in text
    assert "productionClosedLoopDeliveryAuditNextActionPlan" in text
    assert "productionClosedLoopDeliveryAuditNextActionPlanVisibleActions" in text
    assert "productionClosedLoopDeliveryAuditNextActionPlanStatus" in text
    assert "productionDeliveryAuditOperatorQueueState" in text
    assert "loadProductionClosedLoopDeliveryAuditOperatorQueue" in text
    assert "productionClosedLoopDeliveryAuditOperatorQueue" in text
    assert "productionClosedLoopDeliveryAuditOperatorQueueGroups" in text
    assert "productionClosedLoopDeliveryAuditOperatorQueueStatus" in text
    assert "productionDeliveryAuditOpenClawProviderHandoffState" in text
    assert "loadProductionClosedLoopDeliveryAuditOpenClawProviderHandoff" in text
    assert "productionClosedLoopDeliveryAuditOpenClawProviderHandoff" in text
    assert "productionClosedLoopDeliveryAuditOpenClawProviderHandoffItems" in text
    assert "productionClosedLoopDeliveryAuditOpenClawProviderHandoffStatus" in text
    assert "productionDeliveryAuditOperatorQueueRecordSubmitState" in text
    assert "recordProductionClosedLoopDeliveryAuditOperatorQueueInProgress" in text
    assert "admin_dashboard Phase 71Q operator queue control" in text
    assert "Record runbook evidence" in text
    assert "admin_dashboard Phase 71J runbook evidence control" in text
    assert "Refresh runbook readiness" in text
    assert "productionDeliveryAuditBlockerRunbookEvidenceReadinessRefreshState" in text
    assert "refreshProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadiness" in text
    assert "Phase 71O Production Delivery Audit Next Action Plan" in text
    assert "Phase 71P Production Delivery Audit Operator Queue" in text
    assert "Phase 71R OpenClaw Provider Handoff" in text
    assert "production_closed_loop_delivery_audit_openclaw_provider_handoff" in text
    assert "openclaw_provider_handoff_waiting" in text
    assert "Phase 70W Production Closed-Loop Delivery Action Packages" in text
    assert "Phase 70Z Production Delivery Remediation Map" in text
    assert "Phase 71A Production Delivery Remediation Work Orders" in text
    assert "Phase 71B Production Delivery Remediation Work Order Coverage" in text
    assert "Phase 71D Production Delivery Remediation Work Order Execution Prep" in text
    assert "Assign missing work orders" in text
    assert "Mark in progress" in text
    assert "Record completion evidence" in text
    assert "Refresh readiness after completion" in text
    assert "Record blocked evidence" in text
    assert "commercial-delivery-plan-panel" in text
    assert "commercial-delivery-plan-grid" in text
    assert "commercial-delivery-plan-list" in text
    assert "commercial-delivery-audit-blocker-clearance" in text
    assert "commercial-delivery-audit-blocker-clearance-list" in text
    assert "commercial-delivery-audit-runbooks" in text
    assert "commercial-delivery-audit-runbook-list" in text
    assert "commercial-delivery-audit-runbook-coverage-list" in text
    assert "commercial-delivery-audit-next-action-plan" in text
    assert "commercial-delivery-audit-next-action-list" in text
    assert "commercial-delivery-audit-operator-queue" in text
    assert "commercial-delivery-audit-operator-queue-list" in text
    assert "commercial-delivery-audit-openclaw-provider-handoff" in text
    assert "commercial-delivery-audit-openclaw-provider-handoff-list" in text
    assert "commercial-delivery-action-packages" in text
    assert "commercial-delivery-action-package-list" in text
    assert "commercial-delivery-remediation-map" in text
    assert "commercial-delivery-remediation-list" in text
    assert "commercial-delivery-remediation-work-orders" in text
    assert "commercial-delivery-remediation-work-order-coverage" in text
    assert "commercial-delivery-remediation-work-order-coverage-list" in text
    assert "commercial-delivery-remediation-work-order-execution-prep" in text
    assert "commercial-delivery-remediation-work-order-execution-prep-list" in text
    assert "commercial-delivery-action-evidence" in text
    assert "production_closed_loop_delivery_plan" in text
    assert "production_closed_loop_delivery_audit_blocker_clearance_plan" in text
    assert "production_closed_loop_delivery_audit_blocker_work_order_assignment" in text
    assert "production_closed_loop_delivery_audit_blocker_runbook_handoff" in text
    assert "production_closed_loop_delivery_audit_blocker_runbook_evidence" in text
    assert "production_closed_loop_delivery_audit_blocker_runbook_evidence_coverage" in text
    assert "production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh" in text
    assert "production_closed_loop_delivery_audit_next_action_plan" in text
    assert "production_closed_loop_delivery_audit_operator_queue" in text
    assert "production_closed_loop_delivery_audit_operator_queue_record" in text
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan/assign-work-orders"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/next-action-plan"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert (
        "/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue"
        in CLIENT.read_text(encoding="utf-8")
    )
    assert "production_closed_loop_delivery_action_packages" in text
    assert "production_closed_loop_delivery_remediation_map" in text
    assert "production_closed_loop_delivery_remediation_work_order" in text
    assert "production_closed_loop_delivery_remediation_work_order_coverage" in text
    assert "production_closed_loop_delivery_remediation_work_order_assignment" in text
    assert "production_closed_loop_delivery_remediation_work_order_execution_prep" in text
    assert "production_closed_loop_delivery_remediation_work_order_completion" in text
    assert "production_closed_loop_delivery_remediation_work_order_readiness_refresh" in text
    assert "production_closed_loop_delivery_action_evidence" in text
    assert "delivery_plan_only_no_external_execution" in text
    assert "delivery_action_packages_only_no_external_execution" in text
    assert "delivery_remediation_map_only_no_external_execution" in text
    assert "delivery_remediation_work_order_only_no_external_execution" in text
    assert "delivery_remediation_work_order_coverage_only_no_external_execution" in text
    assert "delivery_remediation_work_order_execution_prep_only_no_external_execution" in text
    assert "delivery_remediation_work_order_completion" in text
    assert "delivery_remediation_work_order_readiness_refresh" in text
    assert "admin_dashboard Phase 71C assignment control" in text
    assert "admin_dashboard Phase 71H audit blocker work-order assignment control" in text
    assert "admin_dashboard Phase 71E remediation work-order completion control" in text
    assert "admin_dashboard" in text
    assert "71F" in text
    assert "delivery_action_evidence_only_no_external_execution" in text
    assert "admin_dashboard Phase 71A remediation work-order control" in text
    assert "admin_dashboard Phase 70Y delivery evidence control" in text
    assert "Phase 70E Workspace Acceptance Summary" in text
    assert "Phase 70F Objective Completion Score" in text
    assert "commercial-acceptance-summary-panel" in text


def test_phase_73g_server_codex_quiet_cockpit_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73G_SERVER_CODEX_QUIET_COCKPIT.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73G Server Codex Quiet Cockpit",
        "Phase 73G Server Maintenance Detail Drawer",
        "commercial-server-quiet-cockpit",
        "commercial-server-quiet-pill",
        "commercial-server-maintenance-drawer",
        "commercial-server-maintenance-body",
        "commercial-maintenance-cockpit",
        "commercial-intervention-pressure-overview",
        "commercial-acceptance-summary-panel",
        "commercial-delivery-plan-panel",
        "commercial-project-stage-overview",
        "Production closed-loop intervention queue",
    ]:
        assert token in text

    quiet_index = text.index('aria-label="Phase 73G Server Codex Quiet Cockpit"')
    drawer_index = text.index('aria-label="Phase 73G Server Maintenance Detail Drawer"', quiet_index)
    maintenance_index = text.index('className="commercial-maintenance-cockpit"', drawer_index)
    pressure_index = text.index('className={`commercial-intervention-pressure-overview', maintenance_index)
    acceptance_index = text.index('className="commercial-acceptance-summary-panel"', pressure_index)
    delivery_index = text.index('className="commercial-delivery-plan-panel"', acceptance_index)
    project_index = text.index('className="commercial-project-stage-overview"', delivery_index)
    intervention_index = text.index('title="Production closed-loop intervention queue"', project_index)
    assert quiet_index < drawer_index < maintenance_index < pressure_index < acceptance_index < delivery_index < project_index < intervention_index

    for token in [
        ".commercial-server-quiet-cockpit",
        ".commercial-server-quiet-pill",
        ".commercial-server-maintenance-drawer",
        ".commercial-server-maintenance-drawer > summary",
        ".commercial-server-maintenance-drawer:not([open]) .commercial-server-maintenance-body",
        ".commercial-server-maintenance-body",
        "grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(160px, 0.7fr))",
        "width: 100%",
        "min-width: 0",
        ".commercial-approval-grid input",
        ".commercial-content-grid select",
        ".commercial-link-grid select",
        "max-width: 100%",
    ]:
        assert token in styles
    drawer_rule_index = styles.index(".commercial-server-maintenance-drawer:not([open]) .commercial-server-maintenance-body")
    drawer_fold_index = styles.index("display: none", drawer_rule_index)
    body_rule_index = styles.index(".commercial-server-maintenance-body {")
    assert body_rule_index >= 0
    assert drawer_rule_index < drawer_fold_index

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73G Server Codex Quiet Cockpit" in doc_text
        assert "commercial-server-quiet-cockpit" in doc_text
        assert "commercial-server-maintenance-drawer" in doc_text
        assert "commercial-maintenance-cockpit" in doc_text
        assert "commercial-acceptance-summary-panel" in doc_text
        assert "commercial-delivery-plan-panel" in doc_text
        assert "Codex-like" in doc_text
        assert "admin_dashboard" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text
    assert "commercial-acceptance-completion-strip" in text
    assert "commercial-acceptance-progress" in text
    assert "commercial-acceptance-gates" in text
    assert "commercial-acceptance-summary-grid" in text
    assert "commercial-acceptance-blocker-list" in text
    assert "production_closed_loop_acceptance_summary" in text
    assert "production_closed_loop_completion_score" in text
    assert "real_publish_provider_ready" in text
    assert "recommended_action" in text
    assert "action_key" in text


def test_phase_73h_server_quiet_create_drawer_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73H_SERVER_QUIET_CREATE_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73H Server Quiet Create Operation Drawer",
        "commercial-server-create-drawer",
        "commercial-server-create-body",
        "<Panel title={copy.createTitle}",
        "createOperation()",
        "commercial-action-result-drawer",
    ]:
        assert token in text

    quiet_index = text.index('aria-label="Phase 73G Server Codex Quiet Cockpit"')
    maintenance_index = text.index('aria-label="Phase 73G Server Maintenance Detail Drawer"', quiet_index)
    create_drawer_index = text.index('aria-label="Phase 73H Server Quiet Create Operation Drawer"', maintenance_index)
    create_body_index = text.index('className="commercial-server-create-body"', create_drawer_index)
    create_panel_index = text.index("<Panel title={copy.createTitle}", create_body_index)
    list_panel_index = text.index("<Panel title={copy.listTitle}", create_panel_index)
    assert quiet_index < maintenance_index < create_drawer_index < create_body_index < create_panel_index < list_panel_index

    for token in [
        ".commercial-server-create-drawer",
        ".commercial-server-create-drawer > summary",
        ".commercial-server-create-drawer:not([open]) .commercial-server-create-body",
        ".commercial-server-create-body",
        "grid-template-columns: minmax(0, 1fr)",
    ]:
        assert token in styles
    drawer_rule_index = styles.index(".commercial-server-create-drawer:not([open]) .commercial-server-create-body")
    drawer_fold_index = styles.index("display: none", drawer_rule_index)
    body_rule_index = styles.index(".commercial-server-create-body {")
    assert body_rule_index >= 0
    assert drawer_rule_index < drawer_fold_index

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73H Server Quiet Create Drawer" in doc_text
        assert "commercial-server-create-drawer" in doc_text
        assert "commercial-server-create-body" in doc_text
        assert "createOperation()" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text
    assert "intervention_queue_empty" in text
    assert "Record reminder dispatch" in text
    assert "operationsForTable" in text
    assert "closedLoopStalenessPriority" in text
    assert "staleClosedLoopCount" in text
    assert "production_closed_loop_primary_step_key" in text
    assert "production_closed_loop_staleness_status" in text
    assert "production_closed_loop_waiting_seconds" in text
    assert "production_closed_loop_escalation_recommended" in text
    assert "primary_step_contract" in text
    assert "primary_step_staleness_contract" in text
    assert "staleness_status" in text
    assert "escalation_recommended" in text
    assert "server_read_only_no_openclaw_no_playwright_no_publish" in text
    assert "client execution" in text
    assert 'phase: "61Z"' in text
    assert "Runtime adapter contract" in text
    assert "Phase 62F" in text
    assert 'phase: "62G"' in text
    assert 'phase: "62H"' in text
    assert "read_only_probe_enabled" in text
    assert "read_only_probe_attempted" in text
    assert "readiness_status" in text


def test_phase_73i_server_operation_context_drawer_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73I_SERVER_OPERATION_CONTEXT_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73I Server Operation Context Drawer",
        "commercial-server-operation-context-drawer",
        "commercial-server-operation-context-body",
        "<Panel title={copy.detailTitle}",
        "<Panel",
        "title={copy.agentSkillTitle}",
        "refreshAgentSkillOrchestration()",
    ]:
        assert token in text

    list_panel_index = text.index("<Panel title={copy.listTitle}")
    context_drawer_index = text.index('aria-label="Phase 73I Server Operation Context Drawer"', list_panel_index)
    context_body_index = text.index('className="commercial-server-operation-context-body"', context_drawer_index)
    detail_panel_index = text.index("<Panel title={copy.detailTitle}", context_body_index)
    agent_panel_index = text.index("title={copy.agentSkillTitle}", detail_panel_index)
    action_audit_index = text.index('title="Production closed-loop action audit"', agent_panel_index)
    assert list_panel_index < context_drawer_index < context_body_index < detail_panel_index < agent_panel_index < action_audit_index

    for token in [
        ".commercial-server-operation-context-drawer",
        ".commercial-server-operation-context-drawer > summary",
        ".commercial-server-operation-context-drawer:not([open]) .commercial-server-operation-context-body",
        ".commercial-server-operation-context-body",
        "grid-template-columns: minmax(0, 1fr)",
    ]:
        assert token in styles
    drawer_rule_index = styles.index(".commercial-server-operation-context-drawer:not([open]) .commercial-server-operation-context-body")
    drawer_fold_index = styles.index("display: none", drawer_rule_index)
    body_rule_index = styles.index(".commercial-server-operation-context-body {")
    assert body_rule_index >= 0
    assert drawer_rule_index < drawer_fold_index

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73I Server Operation Context Drawer" in doc_text
        assert "commercial-server-operation-context-drawer" in doc_text
        assert "commercial-server-operation-context-body" in doc_text
        assert "Agent/Skill" in doc_text
        assert "admin_dashboard" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text
    assert "diagnostic_blockers" in text
    assert "recommended_actions" in text
    assert "snapshot_count" in text
    assert "latest_snapshot_status" in text
    assert "latest_snapshot_at" in text
    assert "latest_snapshot_note" in text
    assert "Maintenance runbook" in text
    assert "maintenance_runbook_phase" in text
    assert "next_operator_action" in text
    assert "snapshot_recommended" in text
    assert "recovery_actions" in text
    assert "config_change_request_count" in text
    assert "latest_config_change_status" in text
    assert "latest_config_change_at" in text
    assert "manual_apply_evidence_count" in text
    assert "latest_manual_apply_status" in text
    assert "latest_manual_apply_at" in text
    assert "post_manual_readiness_count" in text
    assert "latest_post_manual_check_status" in text
    assert "latest_post_manual_comparison" in text
    assert "guarded_probe_execution_count" in text
    assert "latest_guarded_probe_status" in text
    assert "latest_guarded_probe_result" in text
    assert "Guarded probe executions" in text
    assert "Execute read-only probe" in text
    assert "Config change requests" in text
    assert "Manual apply evidence" in text
    assert "Post-manual readiness" in text
    assert "创建配置变更申请" in text
    assert "送审配置申请" in text
    assert "批准人工应用" in text
    assert "记录人工应用证据" in text
    assert "创建就绪对比" in text
    assert "updateComfyuiRuntimeConfigChangeRequestStatus" in text
    assert "createComfyuiRuntimeConfigChangeRequest" in text
    assert "createComfyuiRuntimeManualApplyEvidence" in text
    assert "updateComfyuiRuntimeManualApplyEvidenceStatus" in text
    assert "createComfyuiRuntimePostManualReadinessCheck" in text
    assert "updateComfyuiRuntimePostManualReadinessCheckStatus" in text
    assert "createComfyuiRuntimeGuardedProbeExecution" in text
    assert "updateComfyuiRuntimeGuardedProbeExecutionStatus" in text
    assert "executeComfyuiRuntimeGuardedProbeExecution" in text
    assert "saveComfyuiRuntimeDiagnosticSnapshot" in text
    assert "allowed_health_paths" in text
    assert "probe_latency_ms" in text
    assert "health_probe_deferred_to_guarded_execution" in text
    assert "Video resource plan" in text
    assert "Check video resources" in text
    assert "Video generation jobs" in text
    assert "Create video job" in text
    assert "Refresh latest job" in text
    assert "video_job_count" in text
    assert "latest_video_job_status" in text
    assert "createComfyuiVideoJob" in text
    assert "refreshComfyuiVideoJob" in text
    assert "should_submit_now" in text
    assert "selected_endpoint" in text
    assert "endpoint_plans" in text
    assert "planComfyuiVideoResources" in text
    assert "comfyuiRuntimeApi.capabilities" in text
    assert "comfyuiRuntimeApi.diagnostics" in text
    assert "comfyuiRuntimeApi.maintenanceRunbook" in text
    assert "comfyuiRuntimeApi.configChangeRequests" in text
    assert "comfyuiRuntimeApi.createConfigChangeRequest" in text
    assert "comfyuiRuntimeApi.updateConfigChangeRequestStatus" in text
    assert "comfyuiRuntimeApi.manualApplyEvidence" in text
    assert "comfyuiRuntimeApi.createManualApplyEvidence" in text
    assert "comfyuiRuntimeApi.updateManualApplyEvidenceStatus" in text
    assert "comfyuiRuntimeApi.postManualReadinessChecks" in text
    assert "comfyuiRuntimeApi.createPostManualReadinessCheck" in text
    assert "comfyuiRuntimeApi.updatePostManualReadinessCheckStatus" in text
    assert "comfyuiRuntimeApi.guardedProbeExecutions" in text
    assert "comfyuiRuntimeApi.createGuardedProbeExecution" in text
    assert "comfyuiRuntimeApi.updateGuardedProbeExecutionStatus" in text
    assert "comfyuiRuntimeApi.executeGuardedProbeExecution" in text
    assert "comfyuiRuntimeApi.videoResourcePlan" in text
    assert "comfyuiRuntimeApi.videoJobs" in text
    assert "comfyuiRuntimeApi.createVideoJob" in text
    assert "comfyuiRuntimeApi.refreshVideoJob" in text
    assert "comfyuiRuntimeApi.diagnosticSnapshots" in text
    assert "comfyuiRuntimeApi.createDiagnosticSnapshot" in text
    assert "Approval gates" in text
    assert "Safe dry-runs" in text
    assert "Content drafts" in text
    assert "Asset requests" in text
    assert "ComfyUI handoffs" in text
    assert "ComfyUI preflights" in text
    assert "ComfyUI adapter configs" in text
    assert "ComfyUI job requests" in text
    assert "ComfyUI execution plans" in text
    assert "ComfyUI connection probes" in text
    assert "ComfyUI adapter dispatches" in text
    assert "ComfyUI runtime gates" in text
    assert "ComfyUI runtime dry-runs" in text
    assert "ComfyUI runtime activations" in text
    assert "Deliverables" in text
    assert "Evidence snapshots" in text
    assert "Execution requests" in text
    assert "Execution runs" in text
    assert "Results" in text
    assert "Monitoring observations" in text
    assert "Optimization decisions" in text
    assert "证据与交接" in text
    assert "Evidence and handoff" in text
    assert "不会自动发布" in text
    assert "does not publish" in text
    assert "commercialOperationsApi.list" in text
    assert "commercialOperationsApi.create" in text
    assert "commercialOperationsApi.planDraft" in text
    assert "commercialOperationsApi.update" in text
    assert "commercialOperationsApi.agentSkillOrchestration" in text
    assert "commercialOperationsApi.refreshAgentSkillOrchestration" in text
    assert "commercialOperationsApi.approvals" in text
    assert "commercialOperationsApi.createApproval" in text
    assert "commercialOperationsApi.approveApproval" in text
    assert "commercialOperationsApi.rejectApproval" in text
    assert "commercialOperationsApi.cancelApproval" in text
    assert "commercialOperationsApi.dryRuns" in text
    assert "commercialOperationsApi.createDryRun" in text
    assert "commercialOperationsApi.completeDryRun" in text
    assert "commercialOperationsApi.failDryRun" in text
    assert "commercialOperationsApi.cancelDryRun" in text
    assert "commercialOperationsApi.contentDrafts" in text
    assert "commercialOperationsApi.createContentDraft" in text
    assert "commercialOperationsApi.generateContentDraft" in text
    assert "commercialOperationsApi.updateContentDraft" in text
    assert "commercialOperationsApi.readyContentDraft" in text
    assert "commercialOperationsApi.approveContentDraft" in text
    assert "commercialOperationsApi.rejectContentDraft" in text
    assert "commercialOperationsApi.archiveContentDraft" in text
    assert "commercialOperationsApi.assetRequests" in text
    assert "commercialOperationsApi.createAssetRequest" in text
    assert "commercialOperationsApi.generateAssetRequest" in text
    assert "commercialOperationsApi.updateAssetRequest" in text
    assert "commercialOperationsApi.readyAssetRequest" in text
    assert "commercialOperationsApi.approveAssetRequest" in text
    assert "commercialOperationsApi.rejectAssetRequest" in text
    assert "commercialOperationsApi.prepareAssetRequest" in text
    assert "commercialOperationsApi.failAssetRequest" in text
    assert "commercialOperationsApi.archiveAssetRequest" in text
    assert "commercialOperationsApi.comfyuiHandoffs" in text
    assert "commercialOperationsApi.createComfyuiHandoff" in text
    assert "commercialOperationsApi.updateComfyuiHandoff" in text
    assert "commercialOperationsApi.readyComfyuiHandoff" in text
    assert "commercialOperationsApi.approveComfyuiHandoff" in text
    assert "commercialOperationsApi.rejectComfyuiHandoff" in text
    assert "commercialOperationsApi.prepareComfyuiHandoff" in text
    assert "commercialOperationsApi.failComfyuiHandoff" in text
    assert "commercialOperationsApi.archiveComfyuiHandoff" in text
    assert "commercialOperationsApi.comfyuiPreflights" in text
    assert "commercialOperationsApi.createComfyuiPreflight" in text
    assert "commercialOperationsApi.updateComfyuiPreflight" in text
    assert "commercialOperationsApi.checkComfyuiPreflight" in text
    assert "commercialOperationsApi.failComfyuiPreflight" in text
    assert "commercialOperationsApi.archiveComfyuiPreflight" in text
    assert "commercialOperationsApi.comfyuiAdapterConfigs" in text
    assert "commercialOperationsApi.createComfyuiAdapterConfig" in text
    assert "commercialOperationsApi.updateComfyuiAdapterConfig" in text
    assert "commercialOperationsApi.validateComfyuiAdapterConfig" in text
    assert "commercialOperationsApi.failComfyuiAdapterConfig" in text
    assert "commercialOperationsApi.archiveComfyuiAdapterConfig" in text
    assert "commercialOperationsApi.comfyuiJobRequests" in text
    assert "commercialOperationsApi.createComfyuiJobRequest" in text
    assert "commercialOperationsApi.updateComfyuiJobRequest" in text
    assert "commercialOperationsApi.readyComfyuiJobRequest" in text
    assert "commercialOperationsApi.approveComfyuiJobRequest" in text
    assert "commercialOperationsApi.rejectComfyuiJobRequest" in text
    assert "commercialOperationsApi.queueComfyuiJobRequest" in text
    assert "commercialOperationsApi.failComfyuiJobRequest" in text
    assert "commercialOperationsApi.cancelComfyuiJobRequest" in text
    assert "commercialOperationsApi.archiveComfyuiJobRequest" in text
    assert "commercialOperationsApi.comfyuiExecutionPlans" in text
    assert "commercialOperationsApi.createComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.updateComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.readyComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.approveComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.rejectComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.simulateComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.failComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.cancelComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.archiveComfyuiExecutionPlan" in text
    assert "commercialOperationsApi.comfyuiConnectionProbes" in text
    assert "commercialOperationsApi.createComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.updateComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.readyComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.approveComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.rejectComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.probeComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.failComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.cancelComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.archiveComfyuiConnectionProbe" in text
    assert "commercialOperationsApi.comfyuiAdapterDispatches" in text
    assert "commercialOperationsApi.createComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.updateComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.readyComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.approveComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.rejectComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.dispatchComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.failComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.cancelComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.archiveComfyuiAdapterDispatch" in text
    assert "commercialOperationsApi.comfyuiRuntimeGates" in text
    assert "commercialOperationsApi.createComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.updateComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.readyComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.approveComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.rejectComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.armComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.failComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.disableComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.archiveComfyuiRuntimeGate" in text
    assert "commercialOperationsApi.comfyuiRuntimeDryRuns" in text
    assert "commercialOperationsApi.createComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.updateComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.readyComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.approveComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.rejectComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.validateComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.failComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.cancelComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.archiveComfyuiRuntimeDryRun" in text
    assert "commercialOperationsApi.comfyuiRuntimeActivations" in text
    assert "commercialOperationsApi.createComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.updateComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.readyComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.approveComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.rejectComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.scheduleComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.failComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.cancelComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.archiveComfyuiRuntimeActivation" in text
    assert "commercialOperationsApi.deliverables" in text
    assert "commercialOperationsApi.createDeliverable" in text
    assert "commercialOperationsApi.updateDeliverable" in text
    assert "commercialOperationsApi.readyDeliverable" in text
    assert "commercialOperationsApi.approveDeliverable" in text
    assert "commercialOperationsApi.rejectDeliverable" in text
    assert "commercialOperationsApi.packageDeliverable" in text
    assert "commercialOperationsApi.failDeliverable" in text
    assert "commercialOperationsApi.archiveDeliverable" in text
    assert "commercialOperationsApi.evidenceSnapshots" in text
    assert "commercialOperationsApi.createEvidenceSnapshot" in text
    assert "commercialOperationsApi.generateEvidenceSnapshot" in text
    assert "commercialOperationsApi.updateEvidenceSnapshot" in text
    assert "commercialOperationsApi.readyEvidenceSnapshot" in text
    assert "commercialOperationsApi.approveEvidenceSnapshot" in text
    assert "commercialOperationsApi.rejectEvidenceSnapshot" in text
    assert "commercialOperationsApi.archiveEvidenceSnapshot" in text
    assert "commercialOperationsApi.executionRequests" in text
    assert "commercialOperationsApi.createExecutionRequest" in text
    assert "commercialOperationsApi.updateExecutionRequest" in text
    assert "commercialOperationsApi.readyExecutionRequest" in text
    assert "commercialOperationsApi.approveExecutionRequest" in text
    assert "commercialOperationsApi.rejectExecutionRequest" in text
    assert "commercialOperationsApi.prepareExecutionRequest" in text
    assert "commercialOperationsApi.failExecutionRequest" in text
    assert "commercialOperationsApi.cancelExecutionRequest" in text
    assert "commercialOperationsApi.archiveExecutionRequest" in text
    assert "commercialOperationsApi.executionRuns" in text
    assert "commercialOperationsApi.createExecutionRun" in text
    assert "commercialOperationsApi.updateExecutionRun" in text
    assert "commercialOperationsApi.startExecutionRun" in text
    assert "commercialOperationsApi.succeedExecutionRun" in text
    assert "commercialOperationsApi.failExecutionRun" in text
    assert "commercialOperationsApi.retryExecutionRun" in text
    assert "commercialOperationsApi.cancelExecutionRun" in text
    assert "commercialOperationsApi.archiveExecutionRun" in text
    assert "commercialOperationsApi.results" in text
    assert "commercialOperationsApi.createResult" in text
    assert "commercialOperationsApi.updateResult" in text
    assert "commercialOperationsApi.readyResult" in text
    assert "commercialOperationsApi.approveResult" in text
    assert "commercialOperationsApi.rejectResult" in text
    assert "commercialOperationsApi.archiveResult" in text
    assert "commercialOperationsApi.monitoringObservations" in text
    assert "commercialOperationsApi.createMonitoringObservation" in text
    assert "commercialOperationsApi.updateMonitoringObservation" in text
    assert "commercialOperationsApi.readyMonitoringObservation" in text
    assert "commercialOperationsApi.approveMonitoringObservation" in text
    assert "commercialOperationsApi.rejectMonitoringObservation" in text
    assert "commercialOperationsApi.archiveMonitoringObservation" in text
    assert "commercialOperationsApi.optimizationDecisions" in text
    assert "commercialOperationsApi.createOptimizationDecision" in text
    assert "commercialOperationsApi.updateOptimizationDecision" in text
    assert "commercialOperationsApi.readyOptimizationDecision" in text
    assert "commercialOperationsApi.approveOptimizationDecision" in text
    assert "commercialOperationsApi.rejectOptimizationDecision" in text
    assert "commercialOperationsApi.archiveOptimizationDecision" in text
    assert "commercialOperationsApi.links" in text
    assert "commercialOperationsApi.createLink" in text
    assert "commercialOperationsApi.deleteLink" in text
    assert "Generate draft from RAG" in text
    assert "Generate request from RAG" in text
    assert "RAG query" in text
    assert "Search mode" in text


def test_phase_73j_server_action_audit_drawer_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73J_SERVER_ACTION_AUDIT_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73J Server Action Audit Drawer",
        "commercial-server-action-audit-drawer",
        "commercial-server-action-audit-body",
        'title="Production closed-loop action audit"',
        "productionClosedLoopActionAudits",
        "productionClosedLoopOperatorChecklist",
        "server_read_only_no_openclaw_no_playwright_no_publish",
    ]:
        assert token in text

    context_drawer_index = text.index('aria-label="Phase 73I Server Operation Context Drawer"')
    action_drawer_index = text.index('aria-label="Phase 73J Server Action Audit Drawer"', context_drawer_index)
    action_body_index = text.index('className="commercial-server-action-audit-body"', action_drawer_index)
    action_panel_index = text.index('title="Production closed-loop action audit"', action_body_index)
    primary_grid_index = text.index('label="primary_step"', action_panel_index)
    checklist_index = text.index("rows={productionClosedLoopOperatorChecklist}", primary_grid_index)
    comfyui_branch_index = text.index("{isComfyuiPage ? (", checklist_index)
    assert context_drawer_index < action_drawer_index < action_body_index < action_panel_index < primary_grid_index < checklist_index < comfyui_branch_index

    for token in [
        ".commercial-server-action-audit-drawer",
        ".commercial-server-action-audit-drawer > summary",
        ".commercial-server-action-audit-drawer:not([open]) .commercial-server-action-audit-body",
        ".commercial-server-action-audit-body",
        "grid-template-columns: minmax(0, 1fr)",
    ]:
        assert token in styles
    drawer_rule_index = styles.index(".commercial-server-action-audit-drawer:not([open]) .commercial-server-action-audit-body")
    drawer_fold_index = styles.index("display: none", drawer_rule_index)
    body_rule_index = styles.index(".commercial-server-action-audit-body {")
    assert body_rule_index >= 0
    assert drawer_rule_index < drawer_fold_index

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73J Server Action Audit Drawer" in doc_text
        assert "commercial-server-action-audit-drawer" in doc_text
        assert "commercial-server-action-audit-body" in doc_text
        assert "Production closed-loop action audit" in doc_text
        assert "operator checklist" in doc_text
        assert "admin_dashboard" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text


def test_phase_73k_server_production_workstream_drawers_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73K_SERVER_PRODUCTION_WORKSTREAM_DRAWERS.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73K Server Production Upstream Drawer",
        "Phase 73K Server Production Closed Loop Drawer",
        "commercial-server-production-upstream-drawer",
        "commercial-server-production-upstream-body",
        "commercial-server-production-closed-loop-drawer",
        "commercial-server-production-closed-loop-body",
        "Production content and assets",
        "Production delivery loop",
        "title={comfyuiSurfaceCopy.entryTitle}",
        "title={contentCopy.title}",
        "title={assetCopy.title}",
        "title={deliverableCopy.title}",
        "title={executionRunCopy.title}",
        "title={optimizationCopy.title}",
        "title={copy.linksTitle}",
    ]:
        assert token in text

    action_drawer_index = text.index('aria-label="Phase 73J Server Action Audit Drawer"')
    upstream_drawer_index = text.index('aria-label="Phase 73K Server Production Upstream Drawer"', action_drawer_index)
    upstream_body_index = text.index('className="commercial-server-production-upstream-body"', upstream_drawer_index)
    comfyui_entry_index = text.index("title={comfyuiSurfaceCopy.entryTitle}", upstream_body_index)
    content_panel_index = text.index("title={contentCopy.title}", comfyui_entry_index)
    asset_panel_index = text.index("title={assetCopy.title}", content_panel_index)
    comfyui_branch_index = text.index("{isComfyuiPage ? (", asset_panel_index)
    closed_loop_drawer_index = text.index('aria-label="Phase 73K Server Production Closed Loop Drawer"', comfyui_branch_index)
    closed_loop_body_index = text.index('className="commercial-server-production-closed-loop-body"', closed_loop_drawer_index)
    deliverable_panel_index = text.index("title={deliverableCopy.title}", closed_loop_body_index)
    execution_run_index = text.index("title={executionRunCopy.title}", deliverable_panel_index)
    optimization_index = text.index("title={optimizationCopy.title}", execution_run_index)
    links_index = text.index("title={copy.linksTitle}", optimization_index)
    assert (
        action_drawer_index
        < upstream_drawer_index
        < upstream_body_index
        < comfyui_entry_index
        < content_panel_index
        < asset_panel_index
        < comfyui_branch_index
        < closed_loop_drawer_index
        < closed_loop_body_index
        < deliverable_panel_index
        < execution_run_index
        < optimization_index
        < links_index
    )

    for token in [
        ".commercial-server-production-upstream-drawer",
        ".commercial-server-production-closed-loop-drawer",
        ".commercial-server-production-upstream-drawer > summary",
        ".commercial-server-production-closed-loop-drawer > summary",
        ".commercial-server-production-upstream-drawer:not([open]) .commercial-server-production-upstream-body",
        ".commercial-server-production-closed-loop-drawer:not([open]) .commercial-server-production-closed-loop-body",
        ".commercial-server-production-upstream-body",
        ".commercial-server-production-closed-loop-body",
        "grid-template-columns: minmax(0, 1fr)",
    ]:
        assert token in styles
    upstream_rule_index = styles.index(".commercial-server-production-upstream-drawer:not([open]) .commercial-server-production-upstream-body")
    upstream_fold_index = styles.index("display: none", upstream_rule_index)
    closed_rule_index = styles.index(".commercial-server-production-closed-loop-drawer:not([open]) .commercial-server-production-closed-loop-body")
    closed_fold_index = styles.index("display: none", closed_rule_index)
    body_rule_index = styles.index(".commercial-server-production-upstream-body,", closed_fold_index)
    assert upstream_rule_index < upstream_fold_index < body_rule_index
    assert closed_rule_index < closed_fold_index < body_rule_index

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73K Server Production Workstream Drawers" in doc_text
        assert "commercial-server-production-upstream-drawer" in doc_text
        assert "commercial-server-production-closed-loop-drawer" in doc_text
        assert "content drafts" in doc_text
        assert "deliverables" in doc_text
        assert "admin_dashboard" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text


def test_phase_73l_server_operation_list_drawer_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73L_SERVER_OPERATION_LIST_DRAWER.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73L Server Operation List Drawer",
        "commercial-server-operation-list-drawer",
        "commercial-server-operation-list-body",
        "Operation queue",
        "<Panel title={copy.listTitle}",
        "operationsForTable",
        "selectedId={selectedOperation ? valueAt(selectedOperation, [\"id\"]) : null}",
        "onSelect={(row) => setSelectedOperation(row)}",
    ]:
        assert token in text

    create_drawer_index = text.index('aria-label="Phase 73H Server Quiet Create Operation Drawer"')
    operation_list_drawer_index = text.index('aria-label="Phase 73L Server Operation List Drawer"', create_drawer_index)
    operation_list_body_index = text.index('className="commercial-server-operation-list-body"', operation_list_drawer_index)
    operation_list_panel_index = text.index("<Panel title={copy.listTitle}", operation_list_body_index)
    table_index = text.index("rows={operationsForTable}", operation_list_panel_index)
    context_drawer_index = text.index('aria-label="Phase 73I Server Operation Context Drawer"', table_index)
    assert create_drawer_index < operation_list_drawer_index < operation_list_body_index < operation_list_panel_index < table_index < context_drawer_index

    for token in [
        ".commercial-server-operation-list-drawer",
        ".commercial-server-operation-list-drawer > summary",
        ".commercial-server-operation-list-drawer:not([open]) .commercial-server-operation-list-body",
        ".commercial-server-operation-list-body",
        "grid-template-columns: minmax(0, 1fr)",
    ]:
        assert token in styles
    drawer_rule_index = styles.index(".commercial-server-operation-list-drawer:not([open]) .commercial-server-operation-list-body")
    drawer_fold_index = styles.index("display: none", drawer_rule_index)
    body_rule_index = styles.index("\n.commercial-server-operation-list-body {", drawer_fold_index)
    assert drawer_rule_index < drawer_fold_index < body_rule_index

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73L Server Operation List Drawer" in doc_text
        assert "commercial-server-operation-list-drawer" in doc_text
        assert "commercial-server-operation-list-body" in doc_text
        assert "Operation queue" in doc_text
        assert "operationsForTable" in doc_text
        assert "admin_dashboard" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text


def test_phase_73p_server_production_index_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73P_SERVER_PRODUCTION_INDEX.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73P Server Production Index",
        "commercialServerProductionIndexCards",
        "openCommercialServerDrawer",
        "commercial-server-production-index",
        "commercial-server-production-index-head",
        "commercial-server-production-index-grid",
        "commercial-server-production-index-card",
        ".commercial-server-maintenance-drawer",
        ".commercial-server-operation-list-drawer",
        ".commercial-server-operation-context-drawer",
        ".commercial-server-action-audit-drawer",
        ".commercial-server-production-upstream-drawer",
        ".commercial-server-production-closed-loop-drawer",
    ]:
        assert token in text

    quiet_index = text.index('aria-label="Phase 73G Server Codex Quiet Cockpit"')
    production_index = text.index('aria-label="Phase 73P Server Production Index"', quiet_index)
    maintenance_index = text.index('aria-label="Phase 73G Server Maintenance Detail Drawer"', production_index)
    create_index = text.index('aria-label="Phase 73H Server Quiet Create Operation Drawer"', maintenance_index)
    operation_list_index = text.index('aria-label="Phase 73L Server Operation List Drawer"', create_index)
    context_index = text.index('aria-label="Phase 73I Server Operation Context Drawer"', operation_list_index)
    audit_index = text.index('aria-label="Phase 73J Server Action Audit Drawer"', context_index)
    upstream_index = text.index('aria-label="Phase 73K Server Production Upstream Drawer"', audit_index)
    closed_loop_index = text.index('aria-label="Phase 73K Server Production Closed Loop Drawer"', upstream_index)
    assert quiet_index < production_index < maintenance_index < create_index < operation_list_index < context_index < audit_index < upstream_index < closed_loop_index

    for token in [
        ".commercial-server-production-index",
        ".commercial-server-production-index-head",
        ".commercial-server-production-index-grid",
        ".commercial-server-production-index-card",
        ".commercial-server-production-index-card.hot",
        ".commercial-server-production-index-card.busy",
        ".commercial-server-production-index-card.healthy",
        ".commercial-server-production-index-card.blocked",
        "grid-template-columns: repeat(3, minmax(0, 1fr))",
    ]:
        assert token in styles

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73P Server Production Index" in doc_text
        assert "commercial-server-production-index" in doc_text
        assert "commercialServerProductionIndexCards" in doc_text
        assert "openCommercialServerDrawer" in doc_text
        assert "Codex-like" in doc_text
        assert "admin_dashboard" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text


def test_phase_73r_production_release_gate_checklist_contract() -> None:
    text = MAIN.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    phase_doc = (ROOT / "docs/PHASE_73R_PRODUCTION_RELEASE_GATE_CHECKLIST.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    current_runtime = (ROOT / "docs/CURRENT_RUNTIME.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    foundation = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for token in [
        "Phase 73R Production Release Gate Checklist",
        "productionClosedLoopReleaseGateChecklist",
        "release_gate_checklist",
        "commercial-release-gate-checklist",
        "gate.blocking_reasons",
        "gate.evidence",
    ]:
        assert token in text

    blocker_index = text.index('className="commercial-acceptance-blocker-list"')
    checklist_index = text.index('aria-label="Phase 73R Production Release Gate Checklist"', blocker_index)
    footer_index = text.index('className="commercial-acceptance-summary-footer"', checklist_index)
    assert blocker_index < checklist_index < footer_index

    for token in [
        ".commercial-release-gate-checklist",
        ".commercial-release-gate-checklist article",
        ".commercial-release-gate-checklist article.blocked",
        ".commercial-release-gate-checklist article.ready",
        "grid-template-columns: repeat(3, minmax(0, 1fr))",
        ".commercial-release-gate-checklist p",
        ".commercial-release-gate-checklist small",
    ]:
        assert token in styles

    for doc_text in (phase_doc, phase_index, current_next, current_runtime, project_status, foundation):
        assert "Phase 73R Production Release Gate Checklist" in doc_text
        assert "release_gate_checklist" in doc_text
        assert "production_release_gate_checklist_is_machine_readable" in doc_text
        assert "real_openclaw_publish_provider" in doc_text
        assert "customer_machine_publish_result_evidence" in doc_text
        assert "commercial-release-gate-checklist" in doc_text
        assert "scripts/check_production_closed_loop.py" in doc_text
        assert "does not" in doc_text
        assert "bypass approval" in doc_text


def test_admin_dashboard_commercial_operations_api_client_paths() -> None:
    text = CLIENT.read_text(encoding="utf-8")

    assert "export const commercialOperationsApi" in text
    assert "export const comfyuiRuntimeApi" in text
    assert "/commercial-operations" in text
    assert "/comfyui-runtime/health" in text
    assert "/comfyui-runtime/capabilities" in text
    assert "/comfyui-runtime/diagnostics" in text
    assert "/comfyui-runtime/maintenance-runbook" in text
    assert "/comfyui-runtime/config-change-requests" in text
    assert "/comfyui-runtime/config-change-requests/${encodeURIComponent(requestId)}/${encodeURIComponent(action)}" in text
    assert "/comfyui-runtime/manual-apply-evidence" in text
    assert "/comfyui-runtime/config-change-requests/${encodeURIComponent(requestId)}/manual-apply-evidence" in text
    assert "/comfyui-runtime/manual-apply-evidence/${encodeURIComponent(evidenceId)}/${encodeURIComponent(action)}" in text
    assert "/comfyui-runtime/post-manual-readiness-checks" in text
    assert "/comfyui-runtime/manual-apply-evidence/${encodeURIComponent(evidenceId)}/post-manual-readiness-checks" in text
    assert "/comfyui-runtime/post-manual-readiness-checks/${encodeURIComponent(checkId)}/${encodeURIComponent(action)}" in text
    assert "/comfyui-runtime/guarded-probe-executions" in text
    assert "/comfyui-runtime/post-manual-readiness-checks/${encodeURIComponent(checkId)}/guarded-probe-executions" in text
    assert "/comfyui-runtime/guarded-probe-executions/${encodeURIComponent(executionId)}/${encodeURIComponent(action)}" in text
    assert "/comfyui-runtime/guarded-probe-executions/${encodeURIComponent(executionId)}/execute" in text
    assert "/comfyui-runtime/video-resource-plans" in text
    assert "/comfyui-runtime/video-jobs" in text
    assert "/comfyui-runtime/video-jobs/${encodeURIComponent(jobId)}/refresh" in text
    assert "/comfyui-runtime/diagnostic-snapshots" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/plan-draft" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/operation-loop" in text
    assert (
        "/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/next-action/audit-records"
        in text
    )
    assert "productionClosedLoopActionAudits" in text
    assert "/commercial-operations/production-closed-loop/intervention-queue" in text
    assert "productionClosedLoopInterventionQueue" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/intervention-queue/acknowledgements" in text
    assert "createProductionClosedLoopInterventionAcknowledgement" in text
    assert "productionClosedLoopInterventionAcknowledgements" in text
    assert (
        "/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/intervention-queue/reminder-dispatches"
        in text
    )
    assert "createProductionClosedLoopInterventionReminderDispatch" in text
    assert "productionClosedLoopInterventionReminderDispatches" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/agent-skill-orchestration" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/agent-skill-orchestration/refresh" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/complete" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/generate-rag" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/generate-rag" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/prepare" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/prepare" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/preflights" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}/check" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}/validate" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}/job-requests" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/queue" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-job-requests/${encodeURIComponent(jobRequestId)}/execution-plans" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/simulate" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-execution-plans/${encodeURIComponent(executionPlanId)}/connection-probes" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/probe" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-connection-probes/${encodeURIComponent(connectionProbeId)}/adapter-dispatches" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/dispatch" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-dispatches/${encodeURIComponent(adapterDispatchId)}/runtime-gates" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/arm" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/disable" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-gates/${encodeURIComponent(runtimeGateId)}/runtime-dry-runs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/validate" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-dry-runs/${encodeURIComponent(runtimeDryRunId)}/runtime-activations" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}/schedule" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/comfyui-runtime-activations/${encodeURIComponent(runtimeActivationId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/package" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/generate-rag" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/prepare" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/start" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/succeed" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/retry" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/links" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/links/${encodeURIComponent(linkId)}" in text
    assert 'method: "PATCH"' in text
    assert 'method: "DELETE"' in text


def test_admin_dashboard_commercial_operations_styles_are_present() -> None:
    text = STYLES.read_text(encoding="utf-8")

    for selector in (
        ".commercial-command-center",
        ".commercial-flow-grid",
        ".commercial-metrics-grid",
        ".commercial-maintenance-cockpit",
        ".commercial-maintenance-card",
        ".commercial-maintenance-next-card",
        ".commercial-action-result-drawer",
        ".commercial-grid",
        ".commercial-form-grid",
        ".commercial-detail-grid",
        ".commercial-agent-skill-summary",
        ".commercial-action-row",
        ".commercial-approval-grid",
        ".commercial-approval-list",
        ".commercial-approval-item",
        ".commercial-approval-actions",
        ".commercial-dry-run-grid",
        ".commercial-dry-run-list",
        ".commercial-dry-run-item",
        ".commercial-dry-run-actions",
        ".commercial-content-grid",
        ".commercial-content-list",
        ".commercial-content-item",
        ".commercial-content-actions",
        ".commercial-asset-grid",
        ".commercial-asset-list",
        ".commercial-asset-item",
        ".commercial-asset-actions",
        ".commercial-deliverable-grid",
        ".commercial-deliverable-list",
        ".commercial-deliverable-item",
        ".commercial-deliverable-actions",
        ".commercial-evidence-grid",
        ".commercial-evidence-list",
        ".commercial-evidence-item",
        ".commercial-evidence-actions",
        ".commercial-execution-grid",
        ".commercial-execution-list",
        ".commercial-execution-item",
        ".commercial-execution-actions",
        ".commercial-execution-run-grid",
        ".commercial-execution-run-list",
        ".commercial-execution-run-item",
        ".commercial-execution-run-actions",
        ".commercial-result-grid",
        ".commercial-result-list",
        ".commercial-result-item",
        ".commercial-result-actions",
        ".commercial-observation-grid",
        ".commercial-observation-list",
        ".commercial-observation-item",
        ".commercial-observation-actions",
        ".commercial-optimization-grid",
        ".commercial-optimization-list",
        ".commercial-optimization-item",
        ".commercial-optimization-actions",
        ".commercial-delivery-audit-next-action-plan",
        ".commercial-delivery-audit-next-action-list",
        ".commercial-delivery-audit-operator-queue",
        ".commercial-delivery-audit-operator-queue-list",
        ".commercial-delivery-audit-openclaw-provider-handoff",
        ".commercial-delivery-audit-openclaw-provider-handoff-list",
        ".commercial-link-grid",
        ".commercial-link-list",
        ".commercial-link-item",
        ".commercial-link-actions",
    ):
        assert selector in text
