from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_desktop_settings_example_matches_required_defaults() -> None:
    settings = json.loads((DESKTOP_ROOT / "settings.example.json").read_text(encoding="utf-8"))

    assert settings == {
        "localWorkerApi": "http://127.0.0.1:9100",
        "minimizeToTray": True,
        "refreshIntervalMs": 5000,
    }


def test_desktop_settings_loader_supports_required_fields() -> None:
    settings_ts = (DESKTOP_ROOT / "src/settings.ts").read_text(encoding="utf-8")

    assert "localWorkerApi" in settings_ts
    assert "minimizeToTray" in settings_ts
    assert "refreshIntervalMs" in settings_ts
    assert "loadDesktopSettings" in settings_ts
    assert "/settings.json" in settings_ts
    assert "VITE_LOCAL_WORKER_API" in settings_ts
