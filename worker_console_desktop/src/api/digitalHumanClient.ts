import { conversationClient, defaultConversationSettings, type ConversationSettings } from "./conversationClient";

export type DigitalHumanVideoJob = {
  id: string;
  job_status: string;
  provider: string;
  execution_mode: string;
  approval_status: string;
  progress_percent?: number;
  current_stage?: string;
  next_action?: string | null;
  linked_comfyui_video_job_id?: string | null;
  result_summary?: string | null;
  outputs?: Record<string, unknown>[];
  updated_at?: string;
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
    throw new Error(body || `Digital human request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const digitalHumanClient = {
  listVideoJobs: (settings?: ConversationSettings) =>
    requestJson<{ items: DigitalHumanVideoJob[] }>("/digital-humans/video-jobs?limit=5", {}, settings),
  refreshVideoJob: (jobId: string, settings?: ConversationSettings) =>
    requestJson<DigitalHumanVideoJob>(
      `/digital-humans/video-jobs/${encodeURIComponent(jobId)}/refresh`,
      {
        method: "POST",
        body: JSON.stringify({ metadata: { source: "worker_console_video_progress" } }),
      },
      settings,
    ),
};
