"""Packaging script foundation tests."""

from __future__ import annotations

from pathlib import Path


def test_packaging_scripts_exist_and_accept_config_path() -> None:
    """Windows / Mac packaging foundation scripts 应存在并支持 config path。"""

    scripts = [
        Path("packaging/windows_install_requirements.ps1"),
        Path("packaging/windows_register_worker.ps1"),
        Path("packaging/windows_start_worker.ps1"),
        Path("packaging/windows_stop_worker.ps1"),
        Path("packaging/mac_install_requirements.sh"),
        Path("packaging/mac_register_worker.sh"),
        Path("packaging/mac_start_worker.sh"),
        Path("packaging/mac_stop_worker.sh"),
    ]

    for script in scripts:
        content = script.read_text(encoding="utf-8")
        assert script.exists()
        assert "worker_config.yaml" in content or "BaseUrl" in content or "BASE_URL" in content

    assert "python -m worker_client.cli" in Path("packaging/windows_start_worker.ps1").read_text(encoding="utf-8")
    assert "python -m worker_client.cli" in Path("packaging/mac_start_worker.sh").read_text(encoding="utf-8")
