"""Two-phase fake provider, declared harmless intent tool ONLY. No upstream."""
from provider_fixture import MODEL,tool_stream,final_stream
class GuardFailure(ValueError):
 def __init__(self,code):self.guard_code=code;super().__init__(code)
class FixtureSession:
 def __init__(self):self.phase=0;self.tool_result_seen=False
 def response(self,obj):
  if not isinstance(obj,dict) or obj.get('model')!=MODEL or obj.get('stream') is not True:raise GuardFailure('ENVELOPE_MODEL_OR_STREAM')
  messages=obj.get('messages')
  if not isinstance(messages,list):raise GuardFailure('MESSAGES_NOT_LIST')
  if self.phase==0:
   declarations=[x.get('function',{}) for x in obj.get('tools',[]) if isinstance(x,dict) and x.get('type')=='function']
   choices=[x for x in declarations if x.get('name')=='report_intent']
   if len(choices)!=1:raise GuardFailure('INTENT_DECLARATION_COUNT')
   schema=choices[0].get('parameters',{})
   if schema.get('required')!=['intent'] or schema.get('properties',{}).get('intent',{}).get('type')!='string':raise GuardFailure('INTENT_SCHEMA_UNRECOGNIZED')
   body=tool_stream('report_intent',{'intent':'Verify the isolated synthetic streaming fixture.'},{'report_intent'});self.phase=1;return body
  if self.phase==1:
   matching=[m for m in messages if isinstance(m,dict) and m.get('role')=='tool' and m.get('tool_call_id')=='synthetic-call-1']
   if len(matching)!=1:raise GuardFailure('TOOL_RESULT_COUNT')
   self.tool_result_seen=True;self.phase=2;return final_stream()
  raise GuardFailure('PHASE_CEILING')
