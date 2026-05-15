import { ConversationSettings, defaultConversationSettings } from "./conversationClient";

export type WorkflowTemplate = {
  id: string;
  template_key: string;
  name: string;
  description: string | null;
  category: string | null;
  status: string;
  current_version: string | null;
  latest_version: string | null;
  risk_level: string;
  tags: string[];
  metadata: Record<string, unknown>;
  versions: Array<{ id: string; version: string; validation_status: string; compatibility: Record<string, unknown> }>;
};

export type WorkflowTemplateRun = {
  id: string;
  template_id: string;
  template_version_id: string;
  workflow_run_id: string | null;
  status: string;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
  created_at: string;
};

function normalizeApiBase(rawBase: string): string {
  const trimmed = rawBase.replace(/\/$/, "");
  return trimmed.endsWith("/api/v1") ? trimmed : `${trimmed}/api/v1`;
}

async function requestJson<T>(path: string, init?: RequestInit, settings: ConversationSettings = defaultConversationSettings): Promise<T> {
  const response = await fetch(`${normalizeApiBase(settings.aiServerUrl)}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-Id": settings.workspaceId,
      "X-User-Id": settings.userId,
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error((await response.text()) || `Workflow template API request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export const workflowTemplateClient = {
  listTemplates: (settings?: ConversationSettings) => requestJson<{ items: WorkflowTemplate[] }>("/workflow-templates", {}, settings),
  listRuns: (settings?: ConversationSettings) => requestJson<{ items: WorkflowTemplateRun[] }>("/workflow-template-runs", {}, settings),
  validateTemplate: (templateId: string, settings?: ConversationSettings) =>
    requestJson<Record<string, unknown>>(`/workflow-templates/${templateId}/validate`, { method: "POST" }, settings),
  runTemplate: (templateId: string, settings?: ConversationSettings, input: Record<string, unknown> = {}) =>
    requestJson<WorkflowTemplateRun>(
      `/workflow-templates/${templateId}/run`,
      { method: "POST", body: JSON.stringify({ input, mode: "review_first", execution_mode: "immediate" }) },
      settings,
    ),
};
