"""
AI 小说转剧本工具 - AI 分析引擎
===============================
核心模块：将小说文本送入 LLM，分阶段提取角色、场景、对白，生成结构化剧本。

转换流程（四阶段流水线）：
1. 角色提取 → 识别所有角色及其别名、关系
2. 场景切分 → 将每个章节切分为场次
3. 对白与节拍提取 → 每场生成 beats 数组
4. YAML 生成 → 按 Schema 组装输出
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Optional

from openai import AsyncOpenAI

from config import AppConfig
from models import Chapter, Character, Beat, Scene, Act, Script, ConversionResult

logger = logging.getLogger(__name__)

# ============================================================
# Prompt 模板
# ============================================================

CHARACTER_EXTRACT_PROMPT = """你是一位专业的剧本分析师。请从以下小说文本中提取所有角色信息。

要求：
1. 识别所有有姓名或有台词的角色
2. 对每个角色标注别名（同一角色的不同称呼）
3. 推断角色的基本属性

输出 JSON 数组格式：
[
  {
    "id": "char_001",
    "name": "角色名",
    "aliases": ["别名1"],
    "role_type": "主角|配角|反派|龙套",
    "age": 28,
    "gender": "男|女",
    "personality": "性格简述（20字内）",
    "background": "角色背景（50字内）",
    "relationships": [
      {"target": "char_002", "relation": "父子", "description": "描述"}
    ],
    "arc_summary": "角色弧光简述"
  }
]

只输出 JSON，不要其他文字。"""

SCENE_SPLIT_PROMPT = """你是专业的剧本分场师。请将以下章节文本切分为场次。

每场以地点或时间变化为界。输出 JSON 数组：
[
  {
    "scene_id": "scene_001",
    "scene_number": 1,
    "heading": "第1场 内景 地点名 日",
    "location": "具体地点",
    "time_of_day": "日|夜|黄昏|黎明",
    "interior": true,
    "summary": "本场概要（30字内）",
    "characters_present": ["char_001", "char_002"]
  }
]

只输出 JSON，不要其他文字。"""

BEAT_EXTRACT_PROMPT = """你是专业的剧本编剧。请将以下小说场景转换为剧本节拍(beats)。

beats 按时间顺序排列，每个 beat 标注类型。规则：
- action: 环境描写、动作描述
- dialogue: 对白（必须有 speaker，用角色 ID）
- voiceover: 旁白或画外音
- transition: 转场效果
- montage: 时间压缩的蒙太奇段落

输出 JSON 格式：
{
  "beats": [
    {"type": "action", "description": "环境/动作描述"},
    {"type": "dialogue", "speaker": "char_001", "line": "台词", "parenthetical": "", "tone": "愤怒|平静|..."},
    {"type": "voiceover", "speaker": "char_001", "line": "画外音内容"},
    {"type": "transition", "style": "切入|淡出|切黑", "description": "说明"},
    {"type": "montage", "description": "蒙太奇描述", "shots": ["镜头1", "镜头2"]}
  ]
}

重要：对话台词必须从原文中提取，不要编造。只输出 JSON。"""

FINAL_ASSEMBLE_PROMPT = """你是专业剧本统筹。根据以下角色表、幕结构、场次信息，生成完整的剧本 YAML。

严格遵循给定的 YAML Schema：
{{
  "meta": {{"title": "", "summary": "", "genre": "", "total_acts": 0, "total_scenes": 0}},
  "characters": [...],
  "acts": [{{"act_number": 1, "title": "", "summary": "", "scenes": [...]}}],
  "props": [...]
}}

