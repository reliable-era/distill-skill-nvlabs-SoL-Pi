"""NoModel/training/gold/officialgrading;boundedbinarycapture+trustedtarwiring."""
import pathlib,json,uuid,subprocess,shutil,hashlib
from actor_public_inputs import recipe
from fasttext_output_presence import stopped_output_present
from fasttext_grader_setup_r2 import inputs,prepare,ENV
from task_artifacts import capture_stopped_actor
from task_replay import replay_capture
from artifact_capture import CaptureError
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def files(root):return {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
if __name__=='__main__':
 assert not (R/'fasttext-readiness-probe.json').exists();software=json.loads((R/'fasttext-cached-software-probe-r2.json').read_text());assert software['passed'] and software['cleanup_verified'];root=pathlib.Path('/tmp/solpi-fasttext-wiring-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);image=recipe('train-fasttext')['actor_image_id'];owned=[];source=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/train-fasttext/tests');before=files(source);out={'root':str(root),'task':'train-fasttext','model_POST':0,'scored_actor_starts':0,'models_trained':0,'official_test_runs':0,'gold_runs':0,'software_proof_reused':True}
 def docker(*a,timeout=30):return subprocess.check_output(['docker',*a],stderr=subprocess.STDOUT,text=True,timeout=timeout).strip()
 try:
  actor=root.name+'-layout';owned.append(actor);docker('create','--name',actor,'--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','/bin/sh',image,'-c','sleep infinity');assert not stopped_output_present(actor,image);out['stopped_absence_verified']=True;directory=root/'model.bin';directory.mkdir();docker('cp',str(directory),actor+':/app/model.bin');assert stopped_output_present(actor,image)
  try:capture_stopped_actor('train-fasttext',actor,image,root/'unsupported');raise AssertionError('directory accepted')
  except CaptureError:out['directory_rejected_not_qualityzero']=True
  docker('rm',actor);owned.remove(actor);actor=root.name+'-file';owned.append(actor);docker('create','--name',actor,'--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','/bin/sh',image,'-c','sleep infinity');payload=root/'sentinel';payload.write_bytes(b'GENERIC_BINARY_TRANSPORT_NOT_TRAINED_MODEL\x00\xff');docker('cp',str(payload),actor+':/app/model.bin');cap=capture_stopped_actor('train-fasttext',actor,image,root/'captured');assert cap['artifacts']['/app/model.bin']['sha256']==sha(payload);out['regular_binary_capture_verified']=True
  tests=root/'trusted-tests-copy';shutil.copytree(source,tests);assert files(tests)==before;logs=root/'logs';(logs/'verifier').mkdir(parents=True);grader=root.name+'-grader';owned.append(grader);args=['create','--name',grader,'--network','none','--cpus','1','--memory','4096m','--security-opt','no-new-privileges','-v',str(tests)+':/tests:rw','-v',str(logs)+':/logs:rw']
  for m in inputs()['mounts']:args+=['-v',m]
  docker(*args,'--entrypoint','/bin/sh',image,'-c','sleep infinity');docker('start',grader);out['replay']=replay_capture('train-fasttext',grader,image,root/'captured');out['setup']=prepare(grader,image,root);docker('exec',grader,'tar','-xzf','/tests/private_test.tar.gz','-C','/tests',timeout=30);assert all(sha(tests/n)==h for n,h in before.items());out['original_test_files_unchanged_after_tar_extraction']=True;out['trusted_tar_extraction_into_private_writable_copy']=True;text=docker('exec','-w','/app',*ENV,grader,'/root/.local/bin/uvx','-p','3.11','-w','pytest==8.4.1','-w','scikit-learn==1.7.0','-w','fasttext-wheel==0.9.2','-w','numpy==1.24.0','-w','pytest-json-ctrf==0.3.5','pytest','--collect-only','-q','/tests/test_outputs.py');names=[l.strip() for l in text.splitlines() if '::test_' in l];assert names==software['collected_original_tests'];out['collected_original_tests']=names;(root/'collection.log').write_text(text+'\n');docker('cp',grader+':/app/model.bin',str(root/'replayed-sentinel'));assert sha(root/'replayed-sentinel')==sha(payload);out['exact_target_only_replay_no_build_verified']=True;out['passed']=True
 except Exception as e:out.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:1000]})
 finally:
  for n in owned:subprocess.run(['docker','rm','-f',n],capture_output=True,timeout=30)
  out['cleanup_verified']=all(subprocess.run(['docker','inspect',n],capture_output=True,timeout=10).returncode!=0 for n in owned);out['source_tests_unchanged']=files(source)==before;out['original_test_manifest']=before;out['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'fasttext-readiness-probe.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='artifact_hashes'},indent=2))
