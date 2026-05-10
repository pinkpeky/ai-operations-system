"""文档切分模块。

当前阶段按字符切分文本，并在每个 chunk 中保留来源 metadata。
"""

import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    """文档 chunk 数据结构。"""

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_index: int = 0
    start_char: int = 0
    end_char: int = 0
    source_id: str = ""


class DocumentChunker:
    """按字符切分文档。"""

    def chunk_text(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        source_id: str | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> list[DocumentChunk]:
        """将输入文本切分为多个 DocumentChunk。"""

        try:
            if not text.strip():
                raise ValueError("Text cannot be empty")
            if chunk_size <= 0:
                raise ValueError("chunk_size must be positive")
            if chunk_overlap < 0:
                raise ValueError("chunk_overlap cannot be negative")
            if chunk_overlap >= chunk_size:
                raise ValueError("chunk_overlap must be smaller than chunk_size")

            normalized_source_id = source_id or str(uuid4())
            base_metadata = dict(metadata or {})
            chunks: list[DocumentChunk] = []
            start = 0
            index = 0

            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end]
                chunk_metadata = {
                    **base_metadata,
                    "source_id": normalized_source_id,
                    "chunk_index": index,
                    "start_char": start,
                    "end_char": end,
                }
                chunk_id = str(uuid5(NAMESPACE_URL, f"{normalized_source_id}:{index}:{start}:{end}"))
                chunks.append(
                    DocumentChunk(
                        id=chunk_id,
                        text=chunk_text,
                        metadata=chunk_metadata,
                        chunk_index=index,
                        start_char=start,
                        end_char=end,
                        source_id=normalized_source_id,
                    )
                )
                if end == len(text):
                    break
                start = end - chunk_overlap
                index += 1

            logger.info(
                "Document chunked",
                extra={
                    "source_id": normalized_source_id,
                    "chunk_count": len(chunks),
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                },
            )
            return chunks
        except ValueError:
            logger.exception("Document chunking validation failed")
            raise
        except Exception as exc:
            logger.exception("Document chunking failed")
            raise RuntimeError("Document chunking failed") from exc
