import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  MessageCircle,
  PauseCircle,
  PlayCircle,
  RefreshCcw,
  RotateCcw,
  Server,
  Send,
  Square,
  TerminalSquare,
  XCircle,
  Wifi,
  WifiOff,
} from "lucide-react";
import {
  browserRuntimeClient,
  BrowserRuntimeEvent,
  BrowserRuntimeReplay,
  BrowserRuntimeSession,
  BrowserRuntimeSnapshot,
} from "./api/browserRuntimeClient";
import {
  conversationClient,
  ConversationApproval,
  ConversationEvent,
  ConversationMessage,
  ConversationPlaybook,
  ConversationPlaybookRun,
  ConversationSettings,
} from "./api/conversationClient";
import { outputArtifactClient, OutputArtifact } from "./api/outputArtifactClient";
import { taskRunClient, TaskRun, TaskRunEvent } from "./api/taskRunClient";
import { workflowClient, AgentMemorySnapshot, WorkflowPlannerResult, WorkflowRun, WorkflowStep } from "./api/workflowClient";
import { localWorkerClient, WorkerHealth, WorkerLogs, WorkerStatus } from "./api/localWorkerClient";
import "./styles.css";

const fallbackStatus: WorkerStatus = {
  worker_id: null,
  worker_name: null,
  workspace_id: null,
  server_url: null,
  worker_base_url: null,
  runtime_port: null,
  registered: false,
  runtime_running: false,
  heartbeat_running: false,
  current_status: "unknown",
  last_heartbeat_at: null,
  last_error: null,
  openclaw_enabled: false,
  browser_enabled: false,
};

type ControlAction =
  | "startRuntime"
  | "stopRuntime"
  | "restartRuntime"
  | "startHeartbeat"
  | "stopHeartbeat";

function StatusBadge({ label, active }: { label: string; active: boolean }) {
  return (
    <span className={`status-badge ${active ? "status-badge-active" : "status-badge-muted"}`}>
      {active ? <CheckCircle2 size={14} /> : <PauseCircle size={14} />}
      {label}
    </span>
  );
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="field">
      <span className="field-label">{label}</span>
      <span className="field-value">{value ?? "-"}</span>
    </div>
  );
}

function ActionButton({
  icon,
  label,
  onClick,
  disabled,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled: boolean;
}) {
  return (
    <button className="action-button" onClick={onClick} disabled={disabled}>
      {icon}
      <span>{label}</span>
    </button>
  );
}

function isErrorLog(line: string): boolean {
  return /error|failed|exception|traceback/i.test(line);
}

