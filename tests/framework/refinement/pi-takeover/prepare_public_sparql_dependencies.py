"""BoundedPUBLICgenericRDFsoftwarecache;no graph/solution/target/test access."""
import hashlib,json,pathlib,shutil,time,urllib.request,uuid,zipfile,stat
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
if __name__=='__main__':
 assert not (R/'public-sparql-dependency-cache.json').exists();root=pathlib.Path('/tmp/solpi-public-sparql-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);wheels=root/'wheels';wheels.mkdir();packages=root/'packages';packages.mkdir();deadline=time.monotonic()+120;calls=0;size=0;versions={'rdflib':'7.1.4','pyparsing':'3.2.5'};artifacts={};metadata={};report={'root':str(root),'versions':versions,'scope':'publishedgenericsoftwareONLY/no benchmark graph/queries/tests/solutions','model_POST':0,'scored_actor_starts':0,'target_outputs':0,'caps':{'HTTP_requests':6,'bytes':16777216,'seconds':120}}
 def fetch(url):
  global calls,size
  calls+=1;assert calls<=6 and time.monotonic()<deadline
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'solpi-public-software-cache'}),timeout=min(30,max(.1,deadline-time.monotonic()))) as response:
   assert response.status==200;data=response.read(16777217-size);size+=len(data);assert size<=16777216 and time.monotonic()<deadline;return data
 try:
  for package,version in versions.items():
   url=f'https://pypi.org/pypi/{package}/{version}/json';data=fetch(url);(root/(package+'.json')).write_bytes(data);m=json.loads(data);choices=[x for x in m['urls'] if x['filename'].endswith('py3-none-any.whl')];assert len(choices)==1;a=choices[0];blob=fetch(a['url']);assert hashlib.sha256(blob).hexdigest()==a['digests']['sha256'];p=wheels/a['filename'];p.write_bytes(blob);artifacts[p.name]={'bytes':len(blob),'sha256':sha(p),'url':a['url']};metadata[package]={'sha256':sha(root/(package+'.json')),'url':url,'requires_python':m['info']['requires_python'],'requires_dist':m['info']['requires_dist']}
   with zipfile.ZipFile(p) as archive:
    for info in archive.infolist():
     name=pathlib.PurePosixPath(info.filename);assert not name.is_absolute() and '..' not in name.parts and not stat.S_ISLNK(info.external_attr>>16)
     assert info.file_size<16777216
     if not info.is_dir():target=packages/name;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(archive.read(info))
  inv=json.loads((R/'tex-recovery-cache-inventory.json').read_text())
  for rec in inv['verified_wheels'].values():
   p=pathlib.Path(rec['path']);assert sha(p)==rec['sha256'];shutil.copyfile(p,wheels/p.name);artifacts[p.name]={'bytes':rec['bytes'],'sha256':rec['sha256'],'public_source_manifest':'tex-recovery-cache-inventory.json'}
  report.update(prepared=True,artifacts=artifacts,metadata=metadata,packages_manifest={str(p.relative_to(packages)):sha(p) for p in packages.rglob('*') if p.is_file()})
 except Exception as e:report.update(prepared=False,error={'type':type(e).__name__,'message':str(e)[:250]})
 report.update(HTTP_requests=calls,network_bytes=size,seconds=120-max(0,deadline-time.monotonic()));(R/'public-sparql-dependency-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='packages_manifest'},indent=2))
