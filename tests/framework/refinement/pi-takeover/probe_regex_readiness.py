"""Capture/classification/cachecollectiononly;NOgold/originaltestexecutions/LLM."""
import pathlib,json,subprocess,uuid,hashlib
from actor_public_inputs import recipe
from regex_output_presence import stopped_output_present
from task_artifacts import capture_stopped_actor
from artifact_capture import CaptureError
from cached_grader_setup import inputs,prepare,ENV
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 assert not (R/'regex-readiness-probe.json').exists();spec=recipe('regex-log');image=spec['actor_image_id'];assert image==spec['grader_image_id'];transfer=json.loads((R/'file-capture-regex-log-result.json').read_text());control=json.loads((R/'control-regex-log-result.json').read_text());assert transfer['valid_output_replay'] and transfer['cleanup_verified'] and control['valid_baseline_gold_pair'];root=pathlib.Path('/tmp/solpi-regex-readiness-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);owned=[];out={'task':'regex-log','root':str(root),'recipe':spec,'original_positive_controls_reused_not_executed':True,'official_test_runs':0,'model_POST':0,'scored_actor_starts':0,'gold_runs':0}
 def docker(*args,timeout=20):return subprocess.check_output(['docker',*args],stderr=subprocess.STDOUT,text=True,timeout=timeout).strip()
 try:
  actor=root.name+'-layout';owned.append(actor);docker('create','--name',actor,'--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','/bin/sh',image,'-c','sleep infinity');assert not stopped_output_present(actor,image);out['real_stopped_absence_verified']=True
  directory=root/'regex.txt';directory.mkdir();docker('cp',str(directory),actor+':/app/regex.txt');assert stopped_output_present(actor,image)
  try:capture_stopped_actor('regex-log',actor,image,root/'unsupported');raise AssertionError('directorycaptureaccepted')
  except CaptureError:out['directory_not_quality_zero']=True
  docker('rm',actor);owned.remove(actor)
  actor=root.name+'-file';owned.append(actor);docker('create','--name',actor,'--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','/bin/sh',image,'-c','sleep infinity');sentinel=root/'generic-sentinel';sentinel.write_text('GENERIC_TRANSPORT_ONLY_NOT_BENCHMARK_SOLUTION\n');docker('cp',str(sentinel),actor+':/app/regex.txt');assert stopped_output_present(actor,image);cap=capture_stopped_actor('regex-log',actor,image,root/'captured');assert cap['artifacts']['/app/regex.txt']['sha256']==sha(sentinel);out['generic_regular_file_capture_verified']=True
  grader=root.name+'-collect';owned.append(grader);logs=root/'logs';(logs/'verifier').mkdir(parents=True);args=['create','--name',grader,'--network','none','--memory',str(spec['memory_mb'])+'m','--cpus',str(spec['cpus']),'--security-opt','no-new-privileges','-v','/tmp/solpi-refinement-terminal-bench-2/regex-log/tests:/tests:ro','-v',str(logs)+':/logs:rw'];
  for mount in inputs()['mounts']:args+=['-v',mount]
  docker(*args,'--entrypoint','/bin/sh',image,'-c','sleep infinity');docker('start',grader);out['software_setup']=prepare(grader,image,root);text=docker('exec','-w','/app',*ENV,grader,'/root/.local/bin/uvx','-p','3.13','-w','pytest==8.4.1','-w','pytest-json-ctrf==0.3.5','pytest','--collect-only','-q','/tests/test_outputs.py',timeout=60);(root/'collection.log').write_text(text+'\n');names=[l.strip() for l in text.splitlines() if '::test_' in l];assert names==[t['name'] for t in transfer['replay']['tests']];out['collected_original_tests']=names;out['passed']=True
 except Exception as e:out.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:500]})
 finally:
  for name in owned:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  out['cleanup_verified']=all(subprocess.run(['docker','inspect',name],capture_output=True,timeout=10).returncode!=0 for name in owned);out['source_manifest']={str(p.relative_to(pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/regex-log'))):sha(p) for p in pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/regex-log').rglob('*') if p.is_file()};out['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'regex-readiness-probe.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['artifact_hashes','source_manifest']},indent=2))
