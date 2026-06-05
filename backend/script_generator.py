import yaml
from models import Script
class ScriptGenerator:
    @staticmethod
    def to_yaml(s:Script)->str:
        return yaml.dump({"script":ScriptGenerator._s(s)},allow_unicode=True,default_flow_style=False,sort_keys=False,width=120)
    @staticmethod
    def to_json(s:Script)->dict:return ScriptGenerator._s(s)
    @staticmethod
    def _s(s:Script)->dict:
        return{"meta":{"title":s.meta.get("title",""),"original_novel":s.meta.get("original_novel",""),"author":s.meta.get("author",""),"genre":s.meta.get("genre",""),"total_acts":s.meta.get("total_acts",len(s.acts)),"total_scenes":s.meta.get("total_scenes",0),"summary":s.meta.get("summary","")},"characters":[{"id":c.id,"name":c.name,"aliases":c.aliases,"role_type":c.role_type,"age":c.age,"gender":c.gender,"personality":c.personality,"background":c.background,"relationships":c.relationships,"first_appearance":c.first_appearance,"arc_summary":c.arc_summary}for c in s.characters],"acts":[{"act_number":a.act_number,"title":a.title,"summary":a.summary,"scenes":[{"scene_id":sc.scene_id,"scene_number":sc.scene_number,"heading":sc.heading,"location":sc.location,"time_of_day":sc.time_of_day,"interior":sc.interior,"summary":sc.summary,"characters_present":sc.characters_present,"beats":[{"type":b.type,"description":b.description,"speaker":b.speaker,"line":b.line,"parenthetical":b.parenthetical,"tone":b.tone,"style":b.style,"shots":b.shots}for b in sc.beats]}for sc in a.scenes]}for a in s.acts],"props":s.props}
