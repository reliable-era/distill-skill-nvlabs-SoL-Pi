"""Private-only protocol response output; no proxy, retries or remote hosts."""
import requests,json,time,pathlib
from urllib.parse import urlsplit,urljoin
COUNT=0
START=time.monotonic()
ORIGINAL=requests.adapters.HTTPAdapter.send
def bounded_send(self,request,**kwargs):
 global COUNT
 u=urlsplit(request.url)
 if u.hostname!='httpbin.org' or u.scheme not in ('http','https') or u.port not in (None,80,443):raise RuntimeError('host/protocol gate')
 COUNT+=1
 if COUNT>12 or time.monotonic()-START>30:raise RuntimeError('request/deadline cap')
 pathlib.Path('/output/private-send-count.json').write_text(json.dumps({'HTTPAdapter_send_attempts':COUNT}))
 kwargs['timeout']=min(3,max(.1,30-(time.monotonic()-START)))
 return ORIGINAL(self,request,**kwargs)
requests.adapters.HTTPAdapter.send=bounded_send
s=requests.Session();s.trust_env=False;s.verify='/certs/ca.pem'
def get(path,https=False,**kw):
 r=s.get(('https' if https else 'http')+'://httpbin.org'+path,allow_redirects=False,**kw)
 with open('/output/private-responses.jsonl','a') as f:f.write(json.dumps({'url':r.url,'status':r.status_code,'headers':dict(r.headers),'body':r.text})+'\n')
 return r
def run():
 assert get('/get?test=foo&test=baz').json()['args']['test']==['foo','baz']
 assert get('/get',True).status_code==200
 assert get('/basic-auth/user/pass',auth=('user','pass')).json()['authenticated'] is True
 assert get('/digest-auth/auth/user/pass',auth=requests.auth.HTTPDigestAuth('user','pass')).json()['authenticated'] is True
 r=get('/cookies/set?foo=bar');assert r.status_code in (301,302,303,307,308)
 assert get('/cookies').json()['cookies']['foo']=='bar'
 r=get('/redirect/1');assert r.status_code in (301,302,303,307,308)
 assert get(urlsplit(urljoin(r.url,r.headers['Location'])).path).status_code==200
 assert get('/gzip').json()['gzipped'] is True
 assert get('/headers',headers={'X-Parity':'unicode-ASCII'}).json()['headers']['X-Parity']=='unicode-ASCII'
 assert get('/get?unicode=%C3%B8').json()['args']['unicode']=='ø'
 assert COUNT==12
 pathlib.Path('/output/protocol-result.json').write_text(json.dumps({'status':'passed','http_requests':COUNT,'elapsed_seconds':time.monotonic()-START,'TLS_verification':True,'remote_hosts':0}))
if __name__=='__main__':run()
