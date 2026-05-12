"""文件解析器集合。"""

from app.file_pipeline.parsers.base import FileParser, ParsedFile
from app.file_pipeline.parsers.csv_parser import CSVParser
from app.file_pipeline.parsers.docx_parser import DOCXParser
from app.file_pipeline.parsers.pdf_parser import PDFParser
from app.file_pipeline.parsers.registry import FileParserRegistry
from app.file_pipeline.parsers.text_parser import TextFileParser

__all__ = [
    "CSVParser",
    "DOCXParser",
    "FileParser",
    "FileParserRegistry",
    "PDFParser",
    "ParsedFile",
    "TextFileParser",
]

