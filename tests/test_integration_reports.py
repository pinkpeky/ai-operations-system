import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_integration_report_generation_to_temp_paths(tmp_path: Path) -> None:
    json_output = tmp_path / "integration_readiness_report.json"
    md_output = tmp_path / "integration_readiness_report.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_integration_report.py",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(md_output),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert json_output.exists()
    assert md_output.exists()
    report = json.loads(json_output.read_text(encoding="utf-8"))
    assert report["phase"] == "54"
    assert report["base_branch"] == "codex/phase-53-release-smoke-test-matrix-preflight"


def test_generated_integration_reports_are_forbidden_by_hygiene() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_runtime_hygiene", ROOT / "scripts/check_runtime_hygiene.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_runtime_hygiene"] = module
    spec.loader.exec_module(module)

    forbidden, reason = module.is_forbidden("release/reports/integration_readiness_report.json")
    assert forbidden is True
    assert "forbidden" in reason
