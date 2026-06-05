"""
AI 小说转剧本工具 - 测试套件
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from models import Chapter, Character, Beat, Scene, Act, Script, ConversionResult
from novel_preprocessor import NovelPreprocessor
from script_generator import ScriptGenerator


class TestModels:
    def test_chapter_creation(self):
        c = Chapter(number=1, title="第一章", content="测试内容")
        assert c.number == 1
        assert c.title == "第一章"

    def test_beat_types(self):
        b = Beat(type="dialogue", speaker="char_001", line="你好", tone="平静")
        assert b.type == "dialogue"
        assert b.line == "你好"

    def test_scene_beats(self):
        scene = Scene(scene_id="s1", scene_number=1, heading="测试")
        scene.beats.append(Beat(type="action", description="动作"))
        assert len(scene.beats) == 1

    def test_act_structure(self):
        act = Act(act_number=1, title="第一幕")
        act.scenes.append(Scene(scene_id="s1", scene_number=1, heading="场景"))
        assert act.act_number == 1
        assert len(act.scenes) == 1

    def test_conversion_result(self):
        r = ConversionResult(success=True, chapter_count=5, character_count=12, scene_count=20)
        assert r.success
        assert r.chapter_count == 5


class TestNovelPreprocessor:
    def test_split_with_chapters(self):
        text = "第一章 相遇\n这是第一章内容。\n\n第二章 离别\n这是第二章内容。\n\n第三章 重逢\n这是第三章内容。"
        chapters = NovelPreprocessor.split_chapters(text)
        assert len(chapters) >= 3

    def test_split_arabic_numbers(self):
        text = "第1章 开始\n内容A\n\n第2章 发展\n内容B\n\n第3章 高潮\n内容C\n\n第4章 结局\n内容D"
        chapters = NovelPreprocessor.split_chapters(text)
        assert len(chapters) >= 3

    def test_split_fallback(self):
        text = "段落1\n\n段落2\n\n段落3\n\n段落4\n\n段落5\n\n段落6"
        chapters = NovelPreprocessor.split_chapters(text)
        assert len(chapters) >= 1

    def test_extract_metadata(self):
        text = "《红楼梦》\n作者：曹雪芹\n\n第一章 甄士隐梦幻识通灵"
        meta = NovelPreprocessor.extract_metadata(text)
        assert meta["title"] == "红楼梦"
        assert meta["author"] == "曹雪芹"

    def test_empty_text(self):
        chapters = NovelPreprocessor.split_chapters("")
        assert len(chapters) == 1
        assert chapters[0].number == 1


class TestScriptGenerator:
    def test_yaml_output(self):
        script = Script(
            meta={"title": "测试剧本", "summary": "测试", "total_acts": 1, "total_scenes": 1},
            characters=[Character(id="char_001", name="张三", role_type="主角")],
            acts=[Act(act_number=1, title="第一幕",
                scenes=[Scene(scene_id="scene_001", scene_number=1, heading="第1场 内景 书房 日",
                    beats=[Beat(type="dialogue", speaker="char_001", line="测试台词", tone="平静")])])],
        )
        yaml_str = ScriptGenerator.to_yaml(script)
        assert "测试剧本" in yaml_str
        assert "char_001" in yaml_str
        assert "测试台词" in yaml_str
        assert yaml_str.startswith("script:")

    def test_json_output(self):
        script = Script(
            meta={"title": "测试", "summary": "s", "total_acts": 1, "total_scenes": 1},
            characters=[Character(id="c1", name="X")],
            acts=[Act(act_number=1, scenes=[Scene(scene_id="s1", scene_number=1)])],
        )
        j = ScriptGenerator.to_json(script)
        assert j["meta"]["title"] == "测试"
        assert len(j["characters"]) == 1


class TestIntegration:
    def test_full_pipeline_no_ai(self):
        """测试完整管线（不调用AI，只验证数据结构流转）"""
        text = "第一章 测试\n内容第一段。\n\n第二章 继续\n内容第二段。\n\n第三章 结束\n内容第三段。"
        chapters = NovelPreprocessor.split_chapters(text)
        meta = NovelPreprocessor.extract_metadata(text)
        assert len(chapters) >= 3
        assert isinstance(meta, dict)

    def test_api_health(self):
        from fastapi.testclient import TestClient
        from main import app
        client = TestClient(app)
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_api_convert_empty(self):
        from fastapi.testclient import TestClient
        from main import app
        client = TestClient(app)
        resp = client.post("/api/convert", json={"novel_text": ""})
        assert resp.status_code == 400
