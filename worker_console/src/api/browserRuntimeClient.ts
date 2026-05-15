export type BrowserRuntimeSession = {
  id: string;
  workspace_id: string;
  worker_id: string;
  provider: string;
  browser: string;
  session_status: string;
  created_at: string;
  updated_at: string;
  last_activity_at: string | null;
  metadata: Record<string, unknown>;
  current_url: string | null;
  page_title: string | null;
  screenshot_path: string | null;
};

export type BrowserRuntimeEvent = {
  id: string;
  workspace_id: string;
  runtime_session_id: string;
  worker_id: string | null;
  event_type: string;
  status: string;
  message: string | null;
  payload: Record<string, unknown>;
  duration_ms: number | null;
  error: string | null;
  created_at: string;
};

export type BrowserRuntimeSnapshot = {
  id: string;
  workspace_id: string;
  runtime_session_id: string;
  snapshot_type: "page" | "screenshot" | "error" | "final" | string;
  url: string | null;
  page_title: string | null;
  html_path: string | null;
  text_path: string | null;
  screenshot_path: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type BrowserRuntimeReplay = {
  id: string;
  workspace_id: string;
  runtime_session_id: string;
  replay_status: string;
  replay_steps: Record<string, unknown>[];
  source_event_ids: string[];
  source_snapshot_ids: string[];
  metadata: Record<string, unknown>;
  created_at: string;
};

const API_BASE = (import.meta.env.VITE_AI_SERVER_API ?? "http://localhost:8000/api/v1").replace(/\/$/, "");
const WORKSPACE_ID = import.meta.env.VITE_WORKSPACE_ID ?? "demo-workspace";
const USER_ID = import.meta.env.VITE_USER_ID ?? "demo-user";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-Id": WORKSPACE_ID,
      "X-User-Id": USER_ID,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Browser Runtime API request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const browserRuntimeClient = {
  baseUrl: API_BASE,
  workspaceId: WORKSPACE_ID,
  listSessions: () => requestJson<{ items: BrowserRuntimeSession[] }>("/browser-runtime/sessions?status=active"),
  listEvents: (sessionId: string) =>
    requestJson<{ items: BrowserRuntimeEvent[] }>(`/browser-runtime/sessions/${sessionId}/events?limit=200`),
  listSnapshots: (sessionId: string) =>
    requestJson<{ items: BrowserRuntimeSnapshot[] }>(`/browser-runtime/sessions/${sessionId}/snapshots?limit=200`),
  createReplay: (sessionId: string) =>
    requestJson<BrowserRuntimeReplay>(`/browser-runtime/sessions/${sessionId}/replay`, {
      method: "POST",
      body: JSON.stringify({ metadata: { source: "worker_console" } }),
    }),
  exportReplay: (replayId: string) =>
    requestJson<{ replay: BrowserRuntimeReplay; export_path: string; export: Record<string, unknown> }>(
      `/browser-runtime/replays/${replayId}/export`,
    ),
  closeSession: (sessionId: string) =>
    requestJson<BrowserRuntimeSession>(`/browser-runtime/sessions/${sessionId}/close`, {
      method: "POST",
    }),
};
