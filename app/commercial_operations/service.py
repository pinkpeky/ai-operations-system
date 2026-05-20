"""Commercial operation service layer."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commercial_operation import (
    CommercialOperation,
    CommercialOperationApproval,
    CommercialOperationAssetRequest,
    CommercialOperationComfyUIHandoff,
    CommercialOperationContentDraft,
    CommercialOperationDeliverable,
    CommercialOperationDryRun,
    CommercialOperationEvidenceSnapshot,
    CommercialOperationExecutionRequest,
    CommercialOperationExecutionRun,
    CommercialOperationLink,
    CommercialOperationMonitoringObservation,
    CommercialOperationOptimizationDecision,
    CommercialOperationResult,
)
from app.models.enums import (
    CommercialOperationApprovalStatus,
    CommercialOperationAssetRequestStatus,
    CommercialOperationComfyUIHandoffStatus,
    CommercialOperationContentDraftStatus,
    CommercialOperationDeliverableStatus,
    CommercialOperationDryRunStatus,
    CommercialOperationEvidenceSnapshotStatus,
    CommercialOperationExecutionRequestStatus,
    CommercialOperationExecutionRunStatus,
    CommercialOperationMonitoringObservationStatus,
    CommercialOperationOptimizationDecisionStatus,
    CommercialOperationResultStatus,
    CommercialOperationStatus,
    OutputArtifactSourceType,
    OutputArtifactStage,
    OutputArtifactType,
)
from app.services.output_artifact_service import OutputArtifactService


class CommercialOperationService:
    """Workspace-scoped commercial automation project service."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_operation(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        title: str,
        objective: str,
        target_audience: str | None = None,
        channels: list[str] | None = None,
        status: str = CommercialOperationStatus.DRAFT.value,
        priority: str = "normal",
        risk_level: str = "medium",
        budget_amount: Decimal | None = None,
        budget_currency: str = "CNY",
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        knowledge_collection: str | None = None,
        success_metrics: list[str] | None = None,
        constraints: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperation:
        self._validate_date_range(start_at=start_at, end_at=end_at)
        clean_title = self._clean_required_text(title, "title")
        clean_objective = self._clean_required_text(objective, "objective")
        clean_channels = self._clean_list(channels)
        clean_metrics = self._clean_list(success_metrics)
        clean_constraints = self._clean_list(constraints)
        operation = CommercialOperation(
            workspace_id=workspace_id,
            user_id=user_id,
            title=clean_title,
            objective=clean_objective,
            target_audience=target_audience.strip() if target_audience else None,
            channels=clean_channels,
            status=status,
            priority=priority,
            risk_level=risk_level,
            budget_amount=budget_amount,
            budget_currency=budget_currency.strip() or "CNY",
            start_at=start_at,
            end_at=end_at,
            knowledge_collection=knowledge_collection.strip() if knowledge_collection else None,
            success_metrics=clean_metrics,
            constraints=clean_constraints,
            operation_metadata=metadata or {},
        )
        operation.plan_outline = self.build_plan_outline(operation)
        self.session.add(operation)
        await self.session.commit()
        await self.session.refresh(operation)
        return operation

    async def list_operations(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[CommercialOperation]:
        statement = select(CommercialOperation).where(CommercialOperation.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(CommercialOperation.status == status)
        result = await self.session.execute(statement.order_by(CommercialOperation.updated_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_operation(self, *, workspace_id: str, operation_id: UUID) -> CommercialOperation | None:
        result = await self.session.execute(
            select(CommercialOperation).where(
                CommercialOperation.workspace_id == workspace_id,
                CommercialOperation.id == operation_id,
            )
        )
        return result.scalar_one_or_none()

    async def require_operation(self, *, workspace_id: str, operation_id: UUID) -> CommercialOperation:
        operation = await self.get_operation(workspace_id=workspace_id, operation_id=operation_id)
        if operation is None:
            raise ValueError("Commercial operation not found in workspace")
        return operation

    async def update_operation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        patch: dict[str, Any],
    ) -> CommercialOperation:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        start_at = patch.get("start_at", operation.start_at)
        end_at = patch.get("end_at", operation.end_at)
        self._validate_date_range(start_at=start_at, end_at=end_at)
        scalar_fields = {
            "title",
            "objective",
            "target_audience",
            "status",
            "priority",
            "risk_level",
            "budget_amount",
            "budget_currency",
            "start_at",
            "end_at",
            "knowledge_collection",
        }
        for field in scalar_fields:
            if field in patch:
                value = patch[field]
                if isinstance(value, str):
                    value = value.strip()
                    if field in {"title", "objective"} and not value:
                        raise ValueError(f"{field} is required")
                setattr(operation, field, value)
        if "channels" in patch:
            operation.channels = self._clean_list(patch["channels"])
        if "success_metrics" in patch:
            operation.success_metrics = self._clean_list(patch["success_metrics"])
        if "constraints" in patch:
            operation.constraints = self._clean_list(patch["constraints"])
        if "metadata" in patch:
            operation.operation_metadata = patch["metadata"] or {}
        operation.plan_outline = self.build_plan_outline(operation)
        await self.session.commit()
        await self.session.refresh(operation)
        return operation

    async def regenerate_plan(self, *, workspace_id: str, operation_id: UUID) -> CommercialOperation:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        operation.plan_outline = self.build_plan_outline(operation)
        if operation.status == CommercialOperationStatus.DRAFT.value:
            operation.status = CommercialOperationStatus.PLANNING.value
        await self.session.commit()
        await self.session.refresh(operation)
        return operation

    async def create_approval(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        step_key: str,
        title: str,
        requested_by: str | None = None,
        requested_action: str | None = None,
        risk_level: str = "medium",
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationApproval:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        clean_step_key = self._clean_required_text(step_key, "step_key")
        if not self._plan_step(operation, clean_step_key):
            raise ValueError("step_key is not present in operation plan_outline")
        approval = CommercialOperationApproval(
            workspace_id=workspace_id,
            operation_id=operation_id,
            step_key=clean_step_key,
            title=self._clean_required_text(title, "title"),
            requested_action=requested_action.strip() if requested_action and requested_action.strip() else None,
            approval_status=CommercialOperationApprovalStatus.PENDING.value,
            risk_level=risk_level,
            requested_by=requested_by,
            approval_metadata=metadata or {},
        )
        self.session.add(approval)
        await self.session.flush()
        self._apply_approval_to_plan(operation, approval)
        await self.session.commit()
        await self.session.refresh(approval)
        return approval

    async def list_approvals(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationApproval]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationApproval).where(
            CommercialOperationApproval.workspace_id == workspace_id,
            CommercialOperationApproval.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationApproval.approval_status == status)
        result = await self.session.execute(
            statement.order_by(CommercialOperationApproval.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_approval(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        approval_id: UUID,
    ) -> CommercialOperationApproval:
        result = await self.session.execute(
            select(CommercialOperationApproval).where(
                CommercialOperationApproval.workspace_id == workspace_id,
                CommercialOperationApproval.operation_id == operation_id,
                CommercialOperationApproval.id == approval_id,
            )
        )
        approval = result.scalar_one_or_none()
        if approval is None:
            raise ValueError("Commercial operation approval not found in workspace")
        return approval

    async def approve_approval(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        approval_id: UUID,
        reviewer_user_id: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationApproval:
        return await self._decide_approval(
            workspace_id=workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            status=CommercialOperationApprovalStatus.APPROVED.value,
            reviewer_user_id=reviewer_user_id,
            reviewer_notes=reviewer_notes,
        )

    async def reject_approval(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        approval_id: UUID,
        reviewer_user_id: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationApproval:
        return await self._decide_approval(
            workspace_id=workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            status=CommercialOperationApprovalStatus.REJECTED.value,
            reviewer_user_id=reviewer_user_id,
            reviewer_notes=reviewer_notes,
        )

    async def cancel_approval(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        approval_id: UUID,
        reviewer_user_id: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationApproval:
        return await self._decide_approval(
            workspace_id=workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            status=CommercialOperationApprovalStatus.CANCELLED.value,
            reviewer_user_id=reviewer_user_id,
            reviewer_notes=reviewer_notes,
        )

    async def create_dry_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        approval_id: UUID,
        step_key: str = "execution_dry_run",
        title: str,
        requested_by: str | None = None,
        execution_mode: str = "metadata_only",
        execution_target: str | None = None,
        input_summary: str | None = None,
        expected_outputs: list[str] | None = None,
        readiness_checks: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationDryRun:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        approval = await self.require_approval(
            workspace_id=workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
        )
        if approval.approval_status != CommercialOperationApprovalStatus.APPROVED.value:
            raise ValueError("Dry-run requires an approved commercial operation approval")
        clean_step_key = self._clean_required_text(step_key, "step_key")
        if not self._plan_step(operation, clean_step_key):
            raise ValueError("step_key is not present in operation plan_outline")
        clean_outputs = self._clean_list(expected_outputs)
        clean_checks = self._clean_list(readiness_checks) or [
            "approved human gate",
            "metadata-only payload review",
            "no external account action",
            "operator result capture",
        ]
        dry_run = CommercialOperationDryRun(
            workspace_id=workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            step_key=clean_step_key,
            title=self._clean_required_text(title, "title"),
            dry_run_status=CommercialOperationDryRunStatus.CREATED.value,
            execution_mode=execution_mode,
            execution_target=execution_target.strip() if execution_target and execution_target.strip() else None,
            input_summary=input_summary.strip() if input_summary and input_summary.strip() else None,
            runbook=self._build_dry_run_runbook(
                operation=operation,
                approval=approval,
                step_key=clean_step_key,
                execution_mode=execution_mode,
                execution_target=execution_target,
                readiness_checks=clean_checks,
            ),
            expected_outputs=clean_outputs,
            readiness_checks=clean_checks,
            requested_by=requested_by,
            dry_run_metadata=metadata or {},
        )
        self.session.add(dry_run)
        await self.session.flush()
        self._apply_dry_run_to_plan(operation, dry_run)
        await self.session.commit()
        await self.session.refresh(dry_run)
        return dry_run

    async def list_dry_runs(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationDryRun]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationDryRun).where(
            CommercialOperationDryRun.workspace_id == workspace_id,
            CommercialOperationDryRun.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationDryRun.dry_run_status == status)
        result = await self.session.execute(statement.order_by(CommercialOperationDryRun.updated_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def require_dry_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        dry_run_id: UUID,
    ) -> CommercialOperationDryRun:
        result = await self.session.execute(
            select(CommercialOperationDryRun).where(
                CommercialOperationDryRun.workspace_id == workspace_id,
                CommercialOperationDryRun.operation_id == operation_id,
                CommercialOperationDryRun.id == dry_run_id,
            )
        )
        dry_run = result.scalar_one_or_none()
        if dry_run is None:
            raise ValueError("Commercial operation dry-run not found in workspace")
        return dry_run

    async def complete_dry_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        dry_run_id: UUID,
        completed_by: str | None = None,
        result_summary: str | None = None,
    ) -> CommercialOperationDryRun:
        return await self._decide_dry_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            status=CommercialOperationDryRunStatus.COMPLETED.value,
            completed_by=completed_by,
            result_summary=result_summary,
            failure_reason=None,
        )

    async def fail_dry_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        dry_run_id: UUID,
        completed_by: str | None = None,
        result_summary: str | None = None,
        failure_reason: str | None = None,
    ) -> CommercialOperationDryRun:
        return await self._decide_dry_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            status=CommercialOperationDryRunStatus.FAILED.value,
            completed_by=completed_by,
            result_summary=result_summary,
            failure_reason=failure_reason,
        )

    async def cancel_dry_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        dry_run_id: UUID,
        completed_by: str | None = None,
        result_summary: str | None = None,
    ) -> CommercialOperationDryRun:
        return await self._decide_dry_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            status=CommercialOperationDryRunStatus.CANCELLED.value,
            completed_by=completed_by,
            result_summary=result_summary,
            failure_reason=None,
        )

    async def create_content_draft(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        step_key: str = "content_production",
        channel: str,
        content_format: str = "copy",
        title: str,
        audience_segment: str | None = None,
        content_body: str | None = None,
        summary: str | None = None,
        call_to_action: str | None = None,
        source_materials: list[str] | None = None,
        asset_requests: list[dict[str, Any]] | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationContentDraft:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        clean_step_key = self._clean_required_text(step_key, "step_key")
        if not self._plan_step(operation, clean_step_key):
            raise ValueError("step_key is not present in operation plan_outline")
        clean_channel = self._clean_required_text(channel, "channel")
        clean_title = self._clean_required_text(title, "title")
        clean_summary = summary.strip() if summary and summary.strip() else None
        clean_call_to_action = call_to_action.strip() if call_to_action and call_to_action.strip() else None
        clean_source_materials = self._clean_list(source_materials)
        clean_asset_requests = self._clean_asset_requests(asset_requests)
        body = (
            content_body.strip()
            if content_body and content_body.strip()
            else self._build_content_draft_body(
                operation=operation,
                channel=clean_channel,
                content_format=content_format,
                summary=clean_summary,
                call_to_action=clean_call_to_action,
            )
        )
        draft = CommercialOperationContentDraft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            step_key=clean_step_key,
            channel=clean_channel,
            content_format=content_format,
            title=clean_title,
            draft_status=CommercialOperationContentDraftStatus.DRAFT.value,
            audience_segment=audience_segment.strip() if audience_segment and audience_segment.strip() else None,
            content_body=body,
            summary=clean_summary,
            call_to_action=clean_call_to_action,
            source_materials=clean_source_materials,
            asset_requests=clean_asset_requests,
            created_by=created_by,
            updated_by=created_by,
            content_metadata=metadata or {},
        )
        self.session.add(draft)
        await self.session.flush()
        self._apply_content_draft_to_plan(operation, draft)
        await self.session.commit()
        await self.session.refresh(draft)
        return draft

    async def list_content_drafts(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationContentDraft]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationContentDraft).where(
            CommercialOperationContentDraft.workspace_id == workspace_id,
            CommercialOperationContentDraft.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationContentDraft.draft_status == status)
        result = await self.session.execute(
            statement.order_by(CommercialOperationContentDraft.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_content_draft(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        draft_id: UUID,
    ) -> CommercialOperationContentDraft:
        result = await self.session.execute(
            select(CommercialOperationContentDraft).where(
                CommercialOperationContentDraft.workspace_id == workspace_id,
                CommercialOperationContentDraft.operation_id == operation_id,
                CommercialOperationContentDraft.id == draft_id,
            )
        )
        draft = result.scalar_one_or_none()
        if draft is None:
            raise ValueError("Commercial operation content draft not found in workspace")
        return draft

    async def update_content_draft(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        draft_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationContentDraft:
        draft = await self.require_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
        )
        if draft.draft_status == CommercialOperationContentDraftStatus.ARCHIVED.value:
            raise ValueError("Archived content drafts cannot be updated")
        scalar_fields = {
            "channel",
            "content_format",
            "title",
            "audience_segment",
            "content_body",
            "summary",
            "call_to_action",
        }
        required_text_fields = {"channel", "content_format", "title", "content_body"}
        for field in scalar_fields:
            if field in patch:
                value = patch[field]
                if value is None and field in required_text_fields:
                    raise ValueError(f"{field} is required")
                if isinstance(value, str):
                    value = value.strip()
                    if field in required_text_fields and not value:
                        raise ValueError(f"{field} is required")
                setattr(draft, field, value)
        if "source_materials" in patch:
            draft.source_materials = self._clean_list(patch["source_materials"])
        if "asset_requests" in patch:
            draft.asset_requests = self._clean_asset_requests(patch["asset_requests"])
        if "metadata" in patch:
            draft.content_metadata = patch["metadata"] or {}
        draft.updated_by = updated_by
        draft.draft_status = CommercialOperationContentDraftStatus.DRAFT.value
        draft.approved_at = None
        draft.rejected_at = None
        draft.approved_by = None
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        self._apply_content_draft_to_plan(operation, draft)
        await self.session.commit()
        await self.session.refresh(draft)
        return draft

    async def mark_content_draft_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        draft_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationContentDraft:
        return await self._decide_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            status=CommercialOperationContentDraftStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def approve_content_draft(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        draft_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationContentDraft:
        return await self._decide_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            status=CommercialOperationContentDraftStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
        )

    async def reject_content_draft(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        draft_id: UUID,
        rejected_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationContentDraft:
        return await self._decide_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            status=CommercialOperationContentDraftStatus.REJECTED.value,
            actor_user_id=rejected_by,
            reviewer_notes=reviewer_notes,
        )

    async def archive_content_draft(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        draft_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationContentDraft:
        return await self._decide_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            status=CommercialOperationContentDraftStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def create_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        step_key: str = "content_production",
        content_draft_id: UUID | None = None,
        channel: str,
        asset_type: str = "image",
        title: str,
        purpose: str | None = None,
        dimensions: str | None = None,
        style_constraints: str | None = None,
        generation_prompt: str | None = None,
        negative_prompt: str | None = None,
        source_materials: list[str] | None = None,
        readiness_checks: list[str] | None = None,
        requested_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationAssetRequest:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        clean_step_key = self._clean_required_text(step_key, "step_key")
        if not self._plan_step(operation, clean_step_key):
            raise ValueError("step_key is not present in operation plan_outline")
        content_draft: CommercialOperationContentDraft | None = None
        if content_draft_id is not None:
            content_draft = await self.require_content_draft(
                workspace_id=workspace_id,
                operation_id=operation_id,
                draft_id=content_draft_id,
            )
        clean_channel = self._clean_required_text(channel, "channel")
        clean_asset_type = self._clean_required_text(asset_type, "asset_type")
        clean_title = self._clean_required_text(title, "title")
        clean_source_materials = self._clean_list(source_materials or (content_draft.source_materials if content_draft else []))
        clean_readiness_checks = self._clean_list(readiness_checks) or [
            "human review",
            "source materials attached",
            "no ComfyUI job created",
        ]
        asset_request = CommercialOperationAssetRequest(
            workspace_id=workspace_id,
            operation_id=operation_id,
            content_draft_id=content_draft_id,
            step_key=clean_step_key,
            channel=clean_channel,
            asset_type=clean_asset_type,
            title=clean_title,
            request_status=CommercialOperationAssetRequestStatus.DRAFT.value,
            purpose=purpose.strip() if purpose and purpose.strip() else None,
            dimensions=dimensions.strip() if dimensions and dimensions.strip() else None,
            style_constraints=style_constraints.strip() if style_constraints and style_constraints.strip() else None,
            generation_prompt=generation_prompt.strip() if generation_prompt and generation_prompt.strip() else None,
            negative_prompt=negative_prompt.strip() if negative_prompt and negative_prompt.strip() else None,
            source_materials=clean_source_materials,
            readiness_checks=clean_readiness_checks,
            requested_by=requested_by,
            updated_by=requested_by,
            asset_metadata=metadata or {},
        )
        asset_request.handoff_payload = self._build_asset_handoff_payload(
            operation=operation,
            asset_request=asset_request,
        )
        self.session.add(asset_request)
        await self.session.flush()
        self._apply_asset_request_to_plan(operation, asset_request)
        await self.session.commit()
        await self.session.refresh(asset_request)
        return asset_request

    async def list_asset_requests(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        content_draft_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationAssetRequest]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationAssetRequest).where(
            CommercialOperationAssetRequest.workspace_id == workspace_id,
            CommercialOperationAssetRequest.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationAssetRequest.request_status == status)
        if content_draft_id is not None:
            statement = statement.where(CommercialOperationAssetRequest.content_draft_id == content_draft_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationAssetRequest.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
    ) -> CommercialOperationAssetRequest:
        result = await self.session.execute(
            select(CommercialOperationAssetRequest).where(
                CommercialOperationAssetRequest.workspace_id == workspace_id,
                CommercialOperationAssetRequest.operation_id == operation_id,
                CommercialOperationAssetRequest.id == asset_request_id,
            )
        )
        asset_request = result.scalar_one_or_none()
        if asset_request is None:
            raise ValueError("Commercial operation asset request not found in workspace")
        return asset_request

    async def update_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationAssetRequest:
        asset_request = await self.require_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
        )
        if asset_request.request_status == CommercialOperationAssetRequestStatus.ARCHIVED.value:
            raise ValueError("Archived asset requests cannot be updated")
        if "content_draft_id" in patch and patch["content_draft_id"] is not None:
            await self.require_content_draft(
                workspace_id=workspace_id,
                operation_id=operation_id,
                draft_id=patch["content_draft_id"],
            )
        scalar_fields = {
            "content_draft_id",
            "channel",
            "asset_type",
            "title",
            "purpose",
            "dimensions",
            "style_constraints",
            "generation_prompt",
            "negative_prompt",
        }
        required_text_fields = {"channel", "asset_type", "title"}
        for field in scalar_fields:
            if field in patch:
                value = patch[field]
                if value is None and field in required_text_fields:
                    raise ValueError(f"{field} is required")
                if isinstance(value, str):
                    value = value.strip()
                    if field in required_text_fields and not value:
                        raise ValueError(f"{field} is required")
                setattr(asset_request, field, value)
        if "source_materials" in patch:
            asset_request.source_materials = self._clean_list(patch["source_materials"])
        if "readiness_checks" in patch:
            asset_request.readiness_checks = self._clean_list(patch["readiness_checks"])
        if "metadata" in patch:
            asset_request.asset_metadata = patch["metadata"] or {}
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        asset_request.handoff_payload = self._build_asset_handoff_payload(
            operation=operation,
            asset_request=asset_request,
        )
        asset_request.updated_by = updated_by
        asset_request.request_status = CommercialOperationAssetRequestStatus.DRAFT.value
        asset_request.approved_by = None
        asset_request.prepared_by = None
        asset_request.approved_at = None
        asset_request.rejected_at = None
        asset_request.prepared_at = None
        asset_request.failed_at = None
        asset_request.failure_reason = None
        asset_request.result_summary = None
        self._apply_asset_request_to_plan(operation, asset_request)
        await self.session.commit()
        await self.session.refresh(asset_request)
        return asset_request

    async def mark_asset_request_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationAssetRequest:
        return await self._decide_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            status=CommercialOperationAssetRequestStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def approve_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationAssetRequest:
        return await self._decide_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            status=CommercialOperationAssetRequestStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def reject_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        rejected_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationAssetRequest:
        return await self._decide_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            status=CommercialOperationAssetRequestStatus.REJECTED.value,
            actor_user_id=rejected_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def prepare_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        prepared_by: str | None = None,
        result_summary: str | None = None,
    ) -> CommercialOperationAssetRequest:
        return await self._decide_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            status=CommercialOperationAssetRequestStatus.PREPARED.value,
            actor_user_id=prepared_by,
            reviewer_notes=None,
            result_summary=result_summary,
            failure_reason=None,
        )

    async def fail_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        updated_by: str | None = None,
        failure_reason: str | None = None,
    ) -> CommercialOperationAssetRequest:
        return await self._decide_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            status=CommercialOperationAssetRequestStatus.FAILED.value,
            actor_user_id=updated_by,
            reviewer_notes=None,
            result_summary=None,
            failure_reason=failure_reason,
        )

    async def archive_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationAssetRequest:
        return await self._decide_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            status=CommercialOperationAssetRequestStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def create_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        title: str | None = None,
        workflow_name: str = "future_comfyui_handoff",
        dimensions: str | None = None,
        generation_prompt: str | None = None,
        negative_prompt: str | None = None,
        workflow_payload: dict[str, Any] | None = None,
        prompt_payload: dict[str, Any] | None = None,
        source_materials: list[str] | None = None,
        readiness_checks: list[str] | None = None,
        requested_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        asset_request = await self.require_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
        )
        if asset_request.request_status not in {
            CommercialOperationAssetRequestStatus.APPROVED.value,
            CommercialOperationAssetRequestStatus.PREPARED.value,
        }:
            raise ValueError("Only approved or prepared asset requests can create ComfyUI handoffs")
        clean_workflow_name = self._clean_required_text(workflow_name, "workflow_name")[:128]
        clean_title = (
            self._clean_required_text(title, "title")
            if title and title.strip()
            else f"ComfyUI handoff: {asset_request.title}"
        )[:255]
        clean_source_materials = self._clean_list(source_materials or asset_request.source_materials)
        clean_readiness_checks = self._clean_list(readiness_checks) or [
            "asset request approved or prepared",
            "operator reviewed source materials",
            "ComfyUI job not submitted",
            "external execution disabled",
        ]
        clean_prompt_payload = prompt_payload if isinstance(prompt_payload, dict) else {}
        if not clean_prompt_payload:
            clean_prompt_payload = {
                "asset_request_id": str(asset_request.id),
                "asset_type": asset_request.asset_type,
                "channel": asset_request.channel,
                "dimensions": asset_request.dimensions,
                "style_constraints": asset_request.style_constraints,
                "generation_prompt": asset_request.generation_prompt,
                "negative_prompt": asset_request.negative_prompt,
                "source_materials": asset_request.source_materials,
            }
        clean_workflow_payload = workflow_payload if isinstance(workflow_payload, dict) else {}
        clean_workflow_payload = {
            **clean_workflow_payload,
            "workflow_name": clean_workflow_name,
            "execution_mode": "metadata_only",
            "adapter": "future_guarded_comfyui_adapter",
        }
        handoff = CommercialOperationComfyUIHandoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request.id,
            content_draft_id=asset_request.content_draft_id,
            step_key=asset_request.step_key,
            channel=asset_request.channel,
            asset_type=asset_request.asset_type,
            title=clean_title,
            handoff_status=CommercialOperationComfyUIHandoffStatus.DRAFT.value,
            workflow_name=clean_workflow_name,
            dimensions=(dimensions.strip() if dimensions and dimensions.strip() else asset_request.dimensions),
            generation_prompt=(
                generation_prompt.strip()
                if generation_prompt and generation_prompt.strip()
                else asset_request.generation_prompt
            ),
            negative_prompt=(
                negative_prompt.strip()
                if negative_prompt and negative_prompt.strip()
                else asset_request.negative_prompt
            ),
            workflow_payload=clean_workflow_payload,
            prompt_payload=clean_prompt_payload,
            source_materials=clean_source_materials,
            readiness_checks=clean_readiness_checks,
            requested_by=requested_by,
            updated_by=requested_by,
            handoff_metadata=metadata or {},
        )
        handoff.handoff_payload = self._build_comfyui_handoff_payload(
            operation=operation,
            asset_request=asset_request,
            handoff=handoff,
        )
        self.session.add(handoff)
        await self.session.flush()
        self._apply_comfyui_handoff_to_plan(operation, handoff)
        await self.session.commit()
        await self.session.refresh(handoff)
        return handoff

    async def list_comfyui_handoffs(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        asset_request_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationComfyUIHandoff]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationComfyUIHandoff).where(
            CommercialOperationComfyUIHandoff.workspace_id == workspace_id,
            CommercialOperationComfyUIHandoff.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationComfyUIHandoff.handoff_status == status)
        if asset_request_id is not None:
            statement = statement.where(CommercialOperationComfyUIHandoff.asset_request_id == asset_request_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationComfyUIHandoff.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
    ) -> CommercialOperationComfyUIHandoff:
        result = await self.session.execute(
            select(CommercialOperationComfyUIHandoff).where(
                CommercialOperationComfyUIHandoff.workspace_id == workspace_id,
                CommercialOperationComfyUIHandoff.operation_id == operation_id,
                CommercialOperationComfyUIHandoff.id == handoff_id,
            )
        )
        handoff = result.scalar_one_or_none()
        if handoff is None:
            raise ValueError("Commercial operation ComfyUI handoff not found in workspace")
        return handoff

    async def update_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        handoff = await self.require_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
        )
        if handoff.handoff_status == CommercialOperationComfyUIHandoffStatus.ARCHIVED.value:
            raise ValueError("Archived ComfyUI handoffs cannot be updated")
        asset_request = await self.require_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=handoff.asset_request_id,
        )
        if "asset_request_id" in patch and patch["asset_request_id"] is not None:
            asset_request_id = patch["asset_request_id"]
            if isinstance(asset_request_id, str):
                asset_request_id = UUID(asset_request_id)
            asset_request = await self.require_asset_request(
                workspace_id=workspace_id,
                operation_id=operation_id,
                asset_request_id=asset_request_id,
            )
            handoff.asset_request_id = asset_request.id
            handoff.content_draft_id = asset_request.content_draft_id
            handoff.step_key = asset_request.step_key
            handoff.channel = asset_request.channel
            handoff.asset_type = asset_request.asset_type
        if asset_request.request_status not in {
            CommercialOperationAssetRequestStatus.APPROVED.value,
            CommercialOperationAssetRequestStatus.PREPARED.value,
        }:
            raise ValueError("ComfyUI handoffs require an approved or prepared asset request")
        scalar_fields = {"title", "workflow_name", "dimensions", "generation_prompt", "negative_prompt"}
        required_text_fields = {"title", "workflow_name"}
        for field in scalar_fields:
            if field in patch:
                value = patch[field]
                if value is None and field in required_text_fields:
                    raise ValueError(f"{field} is required")
                if isinstance(value, str):
                    value = value.strip()
                    if field in required_text_fields and not value:
                        raise ValueError(f"{field} is required")
                setattr(handoff, field, value)
        workflow_payload = handoff.workflow_payload if isinstance(handoff.workflow_payload, dict) else {}
        if "workflow_payload" in patch:
            workflow_payload = patch["workflow_payload"] if isinstance(patch["workflow_payload"], dict) else {}
        handoff.workflow_payload = {
            **workflow_payload,
            "workflow_name": handoff.workflow_name,
            "execution_mode": "metadata_only",
            "adapter": "future_guarded_comfyui_adapter",
        }
        if "prompt_payload" in patch:
            handoff.prompt_payload = patch["prompt_payload"] if isinstance(patch["prompt_payload"], dict) else {}
        if "source_materials" in patch:
            handoff.source_materials = self._clean_list(patch["source_materials"])
        if "readiness_checks" in patch:
            handoff.readiness_checks = self._clean_list(patch["readiness_checks"])
        if "metadata" in patch:
            handoff.handoff_metadata = patch["metadata"] or {}
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        handoff.handoff_payload = self._build_comfyui_handoff_payload(
            operation=operation,
            asset_request=asset_request,
            handoff=handoff,
        )
        handoff.updated_by = updated_by
        handoff.handoff_status = CommercialOperationComfyUIHandoffStatus.DRAFT.value
        handoff.approved_by = None
        handoff.prepared_by = None
        handoff.approved_at = None
        handoff.rejected_at = None
        handoff.prepared_at = None
        handoff.failed_at = None
        handoff.failure_reason = None
        handoff.result_summary = None
        self._apply_comfyui_handoff_to_plan(operation, handoff)
        await self.session.commit()
        await self.session.refresh(handoff)
        return handoff

    async def mark_comfyui_handoff_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        return await self._decide_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            status=CommercialOperationComfyUIHandoffStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def approve_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        return await self._decide_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            status=CommercialOperationComfyUIHandoffStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def reject_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        rejected_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        return await self._decide_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            status=CommercialOperationComfyUIHandoffStatus.REJECTED.value,
            actor_user_id=rejected_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def prepare_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        prepared_by: str | None = None,
        result_summary: str | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        return await self._decide_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            status=CommercialOperationComfyUIHandoffStatus.PREPARED.value,
            actor_user_id=prepared_by,
            reviewer_notes=None,
            result_summary=result_summary,
            failure_reason=None,
        )

    async def fail_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        updated_by: str | None = None,
        failure_reason: str | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        return await self._decide_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            status=CommercialOperationComfyUIHandoffStatus.FAILED.value,
            actor_user_id=updated_by,
            reviewer_notes=None,
            result_summary=None,
            failure_reason=failure_reason,
        )

    async def archive_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationComfyUIHandoff:
        return await self._decide_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            status=CommercialOperationComfyUIHandoffStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def create_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        step_key: str = "content_production",
        content_draft_id: UUID,
        asset_request_ids: list[UUID] | None = None,
        deliverable_type: str = "content_package",
        title: str,
        summary: str | None = None,
        delivery_notes: str | None = None,
        quality_checks: list[str] | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationDeliverable:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        clean_step_key = self._clean_required_text(step_key, "step_key")
        if not self._plan_step(operation, clean_step_key):
            raise ValueError("step_key is not present in operation plan_outline")
        draft = await self.require_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=content_draft_id,
        )
        if draft.draft_status != CommercialOperationContentDraftStatus.APPROVED.value:
            raise ValueError("Only approved content drafts can produce commercial deliverables")
        if draft.step_key != clean_step_key:
            raise ValueError("deliverable step_key must match the content draft step_key")
        asset_requests = await self._require_deliverable_asset_requests(
            workspace_id=workspace_id,
            operation_id=operation_id,
            content_draft_id=content_draft_id,
            asset_request_ids=asset_request_ids or [],
        )
        clean_title = self._clean_required_text(title, "title")
        clean_type = self._clean_required_text(deliverable_type, "deliverable_type")
        clean_quality_checks = self._clean_list(quality_checks) or [
            "approved content draft",
            "linked assets reviewed",
            "Output Library artifact generated",
            "no external publishing",
        ]
        deliverable = CommercialOperationDeliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            content_draft_id=content_draft_id,
            step_key=clean_step_key,
            channel=draft.channel,
            deliverable_type=clean_type,
            title=clean_title,
            deliverable_status=CommercialOperationDeliverableStatus.DRAFT.value,
            summary=summary.strip() if summary and summary.strip() else draft.summary,
            delivery_notes=delivery_notes.strip() if delivery_notes and delivery_notes.strip() else None,
            asset_request_ids=[str(asset_request.id) for asset_request in asset_requests],
            quality_checks=clean_quality_checks,
            created_by=created_by,
            updated_by=created_by,
            deliverable_metadata=metadata or {},
        )
        self.session.add(deliverable)
        await self.session.flush()
        artifact_content = self._build_deliverable_artifact_content(
            operation=operation,
            draft=draft,
            asset_requests=asset_requests,
            deliverable=deliverable,
        )
        artifact = await OutputArtifactService(self.session).create_artifact(
            workspace_id=workspace_id,
            source_type=OutputArtifactSourceType.COMMERCIAL_OPERATION.value,
            artifact_type=OutputArtifactType.MARKDOWN.value,
            title=deliverable.title,
            summary=deliverable.summary,
            content=artifact_content,
            mime_type="text/markdown",
            metadata=self._build_deliverable_artifact_metadata(
                operation=operation,
                draft=draft,
                asset_requests=asset_requests,
                deliverable=deliverable,
            ),
            artifact_stage=OutputArtifactStage.PROCESSED.value,
            generated_by="commercial_operation_service",
            created_by=created_by,
            commit=False,
        )
        deliverable.output_artifact_id = artifact.id
        deliverable.package_payload = self._build_deliverable_package_payload(
            operation=operation,
            draft=draft,
            asset_requests=asset_requests,
            deliverable=deliverable,
        )
        self._apply_deliverable_to_plan(operation, deliverable)
        await self.session.commit()
        await self.session.refresh(deliverable)
        return deliverable

    async def list_deliverables(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        content_draft_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationDeliverable]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationDeliverable).where(
            CommercialOperationDeliverable.workspace_id == workspace_id,
            CommercialOperationDeliverable.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationDeliverable.deliverable_status == status)
        if content_draft_id is not None:
            statement = statement.where(CommercialOperationDeliverable.content_draft_id == content_draft_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationDeliverable.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
    ) -> CommercialOperationDeliverable:
        result = await self.session.execute(
            select(CommercialOperationDeliverable).where(
                CommercialOperationDeliverable.workspace_id == workspace_id,
                CommercialOperationDeliverable.operation_id == operation_id,
                CommercialOperationDeliverable.id == deliverable_id,
            )
        )
        deliverable = result.scalar_one_or_none()
        if deliverable is None:
            raise ValueError("Commercial operation deliverable not found in workspace")
        return deliverable

    async def update_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationDeliverable:
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
        )
        if deliverable.deliverable_status in {
            CommercialOperationDeliverableStatus.PACKAGED.value,
            CommercialOperationDeliverableStatus.ARCHIVED.value,
        }:
            raise ValueError("Packaged or archived deliverables cannot be updated")
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        draft = await self.require_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=deliverable.content_draft_id,
        )
        if draft.draft_status != CommercialOperationContentDraftStatus.APPROVED.value:
            raise ValueError("Only approved content drafts can produce commercial deliverables")
        if "asset_request_ids" in patch and patch["asset_request_ids"] is not None:
            asset_requests = await self._require_deliverable_asset_requests(
                workspace_id=workspace_id,
                operation_id=operation_id,
                content_draft_id=deliverable.content_draft_id,
                asset_request_ids=patch["asset_request_ids"],
            )
            deliverable.asset_request_ids = [str(asset_request.id) for asset_request in asset_requests]
        else:
            asset_requests = await self._require_deliverable_asset_requests(
                workspace_id=workspace_id,
                operation_id=operation_id,
                content_draft_id=deliverable.content_draft_id,
                asset_request_ids=[UUID(item) for item in deliverable.asset_request_ids],
            )
        scalar_fields = {"deliverable_type", "title", "summary", "delivery_notes"}
        required_text_fields = {"deliverable_type", "title"}
        for field in scalar_fields:
            if field in patch:
                value = patch[field]
                if value is None and field in required_text_fields:
                    raise ValueError(f"{field} is required")
                if isinstance(value, str):
                    value = value.strip()
                    if field in required_text_fields and not value:
                        raise ValueError(f"{field} is required")
                setattr(deliverable, field, value)
        if "quality_checks" in patch:
            deliverable.quality_checks = self._clean_list(patch["quality_checks"])
        if "metadata" in patch:
            deliverable.deliverable_metadata = patch["metadata"] or {}
        deliverable.updated_by = updated_by
        deliverable.deliverable_status = CommercialOperationDeliverableStatus.DRAFT.value
        deliverable.approved_by = None
        deliverable.packaged_by = None
        deliverable.approved_at = None
        deliverable.rejected_at = None
        deliverable.packaged_at = None
        deliverable.failed_at = None
        deliverable.failure_reason = None
        deliverable.result_summary = None
        deliverable.package_payload = self._build_deliverable_package_payload(
            operation=operation,
            draft=draft,
            asset_requests=asset_requests,
            deliverable=deliverable,
        )
        if deliverable.output_artifact_id is not None:
            artifact = await OutputArtifactService(self.session).require_artifact(
                workspace_id=workspace_id,
                artifact_id=deliverable.output_artifact_id,
            )
            artifact.title = deliverable.title[:255]
            artifact.summary = deliverable.summary
            artifact.content = self._build_deliverable_artifact_content(
                operation=operation,
                draft=draft,
                asset_requests=asset_requests,
                deliverable=deliverable,
            )
            artifact.artifact_metadata = self._build_deliverable_artifact_metadata(
                operation=operation,
                draft=draft,
                asset_requests=asset_requests,
                deliverable=deliverable,
            )
            artifact.artifact_stage = OutputArtifactStage.PROCESSED.value
        self._apply_deliverable_to_plan(operation, deliverable)
        await self.session.commit()
        await self.session.refresh(deliverable)
        return deliverable

    async def mark_deliverable_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationDeliverable:
        return await self._decide_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            status=CommercialOperationDeliverableStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def approve_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationDeliverable:
        return await self._decide_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            status=CommercialOperationDeliverableStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def reject_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        rejected_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationDeliverable:
        return await self._decide_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            status=CommercialOperationDeliverableStatus.REJECTED.value,
            actor_user_id=rejected_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def package_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        packaged_by: str | None = None,
        result_summary: str | None = None,
    ) -> CommercialOperationDeliverable:
        return await self._decide_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            status=CommercialOperationDeliverableStatus.PACKAGED.value,
            actor_user_id=packaged_by,
            reviewer_notes=None,
            result_summary=result_summary,
            failure_reason=None,
        )

    async def fail_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        updated_by: str | None = None,
        failure_reason: str | None = None,
    ) -> CommercialOperationDeliverable:
        return await self._decide_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            status=CommercialOperationDeliverableStatus.FAILED.value,
            actor_user_id=updated_by,
            reviewer_notes=None,
            result_summary=None,
            failure_reason=failure_reason,
        )

    async def archive_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationDeliverable:
        return await self._decide_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            status=CommercialOperationDeliverableStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def create_evidence_snapshot(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        evidence_type: str = "rag_snapshot",
        title: str | None = None,
        knowledge_collection: str | None = None,
        query: str | None = None,
        evidence_summary: str | None = None,
        relevance_notes: str | None = None,
        source_document_ids: list[str] | None = None,
        source_links: list[dict[str, Any]] | None = None,
        evidence_items: list[dict[str, Any]] | None = None,
        coverage_checks: list[str] | None = None,
        snapshot_payload: dict[str, Any] | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationEvidenceSnapshot:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
        )
        if deliverable.deliverable_status != CommercialOperationDeliverableStatus.PACKAGED.value:
            raise ValueError("Evidence snapshots require a packaged commercial deliverable")
        clean_type = self._clean_required_text(evidence_type, "evidence_type")
        clean_collection = (
            knowledge_collection.strip()
            if knowledge_collection and knowledge_collection.strip()
            else operation.knowledge_collection
        )
        clean_title = (
            title.strip()
            if title and title.strip()
            else f"Evidence snapshot: {deliverable.title}"
        )
        clean_checks = self._clean_list(coverage_checks) or [
            "source documents or evidence links reviewed",
            "operator confirms evidence relevance",
            "snapshot does not run live RAG ingestion or external analytics",
        ]
        snapshot = CommercialOperationEvidenceSnapshot(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable.id,
            content_draft_id=deliverable.content_draft_id,
            output_artifact_id=deliverable.output_artifact_id,
            step_key=deliverable.step_key,
            channel=deliverable.channel,
            evidence_type=clean_type,
            title=clean_title[:255],
            snapshot_status=CommercialOperationEvidenceSnapshotStatus.DRAFT.value,
            knowledge_collection=clean_collection,
            query=query.strip() if query and query.strip() else None,
            evidence_summary=evidence_summary.strip() if evidence_summary and evidence_summary.strip() else None,
            relevance_notes=relevance_notes.strip() if relevance_notes and relevance_notes.strip() else None,
            source_document_ids=self._clean_list(source_document_ids),
            source_links=self._clean_json_records(source_links),
            evidence_items=self._clean_json_records(evidence_items),
            coverage_checks=clean_checks,
            snapshot_payload=snapshot_payload or {},
            created_by=created_by,
            updated_by=created_by,
            snapshot_metadata=metadata or {},
        )
        self.session.add(snapshot)
        await self.session.flush()
        snapshot.snapshot_payload = {
            **(snapshot.snapshot_payload or {}),
            **self._build_evidence_snapshot_payload(
                operation=operation,
                deliverable=deliverable,
                snapshot=snapshot,
            ),
        }
        self._apply_evidence_snapshot_to_deliverable(deliverable, snapshot)
        self._apply_evidence_snapshot_to_plan(operation, snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot

    async def list_evidence_snapshots(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        deliverable_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationEvidenceSnapshot]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationEvidenceSnapshot).where(
            CommercialOperationEvidenceSnapshot.workspace_id == workspace_id,
            CommercialOperationEvidenceSnapshot.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationEvidenceSnapshot.snapshot_status == status)
        if deliverable_id is not None:
            statement = statement.where(CommercialOperationEvidenceSnapshot.deliverable_id == deliverable_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationEvidenceSnapshot.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_evidence_snapshot(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        snapshot_id: UUID,
    ) -> CommercialOperationEvidenceSnapshot:
        result = await self.session.execute(
            select(CommercialOperationEvidenceSnapshot).where(
                CommercialOperationEvidenceSnapshot.workspace_id == workspace_id,
                CommercialOperationEvidenceSnapshot.operation_id == operation_id,
                CommercialOperationEvidenceSnapshot.id == snapshot_id,
            )
        )
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            raise ValueError("Commercial operation evidence snapshot not found in workspace")
        return snapshot

    async def update_evidence_snapshot(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        snapshot_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationEvidenceSnapshot:
        snapshot = await self.require_evidence_snapshot(
            workspace_id=workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
        )
        if snapshot.snapshot_status not in {
            CommercialOperationEvidenceSnapshotStatus.DRAFT.value,
            CommercialOperationEvidenceSnapshotStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected evidence snapshots can be updated")
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=snapshot.deliverable_id,
        )
        scalar_fields = {
            "evidence_type",
            "title",
            "knowledge_collection",
            "query",
            "evidence_summary",
            "relevance_notes",
        }
        required_text_fields = {"evidence_type", "title"}
        for field in scalar_fields:
            if field in patch:
                value = patch[field]
                if value is None and field in required_text_fields:
                    raise ValueError(f"{field} is required")
                if isinstance(value, str):
                    value = value.strip()
                    if field in required_text_fields and not value:
                        raise ValueError(f"{field} is required")
                    if field not in required_text_fields and not value:
                        value = None
                setattr(snapshot, field, value)
        if "source_document_ids" in patch and patch["source_document_ids"] is not None:
            snapshot.source_document_ids = self._clean_list(patch["source_document_ids"])
        if "source_links" in patch and patch["source_links"] is not None:
            snapshot.source_links = self._clean_json_records(patch["source_links"])
        if "evidence_items" in patch and patch["evidence_items"] is not None:
            snapshot.evidence_items = self._clean_json_records(patch["evidence_items"])
        if "coverage_checks" in patch and patch["coverage_checks"] is not None:
            snapshot.coverage_checks = self._clean_list(patch["coverage_checks"])
        if "snapshot_payload" in patch and patch["snapshot_payload"] is not None:
            snapshot.snapshot_payload = patch["snapshot_payload"] or {}
        if "metadata" in patch and patch["metadata"] is not None:
            snapshot.snapshot_metadata = patch["metadata"] or {}
        snapshot.updated_by = updated_by
        snapshot.snapshot_status = CommercialOperationEvidenceSnapshotStatus.DRAFT.value
        snapshot.approved_by = None
        snapshot.approved_at = None
        snapshot.rejected_at = None
        snapshot.archived_at = None
        snapshot.reviewer_notes = None
        snapshot.snapshot_payload = {
            **(snapshot.snapshot_payload or {}),
            **self._build_evidence_snapshot_payload(
                operation=operation,
                deliverable=deliverable,
                snapshot=snapshot,
            ),
        }
        self._apply_evidence_snapshot_to_deliverable(deliverable, snapshot)
        self._apply_evidence_snapshot_to_plan(operation, snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot

    async def mark_evidence_snapshot_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        snapshot_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationEvidenceSnapshot:
        return await self._decide_evidence_snapshot(
            workspace_id=workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            status=CommercialOperationEvidenceSnapshotStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def approve_evidence_snapshot(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        snapshot_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationEvidenceSnapshot:
        return await self._decide_evidence_snapshot(
            workspace_id=workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            status=CommercialOperationEvidenceSnapshotStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
        )

    async def reject_evidence_snapshot(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        snapshot_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationEvidenceSnapshot:
        return await self._decide_evidence_snapshot(
            workspace_id=workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            status=CommercialOperationEvidenceSnapshotStatus.REJECTED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def archive_evidence_snapshot(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        snapshot_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationEvidenceSnapshot:
        return await self._decide_evidence_snapshot(
            workspace_id=workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            status=CommercialOperationEvidenceSnapshotStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def create_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        execution_type: str = "manual_handoff",
        execution_mode: str = "metadata_only",
        title: str,
        execution_target: str | None = None,
        input_summary: str | None = None,
        runbook: list[dict[str, Any]] | None = None,
        readiness_checks: list[str] | None = None,
        expected_outputs: list[str] | None = None,
        evidence_snapshot_ids: list[UUID] | None = None,
        operator_checklist: list[dict[str, Any]] | None = None,
        requested_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationExecutionRequest:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
        )
        if deliverable.deliverable_status != CommercialOperationDeliverableStatus.PACKAGED.value:
            raise ValueError("Only packaged deliverables can create execution requests")
        evidence_snapshots = await self._resolve_execution_evidence_snapshots(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable.id,
            snapshot_ids=evidence_snapshot_ids,
        )
        clean_title = self._clean_required_text(title, "title")
        clean_type = self._clean_required_text(execution_type, "execution_type")
        clean_mode = self._clean_required_text(execution_mode, "execution_mode")
        clean_checks = self._clean_list(readiness_checks) or [
            "packaged deliverable is available in Output Library",
            "human approval required before runtime execution",
            "no external action executed by this request",
        ]
        if evidence_snapshots and "approved evidence snapshots reviewed" not in clean_checks:
            clean_checks.append("approved evidence snapshots reviewed")
        clean_outputs = self._clean_list(expected_outputs) or [
            "execution request approved or prepared for future runtime handoff",
            "future runtime handoff remains traceable to the packaged deliverable",
        ]
        clean_runbook = self._clean_execution_runbook(runbook) or [
            {"step": "review packaged deliverable", "status": "pending"},
            {"step": "confirm target account or runtime manually", "status": "pending"},
            {"step": "prepare future monitored execution handoff", "status": "pending"},
        ]
        clean_checklist = self._clean_operator_checklist(operator_checklist) or self._build_operator_checklist(
            deliverable=deliverable,
            evidence_snapshots=evidence_snapshots,
        )
        request = CommercialOperationExecutionRequest(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable.id,
            output_artifact_id=deliverable.output_artifact_id,
            step_key=deliverable.step_key,
            channel=deliverable.channel,
            execution_type=clean_type,
            execution_mode=clean_mode,
            title=clean_title,
            request_status=CommercialOperationExecutionRequestStatus.DRAFT.value,
            execution_target=execution_target.strip() if execution_target and execution_target.strip() else None,
            input_summary=input_summary.strip() if input_summary and input_summary.strip() else deliverable.summary,
            runbook=clean_runbook,
            readiness_checks=clean_checks,
            expected_outputs=clean_outputs,
            evidence_snapshot_ids=[str(snapshot.id) for snapshot in evidence_snapshots],
            operator_checklist=clean_checklist,
            requested_by=requested_by,
            updated_by=requested_by,
            execution_metadata=metadata or {},
        )
        self.session.add(request)
        await self.session.flush()
        request.handoff_payload = self._build_execution_request_handoff_payload(
            operation=operation,
            deliverable=deliverable,
            execution_request=request,
        )
        self._apply_execution_request_to_plan(operation, request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def list_execution_requests(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        deliverable_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationExecutionRequest]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationExecutionRequest).where(
            CommercialOperationExecutionRequest.workspace_id == workspace_id,
            CommercialOperationExecutionRequest.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationExecutionRequest.request_status == status)
        if deliverable_id is not None:
            statement = statement.where(CommercialOperationExecutionRequest.deliverable_id == deliverable_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationExecutionRequest.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
    ) -> CommercialOperationExecutionRequest:
        result = await self.session.execute(
            select(CommercialOperationExecutionRequest).where(
                CommercialOperationExecutionRequest.workspace_id == workspace_id,
                CommercialOperationExecutionRequest.operation_id == operation_id,
                CommercialOperationExecutionRequest.id == execution_request_id,
            )
        )
        request = result.scalar_one_or_none()
        if request is None:
            raise ValueError("Commercial operation execution request not found in workspace")
        return request

    async def update_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        request = await self.require_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
        )
        if request.request_status in {
            CommercialOperationExecutionRequestStatus.PREPARED.value,
            CommercialOperationExecutionRequestStatus.CANCELLED.value,
            CommercialOperationExecutionRequestStatus.ARCHIVED.value,
        }:
            raise ValueError("Prepared, cancelled, or archived execution requests cannot be updated")
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=request.deliverable_id,
        )
        scalar_fields = {"execution_type", "execution_mode", "title", "execution_target", "input_summary"}
        required_text_fields = {"execution_type", "execution_mode", "title"}
        for field in scalar_fields:
            if field in patch:
                value = patch[field]
                if value is None and field in required_text_fields:
                    raise ValueError(f"{field} is required")
                if isinstance(value, str):
                    value = value.strip()
                    if field in required_text_fields and not value:
                        raise ValueError(f"{field} is required")
                    if field in {"execution_target", "input_summary"} and not value:
                        value = None
                setattr(request, field, value)
        if "runbook" in patch and patch["runbook"] is not None:
            request.runbook = self._clean_execution_runbook(patch["runbook"])
        if "readiness_checks" in patch and patch["readiness_checks"] is not None:
            request.readiness_checks = self._clean_list(patch["readiness_checks"])
        if "expected_outputs" in patch and patch["expected_outputs"] is not None:
            request.expected_outputs = self._clean_list(patch["expected_outputs"])
        if "evidence_snapshot_ids" in patch and patch["evidence_snapshot_ids"] is not None:
            evidence_snapshots = await self._resolve_execution_evidence_snapshots(
                workspace_id=workspace_id,
                operation_id=operation_id,
                deliverable_id=deliverable.id,
                snapshot_ids=patch["evidence_snapshot_ids"],
            )
            request.evidence_snapshot_ids = [str(snapshot.id) for snapshot in evidence_snapshots]
            if evidence_snapshots and "approved evidence snapshots reviewed" not in request.readiness_checks:
                request.readiness_checks = [
                    *request.readiness_checks,
                    "approved evidence snapshots reviewed",
                ]
        if "operator_checklist" in patch and patch["operator_checklist"] is not None:
            request.operator_checklist = self._clean_operator_checklist(patch["operator_checklist"])
        if "metadata" in patch and patch["metadata"] is not None:
            request.execution_metadata = patch["metadata"] or {}
        request.updated_by = updated_by
        request.request_status = CommercialOperationExecutionRequestStatus.DRAFT.value
        request.approved_by = None
        request.prepared_by = None
        request.cancelled_by = None
        request.approved_at = None
        request.rejected_at = None
        request.prepared_at = None
        request.failed_at = None
        request.cancelled_at = None
        request.archived_at = None
        request.failure_reason = None
        request.result_summary = None
        request.reviewer_notes = None
        request.handoff_payload = self._build_execution_request_handoff_payload(
            operation=operation,
            deliverable=deliverable,
            execution_request=request,
        )
        self._apply_execution_request_to_plan(operation, request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def mark_execution_request_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        return await self._decide_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            status=CommercialOperationExecutionRequestStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def approve_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        return await self._decide_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            status=CommercialOperationExecutionRequestStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def reject_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        rejected_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        return await self._decide_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            status=CommercialOperationExecutionRequestStatus.REJECTED.value,
            actor_user_id=rejected_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def prepare_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        prepared_by: str | None = None,
        result_summary: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        return await self._decide_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            status=CommercialOperationExecutionRequestStatus.PREPARED.value,
            actor_user_id=prepared_by,
            reviewer_notes=None,
            result_summary=result_summary,
            failure_reason=None,
        )

    async def fail_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        updated_by: str | None = None,
        failure_reason: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        return await self._decide_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            status=CommercialOperationExecutionRequestStatus.FAILED.value,
            actor_user_id=updated_by,
            reviewer_notes=None,
            result_summary=None,
            failure_reason=failure_reason,
        )

    async def cancel_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        return await self._decide_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            status=CommercialOperationExecutionRequestStatus.CANCELLED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def archive_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationExecutionRequest:
        return await self._decide_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            status=CommercialOperationExecutionRequestStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
            result_summary=None,
            failure_reason=None,
        )

    async def create_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        title: str | None = None,
        execution_target: str | None = None,
        input_payload: dict[str, Any] | None = None,
        max_retries: int = 0,
        operator_notes: str | None = None,
        queued_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationExecutionRun:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        request = await self.require_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
        )
        if request.request_status != CommercialOperationExecutionRequestStatus.PREPARED.value:
            raise ValueError("Only prepared execution requests can create execution runs")
        clean_title = title.strip() if title and title.strip() else f"Run: {request.title}"
        run = CommercialOperationExecutionRun(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=request.id,
            deliverable_id=request.deliverable_id,
            output_artifact_id=request.output_artifact_id,
            step_key=request.step_key,
            channel=request.channel,
            execution_type=request.execution_type,
            execution_mode=request.execution_mode,
            execution_target=(
                execution_target.strip()
                if execution_target and execution_target.strip()
                else request.execution_target
            ),
            title=clean_title[:255],
            run_status=CommercialOperationExecutionRunStatus.QUEUED.value,
            input_payload=input_payload or {},
            runbook_snapshot=request.runbook,
            readiness_checks=request.readiness_checks,
            expected_outputs=request.expected_outputs,
            evidence_snapshot_ids=request.evidence_snapshot_ids,
            operator_checklist_snapshot=request.operator_checklist,
            retry_count=0,
            max_retries=max(0, max_retries),
            operator_notes=operator_notes.strip() if operator_notes and operator_notes.strip() else None,
            queued_by=queued_by,
            queued_at=datetime.now(UTC),
            run_metadata=metadata or {},
        )
        self.session.add(run)
        await self.session.flush()
        run.runtime_payload = self._build_execution_run_runtime_payload(
            operation=operation,
            execution_request=request,
            execution_run=run,
        )
        run.recovery_plan = self._build_execution_run_recovery_plan(run)
        self._apply_execution_run_to_plan(operation, run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def list_execution_runs(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        execution_request_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationExecutionRun]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationExecutionRun).where(
            CommercialOperationExecutionRun.workspace_id == workspace_id,
            CommercialOperationExecutionRun.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationExecutionRun.run_status == status)
        if execution_request_id is not None:
            statement = statement.where(CommercialOperationExecutionRun.execution_request_id == execution_request_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationExecutionRun.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
    ) -> CommercialOperationExecutionRun:
        result = await self.session.execute(
            select(CommercialOperationExecutionRun).where(
                CommercialOperationExecutionRun.workspace_id == workspace_id,
                CommercialOperationExecutionRun.operation_id == operation_id,
                CommercialOperationExecutionRun.id == execution_run_id,
            )
        )
        run = result.scalar_one_or_none()
        if run is None:
            raise ValueError("Commercial operation execution run not found in workspace")
        return run

    async def update_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationExecutionRun:
        run = await self.require_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
        )
        if run.run_status not in {
            CommercialOperationExecutionRunStatus.QUEUED.value,
            CommercialOperationExecutionRunStatus.RETRYING.value,
        }:
            raise ValueError("Only queued or retrying execution runs can be updated")
        if "title" in patch and patch["title"] is not None:
            run.title = self._clean_required_text(patch["title"], "title")[:255]
        if "execution_target" in patch:
            value = patch["execution_target"]
            run.execution_target = value.strip() if isinstance(value, str) and value.strip() else None
        if "input_payload" in patch and patch["input_payload"] is not None:
            run.input_payload = patch["input_payload"] or {}
        if "max_retries" in patch and patch["max_retries"] is not None:
            run.max_retries = max(0, int(patch["max_retries"]))
        if "operator_notes" in patch:
            value = patch["operator_notes"]
            run.operator_notes = value.strip() if isinstance(value, str) and value.strip() else None
        if "metadata" in patch and patch["metadata"] is not None:
            run.run_metadata = patch["metadata"] or {}
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        request = await self.require_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=run.execution_request_id,
        )
        run.runtime_payload = self._build_execution_run_runtime_payload(
            operation=operation,
            execution_request=request,
            execution_run=run,
        )
        run.recovery_plan = self._build_execution_run_recovery_plan(run)
        if updated_by is not None:
            run.run_metadata = {**(run.run_metadata or {}), "updated_by": updated_by}
        self._apply_execution_run_to_plan(operation, run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def start_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        started_by: str | None = None,
        operator_notes: str | None = None,
    ) -> CommercialOperationExecutionRun:
        return await self._decide_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            status=CommercialOperationExecutionRunStatus.RUNNING.value,
            actor_user_id=started_by,
            result_summary=None,
            failure_reason=None,
            operator_notes=operator_notes,
            result_payload=None,
        )

    async def succeed_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        completed_by: str | None = None,
        result_summary: str | None = None,
        result_payload: dict[str, Any] | None = None,
    ) -> CommercialOperationExecutionRun:
        return await self._decide_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            status=CommercialOperationExecutionRunStatus.SUCCEEDED.value,
            actor_user_id=completed_by,
            result_summary=result_summary,
            failure_reason=None,
            operator_notes=None,
            result_payload=result_payload,
        )

    async def fail_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        updated_by: str | None = None,
        failure_reason: str | None = None,
        result_payload: dict[str, Any] | None = None,
    ) -> CommercialOperationExecutionRun:
        return await self._decide_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            status=CommercialOperationExecutionRunStatus.FAILED.value,
            actor_user_id=updated_by,
            result_summary=None,
            failure_reason=failure_reason,
            operator_notes=None,
            result_payload=result_payload,
        )

    async def retry_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        updated_by: str | None = None,
        operator_notes: str | None = None,
    ) -> CommercialOperationExecutionRun:
        return await self._decide_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            status=CommercialOperationExecutionRunStatus.RETRYING.value,
            actor_user_id=updated_by,
            result_summary=None,
            failure_reason=None,
            operator_notes=operator_notes,
            result_payload=None,
        )

    async def cancel_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        updated_by: str | None = None,
        operator_notes: str | None = None,
    ) -> CommercialOperationExecutionRun:
        return await self._decide_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            status=CommercialOperationExecutionRunStatus.CANCELLED.value,
            actor_user_id=updated_by,
            result_summary=None,
            failure_reason=None,
            operator_notes=operator_notes,
            result_payload=None,
        )

    async def archive_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        updated_by: str | None = None,
        operator_notes: str | None = None,
    ) -> CommercialOperationExecutionRun:
        return await self._decide_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            status=CommercialOperationExecutionRunStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            result_summary=None,
            failure_reason=None,
            operator_notes=operator_notes,
            result_payload=None,
        )

    async def create_result(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        result_type: str = "operator_report",
        title: str | None = None,
        summary: str | None = None,
        outcome_summary: str | None = None,
        observed_metrics: list[dict[str, Any]] | None = None,
        commercial_signals: list[str] | None = None,
        evidence_links: list[dict[str, Any]] | None = None,
        follow_up_actions: list[str] | None = None,
        result_payload: dict[str, Any] | None = None,
        recommendation_payload: dict[str, Any] | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationResult:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        run = await self.require_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
        )
        if run.run_status not in {
            CommercialOperationExecutionRunStatus.SUCCEEDED.value,
            CommercialOperationExecutionRunStatus.FAILED.value,
            CommercialOperationExecutionRunStatus.CANCELLED.value,
        }:
            raise ValueError("Only terminal execution runs can create result records")

        clean_title = title.strip() if title and title.strip() else f"Result: {run.title}"
        result = CommercialOperationResult(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=run.id,
            execution_request_id=run.execution_request_id,
            deliverable_id=run.deliverable_id,
            output_artifact_id=run.output_artifact_id,
            step_key=run.step_key,
            channel=run.channel,
            result_type=self._clean_required_text(result_type, "result_type")[:64],
            title=clean_title[:255],
            result_status=CommercialOperationResultStatus.DRAFT.value,
            summary=summary.strip() if summary and summary.strip() else None,
            outcome_summary=outcome_summary.strip() if outcome_summary and outcome_summary.strip() else None,
            observed_metrics=self._clean_result_metrics(observed_metrics),
            commercial_signals=self._clean_list(commercial_signals),
            evidence_links=self._clean_result_evidence_links(evidence_links),
            follow_up_actions=self._clean_list(follow_up_actions),
            result_payload=result_payload or {},
            recommendation_payload={},
            created_by=created_by,
            result_metadata=metadata or {},
        )
        self.session.add(result)
        await self.session.flush()
        result.recommendation_payload = {
            **self._build_result_recommendation_payload(
                operation=operation,
                execution_run=run,
                result=result,
            ),
            **(recommendation_payload or {}),
        }
        self._apply_result_to_plan(operation, result)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def list_results(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        execution_run_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationResult]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationResult).where(
            CommercialOperationResult.workspace_id == workspace_id,
            CommercialOperationResult.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationResult.result_status == status)
        if execution_run_id is not None:
            statement = statement.where(CommercialOperationResult.execution_run_id == execution_run_id)
        result = await self.session.execute(statement.order_by(CommercialOperationResult.updated_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def require_result(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
    ) -> CommercialOperationResult:
        result = await self.session.execute(
            select(CommercialOperationResult).where(
                CommercialOperationResult.workspace_id == workspace_id,
                CommercialOperationResult.operation_id == operation_id,
                CommercialOperationResult.id == result_id,
            )
        )
        commercial_result = result.scalar_one_or_none()
        if commercial_result is None:
            raise ValueError("Commercial operation result not found in workspace")
        return commercial_result

    async def update_result(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationResult:
        result = await self.require_result(workspace_id=workspace_id, operation_id=operation_id, result_id=result_id)
        if result.result_status not in {
            CommercialOperationResultStatus.DRAFT.value,
            CommercialOperationResultStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected result records can be updated")
        if "result_type" in patch and patch["result_type"] is not None:
            result.result_type = self._clean_required_text(patch["result_type"], "result_type")[:64]
        if "title" in patch and patch["title"] is not None:
            result.title = self._clean_required_text(patch["title"], "title")[:255]
        if "summary" in patch:
            value = patch["summary"]
            result.summary = value.strip() if isinstance(value, str) and value.strip() else None
        if "outcome_summary" in patch:
            value = patch["outcome_summary"]
            result.outcome_summary = value.strip() if isinstance(value, str) and value.strip() else None
        if "observed_metrics" in patch and patch["observed_metrics"] is not None:
            result.observed_metrics = self._clean_result_metrics(patch["observed_metrics"])
        if "commercial_signals" in patch and patch["commercial_signals"] is not None:
            result.commercial_signals = self._clean_list(patch["commercial_signals"])
        if "evidence_links" in patch and patch["evidence_links"] is not None:
            result.evidence_links = self._clean_result_evidence_links(patch["evidence_links"])
        if "follow_up_actions" in patch and patch["follow_up_actions"] is not None:
            result.follow_up_actions = self._clean_list(patch["follow_up_actions"])
        if "result_payload" in patch and patch["result_payload"] is not None:
            result.result_payload = patch["result_payload"] or {}
        if "recommendation_payload" in patch and patch["recommendation_payload"] is not None:
            result.recommendation_payload = patch["recommendation_payload"] or {}
        if "metadata" in patch and patch["metadata"] is not None:
            result.result_metadata = patch["metadata"] or {}
        result.updated_by = updated_by
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        run = await self.require_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=result.execution_run_id,
        )
        if not result.recommendation_payload:
            result.recommendation_payload = self._build_result_recommendation_payload(
                operation=operation,
                execution_run=run,
                result=result,
            )
        self._apply_result_to_plan(operation, result)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def mark_result_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationResult:
        return await self._decide_result(
            workspace_id=workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            status=CommercialOperationResultStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def approve_result(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationResult:
        return await self._decide_result(
            workspace_id=workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            status=CommercialOperationResultStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
        )

    async def reject_result(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationResult:
        return await self._decide_result(
            workspace_id=workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            status=CommercialOperationResultStatus.REJECTED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def archive_result(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationResult:
        return await self._decide_result(
            workspace_id=workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            status=CommercialOperationResultStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def create_monitoring_observation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
        observation_type: str = "manual_snapshot",
        title: str | None = None,
        observation_window_start: datetime | None = None,
        observation_window_end: datetime | None = None,
        metric_snapshots: list[dict[str, Any]] | None = None,
        qualitative_signals: list[str] | None = None,
        evidence_links: list[dict[str, Any]] | None = None,
        anomaly_flags: list[str] | None = None,
        recommended_actions: list[str] | None = None,
        observation_payload: dict[str, Any] | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationMonitoringObservation:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        result = await self.require_result(workspace_id=workspace_id, operation_id=operation_id, result_id=result_id)
        if result.result_status != CommercialOperationResultStatus.APPROVED.value:
            raise ValueError("Only approved commercial results can create monitoring observations")
        self._validate_date_range(start_at=observation_window_start, end_at=observation_window_end)

        clean_title = title.strip() if title and title.strip() else f"Monitoring: {result.title}"
        observation = CommercialOperationMonitoringObservation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            result_id=result.id,
            execution_run_id=result.execution_run_id,
            execution_request_id=result.execution_request_id,
            deliverable_id=result.deliverable_id,
            output_artifact_id=result.output_artifact_id,
            step_key=result.step_key,
            channel=result.channel,
            observation_type=self._clean_required_text(observation_type, "observation_type")[:64],
            title=clean_title[:255],
            observation_status=CommercialOperationMonitoringObservationStatus.DRAFT.value,
            observation_window_start=observation_window_start,
            observation_window_end=observation_window_end,
            metric_snapshots=self._clean_result_metrics(metric_snapshots),
            qualitative_signals=self._clean_list(qualitative_signals),
            evidence_links=self._clean_result_evidence_links(evidence_links),
            anomaly_flags=self._clean_list(anomaly_flags),
            recommended_actions=self._clean_list(recommended_actions),
            observation_payload={},
            created_by=created_by,
            observation_metadata=metadata or {},
        )
        self.session.add(observation)
        await self.session.flush()
        observation.observation_payload = {
            **self._build_monitoring_observation_payload(
                operation=operation,
                result=result,
                observation=observation,
            ),
            **(observation_payload or {}),
        }
        self._apply_monitoring_observation_to_plan(operation, observation)
        await self.session.commit()
        await self.session.refresh(observation)
        return observation

    async def list_monitoring_observations(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        result_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationMonitoringObservation]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationMonitoringObservation).where(
            CommercialOperationMonitoringObservation.workspace_id == workspace_id,
            CommercialOperationMonitoringObservation.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationMonitoringObservation.observation_status == status)
        if result_id is not None:
            statement = statement.where(CommercialOperationMonitoringObservation.result_id == result_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationMonitoringObservation.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_monitoring_observation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
    ) -> CommercialOperationMonitoringObservation:
        result = await self.session.execute(
            select(CommercialOperationMonitoringObservation).where(
                CommercialOperationMonitoringObservation.workspace_id == workspace_id,
                CommercialOperationMonitoringObservation.operation_id == operation_id,
                CommercialOperationMonitoringObservation.id == observation_id,
            )
        )
        observation = result.scalar_one_or_none()
        if observation is None:
            raise ValueError("Commercial operation monitoring observation not found in workspace")
        return observation

    async def update_monitoring_observation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationMonitoringObservation:
        observation = await self.require_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
        )
        if observation.observation_status not in {
            CommercialOperationMonitoringObservationStatus.DRAFT.value,
            CommercialOperationMonitoringObservationStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected monitoring observations can be updated")
        if "observation_type" in patch and patch["observation_type"] is not None:
            observation.observation_type = self._clean_required_text(patch["observation_type"], "observation_type")[:64]
        if "title" in patch and patch["title"] is not None:
            observation.title = self._clean_required_text(patch["title"], "title")[:255]
        if "observation_window_start" in patch:
            observation.observation_window_start = patch["observation_window_start"]
        if "observation_window_end" in patch:
            observation.observation_window_end = patch["observation_window_end"]
        self._validate_date_range(
            start_at=observation.observation_window_start,
            end_at=observation.observation_window_end,
        )
        if "metric_snapshots" in patch and patch["metric_snapshots"] is not None:
            observation.metric_snapshots = self._clean_result_metrics(patch["metric_snapshots"])
        if "qualitative_signals" in patch and patch["qualitative_signals"] is not None:
            observation.qualitative_signals = self._clean_list(patch["qualitative_signals"])
        if "evidence_links" in patch and patch["evidence_links"] is not None:
            observation.evidence_links = self._clean_result_evidence_links(patch["evidence_links"])
        if "anomaly_flags" in patch and patch["anomaly_flags"] is not None:
            observation.anomaly_flags = self._clean_list(patch["anomaly_flags"])
        if "recommended_actions" in patch and patch["recommended_actions"] is not None:
            observation.recommended_actions = self._clean_list(patch["recommended_actions"])
        if "observation_payload" in patch and patch["observation_payload"] is not None:
            observation.observation_payload = patch["observation_payload"] or {}
        if "metadata" in patch and patch["metadata"] is not None:
            observation.observation_metadata = patch["metadata"] or {}
        observation.updated_by = updated_by
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        result = await self.require_result(
            workspace_id=workspace_id,
            operation_id=operation_id,
            result_id=observation.result_id,
        )
        if not observation.observation_payload:
            observation.observation_payload = self._build_monitoring_observation_payload(
                operation=operation,
                result=result,
                observation=observation,
            )
        self._apply_monitoring_observation_to_plan(operation, observation)
        await self.session.commit()
        await self.session.refresh(observation)
        return observation

    async def mark_monitoring_observation_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationMonitoringObservation:
        return await self._decide_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            status=CommercialOperationMonitoringObservationStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def approve_monitoring_observation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationMonitoringObservation:
        return await self._decide_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            status=CommercialOperationMonitoringObservationStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
        )

    async def reject_monitoring_observation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationMonitoringObservation:
        return await self._decide_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            status=CommercialOperationMonitoringObservationStatus.REJECTED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def archive_monitoring_observation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationMonitoringObservation:
        return await self._decide_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            status=CommercialOperationMonitoringObservationStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def create_optimization_decision(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
        decision_type: str = "iterate",
        title: str | None = None,
        priority: str = "normal",
        rationale: str | None = None,
        objective_updates: list[str] | None = None,
        content_actions: list[str] | None = None,
        asset_actions: list[str] | None = None,
        audience_actions: list[str] | None = None,
        execution_actions: list[str] | None = None,
        risk_controls: list[str] | None = None,
        decision_payload: dict[str, Any] | None = None,
        next_review_at: datetime | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationOptimizationDecision:
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        observation = await self.require_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
        )
        if observation.observation_status != CommercialOperationMonitoringObservationStatus.APPROVED.value:
            raise ValueError("Only approved monitoring observations can create optimization decisions")

        clean_title = title.strip() if title and title.strip() else f"Optimization: {observation.title}"
        decision = CommercialOperationOptimizationDecision(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation.id,
            result_id=observation.result_id,
            execution_run_id=observation.execution_run_id,
            execution_request_id=observation.execution_request_id,
            deliverable_id=observation.deliverable_id,
            output_artifact_id=observation.output_artifact_id,
            step_key=observation.step_key,
            channel=observation.channel,
            decision_type=self._clean_required_text(decision_type, "decision_type")[:64],
            title=clean_title[:255],
            decision_status=CommercialOperationOptimizationDecisionStatus.DRAFT.value,
            priority=self._clean_required_text(priority, "priority")[:16],
            rationale=rationale.strip() if rationale and rationale.strip() else None,
            objective_updates=self._clean_list(objective_updates),
            content_actions=self._clean_list(content_actions),
            asset_actions=self._clean_list(asset_actions),
            audience_actions=self._clean_list(audience_actions),
            execution_actions=self._clean_list(execution_actions),
            risk_controls=self._clean_list(risk_controls),
            decision_payload={},
            next_review_at=next_review_at,
            created_by=created_by,
            decision_metadata=metadata or {},
        )
        self.session.add(decision)
        await self.session.flush()
        decision.decision_payload = {
            **self._build_optimization_decision_payload(
                operation=operation,
                observation=observation,
                decision=decision,
            ),
            **(decision_payload or {}),
        }
        self._apply_optimization_decision_to_plan(operation, decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def list_optimization_decisions(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        status: str | None = None,
        observation_id: UUID | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationOptimizationDecision]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationOptimizationDecision).where(
            CommercialOperationOptimizationDecision.workspace_id == workspace_id,
            CommercialOperationOptimizationDecision.operation_id == operation_id,
        )
        if status is not None:
            statement = statement.where(CommercialOperationOptimizationDecision.decision_status == status)
        if observation_id is not None:
            statement = statement.where(CommercialOperationOptimizationDecision.observation_id == observation_id)
        result = await self.session.execute(
            statement.order_by(CommercialOperationOptimizationDecision.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def require_optimization_decision(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        decision_id: UUID,
    ) -> CommercialOperationOptimizationDecision:
        result = await self.session.execute(
            select(CommercialOperationOptimizationDecision).where(
                CommercialOperationOptimizationDecision.workspace_id == workspace_id,
                CommercialOperationOptimizationDecision.operation_id == operation_id,
                CommercialOperationOptimizationDecision.id == decision_id,
            )
        )
        decision = result.scalar_one_or_none()
        if decision is None:
            raise ValueError("Commercial operation optimization decision not found in workspace")
        return decision

    async def update_optimization_decision(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        decision_id: UUID,
        patch: dict[str, Any],
        updated_by: str | None = None,
    ) -> CommercialOperationOptimizationDecision:
        decision = await self.require_optimization_decision(
            workspace_id=workspace_id,
            operation_id=operation_id,
            decision_id=decision_id,
        )
        if decision.decision_status not in {
            CommercialOperationOptimizationDecisionStatus.DRAFT.value,
            CommercialOperationOptimizationDecisionStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected optimization decisions can be updated")
        if "decision_type" in patch and patch["decision_type"] is not None:
            decision.decision_type = self._clean_required_text(patch["decision_type"], "decision_type")[:64]
        if "title" in patch and patch["title"] is not None:
            decision.title = self._clean_required_text(patch["title"], "title")[:255]
        if "priority" in patch and patch["priority"] is not None:
            decision.priority = self._clean_required_text(patch["priority"], "priority")[:16]
        if "rationale" in patch:
            value = patch["rationale"]
            decision.rationale = value.strip() if isinstance(value, str) and value.strip() else None
        if "objective_updates" in patch and patch["objective_updates"] is not None:
            decision.objective_updates = self._clean_list(patch["objective_updates"])
        if "content_actions" in patch and patch["content_actions"] is not None:
            decision.content_actions = self._clean_list(patch["content_actions"])
        if "asset_actions" in patch and patch["asset_actions"] is not None:
            decision.asset_actions = self._clean_list(patch["asset_actions"])
        if "audience_actions" in patch and patch["audience_actions"] is not None:
            decision.audience_actions = self._clean_list(patch["audience_actions"])
        if "execution_actions" in patch and patch["execution_actions"] is not None:
            decision.execution_actions = self._clean_list(patch["execution_actions"])
        if "risk_controls" in patch and patch["risk_controls"] is not None:
            decision.risk_controls = self._clean_list(patch["risk_controls"])
        if "decision_payload" in patch and patch["decision_payload"] is not None:
            decision.decision_payload = patch["decision_payload"] or {}
        if "next_review_at" in patch:
            decision.next_review_at = patch["next_review_at"]
        if "metadata" in patch and patch["metadata"] is not None:
            decision.decision_metadata = patch["metadata"] or {}
        decision.updated_by = updated_by
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        observation = await self.require_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=decision.observation_id,
        )
        decision.decision_payload = {
            **self._build_optimization_decision_payload(
                operation=operation,
                observation=observation,
                decision=decision,
            ),
            **(decision.decision_payload or {}),
        }
        self._apply_optimization_decision_to_plan(operation, decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def mark_optimization_decision_ready(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        decision_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationOptimizationDecision:
        return await self._decide_optimization_decision(
            workspace_id=workspace_id,
            operation_id=operation_id,
            decision_id=decision_id,
            status=CommercialOperationOptimizationDecisionStatus.READY_FOR_REVIEW.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def approve_optimization_decision(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        decision_id: UUID,
        approved_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationOptimizationDecision:
        return await self._decide_optimization_decision(
            workspace_id=workspace_id,
            operation_id=operation_id,
            decision_id=decision_id,
            status=CommercialOperationOptimizationDecisionStatus.APPROVED.value,
            actor_user_id=approved_by,
            reviewer_notes=reviewer_notes,
        )

    async def reject_optimization_decision(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        decision_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationOptimizationDecision:
        return await self._decide_optimization_decision(
            workspace_id=workspace_id,
            operation_id=operation_id,
            decision_id=decision_id,
            status=CommercialOperationOptimizationDecisionStatus.REJECTED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def archive_optimization_decision(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        decision_id: UUID,
        updated_by: str | None = None,
        reviewer_notes: str | None = None,
    ) -> CommercialOperationOptimizationDecision:
        return await self._decide_optimization_decision(
            workspace_id=workspace_id,
            operation_id=operation_id,
            decision_id=decision_id,
            status=CommercialOperationOptimizationDecisionStatus.ARCHIVED.value,
            actor_user_id=updated_by,
            reviewer_notes=reviewer_notes,
        )

    async def create_link(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        link_type: str,
        target_type: str,
        target_id: str,
        title: str,
        summary: str | None = None,
        source_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CommercialOperationLink:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        link = CommercialOperationLink(
            workspace_id=workspace_id,
            operation_id=operation_id,
            link_type=link_type,
            target_type=self._clean_required_text(target_type, "target_type"),
            target_id=self._clean_required_text(target_id, "target_id"),
            title=self._clean_required_text(title, "title"),
            summary=summary.strip() if summary and summary.strip() else None,
            source_name=source_name.strip() if source_name and source_name.strip() else None,
            link_metadata=metadata or {},
        )
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def list_links(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        link_type: str | None = None,
        limit: int = 100,
    ) -> list[CommercialOperationLink]:
        await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        statement = select(CommercialOperationLink).where(
            CommercialOperationLink.workspace_id == workspace_id,
            CommercialOperationLink.operation_id == operation_id,
        )
        if link_type is not None:
            statement = statement.where(CommercialOperationLink.link_type == link_type)
        result = await self.session.execute(statement.order_by(CommercialOperationLink.updated_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def require_link(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        link_id: UUID,
    ) -> CommercialOperationLink:
        result = await self.session.execute(
            select(CommercialOperationLink).where(
                CommercialOperationLink.workspace_id == workspace_id,
                CommercialOperationLink.operation_id == operation_id,
                CommercialOperationLink.id == link_id,
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            raise ValueError("Commercial operation link not found in workspace")
        return link

    async def delete_link(self, *, workspace_id: str, operation_id: UUID, link_id: UUID) -> CommercialOperationLink:
        link = await self.require_link(workspace_id=workspace_id, operation_id=operation_id, link_id=link_id)
        await self.session.delete(link)
        await self.session.commit()
        return link

    def build_plan_outline(self, operation: CommercialOperation) -> list[dict[str, Any]]:
        """Build a deterministic non-executing plan outline.

        The outline is deliberately conservative: it creates a business plan
        surface but never publishes, controls accounts, or runs external tools.
        """

        channels = operation.channels or ["unassigned-channel"]
        metrics = operation.success_metrics or ["qualified_leads", "content_output", "review_pass_rate"]
        return [
            {
                "step_key": "intake",
                "title": "Confirm commercial objective",
                "owner": "operator",
                "status": "planned",
                "summary": operation.objective,
                "checks": ["objective", "audience", "channels", "budget", "success_metrics"],
            },
            {
                "step_key": "knowledge_research",
                "title": "Collect knowledge and materials",
                "owner": "aiops",
                "status": "planned",
                "rag_collection": operation.knowledge_collection,
                "checks": ["RAG search", "source coverage", "material gaps"],
            },
            {
                "step_key": "content_production",
                "title": "Generate channel drafts and asset requests",
                "owner": "content_pipeline",
                "status": "planned",
                "channels": channels,
                "checks": ["copy draft", "asset brief", "ComfyUI placeholder"],
            },
            {
                "step_key": "human_review",
                "title": "Review before execution",
                "owner": "reviewer",
                "status": "required",
                "risk_level": operation.risk_level,
                "checks": ["approval gate", "brand safety", "account action confirmation"],
            },
            {
                "step_key": "execution_dry_run",
                "title": "Prepare safe execution or dry-run",
                "owner": "automation_runtime",
                "status": "blocked_until_approved",
                "channels": channels,
                "checks": ["OpenClaw status", "browser worker status", "dry-run output"],
            },
            {
                "step_key": "monitor_recover",
                "title": "Monitor result and recover failures",
                "owner": "maintainer",
                "status": "planned",
                "metrics": metrics,
                "checks": ["task status", "failure reason", "retry or cancel", "result report"],
            },
        ]

    def _clean_list(self, values: list[str] | None) -> list[str]:
        return [item.strip() for item in values or [] if item and item.strip()]

    def _clean_json_records(self, values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        return [dict(item) for item in values or [] if isinstance(item, dict)]

    def _clean_asset_requests(self, values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        requests: list[dict[str, Any]] = []
        for item in values or []:
            title = str(item.get("title") or item.get("asset") or item.get("name") or "").strip()
            if not title:
                continue
            cleaned = dict(item)
            cleaned["title"] = title
            cleaned["status"] = str(cleaned.get("status") or "placeholder")
            cleaned["execution_boundary"] = "no ComfyUI job is created in this phase"
            requests.append(cleaned)
        return requests

    def _clean_execution_runbook(self, values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        for index, item in enumerate(values or [], start=1):
            if not isinstance(item, dict):
                continue
            step_title = str(item.get("step") or item.get("title") or item.get("name") or "").strip()
            if not step_title:
                continue
            cleaned = dict(item)
            cleaned["step"] = step_title
            cleaned["status"] = str(cleaned.get("status") or "pending").strip() or "pending"
            cleaned.setdefault("order", index)
            cleaned["execution_boundary"] = "metadata-only; no external runtime call"
            steps.append(cleaned)
        return steps

    def _clean_operator_checklist(self, values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        checklist: list[dict[str, Any]] = []
        for index, item in enumerate(values or [], start=1):
            if not isinstance(item, dict):
                continue
            label = str(item.get("item") or item.get("check") or item.get("title") or item.get("step") or "").strip()
            if not label:
                continue
            cleaned = dict(item)
            cleaned["item"] = label
            cleaned["status"] = str(cleaned.get("status") or "pending").strip() or "pending"
            cleaned.setdefault("order", index)
            cleaned["execution_boundary"] = "operator checklist only; no external runtime call"
            checklist.append(cleaned)
        return checklist

    def _clean_result_metrics(self, values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        metrics: list[dict[str, Any]] = []
        for item in values or []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or item.get("metric") or item.get("key") or "").strip()
            if not name:
                continue
            cleaned = dict(item)
            cleaned["name"] = name
            cleaned.setdefault("source", "operator_observed")
            cleaned["attribution_boundary"] = "operator-reported; no platform analytics ingestion"
            metrics.append(cleaned)
        return metrics

    def _clean_result_evidence_links(self, values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        links: list[dict[str, Any]] = []
        for item in values or []:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or item.get("url") or item.get("target_id") or item.get("name") or "").strip()
            if not title:
                continue
            cleaned = dict(item)
            cleaned["title"] = title
            cleaned.setdefault("type", "operator_evidence")
            cleaned["evidence_boundary"] = "reference only; not fetched or verified automatically"
            links.append(cleaned)
        return links

    def _clean_required_text(self, value: str, field_name: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{field_name} is required")
        return cleaned

    def _validate_date_range(self, *, start_at: datetime | None, end_at: datetime | None) -> None:
        if start_at is not None and end_at is not None and end_at < start_at:
            raise ValueError("end_at must be after start_at")

    async def _decide_approval(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        approval_id: UUID,
        status: str,
        reviewer_user_id: str | None,
        reviewer_notes: str | None,
    ) -> CommercialOperationApproval:
        approval = await self.require_approval(
            workspace_id=workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
        )
        if status in {
            CommercialOperationApprovalStatus.APPROVED.value,
            CommercialOperationApprovalStatus.REJECTED.value,
        } and approval.approval_status != CommercialOperationApprovalStatus.PENDING.value:
            raise ValueError("Only pending approvals can be approved or rejected")
        if status == CommercialOperationApprovalStatus.CANCELLED.value and approval.approval_status not in {
            CommercialOperationApprovalStatus.PENDING.value,
            CommercialOperationApprovalStatus.APPROVED.value,
        }:
            raise ValueError("Only pending or approved approvals can be cancelled")
        now = datetime.now(UTC)
        approval.approval_status = status
        approval.reviewer_user_id = reviewer_user_id
        approval.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        if status == CommercialOperationApprovalStatus.APPROVED.value:
            approval.approved_at = now
            approval.rejected_at = None
            approval.cancelled_at = None
        elif status == CommercialOperationApprovalStatus.REJECTED.value:
            approval.rejected_at = now
            approval.approved_at = None
            approval.cancelled_at = None
        elif status == CommercialOperationApprovalStatus.CANCELLED.value:
            approval.cancelled_at = now
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        self._apply_approval_to_plan(operation, approval)
        await self.session.commit()
        await self.session.refresh(approval)
        return approval

    def _plan_step(self, operation: CommercialOperation, step_key: str) -> dict[str, Any] | None:
        for step in operation.plan_outline or []:
            if step.get("step_key") == step_key:
                return step
        return None

    def _apply_approval_to_plan(
        self,
        operation: CommercialOperation,
        approval: CommercialOperationApproval,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == approval.step_key:
                updated = dict(step)
                updated["approval_id"] = str(approval.id)
                updated["approval_status"] = approval.approval_status
                updated["approval_risk_level"] = approval.risk_level
                if (
                    approval.approval_status == CommercialOperationApprovalStatus.CANCELLED.value
                    and approval.cancelled_at is not None
                ):
                    updated["approval_decision_at"] = approval.cancelled_at.isoformat()
                elif (
                    approval.approval_status == CommercialOperationApprovalStatus.REJECTED.value
                    and approval.rejected_at is not None
                ):
                    updated["approval_decision_at"] = approval.rejected_at.isoformat()
                elif approval.approved_at is not None:
                    updated["approval_decision_at"] = approval.approved_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    async def _decide_asset_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        asset_request_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
        result_summary: str | None,
        failure_reason: str | None,
    ) -> CommercialOperationAssetRequest:
        asset_request = await self.require_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
        )
        if asset_request.request_status == CommercialOperationAssetRequestStatus.ARCHIVED.value:
            raise ValueError("Archived asset requests cannot be changed")
        if status == CommercialOperationAssetRequestStatus.READY_FOR_REVIEW.value and asset_request.request_status not in {
            CommercialOperationAssetRequestStatus.DRAFT.value,
            CommercialOperationAssetRequestStatus.REJECTED.value,
            CommercialOperationAssetRequestStatus.FAILED.value,
        }:
            raise ValueError("Only draft, rejected, or failed asset requests can be marked ready")
        if status in {
            CommercialOperationAssetRequestStatus.APPROVED.value,
            CommercialOperationAssetRequestStatus.REJECTED.value,
        } and asset_request.request_status != CommercialOperationAssetRequestStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready asset requests can be approved or rejected")
        if status in {
            CommercialOperationAssetRequestStatus.PREPARED.value,
            CommercialOperationAssetRequestStatus.FAILED.value,
        } and asset_request.request_status != CommercialOperationAssetRequestStatus.APPROVED.value:
            raise ValueError("Only approved asset requests can be prepared or failed")
        now = datetime.now(UTC)
        asset_request.request_status = status
        asset_request.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        asset_request.result_summary = result_summary.strip() if result_summary and result_summary.strip() else None
        asset_request.failure_reason = failure_reason.strip() if failure_reason and failure_reason.strip() else None
        asset_request.updated_by = actor_user_id
        if status == CommercialOperationAssetRequestStatus.APPROVED.value:
            asset_request.approved_by = actor_user_id
            asset_request.approved_at = now
            asset_request.rejected_at = None
            asset_request.prepared_at = None
            asset_request.failed_at = None
            asset_request.archived_at = None
        elif status == CommercialOperationAssetRequestStatus.REJECTED.value:
            asset_request.rejected_at = now
            asset_request.approved_by = None
            asset_request.prepared_by = None
            asset_request.approved_at = None
            asset_request.prepared_at = None
            asset_request.failed_at = None
            asset_request.archived_at = None
        elif status == CommercialOperationAssetRequestStatus.READY_FOR_REVIEW.value:
            asset_request.approved_by = None
            asset_request.prepared_by = None
            asset_request.approved_at = None
            asset_request.rejected_at = None
            asset_request.prepared_at = None
            asset_request.failed_at = None
            asset_request.archived_at = None
        elif status == CommercialOperationAssetRequestStatus.PREPARED.value:
            asset_request.prepared_by = actor_user_id
            asset_request.prepared_at = now
            asset_request.failed_at = None
            asset_request.archived_at = None
        elif status == CommercialOperationAssetRequestStatus.FAILED.value:
            asset_request.failed_at = now
            asset_request.prepared_by = None
            asset_request.prepared_at = None
            asset_request.archived_at = None
        elif status == CommercialOperationAssetRequestStatus.ARCHIVED.value:
            asset_request.archived_at = now
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        asset_request.handoff_payload = self._build_asset_handoff_payload(
            operation=operation,
            asset_request=asset_request,
        )
        self._apply_asset_request_to_plan(operation, asset_request)
        await self.session.commit()
        await self.session.refresh(asset_request)
        return asset_request

    async def _decide_comfyui_handoff(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        handoff_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
        result_summary: str | None,
        failure_reason: str | None,
    ) -> CommercialOperationComfyUIHandoff:
        handoff = await self.require_comfyui_handoff(
            workspace_id=workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
        )
        if handoff.handoff_status == CommercialOperationComfyUIHandoffStatus.ARCHIVED.value:
            raise ValueError("Archived ComfyUI handoffs cannot be changed")
        if status == CommercialOperationComfyUIHandoffStatus.READY_FOR_REVIEW.value and handoff.handoff_status not in {
            CommercialOperationComfyUIHandoffStatus.DRAFT.value,
            CommercialOperationComfyUIHandoffStatus.REJECTED.value,
            CommercialOperationComfyUIHandoffStatus.FAILED.value,
        }:
            raise ValueError("Only draft, rejected, or failed ComfyUI handoffs can be marked ready")
        if status in {
            CommercialOperationComfyUIHandoffStatus.APPROVED.value,
            CommercialOperationComfyUIHandoffStatus.REJECTED.value,
        } and handoff.handoff_status != CommercialOperationComfyUIHandoffStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready ComfyUI handoffs can be approved or rejected")
        if status in {
            CommercialOperationComfyUIHandoffStatus.PREPARED.value,
            CommercialOperationComfyUIHandoffStatus.FAILED.value,
        } and handoff.handoff_status != CommercialOperationComfyUIHandoffStatus.APPROVED.value:
            raise ValueError("Only approved ComfyUI handoffs can be prepared or failed")
        now = datetime.now(UTC)
        handoff.handoff_status = status
        handoff.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        handoff.result_summary = result_summary.strip() if result_summary and result_summary.strip() else None
        handoff.failure_reason = failure_reason.strip() if failure_reason and failure_reason.strip() else None
        handoff.updated_by = actor_user_id
        if status == CommercialOperationComfyUIHandoffStatus.APPROVED.value:
            handoff.approved_by = actor_user_id
            handoff.approved_at = now
            handoff.rejected_at = None
            handoff.prepared_at = None
            handoff.failed_at = None
            handoff.archived_at = None
        elif status == CommercialOperationComfyUIHandoffStatus.REJECTED.value:
            handoff.rejected_at = now
            handoff.approved_by = None
            handoff.prepared_by = None
            handoff.approved_at = None
            handoff.prepared_at = None
            handoff.failed_at = None
            handoff.archived_at = None
        elif status == CommercialOperationComfyUIHandoffStatus.READY_FOR_REVIEW.value:
            handoff.approved_by = None
            handoff.prepared_by = None
            handoff.approved_at = None
            handoff.rejected_at = None
            handoff.prepared_at = None
            handoff.failed_at = None
            handoff.archived_at = None
        elif status == CommercialOperationComfyUIHandoffStatus.PREPARED.value:
            handoff.prepared_by = actor_user_id
            handoff.prepared_at = now
            handoff.failed_at = None
            handoff.archived_at = None
        elif status == CommercialOperationComfyUIHandoffStatus.FAILED.value:
            handoff.failed_at = now
            handoff.prepared_by = None
            handoff.prepared_at = None
            handoff.archived_at = None
        elif status == CommercialOperationComfyUIHandoffStatus.ARCHIVED.value:
            handoff.archived_at = now
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        asset_request = await self.require_asset_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            asset_request_id=handoff.asset_request_id,
        )
        handoff.handoff_payload = self._build_comfyui_handoff_payload(
            operation=operation,
            asset_request=asset_request,
            handoff=handoff,
        )
        self._apply_comfyui_handoff_to_plan(operation, handoff)
        await self.session.commit()
        await self.session.refresh(handoff)
        return handoff

    async def _decide_deliverable(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
        result_summary: str | None,
        failure_reason: str | None,
    ) -> CommercialOperationDeliverable:
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
        )
        if deliverable.deliverable_status == CommercialOperationDeliverableStatus.ARCHIVED.value:
            raise ValueError("Archived deliverables cannot be changed")
        if status == CommercialOperationDeliverableStatus.READY_FOR_REVIEW.value and deliverable.deliverable_status not in {
            CommercialOperationDeliverableStatus.DRAFT.value,
            CommercialOperationDeliverableStatus.REJECTED.value,
            CommercialOperationDeliverableStatus.FAILED.value,
        }:
            raise ValueError("Only draft, rejected, or failed deliverables can be marked ready")
        if status in {
            CommercialOperationDeliverableStatus.APPROVED.value,
            CommercialOperationDeliverableStatus.REJECTED.value,
        } and deliverable.deliverable_status != CommercialOperationDeliverableStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready deliverables can be approved or rejected")
        if status in {
            CommercialOperationDeliverableStatus.PACKAGED.value,
            CommercialOperationDeliverableStatus.FAILED.value,
        } and deliverable.deliverable_status != CommercialOperationDeliverableStatus.APPROVED.value:
            raise ValueError("Only approved deliverables can be packaged or failed")
        now = datetime.now(UTC)
        deliverable.deliverable_status = status
        deliverable.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        deliverable.result_summary = result_summary.strip() if result_summary and result_summary.strip() else None
        deliverable.failure_reason = failure_reason.strip() if failure_reason and failure_reason.strip() else None
        deliverable.updated_by = actor_user_id
        if status == CommercialOperationDeliverableStatus.APPROVED.value:
            deliverable.approved_by = actor_user_id
            deliverable.approved_at = now
            deliverable.rejected_at = None
            deliverable.packaged_at = None
            deliverable.failed_at = None
            deliverable.archived_at = None
        elif status == CommercialOperationDeliverableStatus.REJECTED.value:
            deliverable.rejected_at = now
            deliverable.approved_by = None
            deliverable.packaged_by = None
            deliverable.approved_at = None
            deliverable.packaged_at = None
            deliverable.failed_at = None
            deliverable.archived_at = None
        elif status == CommercialOperationDeliverableStatus.READY_FOR_REVIEW.value:
            deliverable.approved_by = None
            deliverable.packaged_by = None
            deliverable.approved_at = None
            deliverable.rejected_at = None
            deliverable.packaged_at = None
            deliverable.failed_at = None
            deliverable.archived_at = None
        elif status == CommercialOperationDeliverableStatus.PACKAGED.value:
            deliverable.packaged_by = actor_user_id
            deliverable.packaged_at = now
            deliverable.failed_at = None
            deliverable.archived_at = None
        elif status == CommercialOperationDeliverableStatus.FAILED.value:
            deliverable.failed_at = now
            deliverable.packaged_by = None
            deliverable.packaged_at = None
            deliverable.archived_at = None
        elif status == CommercialOperationDeliverableStatus.ARCHIVED.value:
            deliverable.archived_at = now
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        draft = await self.require_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=deliverable.content_draft_id,
        )
        asset_requests = await self._require_deliverable_asset_requests(
            workspace_id=workspace_id,
            operation_id=operation_id,
            content_draft_id=deliverable.content_draft_id,
            asset_request_ids=[UUID(item) for item in deliverable.asset_request_ids],
        )
        deliverable.package_payload = self._build_deliverable_package_payload(
            operation=operation,
            draft=draft,
            asset_requests=asset_requests,
            deliverable=deliverable,
        )
        if deliverable.output_artifact_id is not None:
            artifact = await OutputArtifactService(self.session).require_artifact(
                workspace_id=workspace_id,
                artifact_id=deliverable.output_artifact_id,
            )
            artifact.artifact_stage = (
                OutputArtifactStage.PACKAGED.value
                if status == CommercialOperationDeliverableStatus.PACKAGED.value
                else OutputArtifactStage.PROCESSED.value
            )
            artifact.artifact_metadata = self._build_deliverable_artifact_metadata(
                operation=operation,
                draft=draft,
                asset_requests=asset_requests,
                deliverable=deliverable,
            )
        self._apply_deliverable_to_plan(operation, deliverable)
        await self.session.commit()
        await self.session.refresh(deliverable)
        return deliverable

    async def _decide_evidence_snapshot(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        snapshot_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
    ) -> CommercialOperationEvidenceSnapshot:
        snapshot = await self.require_evidence_snapshot(
            workspace_id=workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
        )
        if snapshot.snapshot_status == CommercialOperationEvidenceSnapshotStatus.ARCHIVED.value:
            raise ValueError("Archived evidence snapshots cannot be changed")
        if status == CommercialOperationEvidenceSnapshotStatus.READY_FOR_REVIEW.value and snapshot.snapshot_status not in {
            CommercialOperationEvidenceSnapshotStatus.DRAFT.value,
            CommercialOperationEvidenceSnapshotStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected evidence snapshots can be marked ready")
        if status in {
            CommercialOperationEvidenceSnapshotStatus.APPROVED.value,
            CommercialOperationEvidenceSnapshotStatus.REJECTED.value,
        } and snapshot.snapshot_status != CommercialOperationEvidenceSnapshotStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready evidence snapshots can be approved or rejected")

        now = datetime.now(UTC)
        snapshot.snapshot_status = status
        snapshot.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        snapshot.updated_by = actor_user_id
        if status == CommercialOperationEvidenceSnapshotStatus.APPROVED.value:
            snapshot.approved_by = actor_user_id
            snapshot.approved_at = now
            snapshot.rejected_at = None
            snapshot.archived_at = None
        elif status == CommercialOperationEvidenceSnapshotStatus.REJECTED.value:
            snapshot.rejected_at = now
            snapshot.approved_by = None
            snapshot.approved_at = None
            snapshot.archived_at = None
        elif status == CommercialOperationEvidenceSnapshotStatus.READY_FOR_REVIEW.value:
            snapshot.approved_by = None
            snapshot.approved_at = None
            snapshot.rejected_at = None
            snapshot.archived_at = None
        elif status == CommercialOperationEvidenceSnapshotStatus.ARCHIVED.value:
            snapshot.archived_at = now

        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=snapshot.deliverable_id,
        )
        snapshot.snapshot_payload = {
            **(snapshot.snapshot_payload or {}),
            **self._build_evidence_snapshot_payload(
                operation=operation,
                deliverable=deliverable,
                snapshot=snapshot,
            ),
        }
        self._apply_evidence_snapshot_to_deliverable(deliverable, snapshot)
        self._apply_evidence_snapshot_to_plan(operation, snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot

    async def _decide_execution_request(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_request_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
        result_summary: str | None,
        failure_reason: str | None,
    ) -> CommercialOperationExecutionRequest:
        request = await self.require_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
        )
        if request.request_status == CommercialOperationExecutionRequestStatus.ARCHIVED.value:
            raise ValueError("Archived execution requests cannot be changed")
        if status == CommercialOperationExecutionRequestStatus.READY_FOR_REVIEW.value and request.request_status not in {
            CommercialOperationExecutionRequestStatus.DRAFT.value,
            CommercialOperationExecutionRequestStatus.REJECTED.value,
            CommercialOperationExecutionRequestStatus.FAILED.value,
        }:
            raise ValueError("Only draft, rejected, or failed execution requests can be marked ready")
        if status in {
            CommercialOperationExecutionRequestStatus.APPROVED.value,
            CommercialOperationExecutionRequestStatus.REJECTED.value,
        } and request.request_status != CommercialOperationExecutionRequestStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready execution requests can be approved or rejected")
        if status in {
            CommercialOperationExecutionRequestStatus.PREPARED.value,
            CommercialOperationExecutionRequestStatus.FAILED.value,
        } and request.request_status != CommercialOperationExecutionRequestStatus.APPROVED.value:
            raise ValueError("Only approved execution requests can be prepared or failed")
        if status == CommercialOperationExecutionRequestStatus.CANCELLED.value and request.request_status in {
            CommercialOperationExecutionRequestStatus.PREPARED.value,
            CommercialOperationExecutionRequestStatus.CANCELLED.value,
            CommercialOperationExecutionRequestStatus.ARCHIVED.value,
        }:
            raise ValueError("Prepared, cancelled, or archived execution requests cannot be cancelled")
        now = datetime.now(UTC)
        request.request_status = status
        request.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        request.result_summary = result_summary.strip() if result_summary and result_summary.strip() else None
        request.failure_reason = failure_reason.strip() if failure_reason and failure_reason.strip() else None
        request.updated_by = actor_user_id
        if status == CommercialOperationExecutionRequestStatus.APPROVED.value:
            request.approved_by = actor_user_id
            request.approved_at = now
            request.rejected_at = None
            request.prepared_at = None
            request.failed_at = None
            request.cancelled_at = None
            request.archived_at = None
        elif status == CommercialOperationExecutionRequestStatus.REJECTED.value:
            request.rejected_at = now
            request.approved_by = None
            request.prepared_by = None
            request.cancelled_by = None
            request.approved_at = None
            request.prepared_at = None
            request.failed_at = None
            request.cancelled_at = None
            request.archived_at = None
        elif status == CommercialOperationExecutionRequestStatus.READY_FOR_REVIEW.value:
            request.approved_by = None
            request.prepared_by = None
            request.cancelled_by = None
            request.approved_at = None
            request.rejected_at = None
            request.prepared_at = None
            request.failed_at = None
            request.cancelled_at = None
            request.archived_at = None
        elif status == CommercialOperationExecutionRequestStatus.PREPARED.value:
            request.prepared_by = actor_user_id
            request.prepared_at = now
            request.failed_at = None
            request.cancelled_at = None
            request.archived_at = None
        elif status == CommercialOperationExecutionRequestStatus.FAILED.value:
            request.failed_at = now
            request.prepared_by = None
            request.prepared_at = None
            request.cancelled_at = None
            request.archived_at = None
        elif status == CommercialOperationExecutionRequestStatus.CANCELLED.value:
            request.cancelled_by = actor_user_id
            request.cancelled_at = now
            request.archived_at = None
        elif status == CommercialOperationExecutionRequestStatus.ARCHIVED.value:
            request.archived_at = now
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        deliverable = await self.require_deliverable(
            workspace_id=workspace_id,
            operation_id=operation_id,
            deliverable_id=request.deliverable_id,
        )
        request.handoff_payload = self._build_execution_request_handoff_payload(
            operation=operation,
            deliverable=deliverable,
            execution_request=request,
        )
        self._apply_execution_request_to_plan(operation, request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def _decide_execution_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        execution_run_id: UUID,
        status: str,
        actor_user_id: str | None,
        result_summary: str | None,
        failure_reason: str | None,
        operator_notes: str | None,
        result_payload: dict[str, Any] | None,
    ) -> CommercialOperationExecutionRun:
        run = await self.require_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
        )
        if run.run_status == CommercialOperationExecutionRunStatus.ARCHIVED.value:
            raise ValueError("Archived execution runs cannot be changed")
        if status == CommercialOperationExecutionRunStatus.RUNNING.value and run.run_status not in {
            CommercialOperationExecutionRunStatus.QUEUED.value,
            CommercialOperationExecutionRunStatus.RETRYING.value,
        }:
            raise ValueError("Only queued or retrying execution runs can be started")
        if status in {
            CommercialOperationExecutionRunStatus.SUCCEEDED.value,
            CommercialOperationExecutionRunStatus.FAILED.value,
        } and run.run_status != CommercialOperationExecutionRunStatus.RUNNING.value:
            raise ValueError("Only running execution runs can succeed or fail")
        if status == CommercialOperationExecutionRunStatus.RETRYING.value:
            if run.run_status != CommercialOperationExecutionRunStatus.FAILED.value:
                raise ValueError("Only failed execution runs can be retried")
            if run.retry_count >= run.max_retries:
                raise ValueError("Execution run retry limit reached")
        if status == CommercialOperationExecutionRunStatus.CANCELLED.value and run.run_status not in {
            CommercialOperationExecutionRunStatus.QUEUED.value,
            CommercialOperationExecutionRunStatus.RUNNING.value,
            CommercialOperationExecutionRunStatus.RETRYING.value,
        }:
            raise ValueError("Only queued, running, or retrying execution runs can be cancelled")

        now = datetime.now(UTC)
        run.run_status = status
        if operator_notes is not None:
            run.operator_notes = operator_notes.strip() if operator_notes.strip() else None
        if result_summary is not None:
            run.result_summary = result_summary.strip() if result_summary.strip() else None
        if failure_reason is not None:
            run.failure_reason = failure_reason.strip() if failure_reason.strip() else None
        if result_payload is not None:
            run.result_payload = result_payload or {}

        if status == CommercialOperationExecutionRunStatus.RUNNING.value:
            run.started_by = actor_user_id
            run.started_at = now
            run.cancelled_by = None
            run.completed_by = None
            run.completed_at = None
            run.cancelled_at = None
            run.archived_at = None
            if run.failed_at is not None:
                run.failed_at = None
        elif status == CommercialOperationExecutionRunStatus.SUCCEEDED.value:
            run.completed_by = actor_user_id
            run.completed_at = now
            run.failed_at = None
            run.cancelled_at = None
            run.archived_at = None
        elif status == CommercialOperationExecutionRunStatus.FAILED.value:
            run.failed_at = now
            run.completed_by = None
            run.completed_at = None
            run.cancelled_at = None
            run.archived_at = None
        elif status == CommercialOperationExecutionRunStatus.RETRYING.value:
            run.retry_count += 1
            run.cancelled_by = None
            run.cancelled_at = None
            run.archived_at = None
        elif status == CommercialOperationExecutionRunStatus.CANCELLED.value:
            run.cancelled_by = actor_user_id
            run.cancelled_at = now
            run.completed_by = None
            run.completed_at = None
            run.archived_at = None
        elif status == CommercialOperationExecutionRunStatus.ARCHIVED.value:
            run.archived_at = now

        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        request = await self.require_execution_request(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_request_id=run.execution_request_id,
        )
        run.runtime_payload = self._build_execution_run_runtime_payload(
            operation=operation,
            execution_request=request,
            execution_run=run,
        )
        run.recovery_plan = self._build_execution_run_recovery_plan(run)
        self._apply_execution_run_to_plan(operation, run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def _decide_result(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        result_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
    ) -> CommercialOperationResult:
        result = await self.require_result(workspace_id=workspace_id, operation_id=operation_id, result_id=result_id)
        if result.result_status == CommercialOperationResultStatus.ARCHIVED.value:
            raise ValueError("Archived result records cannot be changed")
        if status == CommercialOperationResultStatus.READY_FOR_REVIEW.value and result.result_status not in {
            CommercialOperationResultStatus.DRAFT.value,
            CommercialOperationResultStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected result records can be marked ready")
        if status in {
            CommercialOperationResultStatus.APPROVED.value,
            CommercialOperationResultStatus.REJECTED.value,
        } and result.result_status != CommercialOperationResultStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready result records can be approved or rejected")

        now = datetime.now(UTC)
        result.result_status = status
        result.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        result.updated_by = actor_user_id
        if status == CommercialOperationResultStatus.APPROVED.value:
            result.approved_by = actor_user_id
            result.approved_at = now
            result.rejected_at = None
            result.archived_at = None
        elif status == CommercialOperationResultStatus.REJECTED.value:
            result.rejected_at = now
            result.approved_by = None
            result.approved_at = None
            result.archived_at = None
        elif status == CommercialOperationResultStatus.READY_FOR_REVIEW.value:
            result.approved_by = None
            result.approved_at = None
            result.rejected_at = None
            result.archived_at = None
        elif status == CommercialOperationResultStatus.ARCHIVED.value:
            result.archived_at = now

        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        run = await self.require_execution_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            execution_run_id=result.execution_run_id,
        )
        result.recommendation_payload = self._build_result_recommendation_payload(
            operation=operation,
            execution_run=run,
            result=result,
        )
        self._apply_result_to_plan(operation, result)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def _decide_monitoring_observation(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        observation_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
    ) -> CommercialOperationMonitoringObservation:
        observation = await self.require_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
        )
        if observation.observation_status == CommercialOperationMonitoringObservationStatus.ARCHIVED.value:
            raise ValueError("Archived monitoring observations cannot be changed")
        if status == CommercialOperationMonitoringObservationStatus.READY_FOR_REVIEW.value and observation.observation_status not in {
            CommercialOperationMonitoringObservationStatus.DRAFT.value,
            CommercialOperationMonitoringObservationStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected monitoring observations can be marked ready")
        if status in {
            CommercialOperationMonitoringObservationStatus.APPROVED.value,
            CommercialOperationMonitoringObservationStatus.REJECTED.value,
        } and observation.observation_status != CommercialOperationMonitoringObservationStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready monitoring observations can be approved or rejected")

        now = datetime.now(UTC)
        observation.observation_status = status
        observation.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        observation.updated_by = actor_user_id
        if status == CommercialOperationMonitoringObservationStatus.APPROVED.value:
            observation.approved_by = actor_user_id
            observation.approved_at = now
            observation.rejected_at = None
            observation.archived_at = None
        elif status == CommercialOperationMonitoringObservationStatus.REJECTED.value:
            observation.rejected_at = now
            observation.approved_by = None
            observation.approved_at = None
            observation.archived_at = None
        elif status == CommercialOperationMonitoringObservationStatus.READY_FOR_REVIEW.value:
            observation.approved_by = None
            observation.approved_at = None
            observation.rejected_at = None
            observation.archived_at = None
        elif status == CommercialOperationMonitoringObservationStatus.ARCHIVED.value:
            observation.archived_at = now

        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        result = await self.require_result(
            workspace_id=workspace_id,
            operation_id=operation_id,
            result_id=observation.result_id,
        )
        observation.observation_payload = {
            **(observation.observation_payload or {}),
            **self._build_monitoring_observation_payload(
                operation=operation,
                result=result,
                observation=observation,
            ),
        }
        self._apply_monitoring_observation_to_plan(operation, observation)
        await self.session.commit()
        await self.session.refresh(observation)
        return observation

    async def _decide_optimization_decision(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        decision_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
    ) -> CommercialOperationOptimizationDecision:
        decision = await self.require_optimization_decision(
            workspace_id=workspace_id,
            operation_id=operation_id,
            decision_id=decision_id,
        )
        if decision.decision_status == CommercialOperationOptimizationDecisionStatus.ARCHIVED.value:
            raise ValueError("Archived optimization decisions cannot be changed")
        if status == CommercialOperationOptimizationDecisionStatus.READY_FOR_REVIEW.value and decision.decision_status not in {
            CommercialOperationOptimizationDecisionStatus.DRAFT.value,
            CommercialOperationOptimizationDecisionStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected optimization decisions can be marked ready")
        if status in {
            CommercialOperationOptimizationDecisionStatus.APPROVED.value,
            CommercialOperationOptimizationDecisionStatus.REJECTED.value,
        } and decision.decision_status != CommercialOperationOptimizationDecisionStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready optimization decisions can be approved or rejected")

        now = datetime.now(UTC)
        decision.decision_status = status
        decision.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        decision.updated_by = actor_user_id
        if status == CommercialOperationOptimizationDecisionStatus.APPROVED.value:
            decision.approved_by = actor_user_id
            decision.approved_at = now
            decision.rejected_at = None
            decision.archived_at = None
        elif status == CommercialOperationOptimizationDecisionStatus.REJECTED.value:
            decision.rejected_at = now
            decision.approved_by = None
            decision.approved_at = None
            decision.archived_at = None
        elif status == CommercialOperationOptimizationDecisionStatus.READY_FOR_REVIEW.value:
            decision.approved_by = None
            decision.approved_at = None
            decision.rejected_at = None
            decision.archived_at = None
        elif status == CommercialOperationOptimizationDecisionStatus.ARCHIVED.value:
            decision.archived_at = now

        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        observation = await self.require_monitoring_observation(
            workspace_id=workspace_id,
            operation_id=operation_id,
            observation_id=decision.observation_id,
        )
        decision.decision_payload = {
            **(decision.decision_payload or {}),
            **self._build_optimization_decision_payload(
                operation=operation,
                observation=observation,
                decision=decision,
            ),
        }
        self._apply_optimization_decision_to_plan(operation, decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def _decide_content_draft(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        draft_id: UUID,
        status: str,
        actor_user_id: str | None,
        reviewer_notes: str | None,
    ) -> CommercialOperationContentDraft:
        draft = await self.require_content_draft(
            workspace_id=workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
        )
        if draft.draft_status == CommercialOperationContentDraftStatus.ARCHIVED.value:
            raise ValueError("Archived content drafts cannot be changed")
        if status == CommercialOperationContentDraftStatus.READY_FOR_REVIEW.value and draft.draft_status not in {
            CommercialOperationContentDraftStatus.DRAFT.value,
            CommercialOperationContentDraftStatus.REJECTED.value,
        }:
            raise ValueError("Only draft or rejected content drafts can be marked ready")
        if status in {
            CommercialOperationContentDraftStatus.APPROVED.value,
            CommercialOperationContentDraftStatus.REJECTED.value,
        } and draft.draft_status != CommercialOperationContentDraftStatus.READY_FOR_REVIEW.value:
            raise ValueError("Only ready content drafts can be approved or rejected")
        now = datetime.now(UTC)
        draft.draft_status = status
        draft.reviewer_notes = reviewer_notes.strip() if reviewer_notes and reviewer_notes.strip() else None
        draft.updated_by = actor_user_id
        if status == CommercialOperationContentDraftStatus.APPROVED.value:
            draft.approved_by = actor_user_id
            draft.approved_at = now
            draft.rejected_at = None
            draft.archived_at = None
        elif status == CommercialOperationContentDraftStatus.REJECTED.value:
            draft.rejected_at = now
            draft.approved_by = None
            draft.approved_at = None
            draft.archived_at = None
        elif status == CommercialOperationContentDraftStatus.READY_FOR_REVIEW.value:
            draft.approved_by = None
            draft.approved_at = None
            draft.rejected_at = None
            draft.archived_at = None
        elif status == CommercialOperationContentDraftStatus.ARCHIVED.value:
            draft.archived_at = now
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        self._apply_content_draft_to_plan(operation, draft)
        await self.session.commit()
        await self.session.refresh(draft)
        return draft

    async def _decide_dry_run(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        dry_run_id: UUID,
        status: str,
        completed_by: str | None,
        result_summary: str | None,
        failure_reason: str | None,
    ) -> CommercialOperationDryRun:
        dry_run = await self.require_dry_run(
            workspace_id=workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
        )
        if dry_run.dry_run_status != CommercialOperationDryRunStatus.CREATED.value:
            raise ValueError("Only created dry-runs can be completed, failed, or cancelled")
        now = datetime.now(UTC)
        dry_run.dry_run_status = status
        dry_run.completed_by = completed_by
        dry_run.result_summary = result_summary.strip() if result_summary and result_summary.strip() else None
        dry_run.failure_reason = failure_reason.strip() if failure_reason and failure_reason.strip() else None
        if status == CommercialOperationDryRunStatus.COMPLETED.value:
            dry_run.completed_at = now
        elif status == CommercialOperationDryRunStatus.FAILED.value:
            dry_run.failed_at = now
        elif status == CommercialOperationDryRunStatus.CANCELLED.value:
            dry_run.cancelled_at = now
        operation = await self.require_operation(workspace_id=workspace_id, operation_id=operation_id)
        self._apply_dry_run_to_plan(operation, dry_run)
        await self.session.commit()
        await self.session.refresh(dry_run)
        return dry_run

    def _build_dry_run_runbook(
        self,
        *,
        operation: CommercialOperation,
        approval: CommercialOperationApproval,
        step_key: str,
        execution_mode: str,
        execution_target: str | None,
        readiness_checks: list[str],
    ) -> list[dict[str, Any]]:
        target = execution_target.strip() if execution_target and execution_target.strip() else "operator-selected target"
        return [
            {
                "step_key": "confirm_approval",
                "title": "Confirm approved human gate",
                "status": "planned",
                "approval_id": str(approval.id),
                "approval_step_key": approval.step_key,
                "approval_status": approval.approval_status,
            },
            {
                "step_key": "prepare_payload",
                "title": "Prepare metadata-only execution payload",
                "status": "planned",
                "operation_id": str(operation.id),
                "operation_title": operation.title,
                "dry_run_step_key": step_key,
                "execution_mode": execution_mode,
                "execution_target": target,
            },
            {
                "step_key": "readiness_checks",
                "title": "Review readiness checks without external execution",
                "status": "planned",
                "checks": readiness_checks,
            },
            {
                "step_key": "operator_result",
                "title": "Record dry-run result for handoff",
                "status": "planned",
                "non_goals": ["no publish", "no real account control", "no OpenClaw action", "no ComfyUI job"],
            },
        ]

    def _build_content_draft_body(
        self,
        *,
        operation: CommercialOperation,
        channel: str,
        content_format: str,
        summary: str | None,
        call_to_action: str | None,
    ) -> str:
        audience = operation.target_audience or "target audience"
        metrics = ", ".join(operation.success_metrics or ["reviewed content output"])
        constraints = ", ".join(operation.constraints or ["human review before execution"])
        lines = [
            f"Channel: {channel}",
            f"Format: {content_format}",
            f"Audience: {audience}",
            f"Objective: {operation.objective}",
            f"Success metric focus: {metrics}",
            f"Constraints: {constraints}",
        ]
        if summary:
            lines.append(f"Draft summary: {summary}")
        if call_to_action:
            lines.append(f"Call to action: {call_to_action}")
        lines.append("Boundary: this is a draft only; it does not publish or control external accounts.")
        return "\n".join(lines)

    def _build_asset_handoff_payload(
        self,
        *,
        operation: CommercialOperation,
        asset_request: CommercialOperationAssetRequest,
    ) -> dict[str, Any]:
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "content_draft_id": str(asset_request.content_draft_id) if asset_request.content_draft_id else None,
            "step_key": asset_request.step_key,
            "channel": asset_request.channel,
            "asset_type": asset_request.asset_type,
            "title": asset_request.title,
            "purpose": asset_request.purpose,
            "dimensions": asset_request.dimensions,
            "generation_prompt": asset_request.generation_prompt,
            "negative_prompt": asset_request.negative_prompt,
            "source_materials": asset_request.source_materials,
            "readiness_checks": asset_request.readiness_checks,
            "request_status": asset_request.request_status,
            "execution_boundary": "no ComfyUI job is created in this phase",
            "next_runtime": "future_comfyui_handoff",
        }

    def _build_comfyui_handoff_payload(
        self,
        *,
        operation: CommercialOperation,
        asset_request: CommercialOperationAssetRequest,
        handoff: CommercialOperationComfyUIHandoff,
    ) -> dict[str, Any]:
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "asset_request_id": str(asset_request.id),
            "content_draft_id": str(handoff.content_draft_id) if handoff.content_draft_id else None,
            "step_key": handoff.step_key,
            "channel": handoff.channel,
            "asset_type": handoff.asset_type,
            "title": handoff.title,
            "workflow_name": handoff.workflow_name,
            "dimensions": handoff.dimensions,
            "generation_prompt": handoff.generation_prompt,
            "negative_prompt": handoff.negative_prompt,
            "source_materials": handoff.source_materials,
            "readiness_checks": handoff.readiness_checks,
            "prompt_payload": handoff.prompt_payload,
            "workflow_payload": handoff.workflow_payload,
            "handoff_status": handoff.handoff_status,
            "execution_boundary": "metadata-only ComfyUI handoff; no ComfyUI job is submitted in this phase",
            "next_runtime": "future_guarded_comfyui_adapter",
            "forbidden_actions": [
                "no ComfyUI job submission",
                "no image/video generation",
                "no publishing",
                "no account control",
                "no OpenClaw or browser worker execution",
                "no approval bypass",
            ],
        }

    async def _require_deliverable_asset_requests(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        content_draft_id: UUID,
        asset_request_ids: list[UUID],
    ) -> list[CommercialOperationAssetRequest]:
        seen: set[UUID] = set()
        requests: list[CommercialOperationAssetRequest] = []
        for asset_request_id in asset_request_ids:
            if asset_request_id in seen:
                continue
            seen.add(asset_request_id)
            asset_request = await self.require_asset_request(
                workspace_id=workspace_id,
                operation_id=operation_id,
                asset_request_id=asset_request_id,
            )
            if asset_request.request_status not in {
                CommercialOperationAssetRequestStatus.APPROVED.value,
                CommercialOperationAssetRequestStatus.PREPARED.value,
            }:
                raise ValueError("Deliverable asset requests must be approved or prepared")
            if asset_request.content_draft_id is not None and asset_request.content_draft_id != content_draft_id:
                raise ValueError("Deliverable asset requests must belong to the same content draft")
            requests.append(asset_request)
        return requests

    async def _resolve_execution_evidence_snapshots(
        self,
        *,
        workspace_id: str,
        operation_id: UUID,
        deliverable_id: UUID,
        snapshot_ids: list[UUID] | None,
    ) -> list[CommercialOperationEvidenceSnapshot]:
        if snapshot_ids:
            seen: set[UUID] = set()
            snapshots: list[CommercialOperationEvidenceSnapshot] = []
            for snapshot_id in snapshot_ids:
                if isinstance(snapshot_id, str):
                    snapshot_id = UUID(snapshot_id)
                if snapshot_id in seen:
                    continue
                seen.add(snapshot_id)
                snapshot = await self.require_evidence_snapshot(
                    workspace_id=workspace_id,
                    operation_id=operation_id,
                    snapshot_id=snapshot_id,
                )
                if snapshot.deliverable_id != deliverable_id:
                    raise ValueError("Evidence snapshots must belong to the execution request deliverable")
                if snapshot.snapshot_status != CommercialOperationEvidenceSnapshotStatus.APPROVED.value:
                    raise ValueError("Execution requests can only include approved evidence snapshots")
                snapshots.append(snapshot)
            return snapshots
        result = await self.session.execute(
            select(CommercialOperationEvidenceSnapshot).where(
                CommercialOperationEvidenceSnapshot.workspace_id == workspace_id,
                CommercialOperationEvidenceSnapshot.operation_id == operation_id,
                CommercialOperationEvidenceSnapshot.deliverable_id == deliverable_id,
                CommercialOperationEvidenceSnapshot.snapshot_status
                == CommercialOperationEvidenceSnapshotStatus.APPROVED.value,
            )
        )
        return list(result.scalars().all())

    def _build_deliverable_artifact_content(
        self,
        *,
        operation: CommercialOperation,
        draft: CommercialOperationContentDraft,
        asset_requests: list[CommercialOperationAssetRequest],
        deliverable: CommercialOperationDeliverable,
    ) -> str:
        asset_lines = [
            f"- {asset.title} ({asset.asset_type}, {asset.request_status})"
            for asset in asset_requests
        ] or ["- No linked asset requests"]
        checks = [f"- {check}" for check in deliverable.quality_checks] or ["- Operator review required"]
        lines = [
            f"# {deliverable.title}",
            "",
            f"Operation: {operation.title}",
            f"Objective: {operation.objective}",
            f"Channel: {deliverable.channel}",
            f"Deliverable type: {deliverable.deliverable_type}",
            f"Status: {deliverable.deliverable_status}",
            "",
            "## Summary",
            deliverable.summary or draft.summary or "No summary provided.",
            "",
            "## Approved Content",
            draft.content_body,
            "",
            "## Linked Asset Requests",
            *asset_lines,
            "",
            "## Quality Checks",
            *checks,
            "",
            "## Boundary",
            "This deliverable is an Output Library artifact for operator handoff only. It does not publish, control accounts, start ComfyUI, run OpenClaw, or call browser workers.",
        ]
        if draft.call_to_action:
            lines.insert(10, f"Call to action: {draft.call_to_action}")
        if deliverable.delivery_notes:
            lines.extend(["", "## Delivery Notes", deliverable.delivery_notes])
        return "\n".join(lines)

    def _build_deliverable_artifact_metadata(
        self,
        *,
        operation: CommercialOperation,
        draft: CommercialOperationContentDraft,
        asset_requests: list[CommercialOperationAssetRequest],
        deliverable: CommercialOperationDeliverable,
    ) -> dict[str, Any]:
        return {
            "commercial_operation_id": str(operation.id),
            "commercial_operation_title": operation.title,
            "commercial_deliverable_id": str(deliverable.id),
            "content_draft_id": str(draft.id),
            "asset_request_ids": [str(asset.id) for asset in asset_requests],
            "channel": deliverable.channel,
            "deliverable_type": deliverable.deliverable_type,
            "deliverable_status": deliverable.deliverable_status,
            "execution_boundary": "no publish, no real account control, no ComfyUI job, no OpenClaw action, no browser worker action",
            "phase": "61G",
        }

    def _build_deliverable_package_payload(
        self,
        *,
        operation: CommercialOperation,
        draft: CommercialOperationContentDraft,
        asset_requests: list[CommercialOperationAssetRequest],
        deliverable: CommercialOperationDeliverable,
    ) -> dict[str, Any]:
        existing_snapshots = [
            dict(item)
            for item in (deliverable.package_payload or {}).get("evidence_snapshots", [])
            if isinstance(item, dict)
        ]
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "content_draft_id": str(draft.id),
            "output_artifact_id": str(deliverable.output_artifact_id) if deliverable.output_artifact_id else None,
            "step_key": deliverable.step_key,
            "channel": deliverable.channel,
            "deliverable_type": deliverable.deliverable_type,
            "deliverable_status": deliverable.deliverable_status,
            "asset_requests": [
                {
                    "asset_request_id": str(asset.id),
                    "title": asset.title,
                    "asset_type": asset.asset_type,
                    "request_status": asset.request_status,
                    "handoff_payload": asset.handoff_payload,
                }
                for asset in asset_requests
            ],
            "quality_checks": deliverable.quality_checks,
            "evidence_snapshots": existing_snapshots,
            "evidence_snapshot_count": len(existing_snapshots),
            "execution_boundary": "metadata-only deliverable assembly; no publishing or external runtime execution",
            "next_runtime": "future_monitored_execution_request",
        }

    def _build_evidence_snapshot_payload(
        self,
        *,
        operation: CommercialOperation,
        deliverable: CommercialOperationDeliverable,
        snapshot: CommercialOperationEvidenceSnapshot,
    ) -> dict[str, Any]:
        existing_payload = snapshot.snapshot_payload or {}
        generated_from_rag = existing_payload.get("generation_mode") == "rag_search_snapshot"
        if generated_from_rag:
            operator_next_steps = [
                "review retrieved chunks and source documents before execution handoff",
                "approve this snapshot before it can be attached to an execution request",
                "regenerate the snapshot if the knowledge collection or query changes",
            ]
            non_goals = [
                "does not ingest new knowledge files",
                "does not auto-approve retrieved evidence",
                "does not publish, control accounts, or call external runtimes",
            ]
        else:
            operator_next_steps = [
                "review source documents and evidence links before execution handoff",
                "approve this snapshot before it can be attached to an execution request",
                "refresh the snapshot manually if the knowledge collection changes",
            ]
            non_goals = [
                "does not run live RAG retrieval",
                "does not ingest new knowledge files",
                "does not publish, control accounts, or call external runtimes",
            ]
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "deliverable_id": str(deliverable.id),
            "output_artifact_id": str(deliverable.output_artifact_id) if deliverable.output_artifact_id else None,
            "evidence_snapshot_id": str(snapshot.id) if snapshot.id else None,
            "snapshot_status": snapshot.snapshot_status,
            "evidence_type": snapshot.evidence_type,
            "knowledge_collection": snapshot.knowledge_collection,
            "source_document_count": len(snapshot.source_document_ids or []),
            "source_link_count": len(snapshot.source_links or []),
            "evidence_item_count": len(snapshot.evidence_items or []),
            "coverage_checks": snapshot.coverage_checks,
            "operator_next_steps": operator_next_steps,
            "non_goals": non_goals,
        }

    def _build_operator_checklist(
        self,
        *,
        deliverable: CommercialOperationDeliverable,
        evidence_snapshots: list[CommercialOperationEvidenceSnapshot],
    ) -> list[dict[str, Any]]:
        checklist = [
            {
                "order": 1,
                "item": "confirm packaged deliverable is approved for the target channel",
                "status": "pending",
                "reference_id": str(deliverable.id),
                "execution_boundary": "operator checklist only; no external runtime call",
            },
            {
                "order": 2,
                "item": "confirm target account, platform, and owner before any future runtime handoff",
                "status": "pending",
                "execution_boundary": "operator checklist only; no external runtime call",
            },
            {
                "order": 3,
                "item": "confirm an approval gate exists before real publishing or account control",
                "status": "pending",
                "execution_boundary": "operator checklist only; no external runtime call",
            },
        ]
        if evidence_snapshots:
            checklist.insert(
                1,
                {
                    "order": 2,
                    "item": "review approved evidence snapshots and source coverage",
                    "status": "pending",
                    "evidence_snapshot_ids": [str(snapshot.id) for snapshot in evidence_snapshots],
                    "execution_boundary": "operator checklist only; no external runtime call",
                },
            )
            for index, item in enumerate(checklist, start=1):
                item["order"] = index
        return checklist

    def _build_execution_request_handoff_payload(
        self,
        *,
        operation: CommercialOperation,
        deliverable: CommercialOperationDeliverable,
        execution_request: CommercialOperationExecutionRequest,
    ) -> dict[str, Any]:
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "deliverable_id": str(deliverable.id),
            "output_artifact_id": str(deliverable.output_artifact_id) if deliverable.output_artifact_id else None,
            "execution_request_id": str(execution_request.id),
            "step_key": execution_request.step_key,
            "channel": execution_request.channel,
            "execution_type": execution_request.execution_type,
            "execution_mode": execution_request.execution_mode,
            "request_status": execution_request.request_status,
            "execution_target": execution_request.execution_target,
            "input_summary": execution_request.input_summary,
            "runbook": execution_request.runbook,
            "readiness_checks": execution_request.readiness_checks,
            "expected_outputs": execution_request.expected_outputs,
            "evidence_snapshot_ids": execution_request.evidence_snapshot_ids,
            "operator_checklist": execution_request.operator_checklist,
            "execution_boundary": "metadata-only execution request; no external runtime call",
            "next_runtime": "future_guarded_runtime_adapter",
            "forbidden_actions": [
                "no publishing",
                "no real account control",
                "no ComfyUI job",
                "no OpenClaw action",
                "no browser worker action",
            ],
        }

    def _build_execution_run_runtime_payload(
        self,
        *,
        operation: CommercialOperation,
        execution_request: CommercialOperationExecutionRequest,
        execution_run: CommercialOperationExecutionRun,
    ) -> dict[str, Any]:
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "execution_request_id": str(execution_request.id),
            "execution_run_id": str(execution_run.id) if execution_run.id else None,
            "deliverable_id": str(execution_run.deliverable_id),
            "output_artifact_id": str(execution_run.output_artifact_id) if execution_run.output_artifact_id else None,
            "step_key": execution_run.step_key,
            "channel": execution_run.channel,
            "execution_type": execution_run.execution_type,
            "execution_mode": execution_run.execution_mode,
            "execution_target": execution_run.execution_target,
            "run_status": execution_run.run_status,
            "input_payload": execution_run.input_payload,
            "request_handoff_payload": execution_request.handoff_payload,
            "runbook_snapshot": execution_run.runbook_snapshot,
            "readiness_checks": execution_run.readiness_checks,
            "expected_outputs": execution_run.expected_outputs,
            "evidence_snapshot_ids": execution_run.evidence_snapshot_ids,
            "operator_checklist_snapshot": execution_run.operator_checklist_snapshot,
            "execution_boundary": "metadata-only execution run; no external runtime call",
            "next_runtime": "future_guarded_runtime_adapter",
            "forbidden_actions": [
                "no publishing",
                "no real account control",
                "no ComfyUI job",
                "no OpenClaw action",
                "no browser worker action",
            ],
        }

    def _build_execution_run_recovery_plan(
        self,
        execution_run: CommercialOperationExecutionRun,
    ) -> dict[str, Any]:
        can_retry = (
            execution_run.run_status == CommercialOperationExecutionRunStatus.FAILED.value
            and execution_run.retry_count < execution_run.max_retries
        )
        return {
            "retry_count": execution_run.retry_count,
            "max_retries": execution_run.max_retries,
            "can_retry": can_retry,
            "retry_remaining": max(execution_run.max_retries - execution_run.retry_count, 0),
            "operator_actions": [
                "review failure reason and result payload",
                "adjust input payload, execution target, or operator notes if needed",
                "retry only after human approval",
            ],
            "non_goals": [
                "does not auto-publish",
                "does not control real accounts",
                "does not call ComfyUI, OpenClaw, or browser workers",
            ],
        }

    def _build_result_recommendation_payload(
        self,
        *,
        operation: CommercialOperation,
        execution_run: CommercialOperationExecutionRun,
        result: CommercialOperationResult,
    ) -> dict[str, Any]:
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "execution_run_id": str(execution_run.id),
            "execution_run_status": execution_run.run_status,
            "result_id": str(result.id) if result.id else None,
            "result_status": result.result_status,
            "result_type": result.result_type,
            "channel": result.channel,
            "observed_metric_count": len(result.observed_metrics or []),
            "commercial_signal_count": len(result.commercial_signals or []),
            "operator_next_steps": [
                "review linked evidence and observed metrics",
                "compare outcome against the original success metrics",
                "decide whether to iterate content, assets, targeting, or the execution handoff",
            ],
            "non_goals": [
                "does not ingest platform analytics automatically",
                "does not claim ROI attribution",
                "does not publish, control accounts, or call external runtimes",
            ],
        }

    def _build_monitoring_observation_payload(
        self,
        *,
        operation: CommercialOperation,
        result: CommercialOperationResult,
        observation: CommercialOperationMonitoringObservation,
    ) -> dict[str, Any]:
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "result_id": str(result.id),
            "result_status": result.result_status,
            "observation_id": str(observation.id) if observation.id else None,
            "observation_status": observation.observation_status,
            "observation_type": observation.observation_type,
            "channel": observation.channel,
            "metric_snapshot_count": len(observation.metric_snapshots or []),
            "qualitative_signal_count": len(observation.qualitative_signals or []),
            "anomaly_count": len(observation.anomaly_flags or []),
            "operator_next_steps": [
                "review metric snapshots and evidence with the operation owner",
                "compare monitoring signals against approved result expectations",
                "decide whether to iterate content, assets, target audience, or execution handoff",
            ],
            "non_goals": [
                "does not ingest platform analytics automatically",
                "does not claim ROI attribution",
                "does not publish, control accounts, or call external runtimes",
            ],
        }

    def _build_optimization_decision_payload(
        self,
        *,
        operation: CommercialOperation,
        observation: CommercialOperationMonitoringObservation,
        decision: CommercialOperationOptimizationDecision,
    ) -> dict[str, Any]:
        return {
            "operation_id": str(operation.id),
            "operation_title": operation.title,
            "observation_id": str(observation.id),
            "observation_status": observation.observation_status,
            "decision_id": str(decision.id) if decision.id else None,
            "decision_status": decision.decision_status,
            "decision_type": decision.decision_type,
            "priority": decision.priority,
            "channel": decision.channel,
            "objective_update_count": len(decision.objective_updates or []),
            "content_action_count": len(decision.content_actions or []),
            "asset_action_count": len(decision.asset_actions or []),
            "audience_action_count": len(decision.audience_actions or []),
            "execution_action_count": len(decision.execution_actions or []),
            "risk_control_count": len(decision.risk_controls or []),
            "operator_next_steps": [
                "review the approved monitoring observation before changing the operation plan",
                "decide which content, asset, audience, or execution handoff should be adjusted",
                "create a separate approved record before any future runtime or publishing action",
            ],
            "non_goals": [
                "does not auto-optimize content, assets, audiences, or budgets",
                "does not publish, control accounts, or call external runtimes",
                "does not ingest platform analytics automatically or claim ROI attribution",
            ],
        }

    def _apply_content_draft_to_plan(
        self,
        operation: CommercialOperation,
        draft: CommercialOperationContentDraft,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == draft.step_key:
                updated = dict(step)
                updated["content_draft_id"] = str(draft.id)
                updated["content_draft_status"] = draft.draft_status
                updated["content_draft_channel"] = draft.channel
                updated["content_draft_format"] = draft.content_format
                if draft.approved_at is not None:
                    updated["content_draft_decision_at"] = draft.approved_at.isoformat()
                elif draft.rejected_at is not None:
                    updated["content_draft_decision_at"] = draft.rejected_at.isoformat()
                elif draft.archived_at is not None:
                    updated["content_draft_decision_at"] = draft.archived_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_execution_request_to_plan(
        self,
        operation: CommercialOperation,
        execution_request: CommercialOperationExecutionRequest,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == execution_request.step_key:
                updated = dict(step)
                updated["execution_request_id"] = str(execution_request.id)
                updated["execution_request_status"] = execution_request.request_status
                updated["execution_request_type"] = execution_request.execution_type
                updated["execution_request_mode"] = execution_request.execution_mode
                updated["execution_request_evidence_snapshot_count"] = len(
                    execution_request.evidence_snapshot_ids or []
                )
                updated["execution_request_operator_check_count"] = len(execution_request.operator_checklist or [])
                if execution_request.execution_target:
                    updated["execution_request_target"] = execution_request.execution_target
                if execution_request.cancelled_at is not None:
                    updated["execution_request_decision_at"] = execution_request.cancelled_at.isoformat()
                elif execution_request.failed_at is not None:
                    updated["execution_request_decision_at"] = execution_request.failed_at.isoformat()
                elif execution_request.prepared_at is not None:
                    updated["execution_request_decision_at"] = execution_request.prepared_at.isoformat()
                elif execution_request.rejected_at is not None:
                    updated["execution_request_decision_at"] = execution_request.rejected_at.isoformat()
                elif execution_request.approved_at is not None:
                    updated["execution_request_decision_at"] = execution_request.approved_at.isoformat()
                elif execution_request.archived_at is not None:
                    updated["execution_request_decision_at"] = execution_request.archived_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_execution_run_to_plan(
        self,
        operation: CommercialOperation,
        execution_run: CommercialOperationExecutionRun,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == execution_run.step_key:
                updated = dict(step)
                updated["execution_run_id"] = str(execution_run.id)
                updated["execution_run_status"] = execution_run.run_status
                updated["execution_run_target"] = execution_run.execution_target
                updated["execution_run_retry_count"] = execution_run.retry_count
                updated["execution_run_evidence_snapshot_count"] = len(execution_run.evidence_snapshot_ids or [])
                updated["execution_run_operator_check_count"] = len(execution_run.operator_checklist_snapshot or [])
                if execution_run.archived_at is not None:
                    updated["execution_run_decision_at"] = execution_run.archived_at.isoformat()
                elif execution_run.cancelled_at is not None:
                    updated["execution_run_decision_at"] = execution_run.cancelled_at.isoformat()
                elif execution_run.completed_at is not None:
                    updated["execution_run_decision_at"] = execution_run.completed_at.isoformat()
                elif execution_run.failed_at is not None:
                    updated["execution_run_decision_at"] = execution_run.failed_at.isoformat()
                elif execution_run.started_at is not None:
                    updated["execution_run_decision_at"] = execution_run.started_at.isoformat()
                elif execution_run.queued_at is not None:
                    updated["execution_run_decision_at"] = execution_run.queued_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_result_to_plan(
        self,
        operation: CommercialOperation,
        result: CommercialOperationResult,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == result.step_key:
                updated = dict(step)
                updated["commercial_result_id"] = str(result.id)
                updated["commercial_result_status"] = result.result_status
                updated["commercial_result_type"] = result.result_type
                updated["commercial_result_channel"] = result.channel
                if result.archived_at is not None:
                    updated["commercial_result_decision_at"] = result.archived_at.isoformat()
                elif result.approved_at is not None:
                    updated["commercial_result_decision_at"] = result.approved_at.isoformat()
                elif result.rejected_at is not None:
                    updated["commercial_result_decision_at"] = result.rejected_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_monitoring_observation_to_plan(
        self,
        operation: CommercialOperation,
        observation: CommercialOperationMonitoringObservation,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == observation.step_key:
                updated = dict(step)
                updated["monitoring_observation_id"] = str(observation.id)
                updated["monitoring_observation_status"] = observation.observation_status
                updated["monitoring_observation_type"] = observation.observation_type
                updated["monitoring_observation_channel"] = observation.channel
                if observation.archived_at is not None:
                    updated["monitoring_observation_decision_at"] = observation.archived_at.isoformat()
                elif observation.approved_at is not None:
                    updated["monitoring_observation_decision_at"] = observation.approved_at.isoformat()
                elif observation.rejected_at is not None:
                    updated["monitoring_observation_decision_at"] = observation.rejected_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_optimization_decision_to_plan(
        self,
        operation: CommercialOperation,
        decision: CommercialOperationOptimizationDecision,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == decision.step_key:
                updated = dict(step)
                updated["optimization_decision_id"] = str(decision.id)
                updated["optimization_decision_status"] = decision.decision_status
                updated["optimization_decision_type"] = decision.decision_type
                updated["optimization_decision_channel"] = decision.channel
                updated["optimization_decision_priority"] = decision.priority
                if decision.next_review_at is not None:
                    updated["optimization_decision_next_review_at"] = decision.next_review_at.isoformat()
                if decision.archived_at is not None:
                    updated["optimization_decision_decision_at"] = decision.archived_at.isoformat()
                elif decision.approved_at is not None:
                    updated["optimization_decision_decision_at"] = decision.approved_at.isoformat()
                elif decision.rejected_at is not None:
                    updated["optimization_decision_decision_at"] = decision.rejected_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_evidence_snapshot_to_plan(
        self,
        operation: CommercialOperation,
        snapshot: CommercialOperationEvidenceSnapshot,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == snapshot.step_key:
                updated = dict(step)
                updated["evidence_snapshot_id"] = str(snapshot.id)
                updated["evidence_snapshot_status"] = snapshot.snapshot_status
                updated["evidence_snapshot_type"] = snapshot.evidence_type
                updated["evidence_snapshot_channel"] = snapshot.channel
                updated["evidence_snapshot_collection"] = snapshot.knowledge_collection
                updated["evidence_snapshot_item_count"] = len(snapshot.evidence_items or [])
                if snapshot.archived_at is not None:
                    updated["evidence_snapshot_decision_at"] = snapshot.archived_at.isoformat()
                elif snapshot.approved_at is not None:
                    updated["evidence_snapshot_decision_at"] = snapshot.approved_at.isoformat()
                elif snapshot.rejected_at is not None:
                    updated["evidence_snapshot_decision_at"] = snapshot.rejected_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_evidence_snapshot_to_deliverable(
        self,
        deliverable: CommercialOperationDeliverable,
        snapshot: CommercialOperationEvidenceSnapshot,
    ) -> None:
        payload = dict(deliverable.package_payload or {})
        snapshots = [
            dict(item)
            for item in payload.get("evidence_snapshots", [])
            if isinstance(item, dict) and item.get("evidence_snapshot_id") != str(snapshot.id)
        ]
        snapshots.append(
            {
                "evidence_snapshot_id": str(snapshot.id),
                "title": snapshot.title,
                "snapshot_status": snapshot.snapshot_status,
                "evidence_type": snapshot.evidence_type,
                "knowledge_collection": snapshot.knowledge_collection,
                "source_document_count": len(snapshot.source_document_ids or []),
                "evidence_item_count": len(snapshot.evidence_items or []),
            }
        )
        payload["evidence_snapshots"] = snapshots
        payload["evidence_snapshot_count"] = len(snapshots)
        if (snapshot.snapshot_payload or {}).get("generation_mode") == "rag_search_snapshot":
            payload["evidence_boundary"] = (
                "RAG search snapshot only; no ingestion, approval bypass, publishing, or external execution"
            )
        else:
            payload["evidence_boundary"] = "operator-reviewed snapshot only; no live RAG retrieval or external execution"
        deliverable.package_payload = payload

    def _apply_deliverable_to_plan(
        self,
        operation: CommercialOperation,
        deliverable: CommercialOperationDeliverable,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == deliverable.step_key:
                updated = dict(step)
                updated["deliverable_id"] = str(deliverable.id)
                updated["deliverable_status"] = deliverable.deliverable_status
                updated["deliverable_type"] = deliverable.deliverable_type
                updated["deliverable_channel"] = deliverable.channel
                if deliverable.output_artifact_id is not None:
                    updated["deliverable_output_artifact_id"] = str(deliverable.output_artifact_id)
                if deliverable.approved_at is not None:
                    updated["deliverable_decision_at"] = deliverable.approved_at.isoformat()
                elif deliverable.rejected_at is not None:
                    updated["deliverable_decision_at"] = deliverable.rejected_at.isoformat()
                elif deliverable.packaged_at is not None:
                    updated["deliverable_decision_at"] = deliverable.packaged_at.isoformat()
                elif deliverable.failed_at is not None:
                    updated["deliverable_decision_at"] = deliverable.failed_at.isoformat()
                elif deliverable.archived_at is not None:
                    updated["deliverable_decision_at"] = deliverable.archived_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_asset_request_to_plan(
        self,
        operation: CommercialOperation,
        asset_request: CommercialOperationAssetRequest,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == asset_request.step_key:
                updated = dict(step)
                updated["asset_request_id"] = str(asset_request.id)
                updated["asset_request_status"] = asset_request.request_status
                updated["asset_request_channel"] = asset_request.channel
                updated["asset_request_type"] = asset_request.asset_type
                if asset_request.content_draft_id is not None:
                    updated["asset_request_content_draft_id"] = str(asset_request.content_draft_id)
                if asset_request.approved_at is not None:
                    updated["asset_request_decision_at"] = asset_request.approved_at.isoformat()
                elif asset_request.rejected_at is not None:
                    updated["asset_request_decision_at"] = asset_request.rejected_at.isoformat()
                elif asset_request.prepared_at is not None:
                    updated["asset_request_decision_at"] = asset_request.prepared_at.isoformat()
                elif asset_request.failed_at is not None:
                    updated["asset_request_decision_at"] = asset_request.failed_at.isoformat()
                elif asset_request.archived_at is not None:
                    updated["asset_request_decision_at"] = asset_request.archived_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_comfyui_handoff_to_plan(
        self,
        operation: CommercialOperation,
        handoff: CommercialOperationComfyUIHandoff,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == handoff.step_key:
                updated = dict(step)
                updated["comfyui_handoff_id"] = str(handoff.id)
                updated["comfyui_handoff_status"] = handoff.handoff_status
                updated["comfyui_handoff_asset_request_id"] = str(handoff.asset_request_id)
                updated["comfyui_handoff_workflow_name"] = handoff.workflow_name
                if handoff.approved_at is not None:
                    updated["comfyui_handoff_decision_at"] = handoff.approved_at.isoformat()
                elif handoff.rejected_at is not None:
                    updated["comfyui_handoff_decision_at"] = handoff.rejected_at.isoformat()
                elif handoff.prepared_at is not None:
                    updated["comfyui_handoff_decision_at"] = handoff.prepared_at.isoformat()
                elif handoff.failed_at is not None:
                    updated["comfyui_handoff_decision_at"] = handoff.failed_at.isoformat()
                elif handoff.archived_at is not None:
                    updated["comfyui_handoff_decision_at"] = handoff.archived_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline

    def _apply_dry_run_to_plan(
        self,
        operation: CommercialOperation,
        dry_run: CommercialOperationDryRun,
    ) -> None:
        outline: list[dict[str, Any]] = []
        for step in operation.plan_outline or []:
            if step.get("step_key") == dry_run.step_key:
                updated = dict(step)
                updated["dry_run_id"] = str(dry_run.id)
                updated["dry_run_status"] = dry_run.dry_run_status
                updated["dry_run_execution_mode"] = dry_run.execution_mode
                if dry_run.execution_target:
                    updated["dry_run_execution_target"] = dry_run.execution_target
                if dry_run.cancelled_at is not None:
                    updated["dry_run_decision_at"] = dry_run.cancelled_at.isoformat()
                elif dry_run.failed_at is not None:
                    updated["dry_run_decision_at"] = dry_run.failed_at.isoformat()
                elif dry_run.completed_at is not None:
                    updated["dry_run_decision_at"] = dry_run.completed_at.isoformat()
                outline.append(updated)
            else:
                outline.append(dict(step))
        operation.plan_outline = outline
