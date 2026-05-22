"""Phase 62I workstation/customer client frontend UX checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_MAIN = ROOT / "worker_console/src/main.tsx"
WEB_STYLES = ROOT / "worker_console/src/styles.css"
DESKTOP_MAIN = ROOT / "worker_console_desktop/src/main.tsx"
DESKTOP_STYLES = ROOT / "worker_console_desktop/src/styles.css"


def test_worker_console_web_exposes_phase_62i_operator_home() -> None:
    text = WEB_MAIN.read_text(encoding="utf-8")
    styles = WEB_STYLES.read_text(encoding="utf-8")

    for token in [
        "Phase 62I",
        "Workstation Operator Home",
        "工作站操作入口",
        "workerConsoleLanguage",
        "language-switch",
        "operator-status-grid",
        "operator-support-grid",
        "local Worker on the current customer machine",
        "不会直接调用 ComfyUI、OpenClaw、真实平台账号",
        'href="#approvals-panel"',
        'href="#tasks-panel"',
        'id="logs-panel"',
    ]:
        assert token in text

    for token in [
        ".operator-home",
        ".language-switch",
        ".operator-status-card",
        ".quick-link-grid",
        ".recovery-list",
    ]:
        assert token in styles


def test_worker_console_desktop_exposes_phase_62i_operator_home() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")
    styles = DESKTOP_STYLES.read_text(encoding="utf-8")

    for token in [
        "Phase 62I",
        "Customer-Machine Operator Home",
        "客户机操作入口",
        "desktopConsoleLanguage",
        "language-switch",
        "operator-status-grid",
        "operator-support-grid",
        "Use Start Runtime to launch worker_client on this machine.",
        "Desktop Console 只控制当前客户机/工作站的本机 Worker",
        'href="#approvals-panel"',
        'href="#tasks-panel"',
        'id="logs-panel"',
    ]:
        assert token in text

    for token in [
        ".operator-home",
        ".language-switch",
        ".operator-status-card",
        ".quick-link-grid",
        ".recovery-list",
    ]:
        assert token in styles


def test_phase_62i_plan_is_documented() -> None:
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    project_status = (ROOT / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_status = (ROOT / "docs/en/PROJECT_STATUS.md").read_text(encoding="utf-8")
    zh_status = (ROOT / "docs/zh/PROJECT_STATUS.md").read_text(encoding="utf-8")
    en_console = (ROOT / "docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    zh_console = (ROOT / "docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")

    for text in (phase_index, current_next, project_status, en_status, zh_status, en_console, zh_console):
        assert "Phase 62I Workstation/Customer Client Frontend UX Alignment" in text
        assert "codex/phase-62i-workstation-client-ux" in text
        assert "worker_console" in text
        assert "worker_console_desktop" in text
        assert "Chinese/English language switching" in text
