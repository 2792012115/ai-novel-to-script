"""FastAPI 主应用"""
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import time,logging
from config import config
from models import ConvertRequest
from novel_preprocessor import NovelPreprocessor
from ai_analyzer import AIAnalyzer
from script_generator import ScriptGenerator
logging.basicConfig(level=logging.INFO,format="%(asctime)s[%(levelname)s]%(message)s")
logger=logging.getLogger("app")
app=FastAPI(title="AI小说转剧本工具")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
ai=AIAnalyzer(config)
@app.get("/api/health")
async def health():return{"status":"ok","model":config.openai_model}
@app.post("/api/convert")
async def convert(req:ConvertRequest):
    t0=time.time()
    if not req.novel_text.strip():raise HTTPException(400,"文本不能为空")
    chapters=NovelPreprocessor.split_chapters(req.novel_text)
    if len(chapters)<config.min_chapters:raise HTTPException(400,f"需要>=3章,检测到{len(chapters)}章")
    meta=NovelPreprocessor.extract_metadata(req.novel_text)
    if req.novel_title:meta["title"]=req.novel_title
    if req.author:meta["author"]=req.author
    result=await ai.convert(chapters,meta,style_note=req.style_note)
    result.analysis_time_ms=int((time.time()-t0)*1000)
    if not result.success:raise HTTPException(500,result.error)
    return{"success":True,"yaml":result.yaml_output,"summary":result.summary,"chapter_count":result.chapter_count,"character_count":result.character_count,"scene_count":result.scene_count,"analysis_time_ms":result.analysis_time_ms,"script_json":ScriptGenerator.to_json(result.script)}
@app.get("/",response_class=HTMLResponse)
async def index():
    import os;p=os.path.join(os.path.dirname(__file__),"..","frontend","index.html")
    with open(p,encoding="utf-8")as f:return HTMLResponse(f.read())
if __name__=="__main__":
    import uvicorn;uvicorn.run("main:app",host=config.host,port=config.port,reload=True)
