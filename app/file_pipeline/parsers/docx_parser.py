"""DOCX 文件解析器。"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.file_pipeline.parsers.base import ParsedFile

logger = logging.getLogger(__name__)


class DOCXParser:
    """使用 python-docx 抽取段落和表格文本。"""

    supported_types = {"docx"}

    def __init__(self, document_factory: Callable[[str], Any] | None = None) -> None:
        self.document_factory = document_factory

    def parse(self, path: Path) -> ParsedFile:
        """抽取 DOCX 段落和表格文本。"""

        try:
            document_factory = self.document_factory
            if document_factory is None:
                from docx import Document

                document_factory = Document
            document = document_factory(str(path))
            parts: list[str] = []
            for paragraph in document.paragraphs:
                if paragraph.text.strip():
                    parts.append(paragraph.text)
            for table in document.tables:
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if cells:
                        parts.append(" | ".join(cells))
            text = "\n".join(parts)
            if not text.strip():
                raise ValueError("DOCX does not contain extractable text")
            logger.info("DOCX parsed", extra={"path": str(path)})
            return ParsedFile(text=text, metadata={"parser": "python-docx"})
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("DOCX parse failed", extra={"path": str(path)})
            raise RuntimeError("DOCX parse failed") from exc

