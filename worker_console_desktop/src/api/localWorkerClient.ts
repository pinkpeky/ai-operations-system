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

export const DEFAULT_LOCAL_WORKER_API = (import.meta.env.VITE_LOCAL_WORKER_API ?? "http://127.0.0.1:9100").replace(
  /\/$/,
  "",
);

async function requestJson<T>(baseUrl: string, path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
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

export function createLocalWorkerClient(baseUrl = DEFAULT_LOCAL_WORKER_API) {
  const normalizedBaseUrl = baseUrl.replace(/\/$/, "");

  return {
    baseUrl: normalizedBaseUrl,
    getStatus: () => requestJson<WorkerStatus>(normalizedBaseUrl, "/local/status"),
    getHealth: () => requestJson<WorkerHealth>(normalizedBaseUrl, "/local/health"),
    getLogs: (lines = 200) => requestJson<WorkerLogs>(normalizedBaseUrl, `/local/logs?lines=${lines}`),
    startRuntime: () => requestJson<WorkerStatus>(normalizedBaseUrl, "/local/runtime/start", { method: "POST" }),
    stopRuntime: () => requestJson<WorkerStatus>(normalizedBaseUrl, "/local/runtime/stop", { method: "POST" }),
    restartRuntime: () => requestJson<WorkerStatus>(normalizedBaseUrl, "/local/runtime/restart", { method: "POST" }),
    startHeartbeat: () => requestJson<WorkerStatus>(normalizedBaseUrl, "/local/heartbeat/start", { method: "POST" }),
    stopHeartbeat: () => requestJson<WorkerStatus>(normalizedBaseUrl, "/local/heartbeat/stop", { method: "POST" }),
  };
}

export type LocalWorkerClient = ReturnType<typeof createLocalWorkerClient>;

export const localWorkerClient = createLocalWorkerClient(DEFAULT_LOCAL_WORKER_API);
