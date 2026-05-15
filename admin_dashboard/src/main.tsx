import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  Bot,
  Brain,
  ClipboardList,
  Database,
  FileText,
  Gauge,
  HardDrive,
  History,
  KeyRound,
  LayoutDashboard,
  MessageSquareText,
  MonitorCheck,
  PlayCircle,
  RefreshCcw,
  Search,
  Send,
  Server,
  Settings,
  ShieldCheck,
  TerminalSquare,
  Users,
} from "lucide-react";
import {
  AdminSettings,
  auditApi,
  browserRuntimeApi,
  healthApi,
  JsonRecord,
  openclawApi,
  ragApi,
  readAdminSettings,
  safeRequest,
  tasksApi,
  toItems,
  workersApi,
  writeAdminSettings,
} from "./api/client";
import {
  conversationClient,
  ConversationApproval,
  ConversationEvent,
  ConversationMessage,
  ConversationPlaybook,
  ConversationPlaybookRun,
  ConversationThread,
} from "./api/conversationClient";
import { outputArtifactClient, OutputArtifact } from "./api/outputArtifactClient";
import { taskRunClient, TaskRun, TaskRunDiagnostics, TaskRunEvent, TaskSchedulerHealth } from "./api/taskRunClient";
import "./styles.css";

type PageKey =
  | "overview"
  | "workers"
  | "browser-runtime"
  | "conversations"
  | "playbooks"
  | "output-library"
  | "tasks"
  | "openclaw"
  | "audit-logs"
  | "rag-documents"
  | "settings";

interface PageDefinition {
  key: PageKey;
  label: string;
  icon: React.ReactNode;
}

interface AsyncState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  updatedAt: string | null;
}

const pages: PageDefinition[] = [
  { key: "overview", label: "Overview", icon: <LayoutDashboard size={18} /> },
  { key: "workers", label: "Workers", icon: <Server size={18} /> },
  { key: "browser-runtime", label: "Browser Runtime", icon: <MonitorCheck size={18} /> },
  { key: "conversations", label: "Conversations", icon: <MessageSquareText size={18} /> },
  { key: "playbooks", label: "Playbooks", icon: <History size={18} /> },
  { key: "output-library", label: "Output Library", icon: <FileText size={18} /> },
  { key: "tasks", label: "Tasks", icon: <ClipboardList size={18} /> },
  { key: "openclaw", label: "OpenClaw", icon: <Bot size={18} /> },
  { key: "audit-logs", label: "Audit Logs", icon: <ShieldCheck size={18} /> },
  { key: "rag-documents", label: "RAG / Documents", icon: <Database size={18} /> },
  { key: "settings", label: "Settings", icon: <Settings size={18} /> },
];

const taskStatuses = ["pending", "queued", "running", "waiting_approval", "retrying", "failed", "completed", "cancelled", "expired"];

function emptyState<T>(): AsyncState<T> {
  return { data: null, error: null, loading: false, updatedAt: null };
}

function nowLabel(): string {
  return new Date().toLocaleString();
}

function valueAt(record: JsonRecord | null | undefined, keys: string[], fallback = "-"): string {
  if (!record) {
    return fallback;
  }
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      return String(value);
    }
  }
  return fallback;
}

function rowId(record: JsonRecord, preferredKeys: string[]): string {
  return valueAt(record, preferredKeys, JSON.stringify(record).slice(0, 48));
}

function shortJson(value: unknown, limit = 110): string {
  if (value === null || value === undefined) {
    return "-";
  }
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  const rendered = JSON.stringify(value);
  return rendered.length > limit ? `${rendered.slice(0, limit)}...` : rendered;
}

function useAutoRefresh(enabled: boolean, intervalMs: number, callback: () => void): void {
  useEffect(() => {
    if (!enabled) {
      return undefined;
    }
    callback();
    const timer = window.setInterval(callback, intervalMs);
    return () => window.clearInterval(timer);
  }, [callback, enabled, intervalMs]);
}

function StatusPill({ value }: { value: React.ReactNode }) {
  const label = String(value ?? "unknown");
  const variant = /online|active|healthy|completed|success|true/i.test(label)
    ? "ok"
    : /failed|error|offline|timeout|false|revoked/i.test(label)
      ? "bad"
      : "muted";
  return <span className={`status-pill status-pill-${variant}`}>{label}</span>;
}

