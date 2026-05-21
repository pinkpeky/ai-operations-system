"""Disabled-by-default ComfyUI runtime adapter contract service."""

from __future__ import annotations

from urllib.parse import urlparse

from app.core.config import Settings, get_settings
from app.schemas.comfyui_runtime import ComfyUIRuntimeCapabilitiesResponse, ComfyUIRuntimeHealthResponse


DISABLED_COMFYUI_RUNTIME_ACTIONS = [
    "import_adapter",
    "call_comfyui_system_stats",
    "call_comfyui_queue",
    "submit_prompt",
    "upload_file",
    "submit_queue_job",
    "read_history",
    "generate_media",
    "enable_runtime_switch",
    "resolve_secret_value",
]


class ComfyUIRuntimeService:
    """Expose ComfyUI runtime readiness without performing runtime calls."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def health_check(self, *, workspace_id: str | None = None) -> ComfyUIRuntimeHealthResponse:
        """Return the current adapter contract state without contacting ComfyUI."""

        provider = self.settings.comfyui_runtime_provider.strip().lower() or "disabled"
        allowed_hosts = sorted(self.settings.comfyui_runtime_allowed_host_set)
        parsed = urlparse(self.settings.comfyui_runtime_base_url)
        host = (parsed.hostname or "").lower()
        scheme_allowed = parsed.scheme in {"http", "https"}
        host_allowed = bool(host and host in self.settings.comfyui_runtime_allowed_host_set)
        config_ready = provider == "guarded" and self.settings.comfyui_runtime_enabled and self.settings.comfyui_runtime_allow_network and scheme_allowed and host_allowed
        error = self._contract_error(provider=provider, scheme_allowed=scheme_allowed, host_allowed=host_allowed)

        return ComfyUIRuntimeHealthResponse(
            provider=provider,
            enabled=self.settings.comfyui_runtime_enabled,
            reachable=False,
            guarded=True,
            mock=True,
            network_allowed=self.settings.comfyui_runtime_allow_network,
            external_request_attempted=False,
            runtime_calls_enabled=False,
            base_url=self.settings.comfyui_runtime_base_url,
            allowed_hosts=allowed_hosts,
            timeout_seconds=self.settings.comfyui_runtime_timeout_seconds,
            workspace_id=workspace_id,
            error=error,
            raw={
                "phase": "62A",
                "contract_mode": "disabled_by_default",
                "config_ready_for_future_probe": config_ready,
                "parsed_host": host,
                "scheme_allowed": scheme_allowed,
                "host_allowed": host_allowed,
                "no_network_call_performed": True,
                "disabled_actions": DISABLED_COMFYUI_RUNTIME_ACTIONS,
            },
        )

    def capabilities(self, *, workspace_id: str | None = None) -> ComfyUIRuntimeCapabilitiesResponse:
        """Return the guarded contract capabilities for operators and maintainers."""

        provider = self.settings.comfyui_runtime_provider.strip().lower() or "disabled"
        return ComfyUIRuntimeCapabilitiesResponse(
            provider=provider,
            enabled=self.settings.comfyui_runtime_enabled,
            guarded=True,
            mock=True,
            base_url=self.settings.comfyui_runtime_base_url,
            allowed_hosts=sorted(self.settings.comfyui_runtime_allowed_host_set),
            available_actions=[
                "contract_read",
                "configuration_review",
                "disabled_health_contract",
            ],
            disabled_actions=DISABLED_COMFYUI_RUNTIME_ACTIONS,
            guardrails=[
                "COMFYUI_RUNTIME_ENABLED must be true before any future live adapter can be considered",
                "COMFYUI_RUNTIME_ALLOW_NETWORK must be true before any future network probe can be considered",
                "COMFYUI_RUNTIME_BASE_URL host must be in COMFYUI_RUNTIME_ALLOWED_HOSTS",
                "approved/scheduled Commercial Operation runtime activation metadata is required before future execution",
                "Phase 62A does not import adapters, call ComfyUI, read queues, submit prompts, upload files, or generate media",
            ],
            required_configuration=[
                "COMFYUI_RUNTIME_PROVIDER=guarded",
                "COMFYUI_RUNTIME_ENABLED=true",
                "COMFYUI_RUNTIME_ALLOW_NETWORK=true",
                "COMFYUI_RUNTIME_BASE_URL",
                "COMFYUI_RUNTIME_ALLOWED_HOSTS",
                "approved runtime activation record",
            ],
            workspace_id=workspace_id,
            raw={
                "phase": "62A",
                "contract_mode": "guarded_adapter_contract",
                "runtime_calls_enabled": False,
                "external_request_attempted": False,
            },
        )

    def _contract_error(self, *, provider: str, scheme_allowed: bool, host_allowed: bool) -> str:
        if provider != "guarded":
            return "ComfyUI runtime provider is disabled; set COMFYUI_RUNTIME_PROVIDER=guarded in a future live-adapter phase."
        if not self.settings.comfyui_runtime_enabled:
            return "ComfyUI runtime is disabled by COMFYUI_RUNTIME_ENABLED=false."
        if not self.settings.comfyui_runtime_allow_network:
            return "ComfyUI runtime network access is disabled by COMFYUI_RUNTIME_ALLOW_NETWORK=false."
        if not scheme_allowed:
            return "ComfyUI runtime base URL must use http or https."
        if not host_allowed:
            return "ComfyUI runtime base URL host is not in COMFYUI_RUNTIME_ALLOWED_HOSTS."
        return "ComfyUI runtime live probes are not implemented in Phase 62A; no external request was attempted."
