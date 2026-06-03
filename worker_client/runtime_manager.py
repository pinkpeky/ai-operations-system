"""Worker Client 本地 Runtime Manager。"""

from __future__ import annotations

import asyncio
import logging
import threading
from datetime import UTC, datetime
from typing import Any, Callable

from worker_client.config import WorkerClientConfig, load_worker_state
from worker_client.heartbeat import send_heartbeat_once
from worker_client.logging import log_event
from worker_client.metric_dispatch_scheduler import WorkerMetricDispatchScheduler
from worker_client.status import DEFAULT_STATUS_PATH, get_status, update_status

logger = logging.getLogger(__name__)

AppFactory = Callable[..., Any]


class WorkerRuntimeManager:
    """管理本地 worker runtime 与 heartbeat 线程。"""

    def __init__(
        self,
        config: WorkerClientConfig,
        *,
        app_factory: AppFactory | None = None,
        status_path: str | None = None,
    ) -> None:
        self.config = config
        self._app_factory = app_factory
        self._status_path = status_path or str(DEFAULT_STATUS_PATH)
        self._runtime_thread: threading.Thread | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._heartbeat_stop_event = threading.Event()
        self._metric_dispatch_scheduler = WorkerMetricDispatchScheduler(config)
        self._metric_dispatch_scheduler_thread: threading.Thread | None = None
        self._metric_dispatch_scheduler_stop_event = threading.Event()
        self._server: Any | None = None
        self._runtime_running_flag = False
        self._lock = threading.RLock()

    @property
    def runtime_running(self) -> bool:
        """返回 runtime 是否处于运行状态。"""

        return bool(self._runtime_running_flag) or bool(self._runtime_thread and self._runtime_thread.is_alive())

    @property
    def heartbeat_running(self) -> bool:
        """返回 heartbeat 是否处于运行状态。"""

        return bool(self._heartbeat_thread and self._heartbeat_thread.is_alive())

    @property
    def metric_dispatch_scheduler_running(self) -> bool:
        """Return whether the local metric dispatch scheduler loop is running."""

        return bool(self._metric_dispatch_scheduler_thread and self._metric_dispatch_scheduler_thread.is_alive())

    def _base_status(self) -> dict[str, Any]:
        """从 config/state 合成本地状态，不暴露 secret。"""

        state = load_worker_state(self.config.state_path)
        return {
            "worker_id": state.worker_id if state else None,
            "worker_name": self.config.worker_name,
            "workspace_id": self.config.workspace_id,
            "server_url": self.config.normalized_server_url,
            "worker_base_url": state.worker_base_url if state else self.config.effective_worker_base_url,
            "runtime_port": self.config.runtime_port,
            "registered": state is not None,
            "openclaw_enabled": self.config.openclaw_enabled,
            "browser_enabled": True,
        }

    def _write_runtime_status(self, updates: dict[str, Any]) -> dict[str, Any]:
        """写本地运行状态，统一维护 runtime/heartbeat 字段。"""

        existing_status = get_status(self._status_path)
        if "heartbeat_running" in updates:
            heartbeat_running = bool(updates["heartbeat_running"])
        else:
            heartbeat_running = self.heartbeat_running or bool(existing_status.get("heartbeat_running"))
        payload = {
            **self._base_status(),
            "runtime_running": self.runtime_running,
            "heartbeat_running": heartbeat_running,
            "metric_dispatch_scheduler_running": self.metric_dispatch_scheduler_running,
            **updates,
        }
        return update_status(payload, self._status_path)

    def attach_server(self, server: Any) -> None:
        """把外部 uvicorn.Server 绑定到 manager，供 local API stop 使用。"""

        with self._lock:
            self._server = server

    def mark_runtime_running(self, running: bool, *, error: str | None = None) -> dict[str, Any]:
        """由 CLI 外部托管 runtime 时同步运行状态。"""

        self._runtime_running_flag = running
        return self._write_runtime_status(
            {
                "runtime_running": running,
                "current_status": "running" if running else "stopped",
                "last_error": error,
            }
        )

    async def serve_runtime(self) -> dict[str, Any]:
        """在当前 event loop 中运行 runtime server。"""

        self.config.validate_config()
        import uvicorn

        from worker_client.runtime import create_worker_client_app

        app_factory = self._app_factory or create_worker_client_app
        state = load_worker_state(self.config.state_path)
        app = app_factory(self.config, state=state, manager=self)
        server_config = uvicorn.Config(
            app,
            host=self.config.runtime_host,
            port=self.config.runtime_port,
            log_level="info",
        )
        server = uvicorn.Server(server_config)
        self.attach_server(server)
        self.mark_runtime_running(True)
        log_event("worker runtime started", extra={"host": self.config.runtime_host, "port": self.config.runtime_port})
        try:
            await server.serve()
        except Exception as exc:
            logger.exception("Worker runtime failed")
            log_event("worker runtime failed", level=logging.ERROR, extra={"error": str(exc)})
            self.mark_runtime_running(False, error=str(exc))
            raise
        finally:
            self.mark_runtime_running(False)
            log_event("worker runtime stopped")
        return self.runtime_state()

    def _run_runtime_thread(self) -> None:
        """线程入口：运行 uvicorn runtime。"""

        try:
            asyncio.run(self.serve_runtime())
        except Exception as exc:  # pragma: no cover - 防御性日志
            self._write_runtime_status({"runtime_running": False, "current_status": "error", "last_error": str(exc)})

    def start_runtime(self) -> dict[str, Any]:
        """后台启动本地 runtime。"""

        with self._lock:
            if self._runtime_thread and self._runtime_thread.is_alive():
                return self.runtime_state()
            self.config.validate_config()
            self._runtime_running_flag = True
            self._runtime_thread = threading.Thread(target=self._run_runtime_thread, name="worker-runtime", daemon=True)
            self._runtime_thread.start()
            return self._write_runtime_status({"runtime_running": True, "current_status": "starting", "last_error": None})

    def stop_runtime(self) -> dict[str, Any]:
        """优雅停止本地 runtime。"""

        with self._lock:
            if self._server is not None:
                self._server.should_exit = True
            if self._runtime_thread and self._runtime_thread.is_alive():
                self._runtime_thread.join(timeout=10)
            self._runtime_running_flag = False
            log_event("worker runtime stop requested")
            return self._write_runtime_status({"runtime_running": self.runtime_running, "current_status": "stopped"})

    def restart_runtime(self) -> dict[str, Any]:
        """重启本地 runtime。"""

        self.stop_runtime()
        return self.start_runtime()

    def _heartbeat_loop(self, status: str) -> None:
        """线程入口：独立 heartbeat loop。"""

        while not self._heartbeat_stop_event.is_set():
            try:
                result = asyncio.run(send_heartbeat_once(self.config, status=status))
                now = datetime.now(UTC).isoformat()
                self._write_runtime_status(
                    {
                        "heartbeat_running": True,
                        "last_heartbeat_at": now if result.success else get_status(self._status_path).get("last_heartbeat_at"),
                        "current_status": status,
                        "last_error": None if result.success else f"heartbeat failed: {result.status_code}",
                    }
                )
                log_event("worker heartbeat sent", extra={"worker_id": result.worker_id, "success": result.success})
            except Exception as exc:  # pragma: no cover - 防御性日志
                logger.error("Worker heartbeat failed: %s", exc)
                log_event("worker heartbeat failed", level=logging.ERROR, extra={"error": str(exc)})
                self._write_runtime_status({"heartbeat_running": True, "current_status": "error", "last_error": str(exc)})
            self._heartbeat_stop_event.wait(self.config.heartbeat_interval_seconds)

    def start_heartbeat(self, *, status: str = "online") -> dict[str, Any]:
        """后台启动 heartbeat 线程。"""

        with self._lock:
            if self._heartbeat_thread and self._heartbeat_thread.is_alive():
                return self.runtime_state()
            self._heartbeat_stop_event.clear()
            self._heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                args=(status,),
                name="worker-heartbeat",
                daemon=True,
            )
            self._heartbeat_thread.start()
            log_event("worker heartbeat started", extra={"status": status})
            return self._write_runtime_status({"heartbeat_running": True, "current_status": status, "last_error": None})

    def stop_heartbeat(self) -> dict[str, Any]:
        """停止 heartbeat 线程。"""

        with self._lock:
            self._heartbeat_stop_event.set()
            if self._heartbeat_thread and self._heartbeat_thread.is_alive():
                self._heartbeat_thread.join(timeout=10)
            log_event("worker heartbeat stopped")
            return self._write_runtime_status({"heartbeat_running": False})

    def metric_dispatch_scheduler_state(self) -> dict[str, Any]:
        """Return the local metric dispatch scheduler state."""

        state = self._metric_dispatch_scheduler.state()
        state["running"] = self.metric_dispatch_scheduler_running
        return state

    def configure_metric_dispatch_scheduler(self, scheduler_payload: dict[str, Any]) -> dict[str, Any]:
        """Persist the server-issued metric dispatch timer payload."""

        state = self._metric_dispatch_scheduler.configure(scheduler_payload)
        state["running"] = self.metric_dispatch_scheduler_running
        self._write_runtime_status(self._metric_dispatch_status_updates(state))
        return state

    async def tick_metric_dispatch_scheduler(self, *, force: bool = False) -> dict[str, Any]:
        """Execute one local metric dispatch poll tick."""

        state = await self._metric_dispatch_scheduler.tick(force=force)
        state["running"] = self.metric_dispatch_scheduler_running
        self._write_runtime_status(self._metric_dispatch_status_updates(state))
        return state

    def _metric_dispatch_status_updates(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "metric_dispatch_scheduler_running": self.metric_dispatch_scheduler_running,
            "metric_dispatch_scheduler_status": state.get("scheduler_status"),
            "metric_dispatch_scheduler_next_poll_at": state.get("next_poll_at"),
            "metric_dispatch_scheduler_last_error": state.get("last_error"),
        }

    @staticmethod
    def _metric_dispatch_wait_seconds(state: dict[str, Any]) -> int:
        if state.get("tick_status") == "waiting_for_next_poll":
            try:
                return max(10, min(int(state.get("seconds_until_next_poll") or 60), 300))
            except (TypeError, ValueError):
                return 60
        try:
            return max(10, min(int(state.get("recommended_poll_interval_seconds") or 300), 300))
        except (TypeError, ValueError):
            return 60

    def _metric_dispatch_scheduler_loop(self) -> None:
        """Background loop for customer-machine metric dispatch polling."""

        wait_seconds = 10
        while not self._metric_dispatch_scheduler_stop_event.is_set():
            try:
                state = asyncio.run(self._metric_dispatch_scheduler.tick())
                state["running"] = True
                self._write_runtime_status(self._metric_dispatch_status_updates(state))
                wait_seconds = self._metric_dispatch_wait_seconds(state)
            except Exception as exc:  # pragma: no cover - defensive loop guard
                logger.error("Metric dispatch scheduler failed: %s", exc)
                log_event("metric dispatch scheduler loop failed", level=logging.ERROR, extra={"error": str(exc)})
                self._write_runtime_status(
                    {
                        "metric_dispatch_scheduler_running": True,
                        "metric_dispatch_scheduler_status": "loop_failed",
                        "metric_dispatch_scheduler_last_error": str(exc),
                    }
                )
                wait_seconds = 60
            self._metric_dispatch_scheduler_stop_event.wait(wait_seconds)

    def start_metric_dispatch_scheduler(self) -> dict[str, Any]:
        """Start the local metric dispatch scheduler loop."""

        with self._lock:
            state = self._metric_dispatch_scheduler.state()
            if not state.get("configured"):
                state = {**state, "running": False, "tick_status": "not_configured"}
                self._write_runtime_status(self._metric_dispatch_status_updates(state))
                return state
            if not state.get("scheduler_enabled"):
                state = {**state, "running": False, "tick_status": "disabled"}
                self._write_runtime_status(self._metric_dispatch_status_updates(state))
                return state
            if self._metric_dispatch_scheduler_thread and self._metric_dispatch_scheduler_thread.is_alive():
                state["running"] = True
                return state
            self._metric_dispatch_scheduler_stop_event.clear()
            self._metric_dispatch_scheduler_thread = threading.Thread(
                target=self._metric_dispatch_scheduler_loop,
                name="worker-metric-dispatch-scheduler",
                daemon=True,
            )
            self._metric_dispatch_scheduler_thread.start()
            state["running"] = True
            log_event("metric dispatch scheduler started")
            self._write_runtime_status(self._metric_dispatch_status_updates(state))
            return state

    def stop_metric_dispatch_scheduler(self) -> dict[str, Any]:
        """Stop the local metric dispatch scheduler loop."""

        with self._lock:
            self._metric_dispatch_scheduler_stop_event.set()
            if self._metric_dispatch_scheduler_thread and self._metric_dispatch_scheduler_thread.is_alive():
                self._metric_dispatch_scheduler_thread.join(timeout=10)
            state = self._metric_dispatch_scheduler.state()
            state["running"] = False
            log_event("metric dispatch scheduler stopped")
            self._write_runtime_status(self._metric_dispatch_status_updates(state))
            return state

    def clear_metric_dispatch_scheduler(self) -> dict[str, Any]:
        """Clear local metric dispatch scheduler state."""

        with self._lock:
            self._metric_dispatch_scheduler_stop_event.set()
            if self._metric_dispatch_scheduler_thread and self._metric_dispatch_scheduler_thread.is_alive():
                self._metric_dispatch_scheduler_thread.join(timeout=10)
            state = self._metric_dispatch_scheduler.clear()
            state["running"] = False
            self._write_runtime_status(self._metric_dispatch_status_updates(state))
            return state

    def runtime_health(self) -> dict[str, Any]:
        """返回本地 runtime 健康信息。"""

        state = self.runtime_state()
        return {
            "success": True,
            "runtime_running": self.runtime_running,
            "heartbeat_running": state["heartbeat_running"],
            "metric_dispatch_scheduler_running": self.metric_dispatch_scheduler_running,
            "host": self.config.runtime_host,
            "port": self.config.runtime_port,
            "localhost_only": self.config.runtime_host in {"127.0.0.1", "localhost", "::1"},
            "status": state,
        }

    def runtime_state(self) -> dict[str, Any]:
        """返回可展示的本地状态。"""

        status = get_status(self._status_path)
        heartbeat_running = self.heartbeat_running or bool(status.get("heartbeat_running"))
        status.update(
            {
                **self._base_status(),
                "runtime_running": self.runtime_running,
                "heartbeat_running": heartbeat_running,
                "metric_dispatch_scheduler_running": self.metric_dispatch_scheduler_running,
            }
        )
        status.pop("worker_secret", None)
        return status