function DataCard({
  title,
  value,
  detail,
  icon,
  warning,
}: {
  title: string;
  value: React.ReactNode;
  detail?: React.ReactNode;
  icon: React.ReactNode;
  warning?: boolean;
}) {
  return (
    <section className={`metric-card ${warning ? "metric-card-warning" : ""}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <p>{title}</p>
        <strong>{value}</strong>
        {detail ? <span>{detail}</span> : null}
      </div>
    </section>
  );
}

function Panel({
  title,
  description,
  children,
  action,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>{title}</h2>
          {description ? <p>{description}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function LoadNotice<T>({ state }: { state: AsyncState<T> }) {
  if (state.error) {
    return (
      <div className="notice notice-error">
        <AlertTriangle size={16} />
        {state.error}
      </div>
    );
  }
  if (state.loading) {
    return <div className="notice">Loading...</div>;
  }
  return null;
}

function JsonPreview({ value }: { value: unknown }) {
  return <pre className="json-preview">{shortJson(value, 1600)}</pre>;
}

function Table({
  rows,
  columns,
  emptyLabel,
  selectedId,
  onSelect,
}: {
  rows: JsonRecord[];
  columns: { key: string; label: string; aliases?: string[] }[];
  emptyLabel: string;
  selectedId?: string | null;
  onSelect?: (row: JsonRecord) => void;
}) {
  if (!rows.length) {
    return <div className="empty-table">{emptyLabel}</div>;
  }
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const id = rowId(row, ["id", "worker_id", "session_id", "thread_id", "task_id"]);
            return (
              <tr
                key={id}
                className={`${onSelect ? "selectable-row" : ""} ${selectedId === id ? "selected-row" : ""}`}
                onClick={() => onSelect?.(row)}
              >
                {columns.map((column) => {
                  const keys = [column.key, ...(column.aliases || [])];
                  const value = keys.map((key) => row[key]).find((candidate) => candidate !== undefined);
                  return <td key={`${id}-${column.key}`}>{renderCell(value)}</td>;
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function renderCell(value: unknown): React.ReactNode {
  if (typeof value === "string" && /^(active|online|offline|failed|completed|pending|running|healthy|warning|error|true|false)$/i.test(value)) {
    return <StatusPill value={value} />;
  }
  if (typeof value === "boolean") {
    return <StatusPill value={value} />;
  }
  if (value && typeof value === "object") {
    return <code>{shortJson(value)}</code>;
  }
  return <span>{String(value ?? "-")}</span>;
}

function OverviewPage({ settings }: { settings: AdminSettings }) {
  const [state, setState] = useState<AsyncState<JsonRecord>>(emptyState());

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    const [health, workerSummary, taskSummary, taskRuns, schedulerHealth, openclawHealth, sessions, conversations] = await Promise.all([
      safeRequest<JsonRecord>("/health", {}, settings),
      safeRequest<JsonRecord>("/browser-workers/health/summary", {}, settings),
      safeRequest<JsonRecord>("/observability/summary", {}, settings),
      safeRequest<JsonRecord>("/task-runs", {}, settings),
      safeRequest<JsonRecord>("/task-scheduler/health", {}, settings),
      safeRequest<JsonRecord>("/openclaw/health", {}, settings),
      safeRequest<JsonRecord>("/browser-runtime/sessions", {}, settings),
      safeRequest<JsonRecord>("/conversations", {}, settings),
    ]);
    const data: JsonRecord = {
      health: health.ok ? health.data : { unavailable: health.error },
      workerSummary: workerSummary.ok ? workerSummary.data : { unavailable: workerSummary.error },
      taskSummary: taskSummary.ok ? taskSummary.data : { unavailable: taskSummary.error },
      taskRuns: taskRuns.ok ? taskRuns.data : { unavailable: taskRuns.error },
      schedulerHealth: schedulerHealth.ok ? schedulerHealth.data : { unavailable: schedulerHealth.error },
      openclawHealth: openclawHealth.ok ? openclawHealth.data : { unavailable: openclawHealth.error },
      browserRuntimeSessions: sessions.ok ? sessions.data : { unavailable: sessions.error },
      conversations: conversations.ok ? conversations.data : { unavailable: conversations.error },
    };
    setState({ data, error: null, loading: false, updatedAt: nowLabel() });
  }, [settings]);

  useAutoRefresh(true, settings.refreshIntervalMs, load);

  const sessionsCount = state.data ? toItems(state.data.browserRuntimeSessions).length : "-";
  const conversationCount = state.data ? toItems(state.data.conversations).length : "-";
  const taskRuns = state.data ? toItems(state.data.taskRuns) : [];
  const taskRunCounts = taskRuns.reduce<Record<string, number>>((counts, item) => {
    const status = String(item.status ?? "unknown");
    counts[status] = (counts[status] || 0) + 1;
    return counts;
  }, {});
  const workerSummary = (state.data?.workerSummary as JsonRecord | undefined) || null;
  const schedulerHealth = (state.data?.schedulerHealth as JsonRecord | undefined) || null;
  const health = (state.data?.health as JsonRecord | undefined) || null;
  const openclaw = (state.data?.openclawHealth as JsonRecord | undefined) || null;

  return (
    <div className="page-stack">
      <section className="metrics-grid">
        <DataCard title="API health" value={valueAt(health, ["status", "reachable", "success"])} icon={<Gauge size={20} />} />
        <DataCard
          title="Workers"
          value={`${valueAt(workerSummary, ["online_count"], "0")} online`}
          detail={`${valueAt(workerSummary, ["offline_count"], "0")} offline`}
          icon={<Server size={20} />}
        />
        <DataCard title="Browser sessions" value={sessionsCount} detail="runtime sessions" icon={<MonitorCheck size={20} />} />
        <DataCard title="Conversations" value={conversationCount} detail="foundation threads" icon={<MessageSquareText size={20} />} />
        <DataCard
          title="Task runs"
          value={`${taskRunCounts.queued ?? 0} queued / ${taskRunCounts.running ?? 0} running`}
          detail={`${taskRunCounts.failed ?? 0} failed / ${taskRunCounts.retrying ?? 0} retrying`}
          icon={<ClipboardList size={20} />}
        />
        <DataCard
          title="Scheduler"
          value={valueAt(schedulerHealth, ["status"], "unavailable")}
          detail={`${valueAt(schedulerHealth, ["active_task_count"], "0")} active / ${valueAt(schedulerHealth, ["recovered_task_count"], "0")} recovered`}
          icon={<Gauge size={20} />}
        />
        <DataCard
          title="OpenClaw"
          value={valueAt(openclaw, ["provider"], "unavailable")}
          detail="mock adapter only"
          icon={<Bot size={20} />}
        />
      </section>
      <LoadNotice state={state} />
      <Panel title="Recent System Snapshot" description="Partial API failures are shown inline so the dashboard remains usable.">
        <div className="json-grid">
          <JsonPreview value={state.data?.health} />
          <JsonPreview value={state.data?.taskSummary} />
          <JsonPreview value={state.data?.taskRuns} />
          <JsonPreview value={state.data?.schedulerHealth} />
          <JsonPreview value={state.data?.workerSummary} />
          <JsonPreview value={state.data?.openclawHealth} />
        </div>
        <div className="last-updated">Last updated: {state.updatedAt ?? "-"}</div>
      </Panel>
    </div>
  );
}

function WorkersPage({ settings }: { settings: AdminSettings }) {
  const [workers, setWorkers] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [available, setAvailable] = useState<JsonRecord[]>([]);
  const [summary, setSummary] = useState<JsonRecord | null>(null);

  const load = useCallback(async () => {
    setWorkers((current) => ({ ...current, loading: true, error: null }));
    try {
      const [list, availableList, healthSummary] = await Promise.all([
        workersApi.list(settings),
        workersApi.available(settings),
        workersApi.healthSummary(settings),
      ]);
      setWorkers({ data: toItems(list), error: null, loading: false, updatedAt: nowLabel() });
      setAvailable(toItems(availableList));
      setSummary(healthSummary);
    } catch (error) {
      setWorkers({
        data: null,
        error: error instanceof Error ? error.message : "Worker API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  useAutoRefresh(true, settings.refreshIntervalMs, load);

  return (
    <Panel
      title="Workers"
      description="Read-only browser worker inventory. Secret rotation and revoke controls stay outside this foundation UI."
      action={<RefreshButton onClick={load} />}
    >
      <LoadNotice state={workers} />
      <div className="summary-strip">
        <span>Available workers: {available.length}</span>
        <span>Health summary: {summary ? shortJson(summary, 180) : "-"}</span>
      </div>
      <Table
        rows={workers.data || []}
        emptyLabel="No workers found for this workspace."
        columns={[
          { key: "id", label: "worker_id", aliases: ["worker_id"] },
          { key: "worker_name", label: "worker_name" },
          { key: "status", label: "status" },
          { key: "worker_type", label: "worker_type" },
          { key: "base_url", label: "base_url" },
          { key: "capabilities", label: "capabilities" },
          { key: "active_sessions", label: "active_sessions" },
          { key: "max_sessions", label: "max_sessions" },
          { key: "last_heartbeat_at", label: "last_heartbeat_at" },
          { key: "auth_status", label: "auth_status" },
        ]}
      />
      <div className="last-updated">Last updated: {workers.updatedAt ?? "-"}</div>
    </Panel>
  );
}

function BrowserRuntimePage({ settings }: { settings: AdminSettings }) {
  const [sessions, setSessions] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [selectedSession, setSelectedSession] = useState<JsonRecord | null>(null);
  const [events, setEvents] = useState<JsonRecord[]>([]);
  const [snapshots, setSnapshots] = useState<JsonRecord[]>([]);
  const [replay, setReplay] = useState<JsonRecord | null>(null);
  const selectedId = selectedSession ? rowId(selectedSession, ["id", "session_id"]) : null;

  const load = useCallback(async () => {
    setSessions((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await browserRuntimeApi.listSessions(settings);
      const rows = toItems(response);
      setSessions({ data: rows, error: null, loading: false, updatedAt: nowLabel() });
      if (!selectedSession && rows.length) {
        setSelectedSession(rows[0]);
      }
    } catch (error) {
      setSessions({
        data: null,
        error: error instanceof Error ? error.message : "Browser Runtime API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [selectedSession, settings]);

  const loadDetails = useCallback(
    async (row: JsonRecord) => {
      const id = rowId(row, ["id", "session_id"]);
      setSelectedSession(row);
      try {
        const [eventList, snapshotList] = await Promise.all([
          browserRuntimeApi.listEvents(id, settings),
          browserRuntimeApi.listSnapshots(id, settings),
        ]);
        setEvents(toItems(eventList));
        setSnapshots(toItems(snapshotList));
      } catch {
        setEvents([]);
        setSnapshots([]);
      }
    },
    [settings],
  );

  const createReplay = async () => {
    if (!selectedId) {
      return;
    }
    const created = await browserRuntimeApi.createReplay(selectedId, settings);
    const replayId = valueAt(created, ["id", "replay_id"]);
    const exported = replayId !== "-" ? await browserRuntimeApi.exportReplay(replayId, settings) : created;
    setReplay({ created, exported });
  };

  useAutoRefresh(true, settings.refreshIntervalMs, load);
  useEffect(() => {
    if (selectedSession) {
      void loadDetails(selectedSession);
    }
  }, [loadDetails, selectedSession]);

  return (
    <div className="split-page">
      <Panel title="Browser Runtime Sessions" description="Remote worker browser sessions and lifecycle metadata." action={<RefreshButton onClick={load} />}>
        <LoadNotice state={sessions} />
        <Table
          rows={sessions.data || []}
          selectedId={selectedId}
          onSelect={(row) => void loadDetails(row)}
          emptyLabel="No browser runtime sessions found."
          columns={[
            { key: "id", label: "session_id", aliases: ["session_id"] },
            { key: "worker_id", label: "worker_id" },
            { key: "browser", label: "browser" },
            { key: "session_status", label: "status" },
            { key: "created_at", label: "created_at" },
            { key: "last_activity_at", label: "last_activity_at" },
            { key: "metadata", label: "metadata" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <div className="detail-title">
          <h2>Timeline / Snapshots / Replay</h2>
          <button className="primary-button" onClick={() => void createReplay()} disabled={!selectedId}>
            <History size={15} />
            Create replay metadata
          </button>
        </div>
        <p className="foundation-note">Replay is metadata-only. It does not re-execute browser actions.</p>
        <h3>Events</h3>
        <Timeline rows={events} primary="event_type" secondary="message" />
        <h3>Snapshots</h3>
        <Table
          rows={snapshots}
          emptyLabel="No snapshots."
          columns={[
            { key: "snapshot_type", label: "type" },
            { key: "url", label: "url" },
            { key: "page_title", label: "page_title" },
            { key: "screenshot_path", label: "screenshot_path" },
            { key: "html_path", label: "html_path" },
          ]}
        />
        <h3>Replay Metadata</h3>
        <JsonPreview value={replay || { status: "not created" }} />
      </aside>
    </div>
  );
}

function ConversationsPage({ settings }: { settings: AdminSettings }) {
  const [threads, setThreads] = useState<AsyncState<ConversationThread[]>>(emptyState());
  const [selectedThread, setSelectedThread] = useState<ConversationThread | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [events, setEvents] = useState<ConversationEvent[]>([]);
  const [approvals, setApprovals] = useState<ConversationApproval[]>([]);
  const [playbooks, setPlaybooks] = useState<ConversationPlaybook[]>([]);
  const [playbookRuns, setPlaybookRuns] = useState<ConversationPlaybookRun[]>([]);
  const [artifacts, setArtifacts] = useState<OutputArtifact[]>([]);
  const [selectedPlaybookName, setSelectedPlaybookName] = useState("browser_screenshot_report");
  const [newTitle, setNewTitle] = useState("Phase 37 frontend conversation test");
  const [messageInput, setMessageInput] = useState("请帮我生成一条短视频文案，并展示执行事件。");
  const [runStatus, setRunStatus] = useState("idle");
  const [connectionState, setConnectionState] = useState("unknown");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [autoRefreshEvents, setAutoRefreshEvents] = useState(false);
  const [lastRunMetadata, setLastRunMetadata] = useState<JsonRecord | null>(null);
  const selectedId = selectedThread?.id ?? null;

  const load = useCallback(async () => {
    setThreads((current) => ({ ...current, loading: true, error: null }));
    try {
      const [response, playbookResponse, runResponse] = await Promise.all([
        conversationClient.listThreads(settings),
        conversationClient.listPlaybooks(settings),
        conversationClient.listPlaybookRuns(settings),
      ]);
      setConnectionState("connected");
      setThreads({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setPlaybooks(playbookResponse.items ?? []);
      setPlaybookRuns(runResponse.items ?? []);
    } catch (error) {
      setConnectionState("disconnected");
      setThreads({
        data: null,
        error: error instanceof Error ? error.message : "AI Server unreachable",
        loading: false,
        updatedAt: nowLabel(),
      });
      setPlaybooks([]);
      setPlaybookRuns([]);
    }
  }, [settings]);

  const loadThread = useCallback(async (thread: ConversationThread) => {
    setSelectedThread(thread);
    setDetailError(null);
    try {
      const [messageList, eventList, approvalList, artifactList] = await Promise.all([
        conversationClient.listMessages(thread.id, settings),
        conversationClient.listEvents(thread.id, settings),
        conversationClient.listApprovals(thread.id, settings),
        outputArtifactClient.listArtifacts(settings, { threadId: thread.id }),
      ]);
      setMessages(messageList.items);
      setEvents(eventList.items);
      setApprovals(approvalList.items);
      setArtifacts(artifactList.items ?? []);
      const runResponse = await conversationClient.listPlaybookRuns(settings);
      setPlaybookRuns(runResponse.items ?? []);
      setConnectionState("connected");
    } catch (error) {
      setMessages([]);
      setEvents([]);
      setApprovals([]);
      setArtifacts([]);
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
    }
  }, [settings]);

  const createThread = async () => {
    const title = newTitle.trim() || `Conversation ${new Date().toLocaleString()}`;
    setRunStatus("creating thread");
    setDetailError(null);
    try {
      const thread = await conversationClient.createThread(
        { title, metadata: { source: "admin_dashboard", phase: "37" } },
        settings,
      );
      setSelectedThread(thread);
      setMessages([]);
      setEvents([]);
      setApprovals([]);
      setLastRunMetadata(null);
      setConnectionState("connected");
      await load();
      await loadThread(thread);
      setRunStatus("thread created");
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
      setRunStatus("error");
    }
  };

  const refreshSelected = useCallback(async () => {
    if (selectedThread) {
      await loadThread(selectedThread);
    }
  }, [loadThread, selectedThread]);

  const sendMessage = async () => {
    if (!selectedThread) {
      setDetailError("Create or select a thread before sending a message.");
      return;
    }
    const content = messageInput.trim();
    if (!content) {
      return;
    }
    setRunStatus("sending message");
    setDetailError(null);
    try {
      await conversationClient.sendMessage(
        selectedThread.id,
        { role: "user", content, metadata: { source: "admin_dashboard", phase: "37" } },
        settings,
      );
      await refreshSelected();
      setConnectionState("connected");
      setRunStatus("message sent");
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
      setRunStatus("error");
    }
  };

  const runConversation = async (
    mode: "auto_safe" | "review_first" = "auto_safe",
    executionMode: "immediate" | "background" | "scheduled" = "immediate",
  ) => {
    if (!selectedThread) {
      setDetailError("Create or select a thread before running conversation.");
      return;
    }
    const userMessages = messages.filter((message) => message.role === "user");
    const content = messageInput.trim() || userMessages[userMessages.length - 1]?.content || "";
    if (!content) {
      setDetailError("Run requires a message.");
      return;
    }
    setRunStatus(executionMode === "background" ? "queueing background task" : "running conversation");
    setDetailError(null);
    try {
      const response = await conversationClient.runConversation(
        selectedThread.id,
        content,
        settings,
        mode,
        selectedPlaybookName || null,
        executionMode,
      );
      setMessages((await conversationClient.listMessages(selectedThread.id, settings)).items);
      setApprovals((await conversationClient.listApprovals(selectedThread.id, settings)).items);
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items ?? []);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: selectedThread.id })).items ?? []);
      setEvents(response.events);
      setLastRunMetadata(response.result_metadata);
      setConnectionState("connected");
      setRunStatus(
        `mode: ${response.execution_mode} | task: ${response.task_run_id ?? "-"} | route: ${response.route_name} | tool: ${response.selected_tool ?? "none"} | risk: ${response.risk_level ?? "-"} | approval: ${response.approval_status ?? "-"} | success: ${response.success}`,
      );
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
      setRunStatus("error");
    }
  };

  const runSelectedPlaybook = async () => {
    const playbook = playbooks.find((item) => item.name === selectedPlaybookName);
    if (!playbook) {
      setDetailError("Select an available playbook before running.");
      return;
    }
    setRunStatus("running playbook");
    setDetailError(null);
    try {
      const run = await conversationClient.runPlaybook(
        playbook.id,
        { message: messageInput, url: "https://example.com", topic: messageInput || "AI automation operations" },
        settings,
        "review_first",
        selectedThread?.id ?? null,
      );
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items ?? []);
      if (selectedThread) {
        await loadThread(selectedThread);
      }
      setRunStatus(`Playbook run ${run.status}: ${run.id}`);
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "Playbook API unreachable");
      setRunStatus("error");
    }
  };

  const mutateApproval = async (approvalId: string, action: "approve" | "reject" | "cancel" | "execute") => {
    if (!selectedThread) {
      return;
    }
    setRunStatus(`${action} approval`);
    setDetailError(null);
    try {
      if (action === "approve") {
        await conversationClient.approveApproval(approvalId, "Looks safe to execute.", settings);
      } else if (action === "reject") {
        await conversationClient.rejectApproval(approvalId, "Need to rewrite before execution.", settings);
      } else if (action === "cancel") {
        await conversationClient.cancelApproval(approvalId, "Cancelled before execution.", settings);
      } else {
        const response = await conversationClient.executeApproval(approvalId, settings);
        setLastRunMetadata(response.result_metadata);
        setEvents(response.events);
      }
      await loadThread(selectedThread);
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items ?? []);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: selectedThread.id })).items ?? []);
      setConnectionState("connected");
      setRunStatus(`${action} approval completed`);
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "Approval API unreachable");
      setRunStatus("error");
    }
  };

  const saveMessageAsArtifact = async (message: ConversationMessage) => {
    setRunStatus("saving artifact");
    setDetailError(null);
    try {
      await outputArtifactClient.createFromMessage(message.id, settings);
      if (selectedThread) {
        setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: selectedThread.id })).items ?? []);
        await loadThread(selectedThread);
      }
      setRunStatus("artifact saved");
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Output Artifact API unreachable");
      setRunStatus("artifact error");
    }
  };

  const exportArtifact = async (artifact: OutputArtifact) => {
    setRunStatus("exporting artifact");
    setDetailError(null);
    try {
      const exported = await outputArtifactClient.exportArtifact(artifact.id, "markdown", settings);
      setLastRunMetadata({ artifact_export: exported });
      setRunStatus(`artifact exported: ${exported.export_path}`);
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Artifact export failed");
      setRunStatus("artifact export error");
    }
  };

  useEffect(() => {
    if (!autoRefreshEvents || !selectedThread) {
      return undefined;
    }
    const timer = window.setInterval(() => {
      void refreshSelected();
    }, 5000);
    return () => window.clearInterval(timer);
  }, [autoRefreshEvents, refreshSelected, selectedThread]);

  useEffect(() => {
    void load();
  }, [load]);

  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const latestAssistantMessage = assistantMessages[assistantMessages.length - 1];
  const latestEventPayload = events.length > 0 ? events[events.length - 1].payload : { status: "no events" };
  const routeEvent = [...events].reverse().find((event) => event.event_type === "route_selected");

  return (
    <div className="split-page">
      <Panel
        title="Conversations"
        description="Conversation Runtime frontend integration. Polling event timeline only; this is not WebSocket, not SSE, and not a full ChatGPT UI."
        action={<RefreshButton onClick={load} />}
      >
        <div className="conversation-toolbar">
          <input value={newTitle} onChange={(event) => setNewTitle(event.target.value)} aria-label="Conversation title" />
          <button className="primary-button" onClick={() => void createThread()}>
            <MessageSquareText size={15} />
            Create thread
          </button>
        </div>
        <div className="summary-strip">
          <span>AI Server: <StatusPill value={connectionState} /></span>
          <span>workspace: {settings.workspaceId}</span>
          <span>user: {settings.userId}</span>
          <span>selected: {selectedThread?.id ?? "-"}</span>
        </div>
        <LoadNotice state={threads} />
        <Table
          rows={(threads.data || []) as unknown as JsonRecord[]}
          selectedId={selectedId}
          onSelect={(row) => void loadThread(row as unknown as ConversationThread)}
          emptyLabel="No conversation threads."
          columns={[
            { key: "id", label: "thread_id", aliases: ["thread_id"] },
            { key: "title", label: "title" },
            { key: "status", label: "status" },
            { key: "created_at", label: "created_at" },
            { key: "updated_at", label: "updated_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Messages / Events</h2>
        <p className="foundation-note">
          Foundation UI only. Event timeline is polling based; WebSocket and SSE remain placeholders.
        </p>
        <div className="chat-status-row">
          <span>Run status: <StatusPill value={runStatus} /></span>
          <span>Route selected: {valueAt(routeEvent?.payload as JsonRecord, ["route_name"], "-")}</span>
          <span>Selected tool: {valueAt(routeEvent?.payload as JsonRecord, ["selected_tool"], "-")}</span>
          <span>Latest assistant: {latestAssistantMessage?.content ?? "-"}</span>
        </div>
        {detailError ? (
          <div className="notice notice-error">
            <AlertTriangle size={16} />
            {detailError}
          </div>
        ) : null}
        <div className="conversation-compose">
          <textarea
            value={messageInput}
            onChange={(event) => setMessageInput(event.target.value)}
            placeholder="Send a user message, then run the conversation turn."
          />
          <div className="conversation-actions">
            <button className="ghost-button" onClick={() => void sendMessage()} disabled={!selectedThread}>
              <Send size={15} />
              Send message
            </button>
            <button className="primary-button" onClick={() => void runConversation()} disabled={!selectedThread}>
              <Activity size={15} />
              Run conversation auto_safe
            </button>
            <button className="ghost-button" onClick={() => void runConversation("review_first")} disabled={!selectedThread}>
              <AlertTriangle size={15} />
              Run review_first
            </button>
            <button className="ghost-button" onClick={() => void runConversation("review_first", "background")} disabled={!selectedThread}>
              <PlayCircle size={15} />
              Queue background
            </button>
            <button className="ghost-button" onClick={() => void refreshSelected()} disabled={!selectedThread}>
              <RefreshCcw size={15} />
              Refresh messages/events
            </button>
          </div>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={autoRefreshEvents}
              onChange={(event) => setAutoRefreshEvents(event.target.checked)}
            />
            Poll events every 5 seconds
          </label>
        </div>
        <h3>Playbook selector</h3>
        <p className="foundation-note">
          Conversation Playbooks standardize common flows. This is not a full workflow builder and still respects approval gates.
        </p>
        <div className="conversation-compose">
          <select value={selectedPlaybookName} onChange={(event) => setSelectedPlaybookName(event.target.value)}>
            {playbooks.map((playbook) => (
              <option key={playbook.id} value={playbook.name}>
                {playbook.name} | {playbook.risk_level} | {playbook.status}
              </option>
            ))}
          </select>
          <div className="summary-strip">
            <span>Playbook list: {playbooks.length}</span>
            <span>Selected: {selectedPlaybookName || "-"}</span>
            <span>Description: {playbooks.find((item) => item.name === selectedPlaybookName)?.description ?? "-"}</span>
          </div>
          <div className="conversation-actions">
            <button className="primary-button" onClick={() => void runSelectedPlaybook()}>
              <Activity size={15} />
              Run playbook
            </button>
            <button className="ghost-button" onClick={() => void runConversation("review_first")} disabled={!selectedThread}>
              <AlertTriangle size={15} />
              Run conversation with playbook
            </button>
          </div>
        </div>
        <h3>Playbook runs</h3>
        <div className="approval-list">
          {playbookRuns.length > 0 ? (
            playbookRuns.slice(0, 6).map((run) => (
              <div key={run.id} className="approval-card">
                <div className="approval-card-header">
                  <strong>run: {run.id}</strong>
                  <StatusPill value={run.status} />
                  <span>current_step: {run.current_step}</span>
                </div>
                <div className="chat-status-row">
                  <span>playbook_id: {run.playbook_id}</span>
                  <span>thread_id: {run.thread_id}</span>
                </div>
                <h4>Step timeline</h4>
                <JsonPreview value={run.output_payload?.steps ?? []} />
              </div>
            ))
          ) : (
            <div className="empty-chat">No Playbook runs yet. Try browser_screenshot_report or content_generation.</div>
          )}
        </div>
        <h3>Pending Approvals Panel</h3>
        <p className="foundation-note">
          Approval Flow foundation. Medium/high risk actions stay pending until a human approves and explicitly executes them.
        </p>
        <div className="approval-list">
          {approvals.length > 0 ? (
            approvals.map((approval) => (
              <div key={approval.id} className={`approval-card approval-risk-${approval.risk_level}`}>
                <div className="approval-card-header">
                  <strong>{approval.proposed_action}</strong>
                  <StatusPill value={`${approval.risk_level} risk`} />
                  <StatusPill value={approval.approval_status} />
                </div>
                <div className="chat-status-row">
                  <span>route: {approval.route_name}</span>
                  <span>tool: {approval.selected_tool ?? "none"}</span>
                  <span>approval_id: {approval.id}</span>
                </div>
                <JsonPreview value={approval.proposed_payload} />
                <div className="conversation-actions">
                  <button className="ghost-button" onClick={() => void mutateApproval(approval.id, "approve")} disabled={approval.approval_status !== "pending"}>
                    Approve
                  </button>
                  <button className="ghost-button" onClick={() => void mutateApproval(approval.id, "reject")} disabled={approval.approval_status !== "pending"}>
                    Reject
                  </button>
                  <button className="ghost-button" onClick={() => void mutateApproval(approval.id, "cancel")} disabled={!["pending", "approved"].includes(approval.approval_status)}>
                    Cancel
                  </button>
                  <button className="primary-button" onClick={() => void mutateApproval(approval.id, "execute")} disabled={approval.approval_status !== "approved"}>
                    Execute approved action
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-chat">No pending approvals yet. Try Run review_first with a browser request.</div>
          )}
        </div>
        <h3>Messages</h3>
        <div className="approval-list">
          {messages.length > 0 ? (
            messages.map((message) => (
              <div key={message.id} className="approval-card">
                <div className="approval-card-header">
                  <strong>{message.role}</strong>
                  <span>{message.created_at}</span>
                </div>
                <p>{message.content}</p>
                {message.role === "assistant" ? (
                  <button className="ghost-button" onClick={() => void saveMessageAsArtifact(message)}>
                    Save as Artifact
                  </button>
                ) : null}
              </div>
            ))
          ) : (
            <div className="empty-chat">No messages yet.</div>
          )}
        </div>
        <h3>Generated artifacts</h3>
        <div className="approval-list">
          {artifacts.length > 0 ? (
            artifacts.map((artifact) => (
              <div key={artifact.id} className="approval-card">
                <div className="approval-card-header">
                  <strong>{artifact.title}</strong>
                  <StatusPill value={artifact.artifact_type} />
                  <StatusPill value={artifact.source_type} />
                </div>
                <div className="chat-status-row">
                  <span>artifact_id: {artifact.id}</span>
                  <span>playbook_run_id: {artifact.playbook_run_id ?? "-"}</span>
                </div>
                <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
                <button className="ghost-button" onClick={() => void exportArtifact(artifact)}>
                  Export markdown
                </button>
              </div>
            ))
          ) : (
            <div className="empty-chat">No generated artifacts yet. Completed playbook runs will appear here.</div>
          )}
        </div>
        <h3>Events</h3>
        <Timeline rows={events as unknown as JsonRecord[]} primary="event_type" secondary="message" />
        <h3>Latest Event Payload</h3>
        <JsonPreview value={latestEventPayload} />
        <h3>Result Metadata</h3>
        <JsonPreview value={lastRunMetadata || { status: "run a conversation to see full bridge metadata" }} />
      </aside>
    </div>
  );
}

function PlaybooksPage({ settings }: { settings: AdminSettings }) {
  const [playbooks, setPlaybooks] = useState<AsyncState<ConversationPlaybook[]>>(emptyState());
  const [runs, setRuns] = useState<AsyncState<ConversationPlaybookRun[]>>(emptyState());

  const load = useCallback(async () => {
    setPlaybooks((current) => ({ ...current, loading: true, error: null }));
    setRuns((current) => ({ ...current, loading: true, error: null }));
    try {
      const [playbookResponse, runResponse] = await Promise.all([
        conversationClient.listPlaybooks(settings),
        conversationClient.listPlaybookRuns(settings),
      ]);
      setPlaybooks({ data: playbookResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setRuns({ data: runResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Playbook API unreachable";
      setPlaybooks({ data: null, error: message, loading: false, updatedAt: nowLabel() });
      setRuns({ data: null, error: message, loading: false, updatedAt: nowLabel() });
    }
  }, [settings]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="page-stack">
      <Panel
        title="Playbooks"
        description="Conversation Execution Templates & Playbooks. Built-in templates plus run history; not a full workflow builder."
        action={<RefreshButton onClick={load} />}
      >
        <LoadNotice state={playbooks} />
        <Table
          rows={(playbooks.data || []) as unknown as JsonRecord[]}
          emptyLabel="No playbooks."
          columns={[
            { key: "name", label: "name" },
            { key: "category", label: "category" },
            { key: "status", label: "status" },
            { key: "risk_level", label: "risk" },
            { key: "description", label: "description" },
          ]}
        />
      </Panel>
      <Panel title="Playbook Runs" description="Step timeline is stored in output_payload.steps.">
        <LoadNotice state={runs} />
        <Table
          rows={(runs.data || []) as unknown as JsonRecord[]}
          emptyLabel="No playbook runs."
          columns={[
            { key: "id", label: "run_id" },
            { key: "status", label: "status" },
            { key: "current_step", label: "current_step" },
            { key: "playbook_id", label: "playbook_id" },
            { key: "thread_id", label: "thread_id" },
          ]}
        />
      </Panel>
    </div>
  );
}

function OutputLibraryPage({ settings }: { settings: AdminSettings }) {
  const [artifacts, setArtifacts] = useState<AsyncState<OutputArtifact[]>>(emptyState());
  const [selectedArtifact, setSelectedArtifact] = useState<OutputArtifact | null>(null);
  const [artifactType, setArtifactType] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [exportPreview, setExportPreview] = useState<JsonRecord | null>(null);

  const load = useCallback(async () => {
    setArtifacts((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await outputArtifactClient.listArtifacts(settings, {
        artifactType: artifactType || undefined,
        sourceType: sourceType || undefined,
      });
      setArtifacts({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setArtifacts({
        data: null,
        error: error instanceof Error ? error.message : "Output Artifact API unreachable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [artifactType, settings, sourceType]);

  useEffect(() => {
    void load();
  }, [load]);

  const exportSelected = async (format: "markdown" | "json" | "txt") => {
    if (!selectedArtifact) {
      return;
    }
    const exported = await outputArtifactClient.exportArtifact(selectedArtifact.id, format, settings);
    setExportPreview(exported as unknown as JsonRecord);
    await load();
  };

  return (
    <div className="split-page">
      <Panel
        title="Output Library"
        description="Reusable Output Artifacts from Conversation, Playbook, Tool, Browser Runtime, RAG, ContentAgent, Planning, and OpenClaw mock. This is not a full DAM or cloud file manager."
        action={<RefreshButton onClick={load} />}
      >
        <div className="conversation-toolbar">
          <select value={artifactType} onChange={(event) => setArtifactType(event.target.value)} aria-label="artifact_type filter">
            <option value="">All artifact_type</option>
            {["content_draft", "report", "rag_answer", "screenshot", "html_snapshot", "plan", "json", "markdown", "text"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
          <select value={sourceType} onChange={(event) => setSourceType(event.target.value)} aria-label="source_type filter">
            <option value="">All source_type</option>
            {["conversation", "playbook", "tool", "browser_runtime", "rag", "content_agent", "planning", "openclaw_mock"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
        </div>
        <LoadNotice state={artifacts} />
        <Table
          rows={(artifacts.data || []) as unknown as JsonRecord[]}
          selectedId={selectedArtifact?.id ?? null}
          onSelect={(row) => setSelectedArtifact(row as unknown as OutputArtifact)}
          emptyLabel="No output artifacts yet."
          columns={[
            { key: "title", label: "title" },
            { key: "artifact_type", label: "artifact_type" },
            { key: "source_type", label: "source_type" },
            { key: "status", label: "status" },
            { key: "created_at", label: "created_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Artifact Detail</h2>
        {selectedArtifact ? (
          <>
            <div className="chat-status-row">
              <span>artifact_id: {selectedArtifact.id}</span>
              <span>thread_id: {selectedArtifact.thread_id ?? "-"}</span>
              <span>playbook_run_id: {selectedArtifact.playbook_run_id ?? "-"}</span>
              <span>task_run_id: {selectedArtifact.task_run_id ?? "-"}</span>
            </div>
            <div className="approval-card">
              <div className="approval-card-header">
                <strong>{selectedArtifact.title}</strong>
                <StatusPill value={selectedArtifact.artifact_type} />
                <StatusPill value={selectedArtifact.source_type} />
              </div>
              <p>{selectedArtifact.summary ?? selectedArtifact.file_path ?? "No summary"}</p>
              <JsonPreview value={selectedArtifact.metadata} />
            </div>
            <h3>Preview content</h3>
            <pre className="json-preview">{selectedArtifact.content || selectedArtifact.file_path || "File-only artifact; see metadata/path."}</pre>
            <div className="conversation-actions">
              <button className="ghost-button" onClick={() => void exportSelected("markdown")}>Export markdown</button>
              <button className="ghost-button" onClick={() => void exportSelected("json")}>Export json</button>
              <button className="ghost-button" onClick={() => void exportSelected("txt")}>Export txt</button>
            </div>
            <h3>Export result</h3>
            <JsonPreview value={exportPreview ?? { status: "export an artifact to see output path" }} />
          </>
        ) : (
          <div className="empty-chat">Select an artifact to preview content and export markdown/json/txt.</div>
        )}
      </aside>
    </div>
  );
}

function TasksPage({ settings }: { settings: AdminSettings }) {
  const [status, setStatus] = useState("queued");
  const [recoveryFilter, setRecoveryFilter] = useState("all");
  const [tasks, setTasks] = useState<AsyncState<TaskRun[]>>(emptyState());
  const [schedulerHealth, setSchedulerHealth] = useState<TaskSchedulerHealth | null>(null);
  const [selectedTask, setSelectedTask] = useState<TaskRun | null>(null);
  const [diagnostics, setDiagnostics] = useState<TaskRunDiagnostics | null>(null);
  const [events, setEvents] = useState<TaskRunEvent[]>([]);
  const [linkedArtifacts, setLinkedArtifacts] = useState<OutputArtifact[]>([]);
  const [actionError, setActionError] = useState<string | null>(null);
  const selectedId = selectedTask?.id ?? null;

  const load = useCallback(async () => {
    setTasks((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await taskRunClient.listTaskRuns(settings, {
        status,
        recoverable: recoveryFilter === "recoverable" ? true : undefined,
        leaseExpired: recoveryFilter === "lease_expired" ? true : undefined,
        scheduledDue: recoveryFilter === "scheduled_due" ? true : undefined,
      });
      const health = await taskRunClient.schedulerHealth(settings);
      setSchedulerHealth(health);
      setTasks({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setTasks({
        data: null,
        error: error instanceof Error ? error.message : "Task Runs API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings, status, recoveryFilter]);

  const loadTask = async (row: TaskRun) => {
    setSelectedTask(row);
    try {
      const [eventList, artifactList] = await Promise.all([
        taskRunClient.listEvents(row.id, settings),
        outputArtifactClient.listArtifacts(settings, { taskRunId: row.id }),
      ]);
      const taskDiagnostics = await taskRunClient.diagnostics(row.id, settings);
      setEvents(eventList.items ?? []);
      setLinkedArtifacts(artifactList.items ?? []);
      setDiagnostics(taskDiagnostics);
    } catch (error) {
      setEvents([]);
      setLinkedArtifacts([]);
      setDiagnostics(null);
      setActionError(error instanceof Error ? error.message : "Task Run detail unavailable");
    }
  };

  const mutateTask = async (action: "retry" | "cancel" | "resume" | "recover") => {
    if (!selectedTask) {
      return;
    }
    setActionError(null);
    try {
      const updated =
        action === "retry"
          ? await taskRunClient.retry(selectedTask.id, "Manual retry from Admin Dashboard", settings)
          : action === "cancel"
            ? await taskRunClient.cancel(selectedTask.id, "Manual cancel from Admin Dashboard", settings)
            : action === "recover"
              ? await taskRunClient.recover(selectedTask.id, "Manual recovery from Admin Dashboard", settings)
              : await taskRunClient.resume(selectedTask.id, settings);
      setSelectedTask(updated);
      await loadTask(updated);
      await load();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : `${action} failed`);
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="split-page">
      <Panel
        title="Task Runs"
        description="Task Orchestration Foundation for background Conversation and Playbook execution. In-process queue only; not Celery, not Kubernetes, not production HA."
        action={
          <div className="inline-controls">
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              {taskStatuses.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <select value={recoveryFilter} onChange={(event) => setRecoveryFilter(event.target.value)}>
              <option value="all">all</option>
              <option value="recoverable">recoverable</option>
              <option value="lease_expired">lease expired</option>
              <option value="scheduled_due">scheduled due</option>
            </select>
            <RefreshButton onClick={load} />
          </div>
        }
      >
        <section className="metrics-grid compact">
          <DataCard title="Scheduler status" value={schedulerHealth?.status ?? "unavailable"} detail={schedulerHealth?.scheduler_name ?? "in-process"} icon={<Gauge size={18} />} />
          <DataCard title="Heartbeat" value={schedulerHealth?.heartbeat_at ?? "-"} detail={`last scan: ${schedulerHealth?.last_scan_at ?? "-"}`} icon={<Activity size={18} />} />
          <DataCard title="Recovery" value={`${schedulerHealth?.recovered_task_count ?? 0} recovered`} detail={`${schedulerHealth?.active_task_count ?? 0} active`} icon={<RefreshCcw size={18} />} />
        </section>
        <LoadNotice state={tasks} />
        <Table
          rows={(tasks.data || []) as unknown as JsonRecord[]}
          selectedId={selectedId}
          onSelect={(row) => void loadTask(row as unknown as TaskRun)}
          emptyLabel="No task runs for selected status."
          columns={[
            { key: "id", label: "task_run_id" },
            { key: "task_type", label: "task_type" },
            { key: "source_type", label: "source_type" },
            { key: "status", label: "status" },
            { key: "retry_count", label: "retry" },
            { key: "recoverable", label: "recoverable" },
            { key: "lease_expires_at", label: "lease_expires_at" },
            { key: "current_step", label: "step" },
            { key: "scheduled_at", label: "scheduled_at" },
            { key: "created_at", label: "created_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Task Run Detail</h2>
        {actionError ? <div className="notice notice-error">{actionError}</div> : null}
        <JsonPreview value={selectedTask || { status: "select a task run" }} />
        <div className="conversation-actions">
          <button className="ghost-button" onClick={() => void mutateTask("retry")} disabled={!selectedTask}>
            Retry
          </button>
          <button className="ghost-button" onClick={() => void mutateTask("cancel")} disabled={!selectedTask}>
            Cancel
          </button>
          <button className="ghost-button" onClick={() => void mutateTask("resume")} disabled={!selectedTask}>
            Resume after approval
          </button>
          <button className="ghost-button" onClick={() => void mutateTask("recover")} disabled={!selectedTask}>
            Recover
          </button>
        </div>
        <h3>Diagnostics</h3>
        <JsonPreview value={diagnostics || { status: "select a task run" }} />
        <h3>Progress timeline</h3>
        <Timeline rows={events as unknown as JsonRecord[]} primary="event_type" secondary="message" />
        <h3>Linked artifacts</h3>
        {linkedArtifacts.length ? (
          linkedArtifacts.map((artifact) => (
            <div className="approval-card" key={artifact.id}>
              <div className="approval-card-header">
                <strong>{artifact.title}</strong>
                <StatusPill value={artifact.artifact_type} />
              </div>
              <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
            </div>
          ))
        ) : (
          <div className="empty-chat">No artifacts linked to this task run yet.</div>
        )}
      </aside>
    </div>
  );
}

function OpenClawPage({ settings }: { settings: AdminSettings }) {
  const [state, setState] = useState<AsyncState<JsonRecord>>(emptyState());

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [health, capabilities] = await Promise.all([openclawApi.health(settings), openclawApi.capabilities(settings)]);
      setState({ data: { health, capabilities }, error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error.message : "OpenClaw API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Panel
      title="OpenClaw"
      description="OpenClaw is currently a mock / placeholder adapter. No real OpenClaw or social platform automation is connected."
      action={<RefreshButton onClick={load} />}
    >
      <LoadNotice state={state} />
      <div className="metrics-grid compact">
        <DataCard title="Provider" value={valueAt(state.data?.health as JsonRecord, ["provider"], "mock")} icon={<Bot size={20} />} />
        <DataCard title="Mock status" value={valueAt(state.data?.health as JsonRecord, ["mock"], "true")} icon={<TerminalSquare size={20} />} />
      </div>
      <JsonPreview value={state.data || { status: "unavailable" }} />
    </Panel>
  );
}

function AuditLogsPage({ settings }: { settings: AdminSettings }) {
  const [filters, setFilters] = useState({ eventType: "", success: "", targetType: "" });
  const [logs, setLogs] = useState<AsyncState<JsonRecord[]>>(emptyState());

  const load = useCallback(async () => {
    setLogs((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await auditApi.list(
        {
          eventType: filters.eventType || undefined,
          success: filters.success || undefined,
          targetType: filters.targetType || undefined,
        },
        settings,
      );
      setLogs({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setLogs({
        data: null,
        error: error instanceof Error ? error.message : "Audit logs API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [filters, settings]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Panel
      title="Audit Logs"
      description="Browser worker auth, UI access, policy blocks, and related browser security events."
      action={<RefreshButton onClick={load} />}
    >
      <div className="filter-row">
        <input placeholder="event_type" value={filters.eventType} onChange={(event) => setFilters({ ...filters, eventType: event.target.value })} />
        <select value={filters.success} onChange={(event) => setFilters({ ...filters, success: event.target.value })}>
          <option value="">success: any</option>
          <option value="true">success: true</option>
          <option value="false">success: false</option>
        </select>
        <input placeholder="target_type" value={filters.targetType} onChange={(event) => setFilters({ ...filters, targetType: event.target.value })} />
      </div>
      <LoadNotice state={logs} />
      <Table
        rows={logs.data || []}
        emptyLabel="No audit logs."
        columns={[
          { key: "event_type", label: "event_type" },
          { key: "actor_type", label: "actor_type" },
          { key: "target_type", label: "target_type" },
          { key: "target_id", label: "target_id" },
          { key: "success", label: "success" },
          { key: "error", label: "error" },
          { key: "created_at", label: "created_at" },
        ]}
      />
    </Panel>
  );
}

function RagDocumentsPage({ settings }: { settings: AdminSettings }) {
  const [query, setQuery] = useState("AI automation operations");
  const [collection, setCollection] = useState("ai_knowledge_base");
  const [state, setState] = useState<AsyncState<JsonRecord>>(emptyState());
  const [searchResults, setSearchResults] = useState<JsonRecord[]>([]);

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [embeddingHealth, documents, collections] = await Promise.all([
        ragApi.embeddingHealth(settings),
        ragApi.documents(settings),
        ragApi.collections(settings),
      ]);
      setState({ data: { embeddingHealth, documents, collections }, error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error.message : "RAG / Documents API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  const runSearch = async () => {
    const response = await ragApi.search(
      {
        query,
        collection_name: collection,
        search_mode: "hybrid",
        dense_top_k: 20,
        keyword_top_k: 20,
        final_top_k: 5,
      },
      settings,
    );
    setSearchResults(toItems(response));
  };

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Panel title="RAG / Documents" description="Basic knowledge-base entry point. This is not a full document management console." action={<RefreshButton onClick={load} />}>
      <LoadNotice state={state} />
      <div className="json-grid">
        <JsonPreview value={state.data?.embeddingHealth} />
        <JsonPreview value={state.data?.collections} />
      </div>
      <h3>Documents</h3>
      <Table
        rows={toItems(state.data?.documents)}
        emptyLabel="No documents."
        columns={[
          { key: "id", label: "document_id" },
          { key: "source_id", label: "source_id" },
          { key: "source_name", label: "source_name" },
          { key: "status", label: "status" },
          { key: "chunk_count", label: "chunk_count" },
          { key: "collection_name", label: "collection_name" },
        ]}
      />
      <div className="search-row">
        <input value={collection} onChange={(event) => setCollection(event.target.value)} placeholder="collection_name" />
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search query" />
        <button className="primary-button" onClick={() => void runSearch()}>
          <Search size={15} />
          Search
        </button>
      </div>
      <Table
        rows={searchResults}
        emptyLabel="No search results yet."
        columns={[
          { key: "id", label: "chunk_id" },
          { key: "similarity_score", label: "similarity" },
          { key: "rerank_score", label: "rerank" },
          { key: "text", label: "text" },
          { key: "metadata", label: "metadata" },
        ]}
      />
    </Panel>
  );
}

function SettingsPage({
  settings,
  onSave,
}: {
  settings: AdminSettings;
  onSave: (settings: AdminSettings) => void;
}) {
  const [draft, setDraft] = useState(settings);

  return (
    <Panel title="Settings" description="Local browser settings only. No authentication or permissions UI is implemented.">
      <div className="settings-grid">
        <label>
          AI Server URL
          <input value={draft.aiServerUrl} onChange={(event) => setDraft({ ...draft, aiServerUrl: event.target.value })} />
        </label>
        <label>
          Workspace ID
          <input value={draft.workspaceId} onChange={(event) => setDraft({ ...draft, workspaceId: event.target.value })} />
        </label>
        <label>
          User ID
          <input value={draft.userId} onChange={(event) => setDraft({ ...draft, userId: event.target.value })} />
        </label>
        <label>
          Refresh interval
          <input value={`${draft.refreshIntervalMs / 1000}s`} readOnly />
        </label>
      </div>
      <button
        className="primary-button"
        onClick={() => {
          writeAdminSettings(draft);
          onSave(draft);
        }}
      >
        <KeyRound size={15} />
        Save local settings
      </button>
    </Panel>
  );
}

function Timeline({ rows, primary, secondary }: { rows: JsonRecord[]; primary: string; secondary: string }) {
  if (!rows.length) {
    return <div className="empty-table">No records.</div>;
  }
  return (
    <div className="timeline">
      {rows.slice(0, 80).map((row) => {
        const id = rowId(row, ["id"]);
        return (
          <div key={id} className="timeline-item">
            <span>{String(row[primary] ?? "-")}</span>
            <p>{String(row[secondary] ?? "-")}</p>
            <small>{String(row.created_at ?? row.duration_ms ?? "-")}</small>
          </div>
        );
      })}
    </div>
  );
}

function RefreshButton({ onClick }: { onClick: () => void }) {
  return (
    <button className="ghost-button" onClick={() => void onClick()}>
      <RefreshCcw size={15} />
      Refresh
    </button>
  );
}

function App() {
  const [activePage, setActivePage] = useState<PageKey>("overview");
  const [settings, setSettings] = useState<AdminSettings>(() => readAdminSettings());
  const currentPage = useMemo(() => pages.find((page) => page.key === activePage) || pages[0], [activePage]);

  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">
            <Brain size={22} />
          </span>
          <div>
            <strong>AI Ops Admin</strong>
            <small>Monitoring Foundation</small>
          </div>
        </div>
        <nav>
          {pages.map((page) => (
            <button key={page.key} className={activePage === page.key ? "active" : ""} onClick={() => setActivePage(page.key)}>
              {page.icon}
              {page.label}
            </button>
          ))}
        </nav>
        <div className="boundary-box">
          <strong>Phase 36</strong>
          <span>Read-only monitoring foundation. No login UI, permission UI, publishing flow, or real social platform control.</span>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <div>
            <h1>{currentPage.label}</h1>
            <p>{settings.aiServerUrl} · workspace {settings.workspaceId} · user {settings.userId}</p>
          </div>
          <div className="topbar-actions">
            <StatusPill value="foundation" />
            <StatusPill value="read-only" />
          </div>
        </header>
        <div className="content">
          {activePage === "overview" ? <OverviewPage settings={settings} /> : null}
          {activePage === "workers" ? <WorkersPage settings={settings} /> : null}
          {activePage === "browser-runtime" ? <BrowserRuntimePage settings={settings} /> : null}
          {activePage === "conversations" ? <ConversationsPage settings={settings} /> : null}
          {activePage === "playbooks" ? <PlaybooksPage settings={settings} /> : null}
          {activePage === "output-library" ? <OutputLibraryPage settings={settings} /> : null}
          {activePage === "tasks" ? <TasksPage settings={settings} /> : null}
          {activePage === "openclaw" ? <OpenClawPage settings={settings} /> : null}
          {activePage === "audit-logs" ? <AuditLogsPage settings={settings} /> : null}
          {activePage === "rag-documents" ? <RagDocumentsPage settings={settings} /> : null}
          {activePage === "settings" ? <SettingsPage settings={settings} onSave={setSettings} /> : null}
        </div>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
