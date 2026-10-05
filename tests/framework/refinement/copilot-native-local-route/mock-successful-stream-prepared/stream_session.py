"""Two-phase fake provider, declared harmless intent tool ONLY. No upstream."""
from provider_fixture import MODEL,tool_stream,final_stream
class FixtureSession:
 def __init__(self):self.phase=0;self.tool_result_seen=False
 def response(self,obj):
  if not isinstance(obj,dict) or obj.get('model')!=MODEL or obj.get('stream') is not True:raise ValueError('fixed model streaming request required')
  messages=obj.get('messages')
  if not isinstance(messages,list):raise ValueError('messages required')
  if self.phase==0:
   declarations=[x.get('function',{}) for x in obj.get('tools',[]) if isinstance(x,dict) and x.get('type')=='function']
   choices=[x for x in declarations if x.get('name')=='report_intent']
   if len(choices)!=1:raise ValueError('declared report_intent required; no fallback to file or shell tools')
   schema=choices[0].get('parameters',{})
   if schema.get('required')!=['intent'] or schema.get('properties',{}).get('intent',{}).get('type')!='string':raise ValueError('unrecognized harmless intent schema')
   body=tool_stream('report_intent',{'intent':'Verify the isolated synthetic streaming fixture.'},{'report_intent'});self.phase=1;return body
  if self.phase==1:
   matching=[m for m in messages if isinstance(m,dict) and m.get('role')=='tool' and m.get('tool_call_id')=='synthetic-call-1']
   if len(matching)!=1:raise ValueError('tool-result follow-up missing or duplicate')
   self.tool_result_seen=True;self.phase=2;return final_stream()
  raise ValueError('fixture two-POST ceiling; no further response')
