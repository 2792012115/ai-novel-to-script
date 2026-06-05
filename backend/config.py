"""
AI 小说转剧本工具 - 配置模块
============================
"""

import os
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "deepseek-chat"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"))
    llm_temperature: float = 0.4  # 创作类任务略高温度
    llm_max_tokens: int = 8192    # 剧本生成需要较长输出
    max_chapter_length: int = 12000   # 单章最大字符数
    min_chapters: int = 3             # 最少章节数
    host: str = "0.0.0.0"
    port: int = 8000


config = AppConfig()
