"""文件抽取文本清洗工具。"""

import re


class ExtractedTextCleaner:
    """对解析出的文本做轻量清洗，避免破坏原始语义。"""

    def clean(self, text: str) -> str:
        """统一换行、移除空字符并压缩过多空白。"""

        cleaned = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = cleaned.strip()
        if not cleaned:
            raise ValueError("Extracted text is empty after cleaning")
        return cleaned

