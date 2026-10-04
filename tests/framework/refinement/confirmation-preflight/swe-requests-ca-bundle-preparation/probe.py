import pathlib,json,hashlib,inspect,ast
import requests,requests.sessions,requests.adapters,requests.certs,requests.utils
out=pathlib.Path('/output');total=0;records={}
for key,module in [('sessions',requests.sessions),('adapters',requests.adapters),('certs',requests.certs)]:
 path=pathlib.Path(inspect.getsourcefile(module));raw=path.read_bytes();total+=len(raw)
 if total>1048576:raise RuntimeError('extraction byte cap')
 target=out/(key+'.py');target.write_bytes(raw)
 records[key]={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
path=pathlib.Path(requests.utils.DEFAULT_CA_BUNDLE_PATH);raw=path.read_bytes();total+=len(raw)
if total>1048576:raise RuntimeError('extraction byte cap')
(out/'original-default-ca.pem').write_bytes(raw)
records['default_CA']={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'PEM_certificate_count':raw.count(b'-----BEGIN CERTIFICATE-----')}
send=inspect.getsource(requests.sessions.Session.send);request=inspect.getsource(requests.sessions.Session.request);verify=inspect.getsource(requests.adapters.HTTPAdapter.cert_verify)
metadata={'requests_version':requests.__version__,'records':records,'extracted_bytes':total,'facts':{'send_defaults_to_self_verify':"kwargs.setdefault('verify', self.verify)" in send,'send_merges_CA_environment':'REQUESTS_CA_BUNDLE' in send,'request_merges_CA_environment':'REQUESTS_CA_BUNDLE' in request,'adapter_uses_default_CA':'DEFAULT_CA_BUNDLE_PATH' in verify},'HTTP_requests':0}
(out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
