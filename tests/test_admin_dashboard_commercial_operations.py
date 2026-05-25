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
    assert "client execution" in text
    assert 'phase: "61Z"' in text
    assert "Runtime adapter contract" in text
    assert "Phase 62F" in text
    assert 'phase: "62G"' in text
    assert 'phase: "62H"' in text
    assert "read_only_probe_enabled" in text
    assert "read_only_probe_attempted" in text
    assert "readiness_status" in text
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
        ".commercial-link-grid",
        ".commercial-link-list",
        ".commercial-link-item",
        ".commercial-link-actions",
    ):
        assert selector in text
