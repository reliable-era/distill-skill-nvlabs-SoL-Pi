"""One final synthetic SSE, no native tool assumptions or inference."""
from provider_fixture import MODEL,final_stream
class GuardFailure(ValueError):
 def __init__(self,code):self.guard_code=code;super().__init__(code)
class FixtureSession:
 def __init__(self):self.phase=0
 def response(self,obj):
  if not isinstance(obj,dict) or obj.get('model')!=MODEL or obj.get('stream') is not True:raise GuardFailure('ENVELOPE_MODEL_OR_STREAM')
  if not isinstance(obj.get('messages'),list):raise GuardFailure('MESSAGES_NOT_LIST')
  if self.phase!=0:raise GuardFailure('PHASE_CEILING')
  self.phase=1;return final_stream()
