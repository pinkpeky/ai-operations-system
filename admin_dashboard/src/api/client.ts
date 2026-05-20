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
  approvals: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/approvals`, {}, settings),
  createApproval: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  approveApproval: (operationId: string, approvalId: string, reviewerNotes = "Approved from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectApproval: (operationId: string, approvalId: string, reviewerNotes = "Rejected from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  cancelApproval: (operationId: string, approvalId: string, reviewerNotes = "Cancelled from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/cancel`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  dryRuns: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/dry-runs`, {}, settings),
  createDryRun: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/dry-runs`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  completeDryRun: (operationId: string, dryRunId: string, resultSummary = "Completed from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/complete`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  failDryRun: (operationId: string, dryRunId: string, failureReason = "Failed from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  cancelDryRun: (operationId: string, dryRunId: string, resultSummary = "Cancelled from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/cancel`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  contentDrafts: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/content-drafts`, {}, settings),
  createContentDraft: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  generateContentDraft: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/generate-rag`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateContentDraft: (operationId: string, draftId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyContentDraft: (operationId: string, draftId: string, reviewerNotes = "Ready for review from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveContentDraft: (operationId: string, draftId: string, reviewerNotes = "Approved from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectContentDraft: (operationId: string, draftId: string, reviewerNotes = "Rejected from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  archiveContentDraft: (operationId: string, draftId: string, reviewerNotes = "Archived from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  assetRequests: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/asset-requests`, {}, settings),
  createAssetRequest: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  generateAssetRequest: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/generate-rag`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateAssetRequest: (operationId: string, assetRequestId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyAssetRequest: (operationId: string, assetRequestId: string, reviewerNotes = "Ready for review from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveAssetRequest: (operationId: string, assetRequestId: string, reviewerNotes = "Approved from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectAssetRequest: (operationId: string, assetRequestId: string, reviewerNotes = "Rejected from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  prepareAssetRequest: (operationId: string, assetRequestId: string, resultSummary = "Prepared from Commercial Ops; no ComfyUI job started.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/prepare`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  failAssetRequest: (operationId: string, assetRequestId: string, failureReason = "Failed from Commercial Ops; operator review required.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  archiveAssetRequest: (operationId: string, assetRequestId: string, reviewerNotes = "Archived from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  comfyuiHandoffs: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs`, {}, settings),
  createComfyuiHandoff: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateComfyuiHandoff: (operationId: string, handoffId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyComfyuiHandoff: (operationId: string, handoffId: string, reviewerNotes = "Ready for review from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveComfyuiHandoff: (operationId: string, handoffId: string, reviewerNotes = "Approved from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectComfyuiHandoff: (operationId: string, handoffId: string, reviewerNotes = "Rejected from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  prepareComfyuiHandoff: (operationId: string, handoffId: string, resultSummary = "Prepared from Commercial Ops; no ComfyUI job submitted.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/prepare`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  failComfyuiHandoff: (operationId: string, handoffId: string, failureReason = "Failed from Commercial Ops; operator review required.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  archiveComfyuiHandoff: (operationId: string, handoffId: string, reviewerNotes = "Archived from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  comfyuiPreflights: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights`, {}, settings),
  createComfyuiPreflight: (operationId: string, handoffId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-handoffs/${encodeURIComponent(handoffId)}/preflights`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateComfyuiPreflight: (operationId: string, preflightId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  checkComfyuiPreflight: (operationId: string, preflightId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}/check`,
      {
        method: "POST",
        body: JSON.stringify({}),
      },
      settings,
    ),
  failComfyuiPreflight: (operationId: string, preflightId: string, failureReason = "Failed from Commercial Ops preflight; operator review required.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  archiveComfyuiPreflight: (operationId: string, preflightId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-preflights/${encodeURIComponent(preflightId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({}),
      },
      settings,
    ),
  comfyuiAdapterConfigs: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs`, {}, settings),
  createComfyuiAdapterConfig: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateComfyuiAdapterConfig: (operationId: string, configId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  validateComfyuiAdapterConfig: (operationId: string, configId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}/validate`,
      {
        method: "POST",
        body: JSON.stringify({}),
      },
      settings,
    ),
  failComfyuiAdapterConfig: (
    operationId: string,
    configId: string,
    failureReason = "Failed from Commercial Ops adapter config; maintainer review required.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  archiveComfyuiAdapterConfig: (operationId: string, configId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/comfyui-adapter-configs/${encodeURIComponent(configId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({}),
      },
      settings,
    ),
  deliverables: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/deliverables`, {}, settings),
  createDeliverable: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateDeliverable: (operationId: string, deliverableId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyDeliverable: (operationId: string, deliverableId: string, reviewerNotes = "Ready for review from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveDeliverable: (operationId: string, deliverableId: string, reviewerNotes = "Approved from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectDeliverable: (operationId: string, deliverableId: string, reviewerNotes = "Rejected from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  packageDeliverable: (operationId: string, deliverableId: string, resultSummary = "Packaged for Output Library handoff from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/package`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  failDeliverable: (operationId: string, deliverableId: string, failureReason = "Failed from Commercial Ops; operator review required.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  archiveDeliverable: (operationId: string, deliverableId: string, reviewerNotes = "Archived from Commercial Ops.", settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  evidenceSnapshots: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots`, {}, settings),
  createEvidenceSnapshot: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  generateEvidenceSnapshot: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/generate-rag`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateEvidenceSnapshot: (operationId: string, snapshotId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyEvidenceSnapshot: (
    operationId: string,
    snapshotId: string,
    reviewerNotes = "Ready for review from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveEvidenceSnapshot: (
    operationId: string,
    snapshotId: string,
    reviewerNotes = "Approved from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectEvidenceSnapshot: (
    operationId: string,
    snapshotId: string,
    reviewerNotes = "Rejected from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  archiveEvidenceSnapshot: (
    operationId: string,
    snapshotId: string,
    reviewerNotes = "Archived from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  executionRequests: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/execution-requests`, {}, settings),
  createExecutionRequest: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateExecutionRequest: (operationId: string, executionRequestId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes = "Ready for review from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes = "Approved as metadata-only execution request from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes = "Rejected from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  prepareExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    resultSummary = "Prepared for future guarded runtime adapter from Commercial Ops; no execution occurred.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/prepare`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  failExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    failureReason = "Failed from Commercial Ops; no external execution occurred.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  cancelExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes = "Cancelled from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/cancel`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  archiveExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes = "Archived from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  executionRuns: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/execution-runs`, {}, settings),
  createExecutionRun: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateExecutionRun: (operationId: string, executionRunId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  startExecutionRun: (
    operationId: string,
    executionRunId: string,
    operatorNotes = "Started from Commercial Ops; no external runtime was called.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/start`,
      {
        method: "POST",
        body: JSON.stringify({ operator_notes: operatorNotes }),
      },
      settings,
    ),
  succeedExecutionRun: (
    operationId: string,
    executionRunId: string,
    resultSummary = "Succeeded from Commercial Ops metadata run.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/succeed`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  failExecutionRun: (
    operationId: string,
    executionRunId: string,
    failureReason = "Failed from Commercial Ops metadata run; operator review required.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/fail`,
      {
        method: "POST",
        body: JSON.stringify({ failure_reason: failureReason }),
      },
      settings,
    ),
  retryExecutionRun: (
    operationId: string,
    executionRunId: string,
    operatorNotes = "Retry requested from Commercial Ops after human review.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/retry`,
      {
        method: "POST",
        body: JSON.stringify({ operator_notes: operatorNotes }),
      },
      settings,
    ),
  cancelExecutionRun: (
    operationId: string,
    executionRunId: string,
    operatorNotes = "Cancelled from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/cancel`,
      {
        method: "POST",
        body: JSON.stringify({ operator_notes: operatorNotes }),
      },
      settings,
    ),
  archiveExecutionRun: (
    operationId: string,
    executionRunId: string,
    operatorNotes = "Archived from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ operator_notes: operatorNotes }),
      },
      settings,
    ),
  results: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/results`, {}, settings),
  createResult: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateResult: (operationId: string, resultId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyResult: (
    operationId: string,
    resultId: string,
    reviewerNotes = "Ready for review from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveResult: (
    operationId: string,
    resultId: string,
    reviewerNotes = "Approved from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectResult: (
    operationId: string,
    resultId: string,
    reviewerNotes = "Rejected from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  archiveResult: (
    operationId: string,
    resultId: string,
    reviewerNotes = "Archived from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  monitoringObservations: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations`,
      {},
      settings,
    ),
  createMonitoringObservation: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateMonitoringObservation: (
    operationId: string,
    observationId: string,
    payload: JsonRecord,
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyMonitoringObservation: (
    operationId: string,
    observationId: string,
    reviewerNotes = "Ready for review from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveMonitoringObservation: (
    operationId: string,
    observationId: string,
    reviewerNotes = "Approved from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectMonitoringObservation: (
    operationId: string,
    observationId: string,
    reviewerNotes = "Rejected from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  archiveMonitoringObservation: (
    operationId: string,
    observationId: string,
    reviewerNotes = "Archived from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  optimizationDecisions: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions`,
      {},
      settings,
    ),
  createOptimizationDecision: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  updateOptimizationDecision: (
    operationId: string,
    optimizationDecisionId: string,
    payload: JsonRecord,
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyOptimizationDecision: (
    operationId: string,
    optimizationDecisionId: string,
    reviewerNotes = "Ready for review from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveOptimizationDecision: (
    operationId: string,
    optimizationDecisionId: string,
    reviewerNotes = "Approved from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectOptimizationDecision: (
    operationId: string,
    optimizationDecisionId: string,
    reviewerNotes = "Rejected from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  archiveOptimizationDecision: (
    operationId: string,
    optimizationDecisionId: string,
    reviewerNotes = "Archived from Commercial Ops.",
    settings?: AdminSettings,
  ) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/archive`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  links: (operationId: string, settings?: AdminSettings) =>
    requestJson<ApiList<JsonRecord>>(`/commercial-operations/${encodeURIComponent(operationId)}/links`, {}, settings),
  createLink: (operationId: string, payload: JsonRecord, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/links`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  deleteLink: (operationId: string, linkId: string, settings?: AdminSettings) =>
    requestJson<JsonRecord>(
      `/commercial-operations/${encodeURIComponent(operationId)}/links/${encodeURIComponent(linkId)}`,
      {
        method: "DELETE",
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
