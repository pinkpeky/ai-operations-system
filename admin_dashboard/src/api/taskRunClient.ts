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
  lease_owner: string | null;
  lease_token: string | null;
  lease_expires_at: string | null;
  heartbeat_at: string | null;
  recovery_count: number;
  last_recovered_at: string | null;
  recovery_reason: string | null;
  failure_category: string | null;
  failure_reason: string | null;
  recoverable: boolean;
  suggested_action: string | null;
  last_event_summary: string | null;
  input_payload: JsonRecord;
  output_payload: JsonRecord;
  metadata: JsonRecord;
  workflow_run_id: string | null;
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

export interface TaskRunDiagnostics {
  task_run_id: string;
  status: string;
  failure_category: string | null;
  failure_reason: string | null;
  recoverable: boolean;
  suggested_action: string | null;
  last_event_summary: string | null;
  lease_expired: boolean;
  scheduled_due: boolean;
  retry_count: number;
  max_retries: number;
}

export interface TaskSchedulerHealth {
  id: string | null;
  workspace_id: string;
  scheduler_name: string;
  status: string;
  heartbeat_at: string | null;
  last_scan_at: string | null;
  active_task_count: number;
  recovered_task_count: number;
  metadata: JsonRecord;
  created_at: string | null;
  updated_at: string | null;
}

export const taskRunClient = {
  listTaskRuns: (
    settings: AdminSettings = readAdminSettings(),
    filters: { status?: string; taskType?: string; sourceType?: string; recoverable?: boolean; leaseExpired?: boolean; scheduledDue?: boolean } = {},
  ) => {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", filters.status);
    if (filters.taskType) params.set("task_type", filters.taskType);
    if (filters.sourceType) params.set("source_type", filters.sourceType);
    if (filters.recoverable !== undefined) params.set("recoverable", String(filters.recoverable));
    if (filters.leaseExpired !== undefined) params.set("lease_expired", String(filters.leaseExpired));
    if (filters.scheduledDue !== undefined) params.set("scheduled_due", String(filters.scheduledDue));
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
  recover: (taskRunId: string, reason = "manual recover from Admin Dashboard", settings: AdminSettings = readAdminSettings()) =>
    requestJson<TaskRun>(`/task-runs/${taskRunId}/recover`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }, settings),
  diagnostics: (taskRunId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<TaskRunDiagnostics>(`/task-runs/${taskRunId}/diagnostics`, {}, settings),
  schedulerHealth: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<TaskSchedulerHealth>("/task-scheduler/health", {}, settings),
  schedulerScan: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ scheduler: TaskSchedulerHealth; recovered_count: number; details: JsonRecord }>(
      "/task-scheduler/scan",
      { method: "POST" },
      settings,
    ),
};
