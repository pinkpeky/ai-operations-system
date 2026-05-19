"""Commercial operation service layer."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commercial_operation import CommercialOperation, CommercialOperationApproval, CommercialOperationLink
from app.models.enums import CommercialOperationApprovalStatus, CommercialOperationStatus


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
