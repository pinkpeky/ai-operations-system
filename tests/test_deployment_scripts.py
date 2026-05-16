from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_deployment_startup_scripts_exist_and_accept_profiles() -> None:
    scripts = [
        "deployment/windows/start_server_docker.ps1",
        "deployment/windows/start_admin_dashboard.ps1",
        "deployment/windows/start_worker_console.ps1",
        "deployment/windows/start_desktop_console.ps1",
        "deployment/windows/start_client_worker.ps1",
        "deployment/windows/verify_profile.ps1",
        "deployment/mac/start_server_docker.sh",
        "deployment/mac/start_admin_dashboard.sh",
        "deployment/mac/start_worker_console.sh",
        "deployment/mac/start_desktop_console.sh",
        "deployment/mac/start_client_worker.sh",
        "deployment/mac/verify_profile.sh",
    ]

    for script in scripts:
        path = ROOT / script
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "Profile" in text or "PROFILE" in text


def test_release_manifest_references_deployment_profiles() -> None:
    text = (ROOT / "release/manifest.json").read_text(encoding="utf-8")
    assert "deployment_profiles" in text
    assert "generate_env.py" in text
    assert "check_dependencies.py" in text
    assert "check_ports.py" in text
    assert "verify_environment.py" in text

