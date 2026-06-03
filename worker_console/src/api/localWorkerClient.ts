export type WorkerStatus = {
  worker_id: string | null;
  worker_name: string | null;
  workspace_id: string | null;
  server_url: string | null;
  worker_base_url: string | null;
  runtime_port: number | null;
  registered: boolean;
  runtime_running: boolean;
  heartbeat_running: boolean;
  metric_dispatch_scheduler_running?: boolean;
  metric_dispatch_scheduler_status?: string | null;
  metric_dispatch_scheduler_next_poll_at?: string | null;
  metric_dispatch_scheduler_last_error?: string | null;
  current_status: string | null;
  last_heartbeat_at: string | null;
  last_error: string | null;
  openclaw_enabled: boolean;
  browser_enabled: boolean;
};

export type WorkerHealth = {
  success: boolean;
  runtime_running: boolean;
  heartbeat_running: boolean;
  metric_dispatch_scheduler_running?: boolean;
  host?: string;
  port?: number;
  localhost_only?: boolean;
};

export type MetricDispatchLocalSchedulerState = {
  configured: boolean;
  running: boolean;
  scheduler_status: string;
  scheduler_enabled: boolean;
  customer_machine_id?: string | null;
  workspace_id?: string | null;
  next_poll_at?: string | null;
  recommended_poll_interval_seconds?: number;
  tick_status?: string | null;
  last_tick_at?: string | null;
  last_poll_status?: string | null;
  last_error?: string | null;
  client_timer_payload?: Record<string, unknown>;
  notification_records?: Record<string, unknown>[];
  history?: Record<string, unknown>[];
  last_poll_result?: Record<string, unknown>;
};

export type WorkerLogs = {
  lines: string[];
};

export type LocalWorkerOpenClawHealth = {
  success: boolean;
  provider: string;
  reachable: boolean;
  enabled: boolean;
  mock: boolean;
  version?: string | null;
  error?: string | null;
};

export type LocalWorkerOpenClawCapabilities = {
  success: boolean;
  provider: string;
  mock: boolean;
  capabilities: Record<string, unknown>;
  actions: string[];
  error?: string | null;
};

export type LocalWorkerOpenClawProviderDiagnostics = {
  success: boolean;
  provider: string;
  enabled: boolean;
  mock: boolean;
  configured: boolean;
  readiness_status: string;
  base_url_configured: boolean;
  api_key_configured: boolean;
  timeout_seconds?: number | null;
  paths: Record<string, string>;
  missing_config: string[];
  required_env: string[];
  next_actions: string[];
  secret_fields_redacted: string[];
  contract: "openclaw_provider_configuration_preflight" | string;
};

export type LocalWorkerOpenClawActionResponse = {
  success: boolean;
  action_type: string;
  output_payload: Record<string, unknown>;
  error?: string | null;
  duration_ms: number;
  provider: string;
  mock: boolean;
};

const API_BASE = (import.meta.env.VITE_LOCAL_WORKER_API ?? "/local-worker").replace(/\/$/, "");

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Worker API request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const localWorkerClient = {
  baseUrl: API_BASE,
  getStatus: () => requestJson<WorkerStatus>("/local/status"),
  getHealth: () => requestJson<WorkerHealth>("/local/health"),
  getLogs: (lines = 200) => requestJson<WorkerLogs>(`/local/logs?lines=${lines}`),
  startRuntime: () => requestJson<WorkerStatus>("/local/runtime/start", { method: "POST" }),
  stopRuntime: () => requestJson<WorkerStatus>("/local/runtime/stop", { method: "POST" }),
  restartRuntime: () => requestJson<WorkerStatus>("/local/runtime/restart", { method: "POST" }),
  startHeartbeat: () => requestJson<WorkerStatus>("/local/heartbeat/start", { method: "POST" }),
  stopHeartbeat: () => requestJson<WorkerStatus>("/local/heartbeat/stop", { method: "POST" }),
  getMetricDispatchScheduler: () => requestJson<MetricDispatchLocalSchedulerState>("/local/metric-dispatch-scheduler"),
  configureMetricDispatchScheduler: (payload: Record<string, unknown>) =>
    requestJson<MetricDispatchLocalSchedulerState>("/local/metric-dispatch-scheduler/configure", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  tickMetricDispatchScheduler: (force = false) =>
    requestJson<MetricDispatchLocalSchedulerState>("/local/metric-dispatch-scheduler/tick", {
      method: "POST",
      body: JSON.stringify({ force }),
    }),
  startMetricDispatchScheduler: () =>
    requestJson<MetricDispatchLocalSchedulerState>("/local/metric-dispatch-scheduler/start", { method: "POST" }),
  stopMetricDispatchScheduler: () =>
    requestJson<MetricDispatchLocalSchedulerState>("/local/metric-dispatch-scheduler/stop", { method: "POST" }),
  clearMetricDispatchScheduler: () =>
    requestJson<MetricDispatchLocalSchedulerState>("/local/metric-dispatch-scheduler/clear", { method: "POST" }),
  openClawHealth: () => requestJson<LocalWorkerOpenClawHealth>("/openclaw/health"),
  openClawCapabilities: () => requestJson<LocalWorkerOpenClawCapabilities>("/openclaw/capabilities"),
  openClawProviderDiagnostics: () =>
    requestJson<LocalWorkerOpenClawProviderDiagnostics>("/openclaw/provider-diagnostics"),
  executeOpenClawAction: (payload: {
    action_type: string;
    target?: string | null;
    input_payload?: Record<string, unknown>;
    profile_id?: string | null;
    browser_session_id?: string | null;
    metadata?: Record<string, unknown>;
  }) =>
    requestJson<LocalWorkerOpenClawActionResponse>("/openclaw/actions", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
