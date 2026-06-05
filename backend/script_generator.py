"""
AI 小说转剧本工具 - YAML 剧本生成器
===================================
将 Script 数据模型序列化为符合 Schema 的 YAML 格式。
"""

from __future__ import annotations

import yaml

from models import Script, Character, Act, Scene, Beat


class ScriptGenerator:
    """将结构化 Script 对象转为 YAML 字符串"""

    @staticmethod
    def to_yaml(script: Script) -> str:
        """生成 YAML 格式剧本"""
        data = {"script": ScriptGenerator._serialize_script(script)}
        return yaml.dump(
            data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )

    @staticmethod
    def to_json(script: Script) -> dict:
        """生成 JSON 兼容字典（供 API 返回）"""
        return ScriptGenerator._serialize_script(script)

    # ---- 序列化辅助 ----

    @staticmethod
    def _serialize_script(script: Script) -> dict:
        return {
            "meta": {
                "title": script.meta.get("title", ""),
                "original_novel": script.meta.get("original_novel", ""),
                "author": script.meta.get("author", ""),
                "genre": script.meta.get("genre", ""),
                "total_acts": script.meta.get("total_acts", len(script.acts)),
                "total_scenes": script.meta.get("total_scenes", 0),
                "summary": script.meta.get("summary", ""),
            },
            "characters": [ScriptGenerator._serialize_character(c) for c in script.characters],
            "acts": [ScriptGenerator._serialize_act(a) for a in script.acts],
            "props": script.props if script.props else [],
        }

    @staticmethod
    def _serialize_character(c: Character) -> dict:
        return {
            "id": c.id,
            "name": c.name,
            "aliases": c.aliases,
            "role_type": c.role_type,
            "age": c.age,
            "gender": c.gender,
            "personality": c.personality,
            "background": c.background,
            "relationships": c.relationships,
            "first_appearance": c.first_appearance,
            "arc_summary": c.arc_summary,
        }

    @staticmethod
    def _serialize_act(act: Act) -> dict:
        return {
            "act_number": act.act_number,
            "title": act.title,
            "summary": act.summary,
            "scenes": [ScriptGenerator._serialize_scene(s) for s in act.scenes],
        }

    @staticmethod
    def _serialize_scene(scene: Scene) -> dict:
        return {
            "scene_id": scene.scene_id,
            "scene_number": scene.scene_number,
            "heading": scene.heading,
            "location": scene.location,
            "time_of_day": scene.time_of_day,
            "interior": scene.interior,
            "summary": scene.summary,
            "characters_present": scene.characters_present,
            "beats": [ScriptGenerator._serialize_beat(b) for b in scene.beats],
        }

    @staticmethod
    def _serialize_beat(beat: Beat) -> dict:
        base = {"type": beat.type}
        if beat.description:
            base["description"] = beat.description
        if beat.speaker:
            base["speaker"] = beat.speaker
        if beat.line:
            base["line"] = beat.line
        if beat.parenthetical:
            base["parenthetical"] = beat.parenthetical
        if beat.tone:
            base["tone"] = beat.tone
        if beat.style:
            base["style"] = beat.style
        if beat.shots:
            base["shots"] = beat.shots
        return base
