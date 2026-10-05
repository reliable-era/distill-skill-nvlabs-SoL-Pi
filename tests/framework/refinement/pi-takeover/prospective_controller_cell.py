"""Futureprivatepost-actor controller;durablepartialrow beforecapture/drainbeforeclose."""
import pathlib,json,time
from prospective_failure_guard import guard

def persist(path,row):
 path=pathlib.Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(row,indent=2)+'\n');tmp.chmod(0o600);tmp.replace(path)

def run_cell(session,row,path,stop_owned_issuer,capture,grade,teardown,accounting,now=time.monotonic,sleep=time.sleep):
 # Caller supplies frozen owned callbacks;no new actor/POST is permitted here.
 row.update(official_grade_available=False,phase='stopped_actor_pending_capture');persist(path,row)
 def record(result):row['completion_drain']=result;persist(path,row)
 try:
  with guard(session,stop_owned_issuer,record,now=now,sleep=sleep):
   if stop_owned_issuer() is not True:raise RuntimeError('actor not verified stopped beforecapture')
   row['capture']=capture();row['phase']='captured_pending_original_grade';persist(path,row)
   row['grade']=grade();row['official_grade_available']=True
 except Exception as e:
  row['failure']={'type':type(e).__name__,'message':str(e)[:240]};row['phase']='failed_no_inferred_grade';persist(path,row)
 finally:
  # RecordALLcharged/unknownrequests afterpassivegate,BEFOREconnectionteardown.
  try:row['accounting']=accounting();persist(path,row)
  finally:teardown()
  row['teardown_complete']=True;row['accounting_after_teardown']=accounting();persist(path,row)
 return row
