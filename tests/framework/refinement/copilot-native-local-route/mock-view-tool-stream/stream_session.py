"""Declared view ONLY, one owned public marker path, zero inference."""
import json
from provider_fixture import MODEL,tool_stream,final_stream
PATH='/tmp/fresh-home/fixture-marker.txt'
MARKER='SOLPI_PUBLIC_VIEW_MARKER'
class GuardFailure(ValueError):
 def __init__(self,code):self.guard_code=code;super().__init__(code)
class FixtureSession:
 def __init__(self):self.phase=0;self.tool_result_seen=False
 def response(self,obj):
  if not isinstance(obj,dict) or obj.get('model')!=MODEL or obj.get('stream') is not True:raise GuardFailure('ENVELOPE_MODEL_OR_STREAM')
  if not isinstance(obj.get('messages'),list):raise GuardFailure('MESSAGES_NOT_LIST')
  if self.phase==0:
   tools=obj.get('tools',[])
   if not isinstance(tools,list):raise GuardFailure('TOOLS_NOT_LIST')
   funcs=[t.get('function',{}) for t in tools if isinstance(t,dict) and t.get('type')=='function']
   views=[f for f in funcs if isinstance(f,dict) and f.get('name')=='view']
   if len(views)!=1:raise GuardFailure('VIEW_DECLARATION_COUNT')
   schema=views[0].get('parameters',{});props=schema.get('properties',{}) if isinstance(schema,dict) else {};path=props.get('path',{}) if isinstance(props,dict) else {}
   required=schema.get('required',[]) if isinstance(schema,dict) else None
   if not isinstance(required,list) or any(x!='path' for x in required) or not isinstance(path,dict) or path.get('type')!='string':raise GuardFailure('VIEW_PATH_ONLY_SCHEMA')
   self.phase=1;return tool_stream('view',{'path':PATH},{'view'})
  if self.phase==1:
   results=[m for m in obj['messages'] if isinstance(m,dict) and m.get('role')=='tool' and m.get('tool_call_id')=='synthetic-call-1']
   if len(results)!=1:raise GuardFailure('TOOL_RESULT_COUNT')
   if MARKER not in json.dumps(results[0].get('content','')):raise GuardFailure('PUBLIC_MARKER_NOT_IN_RESULT')
   self.tool_result_seen=True;self.phase=2;return final_stream()
  raise GuardFailure('PHASE_CEILING')
