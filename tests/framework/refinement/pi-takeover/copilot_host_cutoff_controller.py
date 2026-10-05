"""Host integration of existing owned epoch stop + partial receipt persistence.
Only bounded synthetic cutoff receipts here; never grade or fabricate usage.
"""
import pathlib,hashlib
from prospective_owned_epoch import stop
from prospective_controller_cell import persist
from copilot_owned_issuance_guard import IssuanceGuard
class HostCutoffController:
 def __init__(self,session,context,docker,owned,root,cap=1):
  self.root=pathlib.Path(root)
  if not self.root.is_dir() or self.root.is_symlink():raise ValueError('private existing host directory required')
  if pathlib.Path(context['path']).parent.resolve()!=self.root.resolve():raise ValueError('row must stay in private host directory')
  self.context=context;self.partial=None
  def record(row):
   self.context['row']['issuer_stop_receipt']=row
   persist(self.context['path'],self.context['row'])
  self.guard=IssuanceGuard(cap,lambda:stop(session,context,docker,owned),record)
 def journal_partial(self,body,promised_length):
  if not isinstance(body,bytes) or len(body)>65536 or type(promised_length) is not int or promised_length<=len(body):raise ValueError('bounded incomplete synthetic response required')
  path=self.root/'partial-response.sse'
  with path.open('xb') as f:f.write(body)
  self.partial={'synthetic_ONLY':True,'file':path.name,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'promised_HTTP_length':promised_length,'prepared_NOT_delivery':True,'usage':None,'usage_complete':False}
  self.context['row']['partial_provider_response']=dict(self.partial)
  persist(self.context['path'],self.context['row'])
  return dict(self.partial)
 def stop_before_eof(self):
  if self.partial is None:raise RuntimeError('partial response journal required before stop')
  row=self.guard.abort('known_incomplete_synthetic_HTTP_response')
  if not row['owned_stop_verified']:raise RuntimeError('owned stop unverified; gate failed')
  return row
