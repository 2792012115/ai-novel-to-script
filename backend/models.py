"""
AI 小说转剧本工具 - 数据模型
============================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================
class ConvertRequest(BaseModel):
    novel_text: str = Field(..., description="小说原文（≥3章）")
    novel_title: str = Field("", description="小说标题")
    author: str = Field("", description="原作者")
    focus_characters: list[str] = Field(default_factory=list, description="重点关注角色")
    style_note: str = Field("", description="改编风格（如：悬疑/喜剧/正剧）")


# ============================================================
# 内部数据模型 (dataclass, 便于 AI 引擎内部传递)
# ============================================================

@dataclass
class Chapter:
    """小说章节"""
    number: int
    title: str = ""
    content: str = ""
    summary: str = ""


@dataclass
class Character:
    """角色"""
    id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    role_type: str = ""
    age: int = 0
    gender: str = ""
    personality: str = ""
    background: str = ""
    relationships: list[dict] = field(default_factory=list)
    first_appearance: str = ""
    arc_summary: str = ""


@dataclass
class Beat:
    """剧本节拍"""
    type: str  # action / dialogue / transition / voiceover / montage
    description: str = ""
    speaker: str = ""
    line: str = ""
    parenthetical: str = ""
    tone: str = ""
    style: str = ""
    shots: list[str] = field(default_factory=list)


@dataclass
class Scene:
    """剧本场次"""
    scene_id: str
    scene_number: int
    heading: str = ""
    location: str = ""
    time_of_day: str = ""
    interior: bool = True
    summary: str = ""
    characters_present: list[str] = field(default_factory=list)
    beats: list[Beat] = field(default_factory=list)


@dataclass
class Act:
    """剧本幕"""
    act_number: int
    title: str = ""
    summary: str = ""
    scenes: list[Scene] = field(default_factory=list)


@dataclass
class Script:
    """完整剧本"""
    meta: dict = field(default_factory=dict)
    characters: list[Character] = field(default_factory=list)
    acts: list[Act] = field(default_factory=list)
    props: list[dict] = field(default_factory=list)


@dataclass
class ConversionResult:
    """转换结果"""
    success: bool = False
    script: Optional[Script] = None
    yaml_output: str = ""
    summary: str = ""
    chapter_count: int = 0
    character_count: int = 0
    scene_count: int = 0
    analysis_time_ms: int = 0
    error: str = ""
