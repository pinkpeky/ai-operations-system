"""Local customer-machine metric dispatch poll scheduler."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

from worker_client.config import WorkerClientConfig
from worker_client.logging import log_event

DEFAULT_METRIC_DISPATCH_SCHEDULER_PATH = Path("worker_client/runtime_state/metric_dispatch_scheduler.json")
EXPECTED_POLL_ENDPOINT = "/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll"
MAX_HISTORY = 50


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value)
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        parsed = datetime.fromisoformat(text)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any, default: int, *, minimum: int = 30, maximum: int = 21600) -> int:
    try:
        return max(minimum, min(int(value), maximum))
    except (TypeError, ValueError):
        return default


def _redact_local_value(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if any(secret_key in key_text.lower() for secret_key in ("secret", "password", "token", "credential", "cookie")):
                redacted[key_text] = "[redacted]"
            else:
                redacted[key_text] = _redact_local_value(item)
        return redacted
    if isinstance(value, list):
        return [_redact_local_value(item) for item in value]
    return value


class WorkerMetricDispatchScheduler:
    """Persist and execute local metric dispatch poll timer payloads."""

    def __init__(self, config: WorkerClientConfig, *, state_path: str | Path | None = None) -> None:
        self.config = config
        self.state_path = Path(state_path) if state_path else self._default_state_path(config)

    @staticmethod
    def _default_state_path(config: WorkerClientConfig) -> Path:
        if config.state_path:
            return Path(config.state_path).parent / "metric_dispatch_scheduler.json"
        return DEFAULT_METRIC_DISPATCH_SCHEDULER_PATH

    def _read_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return self._empty_state()
        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
            return loaded if isinstance(loaded, dict) else self._empty_state()
        except (OSError, json.JSONDecodeError):
            return self._empty_state()

    def _write_state(self, state: dict[str, Any]) -> dict[str, Any]:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        safe_state = _redact_local_value(state)
        with self.state_path.open("w", encoding="utf-8") as file:
            json.dump(safe_state, file, ensure_ascii=False, indent=2)
        return safe_state

    def _empty_state(self) -> dict[str, Any]:
        return {
            "configured": False,
            "running": False,
            "scheduler_status": "not_configured",
            "scheduler_enabled": False,
            "customer_machine_id": None,
            "workspace_id": self.config.workspace_id,
            "next_poll_at": None,
            "recommended_poll_interval_seconds": 300,
            "last_tick_at": None,
            "last_poll_status": None,
            "last_error": None,
            "client_timer_payload": {},
            "notification_records": [],
            "history": [],
            "metadata": {
                "phase": "68U",
                "contract": "local_metric_dispatch_scheduler_state",
                "server_execution_boundary": "local worker only calls metric dispatch poll endpoint; no browser, OpenClaw, platform login, scraping, or publishing",
            },
        }

    def state(self) -> dict[str, Any]:
        return self._read_state()

    def configure(self, scheduler_payload: dict[str, Any]) -> dict[str, Any]:
        client_timer_payload = scheduler_payload.get("client_timer_payload")
        if not isinstance(client_timer_payload, dict):
            client_timer_payload = scheduler_payload
        endpoint = str(client_timer_payload.get("endpoint") or "")
        if endpoint != EXPECTED_POLL_ENDPOINT:
            raise ValueError("metric dispatch scheduler endpoint must be the customer-poll endpoint")
        request_body = client_timer_payload.get("request_body")
        if not isinstance(request_body, dict):
            raise ValueError("metric dispatch scheduler request_body is required")

        now = _utc_now().isoformat()
        current = self._read_state()
        notification_records = [
            *[item for item in current.get("notification_records", []) if isinstance(item, dict)],
            *self._notification_records_from_scheduler_payload(scheduler_payload, created_at=now),
        ][-MAX_HISTORY:]
        state = {
            **current,
            "configured": True,
            "scheduler_status": str(scheduler_payload.get("scheduler_status") or "configured"),
            "scheduler_enabled": bool(scheduler_payload.get("scheduler_enabled", True)),
            "customer_machine_id": str(
                scheduler_payload.get("customer_machine_id")
                or request_body.get("customer_machine_id")
                or self.config.worker_name
            ),
            "workspace_id": str(scheduler_payload.get("workspace_id") or self.config.workspace_id),
            "next_poll_at": str(scheduler_payload.get("next_poll_at") or client_timer_payload.get("next_poll_at") or ""),
            "recommended_poll_interval_seconds": _safe_int(
                scheduler_payload.get("recommended_poll_interval_seconds")
                or client_timer_payload.get("recommended_poll_interval_seconds"),
                300,
            ),
            "last_configured_at": now,
            "last_error": None,
            "client_timer_payload": client_timer_payload,
            "notification_records": notification_records,
            "scheduler_policy": scheduler_payload.get("scheduler_policy") if isinstance(scheduler_payload.get("scheduler_policy"), dict) else {},
            "metadata": {
                **(current.get("metadata") if isinstance(current.get("metadata"), dict) else {}),
                "phase": "68U",
                "contract": "local_metric_dispatch_scheduler_state",
                "source_contract": str((scheduler_payload.get("metadata") or {}).get("contract") if isinstance(scheduler_payload.get("metadata"), dict) else ""),
                "server_does_not_control_real_accounts": True,
            },
        }
        log_event("metric dispatch scheduler configured", extra={"customer_machine_id": state["customer_machine_id"]})
        return self._write_state(state)

    async def tick(
        self,
        *,
        force: bool = False,
        http_client: httpx.AsyncClient | None = None,
    ) -> dict[str, Any]:
        state = self._read_state()
        if not state.get("configured"):
            return self._write_state({**state, "tick_status": "not_configured", "last_error": None})
        if not state.get("scheduler_enabled"):
            return self._write_state({**state, "tick_status": "disabled", "last_error": None})
        next_poll = _parse_datetime(state.get("next_poll_at"))
        now = _utc_now()
        if next_poll and next_poll > now and not force:
            return self._write_state(
                {
                    **state,
                    "tick_status": "waiting_for_next_poll",
                    "seconds_until_next_poll": max(0, int((next_poll - now).total_seconds())),
                    "last_error": None,
                }
            )
        timer_payload = state.get("client_timer_payload") if isinstance(state.get("client_timer_payload"), dict) else {}
        endpoint = str(timer_payload.get("endpoint") or "")
        if endpoint != EXPECTED_POLL_ENDPOINT:
            return self._write_state({**state, "tick_status": "blocked_invalid_endpoint", "last_error": "invalid endpoint"})
        request_body = timer_payload.get("request_body") if isinstance(timer_payload.get("request_body"), dict) else {}
        if not request_body:
            return self._write_state({**state, "tick_status": "blocked_missing_request_body", "last_error": "missing request_body"})
        url = f"{self.config.normalized_server_url}{endpoint}"
        try:
            response_json = await self._post_poll(url=url, request_body=request_body, http_client=http_client)
        except Exception as exc:
            return self._record_tick_failure(state=state, error=str(exc), now=now)
        interval = _safe_int(response_json.get("poll_interval_seconds") or state.get("recommended_poll_interval_seconds"), 300)
        next_poll_at = now + timedelta(seconds=interval)
        notification_records = [
            *[item for item in state.get("notification_records", []) if isinstance(item, dict)],
            *self._notification_records_from_poll_result(response_json, created_at=now.isoformat()),
        ][-MAX_HISTORY:]
        history = [
            *[item for item in state.get("history", []) if isinstance(item, dict)],
            {
                "tick_status": "poll_executed",
                "poll_status": response_json.get("poll_status"),
                "at": now.isoformat(),
                "next_poll_at": next_poll_at.isoformat(),
                "auto_claimed": bool(response_json.get("auto_claimed")),
                "assigned_claim_count": len(response_json.get("assigned_claims") or []),
                "expired_claim_count": len(response_json.get("expired_claims") or []),
            },
        ][-MAX_HISTORY:]
        updated = {
            **state,
            "tick_status": "poll_executed",
            "scheduler_status": self._status_from_poll_status(str(response_json.get("poll_status") or "")),
            "last_tick_at": now.isoformat(),
            "last_poll_status": response_json.get("poll_status"),
            "last_poll_result": _redact_local_value(response_json),
            "last_error": None,
            "recommended_poll_interval_seconds": interval,
            "next_poll_at": next_poll_at.isoformat(),
            "notification_records": notification_records,
            "history": history,
        }
        log_event("metric dispatch scheduler poll executed", extra={"poll_status": response_json.get("poll_status")})
        return self._write_state(updated)

    async def _post_poll(
        self,
        *,
        url: str,
        request_body: dict[str, Any],
        http_client: httpx.AsyncClient | None,
    ) -> dict[str, Any]:
        headers = self.config.headers()
        if http_client is not None:
            response = await http_client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            body = response.json()
            return body if isinstance(body, dict) else {"value": body}
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            body = response.json()
        return body if isinstance(body, dict) else {"value": body}

    def _record_tick_failure(self, *, state: dict[str, Any], error: str, now: datetime) -> dict[str, Any]:
        history = [
            *[item for item in state.get("history", []) if isinstance(item, dict)],
            {"tick_status": "poll_failed", "at": now.isoformat(), "error": error},
        ][-MAX_HISTORY:]
        log_event("metric dispatch scheduler poll failed", extra={"error": error})
        return self._write_state(
            {
                **state,
                "tick_status": "poll_failed",
                "scheduler_status": "local_poll_failed",
                "last_tick_at": now.isoformat(),
                "last_error": error,
                "history": history,
            }
        )

    @staticmethod
    def _status_from_poll_status(poll_status: str) -> str:
        mapping = {
            "auto_claimed": "local_active_claim_created",
            "active_claim_in_progress": "local_active_claim_in_progress",
            "ready_to_claim": "local_ready_to_claim",
            "recovery_required": "local_recovery_required",
            "idle": "local_idle",
            "claim_blocked": "local_blocked",
            "blocked_operator_confirmation_required": "local_blocked",
        }
        return mapping.get(poll_status, "local_poll_review_required")

    @staticmethod
    def _notification_records_from_scheduler_payload(payload: dict[str, Any], *, created_at: str) -> list[dict[str, Any]]:
        events = payload.get("notification_events") if isinstance(payload.get("notification_events"), list) else []
        return [
            {
                **event,
                "source": "68t_scheduler_payload",
                "local_recorded_at": created_at,
                "acknowledged": False,
            }
            for event in events
            if isinstance(event, dict)
        ]

    @staticmethod
    def _notification_records_from_poll_result(poll_result: dict[str, Any], *, created_at: str) -> list[dict[str, Any]]:
        poll_status = str(poll_result.get("poll_status") or "")
        if poll_status == "idle":
            return []
        severity = "info"
        if poll_status in {"ready_to_claim", "claim_blocked", "blocked_operator_confirmation_required"}:
            severity = "warning"
        if poll_status == "recovery_required":
            severity = "critical"
        return [
            {
                "event_type": f"local_metric_dispatch_{poll_status or 'unknown'}",
                "severity": severity,
                "poll_status": poll_status,
                "customer_machine_id": poll_result.get("customer_machine_id"),
                "auto_claimed": bool(poll_result.get("auto_claimed")),
                "assigned_claim_count": len(poll_result.get("assigned_claims") or []),
                "expired_claim_count": len(poll_result.get("expired_claims") or []),
                "next_actions": list(poll_result.get("next_actions") or [])[:3],
                "source": "68u_local_poll_tick",
                "local_recorded_at": created_at,
                "acknowledged": False,
            }
        ]

    def clear(self) -> dict[str, Any]:
        log_event("metric dispatch scheduler cleared")
        return self._write_state(self._empty_state())
