"""Output Artifact service.

Phase 41 keeps reusable Playbook/Conversation/Tool outputs in a workspace
scoped Output Library. The service intentionally stores large files by path and
keeps text content concise enough for list/detail/export views.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.conversation.repositories import ConversationRuntimeRepository
from app.core.config import Settings, get_settings
from app.models.browser_runtime import BrowserRuntimeSnapshot
from app.models.conversation import ConversationPlaybook, ConversationPlaybookRun
from app.models.enums import (
    OutputArtifactRetentionPolicy,
    OutputArtifactRole,
    OutputArtifactSourceType,
    OutputArtifactStage,
    OutputArtifactStatus,
    OutputArtifactType,
)
from app.models.memory import ConversationMessage
from app.models.output_artifact import ArtifactRelationship, OutputArtifact

logger = logging.getLogger(__name__)


class OutputArtifactService:
    """Workspace-scoped Output Library manager."""

    MAX_CONTENT_CHARS = 24000
    MAX_METADATA_CHARS = 40000

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.repository = ConversationRuntimeRepository(session)
        self.storage_root = Path(self.settings.output_artifact_dir)

    async def create_artifact(
        self,
        *,
        workspace_id: str,
        source_type: str,
        artifact_type: str,
        title: str,
        summary: str | None = None,
        content: str | None = None,
        file_path: str | None = None,
        mime_type: str | None = None,
        metadata: dict[str, Any] | None = None,
        thread_id: UUID | None = None,
        playbook_run_id: UUID | None = None,
        task_run_id: UUID | None = None,
        parent_artifact_id: UUID | None = None,
        root_artifact_id: UUID | None = None,
        source_task_run_id: UUID | None = None,
        source_playbook_run_id: UUID | None = None,
        source_conversation_id: UUID | None = None,
        source_runtime_session_id: UUID | None = None,
        artifact_role: str | None = None,
        artifact_stage: str = OutputArtifactStage.PROCESSED.value,
        generated_by: str | None = None,
        exportable: bool = True,
        retention_policy: str = OutputArtifactRetentionPolicy.STANDARD.value,
        expires_at: datetime | None = None,
        created_by: str | None = None,
        commit: bool = True,
    ) -> OutputArtifact:
        """Create one artifact while keeping payloads bounded."""

        self._validate_source_and_type(source_type=source_type, artifact_type=artifact_type)
        self._validate_pipeline_fields(
            artifact_role=artifact_role,
            artifact_stage=artifact_stage,
            retention_policy=retention_policy,
        )
        if parent_artifact_id is not None:
            parent = await self.require_artifact(workspace_id=workspace_id, artifact_id=parent_artifact_id)
            root_artifact_id = root_artifact_id or parent.root_artifact_id or parent.id
        artifact = OutputArtifact(
            workspace_id=workspace_id,
            thread_id=thread_id,
            playbook_run_id=playbook_run_id,
            task_run_id=task_run_id,
            parent_artifact_id=parent_artifact_id,
            root_artifact_id=root_artifact_id,
            source_task_run_id=source_task_run_id or task_run_id,
            source_playbook_run_id=source_playbook_run_id or playbook_run_id,
            source_conversation_id=source_conversation_id or thread_id,
            source_runtime_session_id=source_runtime_session_id,
            source_type=source_type,
            artifact_type=artifact_type,
            artifact_role=artifact_role or self._role_from_artifact_type(artifact_type),
            artifact_stage=artifact_stage,
            title=title[:255],
            summary=self._trim_text(summary),
            content=self._trim_text(content),
            file_path=file_path,
            mime_type=mime_type,
            artifact_metadata=self._trim_metadata(metadata or {}),
            generated_by=generated_by,
            exportable=exportable,
            retention_policy=retention_policy,
            expires_at=expires_at,
            created_by=created_by,
            status=OutputArtifactStatus.ACTIVE.value,
        )
        self.session.add(artifact)
        await self.session.flush()
        if artifact.root_artifact_id is None:
            artifact.root_artifact_id = artifact.id
        if thread_id is not None:
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="artifact_created",
                message=f"Output artifact created: {artifact.title}",
                payload={
                    "artifact_id": str(artifact.id),
                    "artifact_type": artifact.artifact_type,
                    "source_type": artifact.source_type,
                    "playbook_run_id": str(playbook_run_id) if playbook_run_id else None,
                    "task_run_id": str(task_run_id) if task_run_id else None,
                },
            )
            if playbook_run_id is not None:
                await self.repository.append_event(
                    workspace_id=workspace_id,
                    thread_id=thread_id,
                    event_type="artifact_linked_to_playbook_run",
                    message="Output artifact linked to playbook run",
                    payload={"artifact_id": str(artifact.id), "playbook_run_id": str(playbook_run_id)},
                )
        if commit:
            await self.session.commit()
            await self.session.refresh(artifact)
        logger.info(
            "Output artifact created",
            extra={"workspace_id": workspace_id, "artifact_id": str(artifact.id), "artifact_type": artifact_type},
        )
        return artifact

    async def list_artifacts(
        self,
        *,
        workspace_id: str,
        artifact_type: str | None = None,
        source_type: str | None = None,
        thread_id: UUID | None = None,
        playbook_run_id: UUID | None = None,
        task_run_id: UUID | None = None,
        artifact_role: str | None = None,
        artifact_stage: str | None = None,
        source_task_run_id: UUID | None = None,
        source_playbook_run_id: UUID | None = None,
        source_conversation_id: UUID | None = None,
        source_runtime_session_id: UUID | None = None,
        exportable: bool | None = None,
        archived: bool | None = None,
        retention_policy: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int = 100,
    ) -> list[OutputArtifact]:
        """List artifacts with workspace isolation and optional filters."""

        statement = select(OutputArtifact).where(OutputArtifact.workspace_id == workspace_id)
        if not include_deleted:
            statement = statement.where(OutputArtifact.status != OutputArtifactStatus.DELETED.value)
        if artifact_type is not None:
            statement = statement.where(OutputArtifact.artifact_type == artifact_type)
        if source_type is not None:
            statement = statement.where(OutputArtifact.source_type == source_type)
        if thread_id is not None:
            statement = statement.where(OutputArtifact.thread_id == thread_id)
        if playbook_run_id is not None:
            statement = statement.where(OutputArtifact.playbook_run_id == playbook_run_id)
        if task_run_id is not None:
            statement = statement.where(OutputArtifact.task_run_id == task_run_id)
        if artifact_role is not None:
            statement = statement.where(OutputArtifact.artifact_role == artifact_role)
        if artifact_stage is not None:
            statement = statement.where(OutputArtifact.artifact_stage == artifact_stage)
        if source_task_run_id is not None:
            statement = statement.where(OutputArtifact.source_task_run_id == source_task_run_id)
        if source_playbook_run_id is not None:
            statement = statement.where(OutputArtifact.source_playbook_run_id == source_playbook_run_id)
        if source_conversation_id is not None:
            statement = statement.where(OutputArtifact.source_conversation_id == source_conversation_id)
        if source_runtime_session_id is not None:
            statement = statement.where(OutputArtifact.source_runtime_session_id == source_runtime_session_id)
        if exportable is not None:
            statement = statement.where(OutputArtifact.exportable.is_(exportable))
        if retention_policy is not None:
            statement = statement.where(OutputArtifact.retention_policy == retention_policy)
        if archived is True:
            statement = statement.where(
                or_(
                    OutputArtifact.status == OutputArtifactStatus.ARCHIVED.value,
                    OutputArtifact.artifact_stage == OutputArtifactStage.ARCHIVED.value,
                )
            )
        elif archived is False:
            statement = statement.where(
                OutputArtifact.status != OutputArtifactStatus.ARCHIVED.value,
                OutputArtifact.artifact_stage != OutputArtifactStage.ARCHIVED.value,
            )
        if created_from is not None:
            statement = statement.where(OutputArtifact.created_at >= created_from)
        if created_to is not None:
            statement = statement.where(OutputArtifact.created_at <= created_to)
        statement = statement.order_by(OutputArtifact.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_artifact(self, *, workspace_id: str, artifact_id: UUID, include_deleted: bool = False) -> OutputArtifact | None:
        """Get one artifact."""

        statement = select(OutputArtifact).where(OutputArtifact.workspace_id == workspace_id, OutputArtifact.id == artifact_id)
        if not include_deleted:
            statement = statement.where(OutputArtifact.status != OutputArtifactStatus.DELETED.value)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_artifact(
        self,
        *,
        workspace_id: str,
        artifact_id: UUID,
        patch: dict[str, Any],
    ) -> OutputArtifact:
        """Patch editable artifact fields."""

        artifact = await self.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        for field in ("title", "summary", "content", "file_path", "mime_type"):
            if field in patch and patch[field] is not None:
                value = patch[field]
                if field in {"summary", "content"}:
                    value = self._trim_text(value)
                if field == "title":
                    value = str(value)[:255]
                setattr(artifact, field, value)
        if "metadata" in patch and patch["metadata"] is not None:
            artifact.artifact_metadata = self._trim_metadata(patch["metadata"])
            flag_modified(artifact, "artifact_metadata")
        for field in ("artifact_role", "artifact_stage", "generated_by", "exportable", "retention_policy", "expires_at"):
            if field not in patch or patch[field] is None:
                continue
            if field == "artifact_role" and patch[field] not in {item.value for item in OutputArtifactRole}:
                raise ValueError("Invalid output artifact artifact_role")
            if field == "artifact_stage" and patch[field] not in {item.value for item in OutputArtifactStage}:
                raise ValueError("Invalid output artifact artifact_stage")
            if field == "retention_policy" and patch[field] not in {item.value for item in OutputArtifactRetentionPolicy}:
                raise ValueError("Invalid output artifact retention_policy")
            setattr(artifact, field, patch[field])
        await self.session.commit()
        await self.session.refresh(artifact)
        return artifact

    async def link_artifacts_to_task_run(
        self,
        *,
        workspace_id: str,
        task_run_id: UUID,
        playbook_run_id: UUID | None = None,
        thread_id: UUID | None = None,
        commit: bool = True,
    ) -> list[OutputArtifact]:
        """Link existing artifacts to a task run for timeline/library queries."""

        artifacts = await self.list_artifacts(
            workspace_id=workspace_id,
            playbook_run_id=playbook_run_id,
            thread_id=thread_id if playbook_run_id is None else None,
            include_deleted=False,
            limit=500,
        )
        linked: list[OutputArtifact] = []
        for artifact in artifacts:
            if artifact.task_run_id == task_run_id:
                linked.append(artifact)
                continue
            artifact.task_run_id = task_run_id
            artifact.source_task_run_id = artifact.source_task_run_id or task_run_id
            linked.append(artifact)
        if commit:
            await self.session.commit()
            for artifact in linked:
                await self.session.refresh(artifact)
        return linked

    async def delete_artifact(self, *, workspace_id: str, artifact_id: UUID) -> OutputArtifact:
        """Soft-delete an artifact. Physical files are not removed."""

        artifact = await self.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        artifact.status = OutputArtifactStatus.DELETED.value
        if artifact.thread_id is not None:
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=artifact.thread_id,
                event_type="artifact_deleted",
                message="Output artifact soft-deleted",
                payload={"artifact_id": str(artifact.id), "file_path": artifact.file_path},
            )
        await self.session.commit()
        await self.session.refresh(artifact)
        return artifact

    async def export_artifact(self, *, workspace_id: str, artifact_id: UUID, export_format: str) -> tuple[OutputArtifact, Path, str]:
        """Export text/metadata artifacts as markdown/json/txt files."""

        artifact = await self.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        if not artifact.exportable:
            raise ValueError("Output artifact is not exportable")
        normalized_format = export_format.lower().strip()
        if normalized_format not in {"markdown", "json", "txt"}:
            raise ValueError("export format must be markdown, json, or txt")
        content = self._render_export_content(artifact=artifact, export_format=normalized_format)
        export_dir = self._artifact_dir(workspace_id=workspace_id, artifact_id=artifact.id)
        extension = "md" if normalized_format == "markdown" else normalized_format
        export_path = export_dir / f"artifact.{extension}"
        export_path.write_text(content, encoding="utf-8")
        metadata = {**(artifact.artifact_metadata or {}), "last_export_path": str(export_path), "last_export_format": normalized_format}
        artifact.artifact_metadata = self._trim_metadata(metadata)
        flag_modified(artifact, "artifact_metadata")
        if artifact.thread_id is not None:
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=artifact.thread_id,
                event_type="artifact_exported",
                message=f"Output artifact exported as {normalized_format}",
                payload={"artifact_id": str(artifact.id), "format": normalized_format, "export_path": str(export_path)},
            )
        await self.session.commit()
        await self.session.refresh(artifact)
        return artifact, export_path, content

    async def create_from_playbook_run(
        self,
        *,
        workspace_id: str,
        run_id: UUID,
        created_by: str | None = None,
        commit: bool = True,
    ) -> list[OutputArtifact]:
        """Create artifacts for a completed playbook run."""

        run = await self._require_playbook_run(workspace_id=workspace_id, run_id=run_id)
        existing = await self.list_artifacts(workspace_id=workspace_id, playbook_run_id=run_id, include_deleted=False, limit=100)
        if existing:
            return existing
        playbook = await self._get_playbook(workspace_id=workspace_id, playbook_id=run.playbook_id)
        playbook_name = (run.output_payload or {}).get("playbook_name") or (playbook.name if playbook else "playbook")
        artifact_specs = self._artifact_specs_from_playbook_run(run=run, playbook_name=str(playbook_name))
        artifacts: list[OutputArtifact] = []
        for spec in artifact_specs:
            artifacts.append(
                await self.create_artifact(
                    workspace_id=workspace_id,
                    thread_id=run.thread_id,
                    playbook_run_id=run.id,
                    source_playbook_run_id=run.id,
                    source_conversation_id=run.thread_id,
                    generated_by="ConversationPlaybookService",
                    created_by=created_by,
                    commit=False,
                    **spec,
                )
            )
        if commit:
            await self.session.commit()
            for artifact in artifacts:
                await self.session.refresh(artifact)
        return artifacts

    async def create_from_conversation_message(
        self,
        *,
        workspace_id: str,
        message_id: UUID,
        created_by: str | None = None,
        commit: bool = True,
    ) -> OutputArtifact:
        """Create one artifact from a conversation message."""

        message = await self._require_message(workspace_id=workspace_id, message_id=message_id)
        metadata = message.message_metadata or {}
        artifact_type = self._artifact_type_from_message(metadata=metadata, content=message.content)
        artifact = await self.create_artifact(
            workspace_id=workspace_id,
            thread_id=message.thread_id,
            playbook_run_id=self._uuid_or_none(metadata.get("playbook_run_id")),
            source_conversation_id=message.thread_id,
            source_playbook_run_id=self._uuid_or_none(metadata.get("playbook_run_id")),
            generated_by="ConversationService",
            source_type=OutputArtifactSourceType.CONVERSATION.value,
            artifact_type=artifact_type,
            title=self._title_from_text(message.content, fallback=f"Conversation message {message.id}"),
            summary=str(metadata.get("summary") or metadata.get("route_name") or message.role),
            content=message.content,
            mime_type="text/markdown" if artifact_type == OutputArtifactType.MARKDOWN.value else "text/plain",
            metadata={"message_id": str(message.id), "role": message.role, "message_metadata": self._trim_metadata(metadata)},
            created_by=created_by,
            commit=commit,
        )
        return artifact

    async def create_from_browser_snapshot(
        self,
        *,
        workspace_id: str,
        snapshot_id: UUID,
        created_by: str | None = None,
        commit: bool = True,
    ) -> OutputArtifact:
        """Create one artifact from a browser runtime snapshot."""

        snapshot = await self._require_browser_snapshot(workspace_id=workspace_id, snapshot_id=snapshot_id)
        if snapshot.snapshot_type == "screenshot":
            artifact_type = OutputArtifactType.SCREENSHOT.value
            file_path = snapshot.screenshot_path
            mime_type = "image/png"
            content = None
        elif snapshot.snapshot_type == "page":
            artifact_type = OutputArtifactType.HTML_SNAPSHOT.value
            file_path = snapshot.html_path
            mime_type = "text/html"
            content = None
        else:
            artifact_type = OutputArtifactType.JSON.value
            file_path = (snapshot.snapshot_metadata or {}).get("error_path")
            mime_type = "application/json"
            content = json.dumps(snapshot.snapshot_metadata or {}, ensure_ascii=False, indent=2)
        return await self.create_artifact(
            workspace_id=workspace_id,
            source_type=OutputArtifactSourceType.BROWSER_RUNTIME.value,
            artifact_type=artifact_type,
            source_runtime_session_id=snapshot.runtime_session_id,
            artifact_stage=OutputArtifactStage.RAW.value if artifact_type in {OutputArtifactType.SCREENSHOT.value, OutputArtifactType.HTML_SNAPSHOT.value} else OutputArtifactStage.PROCESSED.value,
            generated_by="BrowserRuntimeObservabilityService",
            title=f"Browser snapshot: {snapshot.page_title or snapshot.snapshot_type}",
            summary=snapshot.url,
            content=content,
            file_path=file_path,
            mime_type=mime_type,
            metadata={
                "snapshot_id": str(snapshot.id),
                "runtime_session_id": str(snapshot.runtime_session_id),
                "snapshot_type": snapshot.snapshot_type,
                "url": snapshot.url,
                "page_title": snapshot.page_title,
                "metadata": snapshot.snapshot_metadata,
            },
            created_by=created_by,
            commit=commit,
        )

    async def create_relationship(
        self,
        *,
        workspace_id: str,
        parent_artifact_id: UUID,
        child_artifact_id: UUID,
        relationship_type: str,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> ArtifactRelationship:
        """Create a lineage edge after verifying both artifacts are workspace scoped."""

        if relationship_type not in {"derived_from", "packaged_into", "summarized_from", "exported_from", "replay_of"}:
            raise ValueError("Invalid output artifact relationship_type")
        parent = await self.require_artifact(workspace_id=workspace_id, artifact_id=parent_artifact_id)
        child = await self.require_artifact(workspace_id=workspace_id, artifact_id=child_artifact_id)
        child.parent_artifact_id = child.parent_artifact_id or parent.id
        child.root_artifact_id = child.root_artifact_id or parent.root_artifact_id or parent.id
        relationship = ArtifactRelationship(
            parent_artifact_id=parent.id,
            child_artifact_id=child.id,
            relationship_type=relationship_type,
            relationship_metadata=self._trim_metadata(metadata or {}),
        )
        self.session.add(relationship)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(relationship)
            await self.session.refresh(child)
        return relationship

    async def list_relationships(
        self,
        *,
        workspace_id: str,
        artifact_id: UUID,
        direction: str = "both",
    ) -> list[ArtifactRelationship]:
        """List relationship edges attached to one artifact."""

        await self.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        statement = select(ArtifactRelationship)
        if direction == "parents":
            statement = statement.where(ArtifactRelationship.child_artifact_id == artifact_id)
        elif direction == "children":
            statement = statement.where(ArtifactRelationship.parent_artifact_id == artifact_id)
        else:
            statement = statement.where(
                or_(
                    ArtifactRelationship.parent_artifact_id == artifact_id,
                    ArtifactRelationship.child_artifact_id == artifact_id,
                )
            )
        statement = statement.order_by(ArtifactRelationship.created_at.asc())
        result = await self.session.execute(statement)
        relationships = list(result.scalars().all())
        if not relationships:
            return []
        related_ids = {item.parent_artifact_id for item in relationships} | {item.child_artifact_id for item in relationships}
        artifacts = await self.session.execute(
            select(OutputArtifact.id).where(OutputArtifact.workspace_id == workspace_id, OutputArtifact.id.in_(related_ids))
        )
        workspace_ids = set(artifacts.scalars().all())
        return [
            item
            for item in relationships
            if item.parent_artifact_id in workspace_ids and item.child_artifact_id in workspace_ids
        ]

    async def lineage_for_artifact(self, *, workspace_id: str, artifact_id: UUID) -> dict[str, Any]:
        """Return a small lineage graph centered on one artifact."""

        artifact = await self.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        relationships = await self.list_relationships(workspace_id=workspace_id, artifact_id=artifact_id)
        ancestor_ids = {item.parent_artifact_id for item in relationships if item.child_artifact_id == artifact.id}
        descendant_ids = {item.child_artifact_id for item in relationships if item.parent_artifact_id == artifact.id}
        if artifact.parent_artifact_id:
            ancestor_ids.add(artifact.parent_artifact_id)
        result = await self.session.execute(
            select(OutputArtifact).where(
                OutputArtifact.workspace_id == workspace_id,
                OutputArtifact.id.in_(ancestor_ids | descendant_ids) if ancestor_ids or descendant_ids else OutputArtifact.id == artifact.id,
            )
        )
        related = {item.id: item for item in result.scalars().all()}
        return {
            "artifact": artifact,
            "root_artifact_id": artifact.root_artifact_id,
            "ancestors": [related[item] for item in ancestor_ids if item in related],
            "descendants": [related[item] for item in descendant_ids if item in related],
            "relationships": relationships,
        }

    async def archive_artifact(self, *, workspace_id: str, artifact_id: UUID, reason: str, commit: bool = True) -> OutputArtifact:
        """Soft archive an artifact without deleting physical files."""

        artifact = await self.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        artifact.status = OutputArtifactStatus.ARCHIVED.value
        artifact.artifact_stage = OutputArtifactStage.ARCHIVED.value
        metadata = {**(artifact.artifact_metadata or {}), "archived_reason": reason, "archived_at": datetime.utcnow().isoformat()}
        artifact.artifact_metadata = self._trim_metadata(metadata)
        flag_modified(artifact, "artifact_metadata")
        if commit:
            await self.session.commit()
            await self.session.refresh(artifact)
        return artifact

    async def require_artifact(self, *, workspace_id: str, artifact_id: UUID) -> OutputArtifact:
        artifact = await self.get_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        if artifact is None:
            raise ValueError("Output artifact not found in workspace")
        return artifact

    def _artifact_specs_from_playbook_run(self, *, run: ConversationPlaybookRun, playbook_name: str) -> list[dict[str, Any]]:
        output = run.output_payload or {}
        summary = str(output.get("summary") or f"Playbook {playbook_name} completed")
        steps = output.get("steps") if isinstance(output.get("steps"), list) else []
        metadata = {"playbook_name": playbook_name, "run_status": run.status, "steps": self._step_manifest(steps)}

        if playbook_name == "content_generation":
            content_result = self._find_step_output(steps, "ContentAgent")
            return [
                {
                    "source_type": OutputArtifactSourceType.CONTENT_AGENT.value,
                    "artifact_type": OutputArtifactType.CONTENT_DRAFT.value,
                    "title": str(content_result.get("title") or "Content draft"),
                    "summary": str(content_result.get("description") or summary),
                    "content": self._content_draft_markdown(content_result),
                    "mime_type": "text/markdown",
                    "metadata": {**metadata, "content_result": content_result},
                }
            ]
        if playbook_name == "browser_screenshot_report":
            browser_metadata = self._find_browser_metadata(steps)
            return [
                {
                    "source_type": OutputArtifactSourceType.BROWSER_RUNTIME.value,
                    "artifact_type": OutputArtifactType.SCREENSHOT.value,
                    "title": f"Browser screenshot: {browser_metadata.get('page_title') or browser_metadata.get('target') or 'page'}",
                    "summary": str(browser_metadata.get("target") or summary),
                    "content": None,
                    "file_path": browser_metadata.get("screenshot"),
                    "mime_type": "image/png",
                    "metadata": {**metadata, "browser": browser_metadata},
                },
                {
                    "source_type": OutputArtifactSourceType.PLAYBOOK.value,
                    "artifact_type": OutputArtifactType.REPORT.value,
                    "title": "Browser screenshot report",
                    "summary": summary,
                    "content": self._report_markdown(title="Browser screenshot report", summary=summary, metadata=browser_metadata),
                    "mime_type": "text/markdown",
                    "metadata": {**metadata, "browser": browser_metadata},
                },
            ]
        if playbook_name == "rag_answer":
            return [
                {
                    "source_type": OutputArtifactSourceType.RAG.value,
                    "artifact_type": OutputArtifactType.RAG_ANSWER.value,
                    "title": "RAG answer",
                    "summary": summary,
                    "content": self._report_markdown(title="RAG answer", summary=summary, metadata=metadata),
                    "mime_type": "text/markdown",
                    "metadata": metadata,
                }
            ]
        if playbook_name == "trend_research_draft":
            return [
                {
                    "source_type": OutputArtifactSourceType.PLAYBOOK.value,
                    "artifact_type": OutputArtifactType.REPORT.value,
                    "title": "Trend research draft report",
                    "summary": summary,
                    "content": self._report_markdown(title="Trend research draft", summary=summary, metadata=metadata),
                    "mime_type": "text/markdown",
                    "metadata": metadata,
                },
                {
                    "source_type": OutputArtifactSourceType.CONTENT_AGENT.value,
                    "artifact_type": OutputArtifactType.CONTENT_DRAFT.value,
                    "title": "Trend content draft",
                    "summary": summary,
                    "content": self._report_markdown(title="Trend content draft", summary=summary, metadata=metadata),
                    "mime_type": "text/markdown",
                    "metadata": metadata,
                },
            ]
        if playbook_name == "openclaw_mock_device_check":
            return [
                {
                    "source_type": OutputArtifactSourceType.OPENCLAW_MOCK.value,
                    "artifact_type": OutputArtifactType.JSON.value,
                    "title": "OpenClaw mock device check",
                    "summary": "Mock OpenClaw device check result. No real device action was executed.",
                    "content": json.dumps({"summary": summary, "metadata": metadata}, ensure_ascii=False, indent=2),
                    "mime_type": "application/json",
                    "metadata": metadata,
                }
            ]
        if playbook_name == "planning":
            artifact_type = OutputArtifactType.PLAN.value
        else:
            artifact_type = OutputArtifactType.REPORT.value
        return [
            {
                "source_type": OutputArtifactSourceType.PLAYBOOK.value,
                "artifact_type": artifact_type,
                "title": f"Playbook output: {playbook_name}",
                "summary": summary,
                "content": self._report_markdown(title=f"Playbook output: {playbook_name}", summary=summary, metadata=metadata),
                "mime_type": "text/markdown",
                "metadata": metadata,
            }
        ]

    async def _require_playbook_run(self, *, workspace_id: str, run_id: UUID) -> ConversationPlaybookRun:
        statement = select(ConversationPlaybookRun).where(
            ConversationPlaybookRun.workspace_id == workspace_id,
            ConversationPlaybookRun.id == run_id,
        )
        result = await self.session.execute(statement)
        run = result.scalar_one_or_none()
        if run is None:
            raise ValueError("Conversation playbook run not found in workspace")
        return run

    async def _get_playbook(self, *, workspace_id: str, playbook_id: UUID) -> ConversationPlaybook | None:
        statement = select(ConversationPlaybook).where(
            ConversationPlaybook.workspace_id == workspace_id,
            ConversationPlaybook.id == playbook_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def _require_message(self, *, workspace_id: str, message_id: UUID) -> ConversationMessage:
        statement = select(ConversationMessage).where(
            ConversationMessage.workspace_id == workspace_id,
            ConversationMessage.id == message_id,
        )
        result = await self.session.execute(statement)
        message = result.scalar_one_or_none()
        if message is None:
            raise ValueError("Conversation message not found in workspace")
        return message

    async def _require_browser_snapshot(self, *, workspace_id: str, snapshot_id: UUID) -> BrowserRuntimeSnapshot:
        statement = select(BrowserRuntimeSnapshot).where(
            BrowserRuntimeSnapshot.workspace_id == workspace_id,
            BrowserRuntimeSnapshot.id == snapshot_id,
        )
        result = await self.session.execute(statement)
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            raise ValueError("Browser runtime snapshot not found in workspace")
        return snapshot

    def _validate_source_and_type(self, *, source_type: str, artifact_type: str) -> None:
        if source_type not in {item.value for item in OutputArtifactSourceType}:
            raise ValueError("Invalid output artifact source_type")
        if artifact_type not in {item.value for item in OutputArtifactType}:
            raise ValueError("Invalid output artifact artifact_type")

    def _validate_pipeline_fields(
        self,
        *,
        artifact_role: str | None,
        artifact_stage: str,
        retention_policy: str,
    ) -> None:
        if artifact_role is not None and artifact_role not in {item.value for item in OutputArtifactRole}:
            raise ValueError("Invalid output artifact artifact_role")
        if artifact_stage not in {item.value for item in OutputArtifactStage}:
            raise ValueError("Invalid output artifact artifact_stage")
        if retention_policy not in {item.value for item in OutputArtifactRetentionPolicy}:
            raise ValueError("Invalid output artifact retention_policy")

    def _role_from_artifact_type(self, artifact_type: str) -> str | None:
        mapping = {
            OutputArtifactType.SCREENSHOT.value: OutputArtifactRole.SCREENSHOT.value,
            OutputArtifactType.REPORT.value: OutputArtifactRole.REPORT.value,
            OutputArtifactType.MARKDOWN.value: OutputArtifactRole.MARKDOWN.value,
            OutputArtifactType.HTML.value: OutputArtifactRole.HTML.value,
            OutputArtifactType.HTML_SNAPSHOT.value: OutputArtifactRole.HTML.value,
            OutputArtifactType.JSON.value: OutputArtifactRole.JSON.value,
            OutputArtifactType.BUNDLE.value: OutputArtifactRole.BUNDLE.value,
            OutputArtifactType.DEBUG.value: OutputArtifactRole.DEBUG.value,
            OutputArtifactType.REPLAY.value: OutputArtifactRole.REPLAY.value,
            OutputArtifactType.DATASET.value: OutputArtifactRole.DATASET.value,
            OutputArtifactType.PLAN.value: OutputArtifactRole.REPORT.value,
            OutputArtifactType.RAG_ANSWER.value: OutputArtifactRole.REPORT.value,
            OutputArtifactType.CONTENT_DRAFT.value: OutputArtifactRole.MARKDOWN.value,
        }
        return mapping.get(artifact_type)

    def _artifact_type_from_message(self, *, metadata: dict[str, Any], content: str) -> str:
        route = str(metadata.get("route") or metadata.get("route_name") or "")
        if "content" in route:
            return OutputArtifactType.CONTENT_DRAFT.value
        if "rag" in route:
            return OutputArtifactType.RAG_ANSWER.value
        if "planning" in route or "plan" in route:
            return OutputArtifactType.PLAN.value
        if content.lstrip().startswith("{"):
            return OutputArtifactType.JSON.value
        return OutputArtifactType.MARKDOWN.value

    def _find_step_output(self, steps: list[Any], marker: str) -> dict[str, Any]:
        for step in steps:
            if not isinstance(step, dict):
                continue
            metadata = (((step.get("output") or {}).get("metadata") or {}) if isinstance(step.get("output"), dict) else {})
            if metadata.get("agent_name") == marker:
                return metadata.get("output") or {}
        return {}

    def _find_browser_metadata(self, steps: list[Any]) -> dict[str, Any]:
        for step in steps:
            if not isinstance(step, dict):
                continue
            output = step.get("output") or {}
            metadata = output.get("metadata") if isinstance(output, dict) else {}
            if isinstance(metadata, dict) and ("screenshot" in metadata or "runtime_session_id" in metadata):
                return metadata
        return {}

    def _step_manifest(self, steps: list[Any]) -> list[dict[str, Any]]:
        manifest: list[dict[str, Any]] = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            manifest.append(
                {
                    "step_index": step.get("step_index"),
                    "step_type": step.get("step_type"),
                    "title": step.get("title"),
                    "status": step.get("status"),
                    "duration_ms": step.get("duration_ms"),
                    "risk_level": step.get("risk_level"),
                }
            )
        return manifest

    def _content_draft_markdown(self, result: dict[str, Any]) -> str:
        title = str(result.get("title") or "Untitled")
        description = str(result.get("description") or "")
        tags = result.get("tags") or []
        cta = str(result.get("cta") or "")
        return f"# {title}\n\n{description}\n\nTags: {', '.join(map(str, tags))}\n\nCTA: {cta}".strip()

    def _report_markdown(self, *, title: str, summary: str, metadata: dict[str, Any]) -> str:
        return f"# {title}\n\n{summary}\n\n```json\n{json.dumps(self._trim_metadata(metadata), ensure_ascii=False, indent=2)}\n```"

    def _render_export_content(self, *, artifact: OutputArtifact, export_format: str) -> str:
        payload = {
            "id": str(artifact.id),
            "workspace_id": artifact.workspace_id,
            "source_type": artifact.source_type,
            "artifact_type": artifact.artifact_type,
            "artifact_role": artifact.artifact_role,
            "artifact_stage": artifact.artifact_stage,
            "title": artifact.title,
            "summary": artifact.summary,
            "content": artifact.content,
            "file_path": artifact.file_path,
            "mime_type": artifact.mime_type,
            "status": artifact.status,
            "parent_artifact_id": str(artifact.parent_artifact_id) if artifact.parent_artifact_id else None,
            "root_artifact_id": str(artifact.root_artifact_id) if artifact.root_artifact_id else None,
            "source_task_run_id": str(artifact.source_task_run_id) if artifact.source_task_run_id else None,
            "source_playbook_run_id": str(artifact.source_playbook_run_id) if artifact.source_playbook_run_id else None,
            "source_conversation_id": str(artifact.source_conversation_id) if artifact.source_conversation_id else None,
            "source_runtime_session_id": str(artifact.source_runtime_session_id) if artifact.source_runtime_session_id else None,
            "generated_by": artifact.generated_by,
            "exportable": artifact.exportable,
            "retention_policy": artifact.retention_policy,
            "expires_at": artifact.expires_at.isoformat() if artifact.expires_at else None,
            "metadata": artifact.artifact_metadata,
            "created_at": artifact.created_at.isoformat(),
        }
        if export_format == "json":
            return json.dumps(payload, ensure_ascii=False, indent=2)
        if export_format == "txt":
            return "\n\n".join(item for item in [artifact.title, artifact.summary or "", artifact.content or "", artifact.file_path or ""] if item)
        return (
            f"# {artifact.title}\n\n"
            f"**Type:** {artifact.artifact_type}\n\n"
            f"**Source:** {artifact.source_type}\n\n"
            f"{artifact.summary or ''}\n\n"
            f"{artifact.content or ''}\n\n"
            f"{'File: ' + artifact.file_path if artifact.file_path else ''}\n"
        ).strip()

    def _artifact_dir(self, *, workspace_id: str, artifact_id: UUID) -> Path:
        root = self.storage_root.resolve()
        artifact_dir = (root / self._safe_name(workspace_id) / str(artifact_id)).resolve()
        if not str(artifact_dir).startswith(str(root)):
            raise ValueError("Invalid output artifact path")
        artifact_dir.mkdir(parents=True, exist_ok=True)
        return artifact_dir

    def _trim_text(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value)
        return text if len(text) <= self.MAX_CONTENT_CHARS else f"{text[: self.MAX_CONTENT_CHARS]}\n...[truncated]"

    def _trim_metadata(self, value: dict[str, Any]) -> dict[str, Any]:
        try:
            text = json.dumps(value, ensure_ascii=False, default=str)
            if len(text) <= self.MAX_METADATA_CHARS:
                return json.loads(text)
            return {"truncated": True, "preview": text[: self.MAX_METADATA_CHARS]}
        except Exception:
            return {"serialization_error": True, "preview": str(value)[: self.MAX_METADATA_CHARS]}

    def _title_from_text(self, content: str, *, fallback: str) -> str:
        first_line = next((line.strip("# ").strip() for line in content.splitlines() if line.strip()), "")
        return (first_line or fallback)[:255]

    def _uuid_or_none(self, value: Any) -> UUID | None:
        try:
            return UUID(str(value)) if value else None
        except (TypeError, ValueError):
            return None

    def _safe_name(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]", "-", value).strip("-") or "workspace"
