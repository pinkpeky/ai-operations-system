"""Browser runtime replay metadata tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerService
from app.browser.services.browser_runtime_observability_service import BrowserRuntimeObservabilityService
from app.core.config import Settings
from app.models.browser_runtime import BrowserRuntimeSession


@pytest.mark.asyncio
async def test_browser_runtime_replay_export_is_metadata_only(session: AsyncSession, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Replay export should create readable metadata without executing browser actions."""

    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-runtime-replay",
        worker_name="runtime-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser_runtime": True, "browser": "chromium"},
        metadata={},
    )
    runtime_session = BrowserRuntimeSession(
        workspace_id="workspace-runtime-replay",
        worker_id=worker.id,
        provider="remote",
        browser="chromium",
        session_status="active",
        runtime_metadata={"current_url": "https://example.com"},
    )
    session.add(runtime_session)
    await session.commit()
    await session.refresh(runtime_session)

    service = BrowserRuntimeObservabilityService(session, settings=Settings(BROWSER_RUNTIME_SNAPSHOT_DIR=str(tmp_path)))
    await service.append_event(
        workspace_id="workspace-runtime-replay",
        runtime_session_id=runtime_session.id,
        worker_id=worker.id,
        event_type="navigate_completed",
        payload={"url": "https://example.com"},
        commit=True,
    )
    await service.capture_page_snapshot(
        runtime_session=runtime_session,
        page_data={"current_url": "https://example.com", "page_title": "Example Domain", "content": "<h1>Example Domain</h1>"},
        commit=True,
    )

    replay = await service.create_replay(
        workspace_id="workspace-runtime-replay",
        runtime_session_id=runtime_session.id,
        metadata={"reason": "debug"},
    )
    exported_replay, export_path, payload = await service.export_replay_json(
        workspace_id="workspace-runtime-replay",
        replay_id=replay.id,
    )

    assert exported_replay.replay_status == "exported"
    assert Path(export_path).exists()
    assert payload["metadata"]["note"].startswith("metadata-only replay")
    assert payload["replay_steps"][0]["event_type"] == "navigate_completed"
