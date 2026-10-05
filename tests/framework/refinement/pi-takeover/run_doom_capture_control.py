"""One stopped-oracle ELF replay against trusted original VM/assets;0modelcalls."""
import hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;PRIVATE=pathlib.Path('/tmp/solpi-doom-capture-launch-v1')
def main():
 PRIVATE.mkdir(mode=0o700,exist_ok=False)
 template=pathlib.Path('/tmp/solpi-guarded-tex-launch-v1/worker.py');code=template.read_text()
 code=code.replace("OUTPUTS={'overfull-hbox':'/app/input.tex'","OUTPUTS={'make-doom-for-mips':'/app/doomgeneric_mips','overfull-hbox':'/app/input.tex'")
 code=code.replace(" contract=json.loads((R/'selected-artifact-contracts.json').read_text())['task_contracts'][task]"," contract={'max_file_bytes':33554432}")
 code=code.replace("['/app/main.tex','/app/synonyms.txt']","['/app/vm.js','/app/doom.wad','/app/doomgeneric/doomgeneric/doomgeneric_img.c']")
 code=code.replace('Guarded TeX original-image control','Original-VM ELF replay with explicit supplied-input change witnesses')
 code=code.replace('synthetic-tampered-main.tex','synthetic-tampered-vm.js').replace('after-main.tex','after-vm.js').replace("tampered['/app/main.tex']","tampered['/app/vm.js']")
 needle="  subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15);return name"
 assert code.count(needle)==1
 code=code.replace(needle,"""  subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15)
  with (root/(role+'-apt-metadata.log')).open('wb') as f:
   refresh=subprocess.run(['docker','exec',name,'apt-get','-o','Acquire::Retries=0','update'],stdout=f,stderr=subprocess.STDOUT,timeout=120)
  if refresh.returncode:raise RuntimeError('apt metadata refresh failed')
  return name""")
 needle="  out['replay']=grade('replay',artifact)"
 assert code.count(needle)==1
 code=code.replace(needle,"""  with artifact.open('rb') as f:header=f.read(20)
  out['elf_witness']={'magic':header[:4]==b'\\x7fELF','class':header[4] if len(header)>4 else None,'byte_order':header[5] if len(header)>5 else None,'machine':int.from_bytes(header[18:20],'little' if len(header)>5 and header[5]==1 else 'big') if len(header)==20 else None}
"""+needle)
 # A changed supplied input is observable but not automatically forbidden by the public task.
 code=code.replace("out['protected_check']['unchanged'] and not out['synthetic_tamper_check']['unchanged']","out['elf_witness']['magic'] and out['elf_witness']['machine']==8 and not out['synthetic_tamper_check']['unchanged']")
 worker=PRIVATE/'worker.py';worker.write_text(code);compile(code,str(worker),'exec')
 plan={'task':'make-doom-for-mips','template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'worker_sha256':hashlib.sha256(worker.read_bytes()).hexdigest(),'output':'/app/doomgeneric_mips','fresh_grader_uses_original_vm_and_wad':True,'supplied_input_change_witness_not_new_acceptance_criterion':True,'environment_recipe':'Bounded aptmetadata refresh beforeeachrole,no packagepreinstall','maximum_worker_seconds':3000,'retry':0,'model_POSTs':0,'actor_runs':0}
 (R/'doom-capture-execution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 with (PRIVATE/'worker.log').open('wb') as f:p=subprocess.run([sys.executable,str(worker),'--task','make-doom-for-mips'],stdout=f,stderr=subprocess.STDOUT,timeout=3000)
 print(json.dumps({'worker_exit':p.returncode,'model_POSTs':0,'log':str(PRIVATE/'worker.log')}))
if __name__=='__main__':main()
