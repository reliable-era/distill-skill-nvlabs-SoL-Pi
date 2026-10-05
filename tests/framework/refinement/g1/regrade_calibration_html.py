"""Repair HTML public verifier dependencies only; no model or actor retry."""
import pathlib,json,subprocess,uuid,datetime
import run_calibration as C
import cached_grader_setup as cached
from task_replay import replay_capture

def main():
    launch=json.loads((C.E/'calibration-launch.json').read_text());root=pathlib.Path(launch['root']);d=root/'0'
    progress=json.loads((C.E/'calibration-progress.json').read_text());row=progress['rows'][0]
    assert row['task']=='break-filter-js-from-html' and row['grade_error']['message']=='Original grade unavailable'
    out=d/'html-grader-repair-r2';out.mkdir(mode=0o700,exist_ok=False);logs=out/'logs';(logs/'verifier').mkdir(parents=True)
    name=launch['prefix']+'-html-regrade-r2';image=row['recipe']['grader_image_id'];inputs=cached.inputs();report={'model_POST':0,'native_starts':0,'original_grading_failure':row['grade_error'],'original_reward':row.get('reward'),'original_test_events':row.get('test_events'),'captured_artifact_sha256':C.sha(d/'captured/capture.json'),'source_tests_manifest':C.W.files(pathlib.Path(row['source'])/'tests'),'solved':None,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        args=['create','--pull=never','--name',name,'--network','bridge','--cpus','1','--memory','2g','--pids-limit','512','--security-opt','no-new-privileges','-v',row['source']+'/tests:/tests:ro','-v',str(logs)+':/logs','-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro']
        for mount in inputs['mounts']:args+=['-v',mount]
        C.docker(*args,'--entrypoint','/bin/sh',image,'-c','sleep infinity')
        report['replay']=replay_capture(row['task'],d/'captured',name,image,actor_image_id=row['recipe']['actor_image_id'])
        # Public runner-only preload on this owned grader's bridge. The original
        # helper requires none; change only that topology check, then disconnect
        # before invoking the unchanged task verifier. Preserve the first repair.
        text=(C.R/'cached_grader_setup.py').read_text()
        marker="set(x['NetworkSettings']['Networks'])!={'none'}"
        assert text.count(marker)==1
        import types,hashlib
        preload=types.ModuleType('html_public_preload')
        preload.__file__=str(C.R/'cached_grader_setup.py')
        exec(compile(text.replace(marker,"set(x['NetworkSettings']['Networks'])!={'bridge'}"),'<HTML public preload>', 'exec'),preload.__dict__)
        report['preload_base_sha256']=C.sha(C.R/'cached_grader_setup.py')
        report['preload_changed_only_network_check']=True
        report['generic_preload']=preload.prepare(name,image,out)
        report['generic_preload']['test_network_disconnected']=False
        command=['docker','exec','-w','/','-e','UV_NATIVE_TLS=true','-e','SSL_CERT_FILE=/opt/trusted-ca.pem','-e','CURL_CA_BUNDLE=/opt/trusted-ca.pem','-e','UV_PYTHON_DOWNLOADS=never',name,'/root/.local/bin/uvx','-p','3.13','-w','pytest==8.4.1','-w','selenium==4.35.0','-w','beautifulsoup4==4.13.5','-w','pytest-json-ctrf==0.3.5','pytest','--version']
        with (out/'public-dependencies.log').open('wb') as log:z=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        report['dependency_exit']=z.returncode
        if z.returncode:raise RuntimeError('Public HTML dependencies unavailable')
        C.docker('network','disconnect','bridge',name)
        with (out/'verifier.log').open('wb') as log:z=subprocess.run(cached.grade_argv(name),stdout=log,stderr=subprocess.STDOUT,timeout=600)
        reward=logs/'verifier/reward.txt';ctrf=logs/'verifier/ctrf.json';tests=json.loads(ctrf.read_text())['results']['tests'] if ctrf.exists() else []
        report.update(verifier_exit=z.returncode,reward=reward.read_text().strip() if reward.exists() else None,test_events=len(tests))
        if not tests or report['reward'] not in ('0','1'):raise RuntimeError('Original HTML grade still unavailable')
        report['solved']=report['reward']=='1' and all(t['status']=='passed' for t in tests)
    except Exception as error:report['error']={'type':type(error).__name__,'message':str(error)[:300]}
    finally:
        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
        report['cleanup_verified']=C.absent(name);report['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();C.save(C.E/'html-grader-repair-r2.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
