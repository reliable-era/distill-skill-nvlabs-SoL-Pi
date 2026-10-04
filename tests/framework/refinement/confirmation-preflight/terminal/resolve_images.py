#!/usr/bin/env python3
"""Anonymous DockerHub manifest metadata only: never pull layers or print tokens."""
import hashlib,json,urllib.parse,urllib.request
from pathlib import Path
OUT=Path(__file__).resolve().parent
ACCEPT=', '.join(['application/vnd.oci.image.index.v1+json','application/vnd.docker.distribution.manifest.list.v2+json','application/vnd.oci.image.manifest.v1+json','application/vnd.docker.distribution.manifest.v2+json'])
def resolve(ref):
 repo,tag=ref.rsplit(':',1)
 url='https://auth.docker.io/token?'+urllib.parse.urlencode({'service':'registry.docker.io','scope':'repository:'+repo+':pull'})
 with urllib.request.urlopen(url,timeout=30) as response:token=json.load(response)['token']
 def manifest(version):
  request=urllib.request.Request('https://registry-1.docker.io/v2/'+repo+'/manifests/'+version,headers={'Authorization':'Bearer '+token,'Accept':ACCEPT})
  with urllib.request.urlopen(request,timeout=30) as response:raw=response.read();digest=response.headers.get('Docker-Content-Digest')
  assert digest=='sha256:'+hashlib.sha256(raw).hexdigest()
  return json.loads(raw),digest
 data,index_digest=manifest(tag);platform='linux/amd64'
 if 'manifests' in data:
  matches=[m for m in data['manifests'] if m.get('platform',{}).get('os')=='linux' and m.get('platform',{}).get('architecture')=='amd64'];assert len(matches)==1
  data,digest=manifest(matches[0]['digest'])
 else:digest=index_digest
 return {'original_reference':ref,'tag_manifest_digest':index_digest,'linux_amd64_manifest_digest':digest,'immutable_reference':repo+'@'+digest,'manifest_sha_verified':True,'compressed_layer_bytes':sum(m['size'] for m in data.get('layers',[])),'layers':len(data.get('layers',[])),'config_digest':data['config']['digest'],'metadata_only':True,'layers_downloaded':0,'registry_auth':'Anonymous repository-scoped ephemeral bearer, never persisted or printed'}
if __name__=='__main__':
 inspection=json.loads((OUT/'offline-inspection.json').read_text());rows=[]
 for record in inspection['records']:
  try:rows.append({'task':record['task'],**resolve(record['metadata']['environment']['docker_image'])})
  except Exception as error:rows.append({'task':record['task'],'resolution_error_type':type(error).__name__,'immutable_reference':None})
 (OUT/'resolved-images.json').write_text(json.dumps({'scope':'Anonymous manifest metadata, no layer pulls or Docker builds/controls','records':rows},indent=2)+'\n');print(json.dumps({'resolved':sum(r.get('immutable_reference') is not None for r in rows),'tasks':len(rows),'layers_downloaded':0}))
