"""Admin Dashboard digital human page checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "admin_dashboard/src/main.tsx"
CLIENT = ROOT / "admin_dashboard/src/api/client.ts"


def test_admin_dashboard_exposes_digital_human_page() -> None:
    text = MAIN.read_text(encoding="utf-8")

    assert '"digital-humans"' in text
    assert "DigitalHumansPage" in text
    assert "Digital human studio" in text
    assert "数字人制作台" in text
    assert "上传人物照片" in text
    assert "Upload portrait" in text
    assert 'uploadAsset("material")' in text
    assert "创建数字人视频任务" in text
    assert "Create video job" in text
    assert "video_job_count" in text
    assert "asset_count" in text
    assert "provider_calls_enabled" in text
    assert "local_musetalk_liveportrait" in text
    assert "digitalHumansApi.capabilities" in text
    assert "digitalHumansApi.uploadAsset" in text
    assert "digitalHumansApi.createVideoJob" in text
    assert "digitalHumansApi.refreshVideoJob" in text
    assert "digitalHumansApi.executeVideoJob" in text
    assert "digitalHumansApi.reviewVideoJob" in text


def test_admin_dashboard_digital_human_api_client_paths() -> None:
    text = CLIENT.read_text(encoding="utf-8")

    assert "export const digitalHumansApi" in text
    assert "/digital-humans/capabilities" in text
    assert "/digital-humans/assets" in text
    assert "/digital-humans/assets${suffix}" in text
    assert "/digital-humans/video-jobs" in text
    assert "/digital-humans/video-jobs${suffix}" in text
    assert "/digital-humans/video-jobs/${encodeURIComponent(jobId)}/refresh" in text
    assert "/digital-humans/video-jobs/${encodeURIComponent(jobId)}/execute" in text
    assert "/digital-humans/video-jobs/${encodeURIComponent(jobId)}/${encodeURIComponent(action)}" in text
