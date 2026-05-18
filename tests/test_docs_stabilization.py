import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docs_stabilization_index_files_exist() -> None:
    required = [
        "docs/PHASE_INDEX.md",
        "docs/CURRENT_NEXT_PHASE.md",
        "docs/SYSTEM_BOUNDARIES.md",
        "docs/DOC_RENDER_QA.md",
        "docs/ARCHITECTURE_TIMELINE.md",
    ]
    for relative in required:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.read_text(encoding="utf-8").strip()


def test_phase_index_covers_phase_1_to_52_and_open_prs() -> None:
    text = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# AI Operations System - Phase Index"
    for phase in [str(number) for number in range(1, 53)]:
        assert f"| {phase} |" in text or f"| {phase}A |" in text or f"| {phase}B |" in text
    for pr_number in ["#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11", "#12", "#13"]:
        assert pr_number in text
    assert "Runtime Evolution" in text
    assert "Deployment Evolution" in text


def test_markdown_docs_have_no_bom_or_repeated_question_mark_corruption() -> None:
    for path in (ROOT / "docs").rglob("*.md"):
        data = path.read_bytes()
        assert not data.startswith(b"\xef\xbb\xbf"), str(path)
        text = data.decode("utf-8")
        assert "???" not in text, str(path)
        assert "\ufffd" not in text, str(path)


def test_doc_render_qa_document_defines_soffice_warning_behavior() -> None:
    text = (ROOT / "docs/DOC_RENDER_QA.md").read_text(encoding="utf-8")
    assert "soffice" in text
    assert "WARNING" in text
    assert "PDF conversion succeeds" in text
    assert "docs\\rendered" in text
    assert "docs/rendered/" in text
    assert "docs\nendered" not in text
    assert "ignored QA output directory" in text


def test_docs_have_no_question_mark_separator_pollution() -> None:
    query_marker = re.compile(r"\?[A-Za-z_][A-Za-z0-9_-]*=")
    backtick_separator = re.compile(r"`[^`\n]+`\?`[^`\n]+`")
    phase_separator = re.compile(r"Phase\s+\d+[A-Z]?\s*\?")
    for path in (ROOT / "docs").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            protected = query_marker.sub("__QUERY_MARK__=", line)
            assert not (protected.lstrip().startswith("#") and "?" in protected), f"{path}:{line_number}"
            assert protected.count("?") < 2, f"{path}:{line_number}"
            assert not backtick_separator.search(protected), f"{path}:{line_number}"
            assert not phase_separator.search(protected), f"{path}:{line_number}"


def test_project_status_wording_matches_accepted_mainline_baseline() -> None:
    required_terms = [
        "`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate",
        "PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`",
        "PR #1 and PR #15 are closed as superseded",
        "Phase 56 was reverted and is not active",
    ]
    status_files = [
        "docs/PROJECT_OVERVIEW.md",
        "docs/PHASE_INDEX.md",
        "docs/CURRENT_NEXT_PHASE.md",
        "docs/PROJECT_STATUS.md",
        "docs/en/PROJECT_STATUS.md",
        "docs/zh/PROJECT_STATUS.md",
    ]
    for relative in status_files:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for term in required_terms:
            assert term in text, relative
