export type ConversationThread = {
  id: string;
  workspace_id: string;
  user_id: string | null;
  title: string;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ConversationMessage = {
  id: string;
  workspace_id: string;
  thread_id: string | null;
  role: string;
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type ConversationEvent = {
  id: string;
  workspace_id: string;
  thread_id: string;
  event_type: string;
  message: string | null;
  payload: Record<string, unknown>;
  created_at: string;
};

export type ConversationRunResponse = {
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
  result_metadata: Record<string, unknown>;
  output: Record<string, unknown>;
  approval_required: boolean;
  approval_id: string | null;
  approval_status: string | null;
  risk_level: string | null;
  proposed_action: string | null;
  playbook_run_id: string | null;
  playbook_name: string | null;
  playbook_status: string | null;
  websocket_placeholder: boolean;
  sse_placeholder: boolean;
};

export type ConversationApproval = {
  id: string;
  workspace_id: string;
  thread_id: string;
  message_id: string | null;
  route_name: string;
  selected_tool: string | null;
  risk_level: string;
  approval_status: string;
  proposed_action: string;
  proposed_payload: Record<string, unknown>;
  reviewer_notes: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejected_at: string | null;
  cancelled_at: string | null;
  expires_at: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ConversationSettings = {
  aiServerUrl: string;
  workspaceId: string;
  userId: string;
};

export type ConversationPlaybook = {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  category: string | null;
  status: string;
  risk_level: string;
  steps: Record<string, unknown>[];
  default_inputs: Record<string, unknown>;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ConversationPlaybookRun = {
  id: string;
  workspace_id: string;
  playbook_id: string;
  thread_id: string;
  status: string;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  current_step: number;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

export const defaultConversationSettings: ConversationSettings = {
  aiServerUrl: import.meta.env.VITE_AI_SERVER_API ?? "http://localhost:8000",
  workspaceId: import.meta.env.VITE_WORKSPACE_ID ?? "demo-workspace",
  userId: import.meta.env.VITE_USER_ID ?? "demo-user",
};

function normalizeApiBase(rawBase: string): string {
  const trimmed = rawBase.replace(/\/$/, "");
  return trimmed.endsWith("/api/v1") ? trimmed : `${trimmed}/api/v1`;
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
  settings: ConversationSettings = defaultConversationSettings,
): Promise<T> {
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
    const body = await response.text();
    throw new Error(body || `Conversation API request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const conversationClient = {
  defaultSettings: defaultConversationSettings,
  normalizeApiBase,
  createThread: (title: string, settings?: ConversationSettings) =>
    requestJson<ConversationThread>("/conversations", {
      method: "POST",
      body: JSON.stringify({ title, metadata: { source: "worker_console_desktop" } }),
    }, settings),
  listThreads: (settings?: ConversationSettings) =>
    requestJson<{ items: ConversationThread[] }>("/conversations", {}, settings),
  getThread: (threadId: string, settings?: ConversationSettings) =>
    requestJson<ConversationThread>(`/conversations/${threadId}`, {}, settings),
  sendMessage: (threadId: string, content: string, settings?: ConversationSettings) =>
    requestJson<ConversationMessage>(`/conversations/${threadId}/messages`, {
      method: "POST",
      body: JSON.stringify({ role: "user", content, metadata: { source: "worker_console_desktop" } }),
    }, settings),
  listApprovals: (threadId: string, settings?: ConversationSettings) =>
    requestJson<{ thread_id: string; items: ConversationApproval[] }>(`/conversations/${threadId}/approvals`, {}, settings),
  approveApproval: (approvalId: string, reviewer_notes = "Approved from Desktop Console.", settings?: ConversationSettings) =>
    requestJson<ConversationApproval>(`/conversation-approvals/${approvalId}/approve`, {
      method: "POST",
      body: JSON.stringify({ reviewer_notes }),
    }, settings),
  rejectApproval: (approvalId: string, reviewer_notes = "Rejected from Desktop Console.", settings?: ConversationSettings) =>
    requestJson<ConversationApproval>(`/conversation-approvals/${approvalId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reviewer_notes }),
    }, settings),
  cancelApproval: (approvalId: string, reviewer_notes = "Cancelled from Desktop Console.", settings?: ConversationSettings) =>
    requestJson<ConversationApproval>(`/conversation-approvals/${approvalId}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reviewer_notes }),
    }, settings),
  executeApproval: (approvalId: string, settings?: ConversationSettings) =>
    requestJson<ConversationRunResponse>(`/conversation-approvals/${approvalId}/execute`, {
      method: "POST",
      body: JSON.stringify({ input: { approval_id: approvalId } }),
    }, settings),
  runConversation: (threadId: string, message: string, settings?: ConversationSettings, mode: "auto_safe" | "review_first" | "execute_after_approval" = "auto_safe", playbookName?: string | null) =>
    requestJson<ConversationRunResponse>(`/conversations/${threadId}/run`, {
      method: "POST",
      body: JSON.stringify({ input: { message }, mode, playbook_name: playbookName || undefined }),
    }, settings),
  listPlaybooks: (settings?: ConversationSettings) =>
    requestJson<{ items: ConversationPlaybook[] }>("/conversation-playbooks", {}, settings),
  runPlaybook: (playbookId: string, input: Record<string, unknown>, settings?: ConversationSettings, mode: "auto_safe" | "review_first" | "execute_after_approval" = "auto_safe", threadId?: string | null) =>
    requestJson<ConversationPlaybookRun>(`/conversation-playbooks/${playbookId}/run`, {
      method: "POST",
      body: JSON.stringify({ input, mode, thread_id: threadId || undefined }),
    }, settings),
  listPlaybookRuns: (settings?: ConversationSettings) =>
    requestJson<{ items: ConversationPlaybookRun[] }>("/conversation-playbook-runs", {}, settings),
  cancelPlaybookRun: (runId: string, settings?: ConversationSettings) =>
    requestJson<ConversationPlaybookRun>(`/conversation-playbook-runs/${runId}/cancel`, { method: "POST" }, settings),
  listMessages: (threadId: string, settings?: ConversationSettings) =>
    requestJson<{ thread_id: string; items: ConversationMessage[] }>(`/conversations/${threadId}/messages`, {}, settings),
  listEvents: (threadId: string, settings?: ConversationSettings) =>
    requestJson<{ thread_id: string; items: ConversationEvent[] }>(`/conversations/${threadId}/events`, {}, settings),
  appendMessage: (threadId: string, content: string, settings?: ConversationSettings) =>
    conversationClient.sendMessage(threadId, content, settings),
  run: (threadId: string, message: string, settings?: ConversationSettings) =>
    conversationClient.runConversation(threadId, message, settings),
  getMessages: (threadId: string, settings?: ConversationSettings) =>
    conversationClient.listMessages(threadId, settings),
  getEvents: (threadId: string, settings?: ConversationSettings) =>
    conversationClient.listEvents(threadId, settings),
};
