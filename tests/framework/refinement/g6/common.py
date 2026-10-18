"""G6 private state and frozen-input checks;no credential or model access."""
import hashlib,json,os,pathlib,shutil,subprocess
H=pathlib.Path(__file__).resolve().parent
R=H.parents[3]
def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def save(path,value):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');os.replace(tmp,path)
def command(args,timeout=120,**kw): return subprocess.run(args,check=True,capture_output=True,timeout=timeout,**kw)
def private_root(): return pathlib.Path(json.loads((H/'launch.json').read_text())['private_root'])
def prereg(): return json.loads((H/'preregistration.json').read_text())
def disk_free(): return shutil.disk_usage('/').free
def check_frozen():
    p=prereg();root=private_root()
    binding=hashlib.sha256(json.dumps({k:p[k] for k in ('study_sample','smoke_sample','arm_orders','study_issue_order')},sort_keys=True).encode()).hexdigest()
    assert binding==p['amendment_explicit_v2']['sample_binding_sha256']
    assert sha(root/'dataset.json')==p['private_dataset_sha256']
    assert sha(root/'frozen-control-images.json')==p['frozen_image_leases_sha256']
    leases=json.loads((root/'frozen-control-images.json').read_text());selected=p['study_sample']+p['smoke_sample']
    assert len({leases[t]['image_id'] for t in selected})==len(selected),'Shared IDs require reference-counted leases,not independent deletion'
    for f,digest in p['reuse_g5_source_sha256'].items(): assert sha(H.parent/'g5'/f)==digest
    for f in (root/'marketplace').rglob('*'):
        if f.is_file():
            original=command(['git','show',p['plugin_commit']+':'+str(f.relative_to(root/'marketplace'))],timeout=20).stdout
            assert hashlib.sha256(original).hexdigest()==sha(f)
    return p
