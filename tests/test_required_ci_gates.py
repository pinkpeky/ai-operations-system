import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_ci_gates_json_mode_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_required_ci_gates.py", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert any(check["name"] == "required-ci-gates" and check["status"] == "PASS" for check in payload["checks"])


def test_required_ci_gates_expand_frontend_matrix_names() -> None:
    spec = importlib.util.spec_from_file_location("check_required_ci_gates", ROOT / "scripts/check_required_ci_gates.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_required_ci_gates"] = module
    spec.loader.exec_module(module)

    names = module.workflow_job_names(ROOT / ".github/workflows/pr-quality-gates.yml")

    assert "Python docs and runtime gates" in names
    assert "Frontend build (admin_dashboard)" in names
    assert "Frontend build (worker_console)" in names
    assert "Frontend build (worker_console_desktop)" in names
