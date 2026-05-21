"""Guarded ComfyUI runtime adapter contract service."""

from __future__ import annotations

import json
from time import perf_counter
from typing import Any, Callable, Mapping
from urllib.error import HTTPError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

from app.core.config import Settings, get_settings
from app.schemas.comfyui_runtime import (
    ComfyUIRuntimeCapabilitiesResponse,
    ComfyUIRuntimeDiagnosticCheck,
    ComfyUIRuntimeDiagnosticsResponse,
    ComfyUIRuntimeHealthResponse,
)


COMFYUI_RUNTIME_READ_ONLY_ACTION = "call_comfyui_system_stats_read_only"
DISABLED_COMFYUI_RUNTIME_ACTIONS = [
    "import_adapter",
    "call_comfyui_queue",
    "submit_prompt",
    "upload_file",
    "submit_queue_job",
    "read_history",
    "generate_media",
    "enable_runtime_switch",
    "resolve_secret_value",
]

HttpGet = Callable[[str, float], Mapping[str, Any]]


class ComfyUIRuntimeService:
    """Expose ComfyUI runtime readiness with an explicit read-only probe gate."""

    def __init__(self, settings: Settings | None = None, http_get: HttpGet | None = None) -> None:
        self.settings = settings or get_settings()
        self.http_get = http_get or self._default_http_get

    def health_check(self, *, workspace_id: str | None = None) -> ComfyUIRuntimeHealthResponse:
        """Return adapter contract state and optionally run one guarded read-only probe."""

        provider = self.settings.comfyui_runtime_provider.strip().lower() or "disabled"
        allowed_hosts = sorted(self.settings.comfyui_runtime_allowed_host_set)
        allowed_health_paths = sorted(self.settings.comfyui_runtime_allowed_health_path_set)
        parsed = urlparse(self.settings.comfyui_runtime_base_url)
        host = (parsed.hostname or "").lower()
        scheme_allowed = parsed.scheme in {"http", "https"}
        host_allowed = bool(host and host in self.settings.comfyui_runtime_allowed_host_set)
        health_path = self._normalize_path(self.settings.comfyui_runtime_health_path)
        health_path_allowed = health_path in self.settings.comfyui_runtime_allowed_health_path_set
        config_ready = (
            provider == "guarded"
            and self.settings.comfyui_runtime_enabled
            and self.settings.comfyui_runtime_allow_network
            and scheme_allowed
            and host_allowed
        )
        read_only_probe_ready = config_ready and self.settings.comfyui_runtime_read_only_probe_enabled and health_path_allowed
        error = self._contract_error(
            provider=provider,
            scheme_allowed=scheme_allowed,
            host_allowed=host_allowed,
            health_path_allowed=health_path_allowed,
        )

        raw: dict[str, Any] = {
            "phase": "62B",
            "contract_mode": "guarded_read_only_probe",
            "config_ready_for_read_only_probe": config_ready,
            "read_only_probe_ready": read_only_probe_ready,
            "parsed_host": host,
            "scheme_allowed": scheme_allowed,
            "host_allowed": host_allowed,
            "health_path_allowed": health_path_allowed,
            "no_network_call_performed": True,
            "disabled_actions": self._disabled_actions(read_only_probe_ready=read_only_probe_ready),
        }
        if not read_only_probe_ready:
            return ComfyUIRuntimeHealthResponse(
                provider=provider,
                enabled=self.settings.comfyui_runtime_enabled,
                reachable=False,
                guarded=True,
                mock=True,
                network_allowed=self.settings.comfyui_runtime_allow_network,
                external_request_attempted=False,
                runtime_calls_enabled=False,
                read_only_probe_enabled=self.settings.comfyui_runtime_read_only_probe_enabled,
                read_only_probe_attempted=False,
                health_path=health_path,
                allowed_health_paths=allowed_health_paths,
                probe_status_code=None,
                probe_latency_ms=None,
                base_url=self.settings.comfyui_runtime_base_url,
                allowed_hosts=allowed_hosts,
                timeout_seconds=self.settings.comfyui_runtime_timeout_seconds,
                workspace_id=workspace_id,
                error=error,
                raw=raw,
            )

        probe_url = self._build_probe_url(self.settings.comfyui_runtime_base_url, health_path)
        started_at = perf_counter()
        try:
            probe_response = self.http_get(probe_url, self.settings.comfyui_runtime_timeout_seconds)
            latency_ms = round((perf_counter() - started_at) * 1000, 2)
            status_code = self._status_code(probe_response)
            reachable = status_code is not None and 200 <= status_code < 300
            probe_error = None if reachable else f"ComfyUI read-only probe returned HTTP {status_code or 'unknown'}."
            raw.update(
                {
                    "no_network_call_performed": False,
                    "probe_target_host": host,
                    "probe_path": health_path,
                    "probe_response_summary": self._summarize_probe_response(probe_response),
                }
            )
            return ComfyUIRuntimeHealthResponse(
                provider=provider,
                enabled=self.settings.comfyui_runtime_enabled,
                reachable=reachable,
                guarded=True,
                mock=False,
                network_allowed=self.settings.comfyui_runtime_allow_network,
                external_request_attempted=True,
                runtime_calls_enabled=False,
                read_only_probe_enabled=True,
                read_only_probe_attempted=True,
                health_path=health_path,
                allowed_health_paths=allowed_health_paths,
                probe_status_code=status_code,
                probe_latency_ms=latency_ms,
                base_url=self.settings.comfyui_runtime_base_url,
                allowed_hosts=allowed_hosts,
                timeout_seconds=self.settings.comfyui_runtime_timeout_seconds,
                workspace_id=workspace_id,
                error=probe_error,
                raw=raw,
            )
        except Exception as exc:
            latency_ms = round((perf_counter() - started_at) * 1000, 2)
            raw.update(
                {
                    "no_network_call_performed": False,
                    "probe_target_host": host,
                    "probe_path": health_path,
                    "probe_exception_type": exc.__class__.__name__,
                }
            )
            return ComfyUIRuntimeHealthResponse(
                provider=provider,
                enabled=self.settings.comfyui_runtime_enabled,
                reachable=False,
                guarded=True,
                mock=False,
                network_allowed=self.settings.comfyui_runtime_allow_network,
                external_request_attempted=True,
                runtime_calls_enabled=False,
                read_only_probe_enabled=True,
                read_only_probe_attempted=True,
                health_path=health_path,
                allowed_health_paths=allowed_health_paths,
                probe_status_code=None,
                probe_latency_ms=latency_ms,
                base_url=self.settings.comfyui_runtime_base_url,
                allowed_hosts=allowed_hosts,
                timeout_seconds=self.settings.comfyui_runtime_timeout_seconds,
                workspace_id=workspace_id,
                error=f"ComfyUI read-only probe failed: {exc.__class__.__name__}",
                raw=raw,
            )

    def capabilities(self, *, workspace_id: str | None = None) -> ComfyUIRuntimeCapabilitiesResponse:
        """Return the guarded contract capabilities for operators and maintainers."""

        provider = self.settings.comfyui_runtime_provider.strip().lower() or "disabled"
        parsed = urlparse(self.settings.comfyui_runtime_base_url)
        host = (parsed.hostname or "").lower()
        health_path = self._normalize_path(self.settings.comfyui_runtime_health_path)
        read_only_probe_ready = (
            provider == "guarded"
            and self.settings.comfyui_runtime_enabled
            and self.settings.comfyui_runtime_allow_network
            and self.settings.comfyui_runtime_read_only_probe_enabled
            and parsed.scheme in {"http", "https"}
            and bool(host and host in self.settings.comfyui_runtime_allowed_host_set)
            and health_path in self.settings.comfyui_runtime_allowed_health_path_set
        )
        available_actions = [
            "contract_read",
            "configuration_review",
            "disabled_health_contract",
        ]
        if read_only_probe_ready:
            available_actions.append(COMFYUI_RUNTIME_READ_ONLY_ACTION)
        return ComfyUIRuntimeCapabilitiesResponse(
            provider=provider,
            enabled=self.settings.comfyui_runtime_enabled,
            guarded=True,
            mock=True,
            base_url=self.settings.comfyui_runtime_base_url,
            allowed_hosts=sorted(self.settings.comfyui_runtime_allowed_host_set),
            health_path=health_path,
            allowed_health_paths=sorted(self.settings.comfyui_runtime_allowed_health_path_set),
            read_only_probe_enabled=self.settings.comfyui_runtime_read_only_probe_enabled,
            available_actions=available_actions,
            disabled_actions=self._disabled_actions(read_only_probe_ready=read_only_probe_ready),
            guardrails=[
                "COMFYUI_RUNTIME_ENABLED must be true before any future live adapter can be considered",
                "COMFYUI_RUNTIME_ALLOW_NETWORK must be true before the read-only health probe can be considered",
                "COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED must be true before a ComfyUI health endpoint is called",
                "COMFYUI_RUNTIME_BASE_URL host must be in COMFYUI_RUNTIME_ALLOWED_HOSTS",
                "COMFYUI_RUNTIME_HEALTH_PATH must be in COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS",
                "Phase 62B only permits a read-only system_stats health probe when every explicit gate is enabled",
                "Prompt submission, queue reads/submissions, uploads, media generation, adapter imports, and runtime switch changes remain disabled",
            ],
            required_configuration=[
                "COMFYUI_RUNTIME_PROVIDER=guarded",
                "COMFYUI_RUNTIME_ENABLED=true",
                "COMFYUI_RUNTIME_ALLOW_NETWORK=true",
                "COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true",
                "COMFYUI_RUNTIME_BASE_URL",
                "COMFYUI_RUNTIME_ALLOWED_HOSTS",
                "COMFYUI_RUNTIME_HEALTH_PATH=/system_stats",
                "COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS=/system_stats",
            ],
            workspace_id=workspace_id,
            raw={
                "phase": "62B",
                "contract_mode": "guarded_adapter_contract",
                "runtime_calls_enabled": False,
                "read_only_probe_ready": read_only_probe_ready,
            },
        )

    def diagnostics(self, *, workspace_id: str | None = None) -> ComfyUIRuntimeDiagnosticsResponse:
        """Return no-network readiness diagnostics for the guarded runtime gates."""

        provider = self.settings.comfyui_runtime_provider.strip().lower() or "disabled"
        parsed = urlparse(self.settings.comfyui_runtime_base_url)
        host = (parsed.hostname or "").lower()
        allowed_hosts = sorted(self.settings.comfyui_runtime_allowed_host_set)
        allowed_health_paths = sorted(self.settings.comfyui_runtime_allowed_health_path_set)
        health_path = self._normalize_path(self.settings.comfyui_runtime_health_path)
        scheme_allowed = parsed.scheme in {"http", "https"}
        host_allowed = bool(host and host in self.settings.comfyui_runtime_allowed_host_set)
        health_path_allowed = health_path in self.settings.comfyui_runtime_allowed_health_path_set

        checks: list[ComfyUIRuntimeDiagnosticCheck] = []
        blocking_reasons: list[str] = []
        recommended_actions: list[str] = []

        def add_check(
            *,
            key: str,
            passed: bool,
            label: str,
            detail: str,
            current_value: Any,
            expected_value: Any,
            remediation: str | None,
            required: bool = True,
        ) -> None:
            status = "pass" if passed else "blocked" if required else "warning"
            checks.append(
                ComfyUIRuntimeDiagnosticCheck(
                    key=key,
                    status=status,
                    label=label,
                    detail=detail,
                    current_value=current_value,
                    expected_value=expected_value,
                    remediation=remediation,
                )
            )
            if required and not passed:
                blocking_reasons.append(f"{key}: {detail}")
                if remediation and remediation not in recommended_actions:
                    recommended_actions.append(remediation)

        add_check(
            key="provider_guarded",
            passed=provider == "guarded",
            label="Runtime provider",
            detail=f"Current provider is {provider}; guarded provider is required before any ComfyUI probe.",
            current_value=provider,
            expected_value="guarded",
            remediation="Set COMFYUI_RUNTIME_PROVIDER=guarded after the maintainer approves guarded probing.",
        )
        add_check(
            key="runtime_enabled",
            passed=self.settings.comfyui_runtime_enabled,
            label="Runtime enable switch",
            detail="COMFYUI_RUNTIME_ENABLED must be true before read-only probe readiness.",
            current_value=self.settings.comfyui_runtime_enabled,
            expected_value=True,
            remediation="Set COMFYUI_RUNTIME_ENABLED=true only for the reviewed ComfyUI host.",
        )
        add_check(
            key="network_gate",
            passed=self.settings.comfyui_runtime_allow_network,
            label="Network gate",
            detail="COMFYUI_RUNTIME_ALLOW_NETWORK must be true before the service may contact ComfyUI.",
            current_value=self.settings.comfyui_runtime_allow_network,
            expected_value=True,
            remediation="Set COMFYUI_RUNTIME_ALLOW_NETWORK=true after host and path allowlists are reviewed.",
        )
        add_check(
            key="base_url_scheme",
            passed=scheme_allowed,
            label="Base URL scheme",
            detail="COMFYUI_RUNTIME_BASE_URL must use http or https.",
            current_value=parsed.scheme or None,
            expected_value=["http", "https"],
            remediation="Set COMFYUI_RUNTIME_BASE_URL to an http or https ComfyUI endpoint.",
        )
        add_check(
            key="base_url_host_allowlist",
            passed=host_allowed,
            label="Host allowlist",
            detail=f"Base URL host {host or '<missing>'} must be present in COMFYUI_RUNTIME_ALLOWED_HOSTS.",
            current_value=host or None,
            expected_value=allowed_hosts,
            remediation="Add the ComfyUI host to COMFYUI_RUNTIME_ALLOWED_HOSTS.",
        )
        add_check(
            key="read_only_probe_gate",
            passed=self.settings.comfyui_runtime_read_only_probe_enabled,
            label="Read-only probe gate",
            detail="COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED must be true before GET /system_stats is attempted.",
            current_value=self.settings.comfyui_runtime_read_only_probe_enabled,
            expected_value=True,
            remediation="Set COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true only after provider, network, host, and path gates pass.",
        )
        add_check(
            key="health_path_allowlist",
            passed=health_path_allowed,
            label="Health path allowlist",
            detail=f"Health path {health_path} must be present in COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS.",
            current_value=health_path,
            expected_value=allowed_health_paths,
            remediation="Set COMFYUI_RUNTIME_HEALTH_PATH to an entry in COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS, normally /system_stats.",
        )
        add_check(
            key="execution_boundary",
            passed=True,
            label="Execution boundary",
            detail="Prompt submission, queue operations, uploads, media generation, secrets, and switch mutation remain disabled.",
            current_value=False,
            expected_value=False,
            remediation=None,
            required=False,
        )

        read_only_probe_ready = all(check.status == "pass" for check in checks if check.key != "execution_boundary")
        readiness_status = "ready_for_read_only_probe" if read_only_probe_ready else "blocked"

        return ComfyUIRuntimeDiagnosticsResponse(
            provider=provider,
            enabled=self.settings.comfyui_runtime_enabled,
            guarded=True,
            network_allowed=self.settings.comfyui_runtime_allow_network,
            read_only_probe_enabled=self.settings.comfyui_runtime_read_only_probe_enabled,
            base_url=self.settings.comfyui_runtime_base_url,
            parsed_host=host or None,
            scheme_allowed=scheme_allowed,
            host_allowed=host_allowed,
            allowed_hosts=allowed_hosts,
            health_path=health_path,
            health_path_allowed=health_path_allowed,
            allowed_health_paths=allowed_health_paths,
            read_only_probe_ready=read_only_probe_ready,
            external_request_attempted=False,
            runtime_calls_enabled=False,
            readiness_status=readiness_status,
            blocking_reasons=blocking_reasons,
            recommended_actions=recommended_actions,
            diagnostics=checks,
            forbidden_actions=self._disabled_actions(read_only_probe_ready=read_only_probe_ready),
            workspace_id=workspace_id,
            raw={
                "phase": "62C",
                "contract_mode": "guarded_readiness_diagnostics",
                "no_network_call_performed": True,
                "read_only_probe_ready": read_only_probe_ready,
                "parsed_host": host,
                "scheme_allowed": scheme_allowed,
                "host_allowed": host_allowed,
                "health_path_allowed": health_path_allowed,
                "disabled_actions": self._disabled_actions(read_only_probe_ready=read_only_probe_ready),
            },
        )

    def _contract_error(
        self,
        *,
        provider: str,
        scheme_allowed: bool,
        host_allowed: bool,
        health_path_allowed: bool,
    ) -> str | None:
        if provider != "guarded":
            return "ComfyUI runtime provider is disabled; set COMFYUI_RUNTIME_PROVIDER=guarded before a guarded read-only probe."
        if not self.settings.comfyui_runtime_enabled:
            return "ComfyUI runtime is disabled by COMFYUI_RUNTIME_ENABLED=false."
        if not self.settings.comfyui_runtime_allow_network:
            return "ComfyUI runtime network access is disabled by COMFYUI_RUNTIME_ALLOW_NETWORK=false."
        if not scheme_allowed:
            return "ComfyUI runtime base URL must use http or https."
        if not host_allowed:
            return "ComfyUI runtime base URL host is not in COMFYUI_RUNTIME_ALLOWED_HOSTS."
        if not self.settings.comfyui_runtime_read_only_probe_enabled:
            return "ComfyUI runtime read-only probe is disabled by COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=false."
        if not health_path_allowed:
            return "ComfyUI runtime health path is not in COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS."
        return None

    def _disabled_actions(self, *, read_only_probe_ready: bool) -> list[str]:
        actions = list(DISABLED_COMFYUI_RUNTIME_ACTIONS)
        if not read_only_probe_ready:
            actions.insert(1, COMFYUI_RUNTIME_READ_ONLY_ACTION)
        return actions

    @staticmethod
    def _normalize_path(value: str) -> str:
        raw = (value or "").strip() or "/system_stats"
        parsed = urlparse(raw)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
            return raw
        path = parsed.path or raw
        return path if path.startswith("/") else f"/{path}"

    @staticmethod
    def _build_probe_url(base_url: str, path: str) -> str:
        parsed = urlparse(base_url)
        base_path = parsed.path.rstrip("/")
        probe_path = f"{base_path}{path}" if base_path else path
        return urlunparse((parsed.scheme, parsed.netloc, probe_path, "", "", ""))

    @staticmethod
    def _status_code(response: Mapping[str, Any]) -> int | None:
        value = response.get("status_code")
        if isinstance(value, int):
            return value
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _summarize_probe_response(response: Mapping[str, Any]) -> dict[str, Any]:
        payload = response.get("json")
        text = str(response.get("text", "") or "")
        summary: dict[str, Any] = {
            "status_code": ComfyUIRuntimeService._status_code(response),
            "has_json": isinstance(payload, (dict, list)),
            "text_length": len(text),
        }
        if isinstance(payload, dict):
            summary["json_keys"] = sorted(str(key) for key in payload.keys())[:20]
        elif isinstance(payload, list):
            summary["json_items"] = len(payload)
        return summary

    @staticmethod
    def _default_http_get(url: str, timeout_seconds: float) -> Mapping[str, Any]:
        request = Request(url, headers={"Accept": "application/json"}, method="GET")
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                body = response.read(65536)
                text = body.decode("utf-8", errors="replace")
                return {
                    "status_code": int(getattr(response, "status", response.getcode())),
                    "json": ComfyUIRuntimeService._parse_json(text),
                    "text": text[:2048],
                }
        except HTTPError as exc:
            body = exc.read(65536)
            text = body.decode("utf-8", errors="replace")
            return {
                "status_code": exc.code,
                "json": ComfyUIRuntimeService._parse_json(text),
                "text": text[:2048],
                "error": str(exc.reason),
            }

    @staticmethod
    def _parse_json(text: str) -> Any:
        if not text.strip():
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
