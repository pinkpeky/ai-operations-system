"""文件解析器测试。"""

from pathlib import Path
from types import SimpleNamespace

from app.file_pipeline.parsers.csv_parser import CSVParser
from app.file_pipeline.parsers.docx_parser import DOCXParser
from app.file_pipeline.parsers.pdf_parser import PDFParser
from app.file_pipeline.parsers.registry import FileParserRegistry
from app.file_pipeline.parsers.text_parser import TextFileParser


def test_text_parser_reads_utf8_txt_and_md(tmp_path: Path) -> None:
    """TXT/MD 解析器应按 UTF-8 读取文本。"""

    txt = tmp_path / "demo.txt"
    md = tmp_path / "demo.md"
    txt.write_text("hello upload pipeline", encoding="utf-8")
    md.write_text("# Title\n\nmarkdown content", encoding="utf-8")

    parser = TextFileParser()

    assert parser.parse(txt).text == "hello upload pipeline"
    assert "markdown content" in parser.parse(md).text


def test_csv_parser_uses_pandas_and_preserves_columns(tmp_path: Path) -> None:
    """CSV 解析器应保留列名和行内容。"""

    csv_path = tmp_path / "demo.csv"
    csv_path.write_text("name,value\nalpha,1\nbeta,2\n", encoding="utf-8")

    parsed = CSVParser().parse(csv_path)

    assert "name,value" in parsed.text
    assert "alpha,1" in parsed.text
    assert parsed.metadata["row_count"] == 2
    assert parsed.metadata["columns"] == ["name", "value"]


def test_docx_parser_extracts_paragraphs_and_tables(tmp_path: Path) -> None:
    """DOCX 解析器应抽取段落和表格文本。"""

    class FakeCell:
        def __init__(self, text: str) -> None:
            self.text = text

    class FakeRow:
        cells = [FakeCell("header"), FakeCell("value")]

    class FakeTable:
        rows = [FakeRow()]

    fake_document = SimpleNamespace(
        paragraphs=[SimpleNamespace(text="paragraph text")],
        tables=[FakeTable()],
    )
    parser = DOCXParser(document_factory=lambda path: fake_document)

    parsed = parser.parse(tmp_path / "demo.docx")

    assert "paragraph text" in parsed.text
    assert "header | value" in parsed.text
    assert parsed.metadata["parser"] == "python-docx"


def test_pdf_parser_extracts_page_text(tmp_path: Path) -> None:
    """PDF 解析器应抽取页面文本，不做 OCR。"""

    class FakePage:
        def __init__(self, text: str) -> None:
            self._text = text

        def extract_text(self) -> str:
            return self._text

    fake_reader = SimpleNamespace(pages=[FakePage("first page"), FakePage("second page")])
    parser = PDFParser(reader_factory=lambda path: fake_reader)

    parsed = parser.parse(tmp_path / "demo.pdf")

    assert "first page" in parsed.text
    assert "second page" in parsed.text
    assert parsed.metadata["page_count"] == 2


def test_parser_registry_selects_parser_by_file_type(tmp_path: Path) -> None:
    """注册表应按扩展名选择解析器。"""

    path = tmp_path / "demo.txt"
    path.write_text("registry text", encoding="utf-8")

    parsed = FileParserRegistry(parsers=[TextFileParser()]).parse(path=path, file_type="txt")

    assert parsed.text == "registry text"

