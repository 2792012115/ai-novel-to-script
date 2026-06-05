import asyncio,json,logging,re
from typing import Optional
from openai import AsyncOpenAI
from config import AppConfig
from models import Chapter,Character,Beat,Scene,Act,Script,ConversionResult
logger=logging.getLogger(__name__)
CP='[{"id":"char_001","name":"","aliases":[],"role_type":"","age":0,"gender":"","personality":"","background":"","relationships":[],"arc_summary":""}]'
SP='[{"scene_id":"scene_001","scene_number":1,"heading":"","location":"","time_of_day":"","interior":true,"summary":"","characters_present":[]}]'
BP='{"beats":[{"type":"dialogue","speaker":"char_001","line":"","tone":"","parenthetical":""}]}'
def _j(t):
    m=re.search(r"```(?:json)?\s*([\s\S]*?)\s*```",t)
    if m:t=m.group(1)
    s=max(t.find("["),0)if t.strip().startswith("[")else max(t.find("{"),0)
    e=t.rfind("]")if t.strip().startswith("[")else t.rfind("}")
    return json.loads(t[s:e+1])if s!=-1 and e>s else json.loads("{}")
class AIAnalyzer:
    def __init__(self,c:AppConfig):self.c=c;self._cl=None
    @property
    def cl(self):
        if self._cl is None:self._cl=AsyncOpenAI(api_key=self.c.openai_api_key,base_url=self.c.openai_base_url,timeout=180)
        return self._cl
    async def convert(self,chs,m,f=None,s=""):
        ft="\n\n".join(f"【第{c.number}章 {c.title}】\n{c.content[:self.c.max_chapter_length]}"for c in chs)
        try:
            chars=await self._ec(ft,f or[])
            scs=[]
            for c in chs:
                r=await self.cl.chat.completions.create(model=self.c.openai_model,messages=[{"role":"system","content":SP},{"role":"user","content":f"角色:{','.join(x.id+'='+x.name for x in chars[:15])}\n{c.content[:5000]}"}],temperature=.3,max_tokens=4096)
                d=_j(r.choices[0].message.content or"[]")
                if isinstance(d,dict):d=d.get("scenes",[])
                for x in(d if isinstance(d,list)else[]):
                    if isinstance(x,dict):scs.append(Scene(x.get("scene_id",f"scene_{len(scs)+1:03d}"),x.get("scene_number",len(scs)+1),x.get("heading",""),x.get("location",""),x.get("time_of_day",""),x.get("interior",True),x.get("summary",""),x.get("characters_present",[])))
            sem=asyncio.Semaphore(5)
            async def p(sc):
                async with sem:
                    ch=chs[min(len(chs)-1,max(0,int(sc.scene_id.split("_")[1])-1 if sc.scene_id.split("_")[1].isdigit() else 0))]
                    r=await self.cl.chat.completions.create(model=self.c.openai_model,messages=[{"role":"system","content":BP},{"role":"user","content":f"角色:{','.join(x.id+'='+x.name for x in chars[:10])}\n地点:{sc.location}\n{ch.content[:4000]}"}],temperature=.4,max_tokens=8192)
                    d=_j(r.choices[0].message.content or"{}")
                    if isinstance(d,list):d={"beats":d}
                    for b in d.get("beats",[]):sc.beats.append(Beat(b.get("type","action"),b.get("description",""),b.get("speaker",""),b.get("line",""),b.get("parenthetical",""),b.get("tone",""),b.get("style",""),b.get("shots",[])))
                    return sc
            scs=await asyncio.gather(*[p(sc)for sc in scs])
            t=max(len(scs),1)
            acts=[Act(1,"第一幕：建置","",scs[:t//3]),Act(2,"第二幕：对抗","",scs[t//3:2*t//3]),Act(3,"第三幕：结局","",scs[2*t//3:])]
            r=await self.cl.chat.completions.create(model=self.c.openai_model,messages=[{"role":"user","content":f"小说:{ft[:3000]}\n风格:{s or'自动判断'}\n一句话概括。"}],temperature=.5,max_tokens=200)
            sm=r.choices[0].message.content.strip().strip('"').strip("'")
            scr=Script(meta={"title":m.get("title","未命名"),"original_novel":m.get("title",""),"author":m.get("author",""),"genre":s or"待标注","total_acts":len(acts),"total_scenes":len(scs),"summary":sm},characters=chars,acts=acts)
            from script_generator import ScriptGenerator as SG
            return ConversionResult(True,scr,SG.to_yaml(scr),sm,len(chs),len(chars),len(scs))
        except Exception as ex:return ConversionResult(False,error=str(ex))
    async def _ec(self,t,f):
        p=f"小说:\n{t[:6000]}"
        if f:p+=f"\n重点关注:{','.join(f)}"
        r=await self.cl.chat.completions.create(model=self.c.openai_model,messages=[{"role":"system","content":CP},{"role":"user","content":p}],temperature=.3,max_tokens=4096)
        d=_j(r.choices[0].message.content or"[]")
        if isinstance(d,dict):d=d.get("characters",[])
        return[Character(dd.get("id",f"char_{i+1:03d}"),dd.get("name",""),dd.get("aliases",[]),dd.get("role_type",""),dd.get("age",0),dd.get("gender",""),dd.get("personality",""),dd.get("background",""),dd.get("relationships",[]),dd.get("arc_summary","")or"")for i,dd in enumerate(d)if isinstance(dd,dict)]
