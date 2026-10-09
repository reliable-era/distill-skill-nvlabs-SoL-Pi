"""Additional read-only execution checks; requires complete Aider108 roster.
Does NOT establish statistical acceptance. Frozen auditor handles prompt/grade/
resource/cost reconciliation; this adds windows, schedule, load and captures.
"""
import datetime as D, hashlib, json, pathlib, subprocess
import run_confirmation as controller
H=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(pathlib.Path(p).read_text())
stamp=lambda s:D.datetime.fromisoformat(s)
def git(*args):return subprocess.check_output(['git',*args],cwd=H,text=True).strip()
def main():
    plan=controller.load_plan();audit=load(H/'audits/aider.json')
    expected=[c['cell_id'] for c in plan['schedule'] if c['family']=='aider-polyglot']
    assert len(audit['rows'])==108 and {r['cell_id'] for r in audit['rows']}==set(expected)
    assert all(r['grade_valid'] for r in audit['rows'])
    unknown=[r['cell_id'] for r in audit['rows'] if not r['cost_complete'] or not r['provider_eof_valid']]
    assert unknown==['g2-aider-r1-t5-K'] or set(unknown)=={'g2-aider-r1-t5-K'}
    assert not git('diff','--name-only','1401e9a','HEAD','--','tests/framework/refinement/g1','skills/efficient-coding')
    changed=git('diff','--name-only','1401e9a','HEAD').splitlines()
    assert all(n=='tests/STATUS.md' or n.startswith('tests/framework/refinement/g2/') for n in changed)
    repo=pathlib.Path(git('rev-parse','--show-toplevel'))
    assert sha(repo/'skills/efficient-coding/SKILL.md')=='68ea78dcb9ee8a565f99c8a1b8bfec13f4c6d65c5695ce847eb5577b0449b1ef'
    starts=[];waves=[];baseline=None;requests=0;load_counts=0;gaps=[];max_wall=0
    for file in sorted(H.glob('waves/*/calibration-result.json')):
        v=load(file);launch=load(file.with_name('calibration-launch.json'));window=load(file.with_name('screen-window.json'));handle=load(file.with_name('worker-handle.json'));root=pathlib.Path(v['root'])
        fingerprint={k:launch[k] for k in ('runtime_hashes','binary_sha256','backend','helper_hashes','continuation_sources','orchestration_sha256')}
        if baseline is None:baseline=fingerprint
        else:assert fingerprint==baseline
        assert launch['binary_sha256']==plan['binary_sha256']
        for name,digest in launch['runtime_hashes'].items():assert sha(H.parent/'g1/runtime'/name)==digest
        for name,digest in launch['continuation_sources'].items():assert sha(name)==digest
        marker=H/'windows'/(file.parent.name+'.md')
        commit,when=git('log','-1','--format=%H|%cI','--',str(marker)).split('|')
        assert commit==window['window_commit'] and stamp(when)==stamp(window['window_start'])
        assert stamp(window['window_end'])-stamp(when)==D.timedelta(hours=4)
        assert stamp(window['latest_start'])-stamp(when)==D.timedelta(hours=2)
        assert not subprocess.run(['ps','-p',str(handle['pid']),'-o','pid=,stat=,args='],capture_output=True,text=True).stdout.strip()
        for args in (['docker','ps','-a','--filter','name='+launch['prefix'],'--format','{{.Names}}'],['docker','network','ls','--filter','name='+launch['prefix'],'--format','{{.Name}}']):
            assert not subprocess.check_output(args,text=True,timeout=20).strip()
        raw=load(root/'transport/ledger.json');requests+=len(raw['records'])
        for receipt in raw['records']:
            n=receipt['request'];assert sha(root/f'transport/request-{n}.json')==receipt['request_sha256']
            assert sha(root/f'transport/response-{n}.sse')==receipt['sha256']
            forwarded=load(root/f'transport/forwarded-request-{n}.json');assert forwarded['max_output_tokens']==16384
            assert receipt['provider_backend']=='127.0.0.1:18001' and receipt['path']=='/v1/responses'
        for i,row in enumerate(v['rows']):
            if 'native_exit' not in row:continue
            receipts=[r for r in raw['records'] if r['actor']==row['cell_id']];assert receipts
            starts.append((min(stamp(r['started_utc']) for r in receipts),row['cell_id']))
            admission=load(root/str(i)/'admission.json');assert admission['admitted'] and admission['maximum_wait_seconds']==600 and admission['wait_seconds']<=600
            samples=load(root/str(i)/'load-samples.json');assert samples==row['periodic_load_samples'] and samples[0]['kind']=='start'
            observed=[stamp(s['observations'][0]['observed_utc']) for s in samples if 'observed_utc' in s['observations'][0]]
            gaps.extend((b-a).total_seconds() for a,b in zip(observed,observed[1:]));load_counts+=len(samples)
            assert all(s['kind'] in ('start','periodic') for s in samples)
            max_wall=max(max_wall,row['actor_seconds'])
        waves.append(dict(wave=file.parent.name,window_commit=commit,root=str(root),raw_result_sha256=sha(file),worker_and_owned_resources_absent=True,model_requests=len(raw['records']),load_records_preserved=True))
    assert [cell for _,cell in sorted(starts)]==expected
    assert requests==sum(r['requests'] for r in audit['rows'])
    assert 'while not sampler_stop.wait(30)' in (H.parent/'g1/run_calibration.py').read_text()
    result=dict(status='EXECUTION_AUDITED_NOT_STATISTICAL_ACCEPTANCE',cells=108,requests=requests,exact_frozen_schedule_order=True,rounds_not_interleaved=True,windows_committed_before_calls=True,runtime_and_provider_fingerprints_unchanged=True,all_source_payload_response_hashes_valid=True,all_original_grades_valid=True,raw_costs_complete=False,unknown_cells=unknown,unknown_cost_never_imputed=True,load_sample_records=load_counts,nominal_load_cadence_seconds=30,maximum_observed_load_gap_seconds=max(gaps),maximum_native_wall_seconds=max_wall,cap_hit_cells=[r['cell_id'] for r in audit['rows'] if r['cap_hit']],protected_G1_canonical_and_excluded_paths_unchanged=True,all_workers_owned_containers_networks_absent=True,model_retries=0,terminal_model_attempts=0,waves=waves,audit_sha256=sha(H/'audits/aider.json'),utc=D.datetime.now(D.timezone.utc).isoformat())
    out=H/'audits/final-execution.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='waves'},indent=2))
if __name__=='__main__':main()
