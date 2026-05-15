import { ConversationSettings, defaultConversationSettings } from "./conversationClient";

export type TaskRun = {
  id: string;
  workspace_id: string;
  task_type: string;
  source_type: string;
  source_id: string | null;
  status: string;
  priority: string;
  retry_count: number;
  max_retries: number;
  scheduled_at: string | null;
  lease_expires_at: string | null;
  heartbeat_at: string | null;
  recovery_count: number;
  recoverable: boolean;
  suggested_action: string | null;
  current_step: number;
  error: string | null;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type TaskRunEvent = {
  id: string;
  task_run_id: string;
  event_type: string;
  status: string | null;
  message: string | null;
  payload: Record<string, unknown>;
  error: string | null;
  created_at: string;
};

export type TaskSchedulerHealth = {
  scheduler_name: string;
  status: string;
  heartbeat_at: string | null;
  last_scan_at: string | null;
  active_task_count: number;
  recovered_task_count: number;
  metadata: Record<string, unknown>;
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
    throw new Error((await response.text()) || `Task Run API request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export const taskRunClient = {
  listTaskRuns: (settings?: ConversationSettings, status?: string) => {
    const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
    return requestJson<{ items: TaskRun[] }>(`/task-runs${suffix}`, {}, settings);
  },
  getTaskRun: (taskRunId: string, settings?: ConversationSettings) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}`, {}, settings),
  listEvents: (taskRunId: string, settings?: ConversationSettings) =>
    requestJson<{ task_run_id: string; items: TaskRunEvent[] }>(`/task-runs/${taskRunId}/events`, {}, settings),
  retry: (taskRunId: string, settings?: ConversationSettings) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/retry`, { method: "POST", body: JSON.stringify({ reason: "retry from Desktop Console" }) }, settings),
  cancel: (taskRunId: string, settings?: ConversationSettings) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/cancel`, { method: "POST", body: JSON.stringify({ reason: "cancel from Desktop Console" }) }, settings),
  resume: (taskRunId: string, settings?: ConversationSettings) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/resume`, { method: "POST" }, settings),
  recover: (taskRunId: string, settings?: ConversationSettings) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/recover`, { method: "POST", body: JSON.stringify({ reason: "recover from Desktop Console" }) }, settings),
  schedulerHealth: (settings?: ConversationSettings) =>
    requestJson<TaskSchedulerHealth>("/task-scheduler/health", {}, settings),
};
