import { AdminSettings, ApiList, JsonRecord, readAdminSettings, requestJson } from "./client";

export interface OutputArtifact {
  id: string;
  workspace_id: string;
  thread_id: string | null;
  playbook_run_id: string | null;
  task_run_id: string | null;
  parent_artifact_id: string | null;
  root_artifact_id: string | null;
  source_task_run_id: string | null;
  source_playbook_run_id: string | null;
  source_conversation_id: string | null;
  source_runtime_session_id: string | null;
  workflow_run_id: string | null;
  workflow_step_id: string | null;
  checkpoint_id: string | null;
  memory_snapshot_id: string | null;
  workflow_template_id: string | null;
  workflow_template_version_id: string | null;
  workflow_template_run_id: string | null;
  producing_node_key: string | null;
  replay_source: string | null;
  trace_id: string | null;
  replay_session_id: string | null;
  diagnostic_reference: string | null;
  graph_lineage: JsonRecord;
  source_type: string;
  artifact_type: string;
  artifact_role: string | null;
  artifact_stage: string;
  title: string;
  summary: string | null;
  content: string | null;
  file_path: string | null;
  mime_type: string | null;
  status: string;
  generated_by: string | null;
  exportable: boolean;
  retention_policy: string;
  expires_at: string | null;
  metadata: JsonRecord;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface OutputArtifactExport {
  artifact: OutputArtifact;
  generated_artifact?: OutputArtifact | null;
  format: string;
  export_path?: string;
  output_path?: string;
  content?: string | null;
  metadata?: JsonRecord;
}

export interface ArtifactRelationship {
  id: string;
  parent_artifact_id: string;
  child_artifact_id: string;
  relationship_type: string;
  metadata: JsonRecord;
  created_at: string;
  updated_at: string;
}

export interface ArtifactLineage {
  artifact: OutputArtifact;
  root_artifact_id: string | null;
  ancestors: OutputArtifact[];
  descendants: OutputArtifact[];
  relationships: ArtifactRelationship[];
}

export const outputArtifactClient = {
  listArtifacts: (
    settings: AdminSettings = readAdminSettings(),
    filters: {
      artifactType?: string;
      sourceType?: string;
      threadId?: string;
      playbookRunId?: string;
      taskRunId?: string;
      artifactRole?: string;
      artifactStage?: string;
      retentionPolicy?: string;
      archived?: boolean;
      exportable?: boolean;
      workflowRunId?: string;
      workflowStepId?: string;
      workflowTemplateId?: string;
      workflowTemplateVersionId?: string;
      workflowTemplateRunId?: string;
    } = {},
  ) => {
    const params = new URLSearchParams();
    if (filters.artifactType) params.set("artifact_type", filters.artifactType);
    if (filters.sourceType) params.set("source_type", filters.sourceType);
    if (filters.threadId) params.set("thread_id", filters.threadId);
    if (filters.playbookRunId) params.set("playbook_run_id", filters.playbookRunId);
    if (filters.taskRunId) params.set("task_run_id", filters.taskRunId);
    if (filters.artifactRole) params.set("artifact_role", filters.artifactRole);
    if (filters.artifactStage) params.set("artifact_stage", filters.artifactStage);
    if (filters.retentionPolicy) params.set("retention_policy", filters.retentionPolicy);
    if (filters.archived !== undefined) params.set("archived", String(filters.archived));
    if (filters.exportable !== undefined) params.set("exportable", String(filters.exportable));
    if (filters.workflowRunId) params.set("workflow_run_id", filters.workflowRunId);
    if (filters.workflowStepId) params.set("workflow_step_id", filters.workflowStepId);
    if (filters.workflowTemplateId) params.set("workflow_template_id", filters.workflowTemplateId);
    if (filters.workflowTemplateVersionId) params.set("workflow_template_version_id", filters.workflowTemplateVersionId);
    if (filters.workflowTemplateRunId) params.set("workflow_template_run_id", filters.workflowTemplateRunId);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return requestJson<ApiList<OutputArtifact>>(`/output-artifacts${suffix}`, {}, settings);
  },
  getArtifact: (artifactId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<OutputArtifact>(`/output-artifacts/${artifactId}`, {}, settings),
  createFromMessage: (messageId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<OutputArtifact>(`/output-artifacts/from-message/${messageId}`, { method: "POST" }, settings),
  createFromPlaybookRun: (runId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<OutputArtifact>>(`/output-artifacts/from-playbook-run/${runId}`, { method: "POST" }, settings),
  exportArtifact: (
    artifactId: string,
    format: "markdown" | "json" | "txt" = "markdown",
    settings: AdminSettings = readAdminSettings(),
  ) => requestJson<OutputArtifactExport>(`/output-artifacts/${artifactId}/export?format=${format}`, {}, settings),
  exportArtifactPipeline: (
    artifactId: string,
    format: "markdown" | "html" | "json" | "txt" | "bundle_zip" | "report_package" = "markdown",
    settings: AdminSettings = readAdminSettings(),
  ) => requestJson<OutputArtifactExport>(`/output-artifacts/${artifactId}/export`, {
    method: "POST",
    body: JSON.stringify({ format, metadata: { source: "admin_dashboard" } }),
  }, settings),
  packageArtifact: (
    artifactId: string,
    settings: AdminSettings = readAdminSettings(),
  ) => requestJson<OutputArtifactExport>(`/output-artifacts/${artifactId}/package`, {
    method: "POST",
    body: JSON.stringify({ package_type: "bundle_zip", include_related: true, metadata: { source: "admin_dashboard" } }),
  }, settings),
  getLineage: (artifactId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<ArtifactLineage>(`/output-artifacts/${artifactId}/lineage`, {}, settings),
  getRelationships: (artifactId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<ArtifactRelationship>>(`/output-artifacts/${artifactId}/relationships`, {}, settings),
  cleanupPreview: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ workspace_id: string; count: number; items: JsonRecord[]; execution_mode: string }>(`/output-artifacts/cleanup/preview`, {
      method: "POST",
      body: JSON.stringify({ limit: 100 }),
    }, settings),
  deleteArtifact: (artifactId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<OutputArtifact>(`/output-artifacts/${artifactId}`, { method: "DELETE" }, settings),
};
