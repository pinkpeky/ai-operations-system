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
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationApproval = {
  id: string;
  operation_id: string;
  step_key: string;
  title: string;
  requested_action?: string | null;
  approval_status: string;
  risk_level: string;
  reviewer_notes?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationDeliverable = {
  id: string;
  operation_id: string;
  content_draft_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  deliverable_type: string;
  title: string;
  deliverable_status: string;
  summary?: string | null;
  delivery_notes?: string | null;
  quality_checks: string[];
  package_payload?: Record<string, unknown>;
  result_summary?: string | null;
  metadata?: Record<string, unknown>;
};

export type CommercialOperationExecutionRequest = {
  id: string;
  operation_id: string;
  deliverable_id: string;
  output_artifact_id?: string | null;
  step_key: string;
  channel: string;
  execution_type: string;
  execution_mode: string;
  title: string;
  request_status: string;
  execution_target?: string | null;
  input_summary?: string | null;
  runbook: Record<string, unknown>[];
  readiness_checks: string[];
  expected_outputs: string[];
  operator_checklist: Record<string, unknown>[];
  handoff_payload?: Record<string, unknown>;
  result_summary?: string | null;
  metadata?: Record<string, unknown>;
};

function queryString(params: Record<string, string | number | null | undefined>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

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
  listContentDrafts: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationContentDraft[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts${queryString({ status })}`,
      {},
      settings,
    ),
  approveContentDraft: (
    operationId: string,
    draftId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectContentDraft: (
    operationId: string,
    draftId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationContentDraft>(
      `/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/reject`,
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
  listApprovals: (operationId: string, status?: string, settings?: ConversationSettings) =>
    requestJson<{ items: CommercialOperationApproval[] }>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals${queryString({ status })}`,
      {},
      settings,
    ),
  approveApproval: (
    operationId: string,
    approvalId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationApproval>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  rejectApproval: (
    operationId: string,
    approvalId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationApproval>(
      `/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  createDeliverable: (
    operationId: string,
    payload: {
      step_key?: string;
      content_draft_id: string;
      asset_request_ids?: string[];
      deliverable_type?: string;
      title: string;
      summary?: string;
      delivery_notes?: string;
      quality_checks?: string[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyDeliverable: (
    operationId: string,
    deliverableId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  approveDeliverable: (
    operationId: string,
    deliverableId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
  packageDeliverable: (
    operationId: string,
    deliverableId: string,
    resultSummary: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationDeliverable>(
      `/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/package`,
      {
        method: "POST",
        body: JSON.stringify({ result_summary: resultSummary }),
      },
      settings,
    ),
  createExecutionRequest: (
    operationId: string,
    payload: {
      deliverable_id: string;
      execution_type?: string;
      execution_mode?: string;
      title: string;
      execution_target?: string;
      input_summary?: string;
      runbook?: Record<string, unknown>[];
      readiness_checks?: string[];
      expected_outputs?: string[];
      evidence_snapshot_ids?: string[];
      operator_checklist?: Record<string, unknown>[];
      metadata?: Record<string, unknown>;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRequest>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      settings,
    ),
  readyExecutionRequest: (
    operationId: string,
    executionRequestId: string,
    reviewerNotes: string,
    settings?: ConversationSettings,
  ) =>
    requestJson<CommercialOperationExecutionRequest>(
      `/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/ready`,
      {
        method: "POST",
        body: JSON.stringify({ reviewer_notes: reviewerNotes }),
      },
      settings,
    ),
};
