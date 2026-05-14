import { AdminSettings, ApiList, JsonRecord, readAdminSettings, requestJson } from "./client";

export interface OutputArtifact {
  id: string;
  workspace_id: string;
  thread_id: string | null;
  playbook_run_id: string | null;
  source_type: string;
  artifact_type: string;
  title: string;
  summary: string | null;
  content: string | null;
  file_path: string | null;
  mime_type: string | null;
  status: string;
  metadata: JsonRecord;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface OutputArtifactExport {
  artifact: OutputArtifact;
  format: string;
  export_path: string;
  content: string;
}

export const outputArtifactClient = {
  listArtifacts: (
    settings: AdminSettings = readAdminSettings(),
    filters: { artifactType?: string; sourceType?: string; threadId?: string; playbookRunId?: string } = {},
  ) => {
    const params = new URLSearchParams();
    if (filters.artifactType) params.set("artifact_type", filters.artifactType);
    if (filters.sourceType) params.set("source_type", filters.sourceType);
    if (filters.threadId) params.set("thread_id", filters.threadId);
    if (filters.playbookRunId) params.set("playbook_run_id", filters.playbookRunId);
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
  deleteArtifact: (artifactId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<OutputArtifact>(`/output-artifacts/${artifactId}`, { method: "DELETE" }, settings),
};
