"""测试"""
import sys,os;sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","backend"))
from models import Chapter,Character,Beat,Scene,Act,Script,ConversionResult
from novel_preprocessor import NovelPreprocessor
from script_generator import ScriptGenerator

def test_models():
    assert Chapter(1,"x").number==1
    assert Beat("d",speaker="c",line="hi").line=="hi"
    s=Scene("s",1);s.beats.append(Beat("a"));assert len(s.beats)==1
    a=Act(1);a.scenes.append(Scene("s",1));assert len(a.scenes)==1
    assert ConversionResult(success=True,chapter_count=5).chapter_count==5

def test_preprocessor():
    c=NovelPreprocessor.split_chapters("第一章 相遇\nx\n\n第二章 离\ny\n\n第三章 重\nz")
    assert len(c)>=3
    c2=NovelPreprocessor.split_chapters("第1章 A\na\n\n第2章 B\nb\n\n第3章 C\nc\n\n第4章 D\nd")
    assert len(c2)>=3
    c3=NovelPreprocessor.split_chapters("a\n\nb\n\nc\n\nd\n\ne\n\nf");assert len(c3)>=1
    m=NovelPreprocessor.extract_metadata("《红楼梦》\n作者：曹雪芹\n\n第一章")
    assert m["title"]=="红楼梦" and m["author"]=="曹雪芹"
    c4=NovelPreprocessor.split_chapters("");assert len(c4)==1

def test_generator():
    s=Script(meta={"title":"T","summary":"s","total_acts":1,"total_scenes":1},
             characters=[Character("c1","X")],
             acts=[Act(1,scenes=[Scene("s1",1,beats=[Beat("dialogue",speaker="c1",line="test")])])])
    assert "test" in ScriptGenerator.to_yaml(s)
    j=ScriptGenerator.to_json(s);assert j["meta"]["title"]=="T"

def test_api_health():
    from fastapi.testclient import TestClient;from main import app
    r=TestClient(app).get("/api/health");assert r.status_code==200 and r.json()["status"]=="ok"

def test_api_empty():
    from fastapi.testclient import TestClient;from main import app
    r=TestClient(app).post("/api/convert",json={"novel_text":""});assert r.status_code==400
