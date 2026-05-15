import { AdminSettings, ApiList, JsonRecord, readAdminSettings, requestJson } from "./client";

export interface WorkflowTemplateVersion {
  id: string;
  template_id: string;
  version: string;
  graph_definition: JsonRecord;
  entry_node: string;
  input_schema: JsonRecord;
  output_schema: JsonRecord;
  compatibility: JsonRecord;
  validation_status: string;
  validation_errors: string[];
  changelog: string | null;
  created_by: string | null;
  created_at: string;
}

export interface WorkflowTemplate {
  id: string;
  workspace_id: string;
  template_key: string;
  name: string;
  description: string | null;
  category: string | null;
  status: string;
  current_version: string | null;
  latest_version: string | null;
  risk_level: string;
  tags: string[];
  featured: boolean;
  verified: boolean;
  recommended: boolean;
  usage_count: number;
  success_rate: number;
  average_runtime_ms: number;
  average_step_count: number;
  metadata: JsonRecord;
  versions: WorkflowTemplateVersion[];
  created_at: string;
  updated_at: string;
}

export interface WorkflowTemplateRun {
  id: string;
  template_id: string;
  template_version_id: string;
  workflow_run_id: string | null;
  source_type: string | null;
  source_id: string | null;
  status: string;
  input_payload: JsonRecord;
  output_payload: JsonRecord;
  metadata: JsonRecord;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface WorkflowTemplateCompatibility {
  compatible: boolean;
  warnings: string[];
  errors: string[];
  missing_capabilities: string[];
  validation_status: string;
}

export interface WorkflowTemplateReview {
  id: string;
  template_id: string;
  template_version_id: string;
  reviewer_id: string | null;
  review_status: string;
  review_notes: string | null;
  risk_assessment: JsonRecord;
  compatibility_report: JsonRecord;
  created_at: string;
  updated_at: string;
}

export interface WorkflowTemplateMarketplaceItem {
  template: WorkflowTemplate;
  badges: string[];
  metrics: JsonRecord;
  governance_status: string;
  latest_review_status: string | null;
}

export interface WorkflowTemplateAuditLog {
  id: string;
  template_id: string | null;
  template_version_id: string | null;
  action: string;
  actor_id: string | null;
  previous_state: JsonRecord;
  new_state: JsonRecord;
  metadata: JsonRecord;
  created_at: string;
}

export interface WorkflowTemplateCompatibilityMatrixRow {
  id: string;
  template_version_id: string;
  runtime_capability: string;
  supported: boolean;
  notes: string | null;
  metadata: JsonRecord;
  created_at: string;
}

export const workflowTemplateClient = {
  listTemplates: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<WorkflowTemplate>>("/workflow-templates", {}, settings),
  getTemplate: (templateId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplate>(`/workflow-templates/${templateId}`, {}, settings),
  validateTemplate: (templateId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplateCompatibility>(`/workflow-templates/${templateId}/validate`, { method: "POST" }, settings),
  exportTemplate: (templateId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<JsonRecord>(`/workflow-templates/${templateId}/export`, {}, settings),
  importTemplateDryRun: (template: JsonRecord, settings: AdminSettings = readAdminSettings()) =>
    requestJson<JsonRecord>("/workflow-templates/import", {
      method: "POST",
      body: JSON.stringify({ template, dry_run: true, conflict_strategy: "new_version" }),
    }, settings),
  runTemplate: (templateId: string, settings: AdminSettings = readAdminSettings(), input: JsonRecord = {}) =>
    requestJson<WorkflowTemplateRun>(`/workflow-templates/${templateId}/run`, {
      method: "POST",
      body: JSON.stringify({ input, mode: "review_first", execution_mode: "immediate" }),
    }, settings),
  listRuns: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<WorkflowTemplateRun>>("/workflow-template-runs", {}, settings),
  listReviews: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<WorkflowTemplateReview>>("/workflow-template-reviews", {}, settings),
  submitReview: (templateId: string, templateVersionId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplateReview>("/workflow-template-reviews", {
      method: "POST",
      body: JSON.stringify({ template_id: templateId, template_version_id: templateVersionId, review_notes: "Submitted from Admin Dashboard" }),
    }, settings),
  approveReview: (reviewId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplateReview>(`/workflow-template-reviews/${reviewId}/approve`, {
      method: "POST",
      body: JSON.stringify({ review_notes: "Approved from Admin Dashboard" }),
    }, settings),
  rejectReview: (reviewId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplateReview>(`/workflow-template-reviews/${reviewId}/reject`, {
      method: "POST",
      body: JSON.stringify({ review_notes: "Rejected from Admin Dashboard" }),
    }, settings),
  requestChanges: (reviewId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplateReview>(`/workflow-template-reviews/${reviewId}/request-changes`, {
      method: "POST",
      body: JSON.stringify({ review_notes: "Changes requested from Admin Dashboard" }),
    }, settings),
  activateVersion: (templateId: string, versionId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplate>(`/workflow-templates/${templateId}/activate-version/${versionId}`, { method: "POST" }, settings),
  rollbackTemplate: (templateId: string, versionId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplate>(`/workflow-templates/${templateId}/rollback/${versionId}`, {
      method: "POST",
      body: JSON.stringify({ reason: "Rollback from Admin Dashboard" }),
    }, settings),
  deprecateTemplate: (templateId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplate>(`/workflow-templates/${templateId}/deprecate`, {
      method: "POST",
      body: JSON.stringify({ reason: "Deprecated from Admin Dashboard" }),
    }, settings),
  archiveTemplate: (templateId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowTemplate>(`/workflow-templates/${templateId}/archive`, {
      method: "POST",
      body: JSON.stringify({ reason: "Archived from Admin Dashboard" }),
    }, settings),
  listAuditLogs: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<WorkflowTemplateAuditLog>>("/workflow-template-audit-logs", {}, settings),
  listMarketplace: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ items: WorkflowTemplateMarketplaceItem[] }>("/workflow-template-marketplace", {}, settings),
  listCompatibilityMatrix: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<WorkflowTemplateCompatibilityMatrixRow>>("/workflow-template-compatibility-matrix", {}, settings),
};