function ChatPanel() {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [title, setTitle] = useState("Worker Console conversation");
  const [input, setInput] = useState("请帮我生成一条短视频文案，并展示执行事件。");
  const [settings, setSettings] = useState<ConversationSettings>(() => {
    const stored = window.localStorage.getItem("workerConsoleConversationSettings");
    return stored ? { ...conversationClient.defaultSettings, ...JSON.parse(stored) } : conversationClient.defaultSettings;
  });
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [events, setEvents] = useState<ConversationEvent[]>([]);
  const [approvals, setApprovals] = useState<ConversationApproval[]>([]);
  const [playbooks, setPlaybooks] = useState<ConversationPlaybook[]>([]);
  const [playbookRuns, setPlaybookRuns] = useState<ConversationPlaybookRun[]>([]);
  const [artifacts, setArtifacts] = useState<OutputArtifact[]>([]);
  const [taskRuns, setTaskRuns] = useState<TaskRun[]>([]);
  const [taskEvents, setTaskEvents] = useState<TaskRunEvent[]>([]);
  const [schedulerHealth, setSchedulerHealth] = useState<Record<string, unknown> | null>(null);
  const [selectedTaskRunId, setSelectedTaskRunId] = useState<string | null>(null);
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([]);
  const [memorySnapshots, setMemorySnapshots] = useState<AgentMemorySnapshot[]>([]);
  const [selectedWorkflowRunId, setSelectedWorkflowRunId] = useState<string | null>(null);
  const [workflowPlanner, setWorkflowPlanner] = useState<WorkflowPlannerResult | null>(null);
  const [selectedPlaybookName, setSelectedPlaybookName] = useState("browser_screenshot_report");
  const [chatError, setChatError] = useState<string | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [lastRoute, setLastRoute] = useState<string | null>(null);
  const [lastSelectedTool, setLastSelectedTool] = useState<string | null>(null);
  const [lastRunMetadata, setLastRunMetadata] = useState<Record<string, unknown> | null>(null);
  const [connectionState, setConnectionState] = useState("unknown");
  const [runStatus, setRunStatus] = useState("idle");
  const [pollEvents, setPollEvents] = useState(false);

  useEffect(() => {
    window.localStorage.setItem("workerConsoleConversationSettings", JSON.stringify(settings));
  }, [settings]);

  const refreshPlaybooks = useCallback(async () => {
    try {
      const [playbookResponse, runResponse] = await Promise.all([
        conversationClient.listPlaybooks(settings),
        conversationClient.listPlaybookRuns(settings),
      ]);
      setPlaybooks(playbookResponse.items);
      setPlaybookRuns(runResponse.items);
    } catch {
      setPlaybooks([]);
      setPlaybookRuns([]);
    }
  }, [settings]);

  const refreshTaskRuns = useCallback(async () => {
    try {
      const response = await taskRunClient.listTaskRuns(settings);
      const health = await taskRunClient.schedulerHealth(settings);
      setTaskRuns(response.items);
      setSchedulerHealth(health as unknown as Record<string, unknown>);
      const taskId = selectedTaskRunId || response.items[0]?.id;
      if (taskId) {
        setSelectedTaskRunId(taskId);
        setTaskEvents((await taskRunClient.listEvents(taskId, settings)).items);
      }
    } catch {
      setTaskRuns([]);
      setTaskEvents([]);
    }
  }, [selectedTaskRunId, settings]);

  const refreshWorkflows = useCallback(async () => {
    try {
      const response = await workflowClient.listRuns(settings);
      setWorkflowRuns(response.items);
      const workflowId =
        selectedWorkflowRunId ||
        response.items.find((item) => item.status === "running" || item.status === "waiting_approval")?.id ||
        response.items[0]?.id;
      if (workflowId) {
        setSelectedWorkflowRunId(workflowId);
        const [steps, memories, planner] = await Promise.all([
          workflowClient.listSteps(workflowId, settings),
          workflowClient.listMemorySnapshots(workflowId, settings),
          workflowClient.getPlanner(workflowId, settings).catch(() => null),
        ]);
        setWorkflowSteps(steps.items);
        setMemorySnapshots(memories.items);
        setWorkflowPlanner(planner);
      }
    } catch {
      setWorkflowRuns([]);
      setWorkflowSteps([]);
      setMemorySnapshots([]);
      setWorkflowPlanner(null);
    }
  }, [selectedWorkflowRunId, settings]);

  useEffect(() => {
    void refreshPlaybooks();
    void refreshTaskRuns();
    void refreshWorkflows();
  }, [refreshPlaybooks, refreshTaskRuns, refreshWorkflows]);

  const refreshConversation = useCallback(async () => {
    if (!threadId) {
      return;
    }
    try {
      setChatError(null);
      const [nextMessages, nextEvents, nextApprovals] = await Promise.all([
        conversationClient.listMessages(threadId, settings),
        conversationClient.listEvents(threadId, settings),
        conversationClient.listApprovals(threadId, settings),
      ]);
      setMessages(nextMessages.items);
      setEvents(nextEvents.items);
      setApprovals(nextApprovals.items);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId })).items);
      await refreshPlaybooks();
      await refreshTaskRuns();
      await refreshWorkflows();
      setConnectionState("connected");
    } catch (nextError) {
      setConnectionState("disconnected");
      setChatError(nextError instanceof Error ? nextError.message : "AI Server unreachable");
    }
  }, [refreshPlaybooks, refreshTaskRuns, refreshWorkflows, settings, threadId]);

  useEffect(() => {
    if (!pollEvents || !threadId) {
      return undefined;
    }
    const timer = window.setInterval(() => {
      void refreshConversation();
    }, 5000);
    return () => window.clearInterval(timer);
  }, [pollEvents, refreshConversation, threadId]);

  const createThread = async () => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("creating thread");
    try {
      const thread = await conversationClient.createThread(title.trim() || "Worker Console conversation", settings);
      setThreadId(thread.id);
      setMessages([]);
      setEvents([]);
      setApprovals([]);
      setLastRoute(null);
      setLastSelectedTool(null);
      setLastRunMetadata(null);
      setConnectionState("connected");
      setRunStatus("thread created");
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "AI Server unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const sendConversationMessage = async () => {
    const content = input.trim();
    if (!content) {
      return;
    }
    setChatLoading(true);
    setChatError(null);
    setRunStatus("running conversation");
    try {
      const thread = threadId
        ? { id: threadId }
        : await conversationClient.createThread(title.trim() || `Worker Console Chat ${new Date().toLocaleString()}`, settings);
      if (!threadId) {
        setThreadId(thread.id);
      }
      await conversationClient.sendMessage(thread.id, content, settings);
      const run = await conversationClient.runConversation(thread.id, content, settings, "review_first", selectedPlaybookName);
      setMessages((await conversationClient.listMessages(thread.id, settings)).items);
      setApprovals((await conversationClient.listApprovals(thread.id, settings)).items);
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: thread.id })).items);
      setEvents(run.events);
      setLastRoute(run.route_name);
      setLastSelectedTool(run.selected_tool);
      setLastRunMetadata(run.result_metadata);
      if (run.workflow_run_id) {
        setSelectedWorkflowRunId(run.workflow_run_id);
      }
      if (run.task_run_id) {
        setSelectedTaskRunId(run.task_run_id);
        await refreshTaskRuns();
      }
      await refreshWorkflows();
      setConnectionState("connected");
      setRunStatus(`route: ${run.route_name} | tool: ${run.selected_tool ?? "none"} | risk: ${run.risk_level ?? "-"} | approval: ${run.approval_status ?? "-"} | success: ${run.success}`);
      setInput("");
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "AI Server unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const sendBackgroundConversation = async () => {
    const content = input.trim();
    if (!content) {
      return;
    }
    setChatLoading(true);
    setChatError(null);
    setRunStatus("queueing background task");
    try {
      const thread = threadId
        ? { id: threadId }
        : await conversationClient.createThread(title.trim() || `Worker Console Background ${new Date().toLocaleString()}`, settings);
      if (!threadId) {
        setThreadId(thread.id);
      }
      const run = await conversationClient.runConversation(thread.id, content, settings, "review_first", selectedPlaybookName, "background");
      if (run.task_run_id) {
        setSelectedTaskRunId(run.task_run_id);
      }
      if (run.workflow_run_id) {
        setSelectedWorkflowRunId(run.workflow_run_id);
      }
      await refreshConversation();
      await refreshTaskRuns();
      await refreshWorkflows();
      setLastRunMetadata(run.result_metadata);
      setRunStatus(`background task queued: ${run.task_run_id ?? "-"} | status: ${run.task_status ?? "-"}`);
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "Background task API unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const mutateTaskRun = async (taskRunId: string, action: "retry" | "cancel" | "resume" | "recover") => {
    setChatLoading(true);
    setChatError(null);
    try {
      if (action === "retry") {
        await taskRunClient.retry(taskRunId, settings);
      } else if (action === "cancel") {
        await taskRunClient.cancel(taskRunId, settings);
      } else if (action === "recover") {
        await taskRunClient.recover(taskRunId, settings);
      } else {
        await taskRunClient.resume(taskRunId, settings);
      }
      await refreshTaskRuns();
      setRunStatus(`task ${action} submitted`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : `Task ${action} failed`);
      setRunStatus("task control error");
    } finally {
      setChatLoading(false);
    }
  };

  const mutateApproval = async (approvalId: string, action: "approve" | "reject" | "cancel" | "execute") => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus(`${action} approval`);
    try {
      if (action === "approve") {
        await conversationClient.approveApproval(approvalId, "Looks safe to execute.", settings);
      } else if (action === "reject") {
        await conversationClient.rejectApproval(approvalId, "Need to rewrite before execution.", settings);
      } else if (action === "cancel") {
        await conversationClient.cancelApproval(approvalId, "Cancelled before execution.", settings);
      } else {
        const run = await conversationClient.executeApproval(approvalId, settings);
        setEvents(run.events);
        setLastRunMetadata(run.result_metadata);
      }
      await refreshConversation();
      setConnectionState("connected");
      setRunStatus(`${action} approval completed`);
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "Approval API unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const saveMessageAsArtifact = async (messageId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("saving artifact");
    try {
      await outputArtifactClient.createFromMessage(messageId, settings);
      if (threadId) {
        setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId })).items);
      }
      setRunStatus("artifact saved");
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Output Artifact API unreachable");
      setRunStatus("artifact error");
    } finally {
      setChatLoading(false);
    }
  };

  const exportArtifact = async (artifactId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("exporting artifact");
    try {
      const exported = await outputArtifactClient.exportArtifact(artifactId, "markdown", settings);
      setLastRunMetadata({ artifact_export: exported });
      setRunStatus(`artifact exported: ${exported.export_path}`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Artifact export failed");
      setRunStatus("artifact export error");
    } finally {
      setChatLoading(false);
    }
  };

  const packageArtifact = async (artifactId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("packaging artifact");
    try {
      const packaged = await outputArtifactClient.packageArtifact(artifactId, settings);
      setLastRunMetadata({ artifact_package: packaged });
      setRunStatus(`artifact packaged: ${packaged.output_path ?? packaged.export_path ?? "bundle created"}`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Artifact package failed");
      setRunStatus("artifact package error");
    } finally {
      setChatLoading(false);
    }
  };

  const showArtifactLineage = async (artifactId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("loading artifact lineage");
    try {
      const lineage = await outputArtifactClient.getLineage(artifactId, settings);
      setLastRunMetadata({ artifact_lineage: lineage });
      setRunStatus(`lineage loaded: ${lineage.relationships.length} relationships`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Artifact lineage failed");
      setRunStatus("artifact lineage error");
    } finally {
      setChatLoading(false);
    }
  };

  const runSelectedPlaybook = async () => {
    const playbook = playbooks.find((item) => item.name === selectedPlaybookName);
    if (!playbook) {
      setChatError("Select an available playbook before running.");
      return;
    }
    setChatLoading(true);
    setChatError(null);
    setRunStatus("running playbook");
    try {
      await conversationClient.runPlaybook(
        playbook.id,
        { message: input, url: "https://example.com", topic: input || "AI automation operations" },
        settings,
        "review_first",
        threadId,
      );
      await refreshPlaybooks();
      if (threadId) {
        await refreshConversation();
      }
      setRunStatus("Playbook run submitted");
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Playbook API unreachable");
      setRunStatus("error");
    } finally {
      setChatLoading(false);
    }
  };

  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const latestAssistantMessage = assistantMessages[assistantMessages.length - 1];

  return (
    <section className="panel chat-panel">
      <div className="panel-title logs-title">
        <span>
          <MessageCircle size={18} />
          <h2>Chat Panel</h2>
        </span>
        <div className="chat-actions">
          <button className="refresh-button" onClick={() => void createThread()} disabled={chatLoading}>
            <MessageCircle size={15} />
            Create thread
          </button>
          <button className="refresh-button" onClick={() => void refreshConversation()} disabled={!threadId}>
            <RefreshCcw size={15} />
            Refresh messages/events
          </button>
        </div>
      </div>
      <div className="chat-config-grid">
        <label>
          AI Server URL
          <input
            value={settings.aiServerUrl}
            onChange={(event) => setSettings((current) => ({ ...current, aiServerUrl: event.target.value }))}
          />
        </label>
        <label>
          Workspace ID
          <input
            value={settings.workspaceId}
            onChange={(event) => setSettings((current) => ({ ...current, workspaceId: event.target.value }))}
          />
        </label>
        <label>
          User ID
          <input
            value={settings.userId}
            onChange={(event) => setSettings((current) => ({ ...current, userId: event.target.value }))}
          />
        </label>
        <label>
          Thread title
          <input value={title} onChange={(event) => setTitle(event.target.value)} />
        </label>
      </div>
      <div className="chat-meta">
        AI Server {connectionState} | thread: {threadId ?? "-"} | run status: {runStatus} | route: {lastRoute ?? "-"} | selected tool: {lastSelectedTool ?? "-"}
      </div>
      <div className="latest-assistant">Latest assistant message: {latestAssistantMessage?.content ?? "-"}</div>
      <pre className="event-payload">
        {JSON.stringify(lastRunMetadata ?? { status: "run a conversation to see full bridge metadata" }, null, 2)}
      </pre>
      <label className="chat-checkbox">
        <input type="checkbox" checked={pollEvents} onChange={(event) => setPollEvents(event.target.checked)} />
        Poll events every 5 seconds
      </label>
      {connectionState === "disconnected" ? (
        <div className="inline-error">
          <AlertTriangle size={16} />
          AI Server unreachable. Check VITE_AI_SERVER_API, workspace headers, and that the API server is running.
        </div>
      ) : null}
      {chatError ? (
        <div className="inline-error">
          <AlertTriangle size={16} />
          {chatError}
        </div>
      ) : null}
      <div className="chat-note">
        Worker Console remains a local runtime console. This Chat Panel uses approval review_first by default, polling only, not WebSocket, not SSE, and not a full ChatGPT UI.
      </div>
      <div className="approval-list">
        <h3>Playbook selector</h3>
        <select value={selectedPlaybookName} onChange={(event) => setSelectedPlaybookName(event.target.value)}>
          {playbooks.map((playbook) => (
            <option key={playbook.id} value={playbook.name}>
              {playbook.name} | {playbook.risk_level}
            </option>
          ))}
        </select>
        <div className="chat-note">
          Run playbook keeps the Phase 39 approval gate. Built-ins include browser_screenshot_report and content_generation.
        </div>
        <div className="chat-actions">
          <button className="action-button" onClick={() => void runSelectedPlaybook()} disabled={chatLoading}>
            Run playbook
          </button>
          <button className="refresh-button" onClick={() => void refreshPlaybooks()}>
            Refresh playbooks
          </button>
        </div>
        <h3>Playbook runs</h3>
        {playbookRuns.length > 0 ? playbookRuns.slice(0, 4).map((run) => (
          <div key={run.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{run.id}</strong>
              <span className="status-badge status-badge-muted">{run.status}</span>
            </div>
            <p>Step timeline</p>
            <pre className="event-payload">{JSON.stringify(run.output_payload?.steps ?? [], null, 2)}</pre>
          </div>
        )) : (
          <div className="empty-chat">No Playbook runs yet.</div>
        )}
      </div>
      <div className="approval-list">
        <h3>Pending approvals panel</h3>
        {approvals.length > 0 ? approvals.map((approval) => (
          <div key={approval.id} className={`approval-card approval-risk-${approval.risk_level}`}>
            <div className="approval-card-header">
              <strong>{approval.proposed_action}</strong>
              <span className="status-badge status-badge-muted">{approval.risk_level} risk</span>
              <span className="status-badge status-badge-muted">{approval.approval_status}</span>
            </div>
            <pre className="event-payload">{JSON.stringify(approval.proposed_payload, null, 2)}</pre>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => void mutateApproval(approval.id, "approve")} disabled={approval.approval_status !== "pending"}>Approve</button>
              <button className="refresh-button" onClick={() => void mutateApproval(approval.id, "reject")} disabled={approval.approval_status !== "pending"}>Reject</button>
              <button className="refresh-button" onClick={() => void mutateApproval(approval.id, "cancel")} disabled={!["pending", "approved"].includes(approval.approval_status)}>Cancel</button>
              <button className="action-button" onClick={() => void mutateApproval(approval.id, "execute")} disabled={approval.approval_status !== "approved"}>Execute approved action</button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No pending approvals yet. Medium/high risk tools wait here before execution.</div>
        )}
      </div>
      <div className="chat-grid">
        <div className="message-list">
          {messages.length > 0 ? (
            messages.map((message) => (
              <div key={message.id} className={`chat-message chat-message-${message.role}`}>
                <strong>{message.role}</strong>
                <p>{message.content}</p>
                {message.role === "assistant" ? (
                  <button className="refresh-button" onClick={() => void saveMessageAsArtifact(message.id)} disabled={chatLoading}>
                    Save as Artifact
                  </button>
                ) : null}
              </div>
            ))
          ) : (
            <div className="empty-chat">No messages yet. Create a thread, send a message, then run conversation.</div>
          )}
        </div>
        <div className="event-timeline">
          {events.length > 0 ? (
            events.slice(-12).map((event) => (
              <div key={event.id} className="event-item">
                <span>{event.event_type}</span>
                <p>{event.message ?? "-"}</p>
                <small>{event.created_at}</small>
                <pre className="event-payload">{JSON.stringify(event.payload, null, 2)}</pre>
              </div>
            ))
          ) : (
            <div className="empty-chat">No events yet.</div>
          )}
        </div>
      </div>
      <div className="approval-list">
        <h3>Output Library</h3>
        <div className="chat-note">Generated artifacts from Playbook runs and saved assistant messages. This is not a full DAM.</div>
        {artifacts.length > 0 ? artifacts.slice(0, 5).map((artifact) => (
          <div key={artifact.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{artifact.title}</strong>
              <span>{artifact.artifact_type}</span>
              <span>{artifact.artifact_role ?? "no_role"}</span>
              <span>{artifact.artifact_stage}</span>
              <span>{artifact.retention_policy}</span>
              <span>{artifact.source_type}</span>
            </div>
            <div className="chat-meta">
              artifact_id: {artifact.id} | root: {artifact.root_artifact_id ?? "-"} | playbook_run_id: {artifact.playbook_run_id ?? "-"} | task_run_id: {artifact.task_run_id ?? "-"} | workflow_run_id: {artifact.workflow_run_id ?? "-"} | producing_node_key: {artifact.producing_node_key ?? "-"} | replay_source: {artifact.replay_source ?? "-"}
            </div>
            <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => void exportArtifact(artifact.id)} disabled={chatLoading}>
                Export markdown
              </button>
              <button className="refresh-button" onClick={() => void packageArtifact(artifact.id)} disabled={chatLoading}>
                Package
              </button>
              <button className="refresh-button" onClick={() => void showArtifactLineage(artifact.id)} disabled={chatLoading}>
                Lineage
              </button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No generated artifacts yet.</div>
        )}
      </div>
      <div className="approval-list">
        <h3>Workflow State</h3>
        <div className="chat-note">
          Workflow State tracks current step, checkpoints, and Agent Memory Snapshots for Conversation / Playbook / Task execution. Foundation only; not a full workflow editor and not ComfyUI.
        </div>
        <div className="chat-actions">
          <button className="refresh-button" onClick={() => void refreshWorkflows()}>
            <RefreshCcw size={15} />
            Refresh workflows
          </button>
        </div>
        {workflowRuns.length > 0 ? workflowRuns.slice(0, 5).map((workflow) => (
          <div key={workflow.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{workflow.source_type}</strong>
              <span>{workflow.status}</span>
              <span>step {workflow.current_step}</span>
              <span>node {workflow.current_node_key ?? "-"}</span>
            </div>
            <div className="chat-meta">
              workflow_run_id: {workflow.id} | graph_execution: {String(workflow.graph_execution)} | workflow_graph_id: {workflow.workflow_graph_id ?? "-"} | next: {(workflow.planned_next_nodes ?? []).join(",") || "-"} | checkpoints: {workflow.checkpoints.length}
            </div>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => { setSelectedWorkflowRunId(workflow.id); void refreshWorkflows(); }}>Inspect</button>
              <button className="refresh-button" onClick={() => void workflowClient.pause(workflow.id, settings).then(() => refreshWorkflows())} disabled={chatLoading}>Pause</button>
              <button className="refresh-button" onClick={() => void workflowClient.resume(workflow.id, settings).then(() => refreshWorkflows())} disabled={chatLoading}>Resume</button>
              <button className="refresh-button" onClick={() => void workflowClient.createReplay(workflow.id, settings).then(() => refreshWorkflows())} disabled={chatLoading}>Replay metadata</button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No workflow runs yet.</div>
        )}
        <h4>Workflow timeline {selectedWorkflowRunId ? `for ${selectedWorkflowRunId}` : ""}</h4>
        <div className="chat-note">
          Graph execution panel: current node, planned next nodes, skipped nodes, retry/fallback state. This is not a visual DAG editor.
        </div>
        <pre className="metadata-preview">{JSON.stringify({
          current_node: workflowPlanner?.current_node ?? null,
          next_nodes: workflowPlanner?.next_nodes ?? [],
          skipped_nodes: workflowPlanner?.skipped_nodes ?? [],
          retry_paths: workflowPlanner?.retry_paths ?? [],
          fallback_paths: workflowPlanner?.fallback_paths ?? [],
          condition_results: workflowPlanner?.condition_results ?? [],
        }, null, 2)}</pre>
        {workflowSteps.length > 0 ? workflowSteps.map((step) => (
          <div key={step.id} className="event-item">
            <strong>{step.step_name}</strong>
            <span>{step.status} | {step.step_type} | node: {step.node_key ?? "-"} | duration: {step.duration_ms ?? "-"}ms</span>
            {step.error ? <code>{step.error}</code> : null}
          </div>
        )) : (
          <div className="empty-chat">Select a workflow run to inspect steps.</div>
        )}
        <h4>Agent Memory Snapshots</h4>
        {memorySnapshots.length > 0 ? memorySnapshots.map((snapshot) => (
          <div key={snapshot.id} className="event-item">
            <strong>{snapshot.memory_type}</strong>
            <span>{snapshot.summary ?? "-"}</span>
          </div>
        )) : (
          <div className="empty-chat">No memory snapshots yet.</div>
        )}
      </div>
      <div className="approval-list">
        <h3>Task Runs</h3>
        <div className="chat-note">
          Background execution uses the in-process queue with lease, recovery, retry, cancel, approval resume, task timeline, and artifact linkage. It is not Celery, not Kubernetes, and not production HA.
        </div>
        <div className="chat-note">
          Scheduler: {String(schedulerHealth?.status ?? "unavailable")} | heartbeat: {String(schedulerHealth?.heartbeat_at ?? "-")} | recovered: {String(schedulerHealth?.recovered_task_count ?? 0)}
        </div>
        <div className="chat-actions">
          <button className="refresh-button" onClick={() => void refreshTaskRuns()}>
            <RefreshCcw size={15} />
            Refresh task status
          </button>
        </div>
        {taskRuns.length > 0 ? taskRuns.slice(0, 8).map((task) => (
          <div key={task.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{task.task_type}</strong>
              <span>{task.status}</span>
            </div>
            <div className="chat-meta">
              task_run_id: {task.id} | workflow_run_id: {task.workflow_run_id ?? "-"} | step: {task.current_step} | retry: {task.retry_count}/{task.max_retries} | recoverable: {String(task.recoverable)} | lease: {task.lease_expires_at ?? "-"}
            </div>
            <p>{String(task.error ?? task.suggested_action ?? task.output_payload.summary ?? "No error")}</p>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => { setSelectedTaskRunId(task.id); void refreshTaskRuns(); }}>Events</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "retry")} disabled={chatLoading}>Retry</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "cancel")} disabled={chatLoading}>Cancel</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "resume")} disabled={chatLoading}>Resume</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "recover")} disabled={chatLoading}>Recover</button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No background task runs yet.</div>
        )}
        <h4>Task timeline {selectedTaskRunId ? `for ${selectedTaskRunId}` : ""}</h4>
        {taskEvents.length > 0 ? taskEvents.map((event) => (
          <div key={event.id} className="event-item">
            <strong>{event.event_type}</strong>
            <span>{event.message ?? "-"}</span>
            <code>{JSON.stringify(event.payload)}</code>
          </div>
        )) : (
          <div className="empty-chat">Select a task run to inspect its timeline.</div>
        )}
      </div>
      <div className="chat-input-row">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type one sentence to trigger Planning / Agent / Tool / Worker runtime foundation..."
        />
        <button className="action-button" onClick={() => void sendConversationMessage()} disabled={chatLoading}>
          <Send size={16} />
          Send and run
        </button>
        <button className="action-button" onClick={() => void sendBackgroundConversation()} disabled={chatLoading}>
          <PlayCircle size={16} />
          Run background
        </button>
      </div>
    </section>
  );
}
function BrowserSessionsPanel() {
  const [sessions, setSessions] = useState<BrowserRuntimeSession[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [events, setEvents] = useState<BrowserRuntimeEvent[]>([]);
  const [snapshots, setSnapshots] = useState<BrowserRuntimeSnapshot[]>([]);
  const [replay, setReplay] = useState<BrowserRuntimeReplay | null>(null);
  const [replayExportPath, setReplayExportPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const refreshSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await browserRuntimeClient.listSessions();
      setSessions(response.items);
      setLastUpdated(new Date().toLocaleString());
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Browser Runtime API unreachable");
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshTimeline = useCallback(
    async (sessionId: string) => {
      setLoading(true);
      setError(null);
      try {
        const [nextEvents, nextSnapshots] = await Promise.all([
          browserRuntimeClient.listEvents(sessionId),
          browserRuntimeClient.listSnapshots(sessionId),
        ]);
        setSelectedSessionId(sessionId);
        setEvents(nextEvents.items);
        setSnapshots(nextSnapshots.items);
        setLastUpdated(new Date().toLocaleString());
      } catch (nextError) {
        setError(nextError instanceof Error ? nextError.message : "Browser Runtime timeline API unreachable");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const createReplay = async () => {
    if (!selectedSessionId) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextReplay = await browserRuntimeClient.createReplay(selectedSessionId);
      const exported = await browserRuntimeClient.exportReplay(nextReplay.id);
      setReplay(exported.replay);
      setReplayExportPath(exported.export_path);
      await refreshTimeline(selectedSessionId);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Create browser runtime replay failed");
    } finally {
      setLoading(false);
    }
  };

  const closeSession = async (sessionId: string) => {
    setLoading(true);
    setError(null);
    try {
      await browserRuntimeClient.closeSession(sessionId);
      await refreshSessions();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Close browser runtime session failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refreshSessions();
  }, [refreshSessions]);

  return (
    <section className="panel browser-sessions-panel">
      <div className="panel-title logs-title">
        <span>
          <Server size={18} />
          <h2>Browser Sessions</h2>
        </span>
        <button className="refresh-button" onClick={() => void refreshSessions()} disabled={loading}>
          <RefreshCcw size={15} />
          Refresh
        </button>
      </div>
      <div className="chat-meta">
        API: {browserRuntimeClient.baseUrl} | workspace: {browserRuntimeClient.workspaceId} | last updated: {lastUpdated ?? "-"}
      </div>
      {error ? (
        <div className="inline-error">
          <AlertTriangle size={16} />
          {error}
        </div>
      ) : null}
      <div className="session-table">
        <div className="session-row session-row-head">
          <span>session</span>
          <span>worker</span>
          <span>browser</span>
          <span>status</span>
          <span>current_url</span>
          <span>created_at</span>
          <span>action</span>
        </div>
        {sessions.length > 0 ? (
          sessions.map((session) => (
            <div className="session-row" key={session.id}>
              <span>{session.id}</span>
              <span>{session.worker_id}</span>
              <span>{session.browser}</span>
              <span>{session.session_status}</span>
              <span>{session.current_url ?? "-"}</span>
              <span>{session.created_at}</span>
              <span className="session-actions">
                <button className="icon-button" onClick={() => void refreshTimeline(session.id)} disabled={loading}>
                  <RefreshCcw size={15} />
                  Inspect
                </button>
                <button className="icon-button" onClick={() => void closeSession(session.id)} disabled={loading}>
                  <XCircle size={15} />
                  Close
                </button>
              </span>
            </div>
          ))
        ) : (
          <div className="empty-chat session-empty">No active remote browser runtime sessions.</div>
        )}
      </div>
      <div className="runtime-debug-grid">
        <section className="runtime-debug-card">
          <div className="runtime-debug-title">
            <strong>Timeline</strong>
            <button className="refresh-button" onClick={() => selectedSessionId && void refreshTimeline(selectedSessionId)} disabled={!selectedSessionId || loading}>
              <RefreshCcw size={14} />
              Refresh events
            </button>
          </div>
          {events.length > 0 ? (
            <div className="runtime-timeline">
              {events.map((event) => (
                <div key={event.id} className={`runtime-event runtime-event-${event.status}`}>
                  <span>{event.event_type}</span>
                  <p>{event.message ?? "-"}</p>
                  <small>
                    {event.duration_ms ?? "-"}ms | {event.created_at}
                  </small>
                  {event.error ? <em>{event.error}</em> : null}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-chat">Select a browser session to view timeline events.</div>
          )}
        </section>
        <section className="runtime-debug-card">
          <div className="runtime-debug-title">
            <strong>Snapshots</strong>
            <button className="refresh-button" onClick={() => selectedSessionId && void refreshTimeline(selectedSessionId)} disabled={!selectedSessionId || loading}>
              <RefreshCcw size={14} />
              Refresh snapshots
            </button>
          </div>
          {snapshots.length > 0 ? (
            <div className="snapshot-list">
              {snapshots.map((snapshot) => (
                <div key={snapshot.id} className="snapshot-item">
                  <span>{snapshot.snapshot_type}</span>
                  <p>{snapshot.page_title ?? snapshot.url ?? "-"}</p>
                  <small>
                    html: {snapshot.html_path ?? "-"} | text: {snapshot.text_path ?? "-"} | screenshot:{" "}
                    {snapshot.screenshot_path ?? "-"}
                  </small>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-chat">No page snapshots or screenshot history loaded.</div>
          )}
        </section>
        <section className="runtime-debug-card replay-card">
          <div className="runtime-debug-title">
            <strong>Replay metadata</strong>
            <button className="refresh-button" onClick={() => void createReplay()} disabled={!selectedSessionId || loading}>
              <RotateCcw size={14} />
              Create replay
            </button>
          </div>
          <p className="chat-note">Replay is metadata-only. It does not re-run browser actions.</p>
          <pre className="replay-view">
            {replay ? JSON.stringify({ replay, export_path: replayExportPath }, null, 2) : "No replay metadata generated."}
          </pre>
        </section>
      </div>
    </section>
  );
}

function App() {
  const [status, setStatus] = useState<WorkerStatus>(fallbackStatus);
  const [health, setHealth] = useState<WorkerHealth | null>(null);
  const [logs, setLogs] = useState<WorkerLogs>({ lines: [] });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<ControlAction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setError(null);
      const [nextStatus, nextHealth, nextLogs] = await Promise.all([
        localWorkerClient.getStatus(),
        localWorkerClient.getHealth(),
        localWorkerClient.getLogs(200),
      ]);
      setStatus({ ...fallbackStatus, ...nextStatus });
      setHealth(nextHealth);
      setLogs(nextLogs);
      setLastRefresh(new Date().toLocaleString());
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Worker API unreachable");
      setHealth(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  const runControl = async (action: ControlAction) => {
    setActionLoading(action);
    setError(null);
    try {
      const nextStatus = await localWorkerClient[action]();
      setStatus({ ...fallbackStatus, ...nextStatus });
      await refresh();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Worker API unreachable");
    } finally {
      setActionLoading(null);
    }
  };

  const latestLogs = useMemo(() => logs.lines.slice(-120), [logs.lines]);
  const apiUnreachable = Boolean(error && !health);

  return (
    <main className="app-shell min-h-screen">
      <section className="topbar">
        <div>
          <p className="eyeline">AI Ops Worker Console</p>
          <h1>Local Worker Runtime</h1>
        </div>
        <div className="topbar-status">
          <StatusBadge label="Runtime" active={status.runtime_running} />
          <StatusBadge label="Heartbeat" active={status.heartbeat_running} />
        </div>
      </section>

      {apiUnreachable ? (
        <section className="alert-panel">
          <WifiOff size={22} />
          <div>
            <strong>Worker API unreachable</strong>
            <p>
              Worker Runtime is not running. 请确认 worker_client 是否启动；请确认端口是否为 9100.
            </p>
            <code>{localWorkerClient.baseUrl}</code>
          </div>
        </section>
      ) : null}

      <section className="layout-grid">
        <section className="panel dashboard-panel">
          <div className="panel-title">
            <Server size={18} />
            <h2>Dashboard</h2>
          </div>
          <div className="field-grid">
            <Field label="worker_name" value={status.worker_name} />
            <Field label="worker_id" value={status.worker_id} />
            <Field label="workspace_id" value={status.workspace_id} />
            <Field label="server_url" value={status.server_url} />
            <Field label="registered" value={String(status.registered)} />
            <Field label="runtime_running" value={String(status.runtime_running)} />
            <Field label="heartbeat_running" value={String(status.heartbeat_running)} />
            <Field label="current_status" value={status.current_status} />
            <Field label="last_heartbeat_at" value={status.last_heartbeat_at} />
            <Field label="last_error" value={status.last_error ?? "-"} />
          </div>
        </section>

        <section className="panel control-panel">
          <div className="panel-title">
            <Activity size={18} />
            <h2>Runtime Control</h2>
          </div>
          <div className="control-grid">
            <ActionButton
              icon={<PlayCircle size={16} />}
              label="Start Runtime"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("startRuntime")}
            />
            <ActionButton
              icon={<Square size={16} />}
              label="Stop Runtime"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("stopRuntime")}
            />
            <ActionButton
              icon={<RotateCcw size={16} />}
              label="Restart Runtime"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("restartRuntime")}
            />
            <ActionButton
              icon={<Wifi size={16} />}
              label="Start Heartbeat"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("startHeartbeat")}
            />
            <ActionButton
              icon={<WifiOff size={16} />}
              label="Stop Heartbeat"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("stopHeartbeat")}
            />
          </div>
          <div className="control-note">
            {actionLoading ? `Running ${actionLoading}...` : loading ? "Loading local worker state..." : `Last refresh: ${lastRefresh ?? "-"}`}
          </div>
        </section>

        <section className="panel connection-panel">
          <div className="panel-title">
            <Wifi size={18} />
            <h2>Connection Info</h2>
          </div>
          <div className="field-grid compact">
            <Field label="local_api" value={localWorkerClient.baseUrl} />
            <Field label="server_url" value={status.server_url} />
            <Field label="worker_base_url" value={status.worker_base_url} />
            <Field label="runtime_port" value={status.runtime_port} />
            <Field label="openclaw_enabled" value={String(status.openclaw_enabled)} />
            <Field label="browser_enabled" value={String(status.browser_enabled)} />
          </div>
        </section>

        <ChatPanel />
        <BrowserSessionsPanel />

        <section className="panel logs-panel">
          <div className="panel-title logs-title">
            <span>
              <TerminalSquare size={18} />
              <h2>Logs</h2>
            </span>
            <button className="refresh-button" onClick={() => void refresh()}>
              <RefreshCcw size={15} />
              Refresh
            </button>
          </div>
          {error ? (
            <div className="inline-error">
              <AlertTriangle size={16} />
              {error}
            </div>
          ) : null}
          <pre className="log-view">
            {latestLogs.length > 0
              ? latestLogs.map((line, index) => (
                  <span key={`${line}-${index}`} className={isErrorLog(line) ? "log-error" : undefined}>
                    {line}
                    {"\n"}
                  </span>
                ))
              : "No logs available."}
          </pre>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

