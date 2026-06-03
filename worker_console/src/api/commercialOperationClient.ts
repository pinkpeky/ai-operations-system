import { conversationClient, defaultConversationSettings, type ConversationSettings } from "./conversationClient";

export type CommercialOperation = {
  id: string;
  title: string;
  objective: string;
  status: string;
  target_audience?: string | null;
  channels?: string[];
  knowledge_collection?: string | null;
  success_metrics?: string[];
  constraints?: string[];
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationLoopStageStatus =
  | "complete"
  | "in_progress"
  | "review_required"
  | "blocked"
  | "missing";

export type CommercialOperationLoopStage = {
  stage_key: string;
  title: string;
  owner: string;
  status: CommercialOperationLoopStageStatus;
  summary: string;
  next_action: string;
  blocked_reasons: string[];
  related_records: Record<string, unknown>[];
  operator_actions: string[];
  server_actions: string[];
  client_actions: string[];
};

export type CommercialOperationLoopSummary = {
  operation_id: string;
  workspace_id: string;
  title: string;
  objective: string;
  loop_status: string;
  current_stage_key: string | null;
  next_action: string;
  completion_ratio: number;
  stages: CommercialOperationLoopStage[];
  counts: Record<string, number>;
  execution_protocol: Record<string, unknown>;
  readiness: Record<string, unknown>[];
  boundaries: string[];
  generated_at: string;
};

export type CommercialOperationAgentSkillStatus =
  | "complete"
  | "active"
  | "needs_review"
  | "blocked"
  | "waiting";

export type CommercialOperationAgentSkill = {
  skill_key: string;
  display_name: string;
  owner_agent: string;
  tool_name?: string | null;
  stage_key: string;
  status: CommercialOperationAgentSkillStatus;
  summary: string;
  next_action: string;
  inputs: string[];
  outputs: string[];
  boundary: string;
};

export type CommercialOperationAgentDecision = {
  decision_key: string;
  agent_name: string;
  skill_key: string;
  decision_type: string;
  status: string;
  rationale: string;
  next_action: string;
  evidence: string[];
};

export type CommercialOperationRoutingDecision = {
  decision_key: string;
  controller_agent: string;
  decision_mode: string;
  confidence: number;
  current_stage: string | null;
  recommended_track: string;
  selected_track_status?: string | null;
  selected_skill_key?: string | null;
  selected_agents: string[];
  required_knowledge_collections: string[];
  required_inputs: string[];
  blocked_by: string[];
  reason_codes: string[];
  quality_gates: string[];
  next_executable_contract: Record<string, unknown>;
  production_intervention_required: boolean;
  production_intervention_recommended_action: Record<string, unknown>;
  production_intervention_queue_summary: Record<string, unknown>;
  production_delivery_plan_required: boolean;
  production_delivery_recommended_gate: Record<string, unknown>;
  production_delivery_plan_summary: Record<string, unknown>;
  rationale: string;
  next_action: string;
  evidence: string[];
};

export type CommercialOperationAgentSkillOrchestration = {
  operation_id: string;
  workspace_id: string;
  controller_agent: Record<string, unknown>;
  orchestration_status: string;
  next_skill_key: string | null;
  next_action: string;
  completion_ratio: number;
  skills: CommercialOperationAgentSkill[];
  routing_decision: CommercialOperationRoutingDecision;
  specialist_tracks: Record<string, unknown>[];
  production_intervention_queue: Record<string, unknown>;
  production_delivery_plan: Record<string, unknown>;
  decisions: CommercialOperationAgentDecision[];
  boundaries: string[];
  generated_at: string;
};

export type CommercialOperationPlanPreview = {
  operation_id: string;
  plan_outline: Record<string, unknown>[];
};

export type CommercialOperationLLMResponse = {
  provider: string;
  model: string;
  content: string;
  usage?: Record<string, number>;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationPlanningIntelligence = {
  status: string;
  generated_at: string;
  queries: string[];
  source_results: Record<string, unknown>[];
  skill_cards: Record<string, unknown>[];
  analysis_report: Record<string, unknown>;
  model_capabilities: Record<string, unknown>;
  viral_video_signals: string[];
  competitor_signals: string[];
  operation_data_signals: string[];
  gaps: string[];
  prompt_context: string;
  boundary: string;
};

export type CommercialOperationLLMResourcePlan = {
  success: boolean;
  provider: string;
  model: string;
  workspace_id?: string | null;
  strategy_enabled: boolean;
  mode: string;
  admission_status: string;
  should_run_now: boolean;
  recommended_gpu_indexes: number[];
  cuda_visible_devices?: string | null;
  max_concurrent_llm_requests: number;
  comfyui_active: boolean;
  comfyui_busy_gpu_indexes: number[];
  available_gpu_indexes: number[];
  ollama_options: Record<string, unknown>;
  runtime_notes: string[];
  recommended_actions: string[];
  blocking_reasons: string[];
  comfyui_resource_plan: Record<string, unknown>;
};

export type CommercialOperationPlanCreatePayload = {
  plan_version?: number;
  title: string;
  objective_summary: string;
  audience_strategy?: string | null;
  channel_strategy?: Record<string, unknown>[];
  content_strategy?: Record<string, unknown>;
  production_scope?: Record<string, unknown>[];
  material_requirements?: Record<string, unknown>[];
  kpis?: Record<string, unknown>[];
  publish_schedule?: Record<string, unknown>[];
  risk_notes?: string | null;
  source_goal?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationPlan = {
  id: string;
  operation_id: string;
  plan_version: number;
  title: string;
  plan_status: string;
  objective_summary: string;
  audience_strategy?: string | null;
  channel_strategy: Record<string, unknown>[];
  content_strategy: Record<string, unknown>;
  production_scope: Record<string, unknown>[];
  material_requirements: Record<string, unknown>[];
  kpis: Record<string, unknown>[];
  publish_schedule: Record<string, unknown>[];
  risk_notes?: string | null;
  source_goal?: string | null;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationProjectMaterial = {
  id: string;
  operation_id: string;
  production_task_id?: string | null;
  material_type: string;
  material_status: string;
  name: string;
  source_uri: string;
  file_name?: string | null;
  mime_type?: string | null;
  size_bytes?: number | null;
  authorization_status: string;
  usage_scope?: string | null;
  tags: string[];
  linked_task_ids: string[];
  notes?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationProductionTask = {
  id: string;
  operation_id: string;
  operation_plan_id?: string | null;
  task_type: "copy" | "image" | "media" | string;
  media_subtype?: string | null;
  channel: string;
  title: string;
  task_status: string;
  brief?: string | null;
  source_material_ids: string[];
  output_requirements: Record<string, unknown>[];
  target_specs: Record<string, unknown>;
  workflow_selection_required: boolean;
  assigned_agent?: string | null;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationWorkflowSelection = {
  id: string;
  operation_id: string;
  production_task_id: string;
  workflow_source: string;
  workflow_name: string;
  workflow_kind?: string | null;
  output_type: string;
  selection_status: string;
  candidate_summary?: string | null;
  input_requirements: Record<string, unknown>[];
  expected_outputs: Record<string, unknown>[];
  recommendation_reason?: string | null;
  estimated_duration_seconds?: number | null;
  estimated_vram_mb?: number | null;
  risk_notes?: string | null;
  validation_status: string;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationWorkflowCandidate = {
  candidate_id: string;
  rank: number;
  score: number;
  workflow_source: string;
  workflow_name: string;
  workflow_kind?: string | null;
  output_type: string;
  category?: string | null;
  capabilities: string[];
  candidate_summary?: string | null;
  input_requirements: Record<string, unknown>[];
  expected_outputs: Record<string, unknown>[];
  recommendation_reason?: string | null;
  estimated_duration_seconds?: number | null;
  estimated_vram_mb?: number | null;
  risk_notes?: string | null;
  validation_status: string;
  runtime_readiness: string;
  workflow_path?: string | null;
  workflow_path_exists: boolean;
  requires_prompt_validation: boolean;
  model_refs_found_count: number;
  model_refs_missing: string[];
  missing_executable_node_types: string[];
  metadata?: Record<string, unknown>;
};

export type CommercialOperationWorkflowCandidateList = {
  operation_id: string;
  production_task_id: string;
  query: string;
  required_capabilities: string[];
  preferred_terms: string[];
  items: CommercialOperationWorkflowCandidate[];
  library_metadata: Record<string, unknown>;
};

export type CommercialOperationOutputCandidate = {
  id: string;
  operation_id: string;
  production_task_id?: string | null;
  workflow_selection_id?: string | null;
  output_artifact_id?: string | null;
  candidate_type: string;
  candidate_status: string;
  title: string;
  preview_uri?: string | null;
  source_uri?: string | null;
  thumbnail_uri?: string | null;
  mime_type?: string | null;
  duration_seconds?: number | null;
  generation_summary?: string | null;
  quality_checks: string[];
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationFinalSelection = {
  id: string;
  operation_id: string;
  production_task_id?: string | null;
  output_candidate_id: string;
  final_type: string;
  title: string;
  selection_status: string;
  selection_reason?: string | null;
  platform_targets: string[];
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationOutputPrepPackage = {
  operation_id: string;
  production_task_id: string;
  readiness_status: string;
  blocking_reasons: string[];
  task_status: string;
  workflow_selection_required: boolean;
  approved_workflow_selection_id?: string | null;
  task_summary: Record<string, unknown>;
  candidate_blueprint: Record<string, unknown>;
  required_inputs: Record<string, unknown>[];
  expected_outputs: Record<string, unknown>[];
  review_gates: string[];
  available_output_candidates: CommercialOperationOutputCandidate[];
  existing_final_selections: CommercialOperationFinalSelection[];
  output_storage_policy: Record<string, unknown>;
  metadata: Record<string, unknown>;
};

export type CommercialOperationPublishPackage = {
  id: string;
  operation_id: string;
  final_selection_id?: string | null;
  platform: string;
  account_ref?: string | null;
  title: string;
  body: string;
  package_status: string;
  hashtags: string[];
  cover_candidate_id?: string | null;
  scheduled_at?: string | null;
  publish_payload: Record<string, unknown>;
  risk_notes?: string | null;
  reviewer_notes?: string | null;
  approved_at?: string | null;
  prepared_at?: string | null;
  published_at?: string | null;
  failure_reason?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationPublishPrepPackage = {
  operation_id: string;
  final_selection_id: string;
  readiness_status: string;
  blocking_reasons: string[];
  final_selection_status: string;
  platform_targets: string[];
  final_selection: CommercialOperationFinalSelection;
  selected_output_candidate?: CommercialOperationOutputCandidate | null;
  package_blueprints: Record<string, unknown>[];
  copy_guidance: Record<string, unknown>;
  review_gates: string[];
  existing_publish_packages: CommercialOperationPublishPackage[];
  platform_policy: Record<string, unknown>;
  metadata: Record<string, unknown>;
};

export type CommercialOperationPlatformMetricSnapshot = {
  id: string;
  operation_id: string;
  publish_package_id?: string | null;
  platform: string;
  platform_content_id?: string | null;
  source_type: string;
  snapshot_status: string;
  collected_at?: string | null;
  metric_date?: string | null;
  metrics: Record<string, unknown>;
  summary?: string | null;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationPublishExecutionHandoff = {
  operation_id: string;
  publish_package_id: string;
  readiness_status: string;
  blocking_reasons: string[];
  package_status: string;
  platform: string;
  execution_target?: string | null;
  publish_package: CommercialOperationPublishPackage;
  final_selection?: CommercialOperationFinalSelection | null;
  selected_output_candidate?: CommercialOperationOutputCandidate | null;
  execution_status: Record<string, unknown>;
  client_execution_payload: Record<string, unknown>;
  execution_runbook: Record<string, unknown>[];
  account_confirmation: Record<string, unknown>;
  dry_run_plan: Record<string, unknown>;
  expected_evidence: Record<string, unknown>[];
  metric_pullback_plan: Record<string, unknown>;
  review_gates: string[];
  existing_metric_snapshots: CommercialOperationPlatformMetricSnapshot[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationPublishExecutionStatusValue = "queued" | "running" | "needs_operator" | "succeeded" | "failed" | "cancelled";

export type CommercialOperationPublishExecutionStatus = {
  operation_id: string;
  publish_package_id: string;
  attempt_id: string;
  execution_status: CommercialOperationPublishExecutionStatusValue;
  package_status: string;
  customer_machine_id: string;
  progress?: number | null;
  failure_reason?: string | null;
  publish_package: CommercialOperationPublishPackage;
  latest_attempt: Record<string, unknown>;
  execution_history: Record<string, unknown>[];
  retry_policy: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationPublishExecutionResult = {
  operation_id: string;
  publish_package_id: string;
  result_status: string;
  publish_succeeded: boolean;
  platform: string;
  platform_content_id?: string | null;
  published_url?: string | null;
  publish_package: CommercialOperationPublishPackage;
  created_metric_snapshot?: CommercialOperationPlatformMetricSnapshot | null;
  execution_result: Record<string, unknown>;
  evidence_links: Record<string, unknown>[];
  dry_run_evidence: Record<string, unknown>[];
  execution_log: Record<string, unknown>[];
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricAnalysisSchedule = {
  operation_id: string;
  schedule_status: string;
  enabled: boolean;
  cadence: string;
  local_time: string;
  timezone: string;
  next_run_at?: string | null;
  last_run_at?: string | null;
  lookback_hours: number;
  platform_scope: string[];
  metric_requirements: string[];
  published_package_count: number;
  latest_metric_snapshot?: CommercialOperationPlatformMetricSnapshot | null;
  analysis_contract: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricAnalysisRun = {
  operation_id: string;
  run_status: string;
  forced: boolean;
  due: boolean;
  schedule_status_before: string;
  schedule_status_after: string;
  schedule: CommercialOperationMetricAnalysisSchedule;
  eligible_publish_packages: CommercialOperationPublishPackage[];
  created_metric_snapshots: CommercialOperationPlatformMetricSnapshot[];
  usable_metric_snapshots: CommercialOperationPlatformMetricSnapshot[];
  analysis_package: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricPullbackHandoff = {
  operation_id: string;
  handoff_status: string;
  due: boolean;
  forced: boolean;
  schedule: CommercialOperationMetricAnalysisSchedule;
  published_packages: CommercialOperationPublishPackage[];
  pullback_tasks: Record<string, unknown>[];
  target_metric_keys: string[];
  evidence_requirements: Record<string, unknown>[];
  client_adapter_plan: Record<string, unknown>;
  analysis_run_request_template: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricPullbackSubmission = {
  operation_id: string;
  submission_status: string;
  forced: boolean;
  adapter_mode: string;
  adapter_run_id?: string | null;
  handoff: CommercialOperationMetricPullbackHandoff;
  submitted_metric_count: number;
  accepted_metric_count: number;
  rejected_metric_count: number;
  accepted_metrics: Record<string, unknown>[];
  rejected_metrics: Record<string, unknown>[];
  metric_analysis_run?: CommercialOperationMetricAnalysisRun | null;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricPullbackAdapterProfile = {
  operation_id: string;
  adapter_profile_id: string;
  platform: string;
  profile_status: string;
  due: boolean;
  forced: boolean;
  handoff: CommercialOperationMetricPullbackHandoff;
  supported_input_modes: string[];
  target_metric_keys: string[];
  field_aliases: Record<string, string[]>;
  normalization_rules: Record<string, unknown>[];
  evidence_requirements: Record<string, unknown>[];
  runbook: Record<string, unknown>[];
  browser_assist_plan: Record<string, unknown>;
  export_import_contract: Record<string, unknown>;
  submission_template: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricPullbackExportImportPreview = {
  operation_id: string;
  platform: string;
  preview_status: string;
  forced: boolean;
  operator_confirmed: boolean;
  adapter_profile: CommercialOperationMetricPullbackAdapterProfile;
  parsed_row_count: number;
  accepted_metric_count: number;
  rejected_row_count: number;
  accepted_metrics: Record<string, unknown>[];
  rejected_rows: Record<string, unknown>[];
  submission_payload: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricPullbackBrowserAssistSession = {
  operation_id: string;
  platform: string;
  browser_assist_session_id: string;
  session_status: string;
  forced: boolean;
  operator_confirmed: boolean;
  adapter_profile: CommercialOperationMetricPullbackAdapterProfile;
  target_task_count: number;
  target_tasks: Record<string, unknown>[];
  navigation_targets: Record<string, unknown>[];
  extraction_fields: Record<string, unknown>[];
  evidence_plan: Record<string, unknown>[];
  allowed_domain_suffixes: string[];
  forbidden_actions: string[];
  operator_checklist: Record<string, unknown>[];
  submission_template: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricAnalysisDispatchQueueItem = {
  operation_id: string;
  operation_title: string;
  dispatch_status: string;
  due: boolean;
  forced: boolean;
  platform: string;
  pullback_task_count: number;
  target_metric_keys: string[];
  available_collection_modes: string[];
  recommended_customer_action: string;
  customer_machine_actions: Record<string, unknown>[];
  handoff: CommercialOperationMetricPullbackHandoff;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricAnalysisDispatchQueue = {
  workspace_id: string;
  dispatch_status: string;
  forced: boolean;
  platform?: string | null;
  scanned_operation_count: number;
  due_count: number;
  ready_dispatch_count: number;
  blocked_count: number;
  idle_count: number;
  items: CommercialOperationMetricAnalysisDispatchQueueItem[];
  scheduler_poll_contract: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricDispatchClaim = {
  workspace_id: string;
  claim_id?: string | null;
  claim_status: string;
  operation_id?: string | null;
  platform?: string | null;
  collection_mode?: string | null;
  customer_machine_id?: string | null;
  forced: boolean;
  operator_confirmed: boolean;
  lease_expires_at?: string | null;
  dispatch_item?: Record<string, unknown> | null;
  claim_record: Record<string, unknown>;
  dispatch_queue?: CommercialOperationMetricAnalysisDispatchQueue | null;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricDispatchClaimList = {
  workspace_id: string;
  claim_status?: string | null;
  items: Record<string, unknown>[];
  active_count: number;
  expired_count: number;
  completed_count: number;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricDispatchCustomerPoll = {
  workspace_id: string;
  poll_status: string;
  customer_machine_id: string;
  auto_claimed: boolean;
  poll_interval_seconds: number;
  dispatch_queue: CommercialOperationMetricAnalysisDispatchQueue;
  claim_result?: CommercialOperationMetricDispatchClaim | null;
  claim_list: CommercialOperationMetricDispatchClaimList;
  assigned_claims: Record<string, unknown>[];
  expired_claims: Record<string, unknown>[];
  redispatch_candidates: Record<string, unknown>[];
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationMetricDispatchPollScheduler = {
  workspace_id: string;
  scheduler_status: string;
  scheduler_enabled: boolean;
  customer_machine_id: string;
  platform?: string | null;
  auto_claim: boolean;
  operator_confirmed: boolean;
  recommended_poll_interval_seconds: number;
  next_poll_at?: string | null;
  poll_result?: CommercialOperationMetricDispatchCustomerPoll | null;
  notification_events: Record<string, unknown>[];
  scheduler_policy: Record<string, unknown>;
  client_timer_payload: Record<string, unknown>;
  review_gates: string[];
  next_actions: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopStage = {
  stage_key: string;
  title: string;
  status: string;
  required: boolean;
  count: number;
  complete_count: number;
  blocking_reasons: string[];
  next_action: string;
  primary_record?: Record<string, unknown> | null;
  evidence: string[];
};

export type CommercialOperationProductionClosedLoopReadiness = {
  operation_id: string;
  workspace_id: string;
  readiness_status: string;
  completion_ratio: number;
  current_stage_key?: string | null;
  next_action: string;
  ready_for_customer_machine_execution: boolean;
  ready_for_metric_feedback: boolean;
  ready_for_next_cycle: boolean;
  operation_loop_status: string;
  operation_loop_current_stage_key?: string | null;
  stages: CommercialOperationProductionClosedLoopStage[];
  counts: Record<string, number>;
  latest_records: Record<string, Record<string, unknown> | null>;
  metric_schedule: CommercialOperationMetricAnalysisSchedule;
  metric_dispatch?: CommercialOperationMetricAnalysisDispatchQueue | null;
  metric_claims?: CommercialOperationMetricDispatchClaimList | null;
  acceptance_gates: string[];
  operator_next_actions: string[];
  server_next_actions: string[];
  client_next_actions: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopAcceptanceOperation = {
  operation_id: string;
  title: string;
  status: string;
  readiness_status: string;
  completion_ratio: number;
  current_stage_key?: string | null;
  next_action: string;
  ready_for_customer_machine_execution: boolean;
  ready_for_metric_feedback: boolean;
  ready_for_next_cycle: boolean;
  staleness_status: string;
  waiting_seconds: number;
  escalation_recommended: boolean;
  blocking_reasons: string[];
  operator_next_actions: string[];
};

export type CommercialOperationProductionClosedLoopAcceptanceSummary = {
  workspace_id: string;
  acceptance_status: string;
  operation_count: number;
  accepted_count: number;
  ready_for_customer_machine_execution_count: number;
  ready_for_metric_feedback_count: number;
  ready_for_next_cycle_count: number;
  blocked_count: number;
  intervention_queue_count: number;
  completion_percent: number;
  completion_level: string;
  score_breakdown: Record<string, number>;
  remaining_gates: string[];
  next_focus: string;
  readiness_status_counts: Record<string, number>;
  current_stage_counts: Record<string, number>;
  staleness_status_counts: Record<string, number>;
  operations: CommercialOperationProductionClosedLoopAcceptanceOperation[];
  top_blockers: CommercialOperationProductionClosedLoopAcceptanceOperation[];
  openclaw_provider_readiness: Record<string, unknown>;
  release_ready: boolean;
  release_gate_ready_count: number;
  release_gate_total_count: number;
  release_gate_status_counts: Record<string, number>;
  release_gate_checklist: Array<Record<string, unknown>>;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryPlanGate = {
  gate_key: string;
  gate_status: string;
  title: string;
  owner: string;
  priority: number;
  completion_impact: number;
  required: boolean;
  source: string;
  blocking_reasons: string[];
  operator_next_actions: string[];
  server_next_actions: string[];
  client_next_actions: string[];
  evidence_requirements: string[];
  related_operation_ids: string[];
  action_method?: string | null;
  action_endpoint?: string | null;
  external_execution_allowed: boolean;
};

export type CommercialOperationProductionClosedLoopDeliveryPlan = {
  workspace_id: string;
  delivery_status: string;
  acceptance_status: string;
  completion_percent: number;
  completion_level: string;
  next_focus: string;
  ready_for_handoff: boolean;
  gate_count: number;
  open_gate_count: number;
  critical_gate_count: number;
  gate_plan: CommercialOperationProductionClosedLoopDeliveryPlanGate[];
  immediate_actions: CommercialOperationProductionClosedLoopDeliveryPlanGate[];
  score_breakdown: Record<string, number>;
  openclaw_provider_readiness: Record<string, unknown>;
  acceptance_summary: Record<string, unknown>;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearanceItem = {
  blocker_key: string;
  source: string;
  severity: string;
  title: string;
  message: string;
  operation_id?: string | null;
  operation_title?: string | null;
  gate_key?: string | null;
  remediation_key?: string | null;
  target_console: string;
  target_endpoint?: string | null;
  owner: string;
  priority: number;
  current_state: string;
  coverage_status?: string | null;
  prep_status?: string | null;
  latest_work_order_id?: string | null;
  latest_work_order_status?: string | null;
  latest_readiness_refresh_status?: string | null;
  recommended_action: string;
  expected?: string | null;
  actual?: string | null;
  can_be_resolved_by_ui: boolean;
  external_dependency_required: boolean;
  operator_approval_required: boolean;
  runbook_references: string[];
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan = {
  workspace_id: string;
  clearance_status: string;
  production_config_ready: boolean;
  acceptance_summary_ready: boolean;
  blocker_count: number;
  external_dependency_count: number;
  ui_clearable_count: number;
  work_ordered_count: number;
  ready_for_execution_count: number;
  readiness_refreshed_count: number;
  next_focus: string;
  items: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearanceItem[];
  production_config_findings: Record<string, unknown>[];
  acceptance_summary: Record<string, unknown>;
  remediation_map: CommercialOperationProductionClosedLoopDeliveryRemediationMap;
  work_order_coverage: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage;
  execution_prep: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryActionStep = {
  action_key: string;
  gate_key: string;
  operation_id?: string | null;
  target_console: string;
  action_status: string;
  title: string;
  owner: string;
  method?: string | null;
  endpoint?: string | null;
  requires_operator_confirmation: boolean;
  external_execution_allowed: boolean;
  server_side_external_execution: boolean;
  blocked_by: string[];
  evidence_requirements: string[];
  operator_next_actions: string[];
  server_next_actions: string[];
  client_next_actions: string[];
  payload_template: Record<string, unknown>;
  guardrails: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryActionPackage = {
  gate_key: string;
  gate_status: string;
  title: string;
  owner: string;
  priority: number;
  target_console: string;
  action_status: string;
  action_count: number;
  related_operation_ids: string[];
  blocking_reasons: string[];
  recommended_action_key?: string | null;
  action_steps: CommercialOperationProductionClosedLoopDeliveryActionStep[];
  external_execution_allowed: boolean;
};

export type CommercialOperationProductionClosedLoopDeliveryActionPackages = {
  workspace_id: string;
  action_package_status: string;
  delivery_status: string;
  acceptance_status: string;
  completion_percent: number;
  next_focus: string;
  package_count: number;
  step_count: number;
  immediate_package_count: number;
  gate_packages: CommercialOperationProductionClosedLoopDeliveryActionPackage[];
  immediate_action_packages: CommercialOperationProductionClosedLoopDeliveryActionPackage[];
  delivery_plan: Record<string, unknown>;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediation = {
  remediation_key: string;
  gate_key: string;
  gate_status: string;
  title: string;
  owner: string;
  priority: number;
  target_console: string;
  action_status: string;
  related_operation_ids: string[];
  blocking_reasons: string[];
  recommended_sequence: string[];
  primary_method?: string | null;
  primary_endpoint?: string | null;
  secondary_endpoints: Record<string, unknown>[];
  expected_evidence: string[];
  existing_records_needed: string[];
  completion_gate: string;
  current_evidence_status: string;
  latest_evidence_record_id?: string | null;
  latest_evidence_summary?: string | null;
  source_action_key?: string | null;
  requires_operator_confirmation: boolean;
  can_be_started_from_server: boolean;
  can_be_started_from_customer_machine: boolean;
  automation_allowed: boolean;
  external_execution_allowed: boolean;
  runbook_references: string[];
  handoff_notes: string[];
  guardrails: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationMap = {
  workspace_id: string;
  remediation_status: string;
  delivery_status: string;
  acceptance_status: string;
  completion_percent: number;
  next_focus: string;
  remediation_count: number;
  immediate_remediation_count: number;
  remediations: CommercialOperationProductionClosedLoopDeliveryRemediation[];
  immediate_remediations: CommercialOperationProductionClosedLoopDeliveryRemediation[];
  action_packages: Record<string, unknown>;
  evidence_records: Record<string, unknown>;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord = {
  work_order_id: string;
  workspace_id: string;
  operation_id: string;
  remediation_key: string;
  gate_key: string;
  work_order_status: string;
  assignee?: string | null;
  operator_confirmed: boolean;
  target_console: string;
  primary_endpoint?: string | null;
  completion_gate: string;
  evidence_links: Record<string, unknown>[];
  work_summary?: string | null;
  operator_notes?: string | null;
  contract_snapshot: Record<string, unknown>;
  boundary_checks: string[];
  created_by?: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderList = {
  workspace_id: string;
  work_order_count: number;
  latest_record?: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord | null;
  records: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord[];
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRequest = {
  remediation_key?: string | null;
  gate_key?: string | null;
  operation_id?: string | null;
  work_order_status: string;
  assignee?: string | null;
  operator_confirmed: boolean;
  evidence_links?: Record<string, unknown>[];
  work_summary?: string | null;
  operator_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItem = {
  remediation_key: string;
  gate_key: string;
  gate_status: string;
  title: string;
  owner: string;
  priority: number;
  target_console: string;
  coverage_status: string;
  work_order_required: boolean;
  work_order_count: number;
  latest_work_order_id?: string | null;
  latest_work_order_status?: string | null;
  latest_work_order_assignee?: string | null;
  latest_work_order_operator_confirmed: boolean;
  latest_work_order_created_at?: string | null;
  latest_readiness_refresh_id?: string | null;
  latest_readiness_refresh_status?: string | null;
  latest_readiness_refresh_next_action?: string | null;
  current_evidence_status: string;
  completion_gate: string;
  next_action: string;
  blocking_reasons: string[];
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage = {
  workspace_id: string;
  coverage_status: string;
  remediation_status: string;
  completion_percent: number;
  coverage_percent: number;
  remediation_count: number;
  work_ordered_count: number;
  unassigned_count: number;
  in_progress_count: number;
  completed_count: number;
  readiness_refreshed_count: number;
  blocked_count: number;
  next_focus: string;
  items: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItem[];
  unassigned_items: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItem[];
  in_progress_items: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItem[];
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest = {
  assignee: string;
  operator_confirmed: boolean;
  platform?: string | null;
  force_metric_due?: boolean;
  limit?: number;
  scan_limit?: number;
  work_summary?: string | null;
  operator_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignment = {
  workspace_id: string;
  assignment_status: string;
  requested_count: number;
  created_count: number;
  skipped_count: number;
  assignee: string;
  records: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord[];
  coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentRequest = {
  assignee: string;
  operator_confirmed: boolean;
  platform?: string | null;
  force_metric_due?: boolean;
  limit?: number;
  scan_limit?: number;
  work_order_limit?: number;
  include_external_dependencies?: boolean;
  work_summary?: string | null;
  operator_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentSkippedItem = {
  blocker_key?: string | null;
  source?: string | null;
  gate_key?: string | null;
  remediation_key?: string | null;
  reason: string;
  external_dependency_required: boolean;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignment = {
  workspace_id: string;
  assignment_status: string;
  blocker_count: number;
  assignable_blocker_count: number;
  requested_gate_count: number;
  created_count: number;
  skipped_count: number;
  assignee: string;
  include_external_dependencies: boolean;
  assigned_gate_keys: string[];
  failed_gate_keys: string[];
  skipped_items: CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentSkippedItem[];
  records: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord[];
  clearance_plan_before: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan;
  clearance_plan_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan;
  coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage;
  execution_prep_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackage = {
  package_key: string;
  title: string;
  blocker_keys: string[];
  sources: string[];
  severity: string;
  gate_key?: string | null;
  remediation_key?: string | null;
  target_console: string;
  target_endpoint?: string | null;
  owner: string;
  priority: number;
  external_dependency_required: boolean;
  can_be_resolved_by_ui: boolean;
  operator_approval_required: boolean;
  current_state: string;
  coverage_status?: string | null;
  prep_status?: string | null;
  latest_work_order_id?: string | null;
  latest_work_order_status?: string | null;
  recommended_actions: string[];
  required_inputs: string[];
  manual_steps: string[];
  verification_commands: string[];
  evidence_requirements: string[];
  runbook_references: string[];
  handoff_notes: string[];
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackages = {
  workspace_id: string;
  handoff_status: string;
  package_count: number;
  external_dependency_package_count: number;
  work_ordered_package_count: number;
  next_focus: string;
  packages: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackage[];
  clearance_plan: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecord = {
  evidence_record_id: string;
  workspace_id: string;
  operation_id: string;
  package_key: string;
  gate_key?: string | null;
  remediation_key?: string | null;
  evidence_status: string;
  operator_confirmed: boolean;
  target_console: string;
  current_state: string;
  latest_work_order_id?: string | null;
  latest_work_order_status?: string | null;
  external_dependency_required: boolean;
  evidence_links: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_notes?: string | null;
  verification_commands: string[];
  required_inputs: string[];
  evidence_requirements: string[];
  runbook_references: string[];
  contract_snapshot: Record<string, unknown>;
  boundary_checks: string[];
  created_by?: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceList = {
  workspace_id: string;
  record_count: number;
  latest_record?: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecord | null;
  records: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecord[];
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRequest = {
  package_key?: string | null;
  gate_key?: string | null;
  operation_id?: string | null;
  evidence_status: string;
  operator_confirmed: boolean;
  evidence_links?: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_notes?: string | null;
  platform?: string | null;
  force_metric_due?: boolean;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItem = {
  package_key: string;
  title?: string | null;
  gate_key?: string | null;
  remediation_key?: string | null;
  target_console?: string | null;
  owner?: string | null;
  priority: number;
  external_dependency_required: boolean;
  latest_work_order_id?: string | null;
  latest_work_order_status?: string | null;
  evidence_record_count: number;
  latest_evidence_record_id?: string | null;
  latest_evidence_status?: string | null;
  latest_evidence_summary?: string | null;
  latest_evidence_created_at?: string | null;
  latest_evidence_operator_confirmed: boolean;
  coverage_status: string;
  next_action: string;
  verification_commands: string[];
  evidence_requirements: string[];
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage = {
  workspace_id: string;
  coverage_status: string;
  coverage_percent: number;
  package_count: number;
  evidenced_count: number;
  missing_evidence_count: number;
  resolved_count: number;
  blocked_count: number;
  needs_follow_up_count: number;
  dismissed_count: number;
  next_focus: string;
  items: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItem[];
  missing_items: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItem[];
  blocked_items: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItem[];
  runbook_packages: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackages;
  evidence_records: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceList;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRequest = {
  operation_id?: string | null;
  platform?: string | null;
  force_metric_due?: boolean;
  operator_confirmed: boolean;
  refresh_notes?: string | null;
  limit?: number;
  scan_limit?: number;
  work_order_limit?: number;
  evidence_limit?: number;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRecord = {
  refresh_id: string;
  workspace_id: string;
  operation_id: string;
  refresh_status: string;
  coverage_status: string;
  coverage_percent: number;
  package_count: number;
  resolved_count: number;
  missing_evidence_count: number;
  blocked_count: number;
  needs_follow_up_count: number;
  dismissed_count: number;
  readiness_status: string;
  current_stage_key?: string | null;
  current_stage_status?: string | null;
  next_action_key: string;
  operator_confirmed: boolean;
  refresh_notes?: string | null;
  refreshed_by?: string | null;
  refreshed_at: string;
  metadata: Record<string, unknown>;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefresh = {
  workspace_id: string;
  operation_id: string;
  refresh_id: string;
  refresh_status: string;
  coverage_status: string;
  coverage_percent: number;
  package_count: number;
  resolved_count: number;
  next_focus: string;
  coverage_before: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage;
  coverage_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage;
  acceptance_summary_after: CommercialOperationProductionClosedLoopAcceptanceSummary;
  clearance_plan_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan;
  runbook_packages_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackages;
  readiness: Record<string, unknown>;
  next_action: Record<string, unknown>;
  refresh_record: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRecord;
  operator_confirmed: boolean;
  refresh_notes?: string | null;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanAction = {
  action_key: string;
  title: string;
  owner: string;
  priority: number;
  source_blockers: string[];
  target: string;
  target_console?: string | null;
  required_endpoint?: string | null;
  verification_commands: string[];
  evidence_requirements: string[];
  external_dependency_required: boolean;
  can_be_resolved_by_ui: boolean;
  operator_approval_required: boolean;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlan = {
  workspace_id: string;
  audit_status: string;
  acceptance_status: string;
  completion_percent: number;
  next_focus: string;
  blocker_count: number;
  next_action_count: number;
  runbook_evidence_coverage_ready: boolean;
  runbook_evidence_readiness_refresh_required: boolean;
  blocking_reasons: string[];
  next_actions: CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanAction[];
  first_action?: CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanAction | null;
  acceptance_summary: CommercialOperationProductionClosedLoopAcceptanceSummary;
  clearance_plan: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan;
  runbook_evidence_coverage: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItem = {
  queue_key: string;
  action_key: string;
  title: string;
  owner: string;
  priority: number;
  resolution_mode: string;
  resolution_status: string;
  primary_console: string;
  primary_label: string;
  ui_anchor?: string | null;
  endpoint_method?: string | null;
  endpoint_path?: string | null;
  operator_next_step: string;
  source_blockers: string[];
  evidence_requirements: string[];
  verification_commands: string[];
  external_dependency_required: boolean;
  can_be_resolved_by_ui: boolean;
  operator_approval_required: boolean;
  blocked_by_external_dependency: boolean;
  record_count: number;
  latest_record_id?: string | null;
  latest_record_status?: string | null;
  latest_record_summary?: string | null;
  latest_record_created_at?: string | null;
  latest_record_operator_confirmed: boolean;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueGroup = {
  owner: string;
  owner_label: string;
  queue_status: string;
  top_priority: number;
  action_count: number;
  ui_resolvable_count: number;
  external_dependency_count: number;
  items: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItem[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueue = {
  workspace_id: string;
  queue_status: string;
  audit_status: string;
  acceptance_status: string;
  completion_percent: number;
  owner_count: number;
  action_count: number;
  ui_resolvable_count: number;
  external_dependency_count: number;
  next_owner?: string | null;
  first_item?: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItem | null;
  owner_groups: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueGroup[];
  source_plan: CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlan;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordRequest = {
  queue_key?: string | null;
  action_key: string;
  owner?: string | null;
  operation_id?: string | null;
  record_status?: "queued" | "in_progress" | "blocked" | "resolved" | "needs_follow_up" | "dismissed";
  operator_confirmed?: boolean;
  evidence_links?: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_notes?: string | null;
  platform?: string | null;
  force_metric_due?: boolean;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecord = {
  record_id: string;
  workspace_id: string;
  operation_id: string;
  queue_key: string;
  action_key: string;
  owner: string;
  record_status: string;
  operator_confirmed: boolean;
  resolution_mode: string;
  resolution_status: string;
  primary_console: string;
  primary_label: string;
  endpoint_method?: string | null;
  endpoint_path?: string | null;
  blocked_by_external_dependency: boolean;
  evidence_links: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_notes?: string | null;
  verification_commands: string[];
  evidence_requirements: string[];
  contract_snapshot: Record<string, unknown>;
  boundary_checks: string[];
  created_by?: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordList = {
  workspace_id: string;
  record_count: number;
  latest_record?: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecord | null;
  records: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecord[];
  status_counts: Record<string, number>;
  operator_confirmed_count: number;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffConfigItem = {
  config_key: string;
  required_state: string;
  current_state: string;
  configured: boolean;
  secret: boolean;
  blocking: boolean;
  operator_action: string;
  evidence_requirement: string;
  verification_command?: string | null;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoff = {
  workspace_id: string;
  handoff_status: string;
  readiness_status: string;
  ready: boolean;
  provider: string;
  mock: boolean;
  worker_id?: string | null;
  worker_name?: string | null;
  required_config_count: number;
  missing_config_count: number;
  verification_count: number;
  next_focus: string;
  config_items: CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffConfigItem[];
  verification_commands: string[];
  manual_steps: string[];
  evidence_requirements: string[];
  restart_boundaries: string[];
  provider_readiness: Record<string, unknown>;
  production_config_findings: Record<string, unknown>[];
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItem = {
  prep_key: string;
  remediation_key: string;
  gate_key: string;
  gate_status: string;
  title: string;
  owner: string;
  priority: number;
  operation_id?: string | null;
  prep_status: string;
  coverage_status: string;
  work_order_required: boolean;
  work_order_count: number;
  latest_work_order_id?: string | null;
  latest_work_order_status?: string | null;
  latest_work_order_assignee?: string | null;
  latest_work_order_operator_confirmed: boolean;
  latest_work_order?: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord | null;
  latest_readiness_refresh_id?: string | null;
  latest_readiness_refresh_status?: string | null;
  latest_readiness_refresh_next_action?: string | null;
  target_console: string;
  target_method: string;
  target_endpoint?: string | null;
  completion_gate: string;
  source_action_key?: string | null;
  current_evidence_status: string;
  requires_customer_machine: boolean;
  requires_server_operator: boolean;
  operator_approval_required: boolean;
  operator_confirmed: boolean;
  external_execution_allowed: boolean;
  server_side_external_execution: boolean;
  evidence_requirements: string[];
  prerequisites: string[];
  operator_checklist: string[];
  execution_payload_template: Record<string, unknown>;
  runbook_references: string[];
  guardrails: string[];
  blocking_reasons: string[];
  next_action: string;
  boundary_checks: string[];
  boundaries: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep = {
  workspace_id: string;
  prep_status: string;
  coverage_status: string;
  remediation_status: string;
  completion_percent: number;
  coverage_percent: number;
  remediation_count: number;
  prep_count: number;
  ready_count: number;
  waiting_assignment_count: number;
  blocked_count: number;
  completed_count: number;
  readiness_refreshed_count: number;
  customer_machine_count: number;
  server_operator_count: number;
  next_focus: string;
  items: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItem[];
  ready_items: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItem[];
  waiting_assignment_items: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItem[];
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionRequest = {
  work_order_id?: string | null;
  remediation_key?: string | null;
  gate_key?: string | null;
  operation_id?: string | null;
  completed_by?: string | null;
  operator_confirmed: boolean;
  evidence_links?: Record<string, unknown>[];
  completion_summary?: string | null;
  operator_notes?: string | null;
  platform?: string | null;
  force_metric_due?: boolean;
  limit?: number;
  scan_limit?: number;
  work_order_limit?: number;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletion = {
  workspace_id: string;
  completion_status: string;
  completed_record: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord;
  coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage;
  execution_prep_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep;
  readiness_refresh_required: boolean;
  readiness_refresh_next_action: string;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest = {
  operation_id?: string | null;
  remediation_key?: string | null;
  gate_key?: string | null;
  platform?: string | null;
  force_metric_due?: boolean;
  operator_confirmed: boolean;
  refresh_notes?: string | null;
  limit?: number;
  scan_limit?: number;
  work_order_limit?: number;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRecord = {
  refresh_id: string;
  workspace_id: string;
  operation_id: string;
  remediation_key?: string | null;
  gate_key?: string | null;
  completed_work_order_ids: string[];
  remediation_keys: string[];
  gate_keys: string[];
  refresh_status: string;
  readiness_status: string;
  current_stage_key?: string | null;
  current_stage_status?: string | null;
  next_action_key: string;
  operator_confirmed: boolean;
  refresh_notes?: string | null;
  refreshed_by?: string | null;
  refreshed_at: string;
  metadata: Record<string, unknown>;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefresh = {
  workspace_id: string;
  operation_id: string;
  refresh_id: string;
  refresh_status: string;
  coverage_status: string;
  execution_prep_status: string;
  readiness_status: string;
  current_stage_key?: string | null;
  current_stage_status?: string | null;
  next_action_key: string;
  completed_work_order_count: number;
  readiness_refreshed_count: number;
  completed_items: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItem[];
  coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage;
  execution_prep_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep;
  readiness: CommercialOperationProductionClosedLoopReadiness;
  next_action: CommercialOperationProductionClosedLoopNextAction;
  refresh_record: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRecord;
  readiness_refresh_required: boolean;
  operator_confirmed: boolean;
  refresh_notes?: string | null;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecord = {
  evidence_record_id: string;
  workspace_id: string;
  operation_id: string;
  gate_key: string;
  action_key: string;
  evidence_status: string;
  operator_confirmed: boolean;
  target_console: string;
  action_status: string;
  evidence_links: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_notes?: string | null;
  contract_snapshot: Record<string, unknown>;
  boundary_checks: string[];
  created_by?: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
  boundaries: string[];
};

export type CommercialOperationProductionClosedLoopDeliveryActionEvidenceList = {
  workspace_id: string;
  record_count: number;
  latest_record?: CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecord | null;
  records: CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecord[];
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopDeliveryActionEvidenceRequest = {
  gate_key: string;
  action_key?: string | null;
  operation_id?: string | null;
  evidence_status: string;
  operator_confirmed: boolean;
  evidence_links?: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopAction = {
  action_key: string;
  stage_key: string;
  title: string;
  description: string;
  action_type: string;
  enabled: boolean;
  requires_operator_approval: boolean;
  method?: string | null;
  endpoint?: string | null;
  target_record_id?: string | null;
  payload_template: Record<string, unknown>;
  evidence_requirements: string[];
  review_gates: string[];
  blocking_reasons: string[];
  expected_result: Record<string, unknown>;
  boundary: string;
};

export type CommercialOperationProductionClosedLoopNextAction = {
  operation_id: string;
  workspace_id: string;
  readiness_status: string;
  current_stage_key?: string | null;
  selected_action_key: string;
  selected_action: CommercialOperationProductionClosedLoopAction;
  action_queue: CommercialOperationProductionClosedLoopAction[];
  operator_checklist: string[];
  server_handoff: Record<string, unknown>;
  client_handoff: Record<string, unknown>;
  acceptance_gates: string[];
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionAuditStatus =
  | "reviewed"
  | "confirmed"
  | "submitted"
  | "evidence_returned"
  | "blocked"
  | "cancelled"
  | "failed";

export type CommercialOperationProductionClosedLoopActionAuditRequest = {
  action_key: string;
  stage_key?: string | null;
  action_status?: CommercialOperationProductionClosedLoopActionAuditStatus;
  operator_confirmed?: boolean;
  target_method?: string | null;
  target_endpoint?: string | null;
  target_record_id?: string | null;
  submitted_payload?: Record<string, unknown>;
  evidence_links?: Record<string, unknown>[];
  evidence_summary?: string | null;
  execution_summary?: string | null;
  boundary_checks?: string[];
  client_machine_id?: string | null;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionAuditRecord = {
  audit_id: string;
  operation_id: string;
  workspace_id: string;
  action_key: string;
  stage_key?: string | null;
  action_status: string;
  validation_status: string;
  blocking_reasons: string[];
  operator_confirmed: boolean;
  target_method?: string | null;
  target_endpoint?: string | null;
  target_record_id?: string | null;
  submitted_payload: Record<string, unknown>;
  evidence_links: Record<string, unknown>[];
  evidence_summary?: string | null;
  execution_summary?: string | null;
  boundary_checks: string[];
  client_machine_id?: string | null;
  reviewer_notes?: string | null;
  contract_snapshot: Record<string, unknown>;
  result_binding_status?: string | null;
  result_record_type?: string | null;
  result_record_id?: string | null;
  result_status?: string | null;
  result_endpoint?: string | null;
  result_binding: Record<string, unknown>;
  result_bindings: Record<string, unknown>[];
  result_record_validation_status?: string | null;
  result_record_validation: Record<string, unknown>;
  result_record_validations: Record<string, unknown>[];
  readiness_refresh_status?: string | null;
  readiness_refresh: Record<string, unknown>;
  readiness_refreshes: Record<string, unknown>[];
  created_by?: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionAuditList = {
  operation_id: string;
  workspace_id: string;
  audit_count: number;
  latest_record?: CommercialOperationProductionClosedLoopActionAuditRecord | null;
  records: CommercialOperationProductionClosedLoopActionAuditRecord[];
  counts_by_status: Record<string, number>;
  evidence_coverage: Record<string, number>;
  next_actions: string[];
  operator_checklist: Record<string, unknown>[];
  primary_step?: Record<string, unknown> | null;
  boundaries: string[];
  generated_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionResultBindingStatus =
  | "result_recorded"
  | "result_failed"
  | "evidence_verified"
  | "binding_cancelled";

export type CommercialOperationProductionClosedLoopActionResultBindingRequest = {
  binding_status?: CommercialOperationProductionClosedLoopActionResultBindingStatus;
  result_record_type: string;
  result_record_id?: string | null;
  result_status?: string | null;
  result_endpoint?: string | null;
  evidence_links?: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_confirmed?: boolean;
  binding_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionResultBinding = {
  operation_id: string;
  workspace_id: string;
  audit_id: string;
  binding_id: string;
  binding_status: string;
  result_record_type: string;
  result_record_id?: string | null;
  result_status?: string | null;
  result_endpoint?: string | null;
  evidence_links: Record<string, unknown>[];
  evidence_summary?: string | null;
  operator_confirmed: boolean;
  binding_notes?: string | null;
  bound_by?: string | null;
  bound_at: string;
  audit_record: CommercialOperationProductionClosedLoopActionAuditRecord;
  boundaries: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionReadinessRefreshRequest = {
  platform?: string | null;
  force_metric_due?: boolean;
  operator_confirmed?: boolean;
  refresh_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionResultRecordValidationRequest = {
  operator_confirmed?: boolean;
  validation_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionResultRecordValidation = {
  operation_id: string;
  workspace_id: string;
  audit_id: string;
  validation_id: string;
  binding_id?: string | null;
  validation_status: string;
  result_record_type: string;
  result_record_id: string;
  record_exists: boolean;
  workspace_matches: boolean;
  operation_matches: boolean;
  status_matches: boolean;
  status_field?: string | null;
  record_status?: string | null;
  expected_statuses: string[];
  record_summary: Record<string, unknown>;
  supported_record_types: string[];
  operator_confirmed: boolean;
  validation_notes?: string | null;
  validated_by?: string | null;
  validated_at: string;
  audit_record: CommercialOperationProductionClosedLoopActionAuditRecord;
  result_binding: Record<string, unknown>;
  boundaries: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopActionReadinessRefresh = {
  operation_id: string;
  workspace_id: string;
  audit_id: string;
  refresh_id: string;
  binding_id?: string | null;
  refresh_status: string;
  underlying_refresh_status?: string | null;
  record_validation_gate_status?: string | null;
  record_validation_required: boolean;
  record_validation_passed: boolean;
  record_validation_blocking_reasons: string[];
  result_record_validation_status?: string | null;
  result_record_validation: Record<string, unknown>;
  audit_stage_key?: string | null;
  previous_action_key?: string | null;
  current_stage_key?: string | null;
  current_stage_status?: string | null;
  stage_completed_after_binding: boolean;
  next_action_key: string;
  operator_confirmed: boolean;
  refresh_notes?: string | null;
  readiness: CommercialOperationProductionClosedLoopReadiness;
  next_action: CommercialOperationProductionClosedLoopNextAction;
  audit_record: CommercialOperationProductionClosedLoopActionAuditRecord;
  result_binding: Record<string, unknown>;
  operator_next_actions: string[];
  boundaries: string[];
  refreshed_by?: string | null;
  refreshed_at: string;
  metadata: Record<string, unknown>;
};

export type CommercialOperationMainAgentAdvance = {
  operation_id: string;
  workspace_id: string;
  advance_status: "created" | "updated" | "reused" | "dry_run" | "blocked" | "noop" | string;
  dry_run: boolean;
  advanced_track: string;
  before_stage_key?: string | null;
  after_stage_key?: string | null;
  created_records: Record<string, unknown>[];
  updated_records: Record<string, unknown>[];
  reused_records: Record<string, unknown>[];
  blocked_by: string[];
  operator_next_actions: string[];
  server_next_actions: string[];
  client_next_actions: string[];
  execution_boundary: string;
  operation_loop: Record<string, unknown>;
  boundaries: string[];
  generated_at: string;
};

export type CommercialOperationProductionClosedLoopInterventionAcknowledgement = {
  operation_id: string;
  workspace_id: string;
  acknowledgement_id: string;
  acknowledgement_status: string;
  assignee?: string | null;
  primary_step_key?: string | null;
  staleness_status: string;
  waiting_seconds: number;
  priority_score: number;
  recommended_action_key?: string | null;
  queue_item_snapshot: Record<string, unknown>;
  operator_confirmed: boolean;
  acknowledgement_notes?: string | null;
  created_by?: string | null;
  created_at: string;
  boundaries: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationProductionClosedLoopInterventionAcknowledgementList = {
  operation_id: string;
  workspace_id: string;
  acknowledgement_count: number;
  latest_record?: CommercialOperationProductionClosedLoopInterventionAcknowledgement | null;
  records: CommercialOperationProductionClosedLoopInterventionAcknowledgement[];
  generated_at: string;
  boundaries: string[];
  metadata: Record<string, unknown>;
};

export type CommercialOperationContentDraft = {
  id: string;
  operation_id: string;
  step_key: string;
  channel: string;
  content_format: string;
  title: string;
  draft_status: string;
  summary?: string | null;
  content_body: string;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationApproval = {
  id: string;
  operation_id: string;
  step_key: string;
  title: string;
  requested_action?: string | null;
  approval_status: string;
  risk_level: string;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationDeliverable = {
  id: string;
  operation_id: string;
  content_draft_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  deliverable_type: string;
  title: string;
  deliverable_status: string;
  summary?: string | null;
  delivery_notes?: string | null;
  quality_checks: string[];
  package_payload?: Record<string, unknown>;
  result_summary?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationExecutionRequest = {
  id: string;
  operation_id: string;
  deliverable_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  execution_type: string;
  execution_mode: string;
  title: string;
  request_status: string;
  execution_target?: string | null;
  input_summary?: string | null;
  runbook: Record<string, unknown>[];
  readiness_checks: string[];
  expected_outputs: string[];
  operator_checklist: Record<string, unknown>[];
  handoff_payload?: Record<string, unknown>;
  result_summary?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationExecutionRun = {
  id: string;
  operation_id: string;
  execution_request_id: string;
  deliverable_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  execution_type: string;
  execution_mode: string;
  execution_target?: string | null;
  title: string;
  run_status: string;
  input_payload: Record<string, unknown>;
  runbook_snapshot: Record<string, unknown>[];
  readiness_checks: string[];
  expected_outputs: string[];
  operator_checklist_snapshot: Record<string, unknown>[];
  runtime_payload?: Record<string, unknown>;
  result_payload?: Record<string, unknown>;
  recovery_plan?: Record<string, unknown>;
  retry_count: number;
  max_retries: number;
  result_summary?: string | null;
  failure_reason?: string | null;
  operator_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationResult = {
  id: string;
  operation_id: string;
  execution_run_id: string;
  execution_request_id: string;
  deliverable_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  result_type: string;
  title: string;
  result_status: string;
  summary?: string | null;
  outcome_summary?: string | null;
  observed_metrics: Record<string, unknown>[];
  commercial_signals: string[];
  evidence_links: Record<string, unknown>[];
  follow_up_actions: string[];
  result_payload: Record<string, unknown>;
  recommendation_payload: Record<string, unknown>;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationMonitoringObservation = {
  id: string;
  operation_id: string;
  result_id: string;
  execution_run_id: string;
  execution_request_id: string;
  deliverable_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  observation_type: string;
  title: string;
  observation_status: string;
  observation_window_start?: string | null;
  observation_window_end?: string | null;
  metric_snapshots: Record<string, unknown>[];
  qualitative_signals: string[];
  evidence_links: Record<string, unknown>[];
  anomaly_flags: string[];
  recommended_actions: string[];
  observation_payload: Record<string, unknown>;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationOptimizationDecision = {
  id: string;
  operation_id: string;
  observation_id: string;
  result_id: string;
  execution_run_id: string;
  execution_request_id: string;
  deliverable_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  decision_type: string;
  title: string;
  decision_status: string;
  priority: string;
  rationale?: string | null;
  objective_updates: string[];
  content_actions: string[];
  asset_actions: string[];
  audience_actions: string[];
  execution_actions: string[];
  risk_controls: string[];
  decision_payload: Record<string, unknown>;
  next_review_at?: string | null;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

function queryString(params: Record<string, string | number | null | undefined>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
  settings: ConversationSettings = defaultConversationSettings,
): Promise<T> {
  const response = await fetch(`${conversationClient.normalizeApiBase(settings.aiServerUrl)}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-Id": settings.workspaceId,
      "X-User-Id": settings.userId,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Commercial operation request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const commercialOperationClient = {
  list: (settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperation[] }>("/commercial-operations", {}, settings),
  create: (
    payload: {
      title: string;
      objective: string;
      target_audience?: string;
      channels?: string[];
      knowledge_collection?: string;
      success_metrics?: string[];
      constraints?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperation>(
      "/commercial-operations",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  delete: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperation>(
      `/commercial-operations/${encodeURIComponent(operationId)}`,
      { method: "DELETE" },
      settings,
    ),
  collectPlanningIntelligence: (
    payload: {
      topic: string;
      platform?: string | null;
      project_title?: string | null;
      objective?: string | null;
      target_audience?: string | null;
      max_results?: number;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPlanningIntelligence>(
      "/commercial-operations/planning-intelligence",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  operationLoop: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationLoopSummary>(
      `/commercial-operations/${encodeURIComponent(operationId)}/operation-loop`,
      {},
      settings,
    ),
  productionClosedLoopReadiness: (
    operationId: string,
    options?: { platform?: string | null; force_metric_due?: boolean },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopReadiness>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/readiness${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopAcceptanceSummary: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopAcceptanceSummary>(
      `/commercial-operations/production-closed-loop/acceptance-summary${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryPlan: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryPlan>(
      `/commercial-operations/production-closed-loop/delivery-plan${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryActionPackages: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryActionPackages>(
      `/commercial-operations/production-closed-loop/delivery-action-packages${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryAuditBlockerClearancePlan: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number; work_order_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlan>(
      `/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
        work_order_limit: options?.work_order_limit ? String(options.work_order_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  assignProductionClosedLoopDeliveryAuditBlockerWorkOrders: (
    payload: CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignment>(
      "/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan/assign-work-orders",
      { method: "POST", body: JSON.stringify(payload) },
      settings,
    ),
  productionClosedLoopDeliveryAuditBlockerRunbookPackages: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number; work_order_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackages>(
      `/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
        work_order_limit: options?.work_order_limit ? String(options.work_order_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecords: (
    options?: { package_key?: string | null; gate_key?: string | null; operation_id?: string | null; evidence_status?: string | null; limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceList>(
      `/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records${queryString({
        package_key: options?.package_key || undefined,
        gate_key: options?.gate_key || undefined,
        operation_id: options?.operation_id || undefined,
        evidence_status: options?.evidence_status || undefined,
        limit: options?.limit ? String(options.limit) : undefined,
      })}`,
      {},
      settings,
    ),
  recordProductionClosedLoopDeliveryAuditBlockerRunbookEvidence: (
    payload: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecord>(
      "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records",
      { method: "POST", body: JSON.stringify(payload) },
      settings,
    ),
  productionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number; work_order_limit?: number; evidence_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverage>(
      `/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
        work_order_limit: options?.work_order_limit ? String(options.work_order_limit) : undefined,
        evidence_limit: options?.evidence_limit ? String(options.evidence_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryAuditNextActionPlan: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number; work_order_limit?: number; evidence_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlan>(
      `/commercial-operations/production-closed-loop/delivery-audit/next-action-plan${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
        work_order_limit: options?.work_order_limit ? String(options.work_order_limit) : undefined,
        evidence_limit: options?.evidence_limit ? String(options.evidence_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryAuditOperatorQueue: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number; work_order_limit?: number; evidence_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueue>(
      `/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
        work_order_limit: options?.work_order_limit ? String(options.work_order_limit) : undefined,
        evidence_limit: options?.evidence_limit ? String(options.evidence_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryAuditOperatorQueueRecords: (
    options?: { queue_key?: string | null; action_key?: string | null; owner?: string | null; operation_id?: string | null; record_status?: string | null; limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordList>(
      `/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records${queryString({
        queue_key: options?.queue_key || undefined,
        action_key: options?.action_key || undefined,
        owner: options?.owner || undefined,
        operation_id: options?.operation_id || undefined,
        record_status: options?.record_status || undefined,
        limit: options?.limit ? String(options.limit) : undefined,
      })}`,
      {},
      settings,
    ),
  recordProductionClosedLoopDeliveryAuditOperatorQueueRecord: (
    payload: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecord>(
      "/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records",
      { method: "POST", body: JSON.stringify(payload) },
      settings,
    ),
  productionClosedLoopDeliveryAuditOpenClawProviderHandoff: (settings?: ConversationSettings) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoff>(
      "/commercial-operations/production-closed-loop/delivery-audit/openclaw-provider-handoff",
      {},
      settings,
    ),
  refreshProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadiness: (
    payload: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefresh>(
      "/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh",
      { method: "POST", body: JSON.stringify(payload) },
      settings,
    ),
  productionClosedLoopDeliveryRemediationMap: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationMap>(
      `/commercial-operations/production-closed-loop/delivery-remediation-map${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryRemediationWorkOrders: (
    options?: { gate_key?: string | null; operation_id?: string | null; work_order_status?: string | null; limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderList>(
      `/commercial-operations/production-closed-loop/delivery-remediation-map/work-orders${queryString({
        gate_key: options?.gate_key || undefined,
        operation_id: options?.operation_id || undefined,
        work_order_status: options?.work_order_status || undefined,
        limit: options?.limit ? String(options.limit) : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopDeliveryRemediationWorkOrderCoverage: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number; work_order_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverage>(
      `/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
        work_order_limit: options?.work_order_limit ? String(options.work_order_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  assignMissingProductionClosedLoopDeliveryRemediationWorkOrders: (
    payload: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignment>(
      "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage/assign-missing",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  productionClosedLoopDeliveryRemediationWorkOrderExecutionPrep: (
    options?: { platform?: string | null; force_metric_due?: boolean; limit?: number; scan_limit?: number; work_order_limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrep>(
      `/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
        limit: options?.limit ? String(options.limit) : undefined,
        scan_limit: options?.scan_limit ? String(options.scan_limit) : undefined,
        work_order_limit: options?.work_order_limit ? String(options.work_order_limit) : undefined,
      })}`,
      {},
      settings,
    ),
  completeProductionClosedLoopDeliveryRemediationWorkOrder: (
    payload: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletion>(
      "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep/complete",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  refreshProductionClosedLoopDeliveryRemediationWorkOrderReadiness: (
    payload: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefresh>(
      "/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-completion/readiness-refresh",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  recordProductionClosedLoopDeliveryRemediationWorkOrder: (
    payload: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecord>(
      "/commercial-operations/production-closed-loop/delivery-remediation-map/work-orders",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  productionClosedLoopDeliveryActionEvidenceRecords: (
    options?: { gate_key?: string | null; operation_id?: string | null; limit?: number },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryActionEvidenceList>(
      `/commercial-operations/production-closed-loop/delivery-action-packages/evidence-records${queryString({
        gate_key: options?.gate_key || undefined,
        operation_id: options?.operation_id || undefined,
        limit: options?.limit ? String(options.limit) : undefined,
      })}`,
      {},
      settings,
    ),
  recordProductionClosedLoopDeliveryActionEvidence: (
    payload: CommercialOperationProductionClosedLoopDeliveryActionEvidenceRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecord>(
      "/commercial-operations/production-closed-loop/delivery-action-packages/evidence-records",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  productionClosedLoopNextAction: (
    operationId: string,
    options?: { platform?: string | null; force_metric_due?: boolean },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopNextAction>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/next-action${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
      })}`,
      {},
      settings,
    ),
  productionClosedLoopActionAudits: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationProductionClosedLoopActionAuditList>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/next-action/audit-records`,
      {},
      settings,
    ),
  recordProductionClosedLoopActionAudit: (
    operationId: string,
    payload: CommercialOperationProductionClosedLoopActionAuditRequest,
    options?: { platform?: string | null; force_metric_due?: boolean },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopActionAuditRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/next-action/audit-records${queryString({
        platform: options?.platform || undefined,
        force_metric_due: options?.force_metric_due ? "true" : undefined,
      })}`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  bindProductionClosedLoopActionResult: (
    operationId: string,
    auditId: string,
    payload: CommercialOperationProductionClosedLoopActionResultBindingRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopActionResultBinding>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/next-action/audit-records/${encodeURIComponent(auditId)}/result-binding`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  refreshProductionClosedLoopActionReadinessAfterResultBinding: (
    operationId: string,
    auditId: string,
    payload: CommercialOperationProductionClosedLoopActionReadinessRefreshRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopActionReadinessRefresh>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/next-action/audit-records/${encodeURIComponent(auditId)}/result-binding/readiness-refresh`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  validateProductionClosedLoopActionResultRecord: (
    operationId: string,
    auditId: string,
    payload: CommercialOperationProductionClosedLoopActionResultRecordValidationRequest,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopActionResultRecordValidation>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/next-action/audit-records/${encodeURIComponent(auditId)}/result-binding/record-validation`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  agentSkillOrchestration: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationAgentSkillOrchestration>(
      `/commercial-operations/${encodeURIComponent(operationId)}/agent-skill-orchestration`,
      {},
      settings,
    ),
  refreshAgentSkillOrchestration: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationAgentSkillOrchestration>(
      `/commercial-operations/${encodeURIComponent(operationId)}/agent-skill-orchestration/refresh`,
      { method: "POST" },
      settings,
    ),
  productionClosedLoopInterventionAcknowledgements: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationProductionClosedLoopInterventionAcknowledgementList>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/intervention-queue/acknowledgements`,
      {},
      settings,
    ),
  createProductionClosedLoopInterventionAcknowledgement: (
    operationId: string,
    payload: {
      acknowledgement_status?: "acknowledged" | "assigned" | "in_progress" | "dismissed";
      assignee?: string | null;
      operator_confirmed?: boolean;
      acknowledgement_notes?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionClosedLoopInterventionAcknowledgement>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-closed-loop/intervention-queue/acknowledgements`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  planDraft: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationPlanPreview>(
      `/commercial-operations/${encodeURIComponent(operationId)}/plan-draft`,
      { method: "POST" },
      settings,
    ),
  generateLlmPlanCandidate: (
    payload: {
      system_prompt?: string;
      user_prompt: string;
      temperature?: number;
      max_tokens?: number;
      variables?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationLLMResponse>(
      "/llm/test",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  planLlmResource: (
    payload: {
      task_type?: string;
      client_id?: string;
      priority?: string;
      expected_tokens?: number;
      allow_queue?: boolean;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationLLMResourcePlan>(
      "/llm/resource-plan",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  advanceMainAgentLoop: (
    operationId: string,
    payload?: { dry_run?: boolean; operator_note?: string; metadata?: Record<string, unknown> },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMainAgentAdvance>(
      `/commercial-operations/${encodeURIComponent(operationId)}/main-agent/advance-loop`,
      {
        method: "POST",
        body: JSON.stringify(payload ?? {}),
      },
      settings,
    ),
  listOperationPlans: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationPlan[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/operation-plans${queryString({ status })}`,
      {},
      settings,
    ),
  createOperationPlan: (
    operationId: string,
    payload: CommercialOperationPlanCreatePayload,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPlan>(
      `/commercial-operations/${encodeURIComponent(operationId)}/operation-plans`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  decideOperationPlan: (
    operationId: string,
    planId: string,
    action: "ready" | "approve" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPlan>(
      `/commercial-operations/${encodeURIComponent(operationId)}/operation-plans/${encodeURIComponent(planId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  createProjectMaterial: (
    operationId: string,
    payload: {
      production_task_id?: string | null;
      material_type: string;
      name: string;
      source_uri: string;
      file_name?: string;
      mime_type?: string;
      size_bytes?: number;
      authorization_status?: string;
      usage_scope?: string;
      tags?: string[];
      linked_task_ids?: string[];
      notes?: string;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProjectMaterial>(
      `/commercial-operations/${encodeURIComponent(operationId)}/project-materials`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listProjectMaterials: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationProjectMaterial[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/project-materials${queryString({ status })}`,
      {},
      settings,
    ),
  decideProjectMaterial: (
    operationId: string,
    materialId: string,
    action: "ready" | "approve" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProjectMaterial>(
      `/commercial-operations/${encodeURIComponent(operationId)}/project-materials/${encodeURIComponent(materialId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  listProductionTasks: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationProductionTask[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-tasks${queryString({ status })}`,
      {},
      settings,
    ),
  createProductionTask: (
    operationId: string,
    payload: {
      operation_plan_id?: string | null;
      task_type: "copy" | "image" | "media";
      media_subtype?: "video" | "audio" | "audio_video" | "digital_human" | "postprocess" | null;
      channel: string;
      title: string;
      brief?: string | null;
      source_material_ids?: string[];
      output_requirements?: Record<string, unknown>[];
      target_specs?: Record<string, unknown>;
      workflow_selection_required?: boolean;
      assigned_agent?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionTask>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-tasks`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  decideProductionTask: (
    operationId: string,
    productionTaskId: string,
    action: "ready" | "approve" | "start" | "block" | "complete" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationProductionTask>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-tasks/${encodeURIComponent(productionTaskId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  listWorkflowCandidates: (
    operationId: string,
    productionTaskId: string,
    limit?: number,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationWorkflowCandidateList>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-tasks/${encodeURIComponent(productionTaskId)}/workflow-candidates${queryString({ limit })}`,
      {},
      settings,
    ),
  createWorkflowSelection: (
    operationId: string,
    payload: {
      production_task_id: string;
      workflow_source?: string;
      workflow_name: string;
      workflow_kind?: string;
      output_type: string;
      candidate_summary?: string;
      input_requirements?: Record<string, unknown>[];
      expected_outputs?: Record<string, unknown>[];
      recommendation_reason?: string;
      estimated_duration_seconds?: number;
      estimated_vram_mb?: number;
      risk_notes?: string;
      validation_status?: string;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationWorkflowSelection>(
      `/commercial-operations/${encodeURIComponent(operationId)}/workflow-selections`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listWorkflowSelections: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationWorkflowSelection[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/workflow-selections${queryString({ status })}`,
      {},
      settings,
    ),
  decideWorkflowSelection: (
    operationId: string,
    workflowSelectionId: string,
    action: "ready" | "approve" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationWorkflowSelection>(
      `/commercial-operations/${encodeURIComponent(operationId)}/workflow-selections/${encodeURIComponent(workflowSelectionId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  listOutputCandidates: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationOutputCandidate[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/output-candidates${queryString({ status })}`,
      {},
      settings,
    ),
  createOutputCandidate: (
    operationId: string,
    payload: {
      production_task_id?: string | null;
      workflow_selection_id?: string | null;
      output_artifact_id?: string | null;
      candidate_type: string;
      title: string;
      preview_uri?: string | null;
      source_uri?: string | null;
      thumbnail_uri?: string | null;
      mime_type?: string | null;
      duration_seconds?: number | null;
      generation_summary?: string;
      quality_checks?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationOutputCandidate>(
      `/commercial-operations/${encodeURIComponent(operationId)}/output-candidates`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  decideOutputCandidate: (
    operationId: string,
    outputCandidateId: string,
    action: "ready" | "select" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationOutputCandidate>(
      `/commercial-operations/${encodeURIComponent(operationId)}/output-candidates/${encodeURIComponent(outputCandidateId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  getOutputPrepPackage: (operationId: string, productionTaskId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationOutputPrepPackage>(
      `/commercial-operations/${encodeURIComponent(operationId)}/production-tasks/${encodeURIComponent(productionTaskId)}/output-prep-package`,
      {},
      settings,
    ),
  createFinalSelection: (
    operationId: string,
    payload: {
      production_task_id?: string | null;
      output_candidate_id: string;
      final_type: string;
      title: string;
      selection_reason?: string;
      platform_targets?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationFinalSelection>(
      `/commercial-operations/${encodeURIComponent(operationId)}/final-selections`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listFinalSelections: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationFinalSelection[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/final-selections${queryString({ status })}`,
      {},
      settings,
    ),
  decideFinalSelection: (
    operationId: string,
    finalSelectionId: string,
    action: "ready" | "approve" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationFinalSelection>(
      `/commercial-operations/${encodeURIComponent(operationId)}/final-selections/${encodeURIComponent(finalSelectionId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  getPublishPrepPackage: (operationId: string, finalSelectionId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationPublishPrepPackage>(
      `/commercial-operations/${encodeURIComponent(operationId)}/final-selections/${encodeURIComponent(finalSelectionId)}/publish-prep-package`,
      {},
      settings,
    ),
  createPublishPackage: (
    operationId: string,
    payload: {
      final_selection_id?: string | null;
      platform: string;
      account_ref?: string | null;
      title: string;
      body: string;
      hashtags?: string[];
      cover_candidate_id?: string | null;
      scheduled_at?: string | null;
      publish_payload?: Record<string, unknown>;
      risk_notes?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPublishPackage>(
      `/commercial-operations/${encodeURIComponent(operationId)}/publish-packages`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listPublishPackages: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationPublishPackage[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/publish-packages${queryString({ status })}`,
      {},
      settings,
    ),
  decidePublishPackage: (
    operationId: string,
    publishPackageId: string,
    action: "ready" | "approve" | "prepare" | "publish" | "fail" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPublishPackage>(
      `/commercial-operations/${encodeURIComponent(operationId)}/publish-packages/${encodeURIComponent(publishPackageId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  getPublishExecutionHandoff: (operationId: string, publishPackageId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationPublishExecutionHandoff>(
      `/commercial-operations/${encodeURIComponent(operationId)}/publish-packages/${encodeURIComponent(publishPackageId)}/client-execution-handoff`,
      {},
      settings,
    ),
  updatePublishExecutionStatus: (
    operationId: string,
    publishPackageId: string,
    payload: {
      execution_status: CommercialOperationPublishExecutionStatusValue;
      operator_confirmed: boolean;
      customer_machine_id?: string;
      attempt_id?: string | null;
      progress?: number | null;
      failure_reason?: string | null;
      operator_notes?: string | null;
      retry_after_seconds?: number | null;
      evidence_links?: Record<string, unknown>[];
      execution_log?: Record<string, unknown>[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPublishExecutionStatus>(
      `/commercial-operations/${encodeURIComponent(operationId)}/publish-packages/${encodeURIComponent(publishPackageId)}/execution-status`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  capturePublishExecutionResult: (
    operationId: string,
    publishPackageId: string,
    payload: {
      publish_succeeded?: boolean;
      platform_content_id?: string | null;
      published_url?: string | null;
      execution_summary?: string | null;
      operator_notes?: string | null;
      evidence_links?: Record<string, unknown>[];
      dry_run_evidence?: Record<string, unknown>[];
      execution_log?: Record<string, unknown>[];
      observed_metrics?: Record<string, unknown>;
      metric_snapshot_summary?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPublishExecutionResult>(
      `/commercial-operations/${encodeURIComponent(operationId)}/publish-packages/${encodeURIComponent(publishPackageId)}/execution-result`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listPlatformMetricSnapshots: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationPlatformMetricSnapshot[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/platform-metric-snapshots${queryString({ status })}`,
      {},
      settings,
    ),
  createPlatformMetricSnapshot: (
    operationId: string,
    payload: {
      publish_package_id?: string | null;
      platform: string;
      platform_content_id?: string | null;
      source_type?: string;
      collected_at?: string | null;
      metric_date?: string | null;
      metrics?: Record<string, unknown>;
      summary?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPlatformMetricSnapshot>(
      `/commercial-operations/${encodeURIComponent(operationId)}/platform-metric-snapshots`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  decidePlatformMetricSnapshot: (
    operationId: string,
    snapshotId: string,
    action: "ready" | "approve" | "reject" | "archive",
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationPlatformMetricSnapshot>(
      `/commercial-operations/${encodeURIComponent(operationId)}/platform-metric-snapshots/${encodeURIComponent(snapshotId)}/${action}`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  getMetricAnalysisSchedule: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationMetricAnalysisSchedule>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule`,
      {},
      settings,
    ),
  configureMetricAnalysisSchedule: (
    operationId: string,
    payload: {
      enabled?: boolean;
      local_time?: string;
      timezone?: string;
      lookback_hours?: number;
      platform_scope?: string[];
      metric_requirements?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricAnalysisSchedule>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  runMetricAnalysisSchedule: (
    operationId: string,
    payload: {
      force?: boolean;
      collected_metrics?: Record<string, unknown>[];
      operator_notes?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricAnalysisRun>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule/run`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  getMetricAnalysisDispatchQueue: (platform?: string, force?: boolean, limit?: number, settings?: ConversationSettings) =>
    requestJson<CommercialOperationMetricAnalysisDispatchQueue>(
      `/commercial-operations/metric-analysis-dispatch${queryString({
        platform: platform || undefined,
        force: force ? "true" : undefined,
        limit: limit ? String(limit) : undefined,
      })}`,
      {},
      settings,
    ),
  listMetricAnalysisDispatchClaims: (status?: string, limit?: number, settings?: ConversationSettings) =>
    requestJson<CommercialOperationMetricDispatchClaimList>(
      `/commercial-operations/metric-analysis-dispatch/claims${queryString({
        status: status || undefined,
        limit: limit ? String(limit) : undefined,
      })}`,
      {},
      settings,
    ),
  pollMetricAnalysisDispatchForCustomerMachine: (
    payload: {
      platform?: string | null;
      force?: boolean;
      collection_mode?: string | null;
      customer_machine_id?: string;
      auto_claim?: boolean;
      operator_confirmed?: boolean;
      lease_seconds?: number;
      target_operation_id?: string | null;
      limit?: number;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricDispatchCustomerPoll>(
      "/commercial-operations/metric-analysis-dispatch/customer-poll",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  scheduleMetricDispatchCustomerPoll: (
    payload: {
      platform?: string | null;
      force?: boolean;
      collection_mode?: string | null;
      customer_machine_id?: string;
      scheduler_enabled?: boolean;
      auto_claim?: boolean;
      operator_confirmed?: boolean;
      requested_poll_interval_seconds?: number | null;
      lease_seconds?: number;
      target_operation_id?: string | null;
      limit?: number;
      run_poll_now?: boolean;
      notification_channels?: string[];
      notify_on?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricDispatchPollScheduler>(
      "/commercial-operations/metric-analysis-dispatch/customer-poll/scheduler",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  claimMetricAnalysisDispatch: (
    payload: {
      platform?: string | null;
      force?: boolean;
      collection_mode?: string | null;
      customer_machine_id?: string;
      operator_confirmed?: boolean;
      lease_seconds?: number;
      target_operation_id?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricDispatchClaim>(
      "/commercial-operations/metric-analysis-dispatch/claims",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateMetricAnalysisDispatchClaim: (
    claimId: string,
    payload: {
      claim_status?: "claimed" | "running" | "completed" | "failed" | "released" | string;
      progress?: number | null;
      lease_seconds?: number;
      operator_notes?: string | null;
      evidence_links?: Record<string, unknown>[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricDispatchClaim>(
      `/commercial-operations/metric-analysis-dispatch/claims/${encodeURIComponent(claimId)}/status`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  getMetricPullbackHandoff: (operationId: string, force?: boolean, settings?: ConversationSettings) =>
    requestJson<CommercialOperationMetricPullbackHandoff>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule/pullback-handoff${queryString({ force: force ? "true" : undefined })}`,
      {},
      settings,
    ),
  getMetricPullbackAdapterProfile: (
    operationId: string,
    platform?: string,
    force?: boolean,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricPullbackAdapterProfile>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule/pullback-handoff/adapter-profile${queryString({
        platform: platform || undefined,
        force: force ? "true" : undefined,
      })}`,
      {},
      settings,
    ),
  previewMetricPullbackExportImport: (
    operationId: string,
    payload: {
      platform?: string;
      force?: boolean;
      export_format?: "csv" | "json" | "manual_rows" | "xlsx_rows";
      raw_text?: string | null;
      rows?: Record<string, unknown>[];
      evidence_links?: Record<string, unknown>[];
      operator_confirmed?: boolean;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricPullbackExportImportPreview>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule/pullback-handoff/adapter-profile/parse-export`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  createMetricPullbackBrowserAssistSession: (
    operationId: string,
    payload: {
      platform?: string;
      force?: boolean;
      operator_confirmed?: boolean;
      target_publish_package_id?: string | null;
      open_target_url?: boolean;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricPullbackBrowserAssistSession>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule/pullback-handoff/adapter-profile/browser-assist-session`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  submitMetricPullbackResult: (
    operationId: string,
    payload: {
      force?: boolean;
      adapter_mode?: string;
      adapter_run_id?: string | null;
      collected_metrics?: Record<string, unknown>[];
      operator_notes?: string | null;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMetricPullbackSubmission>(
      `/commercial-operations/${encodeURIComponent(operationId)}/metric-analysis-schedule/pullback-handoff/submit-result`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  createContentDraft: (
    operationId: string,
    payload: {
      step_key?: string;
      channel: string;
      content_format?: string;
      title: string;
      audience_segment?: string;
      content_body?: string;
      summary?: string;
      call_to_action?: string;
      source_materials?: string[];
      asset_requests?: Record<string, unknown>[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyContentDraft: (
    operationId: string,
    draftId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  listContentDrafts: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationContentDraft[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts${queryString({ status })}`,
      {},
      settings,
    ),
  approveContentDraft: (
    operationId: string,
    draftId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectContentDraft: (
    operationId: string,
    draftId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  createApproval: (
    operationId: string,
    payload: {
      step_key: string;
      title: string;
      requested_action?: string;
      risk_level?: string;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationApproval>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listApprovals: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationApproval[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals${queryString({ status })}`,
      {},
      settings,
    ),
  approveApproval: (
    operationId: string,
    approvalId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationApproval>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectApproval: (
    operationId: string,
    approvalId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationApproval>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  createDeliverable: (
    operationId: string,
    payload: {
      step_key?: string;
      content_draft_id: string;
      asset_request_ids?: string[];
      deliverable_type?: string;
      title: string;
      summary?: string;
      delivery_notes?: string;
      quality_checks?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyDeliverable: (
    operationId: string,
    deliverableId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveDeliverable: (
    operationId: string,
    deliverableId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  packageDeliverable: (
    operationId: string,
    deliverableId: string,
    resultSummary: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/package`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  createExecutionRequest: (
    operationId: string,
    payload: {
      deliverable_id: string;
      execution_type?: string;
      execution_mode?: string;
      title: string;
      execution_target?: string;
      input_summary?: string;
      runbook?: Record<string, unknown>[];
      readiness_checks?: string[];
      expected_outputs?: string[];
      evidence_snapshot_ids?: string[];
      operator_checklist?: Record<string, unknown>[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRequest>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRequest>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  listExecutionRequests: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationExecutionRequest[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests${queryString({ status })}`,
      {},
      settings,
    ),
  approveExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRequest>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  prepareExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    resultSummary: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRequest>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/prepare`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  createExecutionRun: (
    operationId: string,
    payload: {
      execution_request_id: string;
      title?: string;
      execution_target?: string;
      input_payload?: Record<string, unknown>;
      max_retries?: number;
      operator_notes?: string;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRun>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateExecutionRun: (
    operationId: string,
    executionRunId: string,
    payload: {
      title?: string;
      execution_target?: string | null;
      input_payload?: Record<string, unknown>;
      max_retries?: number;
      operator_notes?: string;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRun>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listExecutionRuns: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationExecutionRun[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs${queryString({ status })}`,
      {},
      settings,
    ),
  startExecutionRun: (
    operationId: string,
    executionRunId: string,
    operatorNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRun>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/start`,
      {
        method: "POST",
        body: JSON.stringify({ operator_notes: operatorNotes }),
      },
      settings,
    ),
  succeedExecutionRun: (
    operationId: string,
    executionRunId: string,
    resultSummary: string,
    resultPayload: Record<string, unknown>,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRun>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/succeed`,
      {
        method: "POST",
        body: JSON.stringify({
          result_summary: resultSummary,
          result_payload: resultPayload,
        }),
      },
      settings,
    ),
  failExecutionRun: (
    operationId: string,
    executionRunId: string,
    failureReason: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRun>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({
          failure_reason: failureReason,
          result_payload: { external_execution_attempted: false },
        }),
      },
      settings,
    ),
  retryExecutionRun: (
    operationId: string,
    executionRunId: string,
    operatorNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRun>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/retry`,
      {
        method: "POST",
        body: JSON.stringify({ operator_notes: operatorNotes }),
      },
      settings,
    ),
  createResult: (
    operationId: string,
    payload: {
      execution_run_id: string;
      result_type?: string;
      title?: string;
      summary?: string;
      outcome_summary?: string;
      observed_metrics?: Record<string, unknown>[];
      commercial_signals?: string[];
      evidence_links?: Record<string, unknown>[];
      follow_up_actions?: string[];
      result_payload?: Record<string, unknown>;
      recommendation_payload?: Record<string, unknown>;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationResult>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listResults: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationResult[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results${queryString({ status })}`,
      {},
      settings,
    ),
  readyResult: (operationId: string, resultId: string, reviewerNotes: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationResult>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveResult: (operationId: string, resultId: string, reviewerNotes: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationResult>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  createMonitoringObservation: (
    operationId: string,
    payload: {
      result_id: string;
      observation_type?: string;
      title?: string;
      metric_snapshots?: Record<string, unknown>[];
      qualitative_signals?: string[];
      evidence_links?: Record<string, unknown>[];
      anomaly_flags?: string[];
      recommended_actions?: string[];
      observation_payload?: Record<string, unknown>;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMonitoringObservation>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listMonitoringObservations: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationMonitoringObservation[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations${queryString({ status })}`,
      {},
      settings,
    ),
  readyMonitoringObservation: (
    operationId: string,
    observationId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMonitoringObservation>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveMonitoringObservation: (
    operationId: string,
    observationId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationMonitoringObservation>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  createOptimizationDecision: (
    operationId: string,
    payload: {
      observation_id: string;
      decision_type?: string;
      title?: string;
      priority?: string;
      rationale?: string;
      objective_updates?: string[];
      content_actions?: string[];
      asset_actions?: string[];
      audience_actions?: string[];
      execution_actions?: string[];
      risk_controls?: string[];
      decision_payload?: Record<string, unknown>;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationOptimizationDecision>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  listOptimizationDecisions: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationOptimizationDecision[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions${queryString({ status })}`,
      {},
      settings,
    ),
  readyOptimizationDecision: (
    operationId: string,
    optimizationDecisionId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationOptimizationDecision>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveOptimizationDecision: (
    operationId: string,
    optimizationDecisionId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationOptimizationDecision>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
};
