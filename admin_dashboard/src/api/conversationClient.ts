import { AdminSettings, ApiList, JsonRecord, readAdminSettings, requestJson } from "./client";

export interface ConversationThread {
  id: string;
  workspace_id: string;
  user_id: string | null;
  title: string;
  status: string;
  metadata: JsonRecord;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  id: string;
  workspace_id: string;
  thread_id: string | null;
  role: "user" | "assistant" | "system" | "tool" | "event" | string;
  content: string;
  metadata: JsonRecord;
  created_at: string;
}

export interface ConversationEvent {
  id: string;
  workspace_id: string;
  thread_id: string;
  event_type: string;
  message: string | null;
  payload: JsonRecord;
  created_at: string;
}

export interface ConversationRunResponse {
  thread_id: string;
  user_message_id: string;
  assistant_message_id: string;
  assistant_message: ConversationMessage;
  route: string;
  route_name: string;
  selected_tool: string | null;
  events: ConversationEvent[];
  events_created: number;
  success: boolean;
  summary: string;
  result_metadata: JsonRecord;
  output: JsonRecord;
  approval_required: boolean;
  approval_id: string | null;
  approval_status: string | null;
  risk_level: "low" | "medium" | "high" | string | null;
  proposed_action: string | null;
  playbook_run_id: string | null;
  playbook_name: string | null;
  playbook_status: string | null;
  websocket_placeholder: boolean;
  sse_placeholder: boolean;
}

export interface ConversationApproval {
  id: string;
  workspace_id: string;
  thread_id: string;
  message_id: string | null;
  route_name: string;
  selected_tool: string | null;
  risk_level: "low" | "medium" | "high" | string;
  approval_status: "pending" | "approved" | "rejected" | "cancelled" | "expired" | "executed" | string;
  proposed_action: string;
  proposed_payload: JsonRecord;
  reviewer_notes: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejected_at: string | null;
  cancelled_at: string | null;
  expires_at: string | null;
  metadata: JsonRecord;
  created_at: string;
  updated_at: string;
}

export interface ConversationCreateInput {
  title: string;
  metadata?: JsonRecord;
}

export interface ConversationPlaybook {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  category: string | null;
  status: string;
  risk_level: string;
  steps: JsonRecord[];
  default_inputs: JsonRecord;
  metadata: JsonRecord;
  created_at: string;
  updated_at: string;
}

export interface ConversationPlaybookRun {
  id: string;
  workspace_id: string;
  playbook_id: string;
  thread_id: string;
  status: string;
  input_payload: JsonRecord;
  output_payload: JsonRecord;
  current_step: number;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessageInput {
  role?: "user" | "assistant" | "system" | "tool" | "event";
  content: string;
  metadata?: JsonRecord;
}

export const conversationClient = {
  createThread: (input: ConversationCreateInput, settings: AdminSettings = readAdminSettings()) =>
    requestJson<ConversationThread>(
      "/conversations",
      {
        method: "POST",
        body: JSON.stringify({
          title: input.title,
          metadata: input.metadata ?? { source: "admin_dashboard" },
        }),
      },
      settings,
    ),
  listThreads: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<ConversationThread>>("/conversations", {}, settings),
  getThread: (threadId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<ConversationThread>(`/conversations/${threadId}`, {}, settings),
  sendMessage: (
    threadId: string,
    input: ConversationMessageInput,
    settings: AdminSettings = readAdminSettings(),
  ) =>
    requestJson<ConversationMessage>(
      `/conversations/${threadId}/messages`,
      {
        method: "POST",
        body: JSON.stringify({
          role: input.role ?? "user",
          content: input.content,
          metadata: input.metadata ?? { source: "admin_dashboard" },
        }),
      },
      settings,
    ),
  listMessages: (threadId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ thread_id: string; items: ConversationMessage[] }>(
      `/conversations/${threadId}/messages`,
      {},
      settings,
    ),
  listEvents: (threadId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ thread_id: string; items: ConversationEvent[] }>(
      `/conversations/${threadId}/events`,
      {},
      settings,
    ),
  listApprovals: (threadId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<{ thread_id: string; items: ConversationApproval[] }>(
      `/conversations/${threadId}/approvals`,
      {},
      settings,
    ),
  approveApproval: (approvalId: string, reviewer_notes = "Approved from Admin Dashboard.", settings: AdminSettings = readAdminSettings()) =>
    requestJson<ConversationApproval>(
      `/conversation-approvals/${approvalId}/approve`,
      { method: "POST", body: JSON.stringify({ reviewer_notes }) },
      settings,
    ),
  rejectApproval: (approvalId: string, reviewer_notes = "Rejected from Admin Dashboard.", settings: AdminSettings = readAdminSettings()) =>
    requestJson<ConversationApproval>(
      `/conversation-approvals/${approvalId}/reject`,
      { method: "POST", body: JSON.stringify({ reviewer_notes }) },
      settings,
    ),
  cancelApproval: (approvalId: string, reviewer_notes = "Cancelled from Admin Dashboard.", settings: AdminSettings = readAdminSettings()) =>
    requestJson<ConversationApproval>(
      `/conversation-approvals/${approvalId}/cancel`,
      { method: "POST", body: JSON.stringify({ reviewer_notes }) },
      settings,
    ),
  executeApproval: (approvalId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<ConversationRunResponse>(
      `/conversation-approvals/${approvalId}/execute`,
      { method: "POST", body: JSON.stringify({ input: { approval_id: approvalId } }) },
      settings,
    ),
  runConversation: (
    threadId: string,
    message: string,
    settings: AdminSettings = readAdminSettings(),
    mode: "auto_safe" | "review_first" | "execute_after_approval" = "auto_safe",
    playbookName?: string | null,
  ) =>
    requestJson<ConversationRunResponse>(
      `/conversations/${threadId}/run`,
      {
        method: "POST",
        body: JSON.stringify({ input: { message }, mode, playbook_name: playbookName || undefined }),
      },
      settings,
    ),
  listPlaybooks: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<ConversationPlaybook>>("/conversation-playbooks", {}, settings),
  runPlaybook: (
    playbookId: string,
    input: JsonRecord,
    settings: AdminSettings = readAdminSettings(),
    mode: "auto_safe" | "review_first" | "execute_after_approval" = "auto_safe",
    threadId?: string | null,
  ) =>
    requestJson<ConversationPlaybookRun>(
      `/conversation-playbooks/${playbookId}/run`,
      {
        method: "POST",
        body: JSON.stringify({ input, mode, thread_id: threadId || undefined }),
      },
      settings,
    ),
  listPlaybookRuns: (settings: AdminSettings = readAdminSettings()) =>
    requestJson<ApiList<ConversationPlaybookRun>>("/conversation-playbook-runs", {}, settings),
  cancelPlaybookRun: (runId: string, settings: AdminSettings = readAdminSettings()) =>
    requestJson<ConversationPlaybookRun>(
      `/conversation-playbook-runs/${runId}/cancel`,
      { method: "POST" },
      settings,
    ),
};
