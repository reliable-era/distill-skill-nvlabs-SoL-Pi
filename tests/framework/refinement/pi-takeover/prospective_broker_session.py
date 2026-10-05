"""Prospective owned broker wrapper; not referenced by any launch plan.
Keeps the frozen Session/raw ledger intact; emits separate derived receipts.
"""
import copy,hashlib,json,http.client,threading
from prospective_sse_bridge import SSEBridge
class ProspectiveSession:
 def __init__(self,raw_session,peer_provenance):
  self.raw_session=raw_session;self.peer_provenance=copy.deepcopy(peer_provenance);self.prospective_records=[];self.forward_lock=threading.Lock()
 def __getattr__(self,name):return getattr(self.raw_session,name)
 def forward(self,path,body,emit,connect=http.client.HTTPConnection):
  # All arms serialize prospective POSTs;waiting never extends actor deadline.
  with self.forward_lock:return self._forward(path,body,emit,connect)
 def _forward(self,path,body,emit,connect):
  bridge=SSEBridge(emit);before=self.raw_session.posts
  try:
   return self.raw_session.forward(path,body,bridge.feed,connect=connect)
  finally:
   # Owned budget denial has no request/receipt and must remain zero forwards.
   rows=[r for r in self.raw_session.records if r['request']>before]
   for row in rows:
    if len(rows)!=1:raise RuntimeError('prospective actor permits one in-flight POST')
    peer=row.get('provider_backend');provenance=self.peer_provenance.get(peer,{})
    view=bridge.finish(row.get('stream_eof') is True,provenance)
    raw=view.pop('raw_bytes');derived=view.pop('derived_stream_bytes')
    dest=self.raw_session.root/f'response-{row["request"]}.sse'
    if dest.exists() and dest.read_bytes()!=raw:raise RuntimeError('raw bridge/transport journal mismatch')
    out=self.raw_session.root/f'derived-response-{row["request"]}.sse';out.write_bytes(derived);out.chmod(0o600)
    record={'request':row['request'],'actor':row['actor'],'provider_backend':peer,'provenance':provenance,'raw_sha256':hashlib.sha256(raw).hexdigest(),'derived_sha256':hashlib.sha256(derived).hexdigest(),'accounting_view':view,'derived_bytes_are_consumption_evidence':False,'scope':'prospective only;legacy raw ledger unchanged;not native/grade eligibility'}
    self.prospective_records.append(record)
    ledger=self.raw_session.root/'prospective-ledger.json';ledger.write_text(json.dumps({'protocol':'qwen-dflash-derived-receipts-draft-v1','records':self.prospective_records,'deployed':False},indent=2)+'\n');ledger.chmod(0o600)
