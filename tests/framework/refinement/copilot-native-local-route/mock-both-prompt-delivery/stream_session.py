"""Exact public frozen payload delivery only, not skills/cognition/grading."""
import pathlib,hashlib
from provider_fixture import MODEL,final_stream
R=pathlib.Path(__file__).resolve().parent
class GuardFailure(ValueError):pass
class FixtureSession:
 def __init__(self):self.phase=0;self.delivery=None
 def response(self,obj):
  if not isinstance(obj,dict) or obj.get('model')!=MODEL or obj.get('stream') is not True:raise GuardFailure('model/stream envelope')
  if self.phase:raise GuardFailure('one POST ceiling')
  messages=obj.get('messages');texts=[]
  if not isinstance(messages,list):raise GuardFailure('messages required')
  for m in messages:
   if not isinstance(m,dict) or m.get('role')!='user':continue
   c=m.get('content')
   if isinstance(c,str):texts.append(c)
   elif isinstance(c,list):texts.extend(x['text'] for x in c if isinstance(x,dict) and x.get('type')=='text' and isinstance(x.get('text'),str))
  expected=(R/'prompt.txt').read_text();matching=[t for t in texts if expected in t]
  if len(matching)!=1:raise GuardFailure('exact expected prompt not delivered in one user message')
  self.delivery={'channel':'native_CLI_user_prompt_injection_NOT_skill_discovery','prompt_sha256':hashlib.sha256(expected.encode()).hexdigest(),'candidate_sha256':hashlib.sha256((R/'candidate.md').read_bytes()).hexdigest(),'karpathy_sha256':hashlib.sha256((R/'karpathy.md').read_bytes()).hexdigest(),'both_exact_frozen_texts_in_one_user_message':True,'skill_tool_activation_NOT_proven':True,'native_stock_skills_held_not_evaluated':True}
  self.phase=1;return final_stream()
