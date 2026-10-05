"""Predefined booleans/counts, no native payload/schema values or credentials."""
from provider_fixture import MODEL
def describe(obj):
 if not isinstance(obj,dict):return {'object_dict':False}
 tools=obj.get('tools');tools=tools if isinstance(tools,list) else [];fs=[t.get('function',{}) for t in tools if isinstance(t,dict) and t.get('type')=='function' and isinstance(t.get('function'),dict)];views=[f for f in fs if f.get('name')=='view'];out={'model_matches':obj.get('model')==MODEL,'stream_true':obj.get('stream') is True,'messages_list':isinstance(obj.get('messages'),list),'function_count':len(fs),'view_declaration_count':len(views)}
 if len(views)==1:
  s=views[0].get('parameters');s=s if isinstance(s,dict) else {};p=s.get('properties');p=p if isinstance(p,dict) else {};path=p.get('path');path=path if isinstance(path,dict) else {};req=s.get('required');out.update(path_string=path.get('type')=='string',required_list=isinstance(req,list),required_only_path=isinstance(req,list) and all(x=='path' for x in req),property_count=len(p))
 return out
