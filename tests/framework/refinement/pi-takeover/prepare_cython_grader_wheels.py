"""Trusted-only public test-runner wheels;no benchmark data or target artifacts."""
import hashlib,json,pathlib,urllib.request,uuid
R=pathlib.Path(__file__).resolve().parent
VERSIONS={'pytest':'8.4.1','pytest-json-ctrf':'0.3.5','iniconfig':'2.1.0','pluggy':'1.6.0','pygments':'2.19.2'}
def fetch(url,cap):
 with urllib.request.urlopen(url,timeout=30) as response:data=response.read(cap+1)
 if len(data)>cap:raise RuntimeError('public download byte cap')
 return data
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-cython-grader-wheels-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o755);wheels=root/'wheels';wheels.mkdir(mode=0o755);records={};metadata={}
 for package,version in VERSIONS.items():
  url='https://pypi.org/pypi/'+package+'/'+version+'/json';raw=fetch(url,8388608);(root/(package+'-metadata.json')).write_bytes(raw);metadata[package]={'url':url,'sha256':hashlib.sha256(raw).hexdigest()};data=json.loads(raw);matches=[f for f in data['urls'] if f['filename'].endswith('py3-none-any.whl') and not f.get('yanked')]
  if len(matches)!=1:raise RuntimeError('ambiguous public pure-Python wheel')
  f=matches[0]
  if not f['url'].startswith('https://files.pythonhosted.org/packages/'):raise RuntimeError('unexpected public artifact host')
  payload=fetch(f['url'],8388608)
  if len(payload)!=f['size'] or hashlib.sha256(payload).hexdigest()!=f['digests']['sha256']:raise RuntimeError('public wheel digest mismatch')
  (wheels/f['filename']).write_bytes(payload);records[f['filename']]={'bytes':len(payload),'sha256':f['digests']['sha256'],'url':f['url']}
 result={'private_root':str(root),'versions':VERSIONS,'selection':'Official public test.sh pytest/plugin pins;generic dependency pins stable before original image date20251031;existing packaging supplied by unchanged dependency cache','artifacts':records,'metadata':metadata,'mount':str(wheels)+':/opt/grader-wheels:ro','native_starts':0,'provider_POST':0,'target_builds':0,'target_installs':0,'actor_delivery':False,'prepared':True};(R/'cython-grader-wheels-cache.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
