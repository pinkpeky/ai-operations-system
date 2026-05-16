"""Workflow template governance, lifecycle, and marketplace services."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from app.models.enums import (
    WorkflowTemplatePromotionType,
    WorkflowTemplateReviewStatus,
    WorkflowTemplateStatus,
)
from app.models.workflow import (
    WorkflowTemplate,
    WorkflowTemplateAuditLog,
    WorkflowTemplateCompatibilityMatrix,
    WorkflowTemplatePromotion,
    WorkflowTemplateReview,
    WorkflowTemplateVersion,
)
from app.workflow.template_registry import WorkflowTemplateRegistryService


RUNTIME_CAPABILITIES = (
    "browser_runtime",
    "approval_gate",
    "task_scheduler",
    "artifact_pipeline",
    "workflow_graph_runtime",
    "openclaw_mock",
    "rag_pipeline",
)


class WorkflowTemplateGovernanceService:
    """Workspace-scoped internal template governance and marketplace layer."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.registry = WorkflowTemplateRegistryService(session)

    async def submit_for_review(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        template_version_id: UUID,
        reviewer_id: str | None,
        review_notes: str | None = None,
        risk_assessment: dict[str, Any] | None = None,
        actor_id: str | None = None,
        commit: bool = True,
    ) -> WorkflowTemplateReview:
        template = await self.registry.require_template(workspace_id=workspace_id, template_id=template_id)
        version = await self.registry.require_template_version(
            workspace_id=workspace_id,
            template_id=template.id,
            version_id=template_version_id,
        )
        previous = self._template_state(template)
        validated = await self.registry.validate_template(
            workspace_id=workspace_id,
            template_id=template.id,
            version_id=version.id,
            commit=False,
        )
        review = WorkflowTemplateReview(
            workspace_id=workspace_id,
            template_id=template.id,
            template_version_id=version.id,
            reviewer_id=reviewer_id,
            review_status=WorkflowTemplateReviewStatus.PENDING.value,
            review_notes=review_notes,
            risk_assessment=risk_assessment or {"risk_level": template.risk_level},
            compatibility_report=validated.compatibility or {},
        )
        self.session.add(review)
        template.status = WorkflowTemplateStatus.REVIEW.value
        await self._sync_compatibility_matrix(workspace_id=workspace_id, version=validated, compatibility=validated.compatibility or {})
        await self.create_audit_log(
            workspace_id=workspace_id,
            template_id=template.id,
            template_version_id=version.id,
            action="review_submitted",
            actor_id=actor_id or reviewer_id,
            previous_state=previous,
            new_state={"status": template.status, "review_status": review.review_status},
            metadata={"review_notes": review_notes},
            commit=False,
        )
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(review)
        return review

    async def approve_review(
        self,
        *,
        workspace_id: str,
        review_id: UUID,
        actor_id: str | None,
        review_notes: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowTemplateReview:
        return await self._transition_review(
            workspace_id=workspace_id,
            review_id=review_id,
            actor_id=actor_id,
            status=WorkflowTemplateReviewStatus.APPROVED.value,
            template_status=WorkflowTemplateStatus.APPROVED.value,
            review_notes=review_notes,
            metadata=metadata,
            verified=True,
            action="review_approved",
        )

    async def reject_review(
        self,
        *,
        workspace_id: str,
        review_id: UUID,
        actor_id: str | None,
        review_notes: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowTemplateReview:
        return await self._transition_review(
            workspace_id=workspace_id,
            review_id=review_id,
            actor_id=actor_id,
            status=WorkflowTemplateReviewStatus.REJECTED.value,
            template_status=WorkflowTemplateStatus.DRAFT.value,
            review_notes=review_notes,
            metadata=metadata,
            verified=False,
            action="review_rejected",
        )

    async def request_changes(
        self,
        *,
        workspace_id: str,
        review_id: UUID,
        actor_id: str | None,
        review_notes: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowTemplateReview:
        return await self._transition_review(
            workspace_id=workspace_id,
            review_id=review_id,
            actor_id=actor_id,
            status=WorkflowTemplateReviewStatus.CHANGES_REQUESTED.value,
            template_status=WorkflowTemplateStatus.DRAFT.value,
            review_notes=review_notes,
            metadata=metadata,
            verified=False,
            action="changes_requested",
        )

    async def activate_template_version(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version_id: UUID,
        actor_id: str | None,
        reason: str | None = None,
    ) -> WorkflowTemplate:
        template = await self.registry.require_template(workspace_id=workspace_id, template_id=template_id)
        version = await self.registry.require_template_version(workspace_id=workspace_id, template_id=template.id, version_id=version_id)
        approved_review = await self._latest_review(
            workspace_id=workspace_id,
            template_id=template.id,
            version_id=version.id,
            statuses={WorkflowTemplateReviewStatus.APPROVED.value},
        )
        if approved_review is None and not (template.template_metadata or {}).get("built_in"):
            raise ValueError("Workflow template version must be approved before activation")
        validated = await self.registry.validate_template(
            workspace_id=workspace_id,
            template_id=template.id,
            version_id=version.id,
            commit=False,
        )
        if not (validated.compatibility or {}).get("compatible", False):
            raise ValueError("Workflow template version is not compatible and cannot be activated")
        previous = self._template_state(template)
        previous_version = await self._current_version_model(workspace_id=workspace_id, template=template)
        template.status = WorkflowTemplateStatus.ACTIVE.value
        template.current_version = version.version
        template.verified = True
        template.recommended = template.recommended or template.risk_level == "low"
        await self._create_promotion(
            workspace_id=workspace_id,
            template_id=template.id,
            from_version_id=previous_version.id if previous_version else None,
            to_version_id=version.id,
            promotion_type=WorkflowTemplatePromotionType.ACTIVATE.value,
            reason=reason,
            actor_id=actor_id,
        )
        await self.create_audit_log(
            workspace_id=workspace_id,
            template_id=template.id,
            template_version_id=version.id,
            action="template_activated",
            actor_id=actor_id,
            previous_state=previous,
            new_state=self._template_state(template),
            metadata={"review_id": str(approved_review.id) if approved_review else None, "reason": reason},
            commit=False,
        )
        await self.session.commit()
        return await self.registry.require_template(workspace_id=workspace_id, template_id=template.id)

    async def rollback_template_version(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version_id: UUID,
        actor_id: str | None,
        reason: str | None = None,
    ) -> WorkflowTemplate:
        template = await self.registry.require_template(workspace_id=workspace_id, template_id=template_id)
        target = await self.registry.require_template_version(workspace_id=workspace_id, template_id=template.id, version_id=version_id)
        previous = self._template_state(template)
        previous_version = await self._current_version_model(workspace_id=workspace_id, template=template)
        await self.registry.validate_template(workspace_id=workspace_id, template_id=template.id, version_id=target.id, commit=False)
        template.status = WorkflowTemplateStatus.ACTIVE.value
        template.current_version = target.version
        await self._create_promotion(
            workspace_id=workspace_id,
            template_id=template.id,
            from_version_id=previous_version.id if previous_version else None,
            to_version_id=target.id,
            promotion_type=WorkflowTemplatePromotionType.ROLLBACK.value,
            reason=reason,
            actor_id=actor_id,
        )
        await self.create_audit_log(
            workspace_id=workspace_id,
            template_id=template.id,
            template_version_id=target.id,
            action="template_rollback",
            actor_id=actor_id,
            previous_state=previous,
            new_state=self._template_state(template),
            metadata={"reason": reason},
            commit=False,
        )
        await self.session.commit()
        return await self.registry.require_template(workspace_id=workspace_id, template_id=template.id)

    async def deprecate_template(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        actor_id: str | None,
        reason: str | None = None,
    ) -> WorkflowTemplate:
        return await self._set_template_terminal_status(
            workspace_id=workspace_id,
            template_id=template_id,
            actor_id=actor_id,
            status=WorkflowTemplateStatus.DEPRECATED.value,
            promotion_type=WorkflowTemplatePromotionType.DEPRECATE.value,
            action="template_deprecated",
            reason=reason,
        )

    async def archive_template(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        actor_id: str | None,
        reason: str | None = None,
    ) -> WorkflowTemplate:
        return await self._set_template_terminal_status(
            workspace_id=workspace_id,
            template_id=template_id,
            actor_id=actor_id,
            status=WorkflowTemplateStatus.ARCHIVED.value,
            promotion_type=WorkflowTemplatePromotionType.ARCHIVE.value,
            action="template_archived",
            reason=reason,
        )

    async def create_audit_log(
        self,
        *,
        workspace_id: str,
        template_id: UUID | None,
        template_version_id: UUID | None,
        action: str,
        actor_id: str | None,
        previous_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowTemplateAuditLog:
        log = WorkflowTemplateAuditLog(
            workspace_id=workspace_id,
            template_id=template_id,
            template_version_id=template_version_id,
            action=action,
            actor_id=actor_id,
            previous_state=previous_state or {},
            new_state=new_state or {},
            audit_metadata=metadata or {},
        )
        self.session.add(log)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(log)
        return log

    async def list_review_queue(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[WorkflowTemplateReview]:
        statement = select(WorkflowTemplateReview).where(WorkflowTemplateReview.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(WorkflowTemplateReview.review_status == status)
        result = await self.session.execute(statement.order_by(WorkflowTemplateReview.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_review(self, *, workspace_id: str, review_id: UUID) -> WorkflowTemplateReview | None:
        result = await self.session.execute(
            select(WorkflowTemplateReview).where(WorkflowTemplateReview.workspace_id == workspace_id, WorkflowTemplateReview.id == review_id)
        )
        return result.scalar_one_or_none()

    async def require_review(self, *, workspace_id: str, review_id: UUID) -> WorkflowTemplateReview:
        review = await self.get_review(workspace_id=workspace_id, review_id=review_id)
        if review is None:
            raise ValueError("Workflow template review not found in workspace")
        return review

    async def list_governance_events(
        self,
        *,
        workspace_id: str,
        template_id: UUID | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[WorkflowTemplateAuditLog]:
        statement = select(WorkflowTemplateAuditLog).where(WorkflowTemplateAuditLog.workspace_id == workspace_id)
        if template_id is not None:
            statement = statement.where(WorkflowTemplateAuditLog.template_id == template_id)
        if action is not None:
            statement = statement.where(WorkflowTemplateAuditLog.action == action)
        result = await self.session.execute(statement.order_by(WorkflowTemplateAuditLog.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def list_compatibility_matrix(
        self,
        *,
        workspace_id: str,
        template_version_id: UUID | None = None,
        runtime_capability: str | None = None,
        limit: int = 500,
    ) -> list[WorkflowTemplateCompatibilityMatrix]:
        statement = select(WorkflowTemplateCompatibilityMatrix).where(WorkflowTemplateCompatibilityMatrix.workspace_id == workspace_id)
        if template_version_id is not None:
            statement = statement.where(WorkflowTemplateCompatibilityMatrix.template_version_id == template_version_id)
        if runtime_capability is not None:
            statement = statement.where(WorkflowTemplateCompatibilityMatrix.runtime_capability == runtime_capability)
        result = await self.session.execute(
            statement.order_by(WorkflowTemplateCompatibilityMatrix.runtime_capability.asc()).limit(limit)
        )
        return list(result.scalars().all())

    async def list_marketplace(
        self,
        *,
        workspace_id: str,
        featured: bool | None = None,
        verified: bool | None = None,
        recommended: bool | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        templates = await self.registry.list_templates(workspace_id=workspace_id, limit=limit)
        items: list[dict[str, Any]] = []
        for template in templates:
            if featured is not None and template.featured != featured:
                continue
            if verified is not None and template.verified != verified:
                continue
            if recommended is not None and template.recommended != recommended:
                continue
            latest_review = await self._latest_review(workspace_id=workspace_id, template_id=template.id, version_id=None)
            badges = self._badges(template=template, latest_review=latest_review)
            items.append(
                {
                    "template": template,
                    "badges": badges,
                    "metrics": {
                        "total_runs": template.usage_count,
                        "success_rate": template.success_rate,
                        "avg_runtime_ms": template.average_runtime_ms,
                        "avg_step_count": template.average_step_count,
                        "approval_required_rate": (template.template_metadata or {}).get("approval_required_rate", 0),
                        "failure_rate": max(0.0, 1.0 - float(template.success_rate or 0)),
                    },
                    "governance_status": template.status,
                    "latest_review_status": latest_review.review_status if latest_review else None,
                }
            )
        return items

    async def _transition_review(
        self,
        *,
        workspace_id: str,
        review_id: UUID,
        actor_id: str | None,
        status: str,
        template_status: str,
        review_notes: str | None,
        metadata: dict[str, Any] | None,
        verified: bool,
        action: str,
    ) -> WorkflowTemplateReview:
        review = await self.require_review(workspace_id=workspace_id, review_id=review_id)
        if review.review_status not in {WorkflowTemplateReviewStatus.PENDING.value, WorkflowTemplateReviewStatus.CHANGES_REQUESTED.value}:
            raise ValueError("Workflow template review is already finalized")
        template = await self.registry.require_template(workspace_id=workspace_id, template_id=review.template_id)
        previous = {"review_status": review.review_status, **self._template_state(template)}
        review.review_status = status
        if review_notes is not None:
            review.review_notes = review_notes
        review.reviewer_id = actor_id or review.reviewer_id
        template.status = template_status
        template.verified = verified
        await self.create_audit_log(
            workspace_id=workspace_id,
            template_id=template.id,
            template_version_id=review.template_version_id,
            action=action,
            actor_id=actor_id,
            previous_state=previous,
            new_state={"review_status": status, **self._template_state(template)},
            metadata=metadata,
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def _set_template_terminal_status(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        actor_id: str | None,
        status: str,
        promotion_type: str,
        action: str,
        reason: str | None,
    ) -> WorkflowTemplate:
        template = await self.registry.require_template(workspace_id=workspace_id, template_id=template_id)
        previous = self._template_state(template)
        current_version = await self._current_version_model(workspace_id=workspace_id, template=template)
        template.status = status
        template.current_version = None
        template.recommended = False
        await self._create_promotion(
            workspace_id=workspace_id,
            template_id=template.id,
            from_version_id=current_version.id if current_version else None,
            to_version_id=None,
            promotion_type=promotion_type,
            reason=reason,
            actor_id=actor_id,
        )
        await self.create_audit_log(
            workspace_id=workspace_id,
            template_id=template.id,
            template_version_id=current_version.id if current_version else None,
            action=action,
            actor_id=actor_id,
            previous_state=previous,
            new_state=self._template_state(template),
            metadata={"reason": reason},
            commit=False,
        )
        await self.session.commit()
        return await self.registry.require_template(workspace_id=workspace_id, template_id=template.id)

    async def _create_promotion(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        from_version_id: UUID | None,
        to_version_id: UUID | None,
        promotion_type: str,
        reason: str | None,
        actor_id: str | None,
    ) -> WorkflowTemplatePromotion:
        promotion = WorkflowTemplatePromotion(
            workspace_id=workspace_id,
            template_id=template_id,
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            promotion_type=promotion_type,
            promotion_reason=reason,
            promoted_by=actor_id,
        )
        self.session.add(promotion)
        await self.session.flush()
        return promotion

    async def _sync_compatibility_matrix(
        self,
        *,
        workspace_id: str,
        version: WorkflowTemplateVersion,
        compatibility: dict[str, Any],
    ) -> None:
        missing = set(compatibility.get("missing_capabilities") or [])
        warnings = compatibility.get("warnings") or []
        errors = compatibility.get("errors") or []
        for capability in RUNTIME_CAPABILITIES:
            existing = await self.session.execute(
                select(WorkflowTemplateCompatibilityMatrix).where(
                    WorkflowTemplateCompatibilityMatrix.workspace_id == workspace_id,
                    WorkflowTemplateCompatibilityMatrix.template_version_id == version.id,
                    WorkflowTemplateCompatibilityMatrix.runtime_capability == capability,
                )
            )
            row = existing.scalar_one_or_none()
            supported = capability not in missing and not any(capability in str(error) for error in errors)
            notes = "; ".join(str(item) for item in [*warnings, *errors] if capability in str(item)) or None
            if row is None:
                row = WorkflowTemplateCompatibilityMatrix(
                    workspace_id=workspace_id,
                    template_version_id=version.id,
                    runtime_capability=capability,
                    supported=supported,
                    notes=notes,
                    matrix_metadata={"validation_status": compatibility.get("validation_status")},
                )
                self.session.add(row)
            else:
                row.supported = supported
                row.notes = notes
                row.matrix_metadata = {"validation_status": compatibility.get("validation_status")}
                flag_modified(row, "matrix_metadata")
        await self.session.flush()

    async def _latest_review(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version_id: UUID | None,
        statuses: set[str] | None = None,
    ) -> WorkflowTemplateReview | None:
        statement = select(WorkflowTemplateReview).where(
            WorkflowTemplateReview.workspace_id == workspace_id,
            WorkflowTemplateReview.template_id == template_id,
        )
        if version_id is not None:
            statement = statement.where(WorkflowTemplateReview.template_version_id == version_id)
        if statuses:
            statement = statement.where(WorkflowTemplateReview.review_status.in_(statuses))
        result = await self.session.execute(statement.order_by(WorkflowTemplateReview.created_at.desc()).limit(1))
        return result.scalar_one_or_none()

    async def _current_version_model(self, *, workspace_id: str, template: WorkflowTemplate) -> WorkflowTemplateVersion | None:
        if not template.current_version:
            return None
        result = await self.session.execute(
            select(WorkflowTemplateVersion).where(
                WorkflowTemplateVersion.workspace_id == workspace_id,
                WorkflowTemplateVersion.template_id == template.id,
                WorkflowTemplateVersion.version == template.current_version,
            )
        )
        return result.scalar_one_or_none()

    def _template_state(self, template: WorkflowTemplate) -> dict[str, Any]:
        return {
            "template_id": str(template.id),
            "status": template.status,
            "current_version": template.current_version,
            "latest_version": template.latest_version,
            "verified": template.verified,
            "featured": template.featured,
            "recommended": template.recommended,
        }

    def _badges(self, *, template: WorkflowTemplate, latest_review: WorkflowTemplateReview | None) -> list[str]:
        badges: list[str] = []
        if template.featured:
            badges.append("featured")
        if template.verified:
            badges.append("verified")
        if template.recommended:
            badges.append("recommended")
        badges.append(f"risk:{template.risk_level}")
        badges.append(f"status:{template.status}")
        if latest_review:
            badges.append(f"review:{latest_review.review_status}")
        return badges
