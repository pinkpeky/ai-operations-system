"""CSV 文件解析器。"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.file_pipeline.parsers.base import ParsedFile

logger = logging.getLogger(__name__)


class CSVParser:
    """使用 pandas 读取 CSV，并转换为可检索文本。"""

    supported_types = {"csv"}

    def __init__(self, read_csv: Callable[..., Any] | None = None) -> None:
        self.read_csv = read_csv

    def parse(self, path: Path) -> ParsedFile:
        """读取 CSV 并保留列名和行内容。"""

        try:
            read_csv = self.read_csv
            if read_csv is None:
                import pandas as pd

                read_csv = pd.read_csv
            dataframe = read_csv(path)
            if dataframe.empty:
                raise ValueError("CSV does not contain rows")
            dataframe = dataframe.fillna("")
            text = dataframe.to_csv(index=False)
            if not text.strip():
                raise ValueError("CSV does not contain extractable text")
            logger.info("CSV parsed", extra={"path": str(path), "rows": len(dataframe.index)})
            return ParsedFile(
                text=text,
                metadata={"parser": "pandas", "row_count": int(len(dataframe.index)), "columns": list(dataframe.columns)},
            )
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("CSV parse failed", extra={"path": str(path)})
            raise RuntimeError("CSV parse failed") from exc