输出纯 JSON（对应的 YAML 由代码生成），不要 markdown 包裹。"""


# ============================================================
# 工具函数
# ============================================================

def _extract_json(text: str) -> dict | list:
    """从 LLM 返回文本中提取 JSON"""
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if json_match:
        text = json_match.group(1)
    start = text.find("[") if text.strip().startswith("[") else text.find("{")
    end = text.rfind("]") if text.strip().startswith("[") else text.rfind("}")
    if start != -1 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


# ============================================================
# AI 分析器
# ============================================================

class AIAnalyzer:
    """AI 分析引擎——四阶段流水线"""

    def __init__(self, config: AppConfig):
        self.config = config
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_base_url,
                timeout=180.0,
            )
        return self._client

    async def convert(self, chapters: list[Chapter], meta: dict,
                      focus_characters: list[str] = None,
                      style_note: str = "") -> ConversionResult:
        """主转换流程（四阶段）"""
        if not focus_characters:
            focus_characters = []

        # 拼接章节摘要给 LLM
        full_text = "\n\n".join(
            f"【第{c.number}章 {c.title}】\n{c.content[:self.config.max_chapter_length]}"
            for c in chapters
        )

        try:
            # 阶段1: 提取角色
            logger.info("阶段1: 提取角色...")
            characters = await self._extract_characters(full_text, focus_characters)

            # 阶段2: 逐章切分场次
            logger.info("阶段2: 切分场次...")
            all_scenes: list[Scene] = []
            for ch in chapters:
                ch_scenes = await self._split_scenes(ch, characters)
                all_scenes.extend(ch_scenes)

            # 阶段3: 逐场生成 beats
            logger.info("阶段3: 生成节拍...")
            semaphore = asyncio.Semaphore(5)
            async def process_scene(scene: Scene) -> Scene:
                async with semaphore:
                    ch = next((c for c in chapters
                               if c.number == int(scene.scene_id.split("_")[1][0])
                               or scene.scene_id.startswith(f"scene_{c.number:03d}")),
                              chapters[0])
                    return await self._extract_beats(scene, ch, characters)
            all_scenes = await asyncio.gather(*[process_scene(s) for s in all_scenes])

            # 阶段4: 组装幕结构
            logger.info("阶段4: 组装剧本...")
            acts = self._assemble_acts(all_scenes, len(chapters))

            script = Script(
                meta={
                    "title": meta.get("title", "未命名剧本"),
                    "original_novel": meta.get("title", ""),
                    "author": meta.get("author", ""),
                    "genre": style_note or "待标注",
                    "total_acts": len(acts),
                    "total_scenes": len(all_scenes),
                    "summary": await self._generate_summary(full_text, style_note),
                },
                characters=characters,
                acts=acts,
            )

            from script_generator import ScriptGenerator
            yaml_output = ScriptGenerator.to_yaml(script)

            return ConversionResult(
                success=True,
                script=script,
                yaml_output=yaml_output,
                summary=script.meta.get("summary", ""),
                chapter_count=len(chapters),
                character_count=len(characters),
                scene_count=len(all_scenes),
            )

        except Exception as e:
            logger.error(f"转换失败: {e}")
            return ConversionResult(success=False, error=str(e))

    # ---- 阶段1: 角色提取 ----

    async def _extract_characters(self, text: str,
                                  focus: list[str]) -> list[Character]:
        user_prompt = f"小说文本：\n{text[:6000]}\n\n提取角色信息。"
        if focus:
            user_prompt += f"\n重点关注角色：{', '.join(focus)}"

        resp = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": CHARACTER_EXTRACT_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3, max_tokens=4096,
        )
        data = _extract_json(resp.choices[0].message.content or "[]")
        if isinstance(data, dict):
            data = data.get("characters", [])
        chars = []
        for d in data:
            if isinstance(d, dict):
                chars.append(Character(
                    id=d.get("id", f"char_{len(chars)+1:03d}"),
                    name=d.get("name", ""),
                    aliases=d.get("aliases", []),
                    role_type=d.get("role_type", ""),
                    age=d.get("age", 0),
                    gender=d.get("gender", ""),
                    personality=d.get("personality", ""),
                    background=d.get("background", ""),
                    relationships=d.get("relationships", []),
                    arc_summary=d.get("arc_summary", ""),
                ))
        return chars

    # ---- 阶段2: 场景切分 ----

    async def _split_scenes(self, chapter: Chapter,
                            characters: list[Character]) -> list[Scene]:
        char_list = ", ".join(f"{c.id}={c.name}" for c in characters[:15])
        user_prompt = (
            f"角色映射：{char_list}\n\n"
            f"章节文本：\n{chapter.content[:5000]}\n\n"
            "将该章节切分为场次（按地点/时间变化为界）。"
        )
        resp = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": SCENE_SPLIT_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3, max_tokens=4096,
        )
        data = _extract_json(resp.choices[0].message.content or "[]")
        if isinstance(data, dict):
            data = data.get("scenes", [])
        scenes = []
        for d in data:
            if isinstance(d, dict):
                scenes.append(Scene(
                    scene_id=d.get("scene_id", f"scene_{len(scenes)+1:03d}"),
                    scene_number=d.get("scene_number", len(scenes) + 1),
                    heading=d.get("heading", ""),
                    location=d.get("location", ""),
                    time_of_day=d.get("time_of_day", ""),
                    interior=d.get("interior", True),
                    summary=d.get("summary", ""),
                    characters_present=d.get("characters_present", []),
                ))
        return scenes

    # ---- 阶段3: 节拍提取 ----

    async def _extract_beats(self, scene: Scene, chapter: Chapter,
                             characters: list[Character]) -> Scene:
        char_list = ", ".join(f"{c.id}={c.name}" for c in characters[:10])
        user_prompt = (
            f"角色映射：{char_list}\n"
            f"地点：{scene.location}，时间：{scene.time_of_day}\n\n"
            f"章节文本：\n{chapter.content[:4000]}\n\n"
            "提取该场景的 beats 数组。对话必须从原文提取，不要编造。"
        )
        resp = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": BEAT_EXTRACT_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4, max_tokens=8192,
        )
        data = _extract_json(resp.choices[0].message.content or "{}")
        if isinstance(data, list):
            data = {"beats": data}
        for b in data.get("beats", []):
            scene.beats.append(Beat(
                type=b.get("type", "action"),
                description=b.get("description", ""),
                speaker=b.get("speaker", ""),
                line=b.get("line", ""),
                parenthetical=b.get("parenthetical", ""),
                tone=b.get("tone", ""),
                style=b.get("style", ""),
                shots=b.get("shots", []),
            ))
        return scene

    # ---- 阶段4: 组装幕结构 ----

    def _assemble_acts(self, scenes: list[Scene],
                       chapter_count: int) -> list[Act]:
        """按三幕结构分配场次"""
        total = max(len(scenes), 1)
        act_structure = [
            (1, "第一幕：建置", 0, total // 3),
            (2, "第二幕：对抗", total // 3, 2 * total // 3),
            (3, "第三幕：结局", 2 * total // 3, total),
        ]
        acts = []
        for act_num, title, start, end in act_structure:
            acts.append(Act(
                act_number=act_num,
                title=title,
                summary=f"包含第{start+1}至第{min(end, total)}场",
                scenes=scenes[start:end],
            ))
        return acts

    async def _generate_summary(self, text: str, style: str) -> str:
        user_prompt = f"小说内容：\n{text[:3000]}\n风格：{style or '自动判断'}\n请用一句话概括剧情。只输出这句话，不要其他。"
        resp = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.5, max_tokens=200,
        )
        return resp.choices[0].message.content.strip().strip('"').strip("'")
