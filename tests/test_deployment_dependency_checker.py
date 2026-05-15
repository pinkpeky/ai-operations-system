from deployment.scripts.check_dependencies import dependency_checks


def test_dependency_checker_returns_structured_results() -> None:
    checks = dependency_checks("desktop-client")

    names = {check.name for check in checks}
    assert "node" in names
    assert "npm" in names
    assert "cargo" in names
    assert "tauri-icon" in names
    assert all(check.status in {"PASS", "WARNING", "FAIL"} for check in checks)

