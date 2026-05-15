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
    for phase in [str(number) for number in range(1, 53)]:
        assert f"| {phase} |" in text or f"| {phase}A |" in text or f"| {phase}B |" in text
    for pr_number in ["#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11", "#12"]:
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
    assert "docs/rendered/" in text
