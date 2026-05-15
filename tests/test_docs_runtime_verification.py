"""Docs Runtime Verification 测试。"""

import subprocess
import sys


def test_docs_runtime_verification_script_passes() -> None:
    """验证脚本应在 docs 与 runtime 同步时返回 PASS。"""

    result = subprocess.run(
        [sys.executable, "scripts/verify_docs_runtime.py"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "SUMMARY: PASS" in result.stdout or "SUMMARY: WARNING" in result.stdout
    assert "PASS:" in result.stdout
    assert "PHASE_INDEX.md title is clean" in result.stdout
    assert "DOC_RENDER_QA.md render paths are intact" in result.stdout
    assert "Project status wording is consistent" in result.stdout
    assert "Markdown question-mark pollution check passed" in result.stdout
