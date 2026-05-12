"""PDF 文件解析器。"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.file_pipeline.parsers.base import ParsedFile

logger = logging.getLogger(__name__)


class PDFParser:
    """使用 pypdf 抽取 PDF 页面文本。"""

    supported_types = {"pdf"}

    def __init__(self, reader_factory: Callable[[str], Any] | None = None) -> None:
        self.reader_factory = reader_factory

    def parse(self, path: Path) -> ParsedFile:
        """抽取 PDF 中可复制文本；不做 OCR。"""

        try:
            reader_factory = self.reader_factory
            if reader_factory is None:
                from pypdf import PdfReader

                reader_factory = PdfReader
            reader = reader_factory(str(path))
            page_texts = []
            for page_index, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    page_texts.append(text)
                logger.debug("PDF page parsed", extra={"page_index": page_index})
            combined = "\n\n".join(page_texts)
            if not combined.strip():
                raise ValueError("PDF does not contain extractable text")
            logger.info("PDF parsed", extra={"path": str(path), "pages": len(reader.pages)})
            return ParsedFile(text=combined, metadata={"parser": "pypdf", "page_count": len(reader.pages)})
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("PDF parse failed", extra={"path": str(path)})
            raise RuntimeError("PDF parse failed") from exc

