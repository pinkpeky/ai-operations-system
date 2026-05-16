"""Artifact export pipeline service.

Exports are derived artifacts. They never re-run browser/runtime/playbook work;
they only package existing Output Library records and file references.
"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.enums import (
    OutputArtifactRole,
    OutputArtifactSourceType,
    OutputArtifactStage,
    OutputArtifactType,
)
from app.models.output_artifact import OutputArtifact
from app.services.output_artifact_service import OutputArtifactService


class ArtifactExportService:
    """Create export files and child artifacts from existing output artifacts."""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.artifacts = OutputArtifactService(session, settings=self.settings)
        self.export_root = Path(self.settings.output_export_dir)

    async def export_markdown(self, *, workspace_id: str, artifact_id: UUID, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        artifact = await self.artifacts.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        content = self._render_markdown(artifact)
        return await self._write_text_export(
            workspace_id=workspace_id,
            artifact=artifact,
            export_format="markdown",
            extension="md",
            mime_type="text/markdown",
            content=content,
            metadata=metadata,
        )

    async def export_html(self, *, workspace_id: str, artifact_id: UUID, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        artifact = await self.artifacts.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        content = self._render_html(artifact)
        return await self._write_text_export(
            workspace_id=workspace_id,
            artifact=artifact,
            export_format="html",
            extension="html",
            mime_type="text/html",
            content=content,
            metadata=metadata,
        )

    async def export_json(self, *, workspace_id: str, artifact_id: UUID, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        artifact = await self.artifacts.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        content = json.dumps(self._manifest_for_artifact(artifact), ensure_ascii=False, indent=2)
        return await self._write_text_export(
            workspace_id=workspace_id,
            artifact=artifact,
            export_format="json",
            extension="json",
            mime_type="application/json",
            content=content,
            metadata=metadata,
        )

    async def export_txt(self, *, workspace_id: str, artifact_id: UUID, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        artifact = await self.artifacts.require_artifact(workspace_id=workspace_id, artifact_id=artifact_id)
        content = "\n\n".join(item for item in [artifact.title, artifact.summary or "", artifact.content or "", artifact.file_path or ""] if item)
        return await self._write_text_export(
            workspace_id=workspace_id,
            artifact=artifact,
            export_format="txt",
            extension="txt",
            mime_type="text/plain",
            content=content,
            metadata=metadata,
        )

    async def export_bundle_zip(
        self,
        *,
        workspace_id: str,
        artifact_ids: list[UUID],
        bundle_name: str = "artifact-bundle",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        artifacts = [await self.artifacts.require_artifact(workspace_id=workspace_id, artifact_id=item) for item in artifact_ids]
        if not artifacts:
            raise ValueError("No artifacts selected for bundle export")
        bundle_id = artifacts[0].id
        bundle_dir = self._export_dir(workspace_id=workspace_id, artifact_id=bundle_id) / "bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        zip_path = bundle_dir / f"{self._safe_name(bundle_name)}.zip"
        manifest = {
            "bundle_name": bundle_name,
            "workspace_id": workspace_id,
            "artifact_ids": [str(item.id) for item in artifacts],
            "metadata": metadata or {},
            "artifacts": [self._manifest_for_artifact(item) for item in artifacts],
        }
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("metadata.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.writestr("timeline.json", json.dumps({"events": [], "note": "Timeline export uses existing artifact metadata only."}, indent=2))
            archive.writestr("diagnostics.json", json.dumps({"diagnostics": [], "note": "No runtime replay was executed."}, indent=2))
            archive.writestr("report.md", self._render_bundle_report(artifacts))
            for index, artifact in enumerate(artifacts, start=1):
                archive.writestr(f"artifacts/{index:03d}-{artifact.id}.json", json.dumps(self._manifest_for_artifact(artifact), ensure_ascii=False, indent=2))
                if artifact.content:
                    archive.writestr(f"artifacts/{index:03d}-{self._safe_name(artifact.title)}.txt", artifact.content)
        generated = await self.artifacts.create_artifact(
            workspace_id=workspace_id,
            source_type=artifacts[0].source_type,
            artifact_type=OutputArtifactType.BUNDLE.value,
            title=f"Bundle export: {bundle_name}",
            summary=f"Bundle ZIP with {len(artifacts)} artifacts",
            file_path=str(zip_path),
            mime_type="application/zip",
            metadata={"bundle": manifest, "export_path": str(zip_path)},
            parent_artifact_id=artifacts[0].id,
            root_artifact_id=artifacts[0].root_artifact_id or artifacts[0].id,
            artifact_role=OutputArtifactRole.BUNDLE.value,
            artifact_stage=OutputArtifactStage.EXPORTED.value,
            generated_by="ArtifactExportService",
            commit=False,
        )
        for artifact in artifacts:
            await self.artifacts.create_relationship(
                workspace_id=workspace_id,
                parent_artifact_id=artifact.id,
                child_artifact_id=generated.id,
                relationship_type="packaged_into",
                metadata={"bundle_path": str(zip_path)},
                commit=False,
            )
        await self.session.commit()
        await self.session.refresh(generated)
        return {"artifact": artifacts[0], "generated_artifact": generated, "output_path": str(zip_path), "metadata": manifest}

    async def export_report_package(self, *, workspace_id: str, artifact_ids: list[UUID], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self.export_bundle_zip(
            workspace_id=workspace_id,
            artifact_ids=artifact_ids,
            bundle_name="report-package",
            metadata={"package_type": "report_package", **(metadata or {})},
        )

    async def _write_text_export(
        self,
        *,
        workspace_id: str,
        artifact: OutputArtifact,
        export_format: str,
        extension: str,
        mime_type: str,
        content: str,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if not artifact.exportable:
            raise ValueError("Output artifact is not exportable")
        export_dir = self._export_dir(workspace_id=workspace_id, artifact_id=artifact.id)
        export_path = export_dir / f"artifact.{extension}"
        export_path.write_text(content, encoding="utf-8")
        artifact_type_by_format = {
            "markdown": OutputArtifactType.MARKDOWN.value,
            "html": OutputArtifactType.HTML.value,
            "json": OutputArtifactType.JSON.value,
            "txt": OutputArtifactType.TEXT.value,
        }
        artifact_type = artifact_type_by_format[export_format]
        generated = await self.artifacts.create_artifact(
            workspace_id=workspace_id,
            source_type=OutputArtifactSourceType.TOOL.value,
            artifact_type=artifact_type,
            title=f"{artifact.title} ({export_format} export)",
            summary=f"Exported from artifact {artifact.id}",
            content=content if len(content) <= self.artifacts.MAX_CONTENT_CHARS else None,
            file_path=str(export_path),
            mime_type=mime_type,
            metadata={"format": export_format, "source_artifact_id": str(artifact.id), "export_path": str(export_path), **(metadata or {})},
            parent_artifact_id=artifact.id,
            root_artifact_id=artifact.root_artifact_id or artifact.id,
            artifact_role=OutputArtifactRole.MARKDOWN.value if export_format == "markdown" else self.artifacts._role_from_artifact_type(artifact_type),
            artifact_stage=OutputArtifactStage.EXPORTED.value,
            generated_by="ArtifactExportService",
            commit=False,
        )
        await self.artifacts.create_relationship(
            workspace_id=workspace_id,
            parent_artifact_id=artifact.id,
            child_artifact_id=generated.id,
            relationship_type="exported_from",
            metadata={"format": export_format, "export_path": str(export_path)},
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(generated)
        return {"artifact": artifact, "generated_artifact": generated, "output_path": str(export_path), "content": content, "metadata": generated.artifact_metadata}

    def _render_markdown(self, artifact: OutputArtifact) -> str:
        return (
            f"# {artifact.title}\n\n"
            f"**Type:** {artifact.artifact_type}\n\n"
            f"**Role:** {artifact.artifact_role or '-'}\n\n"
            f"**Stage:** {artifact.artifact_stage}\n\n"
            f"**Source:** {artifact.source_type}\n\n"
            f"{artifact.summary or ''}\n\n"
            f"{artifact.content or ''}\n\n"
            f"{'File: ' + artifact.file_path if artifact.file_path else ''}\n"
        ).strip()

    def _render_html(self, artifact: OutputArtifact) -> str:
        body = self._render_markdown(artifact).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<!doctype html><html><head><meta charset=\"utf-8\"><title>{artifact.title}</title></head><body><pre>{body}</pre></body></html>"

    def _render_bundle_report(self, artifacts: list[OutputArtifact]) -> str:
        lines = ["# Artifact Bundle", ""]
        for artifact in artifacts:
            lines.append(f"## {artifact.title}")
            lines.append(f"- id: {artifact.id}")
            lines.append(f"- type: {artifact.artifact_type}")
            lines.append(f"- role: {artifact.artifact_role or '-'}")
            if artifact.summary:
                lines.append(f"- summary: {artifact.summary}")
            if artifact.file_path:
                lines.append(f"- file: {artifact.file_path}")
            lines.append("")
        return "\n".join(lines)

    def _manifest_for_artifact(self, artifact: OutputArtifact) -> dict[str, Any]:
        return {
            "id": str(artifact.id),
            "workspace_id": artifact.workspace_id,
            "source_type": artifact.source_type,
            "artifact_type": artifact.artifact_type,
            "artifact_role": artifact.artifact_role,
            "artifact_stage": artifact.artifact_stage,
            "title": artifact.title,
            "summary": artifact.summary,
            "file_path": artifact.file_path,
            "mime_type": artifact.mime_type,
            "parent_artifact_id": str(artifact.parent_artifact_id) if artifact.parent_artifact_id else None,
            "root_artifact_id": str(artifact.root_artifact_id) if artifact.root_artifact_id else None,
            "source_task_run_id": str(artifact.source_task_run_id) if artifact.source_task_run_id else None,
            "source_playbook_run_id": str(artifact.source_playbook_run_id) if artifact.source_playbook_run_id else None,
            "source_conversation_id": str(artifact.source_conversation_id) if artifact.source_conversation_id else None,
            "source_runtime_session_id": str(artifact.source_runtime_session_id) if artifact.source_runtime_session_id else None,
            "metadata": artifact.artifact_metadata or {},
            "created_at": artifact.created_at.isoformat(),
        }

    def _export_dir(self, *, workspace_id: str, artifact_id: UUID) -> Path:
        root = self.export_root.resolve()
        export_dir = (root / self._safe_name(workspace_id) / str(artifact_id) / "exports").resolve()
        if not str(export_dir).startswith(str(root)):
            raise ValueError("Invalid output export path")
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    def _safe_name(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]", "-", value).strip("-") or "artifact"
