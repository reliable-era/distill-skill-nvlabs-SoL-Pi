"""Explicit supervisor-authorized K denominator bounds; frozen math unchanged.
See analysis-notes.md. Never estimate unknown cost or modify raw audit rows.
"""
import argparse, copy, hashlib, json, pathlib
import analyze as frozen
H=pathlib.Path(__file__).resolve().parent
AUTHORIZED='g2-aider-r1-t5-K'
TASK='javascript/exercises/practice/alphametics'

def analyze(rows,tasks,rounds,seed,repetitions=20000):
    computational=copy.deepcopy(rows);bounded=[]
    raw_complete=all(r['grade_valid'] and r['cost_complete'] and r.get('provider_eof_valid',True) for r in rows)
    for row in computational:
        if not row['cost_complete'] or not row.get('provider_eof_valid',True):
            if (row.get('cell_id')==AUTHORIZED and row['arm']=='K' and
                row['round']==1 and row['task']==TASK and row['grade_valid'] and
                row['solved'] is True and row['tokens_lower_bound']>=0):
                bounded.append(row['cell_id'])
                # In-memory mathematical surrogate only: costs are the observed
                # lower bound, NOT imputed totals. Raw flags stay unchanged.
                row['cost_complete']=True;row['provider_eof_valid']=True
    result=frozen.analyze(computational,tasks,rounds,seed,repetitions)
    result['raw_evidence_complete']=raw_complete
    result['bounded_comparator_cells']=bounded
    result['analysis_eligible_under_supervisor_ruling']=result['evidence_complete']
    result['evidence_complete_definition']='Complete mathematical inputs for conservative surrogate under recorded ruling; NOT complete raw provider costs/EOF. See raw_evidence_complete.'
    result['analysis_policy']='SUPERVISOR_K_LOWER_BOUND; not original complete-cost preregistration'
    result['missing_cost_estimated']=False
    if bounded:
        aggregate=result['aggregates']['K'];aggregate['costs_complete']=False
        aggregate['tokens_per_solve_lower_bound']=aggregate['tokens_per_solve']
        aggregate['tokens_per_solve']=None
        aggregate['tokens_relation']='>=';aggregate['tokens_per_solve_relation']='>='
    for key,value in result['comparisons'].items():
        a,b=key.split('/')
        relation='<=' if bounded and b=='K' else '>=' if bounded and a=='K' else '='
        value['true_ratio_relation_to_reported']=relation
        value['bootstrap_interpretation']=('Paired 95% interval for conservative upper-bound surrogate; NOT exact equal-tailed interval for unknown true ratio' if relation=='<=' else 'Paired 95% interval for lower-bound surrogate; no upper-bound acceptance interpretation' if relation=='>=' else 'Original paired task-cluster bootstrap 95% ratio interval')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('audit',type=pathlib.Path);p.add_argument('--rounds',type=int,default=1);p.add_argument('--output',required=True,type=pathlib.Path);args=p.parse_args()
    # Preserve frozen implementation and require recorded notes to predate use.
    plan=json.loads((H/'plan.json').read_text());digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(H/'analyze.py')==plan['implementation_sha256']['analyze.py']
    audit=json.loads(args.audit.read_text());rounds=list(range(1,args.rounds+1));rows=[r for r in audit['rows'] if r['round'] in rounds]
    for row in rows:
        if row.get('cell_id')!=AUTHORIZED:continue
        sidecar=json.loads((H/'waves/aider-r1-w04/grade-and-accounting-repair.json').read_text())
        assert sidecar['updates']['unknown_cost_requests']==[97]
        assert not sidecar['updates']['cost_complete'] and sidecar['updates']['solved'] is True
        assert row['tokens_lower_bound']==sidecar['updates']['provider_tokens_lower_bound']
        assert digest(H/'waves/aider-r1-w04/calibration-result.json')==sidecar['original_result_sha256']
    family=audit['family'];result=analyze(rows,plan['families'][family]['tasks'],rounds,plan['analysis']['bootstrap_seeds'][family],plan['analysis']['bootstrap_repetitions'])
    result['source_evidence']=dict(audit_sha256=digest(args.audit),notes_sha256=digest(H/'analysis-notes.md'),adapter_sha256=digest(pathlib.Path(__file__)),frozen_analysis_sha256=digest(H/'analyze.py'))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('raw_evidence_complete','analysis_eligible_under_supervisor_ruling','round_1_negative_stop','family_accepted','comparisons')},indent=2))
if __name__=='__main__':main()
