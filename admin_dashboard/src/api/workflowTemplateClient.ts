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
};
