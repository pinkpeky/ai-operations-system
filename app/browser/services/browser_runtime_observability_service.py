"""Browser Runtime observability and replay service.

Phase 35A records browser runtime timelines, snapshots, and replay metadata.
Replay is deliberately metadata-only: it never re-executes browser actions.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.browser_runtime import (
    BrowserRuntimeEvent,
    BrowserRuntimeReplay,
    BrowserRuntimeSession,
    BrowserRuntimeSnapshot,
)

logger = logging.getLogger(__name__)


class BrowserRuntimeObservabilityService:
    """Record browser runtime debug artifacts with workspace isolation."""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.snapshot_root = Path(self.settings.browser_runtime_snapshot_dir)

    async def append_event(
        self,
        *,
        workspace_id: str,
        runtime_session_id: UUID,
        worker_id: UUID | None,
        event_type: str,
        status: str = "completed",
        message: str | None = None,
        payload: dict[str, Any] | None = None,
        duration_ms: int | None = None,
        error: str | None = None,
        commit: bool = False,
    ) -> BrowserRuntimeEvent:
        """Append one timeline event."""

        event = BrowserRuntimeEvent(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session_id,
            worker_id=worker_id,
            event_type=event_type,
            status=status,
            message=message,
            payload=self._json_safe(payload or {}),
            duration_ms=duration_ms,
            error=error,
        )
        self.session.add(event)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(event)
        logger.info(
            "Browser runtime event appended",
            extra={
                "workspace_id": workspace_id,
                "runtime_session_id": str(runtime_session_id),
                "event_type": event_type,
                "status": status,
            },
        )
        return event

    async def capture_page_snapshot(
        self,
        *,
        runtime_session: BrowserRuntimeSession,
        page_data: dict[str, Any],
        commit: bool = False,
    ) -> BrowserRuntimeSnapshot:
        """Persist current page HTML/text snapshot metadata."""

        html = str(page_data.get("content") or page_data.get("html") or "")
        text = self._html_to_text(html)
        page_title = page_data.get("page_title") or page_data.get("title")
        url = page_data.get("current_url") or page_data.get("url") or (runtime_session.runtime_metadata or {}).get("current_url")

        snapshot = BrowserRuntimeSnapshot(
            workspace_id=runtime_session.workspace_id,
            runtime_session_id=runtime_session.id,
            snapshot_type="page",
            url=url,
            page_title=page_title,
            snapshot_metadata={
                "content_length": len(html),
                "text_length": len(text),
                "source": "get_page",
            },
        )
        self.session.add(snapshot)
        await self.session.flush()

        session_dir = self._session_dir(runtime_session.workspace_id, runtime_session.id)
        html_path = session_dir / f"page-{snapshot.id}.html"
        text_path = session_dir / f"page-{snapshot.id}.txt"
        html_path.write_text(html, encoding="utf-8")
        text_path.write_text(text, encoding="utf-8")
        snapshot.html_path = str(html_path)
        snapshot.text_path = str(text_path)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(snapshot)
        return snapshot

    async def capture_screenshot_snapshot(
        self,
        *,
        runtime_session: BrowserRuntimeSession,
        screenshot_path: str | None,
        metadata: dict[str, Any] | None = None,
        commit: bool = False,
    ) -> BrowserRuntimeSnapshot:
        """Record screenshot snapshot metadata without overwriting the image file."""

        runtime_metadata = runtime_session.runtime_metadata or {}
        snapshot = BrowserRuntimeSnapshot(
            workspace_id=runtime_session.workspace_id,
            runtime_session_id=runtime_session.id,
            snapshot_type="screenshot",
            url=runtime_metadata.get("current_url"),
            page_title=runtime_metadata.get("page_title"),
            screenshot_path=screenshot_path,
            snapshot_metadata=self._json_safe(metadata or {}),
        )
        self.session.add(snapshot)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(snapshot)
        return snapshot

    async def capture_error_snapshot(
        self,
        *,
        runtime_session: BrowserRuntimeSession,
        action_type: str,
        error: str,
        payload: dict[str, Any] | None = None,
        duration_ms: int | None = None,
        commit: bool = False,
    ) -> BrowserRuntimeSnapshot:
        """Capture structured failure context for later debugging."""

        runtime_metadata = runtime_session.runtime_metadata or {}
        snapshot = BrowserRuntimeSnapshot(
            workspace_id=runtime_session.workspace_id,
            runtime_session_id=runtime_session.id,
            snapshot_type="error",
            url=runtime_metadata.get("current_url") or (payload or {}).get("url"),
            page_title=runtime_metadata.get("page_title"),
            snapshot_metadata={
                "action_type": action_type,
                "error": error,
                "duration_ms": duration_ms,
                "payload": self._json_safe(payload or {}),
                "last_known_url": runtime_metadata.get("current_url"),
                "last_page_title": runtime_metadata.get("page_title"),
            },
        )
        self.session.add(snapshot)
        await self.session.flush()

        session_dir = self._session_dir(runtime_session.workspace_id, runtime_session.id)
        error_path = session_dir / f"error-{snapshot.id}.json"
        error_payload = {
            "snapshot_id": str(snapshot.id),
            "runtime_session_id": str(runtime_session.id),
            "worker_id": str(runtime_session.worker_id),
            "action_type": action_type,
            "error": error,
            "duration_ms": duration_ms,
            "metadata": snapshot.snapshot_metadata,
            "created_at": datetime.now(UTC).isoformat(),
        }
        error_path.write_text(json.dumps(error_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        snapshot.snapshot_metadata = {**snapshot.snapshot_metadata, "error_path": str(error_path)}
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(snapshot)
        return snapshot

    async def list_events(
        self,
        *,
        workspace_id: str,
        runtime_session_id: UUID,
        limit: int = 100,
    ) -> list[BrowserRuntimeEvent]:
        """List timeline events in chronological order."""

        statement = (
            select(BrowserRuntimeEvent)
            .where(
                BrowserRuntimeEvent.workspace_id == workspace_id,
                BrowserRuntimeEvent.runtime_session_id == runtime_session_id,
            )
            .order_by(BrowserRuntimeEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_snapshots(
        self,
        *,
        workspace_id: str,
        runtime_session_id: UUID,
        snapshot_type: str | None = None,
        limit: int = 100,
    ) -> list[BrowserRuntimeSnapshot]:
        """List snapshots in chronological order."""

        statement = select(BrowserRuntimeSnapshot).where(
            BrowserRuntimeSnapshot.workspace_id == workspace_id,
            BrowserRuntimeSnapshot.runtime_session_id == runtime_session_id,
        )
        if snapshot_type is not None:
            statement = statement.where(BrowserRuntimeSnapshot.snapshot_type == snapshot_type)
        statement = statement.order_by(BrowserRuntimeSnapshot.created_at.asc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_replay(
        self,
        *,
        workspace_id: str,
        runtime_session_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserRuntimeReplay:
        """Create readable replay metadata from events and snapshots."""

        runtime_session = await self._require_session(workspace_id=workspace_id, runtime_session_id=runtime_session_id)
        events = await self.list_events(workspace_id=workspace_id, runtime_session_id=runtime_session_id, limit=1000)
        snapshots = await self.list_snapshots(workspace_id=workspace_id, runtime_session_id=runtime_session_id, limit=1000)
        replay_steps = [
            {
                "event_id": str(event.id),
                "event_type": event.event_type,
                "status": event.status,
                "message": event.message,
                "duration_ms": event.duration_ms,
                "error": event.error,
                "payload": event.payload,
                "created_at": event.created_at.isoformat(),
            }
            for event in events
        ]
        replay = BrowserRuntimeReplay(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session_id,
            replay_status="created",
            replay_steps=replay_steps,
            source_event_ids=[str(event.id) for event in events],
            source_snapshot_ids=[str(snapshot.id) for snapshot in snapshots],
            replay_metadata={
                **(metadata or {}),
                "runtime_session_status": runtime_session.session_status,
                "worker_id": str(runtime_session.worker_id),
                "note": "metadata-only replay; browser actions are not re-executed",
            },
        )
        self.session.add(replay)
        await self.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session_id,
            worker_id=runtime_session.worker_id,
            event_type="replay_requested",
            status="completed",
            message="Browser runtime replay metadata created",
            payload={"metadata": metadata or {}},
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(replay)
        return replay

    async def get_replay(self, *, workspace_id: str, replay_id: UUID) -> BrowserRuntimeReplay | None:
        """Load one replay record in the current workspace."""

        statement = select(BrowserRuntimeReplay).where(
            BrowserRuntimeReplay.workspace_id == workspace_id,
            BrowserRuntimeReplay.id == replay_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def export_replay_json(self, *, workspace_id: str, replay_id: UUID) -> tuple[BrowserRuntimeReplay, Path, dict[str, Any]]:
        """Export replay metadata to a JSON file and return the payload."""

        replay = await self.get_replay(workspace_id=workspace_id, replay_id=replay_id)
        if replay is None:
            raise ValueError("Browser runtime replay not found")
        snapshots = await self.list_snapshots(
            workspace_id=workspace_id,
            runtime_session_id=replay.runtime_session_id,
            limit=1000,
        )
        payload = {
            "replay_id": str(replay.id),
            "workspace_id": replay.workspace_id,
            "runtime_session_id": str(replay.runtime_session_id),
            "replay_status": "exported",
            "replay_steps": replay.replay_steps,
            "source_event_ids": replay.source_event_ids,
            "source_snapshot_ids": replay.source_snapshot_ids,
            "snapshots": [
                {
                    "id": str(snapshot.id),
                    "snapshot_type": snapshot.snapshot_type,
                    "url": snapshot.url,
                    "page_title": snapshot.page_title,
                    "html_path": snapshot.html_path,
                    "text_path": snapshot.text_path,
                    "screenshot_path": snapshot.screenshot_path,
                    "metadata": snapshot.snapshot_metadata,
                    "created_at": snapshot.created_at.isoformat(),
                }
                for snapshot in snapshots
            ],
            "metadata": {
                **(replay.replay_metadata or {}),
                "note": "metadata-only replay; browser actions are not re-executed",
            },
            "exported_at": datetime.now(UTC).isoformat(),
        }
        export_dir = self._session_dir(workspace_id, replay.runtime_session_id)
        export_path = export_dir / f"replay-{replay.id}.json"
        export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        replay.replay_status = "exported"
        replay.replay_metadata = {**(replay.replay_metadata or {}), "export_path": str(export_path)}
        await self.session.commit()
        await self.session.refresh(replay)
        return replay, export_path, payload

    async def _require_session(self, *, workspace_id: str, runtime_session_id: UUID) -> BrowserRuntimeSession:
        statement = select(BrowserRuntimeSession).where(
            BrowserRuntimeSession.workspace_id == workspace_id,
            BrowserRuntimeSession.id == runtime_session_id,
        )
        result = await self.session.execute(statement)
        runtime_session = result.scalar_one_or_none()
        if runtime_session is None:
            raise ValueError("Browser runtime session not found")
        return runtime_session

    def _session_dir(self, workspace_id: str, runtime_session_id: UUID) -> Path:
        """Create and return the scoped snapshot directory."""

        safe_workspace = self._safe_name(workspace_id)
        root = self.snapshot_root.resolve()
        session_dir = (root / safe_workspace / str(runtime_session_id)).resolve()
        if not str(session_dir).startswith(str(root)):
            raise ValueError("Invalid browser runtime snapshot path")
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def _safe_name(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]", "-", value).strip("-") or "workspace"

    def _html_to_text(self, html: str) -> str:
        text = re.sub(r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>", " ", html, flags=re.IGNORECASE)
        text = re.sub(r"<style\b[^<]*(?:(?!</style>)<[^<]*)*</style>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _json_safe(self, value: dict[str, Any]) -> dict[str, Any]:
        """Normalize arbitrary payloads into JSON-compatible dictionaries."""

        try:
            json.dumps(value)
            return value
        except TypeError:
            return json.loads(json.dumps(value, default=str))
