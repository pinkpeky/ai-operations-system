"""Artifact packaging service.

Packages artifacts from playbook runs, task runs, browser runtime sessions, or
conversation threads into ZIP bundles without copying large source files unless
they are already represented as small artifact content.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.services.artifact_export_service import ArtifactExportService
from app.services.output_artifact_service import OutputArtifactService


class ArtifactPackagingService:
    """High-level package builder for artifact collections."""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.artifacts = OutputArtifactService(session, settings=self.settings)
        self.exports = ArtifactExportService(session, settings=self.settings)

    async def package_artifact(
        self,
        *,
        workspace_id: str,
        artifact_id: UUID,
        include_related: bool = True,
        package_type: str = "bundle_zip",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        artifact = await self.artifacts.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        artifact_ids = [artifact.id]
        if include_related:
            lineage = await self.artifacts.lineage_for_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
            artifact_ids.extend(item.id for item in lineage["ancestors"])
            artifact_ids.extend(item.id for item in lineage["descendants"])
        artifact_ids = list(dict.fromkeys(artifact_ids))
        if package_type == "report_package":
            return await self.exports.export_report_package(workspace_id=workspace_id, artifact_ids=artifact_ids, metadata=metadata)
        return await self.exports.export_bundle_zip(
            workspace_id=workspace_id,
            artifact_ids=artifact_ids,
            bundle_name=f"artifact-{artifact.id}",
            metadata={"package_type": package_type, **(metadata or {})},
        )

    async def package_playbook_run(self, *, workspace_id: str, playbook_run_id: UUID, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        artifacts = await self.artifacts.list_artifacts(workspace_id=workspace_id, playbook_run_id=playbook_run_id, limit=500)
        if not artifacts:
            raise ValueError("No artifacts found for playbook run")
        return await self.exports.export_bundle_zip(
            workspace_id=workspace_id,
            artifact_ids=[item.id for item in artifacts],
            bundle_name=f"playbook-run-{playbook_run_id}",
            metadata={"package_source": "playbook_run", "playbook_run_id": str(playbook_run_id), **(metadata or {})},
        )

    async def package_task_run(self, *, workspace_id: str, task_run_id: UUID, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        artifacts = await self.artifacts.list_artifacts(workspace_id=workspace_id, task_run_id=task_run_id, limit=500)
        if not artifacts:
            raise ValueError("No artifacts found for task run")
        return await self.exports.export_bundle_zip(
            workspace_id=workspace_id,
            artifact_ids=[item.id for item in artifacts],
            bundle_name=f"task-run-{task_run_id}",
            metadata={"package_source": "task_run", "task_run_id": str(task_run_id), **(metadata or {})},
        )

    async def package_browser_runtime_session(
        self,
        *,
        workspace_id: str,
        runtime_session_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        artifacts = await self.artifacts.list_artifacts(
            workspace_id=workspace_id,
            source_runtime_session_id=runtime_session_id,
            limit=500,
        )
        if not artifacts:
            raise ValueError("No artifacts found for browser runtime session")
        return await self.exports.export_bundle_zip(
            workspace_id=workspace_id,
            artifact_ids=[item.id for item in artifacts],
            bundle_name=f"browser-runtime-{runtime_session_id}",
            metadata={"package_source": "browser_runtime_session", "runtime_session_id": str(runtime_session_id), **(metadata or {})},
        )

    async def package_conversation(self, *, workspace_id: str, conversation_id: UUID, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        artifacts = await self.artifacts.list_artifacts(
            workspace_id=workspace_id,
            source_conversation_id=conversation_id,
            limit=500,
        )
        if not artifacts:
            artifacts = await self.artifacts.list_artifacts(workspace_id=workspace_id, thread_id=conversation_id, limit=500)
        if not artifacts:
            raise ValueError("No artifacts found for conversation")
        return await self.exports.export_bundle_zip(
            workspace_id=workspace_id,
            artifact_ids=[item.id for item in artifacts],
            bundle_name=f"conversation-{conversation_id}",
            metadata={"package_source": "conversation", "conversation_id": str(conversation_id), **(metadata or {})},
        )
