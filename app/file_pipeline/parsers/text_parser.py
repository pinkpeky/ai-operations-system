"""TXT / Markdown 文本解析器。"""

import logging
from pathlib import Path

from app.file_pipeline.parsers.base import ParsedFile

logger = logging.getLogger(__name__)


class TextFileParser:
    """使用 UTF-8 解析普通文本文件。"""

    supported_types = {"txt", "md"}

    def parse(self, path: Path) -> ParsedFile:
        """读取 UTF-8 文本文件。"""

        try:
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise ValueError("File does not contain extractable text")
            logger.info("Text file parsed", extra={"path": str(path)})
            return ParsedFile(text=text, metadata={"parser": "text"})
        except UnicodeDecodeError as exc:
            logger.exception("Text file is not valid UTF-8", extra={"path": str(path)})
            raise ValueError("TXT/MD files must be UTF-8 encoded") from exc
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Text file parse failed", extra={"path": str(path)})
            raise RuntimeError("Text file parse failed") from exc

