from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from pydantic import BaseModel, Field

class ConvertRequest(BaseModel):
    novel_text: str = Field(..., description="小说原文(>=3章)")
    novel_title: str = Field("")
    author: str = Field("")
    style_note: str = Field("")

@dataclass
class Chapter:
    number: int; title: str = ""; content: str = ""

@dataclass
class Character:
    id: str; name: str; aliases: list[str] = field(default_factory=list)
    role_type: str = ""; age: int = 0; gender: str = ""
    personality: str = ""; background: str = ""
    relationships: list[dict] = field(default_factory=list)
    first_appearance: str = ""; arc_summary: str = ""

@dataclass
class Beat:
    type: str; description: str = ""; speaker: str = ""; line: str = ""
    parenthetical: str = ""; tone: str = ""; style: str = ""
    shots: list[str] = field(default_factory=list)

@dataclass
class Scene:
    scene_id: str; scene_number: int; heading: str = ""; location: str = ""
    time_of_day: str = ""; interior: bool = True; summary: str = ""
    characters_present: list[str] = field(default_factory=list)
    beats: list[Beat] = field(default_factory=list)

@dataclass
class Act:
    act_number: int; title: str = ""; summary: str = ""
    scenes: list[Scene] = field(default_factory=list)

@dataclass
class Script:
    meta: dict = field(default_factory=dict)
    characters: list[Character] = field(default_factory=list)
    acts: list[Act] = field(default_factory=list)
    props: list[dict] = field(default_factory=list)

@dataclass
class ConversionResult:
    success: bool = False; script: Optional[Script] = None
    yaml_output: str = ""; summary: str = ""
    chapter_count: int = 0; character_count: int = 0; scene_count: int = 0
    analysis_time_ms: int = 0; error: str = ""
