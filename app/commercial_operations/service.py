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
    CommercialOperationContentDraft,
    CommercialOperationDryRun,
    CommercialOperationLink,
)
from app.models.enums import (
    CommercialOperationApprovalStatus,
    CommercialOperationContentDraftStatus,
    CommercialOperationDryRunStatus,
    CommercialOperationStatus,
)


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
