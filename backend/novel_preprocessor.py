import re, logging
from models import Chapter
logger = logging.getLogger(__name__)
CHAPTER_PATTERNS=[re.compile(r"第[一二三四五六七八九十百千万\d]+章\s*.+",re.MULTILINE),re.compile(r"第[一二三四五六七八九十百千万\d]+节\s*.+",re.MULTILINE),re.compile(r"Chapter\s*\d+.*",re.IGNORECASE|re.MULTILINE),re.compile(r"^\s*\d+[\.\、\s]+.+",re.MULTILINE)]
class NovelPreprocessor:
    @staticmethod
    def split_chapters(text:str):
        text=text.strip()
        for p in CHAPTER_PATTERNS:
            m=list(p.finditer(text))
            if len(m)>=3:
                chs=[]
                for i,mm in enumerate(m):
                    s=mm.start();e=m[i+1].start() if i+1<len(m) else len(text)
                    chs.append(Chapter(i+1,mm.group().strip()[:80],text[s:e].strip()))
                return chs
        ps=[x.strip() for x in text.split("\n\n") if x.strip()]
        if len(ps)<3:return[Chapter(1,"全文",text)]
        sz=max(len(ps)//3,1)
        return[Chapter(i+1,f"第{i+1}部分","\n\n".join(ps[i*sz:(i+1)*sz]))for i in range(0,len(ps),sz)]
    @staticmethod
    def extract_metadata(text:str):
        m={"title":"","author":""}
        for l in text.split("\n")[:10]:
            l=l.strip()
            x=re.search(r"《(.+?)》",l)
            if x:m["title"]=x.group(1)
            x=re.match(r"作者[：:]\s*(.+)",l)
            if x:m["author"]=x.group(1).strip()
        return m
