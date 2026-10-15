"""Prepare immutable cost-preserving resume snapshot;no model calls.
Evidence from retained raw/native hashes and original summary;never edit raw.
"""
import collections,datetime,json,pathlib
from common import H,private_root,save,sha
from five_xx import record

def main():
 root=private_root();assert not (root/'models-resume-v1-launch.json').exists();rows=json.loads((root/'model-summary.json').read_text());assert len(rows)==92;recount=json.loads((root/'native-5xx-recount.json').read_text());evidence=recount['attempt_native_evidence'];by={v['cell_id']:v for v in rows};http={v['cell_id'] for v in recount['rows'] if v['category']=='final_5xx'};assert len(http)==78
 harness={'g5-023-ours',*[f'g5-027-{a}' for a in ('none','K','Both')],*[f'g5-028-{a}' for a in ('none','K','ours','Both')],*[f'g5-{n:03}-{a}' for n in (29,30) for a in ('none','K','ours','Both')]};assert len(harness)==16;assert not http&harness;pending=http|harness;retained=[r for r in rows if r['cell_id'] not in pending];assert len(retained)==6;prior={};allrows={}
 for r in rows:
  for a in r['attempt_rows']:allrows[a['root']]=dict(a)
 for f in (root/'models').glob('*/g5-*-a*/attempt-result.json'):
  a=json.loads(f.read_text());allrows.setdefault(a['root'],a)
 finished=[]
 for a in allrows.values():
  e=evidence.get(a['root'],{}).get('native_events',{});ended=e.get('connection_infra_failure',False);a['connection_infra_failure']=bool(a.get('connection_infra_failure') or ended);a['ended_on_5xx']=ended;a['historical_original_attempt_root']=a['root'];cid=a['cell_id']
  if cid in pending:prior.setdefault(cid,[]).append(a)
  if a.get('started_utc'):
   epoch=datetime.datetime.fromisoformat(a['started_utc']).timestamp()+a.get('wall_seconds',0);finished.append(dict(epoch=epoch,cell_id=cid,attempt=a['attempt'],ended5xx=ended))
  for event in e.get('native_http5xx_events',[]):
   for status in event['status_codes']:record(root/'http5xx-cells',root/'http5xx-global.jsonl',cid,a['attempt'],status,None,'historical_native_event',event_id=sha(pathlib.Path(__file__))+':'+cid+':'+str(a['attempt'])+':'+str(event['line']),event_time=event.get('event_time'))
 for cid in pending:
  prior.setdefault(cid,[]);prior[cid].sort(key=lambda a:a['attempt']);assert [a['attempt'] for a in prior[cid]]==list(range(1,len(prior[cid])+1));assert len(prior[cid])<5
 # Per-cell historical ledgers contain exactly that cell's events;global raw
 # times unavailable are explicit,event_time=None,observation time is current.
 if (root/'http5xx-global.jsonl').exists():
  grouped=collections.defaultdict(list)
  for line in (root/'http5xx-global.jsonl').read_text().splitlines():v=json.loads(line);grouped[v['cell']].append(v)
  for cid,es in grouped.items():
   p=root/'http5xx-cells'/(cid+'.jsonl');p.parent.mkdir(exist_ok=True)
   with p.open('w') as out:
    for v in es:out.write(json.dumps(v,separators=(',',':'))+'\n')
 snapshot=dict(original_summary_sha256=sha(root/'model-summary.json'),native_recount_sha256=sha(root/'native-5xx-recount.json'),original_rows=92,final5xx_rows=78,final5xx_empty_patch_rows=64,nonempty_final5xx_rows=14,harness_affected_cells=sorted(harness),authorized_recovery_cells=sorted(pending),retained_rows=retained,prior_attempt_rows=prior,last16_finished_attempts=sorted(finished,key=lambda x:x['epoch'])[-16:],all_original_tokens_charged=True,original_raw_records_unchanged=True);save(root/'harness-5xx-recovery.json',snapshot);save(H/'recovery-summary.json',{k:v for k,v in snapshot.items() if k not in ('retained_rows','prior_attempt_rows','last16_finished_attempts')});print('Recovery snapshot:78 final5xx +16 harness,6 retained;all original costs retained,no models.')
if __name__=='__main__':main()
