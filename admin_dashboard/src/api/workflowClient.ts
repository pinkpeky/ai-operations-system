import { AdminSettings, ApiList, JsonRecord, readAdminSettings, requestJson } from "./client";

export interface WorkflowRun {
  id: string;
  workspace_id: string;
  source_type: string;
  source_id: string | null;
  conversation_thread_id: string | null;
  playbook_run_id: string | null;
  task_run_id: string | null;
  status: string;
  current_step: number;
  variables: JsonRecord;
  context: JsonRecord;
  checkpoints: JsonRecord[];
  metadata: JsonRecord;
  started_at: string | null;
  completed_at: string | null;
  paused_at: string | null;
  resumed_at: string | null;
  failed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkflowStep {
  id: string;
  workflow_run_id: string;
  step_index: number;
  step_name: string;
  step_type: string;
  status: string;
  input_payload: JsonRecord;
  output_payload: JsonRecord;
  error: string | null;
  duration_ms: number | null;
  created_at: string;
}

export interface WorkflowCheckpoint {
  id: string;
  workflow_run_id: string;
  checkpoint_name: string;
  checkpoint_type: string;
  state_payload: JsonRecord;
  created_by: string | null;
  created_at: string;
}

export interface AgentMemorySnapshot {
  id: string;
  workflow_run_id: string | null;
  memory_type: string;
  summary: string | null;
  memory_payload: JsonRecord;
  source_event_ids: string[];
  source_artifact_ids: string[];
  created_at: string;
}

export const workflowClient = {
  listRuns: (
    settings: AdminSettings = readAdminSettings(),
    filters: { status?: string; sourceType?: string; taskRunId?: string; playbookRunId?: string; conversationThreadId?: string } = {},
  ) => {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", filters.status);
    if (filters.sourceType) params.set("source_type", filters.sourceType);
    if (filters.taskRunId) params.set("task_run_id", filters.taskRunId);
    if (filters.playbookRunId) params.set("playbook_run_id", filters.playbookRunId);
    if (filters.conversationThreadId) params.set("conversation_thread_id", filters.conversationThreadId);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return requestJson<ApiList<WorkflowRun>>(`/workflow-runs${suffix}`, {}, settings);
  },
  getRun: (workflowRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowRun>(`/workflow-runs/${workflowRunId}`, {}, settings),
  listSteps: (workflowRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ workflow_run_id: string; items: WorkflowStep[] }>(`/workflow-runs/${workflowRunId}/steps`, {}, settings),
  listCheckpoints: (workflowRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ workflow_run_id: string; items: WorkflowCheckpoint[] }>(`/workflow-runs/${workflowRunId}/checkpoints`, {}, settings),
  listMemorySnapshots: (workflowRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ workflow_run_id: string; items: AgentMemorySnapshot[] }>(`/workflow-runs/${workflowRunId}/memory-snapshots`, {}, settings),
  pause: (workflowRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowRun>(`/workflow-runs/${workflowRunId}/pause`, {
      method: "POST",
      body: JSON.stringify({ reason: "Manual pause from Admin Dashboard" }),
    }, settings),
  resume: (workflowRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowRun>(`/workflow-runs/${workflowRunId}/resume`, {
      method: "POST",
      body: JSON.stringify({ reason: "Manual resume from Admin Dashboard" }),
    }, settings),
  createCheckpoint: (workflowRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<WorkflowCheckpoint>(`/workflow-runs/${workflowRunId}/checkpoints`, {
      method: "POST",
      body: JSON.stringify({ checkpoint_name: "manual-admin-checkpoint", checkpoint_type: "manual" }),
    }, settings),
};
