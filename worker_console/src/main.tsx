import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  PauseCircle,
  PlayCircle,
  RefreshCcw,
  RotateCcw,
  Server,
  Square,
  TerminalSquare,
  Wifi,
  WifiOff,
} from "lucide-react";
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
            <p>请确认 worker_client 是否启动；请确认端口是否为 9100。</p>
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
