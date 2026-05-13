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
  host?: string;
  port?: number;
  localhost_only?: boolean;
};

export type WorkerLogs = {
  lines: string[];
};

const API_BASE = (import.meta.env.VITE_LOCAL_WORKER_API ?? "http://127.0.0.1:9100").replace(/\/$/, "");

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
};
