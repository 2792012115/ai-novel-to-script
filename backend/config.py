import os
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY",""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL","deepseek-chat"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL","https://api.deepseek.com/v1"))
    llm_temperature: float = 0.4
    llm_max_tokens: int = 8192
    max_chapter_length: int = 12000
    min_chapters: int = 3
    host: str = "0.0.0.0"
    port: int = 8000

config = AppConfig()
