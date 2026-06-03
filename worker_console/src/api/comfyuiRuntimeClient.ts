import { conversationClient, defaultConversationSettings, type ConversationSettings } from "./conversationClient";

export type ComfyUIRuntimeHealth = {
  success: boolean;
  provider: string;
  enabled: boolean;
  reachable: boolean;
  guarded: boolean;
  mock: boolean;
  network_allowed: boolean;
  external_request_attempted: boolean;
  runtime_calls_enabled: boolean;
  read_only_probe_enabled: boolean;
  read_only_probe_attempted: boolean;
  health_path?: string | null;
  probe_status_code?: number | null;
  probe_latency_ms?: number | null;
  base_url: string;
  error?: string | null;
};

export type ComfyUIRuntimeDiagnostics = {
  success: boolean;
  provider: string;
  enabled: boolean;
  network_allowed: boolean;
  read_only_probe_enabled: boolean;
  base_url: string;
  readiness_status: string;
  read_only_probe_ready: boolean;
  runtime_calls_enabled: boolean;
  blocking_reasons: string[];
  recommended_actions: string[];
};

export type ComfyUIRuntimeQueueStatus = {
  success: boolean;
  provider: string;
  base_url: string;
  external_request_attempted: boolean;
  runtime_calls_enabled: boolean;
  prompt_submission_enabled: boolean;
  status_code?: number | null;
  queue_running: unknown[];
  queue_pending: unknown[];
  error?: string | null;
};

export type ComfyUIRuntimeVideoResourcePlan = {
  success: boolean;
  provider: string;
  base_url: string;
  admission_status: string;
  should_submit_now: boolean;
  runtime_calls_enabled: boolean;
  prompt_submission_enabled: boolean;
  selected_endpoint?: Record<string, unknown> | null;
  selected_gpu?: Record<string, unknown> | null;
  gpu_devices: Record<string, unknown>[];
  queue_running_count: number;
  queue_pending_count: number;
  blocking_reasons: string[];
  recommended_actions: string[];
  error?: string | null;
};

async function requestJson<T>(
  path: string,
  init?: RequestInit,
  settings: ConversationSettings = defaultConversationSettings,
): Promise<T> {
  const response = await fetch(`${conversationClient.normalizeApiBase(settings.aiServerUrl)}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-Id": settings.workspaceId,
      "X-User-Id": settings.userId,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `ComfyUI runtime request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const comfyuiRuntimeClient = {
  health: (settings?: ConversationSettings) =>
    requestJson<ComfyUIRuntimeHealth>("/comfyui-runtime/health", {}, settings),
  diagnostics: (settings?: ConversationSettings) =>
    requestJson<ComfyUIRuntimeDiagnostics>("/comfyui-runtime/diagnostics", {}, settings),
  queueStatus: (settings?: ConversationSettings) =>
    requestJson<ComfyUIRuntimeQueueStatus>("/comfyui-runtime/queue", {}, settings),
  videoResourcePlan: (settings?: ConversationSettings) =>
    requestJson<ComfyUIRuntimeVideoResourcePlan>(
      "/comfyui-runtime/video-resource-plans",
      {
        method: "POST",
        body: JSON.stringify({
          resource_profile: "standard",
          width: 1280,
          height: 720,
          frames: 96,
          fps: 24,
          allow_queue: true,
          metadata: { source: "worker_console_server_pressure" },
        }),
      },
      settings,
    ),
};
