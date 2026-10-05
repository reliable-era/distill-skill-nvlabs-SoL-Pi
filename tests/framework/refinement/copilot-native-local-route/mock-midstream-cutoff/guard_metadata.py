"""Only predefined structural flags/counts; never values, prompts or headers."""
from provider_fixture import MODEL
def describe(obj):
 if not isinstance(obj,dict):return {'object_dict':False}
 tools=obj.get('tools');tools=tools if isinstance(tools,list) else []
 fs=[t.get('function',{}) for t in tools if isinstance(t,dict) and t.get('type')=='function' and isinstance(t.get('function'),dict)]
 intents=[f for f in fs if f.get('name')=='report_intent']
 out={'object_dict':True,'model_matches':obj.get('model')==MODEL,'stream_true':obj.get('stream') is True,'messages_list':isinstance(obj.get('messages'),list),'tools_list':isinstance(obj.get('tools'),list),'tool_count':len(tools),'function_count':len(fs),'intent_declaration_count':len(intents)}
 if len(intents)==1:
  schema=intents[0].get('parameters');schema=schema if isinstance(schema,dict) else {};props=schema.get('properties');props=props if isinstance(props,dict) else {};prop=props.get('intent');prop=prop if isinstance(prop,dict) else {}
  out.update(intent_required_exact=schema.get('required')==['intent'],intent_property_string=prop.get('type')=='string',intent_property_count=len(props))
 return out
