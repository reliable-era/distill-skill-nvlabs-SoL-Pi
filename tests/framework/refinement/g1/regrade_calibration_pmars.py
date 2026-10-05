"""Original PMARS verifier regrade on the captured artifact; zero actor retries."""
import pathlib,json,subprocess,datetime
import run_calibration as C
import pmars_grader_setup as setup
from task_replay import replay_capture

def main():
    launch=json.loads((C.E/'calibration-launch.json').read_text());root=pathlib.Path(launch['root']);d=root/'2';row=json.loads((C.E/'calibration-progress.json').read_text())['rows'][2]
    assert row['task']=='build-pmars' and row['grade_error']['message']=='only trusted setup bridge allowed'
    out=d/'grader-repair';out.mkdir(mode=0o700,exist_ok=False);logs=out/'logs';(logs/'verifier').mkdir(parents=True)
    name=launch['prefix']+'-pmars-regrade';image=row['recipe']['grader_image_id'];paths=row['capture']['artifacts'];dynamic={'source_directory':next(p for p in paths if p.startswith('/app/pmars-'))}
    report={'native_starts':0,'model_POST':0,'original_failure':row['grade_error'],'captured_artifact_sha256':C.sha(d/'captured/capture.json'),'dynamic':dynamic,'solved':None,'source_tests_manifest':C.W.files(pathlib.Path(row['source'])/'tests')}
    try:
        C.docker('create','--pull=never','--name',name,'--network','bridge','--cpus','1','--memory',str(row['recipe']['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',row['source']+'/tests:/tests:ro','-v',str(logs)+':/logs','--entrypoint','/bin/sh',image,'-c','sleep infinity')
        report['replay']=replay_capture(row['task'],d/'captured',name,image,dynamic=dynamic,actor_image_id=row['recipe']['actor_image_id'])
        report['preload']=setup.prepare(name,image,out)
        with (out/'verifier.log').open('wb') as log:z=subprocess.run(setup.grade_argv(name),stdout=log,stderr=subprocess.STDOUT,timeout=600)
        reward=logs/'verifier/reward.txt';ctrf=logs/'verifier/ctrf.json';tests=json.loads(ctrf.read_text())['results']['tests'] if ctrf.exists() else []
        report.update(verifier_exit=z.returncode,reward=reward.read_text().strip() if reward.exists() else None,test_events=len(tests))
        if not tests or report['reward'] not in ('0','1'):raise RuntimeError('Original PMARS grade unavailable')
        report['solved']=report['reward']=='1' and all(t['status']=='passed' for t in tests)
    except Exception as error:report['error']={'type':type(error).__name__,'message':str(error)[:300]}
    finally:
        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);report['cleanup_verified']=C.absent(name);report['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();C.save(C.E/'pmars-grader-repair.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
