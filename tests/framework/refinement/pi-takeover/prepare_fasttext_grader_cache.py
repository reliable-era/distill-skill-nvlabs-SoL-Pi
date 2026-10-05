"""BoundedPUBLICgrader-softwareONLY;neverreadsdata/target/tests/solutions."""
import pathlib,json,hashlib,urllib.request,time,uuid,shutil,tarfile
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 assert not (R/'fasttext-public-grader-cache.json').exists();root=pathlib.Path('/tmp/solpi-fasttext-public-grader-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);wheels=root/'wheels';wheels.mkdir();deadline=time.monotonic()+300;calls=0;size=0;report={'root':str(root),'model_POST':0,'actor_starts':0,'models_trained':0,'dataset_or_target_or_test_reads':0,'official_or_gold_runs':0,'scope':'publicPython3.11.14+original-scriptsoftwareversions+explicitpublictransitivepins;NOTclaimmatchingalloldtransitives','cap_seconds':300,'cap_HTTP_requests_including_redirects':24,'cap_network_bytes':167772160};requests=[]
 class CountRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,req,fp,code,msg,headers,newurl):
   global calls
   calls+=1;assert calls<=24 and time.monotonic()<deadline;requests.append({'redirect':code,'to':newurl.split('?')[0]});return super().redirect_request(req,fp,code,msg,headers,newurl)
 opener=urllib.request.build_opener(CountRedirect)
 def fetch(url):
  global calls,size
  calls+=1;assert calls<=24 and time.monotonic()<deadline
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'solpi-public-grader-software'}),timeout=min(45,max(.1,deadline-time.monotonic()))) as response:
   assert response.status==200;parts=[]
   while True:
    chunk=response.read(1048576)
    if not chunk:break
    size+=len(chunk);assert size<=167772160 and time.monotonic()<deadline;parts.append(chunk)
   result=b''.join(parts);requests.append({'url':url,'status':200,'bytes':len(result),'sha256':hashlib.sha256(result).hexdigest()});return result
 try:
  source=pathlib.Path('/tmp/solpi-tex-public-runtime-metadata/python-download-metadata.json');assert sha(source)=='fe7014cebbe034c8cbf17c79cda78872774378ff66cad78077f27d289e6e7862';meta=json.loads(source.read_text());python=meta['cpython-3.11.14-linux-x86_64-gnu'];assert python['url'].startswith('https://github.com/astral-sh/python-build-standalone/releases/download/20251014/');blob=fetch(python['url']);assert hashlib.sha256(blob).hexdigest()==python['sha256'];archive=root/'cpython-3.11.14.tar.gz';archive.write_bytes(blob);expanded=root/'runtime';expanded.mkdir()
  with tarfile.open(archive) as tar:
   members=tar.getmembers();assert len(members)<20000 and sum(x.size for x in members)<536870912
   for x in members:assert not pathlib.PurePosixPath(x.name).is_absolute() and '..' not in pathlib.PurePosixPath(x.name).parts and not (x.isdev() or x.isfifo())
   tar.extractall(expanded,filter='data')
  versions={'numpy':'1.24.0','scikit-learn':'1.7.0','fasttext-wheel':'0.9.2','scipy':'1.15.3','joblib':'1.5.2','threadpoolctl':'3.6.0'};artifacts={};metadata={}
  for package,version in versions.items():
   url=f'https://pypi.org/pypi/{package}/{version}/json';data=fetch(url);p=root/(package+'.json');p.write_bytes(data);m=json.loads(data);candidates=[x for x in m['urls'] if x['filename'].endswith('py3-none-any.whl') or ('cp311-cp311' in x['filename'] and 'manylinux' in x['filename'] and 'x86_64.whl' in x['filename'])];assert len(candidates)==1,(package,[x['filename'] for x in candidates]);item=candidates[0];blob=fetch(item['url']);assert hashlib.sha256(blob).hexdigest()==item['digests']['sha256'];p=wheels/item['filename'];p.write_bytes(blob);artifacts[p.name]={'bytes':len(blob),'sha256':sha(p),'url':item['url']};metadata[package]={'metadata_sha256':sha(root/(package+'.json')),'requires_python':m['info']['requires_python'],'requires_dist':m['info']['requires_dist']}
  inv=json.loads((R/'tex-recovery-cache-inventory.json').read_text())
  for v in inv['verified_wheels'].values():
   p=pathlib.Path(v['path']);assert sha(p)==v['sha256'];shutil.copyfile(p,wheels/p.name);artifacts[p.name]={'bytes':v['bytes'],'sha256':v['sha256'],'source_manifest':'tex-recovery-cache-inventory.json'}
  runtime=expanded/'python';report.update(prepared=True,versions=versions,artifacts=artifacts,metadata=metadata,python={'version':'3.11.14','url':python['url'],'archive_sha256':sha(archive),'root':str(runtime),'files':{str(p.relative_to(runtime)):sha(p) for p in runtime.rglob('*') if p.is_file() and not p.is_symlink()},'links':{str(p.relative_to(runtime)):str(p.readlink()) for p in runtime.rglob('*') if p.is_symlink()}},uv_reused='/tmp/solpi-tex-public-runtime-expanded/uv/uv-x86_64-unknown-linux-gnu')
 except Exception as e:report.update(prepared=False,error={'type':type(e).__name__,'message':str(e)[:500]})
 report.update(HTTP_requests_including_redirects=calls,network_bytes=size,requests=requests,seconds=300-max(0,deadline-time.monotonic()));(R/'fasttext-public-grader-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['python','metadata','requests']},indent=2))
