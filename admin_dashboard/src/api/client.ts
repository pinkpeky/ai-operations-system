export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type JsonRecord = Record<string, unknown>;

export interface AdminSettings {
  aiServerUrl: string;
  workspaceId: string;
  userId: string;
  refreshIntervalMs: number;
}

export interface ApiList<T = JsonRecord> {
  items?: T[];
  collections?: T[];
  workers?: T[];
  [key: string]: unknown;
}

export interface ApiErrorPayload {
  status?: number;
  message: string;
  details?: unknown;
}

const DEFAULT_REFRESH_INTERVAL_MS = 10000;

export const settingsStorageKeys = {
  aiServerUrl: "aiServerUrl",
  workspaceId: "workspaceId",
  userId: "userId",
} as const;

export function readAdminSettings(): AdminSettings {
  return {
    aiServerUrl:
      localStorage.getItem(settingsStorageKeys.aiServerUrl) ||
      import.meta.env.VITE_AI_SERVER_API ||
      "http://localhost:8000",
    workspaceId:
      localStorage.getItem(settingsStorageKeys.workspaceId) ||
      import.meta.env.VITE_WORKSPACE_ID ||
      "demo-workspace",
    userId:
      localStorage.getItem(settingsStorageKeys.userId) ||
      import.meta.env.VITE_USER_ID ||
      "demo-user",
    refreshIntervalMs: DEFAULT_REFRESH_INTERVAL_MS,
  };
}

export function writeAdminSettings(settings: AdminSettings): void {
  localStorage.setItem(settingsStorageKeys.aiServerUrl, settings.aiServerUrl);
  localStorage.setItem(settingsStorageKeys.workspaceId, settings.workspaceId);
  localStorage.setItem(settingsStorageKeys.userId, settings.userId);
}

function normalizePath(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return cleanPath.startsWith("/api/v1") ? cleanPath : `/api/v1${cleanPath}`;
}

function joinUrl(baseUrl: string, path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${baseUrl.replace(/\/+$/, "")}${normalizePath(path)}`;
}

export async function requestJson<T>(
  path: string,
  options: RequestInit = {},
  settings: AdminSettings = readAdminSettings(),
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("X-Workspace-Id", settings.workspaceId);
  headers.set("X-User-Id", settings.userId);
  const isFormDataBody = typeof FormData !== "undefined" && options.body instanceof FormData;
  if (!headers.has("Content-Type") && options.body && !isFormDataBody) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(joinUrl(settings.aiServerUrl, path), {
    ...options,
    headers,
  });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? String((payload as { detail?: unknown }).detail)
        : `Request failed with status ${response.status}`;
    const error = new Error(message) as Error & { payload?: ApiErrorPayload };
    error.payload = { status: response.status, message, details: payload };
    throw error;
  }
  return payload as T;
}

export async function safeRequest<T>(
  path: string,
  options: RequestInit = {},
  settings: AdminSettings = readAdminSettings(),
): Promise<{ ok: true; data: T } | { ok: false; error: string }> {
  try {
    return { ok: true, data: await requestJson<T>(path, options, settings) };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "API unavailable" };
  }
}

export function toItems<T = JsonRecord>(payload: ApiList<T> | T[] | unknown): T[] {
  if (Array.isArray(payload)) {
    return payload as T[];
  }
  if (!payload || typeof payload !== "object") {
    return [];
  }
  const record = payload as ApiList<T>;
  if (Array.isArray(record.items)) {
    return record.items;
  }
  if (Array.isArray(record.collections)) {
    return record.collections;
  }
  if (Array.isArray(record.workers)) {
    return record.workers;
  }
  return [];
}

export const healthApi = {
  get: (settings?: AdminSettings) => requestJson<JsonRecord>("/health", {}, settings),
};

export const workersApi = {
  list: (settings?: AdminSettings) => requestJson<ApiList<JsonRecord>>("/browser-workers", {}, settings),
  available: (settings?: AdminSettings) => requestJson<ApiList<JsonRecord>>("/browser-workers/available", {}, settings),
  healthSummary: (settings?: AdminSettings) =>
    requestJson<JsonRecord>("/browser-workers/health/summary", {}, settings),
};

export const browserRuntimeApi = {
  listSessions: (settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>("/browser-runtime/sessions", {}, settings),
  getSession: (sessionId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/browser-runtime/sessions/${sessionId}`, {}, settings),
  listEvents: (sessionId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/browser-runtime/sessions/${sessionId}/events`, {}, settings),
  listSnapshots: (sessionId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/browser-runtime/sessions/${sessionId}/snapshots`, {}, settings),
  createReplay: (sessionId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/browser-runtime/sessions/${sessionId}/replay`,
      {
        method: "POST",
        body: JSON.stringify({ metadata: { source: "admin_dashboard", replay: "metadata-only" } }),
      },
      settings,
    ),
  getReplay: (replayId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/browser-runtime/replays/${replayId}`, {}, settings),
  exportReplay: (replayId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/browser-runtime/replays/${replayId}/export`, {}, settings),
};

export const conversationsApi = {
  list: (settings?: AdminSettings) => requestJson<ApiList<JsonRecord>>("/conversations", {}, settings),
  get: (threadId: string, settings?: AdminSettings) => requestJson<JsonRecord>(`/conversations/${threadId}`, {}, settings),
  messages: (threadId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/conversations/${threadId}/messages`, {}, settings),
  events: (threadId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/conversations/${threadId}/events`, {}, settings),
};

export const commercialOperationsApi = {
  list: (status = "", settings?: AdminSettings) => {
    const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
    return requestJson<ApiList<JsonRecord>>(`/commercial-operations${suffix}`, {}, settings);
  },
  create: (payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      "/commercial-operations",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  get: (operationId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/commercial-operations/${encodeURIComponent(operationId)}`, {}, settings),
  update: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  planDraft: (operationId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/plan-draft`,
      {
        method: "POST",
      },
      settings,
    ),
};

export const tasksApi = {
  list: (status = "pending", settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/tasks?status=${encodeURIComponent(status)}`, {}, settings),
  events: (taskId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/tasks/${taskId}/events`, {}, settings),
  logs: (taskId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/tasks/${taskId}/logs`, {}, settings),
  summary: (settings?: AdminSettings) => requestJson<JsonRecord>("/observability/summary", {}, settings),
};

