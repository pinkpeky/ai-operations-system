import { ConversationSettings, defaultConversationSettings } from "./conversationClient";

export type OutputArtifact = {
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
  metadata: Record<string, unknown>;
  created_by: string | null;
  created_at: string;
  updated_at: string;
};

export type OutputArtifactExport = {
  artifact: OutputArtifact;
  format: string;
  export_path: string;
  content: string;
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
  listArtifacts: (settings?: ConversationSettings, filters: { artifactType?: string; sourceType?: string; threadId?: string; playbookRunId?: string } = {}) => {
    const params = new URLSearchParams();
    if (filters.artifactType) params.set("artifact_type", filters.artifactType);
    if (filters.sourceType) params.set("source_type", filters.sourceType);
    if (filters.threadId) params.set("thread_id", filters.threadId);
    if (filters.playbookRunId) params.set("playbook_run_id", filters.playbookRunId);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return requestJson<{ items: OutputArtifact[] }>(`/output-artifacts${suffix}`, {}, settings);
  },
  createFromMessage: (messageId: string, settings?: ConversationSettings) =>
    requestJson<OutputArtifact>(`/output-artifacts/from-message/${messageId}`, { method: "POST" }, settings),
  createFromPlaybookRun: (runId: string, settings?: ConversationSettings) =>
    requestJson<{ items: OutputArtifact[] }>(`/output-artifacts/from-playbook-run/${runId}`, { method: "POST" }, settings),
  exportArtifact: (artifactId: string, format: "markdown" | "json" | "txt" = "markdown", settings?: ConversationSettings) =>
    requestJson<OutputArtifactExport>(`/output-artifacts/${artifactId}/export?format=${format}`, {}, settings),
};
