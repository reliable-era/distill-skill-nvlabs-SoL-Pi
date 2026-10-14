"""Whole scheduler lifecycle in isolated temporary fixtures; zero network/Docker.
Exercises fixed adjacency,16 workers,4 image leases,retry accounting/archive.
"""
import contextlib,io,json,pathlib,subprocess,tempfile,threading,time,unittest
from unittest.mock import patch
import model_runs
from common import save,sha
from analyze import panel
class Scheduler(unittest.TestCase):
 def test_rolling_lifecycle_and_retry_last_quality_all_costs(self):self.run_fixture(False)
 def test_shared_preparation_failure_counts_once_for_each_arm(self):self.run_fixture(True)
 def run_fixture(self,preparation_failure):
  with tempfile.TemporaryDirectory(prefix='solpi-g5-test-') as temp:
   root=pathlib.Path(temp);public=root/'public';public.mkdir();tasks=[f'task-{i}' for i in range(8)];queue=[dict(task=t,arm=a,cell_id='g5-'+t+'-'+a,part='C',round=1) for t in tasks for a in ('Both','none','ours','K')];save(root/'queue.json',queue);save(root/'dataset.json',[dict(instance_id=t) for t in tasks]);save(root/'grader-template.json',dict(wheelhouse='fixture'));p=dict(queue_sha256=sha(root/'queue.json'),caps=dict(requests=60,seconds=7200,output_tokens=16384),skills_sha256={'skills/efficient-coding/SKILL.md':'fixture','tests/framework/refinement/g2/frozen/karpathy/SKILL.md':'fixture'});c=dict(eligible_tasks=tasks,control_session='controls-test');mutex=threading.RLock();live=set();max_images=[0];completed={t:0 for t in tasks};starts=[];calls=[]
   for t in tasks:save(root/'controls-test'/t/'final-control.json',dict(valid_pair=True,image_lease=dict(image_id='fixture')))
   class Images:
    def __init__(self,r):pass
    def acquire_control_image(self,iid,lease):
     with mutex:live.add(iid);max_images[0]=max(max_images[0],len(live));assert len(live)<=4
     return lease
    def release(self,iid):
     with mutex:
      if iid in live:assert completed[iid]==4 or (preparation_failure and iid==tasks[0] and completed[iid]==0);live.remove(iid)
   class Watch:
    def __init__(self,*a):pass
    def start(self):pass
    def close(self):pass
   def prep(task,image,d):
    d.mkdir();(d/'proof').write_text('zero-model fixture')
    if preparation_failure and task['instance_id']==tasks[0] and d.name=='source-1':raise subprocess.CalledProcessError(1,['fixture-only'])
   def attempt(cell,n,d,plan,window,callback):
    d.mkdir();assert cell['cell_id'] in window['cells'];callback(cell,n)
    with mutex:starts.append(cell['cell_id']);calls.append((cell['cell_id'],n))
    retry=cell['task']==tasks[0] and cell['arm']=='ours' and n==1;transport=d/'transport';transport.mkdir();save(transport/'ledger.json',dict(budget_denials=[],records=[dict(request=1,provider_status=503 if retry else 200)]));time.sleep(.01)
    row=dict(cell_id=cell['cell_id'],task=cell['task'],arm=cell['arm'],attempt=n,root=str(d),native_started=True,requests=1,known_tokens_lower_bound=13 if retry else 100,cost_complete=not retry,grade_valid=True,solved=retry,timeout=False,grader_timeout=False,owned_cleanup_verified=True,error=None)
    if not retry:
     with mutex:completed[cell['task']]+=1
    save(d/'attempt-result.json',row);return row
   with patch.multiple(model_runs,private_root=lambda:root,verify_barrier=lambda *a:(p,c),H=public,ModelImages=Images,Watch=Watch,prepare=prep,attempt=attempt),contextlib.redirect_stdout(io.StringIO()):model_runs.main('fixture')
   rows=json.loads((root/'model-summary.json').read_text());panel(rows,tasks);self.assertEqual(len(rows),32);self.assertEqual(len(calls),32 if preparation_failure else 33);self.assertFalse(live);self.assertLessEqual(max_images[0],4);self.assertEqual(len(list((root/'archives').glob('*.tar.gz'))),8);self.assertFalse(list((root/'models').glob('*')))
   ours=next(r for r in rows if r['task']==tasks[0] and r['arm']=='ours');self.assertEqual(ours['scored_attempt'],2);self.assertFalse(ours['solved']);self.assertEqual(ours['known_tokens_lower_bound'],100 if preparation_failure else 113);self.assertEqual(ours['cost_complete'],preparation_failure);admissions=json.loads((root/'model-admissions.json').read_text());self.assertEqual(len(admissions),32 if preparation_failure else 33);self.assertTrue(all(1<=r['occupied_slots_after_admission']<=16 for r in admissions));self.assertTrue((root/'models-complete.json').exists())
if __name__=='__main__':unittest.main()
