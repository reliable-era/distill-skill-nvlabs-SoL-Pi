"""G2 remaining-cell bounded wave; reuse G1 runtime without writing G1 results."""
import datetime, hashlib, json, pathlib, shutil, subprocess, sys
HERE=pathlib.Path(__file__).resolve().parent
G1=HERE.parent/'g1'
sys.path.insert(0,str(G1))
import run_calibration_continuation as C
import run_calibration as R
PLAN=HERE/'plan.json'
ARMS={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']}
sha=R.sha

def load_plan():
    plan=json.loads(PLAN.read_text())
    # The freeze and complete implementation must exist in git before inference.
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip()
    for name,digest in plan['implementation_sha256'].items():
        p=HERE/name
        if sha(p)!=digest:raise RuntimeError('Preregistered implementation changed: '+name)
        committed=subprocess.check_output(['git','show',head+':tests/framework/refinement/g2/'+name],cwd=HERE)
        if hashlib.sha256(committed).hexdigest()!=digest:raise RuntimeError('Implementation not committed')
    committed=subprocess.check_output(['git','show',head+':tests/framework/refinement/g2/plan.json'],cwd=HERE)
    if committed!=PLAN.read_bytes():raise RuntimeError('Plan not committed')
    for key,skill in plan['skills'].items():
        if R.W.files(skill['path'])!=skill['tree_hashes']:raise RuntimeError('Frozen skill changed: '+key)
    for name,digest in plan['protected_g1_hashes'].items():
        if sha(G1/name)!=digest:raise RuntimeError('Closed G1 changed: '+name)
    return plan

def completed_cells():
    ids=set()
    for p in HERE.glob('waves/*/calibration-launch.json'):
        result=p.with_name('calibration-result.json')
        if not result.exists():raise RuntimeError('Existing wave not terminal; do not duplicate worker')
        value=json.loads(result.read_text())
        root=pathlib.Path(value['root'])
        raw=json.loads((root/'transport/ledger.json').read_text()) if (root/'transport/ledger.json').exists() else {'records':[]}
        ids.update(v['actor'] for v in raw['records'])
        # A started native cell with no POST must be explicitly classified before retry.
        for row in value['rows']:
            if 'native_exit' in row and row.get('cell_id') not in ids:
                raise RuntimeError('Zero-model native attempt needs separate infrastructure classification')
    return ids

def selection(family,round_number,plan):
    if family=='terminal-bench-2':
        path=HERE/'analysis/aider-final.json'
        if not path.exists() or not json.loads(path.read_text())['family_accepted']:
            raise RuntimeError('Terminal stage locked until Aider acceptance')
        raise RuntimeError('Aider passed; commit conditional Terminal execution adapter before any Terminal inference')
    if round_number>1:
        path=HERE/'analysis'/('aider-round-1.json' if family=='aider-polyglot' else 'terminal-round-1.json')
        if not path.exists():raise RuntimeError('Round-1 gate not analyzed')
        gate=json.loads(path.read_text())
        if not gate['evidence_complete'] or gate['round_1_negative_stop']:
            raise RuntimeError('Round-1 futility stop; no later round')
        # A round is independently scheduled, never interleaved with an unfinished earlier round.
        prior=[v for v in plan['schedule'] if v['family']==family and v['round']<round_number]
        if not {v['cell_id'] for v in prior}.issubset(completed_cells()):raise RuntimeError('Previous round unfinished')
    done=completed_cells()
    pending=[v for v in plan['schedule'] if v['family']==family and v['round']==round_number and v['cell_id'] not in done]
    return pending[:6]

def prompt(instruction,spec,task,d):
    plan=load_plan()
    if spec!=plan['task_resource_specs'][task['id']]:raise RuntimeError('Resource recipe changed')
    for key in ARMS[task['arm']]:shutil.copytree(plan['skills'][key]['path'],d/'skills'/key)
    text=instruction+'\n\n'+spec['guidance']+'\n\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
    for key in ARMS[task['arm']]:text+='\n'+(d/'skills'/key/'SKILL.md').read_text()
    if not ARMS[task['arm']]:text+='\nNo skill is supplied.\n'
    return text

def transform(code):
    def replace(old,new):
        nonlocal code
        if code.count(old)!=1:raise RuntimeError('Guarded G2 substitution not unique: '+old[:100])
        code=code.replace(old,new)
    replace("assert contract['arms'] == ['No skill']", "assert set(contract['arms']) == {'none','K','candidate','Both'}")
    replace("'arm':'No skill','family':task['family']", "'arm':task['arm'],'cell_id':task['cell_id'],'round':task['round'],'family':task['family']")
    replace("session.begin(ident,admission[0]['load'])", "session.begin(task['cell_id'],admission[0]['load'])")
    replace("requests=session.accounting_rows(ident)", "requests=session.accounting_rows(task['cell_id'])")
    old="            prompt=instruction+'\\n\\n'+spec['guidance']+'\\n\\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. No skill is supplied.\\n'"
    replace(old,"            prompt=confirmation_prompt(instruction,spec,task,d)")
    replace("plan['continuation_sources']={p.name:sha(p) for p in driver_entries}","plan['continuation_sources']={str(p):sha(p) for p in driver_entries}")
    replace("sha(G/name)!=value for name,value in plan['continuation_sources'].items()", "sha(pathlib.Path(name))!=value for name,value in plan['continuation_sources'].items()")
    replace("    plan['launch_commit'] =", "    plan['g2_plan_sha256']=sha(G2_PLAN)\n    plan['scheduled_cells']=contract['development_pool']\n    plan['launch_commit'] =")
    replace("            if sources()!=live", "            if sha(G2_PLAN)!=plan['g2_plan_sha256']:raise RuntimeError('G2 plan changed')\n            if sources()!=live")
    replace("root = pathlib.Path('/tmp/solpi-g1-cal-'", "root = pathlib.Path('/tmp/solpi-g2-confirm-'")
    replace("            until=time.monotonic()+240", "            if task['family']=='aider-polyglot':\n                work=d/'final-work';work.mkdir();docker('cp',name+':/app/.',str(work))\n                row['captured_work_hashes']=W.files(work)\n            until=time.monotonic()+240")
    replace("                    work=d/'final-work';work.mkdir();docker('cp',name+':/app/.',str(work))", "                    work=d/'final-work';assert work.is_dir()")
    replace("'not_started':[t['id'] for t in contract['development_pool'] if t['id'] not in {r['task'] for r in rows if 'native_exit' in r}]", "'not_started':[t['cell_id'] for t in contract['development_pool'] if t['cell_id'] not in {r['cell_id'] for r in rows if 'native_exit' in r}]")
    replace("'scope':'Step 3 calibration only; no savings or confirmation claim'", "'scope':'G2 sealed confirmation; this wave is not acceptance evidence on its own'")
    return code

def controller(wave,family,round_number):
    plan=load_plan();cells=selection(family,round_number,plan)
    if not cells:raise RuntimeError('No remaining cells in requested round')
    E=HERE/'waves'/wave;E.mkdir(parents=True,exist_ok=True)
    def contract():
        v=json.loads((G1/'calibration-contract.json').read_text())
        v['arms']=list(ARMS);v['phase']='G2 sealed confirmation'
        v['development_pool']=[dict(id=c['task'],source=plan['task_sources'][c['task']],family=c['family'],arm=c['arm'],round=c['round'],cell_id=c['cell_id']) for c in cells]
        return v
    def window_end():
        marker=HERE/'windows'/(wave+'.md')
        value=subprocess.check_output(['git','log','-1','--format=%H|%cI','--',str(marker)],cwd=HERE,text=True).strip()
        if not value:raise RuntimeError('New bounded window not committed')
        commit,stamp=value.split('|',1);start=datetime.datetime.fromisoformat(stamp);end=start+datetime.timedelta(hours=4)
        record=dict(window_commit=commit,window_start=start.isoformat(),window_end=end.isoformat(),latest_start=(end-datetime.timedelta(hours=2)).isoformat(),scheduled_cells=[c['cell_id'] for c in cells])
        path=E/'screen-window.json'
        if path.exists() and json.loads(path.read_text())!=record:raise RuntimeError('Window immutable; no renewal')
        R.save(path,record);return end.timestamp()
    base=C.make_controller(primary_count=999,driver_path=__file__,source_transform=transform)
    base.E=E;base.load_contract=contract;base.window_end=window_end;base.confirmation_prompt=prompt;base.G2_PLAN=PLAN
    base.fixture_spec=lambda ident,ignored:plan['task_resource_specs'][ident]
    return base

if __name__=='__main__':
    p=__import__('argparse').ArgumentParser();p.add_argument('wave');p.add_argument('--family',default='aider-polyglot',choices=['aider-polyglot','terminal-bench-2']);p.add_argument('--round',type=int,default=1,choices=[1,2,3]);a=p.parse_args()
    if not __import__('re').fullmatch(r'[a-z0-9-]+',a.wave):raise RuntimeError('Unsafe wave identifier')
    controller(a.wave,a.family,a.round).main()