export const taskRunsApi = {
  list: (status = "", settings?: AdminSettings) => {
    const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
    return requestJson<ApiList<JsonRecord>>(`/task-runs${suffix}`, {}, settings);
  },
  events: (taskRunId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/task-runs/${taskRunId}/events`, {}, settings),
  retry: (taskRunId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/task-runs/${taskRunId}/retry`, { method: "POST", body: JSON.stringify({ reason: "retry from dashboard" }) }, settings),
  cancel: (taskRunId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/task-runs/${taskRunId}/cancel`, { method: "POST", body: JSON.stringify({ reason: "cancel from dashboard" }) }, settings),
  resume: (taskRunId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/task-runs/${taskRunId}/resume`, { method: "POST" }, settings),
  diagnostics: (taskRunId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/task-runs/${taskRunId}/diagnostics`, {}, settings),
  recover: (taskRunId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/task-runs/${taskRunId}/recover`, { method: "POST", body: JSON.stringify({ reason: "recover from dashboard" }) }, settings),
  schedulerHealth: (settings?: AdminSettings) => requestJson<JsonRecord>("/task-scheduler/health", {}, settings),
  schedulerScan: (settings?: AdminSettings) => requestJson<JsonRecord>("/task-scheduler/scan", { method: "POST" }, settings),
};

export const openclawApi = {
  health: (settings?: AdminSettings) => requestJson<JsonRecord>("/openclaw/health", {}, settings),
  capabilities: (settings?: AdminSettings) => requestJson<JsonRecord>("/openclaw/capabilities", {}, settings),
};

export const auditApi = {
  list: (
    filters: { eventType?: string; success?: string; targetType?: string },
    settings?: AdminSettings,
  ) => {
    const params = new URLSearchParams();
    if (filters.eventType) {
      params.set("event_type", filters.eventType);
    }
    if (filters.success) {
      params.set("success", filters.success);
    }
    if (filters.targetType) {
      params.set("target_type", filters.targetType);
    }
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return requestJson<ApiList<JsonRecord>>(`/browser/security/audit-logs${suffix}`, {}, settings);
  },
};

export const ragApi = {
  embeddingHealth: (settings?: AdminSettings) => requestJson<JsonRecord>("/rag/embedding/health", {}, settings),
  documents: (settings?: AdminSettings) => requestJson<ApiList<JsonRecord>>("/documents", {}, settings),
  documentDetail: (documentId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(`/documents/${encodeURIComponent(documentId)}`, {}, settings),
  collections: (settings?: AdminSettings) => requestJson<ApiList<JsonRecord>>("/rag/collections", {}, settings),
  uploadFile: (
    payload: {
      file: File;
      collectionName?: string;
      duplicateStrategy?: "skip" | "force_reingest";
      chunkSize?: number;
      chunkOverlap?: number;
    },
    settings?: AdminSettings,
  ) => {
    const form = new FormData();
    form.set("file", payload.file);
    if (payload.collectionName) {
      form.set("collection_name", payload.collectionName);
    }
    form.set("duplicate_strategy", payload.duplicateStrategy || "skip");
    form.set("chunk_size", String(payload.chunkSize ?? 500));
    form.set("chunk_overlap", String(payload.chunkOverlap ?? 50));
    return requestJson<JsonRecord>("/files/upload", { method: "POST", body: form }, settings);
  },
  ingestText: (payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      "/rag/ingest",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  reingestText: (payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      "/documents/reingest",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  deleteBySource: (sourceId: string, collectionName?: string, settings?: AdminSettings) => {
    const params = new URLSearchParams();
    if (collectionName) {
      params.set("collection_name", collectionName);
    }
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return requestJson<JsonRecord>(`/documents/by-source/${encodeURIComponent(sourceId)}${suffix}`, { method: "DELETE" }, settings);
  },
  search: (payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(
      "/rag/search",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  debug: (payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      "/rag/debug",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
};
