"""Apply verified grade-only/mechanical sidecars to frozen G2 audit, never inference.
Raw result files, frozen auditor/analysis and G1 remain unchanged.
"""
import hashlib, json, pathlib, shutil
import audit as original
H=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def main():
    overlays={};proofs=[]
    for sidecar in H.glob('waves/*/grade-and-accounting-repair.json'):
        value=json.loads(sidecar.read_text());raw=sidecar.with_name('calibration-result.json')
        assert sha(raw)==value['original_result_sha256']
        assert value['model_requests_added']==0 and value['model_cell_retries']==0
        result=json.loads(raw.read_text());root=pathlib.Path(result['root'])
        matches=[(i,r) for i,r in enumerate(result['rows']) if r['cell_id']==value['cell_id']];assert len(matches)==1
        index,row=matches[0];d=root/str(index)
        assert original.tree(d/'final-work')==value['captured_work_hashes']==row['captured_work_hashes']
        assert sha(d/'native.jsonl')==value['native_trace_sha256']==row['native_trace_sha256']
        log=pathlib.Path(value['grade_replay_log']);assert sha(log)==value['grade_replay_log_sha256']
        # Original pre-grade transport exception produced no verifier log. Preserve
        # the separate replay artifact and explicitly expose its exact-byte copy.
        projected_log=d/'verifier.log'
        if projected_log.exists():assert sha(projected_log)==sha(log)
        else:shutil.copy2(log,projected_log)
        row.update(value['updates']);overlays[raw.resolve()]=json.dumps(result)
        proofs.append(dict(sidecar=str(sidecar),sha256=sha(sidecar),original_result_sha256=sha(raw),cell_id=value['cell_id']))
    read_text=pathlib.Path.read_text
    def read_projection(path,*args,**kwargs):
        return overlays[path.resolve()] if path.resolve() in overlays else read_text(path,*args,**kwargs)
    try:
        pathlib.Path.read_text=read_projection
        result=original.audit('aider-polyglot')
    finally:pathlib.Path.read_text=read_text
    result['repair_sidecars']=proofs
    result['raw_results_unchanged']=True
    result['model_retries']=0
    result['unknown_costs_retained']=True
    out=H/'audits/aider.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print('Verified sidecar projections:',len(proofs),'unknown-cost cells:',sum(not r['cost_complete'] for r in result['rows']))
if __name__=='__main__':main()
