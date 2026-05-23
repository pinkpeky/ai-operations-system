import { conversationClient, defaultConversationSettings, type ConversationSettings } from "./conversationClient";

export type CommercialOperation = {
  id: string;
  title: string;
  objective: string;
  status: string;
  channels?: string[];
  knowledge_collection?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type CommercialOperationLoopStageStatus =
  | "complete"
  | "in_progress"
  | "review_required"
  | "blocked"
  | "missing";

export type CommercialOperationLoopStage = {
  stage_key: string;
  title: string;
  owner: string;
  status: CommercialOperationLoopStageStatus;
  summary: string;
  next_action: string;
  blocked_reasons: string[];
  related_records: Record<string, unknown>[];
  operator_actions: string[];
  server_actions: string[];
  client_actions: string[];
};

export type CommercialOperationLoopSummary = {
  operation_id: string;
  workspace_id: string;
  title: string;
  objective: string;
  loop_status: string;
  current_stage_key: string | null;
  next_action: string;
  completion_ratio: number;
  stages: CommercialOperationLoopStage[];
  counts: Record<string, number>;
  execution_protocol: Record<string, unknown>;
  readiness: Record<string, unknown>[];
  boundaries: string[];
  generated_at: string;
};

export type CommercialOperationPlanPreview = {
  operation_id: string;
  plan_outline: Record<string, unknown>[];
};

export type CommercialOperationContentDraft = {
  id: string;
  operation_id: string;
  step_key: string;
  channel: string;
  content_format: string;
  title: string;
  draft_status: string;
  summary?: string | null;
  content_body: string;
};

export type CommercialOperationApproval = {
  id: string;
  operation_id: string;
  step_key: string;
  title: string;
  approval_status: string;
  risk_level: string;
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
    throw new Error(body || `Commercial operation request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const commercialOperationClient = {
  list: (settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperation[] }>("/commercial-operations", {}, settings),
  create: (
    payload: {
      title: string;
      objective: string;
      target_audience?: string;
      channels?: string[];
      knowledge_collection?: string;
      success_metrics?: string[];
      constraints?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperation>(
      "/commercial-operations",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  operationLoop: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationLoopSummary>(
      `/commercial-operations/${encodeURIComponent(operationId)}/operation-loop`,
      {},
      settings,
    ),
  planDraft: (operationId: string, settings?: ConversationSettings) =>
    requestJson<CommercialOperationPlanPreview>(
      `/commercial-operations/${encodeURIComponent(operationId)}/plan-draft`,
      { method: "POST" },
      settings,
    ),
  createContentDraft: (
    operationId: string,
    payload: {
      step_key?: string;
      channel: string;
      content_format?: string;
      title: string;
      audience_segment?: string;
      content_body?: string;
      summary?: string;
      call_to_action?: string;
      source_materials?: string[];
      asset_requests?: Record<string, unknown>[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyContentDraft: (
    operationId: string,
    draftId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  createApproval: (
    operationId: string,
    payload: {
      step_key: string;
      title: string;
      requested_action?: string;
      risk_level?: string;
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationApproval>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
};
