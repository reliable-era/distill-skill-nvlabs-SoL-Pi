"""Independent G2 artifact/receipt audit; never inference or writes to G1."""
import argparse, datetime, hashlib, json, pathlib, re
HERE=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def tree(root):
    root=pathlib.Path(root)
    return {str(p.relative_to(root)):({'symlink_target':str(p.readlink())} if p.is_symlink() else sha(p)) for p in sorted(root.rglob('*')) if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts}

def audit(family):
    plan=json.loads((HERE/'plan.json').read_text());expected={v['cell_id']:v for v in plan['schedule']};rows=[];waves=[]
    for name,digest in plan['implementation_sha256'].items():assert sha(HERE/name)==digest
    for key,skill in plan['skills'].items():assert tree(skill['path'])==skill['tree_hashes']
    for name,digest in plan['protected_g1_hashes'].items():assert sha(HERE.parent/'g1'/name)==digest
    for file in sorted(HERE.glob('waves/*/calibration-result.json')):
        value=json.loads(file.read_text());launch=json.loads(file.with_name('calibration-launch.json').read_text());window=json.loads(file.with_name('screen-window.json').read_text());root=pathlib.Path(value['root'])
        assert launch['g2_plan_sha256']==sha(HERE/'plan.json')
        raw=json.loads((root/'transport/ledger.json').read_text());derived=json.loads((root/'transport/prospective-ledger.json').read_text())['records'];views={v['request']:v for v in derived}
        assert len(raw['records'])==len(derived)==value['POST'];assert value['starts']<=6 and value['POST']<=360
        assert not value['cleanup_errors'] and value['owned_containers_absent']
        for receipt in raw['records']:
            assert receipt['actor'] in expected and receipt['provider_backend']=='127.0.0.1:18001'
            assert receipt['payload_policy']['output_cap']==16384
            assert receipt['observed_queue_before_request'][0]['port']==18001
        for index,row in enumerate(value['rows']):
            if 'native_exit' not in row:continue
            c=expected[row['cell_id']];assert row['task']==c['task'] and row['arm']==c['arm'] and row['round']==c['round'] and row['family']==c['family']
            if row['family']!=family:continue
            assert row['recipe']==plan['task_resource_specs'][row['task']]
            d=root/str(index);assert sha(d/'prompt.txt')==row['prompt_sha256'] and sha(d/'native.jsonl')==row['native_trace_sha256']
            names=plan['arm_skills'][row['arm']];assert sorted(p.name for p in (d/'skills').iterdir())==sorted(names)
            for key in names:assert tree(d/'skills'/key)==plan['skills'][key]['tree_hashes']
            instruction=(d/'prepared/prompt.txt').read_text() if family=='aider-polyglot' else (pathlib.Path(row['source'])/'instruction.md').read_text()
            prompt=instruction+'\n\n'+row['recipe']['guidance']+'\n\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
            for key in names:prompt+='\n'+(d/'skills'/key/'SKILL.md').read_text()
            if not names:prompt+='\nNo skill is supplied.\n'
            assert prompt==(d/'prompt.txt').read_text()
            obs=row['load_at_start'][0];assert obs['status']==200 and all(0<=v['num_reqs']<8 for v in obs['load'])
            assert datetime.datetime.fromisoformat(window['window_start'])<=datetime.datetime.fromisoformat(obs['observed_utc'])<=datetime.datetime.fromisoformat(window['latest_start'])
            receipts=[v for v in raw['records'] if v['actor']==row['cell_id']];assert len(receipts)==row['provider_POST']<=60
            known=bool(receipts) and all(views[v['request']]['accounting_view']['derived_cost']['provider_cost_complete'] for v in receipts)
            tokens=sum(views[v['request']]['accounting_view']['derived_cost'].get('gross_tokens',0) for v in receipts if views[v['request']]['accounting_view']['derived_cost']['provider_cost_complete'])
            assert tokens==row['provider_tokens_lower_bound'] and known==row['cost_complete']
            eof=all(v['provider_status']==200 and v['stream_eof'] and not v['error'] for v in receipts)
            grade_valid=False;test_count=row.get('test_events',0)
            if family=='aider-polyglot':
                prepared=d/'prepared';assert sha(prepared/'grader/grade.py')==plan['grader_sha256']
                manifest=json.loads((prepared/'manifest.json').read_text());assert manifest['task_id']==row['task']
                assert manifest['source_files_sha256']==plan['task_source_hashes'][row['task']]
                assert tree(d/'final-work')==row['captured_work_hashes']
                text=(d/'verifier.log').read_text(errors='replace') if (d/'verifier.log').exists() else ''
                count=re.search(r'Executed accepted tests:\s*(\d+)',text);test_count=int(count.group(1)) if count else 0
                # Original grader exit 1 is an actual solution/test rejection, including
                # syntax/compile/missing-solution failures. Infrastructure is exit 2.
                grade_valid='grade_error' not in row and row.get('verifier_exit') in (0,1) and row.get('solved')==(row['verifier_exit']==0) and (row['verifier_exit']==1 or test_count>0)
            else:grade_valid=row.get('solved') in (True,False) and test_count>0 and 'grade_error' not in row
            rows.append(dict(cell_id=row['cell_id'],task=row['task'],round=row['round'],arm=row['arm'],family=family,
                solved=row['solved'] if grade_valid else None,grade_valid=grade_valid,tests=test_count,cost_complete=known,
                tokens_lower_bound=tokens,provider_eof_valid=eof,requests=len(receipts),native_wall_seconds=row['actor_seconds'],
                heavy_load=row['heavy_load'],cap_hit=len(receipts)>=60 or bool(row.get('actor_deadline_interrupted')),
                result_sha256=sha(file),native_trace_sha256=row['native_trace_sha256']))
        waves.append(dict(wave=file.parent.name,result_sha256=sha(file),error=value['error'],cleanup_errors=value['cleanup_errors'],owned_cleanup=value['owned_containers_absent']))
    ids=[r['cell_id'] for r in rows];assert len(ids)==len(set(ids))
    missing=[v['cell_id'] for v in plan['schedule'] if v['family']==family and v['cell_id'] not in ids]
    result=dict(family=family,plan_sha256=sha(HERE/'plan.json'),rows=rows,waves=waves,missing_cells=missing,
                all_observed_evidence_valid=all(r['grade_valid'] and r['cost_complete'] and r['provider_eof_valid'] for r in rows),
                acceptance_established=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    output=HERE/'audits'/('aider.json' if family=='aider-polyglot' else 'terminal.json');output.parent.mkdir(exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(family=family,finished_cells=len(rows),missing_cells=len(missing),observed_valid=result['all_observed_evidence_valid']),indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--family',default='aider-polyglot',choices=['aider-polyglot','terminal-bench-2']);a=p.parse_args();audit(a.family)
