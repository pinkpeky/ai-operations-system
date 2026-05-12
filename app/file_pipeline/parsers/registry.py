"""文件解析器注册表。"""

import logging
from pathlib import Path

from app.file_pipeline.parsers.base import FileParser, ParsedFile
from app.file_pipeline.parsers.csv_parser import CSVParser
from app.file_pipeline.parsers.docx_parser import DOCXParser
from app.file_pipeline.parsers.pdf_parser import PDFParser
from app.file_pipeline.parsers.text_parser import TextFileParser

logger = logging.getLogger(__name__)


class FileParserRegistry:
    """按文件扩展名选择解析器。"""

    def __init__(self, parsers: list[FileParser] | None = None) -> None:
        self.parsers = parsers or [
            PDFParser(),
            DOCXParser(),
            CSVParser(),
            TextFileParser(),
        ]

    def parse(self, *, path: Path, file_type: str) -> ParsedFile:
        """根据 file_type 解析文件。"""

        normalized_type = file_type.lower().lstrip(".")
        for parser in self.parsers:
            if normalized_type in parser.supported_types:
                logger.info("File parser selected", extra={"file_type": normalized_type, "parser": parser.__class__.__name__})
                return parser.parse(path)
        raise ValueError(f"Unsupported file type: {normalized_type}")

