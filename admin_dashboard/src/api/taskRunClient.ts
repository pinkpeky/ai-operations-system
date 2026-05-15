import { AdminSettings, ApiList, JsonRecord, readAdminSettings, requestJson } from "./client";

export interface TaskRun {
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
  started_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  failed_at: string | null;
  current_step: number;
  error: string | null;
  input_payload: JsonRecord;
  output_payload: JsonRecord;
  metadata: JsonRecord;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskRunEvent {
  id: string;
  workspace_id: string;
  task_run_id: string;
  event_type: string;
  status: string | null;
  message: string | null;
  payload: JsonRecord;
  error: string | null;
  created_at: string;
}

export const taskRunClient = {
  listTaskRuns: (
    settings: AdminSettings = readAdminSettings(),
    filters: { status?: string; taskType?: string; sourceType?: string } = {},
  ) => {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", filters.status);
    if (filters.taskType) params.set("task_type", filters.taskType);
    if (filters.sourceType) params.set("source_type", filters.sourceType);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return requestJson<ApiList<TaskRun>>(`/task-runs${suffix}`, {}, settings);
  },
  getTaskRun: (taskRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}`, {}, settings),
  listEvents: (taskRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ task_run_id: string; items: TaskRunEvent[] }>(`/task-runs/${taskRunId}/events`, {}, settings),
  retry: (taskRunId: string, reason = "retry from Admin Dashboard", settings: AdminSettings = readAdminSettings()) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/retry`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }, settings),
  cancel: (taskRunId: string, reason = "cancel from Admin Dashboard", settings: AdminSettings = readAdminSettings()) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }, settings),
  resume: (taskRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/resume`, { method: "POST" }, settings),
};
