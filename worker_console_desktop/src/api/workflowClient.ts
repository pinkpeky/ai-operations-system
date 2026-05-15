import { ConversationSettings, defaultConversationSettings } from "./conversationClient";

export type WorkflowRun = {
  id: string;
  source_type: string;
  source_id: string | null;
  conversation_thread_id: string | null;
  playbook_run_id: string | null;
  task_run_id: string | null;
  status: string;
  current_step: number;
  variables: Record<string, unknown>;
  context: Record<string, unknown>;
  checkpoints: Record<string, unknown>[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type WorkflowStep = {
  id: string;
  workflow_run_id: string;
  step_index: number;
  step_name: string;
  step_type: string;
  status: string;
  duration_ms: number | null;
  error: string | null;
  created_at: string;
};

export type AgentMemorySnapshot = {
  id: string;
  workflow_run_id: string | null;
  memory_type: string;
  summary: string | null;
  created_at: string;
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
    throw new Error((await response.text()) || `Workflow API request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export const workflowClient = {
  listRuns: (settings?: ConversationSettings, status?: string) => {
    const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
    return requestJson<{ items: WorkflowRun[] }>(`/workflow-runs${suffix}`, {}, settings);
  },
  listSteps: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<{ workflow_run_id: string; items: WorkflowStep[] }>(`/workflow-runs/${workflowRunId}/steps`, {}, settings),
  listMemorySnapshots: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<{ workflow_run_id: string; items: AgentMemorySnapshot[] }>(`/workflow-runs/${workflowRunId}/memory-snapshots`, {}, settings),
  pause: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<WorkflowRun>(`/workflow-runs/${workflowRunId}/pause`, { method: "POST", body: JSON.stringify({ reason: "Desktop Console pause" }) }, settings),
  resume: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<WorkflowRun>(`/workflow-runs/${workflowRunId}/resume`, { method: "POST", body: JSON.stringify({ reason: "Desktop Console resume" }) }, settings),
};
