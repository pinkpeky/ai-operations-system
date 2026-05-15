import { ConversationSettings, defaultConversationSettings } from "./conversationClient";

export type OutputArtifact = {
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
  metadata: Record<string, unknown>;
  created_by: string | null;
  created_at: string;
  updated_at: string;
};

export type OutputArtifactExport = {
  artifact: OutputArtifact;
  generated_artifact?: OutputArtifact | null;
  format: string;
  export_path?: string;
  output_path?: string;
  content?: string | null;
  metadata?: Record<string, unknown>;
};

export type ArtifactLineage = {
  artifact: OutputArtifact;
  root_artifact_id: string | null;
  ancestors: OutputArtifact[];
  descendants: OutputArtifact[];
  relationships: Array<Record<string, unknown>>;
};

function normalizeApiBase(rawBase: string): string {
  const trimmed = rawBase.replace(/\/$/, "");
  return trimmed.endsWith("/api/v1") ? trimmed : `${trimmed}/api/v1`;
}

async function requestJson<T>(path: string, init?: RequestInit, settings: ConversationSettings = defaultConversationSettings): Promise<T> {
  const response = await fetch(`${normalizeApiBase(settings.aiServerUrl)}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-Id": settings.workspaceId,
      "X-User-Id": settings.userId,
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error((await response.text()) || `Output Artifact API request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export const outputArtifactClient = {
  listArtifacts: (settings?: ConversationSettings, filters: { artifactType?: string; sourceType?: string; threadId?: string; playbookRunId?: string; taskRunId?: string; workflowRunId?: string; artifactRole?: string; artifactStage?: string; retentionPolicy?: string } = {}) => {
    const params = new URLSearchParams();
    if (filters.artifactType) params.set("artifact_type", filters.artifactType);
    if (filters.sourceType) params.set("source_type", filters.sourceType);
    if (filters.threadId) params.set("thread_id", filters.threadId);
    if (filters.playbookRunId) params.set("playbook_run_id", filters.playbookRunId);
    if (filters.taskRunId) params.set("task_run_id", filters.taskRunId);
    if (filters.workflowRunId) params.set("workflow_run_id", filters.workflowRunId);
    if (filters.artifactRole) params.set("artifact_role", filters.artifactRole);
    if (filters.artifactStage) params.set("artifact_stage", filters.artifactStage);
    if (filters.retentionPolicy) params.set("retention_policy", filters.retentionPolicy);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return requestJson<{ items: OutputArtifact[] }>(`/output-artifacts${suffix}`, {}, settings);
  },
  createFromMessage: (messageId: string, settings?: ConversationSettings) =>
    requestJson<OutputArtifact>(`/output-artifacts/from-message/${messageId}`, { method: "POST" }, settings),
  createFromPlaybookRun: (runId: string, settings?: ConversationSettings) =>
    requestJson<{ items: OutputArtifact[] }>(`/output-artifacts/from-playbook-run/${runId}`, { method: "POST" }, settings),
  exportArtifact: (artifactId: string, format: "markdown" | "json" | "txt" = "markdown", settings?: ConversationSettings) =>
    requestJson<OutputArtifactExport>(`/output-artifacts/${artifactId}/export?format=${format}`, {}, settings),
  exportArtifactPipeline: (artifactId: string, format: "markdown" | "html" | "json" | "txt" | "bundle_zip" = "markdown", settings?: ConversationSettings) =>
    requestJson<OutputArtifactExport>(`/output-artifacts/${artifactId}/export`, {
      method: "POST",
      body: JSON.stringify({ format, metadata: { source: "worker_console_desktop" } }),
    }, settings),
  packageArtifact: (artifactId: string, settings?: ConversationSettings) =>
    requestJson<OutputArtifactExport>(`/output-artifacts/${artifactId}/package`, {
      method: "POST",
      body: JSON.stringify({ package_type: "bundle_zip", include_related: true, metadata: { source: "worker_console_desktop" } }),
    }, settings),
  getLineage: (artifactId: string, settings?: ConversationSettings) =>
    requestJson<ArtifactLineage>(`/output-artifacts/${artifactId}/lineage`, {}, settings),
};
