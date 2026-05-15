from deployment.scripts.verify_environment import verify_environment


def test_verify_environment_desktop_client_is_non_destructive() -> None:
    checks = verify_environment("desktop-client")

    names = {check.name for check in checks}
    assert "desktop-frontend-build" in names
    assert "tauri-icon" in names
    assert all(check.status in {"PASS", "WARNING", "FAIL"} for check in checks)

