"""
AI 小说转剧本工具 - FastAPI 主应用
==================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from config import config
from models import ConvertRequest, ConversionResult
from novel_preprocessor import NovelPreprocessor
from ai_analyzer import AIAnalyzer
from script_generator import ScriptGenerator

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("novel-to-script")

app = FastAPI(title="AI 小说转剧本工具", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

ai_analyzer = AIAnalyzer(config)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Novel-to-Script", "model": config.openai_model}


@app.post("/api/convert")
async def convert_novel(request: ConvertRequest):
    """核心接口：小说文本 → YAML 剧本"""
    t0 = time.time()

    if not request.novel_text.strip():
        raise HTTPException(status_code=400, detail="小说文本不能为空")

    # 1. 预处理
    chapters = NovelPreprocessor.split_chapters(request.novel_text)
    if len(chapters) < config.min_chapters:
        raise HTTPException(
            status_code=400,
            detail=f"小说至少需要 {config.min_chapters} 个章节，当前检测到 {len(chapters)} 个",
        )
    meta = NovelPreprocessor.extract_metadata(request.novel_text)
    if request.novel_title:
        meta["title"] = request.novel_title
    if request.author:
        meta["author"] = request.author

    # 2. AI 转换
    result = await ai_analyzer.convert(
        chapters, meta,
        focus_characters=request.focus_characters,
        style_note=request.style_note,
    )
    result.analysis_time_ms = int((time.time() - t0) * 1000)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return {
        "success": True,
        "yaml": result.yaml_output,
        "summary": result.summary,
        "chapter_count": result.chapter_count,
        "character_count": result.character_count,
        "scene_count": result.scene_count,
        "analysis_time_ms": result.analysis_time_ms,
        "script_json": ScriptGenerator.to_json(result.script),
    }


@app.get("/api/convert/yaml")
async def convert_yaml_only(novel_text: str):
    """仅返回 YAML 格式（GET 便捷接口，适合 curl 测试）"""
    request = ConvertRequest(novel_text=novel_text)
    resp = await convert_novel(request)
    return PlainTextResponse(content=resp["yaml"], media_type="text/yaml; charset=utf-8")


@app.get("/", response_class=HTMLResponse)
async def index():
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
