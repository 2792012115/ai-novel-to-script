"""
AI 小说转剧本工具 - 小说预处理引擎
==================================
将原始小说文本切分为章节，提取元信息。
"""

from __future__ import annotations

import re
import logging
from models import Chapter

logger = logging.getLogger(__name__)

# 常见章节标题模式
CHAPTER_PATTERNS = [
    re.compile(r"第[一二三四五六七八九十百千万\d]+章\s*.+", re.MULTILINE),
    re.compile(r"第[一二三四五六七八九十百千万\d]+节\s*.+", re.MULTILINE),
    re.compile(r"Chapter\s*\d+.*", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*\d+[\.\、\s]+.+", re.MULTILINE),  # "1. 标题" 格式
    re.compile(r"^\s*[一二三四五六七八九十]+[\.\、\s]+.+", re.MULTILINE),  # "一、标题"
]


class NovelPreprocessor:
    """
    小说文本预处理器。

    - 自动识别章节边界
    - 清理文本噪声
    - 统计元信息
    """

    @staticmethod
    def split_chapters(text: str) -> list[Chapter]:
        """
        将小说文本按章节切分。
        如果检测不到章节标记，则按等长度切分。
        """
        text = text.strip()

        # 尝试匹配章节
        for pattern in CHAPTER_PATTERNS:
            matches = list(pattern.finditer(text))
            if len(matches) >= 3:  # 至少匹配到 3 个章节才算有效
                chapters = []
                for i, match in enumerate(matches):
                    start = match.start()
                    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                    content = text[start:end].strip()
                    chapters.append(Chapter(
                        number=i + 1,
                        title=match.group().strip()[:80],
                        content=content,
                    ))
                logger.info(f"检测到 {len(chapters)} 个章节 (模式: {pattern.pattern[:50]}...)")
                return chapters

        # 回退：按长段落等分
        logger.warning("未检测到章节标记，按段落长度自动切分")
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paras) < 3:
            return [Chapter(number=1, title="全文", content=text)]

        chunk_size = max(len(paras) // 3, 1)
        chapters = []
        for i in range(0, len(paras), chunk_size):
            chunk = "\n\n".join(paras[i:i + chunk_size])
            chapters.append(Chapter(
                number=len(chapters) + 1,
                title=f"第{len(chapters)+1}部分",
                content=chunk,
            ))
        return chapters

    @staticmethod
    def extract_metadata(text: str) -> dict:
        """提取小说元信息：标题、作者（从文本前几行尝试推断）"""
        lines = text.strip().split("\n")[:10]
        meta = {"title": "", "author": ""}
        for line in lines:
            line = line.strip()
            if re.match(r"《.+》", line):
                meta["title"] = re.search(r"《(.+?)》", line).group(1)
            if re.match(r"作者[：:]\s*.+", line):
                meta["author"] = re.sub(r"作者[：:]\s*", "", line).strip()
        return meta
