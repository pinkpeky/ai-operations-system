"""文件解析器基础协议。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ParsedFile:
    """文件解析结果。"""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class FileParser(Protocol):
    """所有文件解析器必须实现的协议。"""

    supported_types: set[str]

    def parse(self, path: Path) -> ParsedFile:
        """从文件中抽取文本。"""

