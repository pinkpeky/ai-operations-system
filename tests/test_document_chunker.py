"""DocumentChunker 测试模块。

验证按字符切分、overlap 和 metadata 保留行为。
"""

import pytest

from app.rag.document_chunker import DocumentChunker


def test_document_chunker_splits_text_with_overlap_and_metadata() -> None:
    """切分时应保留 overlap 和 metadata。"""

    chunker = DocumentChunker()

    chunks = chunker.chunk_text(
        text="abcdefghij",
        metadata={"category": "test"},
        source_id="source-1",
        chunk_size=4,
        chunk_overlap=1,
    )

    assert [chunk.text for chunk in chunks] == ["abcd", "defg", "ghij"]
    assert [chunk.start_char for chunk in chunks] == [0, 3, 6]
    assert all(chunk.metadata["category"] == "test" for chunk in chunks)
    assert all(chunk.metadata["source_id"] == "source-1" for chunk in chunks)


def test_document_chunker_overlap_is_correct() -> None:
    """chunk overlap 必须精确复用上一段尾部字符。"""

    chunker = DocumentChunker()

    chunks = chunker.chunk_text(
        text="abcdefghijkl",
        source_id="overlap-source",
        chunk_size=5,
        chunk_overlap=2,
    )

    assert [chunk.text for chunk in chunks] == ["abcde", "defgh", "ghijk", "jkl"]
    assert chunks[0].text[-2:] == chunks[1].text[:2]
    assert chunks[1].text[-2:] == chunks[2].text[:2]
    assert chunks[2].text[-2:] == chunks[3].text[:2]


def test_document_chunker_rejects_invalid_overlap() -> None:
    """overlap 不能大于或等于 chunk_size。"""

    chunker = DocumentChunker()

    with pytest.raises(ValueError, match="chunk_overlap must be smaller than chunk_size"):
        chunker.chunk_text(text="abcdef", chunk_size=3, chunk_overlap=3)
