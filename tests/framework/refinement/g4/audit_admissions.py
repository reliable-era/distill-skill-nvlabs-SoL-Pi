"""Independent raw8000 admission/scheduler-observation history audit, no calls.
Not a continuous empirical occupied-slot trace: reported occupied counts +
frozen16-worker/exclusive-lock proofs must be combined with launch/cleanup
bindings. Shared runtime UTC is not externally notarized; later load can vary.
"""
import argparse,datetime,json,pathlib
from native import H,sha
from transport import save

def zero(load):
 if not isinstance(load,dict) or load.get('backend')!='127.0.0.1:8000' or load.get('path')!='/get_load' or load.get('status')!=200:return False
 rows=load.get('body')
 return isinstance(rows,list) and bool(rows) and all(isinstance(r,dict) and type(r.get('num_waiting_reqs')) is int and r['num_waiting_reqs']==0 for r in rows)
def key(load):return json.dumps(load,sort_keys=True,separators=(',',':'))
def audit(windows):
 proofs=[];errors=[];pending=[];histories=[]
 for window in windows:
  launch=json.loads((H/f'window-{window}-launch.json').read_text());root=pathlib.Path(launch['root']);samples_path=root/'admission-observations.json';samples=json.loads(samples_path.read_text());sample_keys={key(s) for s in samples};cells=json.loads((H/f'windows/{window}.json').read_text())['cells']
  histories.append(dict(window=window,observations=len(samples),zero_wait_observations=sum(zero(s) for s in samples),nonadmissible_observations=sum(not zero(s) for s in samples),observation_sha256=sha(samples_path)))
  for cell in cells:
   directories=sorted(p for p in root.glob(cell+'-a*') if p.is_dir())
   if not directories:pending.append(cell);continue
   for d in directories:
    row_path=d/'attempt-result.json' if (d/'attempt-result.json').exists() else d/'attempt-progress.json'
    if not row_path.exists():pending.append(d.name);continue
    row=json.loads(row_path.read_text())
    if not row.get('native_started'):pending.append(d.name+': not native admitted');continue
    admission_path=d/'admission.json';a=json.loads(admission_path.read_text());load=a['load'];ledger=json.loads((d/'transport/ledger.json').read_text());bad=[];slots=a.get('occupied_slots_after_admission')
    if not zero(load):bad.append('not exact8000/all-backend waiting0')
    if type(slots) is not int or not 1<=slots<=16:bad.append('reported occupied slots invalid')
    if a['cell_id']!=cell or a['attempt']!=row['attempt']:bad.append('cell/attempt identity')
    if key(load) not in sample_keys:bad.append('exact callback load absent from scheduler observation history')
    load_utc=datetime.datetime.fromisoformat(load['utc']);started=datetime.datetime.fromisoformat(row['started_utc'])
    if started<load_utc:bad.append('native start precedes load proof')
    first=min((datetime.datetime.fromisoformat(r['started_utc']) for r in ledger['records']),default=None)
    if first is not None and first<started:bad.append('provider POST precedes native admission')
    if bad:errors.append(dict(attempt=d.name,checks=bad))
    proofs.append(dict(window=window,cell_id=cell,attempt=row['attempt'],reported_occupied_slots=slots,advertised_backend_count=len(load['body']),load_to_native_start_seconds=(started-load_utc).total_seconds(),native_start_to_first_POST_seconds=(first-started).total_seconds() if first else None,admission_sha256=sha(admission_path),all_checks_passed=not bad))
 r=dict(windows=windows,proofs=proofs,histories=histories,pending=pending,errors=errors,all_started_admissions_verified=not errors,all_planned_admissions_verified=not pending and not errors,limitations=['Reported occupied counts are not a continuous independent slot trace; combine frozen16-worker/exclusive-lock code, original regrade12-slot bound and later exclusive4-slot launches with final cleanup/launch chronology','Runtime UTC is shared, not externally notarized','Admission verifies sampled all-backend waiting0, not future load or absence of other workloads'],auditor_sha256=sha(__file__),model_calls=0,metadata_calls=0,not_a_completion_audit=True);save(H/'admission-history-audit.json',r);return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('windows',nargs='+');a=p.parse_args();r=audit(a.windows);print('Admission proofs',len(r['proofs']),'pending',r['pending'],'errors',r['errors'])
