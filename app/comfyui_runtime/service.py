"""Guarded ComfyUI runtime adapter contract service."""

from __future__ import annotations

import json
from math import ceil
from time import perf_counter
from typing import Any, Callable, Mapping
from uuid import UUID
from urllib.error import HTTPError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.comfyui_runtime import (
    ComfyUIRuntimeConfigChangeRequest,
    ComfyUIRuntimeDiagnosticSnapshot,
    ComfyUIRuntimeGuardedProbeExecution,
    ComfyUIRuntimeManualApplyEvidence,
    ComfyUIRuntimePostManualReadinessCheck,
    ComfyUIRuntimeVideoJob,
)
from app.schemas.comfyui_runtime import (
    ComfyUIRuntimeCapabilitiesResponse,
    ComfyUIRuntimeConfigChangeRequestListResponse,
    ComfyUIRuntimeConfigChangeRequestResponse,
    ComfyUIRuntimeDiagnosticCheck,
    ComfyUIRuntimeDiagnosticSnapshotListResponse,
    ComfyUIRuntimeDiagnosticSnapshotResponse,
    ComfyUIRuntimeDiagnosticsResponse,
    ComfyUIRuntimeGuardedProbeExecutionListResponse,
    ComfyUIRuntimeGuardedProbeExecutionResponse,
    ComfyUIRuntimeHealthResponse,
    ComfyUIRuntimeMaintenanceRunbookResponse,
    ComfyUIRuntimeMaintenanceStep,
    ComfyUIRuntimeManualApplyEvidenceListResponse,
    ComfyUIRuntimeManualApplyEvidenceResponse,
    ComfyUIRuntimePromptHistoryResponse,
    ComfyUIRuntimePromptJobSubmitResponse,
    ComfyUIRuntimeQueueResponse,
    ComfyUIRuntimePostManualReadinessCheckListResponse,
    ComfyUIRuntimePostManualReadinessCheckResponse,
    ComfyUIRuntimeVideoJobListResponse,
    ComfyUIRuntimeVideoJobResponse,
    ComfyUIRuntimeVideoResourcePlanResponse,
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
COMFYUI_RUNTIME_CONFIG_CHANGE_STATUSES = {
    "draft",
    "ready_for_review",
    "approved_for_manual_apply",
    "rejected",
    "cancelled",
    "archived",
}
COMFYUI_RUNTIME_MANUAL_APPLY_EVIDENCE_STATUSES = {
    "draft",
    "ready_for_review",
    "verified",
    "rejected",
    "failed",
    "archived",
}
COMFYUI_RUNTIME_POST_MANUAL_READINESS_STATUSES = {
    "draft",
    "ready_for_review",
    "approved_for_read_only_probe",
    "rejected",
    "failed",
    "archived",
}
COMFYUI_RUNTIME_GUARDED_PROBE_EXECUTION_STATUSES = {
    "draft",
    "ready_for_approval",
    "approved_for_execution",
    "rejected",
    "executing",
    "succeeded",
    "failed",
    "cancelled",
    "archived",
}
COMFYUI_RUNTIME_VIDEO_JOB_STATUSES = {
    "draft",
    "resource_blocked",
    "queued",
    "ready_to_submit",
    "submitted",
    "output_ready",
    "failed",
    "cancelled",
    "archived",
}

HttpGet = Callable[[str, float], Mapping[str, Any]]
HttpPost = Callable[[str, Mapping[str, Any], float], Mapping[str, Any]]


class ComfyUIRuntimeService:
    """Expose ComfyUI runtime readiness with an explicit read-only probe gate."""

    def __init__(
        self,
        settings: Settings | None = None,
        http_get: HttpGet | None = None,
        http_post: HttpPost | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.http_get = http_get or self._default_http_get
        self.http_post = http_post or self._default_http_post_json

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
        prompt_submission_ready = self._runtime_execution_error(path="/prompt") is None
        if read_only_probe_ready:
            available_actions.append(COMFYUI_RUNTIME_READ_ONLY_ACTION)
        if prompt_submission_ready:
            available_actions.extend(
                [
                    "submit_comfyui_prompt_job",
                    "read_comfyui_prompt_history",
                    "read_comfyui_queue_status",
                ]
            )
        return ComfyUIRuntimeCapabilitiesResponse(
            provider=provider,
            enabled=self.settings.comfyui_runtime_enabled,
            guarded=True,
            mock=not prompt_submission_ready,
            base_url=self.settings.comfyui_runtime_base_url,
            allowed_hosts=sorted(self.settings.comfyui_runtime_allowed_host_set),
            health_path=health_path,
            allowed_health_paths=sorted(self.settings.comfyui_runtime_allowed_health_path_set),
            read_only_probe_enabled=self.settings.comfyui_runtime_read_only_probe_enabled,
            available_actions=available_actions,
            disabled_actions=self._disabled_actions(
                read_only_probe_ready=read_only_probe_ready,
                prompt_submission_ready=prompt_submission_ready,
            ),
            guardrails=[
                "COMFYUI_RUNTIME_ENABLED must be true before any future live adapter can be considered",
                "COMFYUI_RUNTIME_ALLOW_NETWORK must be true before the read-only health probe can be considered",
                "COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED must be true before a ComfyUI health endpoint is called",
                "COMFYUI_RUNTIME_BASE_URL host must be in COMFYUI_RUNTIME_ALLOWED_HOSTS",
                "COMFYUI_RUNTIME_HEALTH_PATH must be in COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS",
                "COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED must be true before guarded prompt submission is allowed",
                "COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS must allow /prompt, /history, and /queue before real adapter calls",
                "Prompt submission remains disabled unless every explicit guarded runtime gate is enabled",
                "Uploads, secret resolution, account control, publishing, and runtime switch changes remain disabled",
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
                "COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=true",
                "COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS=/prompt,/history,/queue",
            ],
            workspace_id=workspace_id,
            raw={
                "phase": "65A",
                "contract_mode": "guarded_real_prompt_adapter",
                "runtime_calls_enabled": prompt_submission_ready,
                "read_only_probe_ready": read_only_probe_ready,
                "prompt_submission_ready": prompt_submission_ready,
                "allowed_execution_paths": sorted(self.settings.comfyui_runtime_allowed_execution_path_set),
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

    def maintenance_runbook(self, *, workspace_id: str | None = None) -> ComfyUIRuntimeMaintenanceRunbookResponse:
        """Return an operator-facing, no-network maintenance runbook."""

        diagnostics = self.diagnostics(workspace_id=workspace_id)
        steps = [
            ComfyUIRuntimeMaintenanceStep(
                key=f"check_{check.key}",
                title=check.label,
                status=check.status,
                audience="server_maintainer" if check.key != "execution_boundary" else "operations_reviewer",
                detail=check.detail,
                action=check.remediation,
                blocking=check.status == "blocked",
                source_check=check.key,
            )
            for check in diagnostics.diagnostics
        ]
        blocked_steps = [step for step in steps if step.blocking]
        recovery_actions = list(diagnostics.recommended_actions)
        snapshot_action = "Save a diagnostic snapshot before and after any runtime configuration change."
        restart_action = "Restart the API service after changing ComfyUI runtime environment variables, then refresh this runbook."
        boundary_action = (
            "Keep prompt submission, queue reads/submissions, uploads, generation, secret resolution, and switch mutation disabled "
            "until a later reviewed execution phase explicitly enables them."
        )
        for action in [snapshot_action, restart_action, boundary_action]:
            if action not in recovery_actions:
                recovery_actions.append(action)

        if blocked_steps:
            next_operator_action = blocked_steps[0].action or blocked_steps[0].detail
        else:
            next_operator_action = (
                "All no-network gates pass. Save a diagnostic snapshot, then use the health endpoint for the explicitly "
                "guarded GET /system_stats read-only probe only if the maintainer intends to test reachability."
            )

        return ComfyUIRuntimeMaintenanceRunbookResponse(
            workspace_id=workspace_id,
            title="ComfyUI runtime maintenance runbook",
            summary=(
                "No-network maintainer checklist for reviewing provider, runtime switch, network gate, host allowlist, "
                "health path allowlist, and the execution boundary before any guarded read-only probe."
            ),
            readiness_status=diagnostics.readiness_status,
            read_only_probe_ready=diagnostics.read_only_probe_ready,
            external_request_attempted=False,
            runtime_calls_enabled=False,
            next_operator_action=next_operator_action,
            snapshot_recommended=True,
            steps=steps,
            recovery_actions=recovery_actions,
            disabled_actions=list(diagnostics.forbidden_actions),
            configuration_summary={
                "provider": diagnostics.provider,
                "enabled": diagnostics.enabled,
                "network_allowed": diagnostics.network_allowed,
                "read_only_probe_enabled": diagnostics.read_only_probe_enabled,
                "base_url": diagnostics.base_url,
                "parsed_host": diagnostics.parsed_host,
                "host_allowed": diagnostics.host_allowed,
                "health_path": diagnostics.health_path,
                "health_path_allowed": diagnostics.health_path_allowed,
                "allowed_hosts": diagnostics.allowed_hosts,
                "allowed_health_paths": diagnostics.allowed_health_paths,
            },
            diagnostics=diagnostics,
            raw={
                "phase": "62E",
                "contract_mode": "guarded_runtime_maintenance_runbook",
                "no_network_call_performed": True,
                "source_endpoint": "/api/v1/comfyui-runtime/diagnostics",
                "blocked_step_count": len(blocked_steps),
            },
        )

    async def create_config_change_request(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        user_id: str | None = None,
        change_reason: str | None = None,
        requested_changes: list[Mapping[str, Any]] | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeConfigChangeRequestResponse:
        """Persist a metadata-only configuration change request from the current runbook."""

        runbook = self.maintenance_runbook(workspace_id=workspace_id)
        normalized_changes = [dict(item) for item in requested_changes or []]
        if not normalized_changes:
            normalized_changes = self._recommended_config_changes(runbook)
        request_metadata = {
            **dict(metadata or {}),
            "phase": "62F",
            "source": "comfyui_runtime_maintenance_runbook",
            "no_network_call_performed": True,
            "config_mutation_performed": False,
        }
        change_request = ComfyUIRuntimeConfigChangeRequest(
            workspace_id=workspace_id,
            user_id=user_id,
            change_status="draft",
            provider=runbook.diagnostics.provider,
            readiness_status=runbook.readiness_status,
            read_only_probe_ready=runbook.read_only_probe_ready,
            external_request_attempted=False,
            runtime_calls_enabled=False,
            config_mutation_performed=False,
            current_configuration=dict(runbook.configuration_summary),
            requested_changes=normalized_changes,
            runbook_steps=[step.model_dump(mode="json") for step in runbook.steps],
            recovery_actions=list(runbook.recovery_actions),
            disabled_actions=list(runbook.disabled_actions),
            runbook_payload=runbook.model_dump(mode="json"),
            change_reason=change_reason.strip() if change_reason else None,
            operator_note=operator_note.strip() if operator_note else None,
            request_metadata=request_metadata,
        )
        session.add(change_request)
        await session.commit()
        await session.refresh(change_request)
        return ComfyUIRuntimeConfigChangeRequestResponse.from_model(change_request)

    async def list_config_change_requests(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        limit: int = 20,
    ) -> ComfyUIRuntimeConfigChangeRequestListResponse:
        """List recent metadata-only configuration change requests for one workspace."""

        bounded_limit = max(1, min(limit, 100))
        result = await session.execute(
            select(ComfyUIRuntimeConfigChangeRequest)
            .where(ComfyUIRuntimeConfigChangeRequest.workspace_id == workspace_id)
            .order_by(ComfyUIRuntimeConfigChangeRequest.created_at.desc())
            .limit(bounded_limit)
        )
        requests = result.scalars().all()
        return ComfyUIRuntimeConfigChangeRequestListResponse(
            workspace_id=workspace_id,
            items=[ComfyUIRuntimeConfigChangeRequestResponse.from_model(request) for request in requests],
        )

    async def update_config_change_request_status(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        request_id: UUID,
        status: str,
        reviewer_notes: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeConfigChangeRequestResponse:
        """Update review status without mutating ComfyUI runtime configuration."""

        if status not in COMFYUI_RUNTIME_CONFIG_CHANGE_STATUSES:
            raise ValueError(f"Unsupported ComfyUI runtime config change status: {status}")
        result = await session.execute(
            select(ComfyUIRuntimeConfigChangeRequest).where(
                ComfyUIRuntimeConfigChangeRequest.id == request_id,
                ComfyUIRuntimeConfigChangeRequest.workspace_id == workspace_id,
            )
        )
        request = result.scalar_one_or_none()
        if request is None:
            raise LookupError("ComfyUI runtime config change request not found")
        request.change_status = status
        request.reviewer_notes = reviewer_notes.strip() if reviewer_notes else request.reviewer_notes
        request.config_mutation_performed = False
        request.external_request_attempted = False
        request.runtime_calls_enabled = False
        request.request_metadata = {
            **(request.request_metadata or {}),
            **dict(metadata or {}),
            "phase": "62F",
            "last_review_status": status,
            "no_network_call_performed": True,
            "config_mutation_performed": False,
        }
        await session.commit()
        await session.refresh(request)
        return ComfyUIRuntimeConfigChangeRequestResponse.from_model(request)

    async def create_manual_apply_evidence(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        request_id: UUID,
        user_id: str | None = None,
        before_snapshot_id: UUID | None = None,
        after_snapshot_id: UUID | None = None,
        manual_config_applied: bool = True,
        service_restart_reported: bool = False,
        manual_apply_steps: list[Mapping[str, Any]] | None = None,
        restart_evidence: Mapping[str, Any] | None = None,
        rollback_notes: str | None = None,
        verification_notes: str | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeManualApplyEvidenceResponse:
        """Record human-applied configuration evidence without mutating runtime configuration."""

        result = await session.execute(
            select(ComfyUIRuntimeConfigChangeRequest).where(
                ComfyUIRuntimeConfigChangeRequest.id == request_id,
                ComfyUIRuntimeConfigChangeRequest.workspace_id == workspace_id,
            )
        )
        change_request = result.scalar_one_or_none()
        if change_request is None:
            raise LookupError("ComfyUI runtime config change request not found")
        if change_request.change_status != "approved_for_manual_apply":
            raise ValueError("ComfyUI runtime config change request must be approved_for_manual_apply before manual apply evidence can be recorded")

        diagnostics = self.diagnostics(workspace_id=workspace_id)
        diagnostics_payload = diagnostics.model_dump(mode="json")
        normalized_steps = [dict(item) for item in manual_apply_steps or []]
        if not normalized_steps:
            normalized_steps = self._manual_apply_steps_from_request(change_request)
        config_request_payload = ComfyUIRuntimeConfigChangeRequestResponse.from_model(change_request).model_dump(mode="json")
        evidence_metadata = {
            **dict(metadata or {}),
            "phase": "62G",
            "source": "comfyui_runtime_manual_apply_evidence",
            "no_network_call_performed": True,
            "api_config_mutation_performed": False,
            "external_request_attempted": False,
            "runtime_calls_enabled": False,
        }
        verification_results = {
            "post_change_diagnostics_captured": True,
            "health_probe_executed": False,
            "readiness_status_after": diagnostics.readiness_status,
            "read_only_probe_ready_after": diagnostics.read_only_probe_ready,
            "service_restart_reported": service_restart_reported,
            "api_config_mutation_performed": False,
            "external_request_attempted": False,
            "runtime_calls_enabled": False,
        }
        evidence = ComfyUIRuntimeManualApplyEvidence(
            workspace_id=workspace_id,
            user_id=user_id,
            config_change_request_id=request_id,
            before_snapshot_id=before_snapshot_id,
            after_snapshot_id=after_snapshot_id,
            evidence_status="draft",
            provider=diagnostics.provider,
            readiness_status_before=change_request.readiness_status,
            readiness_status_after=diagnostics.readiness_status,
            read_only_probe_ready_before=change_request.read_only_probe_ready,
            read_only_probe_ready_after=diagnostics.read_only_probe_ready,
            external_request_attempted=False,
            runtime_calls_enabled=False,
            api_config_mutation_performed=False,
            manual_config_applied=manual_config_applied,
            service_restart_reported=service_restart_reported,
            config_change_request_payload=config_request_payload,
            current_configuration_before=change_request.current_configuration or {},
            current_configuration_after=self._configuration_summary_from_diagnostics(diagnostics),
            requested_changes=change_request.requested_changes or [],
            manual_apply_steps=normalized_steps,
            restart_evidence=dict(restart_evidence or {}),
            verification_results=verification_results,
            diagnostics_payload=diagnostics_payload,
            rollback_notes=rollback_notes.strip() if rollback_notes else None,
            verification_notes=verification_notes.strip() if verification_notes else None,
            operator_note=operator_note.strip() if operator_note else None,
            evidence_metadata=evidence_metadata,
        )
        session.add(evidence)
        await session.commit()
        await session.refresh(evidence)
        return ComfyUIRuntimeManualApplyEvidenceResponse.from_model(evidence)

    async def list_manual_apply_evidence(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        limit: int = 20,
    ) -> ComfyUIRuntimeManualApplyEvidenceListResponse:
        """List recent metadata-only manual apply evidence for one workspace."""

        bounded_limit = max(1, min(limit, 100))
        result = await session.execute(
            select(ComfyUIRuntimeManualApplyEvidence)
            .where(ComfyUIRuntimeManualApplyEvidence.workspace_id == workspace_id)
            .order_by(ComfyUIRuntimeManualApplyEvidence.created_at.desc())
            .limit(bounded_limit)
        )
        evidence = result.scalars().all()
        return ComfyUIRuntimeManualApplyEvidenceListResponse(
            workspace_id=workspace_id,
            items=[ComfyUIRuntimeManualApplyEvidenceResponse.from_model(item) for item in evidence],
        )

    async def update_manual_apply_evidence_status(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        evidence_id: UUID,
        status: str,
        reviewer_notes: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeManualApplyEvidenceResponse:
        """Update manual apply evidence review status without performing runtime actions."""

        if status not in COMFYUI_RUNTIME_MANUAL_APPLY_EVIDENCE_STATUSES:
            raise ValueError(f"Unsupported ComfyUI runtime manual apply evidence status: {status}")
        result = await session.execute(
            select(ComfyUIRuntimeManualApplyEvidence).where(
                ComfyUIRuntimeManualApplyEvidence.id == evidence_id,
                ComfyUIRuntimeManualApplyEvidence.workspace_id == workspace_id,
            )
        )
        evidence = result.scalar_one_or_none()
        if evidence is None:
            raise LookupError("ComfyUI runtime manual apply evidence not found")
        evidence.evidence_status = status
        evidence.reviewer_notes = reviewer_notes.strip() if reviewer_notes else evidence.reviewer_notes
        evidence.api_config_mutation_performed = False
        evidence.external_request_attempted = False
        evidence.runtime_calls_enabled = False
        evidence.evidence_metadata = {
            **(evidence.evidence_metadata or {}),
            **dict(metadata or {}),
            "phase": "62G",
            "last_review_status": status,
            "no_network_call_performed": True,
            "api_config_mutation_performed": False,
            "external_request_attempted": False,
            "runtime_calls_enabled": False,
        }
        await session.commit()
        await session.refresh(evidence)
        return ComfyUIRuntimeManualApplyEvidenceResponse.from_model(evidence)

    async def create_post_manual_readiness_check(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        evidence_id: UUID,
        user_id: str | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimePostManualReadinessCheckResponse:
        """Compare verified manual apply evidence with current no-network diagnostics."""

        result = await session.execute(
            select(ComfyUIRuntimeManualApplyEvidence).where(
                ComfyUIRuntimeManualApplyEvidence.id == evidence_id,
                ComfyUIRuntimeManualApplyEvidence.workspace_id == workspace_id,
            )
        )
        evidence = result.scalar_one_or_none()
        if evidence is None:
            raise LookupError("ComfyUI runtime manual apply evidence not found")
        if evidence.evidence_status != "verified":
            raise ValueError("ComfyUI runtime manual apply evidence must be verified before post-manual readiness can be checked")

        diagnostics = self.diagnostics(workspace_id=workspace_id)
        comparison = self._post_manual_readiness_comparison(evidence, diagnostics)
        evidence_payload = ComfyUIRuntimeManualApplyEvidenceResponse.from_model(evidence).model_dump(mode="json")
        check_metadata = {
            **dict(metadata or {}),
            "phase": "62H",
            "source": "comfyui_runtime_post_manual_readiness",
            "no_network_call_performed": True,
            "health_probe_executed": False,
            "api_config_mutation_performed": False,
            "external_request_attempted": False,
            "runtime_calls_enabled": False,
        }
        check = ComfyUIRuntimePostManualReadinessCheck(
            workspace_id=workspace_id,
            user_id=user_id,
            manual_apply_evidence_id=evidence_id,
            config_change_request_id=evidence.config_change_request_id,
            check_status="draft",
            comparison_status=comparison["comparison_status"],
            provider=diagnostics.provider,
            readiness_status_before=evidence.readiness_status_before,
            readiness_status_after_evidence=evidence.readiness_status_after,
            readiness_status_current=diagnostics.readiness_status,
            read_only_probe_ready_before=evidence.read_only_probe_ready_before,
            read_only_probe_ready_after_evidence=evidence.read_only_probe_ready_after,
            read_only_probe_ready_current=diagnostics.read_only_probe_ready,
            guarded_probe_ready=bool(comparison["guarded_probe_ready"]),
            manual_evidence_status=evidence.evidence_status,
            manual_config_applied=evidence.manual_config_applied,
            service_restart_reported=evidence.service_restart_reported,
            external_request_attempted=False,
            runtime_calls_enabled=False,
            health_probe_executed=False,
            api_config_mutation_performed=False,
            requested_changes=evidence.requested_changes or [],
            manual_apply_steps=evidence.manual_apply_steps or [],
            restart_evidence=evidence.restart_evidence or {},
            evidence_payload=evidence_payload,
            current_diagnostics_payload=diagnostics.model_dump(mode="json"),
            comparison_results=comparison,
            blocking_reasons=list(comparison["blocking_reasons"]),
            recommended_actions=list(comparison["recommended_actions"]),
            next_operator_action=comparison["next_operator_action"],
            operator_note=operator_note.strip() if operator_note else None,
            check_metadata=check_metadata,
        )
        session.add(check)
        await session.commit()
        await session.refresh(check)
        return ComfyUIRuntimePostManualReadinessCheckResponse.from_model(check)

    async def list_post_manual_readiness_checks(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        limit: int = 20,
    ) -> ComfyUIRuntimePostManualReadinessCheckListResponse:
        """List recent post-manual readiness comparisons for one workspace."""

        bounded_limit = max(1, min(limit, 100))
        result = await session.execute(
            select(ComfyUIRuntimePostManualReadinessCheck)
            .where(ComfyUIRuntimePostManualReadinessCheck.workspace_id == workspace_id)
            .order_by(ComfyUIRuntimePostManualReadinessCheck.created_at.desc())
            .limit(bounded_limit)
        )
        checks = result.scalars().all()
        return ComfyUIRuntimePostManualReadinessCheckListResponse(
            workspace_id=workspace_id,
            items=[ComfyUIRuntimePostManualReadinessCheckResponse.from_model(check) for check in checks],
        )

    async def update_post_manual_readiness_check_status(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        check_id: UUID,
        status: str,
        reviewer_notes: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimePostManualReadinessCheckResponse:
        """Update post-manual readiness review status without performing runtime actions."""

        if status not in COMFYUI_RUNTIME_POST_MANUAL_READINESS_STATUSES:
            raise ValueError(f"Unsupported ComfyUI runtime post-manual readiness status: {status}")
        result = await session.execute(
            select(ComfyUIRuntimePostManualReadinessCheck).where(
                ComfyUIRuntimePostManualReadinessCheck.id == check_id,
                ComfyUIRuntimePostManualReadinessCheck.workspace_id == workspace_id,
            )
        )
        check = result.scalar_one_or_none()
        if check is None:
            raise LookupError("ComfyUI runtime post-manual readiness check not found")
        if status == "approved_for_read_only_probe" and not check.guarded_probe_ready:
            raise ValueError("Post-manual readiness check must be ready for guarded read-only probe before approval")
        check.check_status = status
        check.reviewer_notes = reviewer_notes.strip() if reviewer_notes else check.reviewer_notes
        check.api_config_mutation_performed = False
        check.external_request_attempted = False
        check.runtime_calls_enabled = False
        check.health_probe_executed = False
        check.check_metadata = {
            **(check.check_metadata or {}),
            **dict(metadata or {}),
            "phase": "62H",
            "last_review_status": status,
            "no_network_call_performed": True,
            "health_probe_executed": False,
            "api_config_mutation_performed": False,
            "external_request_attempted": False,
            "runtime_calls_enabled": False,
        }
        await session.commit()
        await session.refresh(check)
        return ComfyUIRuntimePostManualReadinessCheckResponse.from_model(check)

    async def create_guarded_probe_execution(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        check_id: UUID,
        user_id: str | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeGuardedProbeExecutionResponse:
        """Create an auditable approval record for a later guarded read-only probe."""

        result = await session.execute(
            select(ComfyUIRuntimePostManualReadinessCheck).where(
                ComfyUIRuntimePostManualReadinessCheck.id == check_id,
                ComfyUIRuntimePostManualReadinessCheck.workspace_id == workspace_id,
            )
        )
        check = result.scalar_one_or_none()
        if check is None:
            raise LookupError("ComfyUI runtime post-manual readiness check not found")
        if check.check_status != "approved_for_read_only_probe":
            raise ValueError("Post-manual readiness check must be approved before creating a guarded probe execution")
        if not check.guarded_probe_ready:
            raise ValueError("Post-manual readiness check must be ready for guarded read-only probe execution")

        diagnostics = self.diagnostics(workspace_id=workspace_id)
        if not diagnostics.read_only_probe_ready:
            raise ValueError("Current diagnostics are no longer ready for guarded read-only probe execution")

        readiness_payload = ComfyUIRuntimePostManualReadinessCheckResponse.from_model(check).model_dump(mode="json")
        diagnostics_payload = diagnostics.model_dump(mode="json")
        probe_request = {
            "method": "GET",
            "url": self._build_probe_url(diagnostics.base_url, diagnostics.health_path),
            "health_path": diagnostics.health_path,
            "allowed_hosts": diagnostics.allowed_hosts,
            "allowed_health_paths": diagnostics.allowed_health_paths,
            "read_only": True,
            "requires_execute_endpoint": True,
        }
        execution_metadata = {
            **dict(metadata or {}),
            "phase": "62J",
            "source": "comfyui_runtime_guarded_probe_execution",
            "no_network_call_performed": True,
            "created_from_post_manual_readiness_check": str(check_id),
            "health_probe_executed": False,
            "api_config_mutation_performed": False,
            "external_request_attempted": False,
            "runtime_calls_enabled": False,
        }
        execution = ComfyUIRuntimeGuardedProbeExecution(
            workspace_id=workspace_id,
            user_id=user_id,
            post_manual_readiness_check_id=check_id,
            manual_apply_evidence_id=check.manual_apply_evidence_id,
            config_change_request_id=check.config_change_request_id,
            execution_status="draft",
            provider=diagnostics.provider,
            readiness_status_current=diagnostics.readiness_status,
            read_only_probe_ready_current=diagnostics.read_only_probe_ready,
            guarded_probe_ready=True,
            base_url=diagnostics.base_url,
            health_path=diagnostics.health_path,
            allowed_hosts=list(diagnostics.allowed_hosts),
            allowed_health_paths=list(diagnostics.allowed_health_paths),
            external_request_attempted=False,
            runtime_calls_enabled=False,
            health_probe_executed=False,
            read_only_probe_attempted=False,
            api_config_mutation_performed=False,
            probe_status_code=None,
            probe_latency_ms=None,
            probe_result_status="not_started",
            readiness_check_payload=readiness_payload,
            current_diagnostics_payload=diagnostics_payload,
            probe_request=probe_request,
            probe_response={},
            blocking_reasons=list(diagnostics.blocking_reasons),
            recommended_actions=list(diagnostics.recommended_actions),
            disabled_actions=self._disabled_actions(read_only_probe_ready=diagnostics.read_only_probe_ready),
            operator_note=operator_note.strip() if operator_note else None,
            execution_metadata=execution_metadata,
        )
        session.add(execution)
        await session.commit()
        await session.refresh(execution)
        return ComfyUIRuntimeGuardedProbeExecutionResponse.from_model(execution)

    async def list_guarded_probe_executions(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        limit: int = 20,
    ) -> ComfyUIRuntimeGuardedProbeExecutionListResponse:
        """List recent guarded read-only probe execution audit records for one workspace."""

        bounded_limit = max(1, min(limit, 100))
        result = await session.execute(
            select(ComfyUIRuntimeGuardedProbeExecution)
            .where(ComfyUIRuntimeGuardedProbeExecution.workspace_id == workspace_id)
            .order_by(ComfyUIRuntimeGuardedProbeExecution.created_at.desc())
            .limit(bounded_limit)
        )
        executions = result.scalars().all()
        return ComfyUIRuntimeGuardedProbeExecutionListResponse(
            workspace_id=workspace_id,
            items=[ComfyUIRuntimeGuardedProbeExecutionResponse.from_model(execution) for execution in executions],
        )

    async def update_guarded_probe_execution_status(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        execution_id: UUID,
        status: str,
        reviewer_notes: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeGuardedProbeExecutionResponse:
        """Update guarded probe execution review status without calling ComfyUI."""

        if status not in COMFYUI_RUNTIME_GUARDED_PROBE_EXECUTION_STATUSES:
            raise ValueError(f"Unsupported ComfyUI runtime guarded probe execution status: {status}")
        result = await session.execute(
            select(ComfyUIRuntimeGuardedProbeExecution).where(
                ComfyUIRuntimeGuardedProbeExecution.id == execution_id,
                ComfyUIRuntimeGuardedProbeExecution.workspace_id == workspace_id,
            )
        )
        execution = result.scalar_one_or_none()
        if execution is None:
            raise LookupError("ComfyUI runtime guarded probe execution not found")
        if status == "approved_for_execution" and execution.execution_status != "ready_for_approval":
            raise ValueError("Guarded probe execution must be ready for approval before execution approval")
        if status == "ready_for_approval" and execution.execution_status not in {"draft", "rejected"}:
            raise ValueError("Guarded probe execution can only be marked ready from draft or rejected")
        execution.execution_status = status
        execution.reviewer_notes = reviewer_notes.strip() if reviewer_notes else execution.reviewer_notes
        execution.api_config_mutation_performed = False
        execution.runtime_calls_enabled = False
        execution.execution_metadata = {
            **(execution.execution_metadata or {}),
            **dict(metadata or {}),
            "phase": "62J",
            "last_review_status": status,
            "status_update_no_network_call_performed": True,
            "health_probe_executed": execution.health_probe_executed,
            "api_config_mutation_performed": False,
            "external_request_attempted": execution.external_request_attempted,
            "runtime_calls_enabled": False,
        }
        await session.commit()
        await session.refresh(execution)
        return ComfyUIRuntimeGuardedProbeExecutionResponse.from_model(execution)

    async def execute_guarded_probe_execution(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        execution_id: UUID,
        reviewer_notes: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeGuardedProbeExecutionResponse:
        """Run the approved guarded read-only health probe and persist the outcome."""

        result = await session.execute(
            select(ComfyUIRuntimeGuardedProbeExecution).where(
                ComfyUIRuntimeGuardedProbeExecution.id == execution_id,
                ComfyUIRuntimeGuardedProbeExecution.workspace_id == workspace_id,
            )
        )
        execution = result.scalar_one_or_none()
        if execution is None:
            raise LookupError("ComfyUI runtime guarded probe execution not found")
        if execution.execution_status != "approved_for_execution":
            raise ValueError("Guarded probe execution must be approved before execute can run")

        diagnostics = self.diagnostics(workspace_id=workspace_id)
        diagnostics_payload = diagnostics.model_dump(mode="json")
        execution.current_diagnostics_payload = diagnostics_payload
        execution.provider = diagnostics.provider
        execution.readiness_status_current = diagnostics.readiness_status
        execution.read_only_probe_ready_current = diagnostics.read_only_probe_ready
        execution.base_url = diagnostics.base_url
        execution.health_path = diagnostics.health_path
        execution.allowed_hosts = list(diagnostics.allowed_hosts)
        execution.allowed_health_paths = list(diagnostics.allowed_health_paths)
        execution.blocking_reasons = list(diagnostics.blocking_reasons)
        execution.recommended_actions = list(diagnostics.recommended_actions)
        execution.disabled_actions = self._disabled_actions(read_only_probe_ready=diagnostics.read_only_probe_ready)
        execution.probe_request = {
            "method": "GET",
            "url": self._build_probe_url(diagnostics.base_url, diagnostics.health_path),
            "health_path": diagnostics.health_path,
            "allowed_hosts": diagnostics.allowed_hosts,
            "allowed_health_paths": diagnostics.allowed_health_paths,
            "read_only": True,
            "requires_execute_endpoint": True,
        }
        execution.reviewer_notes = reviewer_notes.strip() if reviewer_notes else execution.reviewer_notes
        execution.api_config_mutation_performed = False
        execution.runtime_calls_enabled = False

        if not diagnostics.read_only_probe_ready:
            execution.execution_status = "failed"
            execution.probe_result_status = "blocked_before_execution"
            execution.external_request_attempted = False
            execution.health_probe_executed = False
            execution.read_only_probe_attempted = False
            execution.probe_response = {
                "success": False,
                "reachable": False,
                "error": "Current diagnostics are no longer ready for guarded read-only probe execution.",
                "diagnostics": diagnostics_payload,
            }
            execution.execution_metadata = {
                **(execution.execution_metadata or {}),
                **dict(metadata or {}),
                "phase": "62J",
                "last_review_status": "failed",
                "no_network_call_performed": True,
                "health_probe_executed": False,
                "api_config_mutation_performed": False,
                "external_request_attempted": False,
                "runtime_calls_enabled": False,
            }
            await session.commit()
            await session.refresh(execution)
            return ComfyUIRuntimeGuardedProbeExecutionResponse.from_model(execution)

        health = self.health_check(workspace_id=workspace_id)
        health_payload = health.model_dump(mode="json")
        execution.execution_status = "succeeded" if health.reachable else "failed"
        execution.external_request_attempted = health.external_request_attempted
        execution.health_probe_executed = health.read_only_probe_attempted
        execution.read_only_probe_attempted = health.read_only_probe_attempted
        execution.runtime_calls_enabled = False
        execution.api_config_mutation_performed = False
        execution.probe_status_code = health.probe_status_code
        execution.probe_latency_ms = health.probe_latency_ms
        execution.probe_result_status = "reachable" if health.reachable else "unreachable"
        execution.probe_response = health_payload
        execution.execution_metadata = {
            **(execution.execution_metadata or {}),
            **dict(metadata or {}),
            "phase": "62J",
            "last_review_status": execution.execution_status,
            "no_network_call_performed": False,
            "health_probe_executed": health.read_only_probe_attempted,
            "api_config_mutation_performed": False,
            "external_request_attempted": health.external_request_attempted,
            "runtime_calls_enabled": False,
        }
        await session.commit()
        await session.refresh(execution)
        return ComfyUIRuntimeGuardedProbeExecutionResponse.from_model(execution)

    async def create_diagnostic_snapshot(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        user_id: str | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeDiagnosticSnapshotResponse:
        """Persist a no-network diagnostics snapshot for maintainer audit trails."""

        diagnostics = self.diagnostics(workspace_id=workspace_id)
        snapshot_payload = diagnostics.model_dump(mode="json")
        snapshot_metadata = {
            **dict(metadata or {}),
            "phase": "62D",
            "source": "comfyui_runtime_diagnostics",
            "no_network_call_performed": True,
        }
        snapshot = ComfyUIRuntimeDiagnosticSnapshot(
            workspace_id=workspace_id,
            user_id=user_id,
            provider=diagnostics.provider,
            enabled=diagnostics.enabled,
            guarded=diagnostics.guarded,
            network_allowed=diagnostics.network_allowed,
            read_only_probe_enabled=diagnostics.read_only_probe_enabled,
            base_url=diagnostics.base_url,
            parsed_host=diagnostics.parsed_host,
            scheme_allowed=diagnostics.scheme_allowed,
            host_allowed=diagnostics.host_allowed,
            allowed_hosts=list(diagnostics.allowed_hosts),
            health_path=diagnostics.health_path,
            health_path_allowed=diagnostics.health_path_allowed,
            allowed_health_paths=list(diagnostics.allowed_health_paths),
            read_only_probe_ready=diagnostics.read_only_probe_ready,
            readiness_status=diagnostics.readiness_status,
            external_request_attempted=diagnostics.external_request_attempted,
            runtime_calls_enabled=diagnostics.runtime_calls_enabled,
            blocking_reasons=list(diagnostics.blocking_reasons),
            recommended_actions=list(diagnostics.recommended_actions),
            diagnostics=[check.model_dump(mode="json") for check in diagnostics.diagnostics],
            forbidden_actions=list(diagnostics.forbidden_actions),
            snapshot_payload=snapshot_payload,
            operator_note=operator_note.strip() if operator_note else None,
            snapshot_metadata=snapshot_metadata,
        )
        session.add(snapshot)
        await session.commit()
        await session.refresh(snapshot)
        return ComfyUIRuntimeDiagnosticSnapshotResponse.from_model(snapshot)

    async def list_diagnostic_snapshots(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        limit: int = 20,
    ) -> ComfyUIRuntimeDiagnosticSnapshotListResponse:
        """List recent persisted no-network diagnostics snapshots for one workspace."""

        bounded_limit = max(1, min(limit, 100))
        result = await session.execute(
            select(ComfyUIRuntimeDiagnosticSnapshot)
            .where(ComfyUIRuntimeDiagnosticSnapshot.workspace_id == workspace_id)
            .order_by(ComfyUIRuntimeDiagnosticSnapshot.created_at.desc())
            .limit(bounded_limit)
        )
        snapshots = result.scalars().all()
        return ComfyUIRuntimeDiagnosticSnapshotListResponse(
            workspace_id=workspace_id,
            items=[ComfyUIRuntimeDiagnosticSnapshotResponse.from_model(snapshot) for snapshot in snapshots],
        )

    async def create_video_job(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        user_id: str | None = None,
        prompt: Mapping[str, Any] | None = None,
        workflow: Mapping[str, Any] | None = None,
        extra_data: Mapping[str, Any] | None = None,
        client_id: str | None = None,
        resource_profile: str = "standard",
        width: int | None = 1280,
        height: int | None = 720,
        frames: int | None = 96,
        fps: float | None = 24.0,
        duration_seconds: float | None = None,
        estimated_vram_mb: int | None = None,
        reserve_vram_mb: int | None = None,
        submit_immediately: bool = True,
        poll_history: bool = True,
        operator_note: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeVideoJobResponse:
        """Create a persisted video job and submit it through the guarded ComfyUI gates when allowed."""

        normalized = self._normalize_video_job_request(
            resource_profile=resource_profile,
            width=width,
            height=height,
            frames=frames,
            fps=fps,
            duration_seconds=duration_seconds,
            estimated_vram_mb=estimated_vram_mb,
            reserve_vram_mb=reserve_vram_mb,
        )
        request_metadata = {
            **dict(metadata or {}),
            "phase": str((metadata or {}).get("phase") or "66B"),
            "media_type": "video",
            "source": "comfyui_runtime_video_job",
            "submit_immediately": bool(submit_immediately),
        }
        submit = None
        history = None
        queue = None
        outputs: list[dict[str, Any]] = []
        planned_resource_plan: dict[str, Any] = {}
        if not submit_immediately:
            planned_resource_plan = self.video_resource_plan(
                workspace_id=workspace_id,
                resource_profile=normalized["resource_profile"],
                width=normalized["width"],
                height=normalized["height"],
                frames=normalized["frames"],
                fps=normalized["fps"],
                duration_seconds=normalized["duration_seconds"],
                estimated_vram_mb=normalized["estimated_vram_mb"],
                reserve_vram_mb=normalized["reserve_vram_mb"],
                metadata={**request_metadata, "source": "comfyui_runtime_video_job_plan"},
            ).model_dump(mode="json")
        if submit_immediately:
            submit = self.submit_prompt_job(
                workspace_id=workspace_id,
                prompt=dict(prompt or {}),
                client_id=client_id,
                extra_data=extra_data,
                workflow=workflow,
                media_type="video",
                resource_profile=normalized["resource_profile"],
                width=normalized["width"],
                height=normalized["height"],
                frames=normalized["frames"],
                fps=normalized["fps"],
                duration_seconds=normalized["duration_seconds"],
                estimated_vram_mb=normalized["estimated_vram_mb"],
                reserve_vram_mb=normalized["reserve_vram_mb"],
                metadata=request_metadata,
            )
            if submit.success and submit.prompt_id and poll_history:
                history, queue = self._poll_video_job_runtime(
                    workspace_id=workspace_id,
                    prompt_id=submit.prompt_id,
                    base_url=submit.base_url,
                )
                outputs = self._extract_prompt_output_files(history.outputs if history else {})

        resource_plan = self._video_resource_plan_from_submit(submit) or planned_resource_plan
        queue_payload = dict(queue.response_payload) if queue else self._queue_payload_from_resource_plan(resource_plan)
        job_status = self._video_job_status_from_runtime(submit=submit, resource_plan=resource_plan, outputs=outputs)
        failure_reason = self._video_job_failure_reason(submit=submit, history=history, queue=queue, status=job_status)
        job = ComfyUIRuntimeVideoJob(
            workspace_id=workspace_id,
            user_id=user_id,
            job_status=job_status,
            provider=self._provider(),
            media_type="video",
            resource_profile=normalized["resource_profile"],
            client_id=client_id,
            prompt=dict(prompt or {}),
            workflow=dict(workflow or {}),
            extra_data=dict(extra_data or {}),
            width=normalized["width"],
            height=normalized["height"],
            frames=normalized["frames"],
            fps=normalized["fps"],
            duration_seconds=normalized["duration_seconds"],
            estimated_vram_mb=normalized["estimated_vram_mb"],
            reserve_vram_mb=normalized["reserve_vram_mb"],
            resource_plan=resource_plan,
            selected_endpoint=self._selected_endpoint_from_resource_plan(resource_plan),
            selected_gpu=self._selected_gpu_from_resource_plan(resource_plan),
            runtime_base_url=submit.base_url if submit else self.settings.comfyui_runtime_base_url,
            runtime_prompt_id=submit.prompt_id if submit else None,
            submit_payload=submit.request_payload if submit else {},
            submit_response=submit.response_payload if submit else {},
            history_payload=history.response_payload if history else {},
            queue_payload=queue_payload,
            outputs=outputs,
            external_request_attempted=bool(
                (submit.external_request_attempted if submit else False)
                or (history.external_request_attempted if history else False)
                or (queue.external_request_attempted if queue else False)
            ),
            runtime_calls_enabled=bool(
                (submit.runtime_calls_enabled if submit else False)
                or (history.runtime_calls_enabled if history else False)
                or (queue.runtime_calls_enabled if queue else False)
            ),
            prompt_submission_enabled=self.settings.comfyui_runtime_prompt_submission_enabled,
            failure_reason=failure_reason,
            result_summary=self._video_job_result_summary(status=job_status, prompt_id=submit.prompt_id if submit else None, outputs=outputs),
            operator_note=operator_note,
            job_metadata=request_metadata,
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return ComfyUIRuntimeVideoJobResponse.from_model(job)

    async def list_video_jobs(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 20,
    ) -> ComfyUIRuntimeVideoJobListResponse:
        """List recent ComfyUI video jobs for one workspace."""

        bounded_limit = max(1, min(limit, 100))
        query = select(ComfyUIRuntimeVideoJob).where(ComfyUIRuntimeVideoJob.workspace_id == workspace_id)
        if status:
            query = query.where(ComfyUIRuntimeVideoJob.job_status == status)
        result = await session.execute(query.order_by(ComfyUIRuntimeVideoJob.created_at.desc()).limit(bounded_limit))
        jobs = result.scalars().all()
        return ComfyUIRuntimeVideoJobListResponse(
            workspace_id=workspace_id,
            items=[ComfyUIRuntimeVideoJobResponse.from_model(job) for job in jobs],
        )

    async def get_video_job(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
    ) -> ComfyUIRuntimeVideoJobResponse:
        """Return one ComfyUI video job by id."""

        job = await self._get_video_job_model(session, workspace_id=workspace_id, job_id=job_id)
        return ComfyUIRuntimeVideoJobResponse.from_model(job)

    async def refresh_video_job(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
        poll_history: bool = True,
        resubmit_if_waiting: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeVideoJobResponse:
        """Refresh a persisted video job from guarded ComfyUI queue/history, resubmitting waiting jobs when allowed."""

        job = await self._get_video_job_model(session, workspace_id=workspace_id, job_id=job_id)
        if job.job_status in {"cancelled", "archived"}:
            return ComfyUIRuntimeVideoJobResponse.from_model(job)

        submit = None
        history = None
        queue = None
        outputs = list(job.outputs or [])
        merged_metadata = {
            **(job.job_metadata or {}),
            **dict(metadata or {}),
            "phase": "66B",
            "refresh_attempted": True,
        }

        if job.runtime_prompt_id:
            if poll_history:
                history, queue = self._poll_video_job_runtime(
                    workspace_id=workspace_id,
                    prompt_id=job.runtime_prompt_id,
                    base_url=job.runtime_base_url or self.settings.comfyui_runtime_base_url,
                )
                outputs = self._extract_prompt_output_files(history.outputs if history else {})
        elif resubmit_if_waiting and job.job_status in {"draft", "resource_blocked", "queued", "failed"}:
            submit = self.submit_prompt_job(
                workspace_id=workspace_id,
                prompt=job.prompt or {},
                client_id=job.client_id,
                extra_data=job.extra_data or {},
                workflow=job.workflow or {},
                media_type="video",
                resource_profile=job.resource_profile,
                width=job.width,
                height=job.height,
                frames=job.frames,
                fps=job.fps,
                duration_seconds=job.duration_seconds,
                estimated_vram_mb=job.estimated_vram_mb,
                reserve_vram_mb=job.reserve_vram_mb,
                metadata=merged_metadata,
            )
            if submit.success and submit.prompt_id and poll_history:
                history, queue = self._poll_video_job_runtime(
                    workspace_id=workspace_id,
                    prompt_id=submit.prompt_id,
                    base_url=submit.base_url,
                )
                outputs = self._extract_prompt_output_files(history.outputs if history else {})

        resource_plan = self._video_resource_plan_from_submit(submit) or (job.resource_plan or {})
        job.job_status = self._video_job_status_from_runtime(
            submit=submit,
            resource_plan=resource_plan,
            outputs=outputs,
            current_status=job.job_status,
            has_prompt_id=bool(job.runtime_prompt_id or (submit.prompt_id if submit else None)),
        )
        job.resource_plan = resource_plan
        job.selected_endpoint = self._selected_endpoint_from_resource_plan(resource_plan)
        job.selected_gpu = self._selected_gpu_from_resource_plan(resource_plan)
        if submit:
            job.runtime_base_url = submit.base_url
            job.runtime_prompt_id = submit.prompt_id
            job.submit_payload = submit.request_payload
            job.submit_response = submit.response_payload
        if history:
            job.history_payload = history.response_payload
        if queue:
            job.queue_payload = queue.response_payload
        elif resource_plan:
            job.queue_payload = self._queue_payload_from_resource_plan(resource_plan)
        job.outputs = outputs
        job.external_request_attempted = bool(
            job.external_request_attempted
            or (submit.external_request_attempted if submit else False)
            or (history.external_request_attempted if history else False)
            or (queue.external_request_attempted if queue else False)
        )
        job.runtime_calls_enabled = bool(
            (submit.runtime_calls_enabled if submit else False)
            or (history.runtime_calls_enabled if history else False)
            or (queue.runtime_calls_enabled if queue else False)
        )
        job.prompt_submission_enabled = self.settings.comfyui_runtime_prompt_submission_enabled
        job.failure_reason = self._video_job_failure_reason(
            submit=submit,
            history=history,
            queue=queue,
            status=job.job_status,
        ) or job.failure_reason
        job.result_summary = self._video_job_result_summary(status=job.job_status, prompt_id=job.runtime_prompt_id, outputs=outputs)
        job.job_metadata = merged_metadata
        await session.commit()
        await session.refresh(job)
        return ComfyUIRuntimeVideoJobResponse.from_model(job)

    def submit_prompt_job(
        self,
        *,
        prompt: Mapping[str, Any],
        client_id: str | None = None,
        extra_data: Mapping[str, Any] | None = None,
        workflow: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        workspace_id: str | None = None,
        media_type: str = "image",
        resource_profile: str = "standard",
        width: int | None = None,
        height: int | None = None,
        frames: int | None = None,
        fps: float | None = None,
        duration_seconds: float | None = None,
        estimated_vram_mb: int | None = None,
        reserve_vram_mb: int | None = None,
    ) -> ComfyUIRuntimePromptJobSubmitResponse:
        """Submit one guarded real ComfyUI prompt job to /prompt."""

        request_payload: dict[str, Any] = {"prompt": dict(prompt or {})}
        if client_id:
            request_payload["client_id"] = client_id
        merged_extra_data = dict(extra_data or {})
        if workflow is not None:
            extra_pnginfo = dict(merged_extra_data.get("extra_pnginfo") or {})
            extra_pnginfo["workflow"] = dict(workflow)
            merged_extra_data["extra_pnginfo"] = extra_pnginfo
        if merged_extra_data:
            request_payload["extra_data"] = merged_extra_data

        clean_media_type = str(media_type or "image").strip().lower()
        target_base_url = self.settings.comfyui_runtime_base_url
        resource_plan_payload: dict[str, Any] | None = None
        if clean_media_type in {"video", "animation", "motion"}:
            resource_plan = self.video_resource_plan(
                workspace_id=workspace_id,
                resource_profile=resource_profile,
                width=width or self._dimension_from_prompt(prompt, "width", 1280),
                height=height or self._dimension_from_prompt(prompt, "height", 720),
                frames=frames or self._frames_from_prompt(prompt, duration_seconds=duration_seconds, fps=fps or 24.0),
                fps=fps or 24.0,
                duration_seconds=duration_seconds,
                estimated_vram_mb=estimated_vram_mb,
                reserve_vram_mb=reserve_vram_mb,
                metadata={**dict(metadata or {}), "source": "submit_prompt_job"},
            )
            selected_endpoint = resource_plan.selected_endpoint or {}
            target_base_url = str(selected_endpoint.get("base_url") or target_base_url)
            if not resource_plan.should_submit_now:
                plan_payload = resource_plan.model_dump(mode="json")
                return ComfyUIRuntimePromptJobSubmitResponse(
                    success=False,
                    workspace_id=workspace_id,
                    provider=self._provider(),
                    enabled=self.settings.comfyui_runtime_enabled,
                    base_url=target_base_url,
                    external_request_attempted=resource_plan.external_request_attempted,
                    runtime_calls_enabled=False,
                    prompt_submission_enabled=self.settings.comfyui_runtime_prompt_submission_enabled,
                    request_payload=request_payload,
                    error=f"ComfyUI video resource admission {resource_plan.admission_status}: {resource_plan.error or '; '.join(resource_plan.blocking_reasons)}",
                    metadata={
                        **dict(metadata or {}),
                        "media_type": "video",
                        "prompt_submission_skipped": True,
                        "video_resource_plan": plan_payload,
                    },
                )
            request_payload["extra_data"] = {
                **dict(request_payload.get("extra_data") or {}),
                "aiops_video_resource_plan": resource_plan.model_dump(mode="json"),
            }
            resource_plan_payload = resource_plan.model_dump(mode="json")

        readiness_error = self._runtime_execution_error(path="/prompt", base_url=target_base_url)
        if readiness_error:
            return ComfyUIRuntimePromptJobSubmitResponse(
                success=False,
                workspace_id=workspace_id,
                provider=self._provider(),
                enabled=self.settings.comfyui_runtime_enabled,
                base_url=target_base_url,
                external_request_attempted=False,
                runtime_calls_enabled=False,
                prompt_submission_enabled=self.settings.comfyui_runtime_prompt_submission_enabled,
                request_payload=request_payload,
                error=readiness_error,
                metadata={
                    **dict(metadata or {}),
                    **({"media_type": clean_media_type, "video_resource_plan": resource_plan_payload} if resource_plan_payload else {}),
                },
            )

        if not request_payload["prompt"]:
            return ComfyUIRuntimePromptJobSubmitResponse(
                success=False,
                workspace_id=workspace_id,
                provider=self._provider(),
                enabled=self.settings.comfyui_runtime_enabled,
                base_url=target_base_url,
                external_request_attempted=False,
                runtime_calls_enabled=False,
                prompt_submission_enabled=True,
                request_payload=request_payload,
                error="ComfyUI prompt payload is empty; provide a valid workflow prompt graph before submission.",
                metadata={
                    **dict(metadata or {}),
                    **({"media_type": clean_media_type, "video_resource_plan": resource_plan_payload} if resource_plan_payload else {}),
                },
            )

        url = self._build_runtime_url(target_base_url, "/prompt")
        response = self.http_post(url, request_payload, self.settings.comfyui_runtime_timeout_seconds)
        status_code = self._status_code(response)
        payload = response.get("json")
        response_payload = payload if isinstance(payload, dict) else {}
        success = status_code is not None and 200 <= status_code < 300 and "prompt_id" in response_payload
        return ComfyUIRuntimePromptJobSubmitResponse(
            success=success,
            workspace_id=workspace_id,
            provider=self._provider(),
            enabled=self.settings.comfyui_runtime_enabled,
            base_url=target_base_url,
            external_request_attempted=True,
            runtime_calls_enabled=True,
            prompt_submission_enabled=True,
            status_code=status_code,
            prompt_id=str(response_payload.get("prompt_id")) if response_payload.get("prompt_id") is not None else None,
            number=response_payload.get("number") if isinstance(response_payload.get("number"), (int, float)) else None,
            node_errors=response_payload.get("node_errors") if isinstance(response_payload.get("node_errors"), dict) else {},
            response_payload=response_payload,
            request_payload=request_payload,
            error=None if success else str(response.get("error") or response_payload.get("error") or "ComfyUI prompt submission did not return a prompt_id."),
            metadata={
                **dict(metadata or {}),
                **({"media_type": clean_media_type, "video_resource_plan": resource_plan_payload} if resource_plan_payload else {}),
            },
        )

    def video_resource_plan(
        self,
        *,
        workspace_id: str | None = None,
        resource_profile: str = "standard",
        width: int = 1280,
        height: int = 720,
        frames: int = 96,
        fps: float = 24.0,
        duration_seconds: float | None = None,
        estimated_vram_mb: int | None = None,
        reserve_vram_mb: int | None = None,
        priority: str = "normal",
        allow_queue: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> ComfyUIRuntimeVideoResourcePlanResponse:
        """Plan whether a ComfyUI video request may submit now based on live GPU and queue state."""

        def unique(items: list[str]) -> list[str]:
            seen: set[str] = set()
            cleaned: list[str] = []
            for item in items:
                value = str(item or "").strip()
                if value and value not in seen:
                    seen.add(value)
                    cleaned.append(value)
            return cleaned

        normalized_profile = str(resource_profile or "standard").strip().lower()[:64] or "standard"
        safe_width = max(64, min(int(width or 1280), 8192))
        safe_height = max(64, min(int(height or 720), 8192))
        safe_fps = max(1.0, min(float(fps or 24.0), 240.0))
        if duration_seconds is not None:
            safe_frames = max(1, min(int(round(float(duration_seconds) * safe_fps)), 20000))
        else:
            safe_frames = max(1, min(int(frames or 96), 20000))
        clean_priority = str(priority or "normal").strip().lower()[:32] or "normal"
        estimate_mb = self._estimate_video_vram_mb(
            width=safe_width,
            height=safe_height,
            frames=safe_frames,
            profile=normalized_profile,
            explicit_estimate_mb=estimated_vram_mb,
        )
        reserve_mb = int(reserve_vram_mb if reserve_vram_mb is not None else self.settings.comfyui_video_min_free_vram_mb)
        required_free_mb = estimate_mb + max(0, reserve_mb)
        max_concurrent = self.settings.comfyui_video_max_concurrent_jobs
        pending_limit = self.settings.comfyui_video_queue_pending_limit
        endpoint_candidates = self._video_endpoint_candidates()
        endpoint_plans: list[dict[str, Any]] = []
        system_stats_attempted = False
        queue_status_attempted = False

        for endpoint in endpoint_candidates:
            endpoint_name = str(endpoint["name"])
            endpoint_base_url = str(endpoint["base_url"])
            endpoint_gpu_index = endpoint.get("gpu_index")
            endpoint_blocking_reasons: list[str] = []
            endpoint_recommended_actions: list[str] = []
            system_stats_response: Mapping[str, Any] | None = None
            endpoint_system_stats_attempted = False
            stats_error = self._read_only_system_stats_error(base_url=endpoint_base_url)
            if stats_error:
                endpoint_blocking_reasons.append(stats_error)
                endpoint_recommended_actions.append("Enable the guarded ComfyUI read-only /system_stats gate before video GPU admission.")
            else:
                endpoint_system_stats_attempted = True
                system_stats_attempted = True
                try:
                    system_stats_response = self.http_get(
                        self._build_runtime_url(endpoint_base_url, "/system_stats"),
                        self.settings.comfyui_runtime_timeout_seconds,
                    )
                except Exception as exc:
                    endpoint_blocking_reasons.append(f"ComfyUI /system_stats failed for {endpoint_name}: {exc.__class__.__name__}")
                    endpoint_recommended_actions.append("Confirm the selected ComfyUI instance is running before admitting video generation.")

            system_stats_payload = (
                system_stats_response.get("json")
                if isinstance(system_stats_response, Mapping) and isinstance(system_stats_response.get("json"), dict)
                else {}
            )
            system_stats_status = self._status_code(system_stats_response or {})
            if endpoint_system_stats_attempted and not (system_stats_status is not None and 200 <= system_stats_status < 300):
                endpoint_blocking_reasons.append(f"ComfyUI /system_stats returned HTTP {system_stats_status or 'unknown'} for {endpoint_name}.")
                endpoint_recommended_actions.append("Refresh ComfyUI diagnostics and avoid submitting video jobs until GPU stats are readable.")

            gpu_devices = self._extract_gpu_devices(system_stats_payload)
            annotated_gpu_devices: list[dict[str, Any]] = []
            for device in gpu_devices:
                annotated = {
                    **device,
                    "endpoint_name": endpoint_name,
                    "endpoint_base_url": endpoint_base_url,
                }
                annotated_gpu_devices.append(annotated)

            endpoint_gpu_devices = annotated_gpu_devices
            if isinstance(endpoint_gpu_index, int):
                endpoint_gpu_devices = [device for device in annotated_gpu_devices if int(device.get("index", -1)) == endpoint_gpu_index]
                if annotated_gpu_devices and not endpoint_gpu_devices:
                    endpoint_blocking_reasons.append(f"Configured GPU index {endpoint_gpu_index} was not found on {endpoint_name}.")
                    endpoint_recommended_actions.append("Update COMFYUI_VIDEO_GPU_ENDPOINTS so each endpoint points at the GPU index used by that ComfyUI process.")

            if not endpoint_gpu_devices:
                endpoint_blocking_reasons.append(f"No GPU device with readable VRAM statistics was found for {endpoint_name}.")
                endpoint_recommended_actions.append("Start this ComfyUI instance with CUDA/DirectML GPU support or remove it from the video endpoint pool.")
            selected_gpu = self._select_gpu(endpoint_gpu_devices, required_free_mb=required_free_mb)
            if endpoint_gpu_devices and selected_gpu is None:
                best_free = max((int(device.get("vram_free_mb") or 0) for device in endpoint_gpu_devices), default=0)
                endpoint_blocking_reasons.append(
                    f"Insufficient free VRAM on {endpoint_name}: requires {required_free_mb} MB including reserve, best GPU has {best_free} MB free."
                )
                endpoint_recommended_actions.append("Reduce resolution, frames, model profile, or wait for other GPU jobs to finish.")

            queue = self.queue_status(workspace_id=workspace_id, base_url=endpoint_base_url)
            endpoint_queue_status_attempted = bool(queue.external_request_attempted)
            queue_status_attempted = queue_status_attempted or endpoint_queue_status_attempted
            if queue.error and not queue.success:
                endpoint_blocking_reasons.append(queue.error)
                endpoint_recommended_actions.append("Enable guarded /queue access before admitting video submissions.")
            running_count = len(queue.queue_running or [])
            pending_count = len(queue.queue_pending or [])

            endpoint_status = "blocked"
            endpoint_should_submit_now = False
            if endpoint_blocking_reasons:
                endpoint_status = "blocked"
            elif running_count >= max_concurrent:
                endpoint_status = "queued" if allow_queue else "blocked"
                endpoint_recommended_actions.append("Keep the video request queued until a GPU slot is free.")
            elif pending_count > pending_limit:
                endpoint_status = "queued" if allow_queue else "blocked"
                endpoint_recommended_actions.append("Wait for the ComfyUI pending queue to drain before submitting another video job.")
            else:
                endpoint_status = "admitted"
                endpoint_should_submit_now = True
                endpoint_recommended_actions.append("Submit the video prompt now; record prompt_id and refresh history until outputs appear.")

            endpoint_plans.append(
                {
                    "name": endpoint_name,
                    "base_url": endpoint_base_url,
                    "gpu_index": endpoint_gpu_index,
                    "source": endpoint.get("source"),
                    "admission_status": endpoint_status,
                    "should_submit_now": endpoint_should_submit_now,
                    "success": endpoint_status in {"admitted", "queued"},
                    "selected_gpu": selected_gpu,
                    "gpu_devices": endpoint_gpu_devices,
                    "queue_running_count": running_count,
                    "queue_pending_count": pending_count,
                    "system_stats_attempted": endpoint_system_stats_attempted,
                    "system_stats_status_code": system_stats_status,
                    "queue_status_attempted": endpoint_queue_status_attempted,
                    "queue_success": queue.success,
                    "queue_error": queue.error,
                    "blocking_reasons": unique(endpoint_blocking_reasons),
                    "recommended_actions": unique(endpoint_recommended_actions),
                    "queue_payload": queue.response_payload,
                }
            )

        def endpoint_sort_key(plan: dict[str, Any]) -> tuple[int, int, int]:
            selected = plan.get("selected_gpu") if isinstance(plan.get("selected_gpu"), dict) else {}
            free_vram = int(selected.get("vram_free_mb") or 0)
            return (int(plan.get("queue_running_count") or 0), int(plan.get("queue_pending_count") or 0), -free_vram)

        admitted_plans = [plan for plan in endpoint_plans if plan.get("should_submit_now")]
        queued_plans = [plan for plan in endpoint_plans if plan.get("admission_status") == "queued"]
        selected_endpoint_plan: dict[str, Any] | None = None
        if admitted_plans:
            selected_endpoint_plan = sorted(admitted_plans, key=endpoint_sort_key)[0]
            admission_status = "admitted"
            should_submit_now = True
        elif queued_plans:
            selected_endpoint_plan = sorted(queued_plans, key=endpoint_sort_key)[0]
            admission_status = "queued"
            should_submit_now = False
        else:
            admission_status = "blocked"
            should_submit_now = False

        selected_endpoint = None
        selected_gpu = None
        selected_queue_payload: dict[str, Any] = {}
        running_count = 0
        pending_count = 0
        selected_system_stats_status: int | None = None
        if selected_endpoint_plan:
            selected_gpu = selected_endpoint_plan.get("selected_gpu") if isinstance(selected_endpoint_plan.get("selected_gpu"), dict) else None
            selected_endpoint = {
                "name": selected_endpoint_plan.get("name"),
                "base_url": selected_endpoint_plan.get("base_url"),
                "gpu_index": selected_endpoint_plan.get("gpu_index"),
                "admission_status": selected_endpoint_plan.get("admission_status"),
                "queue_running_count": selected_endpoint_plan.get("queue_running_count"),
                "queue_pending_count": selected_endpoint_plan.get("queue_pending_count"),
                "selected_gpu": selected_gpu,
            }
            selected_queue_payload = selected_endpoint_plan.get("queue_payload") if isinstance(selected_endpoint_plan.get("queue_payload"), dict) else {}
            running_count = int(selected_endpoint_plan.get("queue_running_count") or 0)
            pending_count = int(selected_endpoint_plan.get("queue_pending_count") or 0)
            selected_system_stats_status = (
                selected_endpoint_plan.get("system_stats_status_code")
                if isinstance(selected_endpoint_plan.get("system_stats_status_code"), int)
                else None
            )

        if admission_status == "blocked":
            blocking_reasons = unique(
                [
                    reason
                    for plan in endpoint_plans
                    for reason in plan.get("blocking_reasons", [])
                    if isinstance(reason, str)
                ]
            )
            recommended_actions = unique(
                [
                    action
                    for plan in endpoint_plans
                    for action in plan.get("recommended_actions", [])
                    if isinstance(action, str)
                ]
            )
        else:
            blocking_reasons = []
            recommended_actions = unique(
                [
                    action
                    for action in (selected_endpoint_plan or {}).get("recommended_actions", [])
                    if isinstance(action, str)
                ]
            )

        gpu_devices = [
            device
            for plan in endpoint_plans
            for device in plan.get("gpu_devices", [])
            if isinstance(device, dict)
        ]
        response_base_url = str((selected_endpoint or {}).get("base_url") or self.settings.comfyui_runtime_base_url)
        error = "; ".join(blocking_reasons) if blocking_reasons else None
        return ComfyUIRuntimeVideoResourcePlanResponse(
            success=admission_status in {"admitted", "queued"},
            workspace_id=workspace_id,
            provider=self._provider(),
            base_url=response_base_url,
            resource_profile=normalized_profile,
            width=safe_width,
            height=safe_height,
            frames=safe_frames,
            fps=safe_fps,
            duration_seconds=duration_seconds,
            estimated_vram_mb=estimate_mb,
            reserve_vram_mb=reserve_mb,
            required_free_vram_mb=required_free_mb,
            max_concurrent_video_jobs=max_concurrent,
            queue_pending_limit=pending_limit,
            admission_status=admission_status,
            should_submit_now=should_submit_now,
            external_request_attempted=system_stats_attempted or queue_status_attempted,
            system_stats_attempted=system_stats_attempted,
            queue_status_attempted=queue_status_attempted,
            runtime_calls_enabled=should_submit_now,
            prompt_submission_enabled=self.settings.comfyui_runtime_prompt_submission_enabled,
            selected_endpoint=selected_endpoint,
            endpoint_plans=endpoint_plans,
            selected_gpu=selected_gpu,
            gpu_devices=gpu_devices,
            queue_running_count=running_count,
            queue_pending_count=pending_count,
            blocking_reasons=blocking_reasons,
            recommended_actions=recommended_actions,
            queue_payload=selected_queue_payload,
            raw={
                "phase": "66A",
                "priority": clean_priority,
                "allow_queue": allow_queue,
                "metadata": dict(metadata or {}),
                "endpoint_pool_configured": bool(str(self.settings.comfyui_video_gpu_endpoints or "").strip()),
                "endpoint_count": len(endpoint_candidates),
                "system_stats_status_code": selected_system_stats_status,
                "selected_endpoint_name": (selected_endpoint or {}).get("name"),
            },
            error=error,
        )

    def prompt_history(
        self,
        *,
        prompt_id: str,
        workspace_id: str | None = None,
        base_url: str | None = None,
    ) -> ComfyUIRuntimePromptHistoryResponse:
        """Read one guarded real ComfyUI prompt history response."""

        safe_prompt_id = self._sanitize_prompt_id(prompt_id)
        path = f"/history/{safe_prompt_id}"
        runtime_base_url = base_url or self.settings.comfyui_runtime_base_url
        readiness_error = self._runtime_execution_error(path=path, base_url=runtime_base_url)
        if readiness_error:
            return ComfyUIRuntimePromptHistoryResponse(
                success=False,
                workspace_id=workspace_id,
                provider=self._provider(),
                base_url=runtime_base_url,
                path=path,
                prompt_id=safe_prompt_id,
                external_request_attempted=False,
                runtime_calls_enabled=False,
                prompt_submission_enabled=self.settings.comfyui_runtime_prompt_submission_enabled,
                error=readiness_error,
            )

        response = self.http_get(self._build_runtime_url(runtime_base_url, path), self.settings.comfyui_runtime_timeout_seconds)
        status_code = self._status_code(response)
        payload = response.get("json")
        response_payload = payload if isinstance(payload, dict) else {}
        history_item = response_payload.get(safe_prompt_id) if isinstance(response_payload.get(safe_prompt_id), dict) else {}
        outputs = history_item.get("outputs") if isinstance(history_item.get("outputs"), dict) else {}
        success = status_code is not None and 200 <= status_code < 300
        return ComfyUIRuntimePromptHistoryResponse(
            success=success,
            workspace_id=workspace_id,
            provider=self._provider(),
            base_url=runtime_base_url,
            path=path,
            prompt_id=safe_prompt_id,
            external_request_attempted=True,
            runtime_calls_enabled=True,
            prompt_submission_enabled=True,
            status_code=status_code,
            response_payload=response_payload,
            outputs=outputs,
            error=None if success else str(response.get("error") or "ComfyUI prompt history read failed."),
        )

    def queue_status(self, *, workspace_id: str | None = None, base_url: str | None = None) -> ComfyUIRuntimeQueueResponse:
        """Read guarded real ComfyUI queue status."""

        runtime_base_url = base_url or self.settings.comfyui_runtime_base_url
        readiness_error = self._runtime_execution_error(path="/queue", base_url=runtime_base_url)
        if readiness_error:
            return ComfyUIRuntimeQueueResponse(
                success=False,
                workspace_id=workspace_id,
                provider=self._provider(),
                base_url=runtime_base_url,
                external_request_attempted=False,
                runtime_calls_enabled=False,
                prompt_submission_enabled=self.settings.comfyui_runtime_prompt_submission_enabled,
                error=readiness_error,
            )

        response = self.http_get(self._build_runtime_url(runtime_base_url, "/queue"), self.settings.comfyui_runtime_timeout_seconds)
        status_code = self._status_code(response)
        payload = response.get("json")
        response_payload = payload if isinstance(payload, dict) else {}
        running = response_payload.get("queue_running") if isinstance(response_payload.get("queue_running"), list) else []
        pending = response_payload.get("queue_pending") if isinstance(response_payload.get("queue_pending"), list) else []
        success = status_code is not None and 200 <= status_code < 300
        return ComfyUIRuntimeQueueResponse(
            success=success,
            workspace_id=workspace_id,
            provider=self._provider(),
            base_url=runtime_base_url,
            external_request_attempted=True,
            runtime_calls_enabled=True,
            prompt_submission_enabled=True,
            status_code=status_code,
            response_payload=response_payload,
            queue_running=running,
            queue_pending=pending,
            error=None if success else str(response.get("error") or "ComfyUI queue status read failed."),
        )

    async def _get_video_job_model(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
    ) -> ComfyUIRuntimeVideoJob:
        result = await session.execute(
            select(ComfyUIRuntimeVideoJob).where(
                ComfyUIRuntimeVideoJob.workspace_id == workspace_id,
                ComfyUIRuntimeVideoJob.id == job_id,
            )
        )
        job = result.scalar_one_or_none()
        if job is None:
            raise LookupError("ComfyUI video job not found")
        return job

    def _normalize_video_job_request(
        self,
        *,
        resource_profile: str,
        width: int | None,
        height: int | None,
        frames: int | None,
        fps: float | None,
        duration_seconds: float | None,
        estimated_vram_mb: int | None,
        reserve_vram_mb: int | None,
    ) -> dict[str, Any]:
        safe_fps = max(1.0, min(float(fps or 24.0), 240.0))
        if duration_seconds is not None:
            safe_frames = max(1, min(int(round(float(duration_seconds) * safe_fps)), 20000))
        else:
            safe_frames = max(1, min(int(frames or 96), 20000))
        return {
            "resource_profile": str(resource_profile or "standard").strip().lower()[:64] or "standard",
            "width": max(64, min(int(width or 1280), 8192)),
            "height": max(64, min(int(height or 720), 8192)),
            "frames": safe_frames,
            "fps": safe_fps,
            "duration_seconds": duration_seconds,
            "estimated_vram_mb": estimated_vram_mb,
            "reserve_vram_mb": reserve_vram_mb,
        }

    def _poll_video_job_runtime(
        self,
        *,
        workspace_id: str,
        prompt_id: str,
        base_url: str | None,
    ) -> tuple[ComfyUIRuntimePromptHistoryResponse, ComfyUIRuntimeQueueResponse]:
        history = self.prompt_history(workspace_id=workspace_id, prompt_id=prompt_id, base_url=base_url)
        queue = self.queue_status(workspace_id=workspace_id, base_url=base_url)
        return history, queue

    def _video_resource_plan_from_submit(
        self,
        submit: ComfyUIRuntimePromptJobSubmitResponse | None,
    ) -> dict[str, Any]:
        if submit is None:
            return {}
        plan = submit.metadata.get("video_resource_plan") if isinstance(submit.metadata, dict) else None
        if isinstance(plan, dict):
            return plan
        extra_data = submit.request_payload.get("extra_data") if isinstance(submit.request_payload, dict) else None
        if isinstance(extra_data, dict) and isinstance(extra_data.get("aiops_video_resource_plan"), dict):
            return dict(extra_data["aiops_video_resource_plan"])
        return {}

    def _selected_endpoint_from_resource_plan(self, resource_plan: Mapping[str, Any] | None) -> dict[str, Any]:
        selected = (resource_plan or {}).get("selected_endpoint") if isinstance(resource_plan, Mapping) else None
        return dict(selected) if isinstance(selected, Mapping) else {}

    def _selected_gpu_from_resource_plan(self, resource_plan: Mapping[str, Any] | None) -> dict[str, Any]:
        selected = (resource_plan or {}).get("selected_gpu") if isinstance(resource_plan, Mapping) else None
        return dict(selected) if isinstance(selected, Mapping) else {}

    def _queue_payload_from_resource_plan(self, resource_plan: Mapping[str, Any] | None) -> dict[str, Any]:
        if not isinstance(resource_plan, Mapping):
            return {}
        queue_payload = resource_plan.get("queue_payload")
        if isinstance(queue_payload, Mapping):
            return dict(queue_payload)
        endpoint_plans = resource_plan.get("endpoint_plans")
        if isinstance(endpoint_plans, list):
            for endpoint_plan in endpoint_plans:
                if isinstance(endpoint_plan, Mapping) and isinstance(endpoint_plan.get("queue_payload"), Mapping):
                    return dict(endpoint_plan["queue_payload"])
        return {}

    def _video_job_status_from_runtime(
        self,
        *,
        submit: ComfyUIRuntimePromptJobSubmitResponse | None,
        resource_plan: Mapping[str, Any] | None,
        outputs: list[dict[str, Any]],
        current_status: str | None = None,
        has_prompt_id: bool = False,
    ) -> str:
        if outputs:
            return "output_ready"
        if submit is not None:
            if submit.success:
                return "submitted"
            admission_status = str((resource_plan or {}).get("admission_status") or "").strip().lower()
            if admission_status == "queued":
                return "queued"
            if admission_status == "blocked":
                return "resource_blocked"
            return "failed"
        admission_status = str((resource_plan or {}).get("admission_status") or "").strip().lower()
        if admission_status == "queued":
            return "queued"
        if admission_status == "blocked":
            return "resource_blocked"
        if admission_status == "admitted":
            return "ready_to_submit"
        if has_prompt_id:
            return current_status if current_status == "output_ready" else "submitted"
        return current_status if current_status in COMFYUI_RUNTIME_VIDEO_JOB_STATUSES else "draft"

    def _video_job_failure_reason(
        self,
        *,
        submit: ComfyUIRuntimePromptJobSubmitResponse | None,
        history: ComfyUIRuntimePromptHistoryResponse | None,
        queue: ComfyUIRuntimeQueueResponse | None,
        status: str,
    ) -> str | None:
        if submit and submit.error:
            return submit.error
        if status in {"submitted", "output_ready"}:
            if history and history.error:
                return history.error
            if queue and queue.error:
                return queue.error
        if status == "failed":
            return "ComfyUI video job failed without a runtime prompt_id."
        return None

    def _video_job_result_summary(
        self,
        *,
        status: str,
        prompt_id: str | None,
        outputs: list[dict[str, Any]],
    ) -> str:
        if outputs:
            return f"ComfyUI video job {prompt_id or 'unknown'} produced {len(outputs)} output file(s)."
        if status == "submitted":
            return f"ComfyUI video job {prompt_id or 'unknown'} submitted; refresh history until outputs appear."
        if status == "queued":
            return "ComfyUI video job is waiting for an admitted GPU/queue slot."
        if status == "ready_to_submit":
            return "ComfyUI video job has an admitted GPU/queue plan and is waiting for operator-approved prompt submission."
        if status == "resource_blocked":
            return "ComfyUI video job is blocked by GPU, queue, or guarded runtime admission."
        if status == "failed":
            return "ComfyUI video job failed before output was available."
        return "ComfyUI video job has been recorded."

    def _extract_prompt_output_files(self, outputs: Mapping[str, Any] | None) -> list[dict[str, Any]]:
        if not isinstance(outputs, Mapping):
            return []
        extracted: list[dict[str, Any]] = []
        for node_id, node_outputs in outputs.items():
            if not isinstance(node_outputs, Mapping):
                continue
            for kind, value in node_outputs.items():
                values = value if isinstance(value, list) else [value]
                for item in values:
                    if isinstance(item, Mapping) and item.get("filename") is not None:
                        extracted.append(
                            {
                                "node_id": str(node_id),
                                "kind": str(kind),
                                "filename": str(item.get("filename")),
                                "subfolder": str(item.get("subfolder") or ""),
                                "type": str(item.get("type") or ""),
                            }
                        )
                    elif isinstance(item, str) and item:
                        extracted.append(
                            {
                                "node_id": str(node_id),
                                "kind": str(kind),
                                "filename": item,
                                "subfolder": "",
                                "type": "",
                            }
                        )
        return extracted

    def _recommended_config_changes(
        self,
        runbook: ComfyUIRuntimeMaintenanceRunbookResponse,
    ) -> list[dict[str, Any]]:
        changes: list[dict[str, Any]] = []
        env_targets = {
            "provider_guarded": ("COMFYUI_RUNTIME_PROVIDER", "guarded"),
            "runtime_enabled": ("COMFYUI_RUNTIME_ENABLED", "true"),
            "network_gate": ("COMFYUI_RUNTIME_ALLOW_NETWORK", "true"),
            "base_url_scheme": ("COMFYUI_RUNTIME_BASE_URL", "http://127.0.0.1:8188"),
            "base_url_host_allowlist": ("COMFYUI_RUNTIME_ALLOWED_HOSTS", runbook.configuration_summary.get("parsed_host")),
            "read_only_probe_gate": ("COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED", "true"),
            "health_path_allowlist": ("COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS", runbook.configuration_summary.get("health_path")),
        }
        for step in runbook.steps:
            if not step.blocking:
                continue
            target_env, suggested_value = env_targets.get(step.source_check or "", (None, None))
            changes.append(
                {
                    "key": step.key,
                    "source_check": step.source_check,
                    "title": step.title,
                    "status": "requested",
                    "target_env": target_env,
                    "suggested_value": suggested_value,
                    "action": step.action,
                    "requires_api_restart": True,
                    "config_mutation_performed": False,
                }
            )
        if not changes:
            changes.append(
                {
                    "key": "save_snapshot_and_probe",
                    "source_check": "read_only_probe_ready",
                    "title": "Ready for guarded read-only probe",
                    "status": "requested",
                    "target_env": None,
                    "suggested_value": None,
                    "action": runbook.next_operator_action,
                    "requires_api_restart": False,
                    "config_mutation_performed": False,
                }
            )
        return changes

    @staticmethod
    def _manual_apply_steps_from_request(
        request: ComfyUIRuntimeConfigChangeRequest,
    ) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for item in request.requested_changes or []:
            steps.append(
                {
                    "key": item.get("key"),
                    "source_check": item.get("source_check"),
                    "title": item.get("title"),
                    "status": "operator_reported",
                    "target_env": item.get("target_env"),
                    "suggested_value": item.get("suggested_value"),
                    "requires_api_restart": item.get("requires_api_restart", True),
                    "api_config_mutation_performed": False,
                }
            )
        if not steps:
            steps.append(
                {
                    "key": "manual_apply_review",
                    "source_check": None,
                    "title": "Manual apply evidence review",
                    "status": "operator_reported",
                    "target_env": None,
                    "suggested_value": None,
                    "requires_api_restart": False,
                    "api_config_mutation_performed": False,
                }
            )
        return steps

    @staticmethod
    def _post_manual_readiness_comparison(
        evidence: ComfyUIRuntimeManualApplyEvidence,
        diagnostics: ComfyUIRuntimeDiagnosticsResponse,
    ) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        blocking_reasons: list[str] = []
        recommended_actions: list[str] = []

        def add_check(
            *,
            key: str,
            passed: bool,
            detail: str,
            current_value: Any,
            expected_value: Any,
            remediation: str | None = None,
            required: bool = True,
        ) -> None:
            status = "pass" if passed else "blocked" if required else "warning"
            checks.append(
                {
                    "key": key,
                    "status": status,
                    "detail": detail,
                    "current_value": current_value,
                    "expected_value": expected_value,
                    "remediation": remediation,
                    "required": required,
                }
            )
            if required and not passed:
                blocking_reasons.append(f"{key}: {detail}")
                if remediation and remediation not in recommended_actions:
                    recommended_actions.append(remediation)

        add_check(
            key="manual_evidence_verified",
            passed=evidence.evidence_status == "verified",
            detail="Manual apply evidence must be verified before any post-manual readiness decision.",
            current_value=evidence.evidence_status,
            expected_value="verified",
            remediation="Verify the manual apply evidence after maintainer review.",
        )
        add_check(
            key="manual_config_applied",
            passed=evidence.manual_config_applied,
            detail="The maintainer must explicitly report that the approved configuration was applied.",
            current_value=evidence.manual_config_applied,
            expected_value=True,
            remediation="Record manual apply evidence after the approved configuration has been applied outside the app.",
        )
        add_check(
            key="service_restart_reported",
            passed=evidence.service_restart_reported,
            detail="Service restart evidence should be recorded before post-manual readiness approval.",
            current_value=evidence.service_restart_reported,
            expected_value=True,
            remediation="Attach restart evidence or record why restart was not required.",
        )
        add_check(
            key="api_config_mutation_performed",
            passed=not evidence.api_config_mutation_performed,
            detail="The API must not mutate runtime configuration during manual apply evidence or readiness comparison.",
            current_value=evidence.api_config_mutation_performed,
            expected_value=False,
            remediation="Recreate evidence only through metadata-only routes.",
        )
        add_check(
            key="external_request_attempted",
            passed=not diagnostics.external_request_attempted,
            detail="Current diagnostics must remain no-network before any guarded health probe.",
            current_value=diagnostics.external_request_attempted,
            expected_value=False,
            remediation="Use diagnostics/readiness comparison only until guarded probe approval.",
        )
        add_check(
            key="runtime_calls_enabled",
            passed=not diagnostics.runtime_calls_enabled,
            detail="Runtime calls must remain disabled during post-manual readiness comparison.",
            current_value=diagnostics.runtime_calls_enabled,
            expected_value=False,
            remediation="Keep ComfyUI runtime calls disabled until a later guarded adapter phase.",
        )
        add_check(
            key="health_probe_executed",
            passed=True,
            detail="No ComfyUI health probe is executed by this readiness comparison.",
            current_value=False,
            expected_value=False,
            remediation=None,
            required=False,
        )
        add_check(
            key="read_only_probe_ready_current",
            passed=diagnostics.read_only_probe_ready,
            detail="Current no-network diagnostics must show all guarded read-only probe gates ready.",
            current_value=diagnostics.read_only_probe_ready,
            expected_value=True,
            remediation="Complete the remaining ComfyUI runtime provider, switch, network, host, and path gates, then save a new readiness comparison.",
        )

        for action in diagnostics.recommended_actions:
            if action not in recommended_actions:
                recommended_actions.append(action)

        guarded_probe_ready = all(check["status"] == "pass" for check in checks if check["required"])
        comparison_status = "ready_for_guarded_read_only_probe" if guarded_probe_ready else "blocked"
        if guarded_probe_ready:
            next_operator_action = "Ready for a separate guarded read-only health probe approval; this comparison still did not call ComfyUI."
        else:
            next_operator_action = recommended_actions[0] if recommended_actions else "Review blocked readiness checks before any guarded probe."

        return {
            "phase": "62H",
            "comparison_status": comparison_status,
            "guarded_probe_ready": guarded_probe_ready,
            "checks": checks,
            "blocking_reasons": blocking_reasons,
            "recommended_actions": recommended_actions,
            "next_operator_action": next_operator_action,
            "readiness_delta": {
                "before": evidence.readiness_status_before,
                "after_evidence": evidence.readiness_status_after,
                "current": diagnostics.readiness_status,
                "read_only_probe_ready_before": evidence.read_only_probe_ready_before,
                "read_only_probe_ready_after_evidence": evidence.read_only_probe_ready_after,
                "read_only_probe_ready_current": diagnostics.read_only_probe_ready,
            },
            "no_network_call_performed": True,
            "health_probe_executed": False,
            "api_config_mutation_performed": False,
            "external_request_attempted": False,
            "runtime_calls_enabled": False,
        }

    @staticmethod
    def _configuration_summary_from_diagnostics(
        diagnostics: ComfyUIRuntimeDiagnosticsResponse,
    ) -> dict[str, Any]:
        return {
            "provider": diagnostics.provider,
            "enabled": diagnostics.enabled,
            "network_allowed": diagnostics.network_allowed,
            "read_only_probe_enabled": diagnostics.read_only_probe_enabled,
            "base_url": diagnostics.base_url,
            "parsed_host": diagnostics.parsed_host,
            "host_allowed": diagnostics.host_allowed,
            "health_path": diagnostics.health_path,
            "health_path_allowed": diagnostics.health_path_allowed,
            "allowed_hosts": diagnostics.allowed_hosts,
            "allowed_health_paths": diagnostics.allowed_health_paths,
        }

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

    def _disabled_actions(
        self,
        *,
        read_only_probe_ready: bool,
        prompt_submission_ready: bool = False,
    ) -> list[str]:
        actions = list(DISABLED_COMFYUI_RUNTIME_ACTIONS)
        if not read_only_probe_ready:
            actions.insert(1, COMFYUI_RUNTIME_READ_ONLY_ACTION)
        if prompt_submission_ready:
            actions = [
                action
                for action in actions
                if action
                not in {
                    "call_comfyui_queue",
                    "submit_prompt",
                    "submit_queue_job",
                    "read_history",
                    "generate_media",
                }
            ]
        return actions

    def _video_endpoint_candidates(self) -> list[dict[str, Any]]:
        raw_pool = str(self.settings.comfyui_video_gpu_endpoints or "").strip()
        if not raw_pool:
            return [
                {
                    "name": "default",
                    "base_url": self.settings.comfyui_runtime_base_url,
                    "gpu_index": None,
                    "source": "COMFYUI_RUNTIME_BASE_URL",
                }
            ]

        endpoints: list[dict[str, Any]] = []
        for index, raw_item in enumerate(raw_pool.split(";")):
            item = raw_item.strip()
            if not item:
                continue
            parts = [part.strip() for part in item.split("|")]
            name = f"video-gpu-{index}"
            base_url = ""
            gpu_index: int | None = None
            if len(parts) == 1:
                base_url = parts[0]
            elif parts[0].startswith(("http://", "https://")):
                base_url = parts[0]
                try:
                    gpu_index = int(parts[1]) if len(parts) > 1 and parts[1] != "" else None
                except ValueError:
                    gpu_index = None
            else:
                name = parts[0] or name
                base_url = parts[1] if len(parts) > 1 else ""
                try:
                    gpu_index = int(parts[2]) if len(parts) > 2 and parts[2] != "" else None
                except ValueError:
                    gpu_index = None
            if not base_url:
                continue
            endpoints.append(
                {
                    "name": name[:80],
                    "base_url": base_url.rstrip("/"),
                    "gpu_index": gpu_index,
                    "source": "COMFYUI_VIDEO_GPU_ENDPOINTS",
                }
            )
        if endpoints:
            return endpoints
        return [
            {
                "name": "default",
                "base_url": self.settings.comfyui_runtime_base_url,
                "gpu_index": None,
                "source": "COMFYUI_RUNTIME_BASE_URL",
            }
        ]

    def _runtime_execution_error(self, *, path: str, base_url: str | None = None) -> str | None:
        provider = self._provider()
        runtime_base_url = base_url or self.settings.comfyui_runtime_base_url
        parsed = urlparse(runtime_base_url)
        host = (parsed.hostname or "").lower()
        normalized_path = self._normalize_path(path)
        if provider != "guarded":
            return "ComfyUI runtime provider is disabled; set COMFYUI_RUNTIME_PROVIDER=guarded before real prompt submission."
        if not self.settings.comfyui_runtime_enabled:
            return "ComfyUI runtime is disabled by COMFYUI_RUNTIME_ENABLED=false."
        if not self.settings.comfyui_runtime_allow_network:
            return "ComfyUI runtime network access is disabled by COMFYUI_RUNTIME_ALLOW_NETWORK=false."
        if not self.settings.comfyui_runtime_read_only_probe_enabled:
            return "ComfyUI read-only probe gate is disabled by COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=false."
        health_path = self._normalize_path(self.settings.comfyui_runtime_health_path)
        if health_path not in self.settings.comfyui_runtime_allowed_health_path_set:
            return "ComfyUI read-only health path is not in COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS."
        if parsed.scheme not in {"http", "https"}:
            return "ComfyUI runtime base URL must use http or https."
        if not host or host not in self.settings.comfyui_runtime_allowed_host_set:
            return "ComfyUI runtime base URL host is not in COMFYUI_RUNTIME_ALLOWED_HOSTS."
        if not self.settings.comfyui_runtime_prompt_submission_enabled:
            return "ComfyUI prompt submission is disabled by COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=false."
        if not self._path_is_allowed(normalized_path, self.settings.comfyui_runtime_allowed_execution_path_set):
            return "ComfyUI runtime execution path is not in COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS."
        return None

    def _read_only_system_stats_error(self, *, base_url: str | None = None) -> str | None:
        provider = self._provider()
        runtime_base_url = base_url or self.settings.comfyui_runtime_base_url
        parsed = urlparse(runtime_base_url)
        host = (parsed.hostname or "").lower()
        if provider != "guarded":
            return "ComfyUI runtime provider is disabled; set COMFYUI_RUNTIME_PROVIDER=guarded before video GPU admission."
        if not self.settings.comfyui_runtime_enabled:
            return "ComfyUI runtime is disabled by COMFYUI_RUNTIME_ENABLED=false."
        if not self.settings.comfyui_runtime_allow_network:
            return "ComfyUI runtime network access is disabled by COMFYUI_RUNTIME_ALLOW_NETWORK=false."
        if parsed.scheme not in {"http", "https"}:
            return "ComfyUI runtime base URL must use http or https."
        if not host or host not in self.settings.comfyui_runtime_allowed_host_set:
            return "ComfyUI runtime base URL host is not in COMFYUI_RUNTIME_ALLOWED_HOSTS."
        if not self.settings.comfyui_runtime_read_only_probe_enabled:
            return "ComfyUI read-only probe gate is disabled by COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=false."
        if "/system_stats" not in self.settings.comfyui_runtime_allowed_health_path_set:
            return "ComfyUI /system_stats is not in COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS."
        return None

    def _provider(self) -> str:
        return self.settings.comfyui_runtime_provider.strip().lower() or "disabled"

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
    def _build_runtime_url(base_url: str, path: str) -> str:
        return ComfyUIRuntimeService._build_probe_url(base_url, path)

    @staticmethod
    def _path_is_allowed(path: str, allowed_paths: set[str]) -> bool:
        for allowed in allowed_paths:
            if path == allowed or path.startswith(f"{allowed.rstrip('/')}/"):
                return True
        return False

    @staticmethod
    def _sanitize_prompt_id(prompt_id: str) -> str:
        value = prompt_id.strip()
        if not value or any(token in value for token in ("/", "\\", "?", "#", "&")) or ".." in value:
            raise ValueError("Invalid ComfyUI prompt_id.")
        return value

    def _dimension_from_prompt(self, prompt: Mapping[str, Any], key: str, default: int) -> int:
        for node in (prompt or {}).values():
            if not isinstance(node, Mapping):
                continue
            inputs = node.get("inputs")
            if not isinstance(inputs, Mapping):
                continue
            value = inputs.get(key)
            if isinstance(value, (int, float)) and value > 0:
                return max(64, min(int(value), 8192))
        return default

    def _frames_from_prompt(
        self,
        prompt: Mapping[str, Any],
        *,
        duration_seconds: float | None = None,
        fps: float = 24.0,
    ) -> int:
        for node in (prompt or {}).values():
            if not isinstance(node, Mapping):
                continue
            inputs = node.get("inputs")
            if not isinstance(inputs, Mapping):
                continue
            for key in ("frames", "frame_count", "num_frames", "length"):
                value = inputs.get(key)
                if isinstance(value, (int, float)) and value > 0:
                    return max(1, min(int(value), 20000))
        if duration_seconds is not None:
            return max(1, min(int(ceil(float(duration_seconds) * float(fps or 24.0))), 20000))
        return 96

    def _estimate_video_vram_mb(
        self,
        *,
        width: int,
        height: int,
        frames: int,
        profile: str,
        explicit_estimate_mb: int | None = None,
    ) -> int:
        if explicit_estimate_mb is not None:
            return max(256, min(int(explicit_estimate_mb), 131072))
        normalized = str(profile or "standard").strip().lower()
        profile_floor = {
            "preview": 4096,
            "low": 6144,
            "standard": self.settings.comfyui_video_default_vram_estimate_mb,
            "high": 12288,
            "sdxl_video": 12288,
            "animatediff": 12288,
            "wan_2_1": 16384,
            "wan": 16384,
            "wan_14b": 24576,
        }.get(normalized, self.settings.comfyui_video_default_vram_estimate_mb)
        megapixel_frames = (max(width, 64) * max(height, 64) * max(frames, 1)) / 1_000_000
        dynamic_mb = int(ceil(megapixel_frames * 64))
        return max(self.settings.comfyui_video_default_vram_estimate_mb, profile_floor + dynamic_mb)

    def _extract_gpu_devices(self, system_stats_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
        devices = system_stats_payload.get("devices") if isinstance(system_stats_payload, Mapping) else None
        if not isinstance(devices, list):
            return []
        gpu_devices: list[dict[str, Any]] = []
        for index, raw_device in enumerate(devices):
            if not isinstance(raw_device, Mapping):
                continue
            name = str(raw_device.get("name") or raw_device.get("device_name") or f"gpu-{index}")
            device_type = str(raw_device.get("type") or raw_device.get("device_type") or "gpu")
            total_mb = self._runtime_bytes_to_mb(
                raw_device.get("vram_total")
                or raw_device.get("total_vram")
                or raw_device.get("torch_vram_total")
                or raw_device.get("total_memory")
            )
            free_candidates = [
                self._runtime_bytes_to_mb(raw_device.get("vram_free")),
                self._runtime_bytes_to_mb(raw_device.get("free_vram")),
                self._runtime_bytes_to_mb(raw_device.get("torch_vram_free")),
                self._runtime_bytes_to_mb(raw_device.get("free_memory")),
            ]
            free_mb = max((value for value in free_candidates if value is not None), default=None)
            used_mb = self._runtime_bytes_to_mb(raw_device.get("vram_used") or raw_device.get("torch_vram_used") or raw_device.get("used_memory"))
            if free_mb is None and total_mb is not None and used_mb is not None:
                free_mb = max(0, total_mb - used_mb)
            if free_mb is None:
                continue
            gpu_devices.append(
                {
                    "index": int(raw_device.get("index") if isinstance(raw_device.get("index"), int) else index),
                    "name": name,
                    "type": device_type,
                    "vram_total_mb": total_mb,
                    "vram_free_mb": free_mb,
                    "vram_used_mb": used_mb,
                }
            )
        return gpu_devices

    @staticmethod
    def _runtime_bytes_to_mb(value: Any) -> int | None:
        if not isinstance(value, (int, float)):
            return None
        if value < 0:
            return None
        if value > 1_000_000:
            return int(value // (1024 * 1024))
        return int(value)

    @staticmethod
    def _select_gpu(
        gpu_devices: list[dict[str, Any]],
        *,
        required_free_mb: int,
    ) -> dict[str, Any] | None:
        eligible = [
            device
            for device in gpu_devices
            if int(device.get("vram_free_mb") or 0) >= required_free_mb
        ]
        if not eligible:
            return None
        return max(eligible, key=lambda device: int(device.get("vram_free_mb") or 0))

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
    def _default_http_post_json(url: str, payload: Mapping[str, Any], timeout_seconds: float) -> Mapping[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=body,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                response_body = response.read(65536)
                text = response_body.decode("utf-8", errors="replace")
                return {
                    "status_code": int(getattr(response, "status", response.getcode())),
                    "json": ComfyUIRuntimeService._parse_json(text),
                    "text": text[:2048],
                }
        except HTTPError as exc:
            response_body = exc.read(65536)
            text = response_body.decode("utf-8", errors="replace")
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
