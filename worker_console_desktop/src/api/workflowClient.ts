import { ConversationSettings, defaultConversationSettings } from "./conversationClient";

export type WorkflowRun = {
  id: string;
  source_type: string;
  source_id: string | null;
  conversation_thread_id: string | null;
  playbook_run_id: string | null;
  task_run_id: string | null;
  workflow_graph_id: string | null;
  graph_execution: boolean;
  current_node_key: string | null;
  planned_next_nodes: string[];
  skipped_nodes: string[];
  retry_state: Record<string, unknown>;
  fallback_state: Record<string, unknown>;
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
  node_key: string | null;
  parent_node_key: string | null;
  dependency_state: Record<string, unknown>;
  status: string;
  duration_ms: number | null;
  error: string | null;
  created_at: string;
};

export type AgentMemorySnapshot = {
  id: string;
  workflow_run_id: string | null;
  node_key: string | null;
  memory_type: string;
  summary: string | null;
  created_at: string;
};

export type WorkflowPlannerResult = {
  valid: boolean;
  errors: string[];
  current_node: string | null;
  next_nodes: string[];
  skipped_nodes: string[];
  retry_paths: Record<string, unknown>[];
  fallback_paths: Record<string, unknown>[];
  condition_results: Record<string, unknown>[];
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
  getPlanner: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<WorkflowPlannerResult>(`/workflow-runs/${workflowRunId}/planner`, {}, settings),
  createReplay: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<{ id: string; replay_status: string; metadata: Record<string, unknown> }>(
      `/workflow-runs/${workflowRunId}/replay`,
      { method: "POST", body: JSON.stringify({ replay_reason: "Replay metadata requested from Desktop Console" }) },
      settings,
    ),
  pause: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<WorkflowRun>(`/workflow-runs/${workflowRunId}/pause`, { method: "POST", body: JSON.stringify({ reason: "Desktop Console pause" }) }, settings),
  resume: (workflowRunId: string, settings?: ConversationSettings) =>
    requestJson<WorkflowRun>(`/workflow-runs/${workflowRunId}/resume`, { method: "POST", body: JSON.stringify({ reason: "Desktop Console resume" }) }, settings),
};
