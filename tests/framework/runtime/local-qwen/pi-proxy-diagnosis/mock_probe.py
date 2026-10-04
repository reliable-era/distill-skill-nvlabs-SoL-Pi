"""One owned loopback POST proxy probe; no provider/model/auth routes."""
import pathlib,hashlib,sys,http.server,threading,subprocess,os,json,http.client,urllib.parse,time
counts={'proxy_POST':0,'mock_POST':0,'CONNECT':0};receipts=[];guard=threading.Lock()
class Mock(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):
  with guard:counts['mock_POST']+=1
  self.rfile.read(min(int(self.headers.get('Content-Length','0')),4096));self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"error":{"message":"owned mock","type":"mock_error"}}')
class Proxy(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_CONNECT(self):
  with guard:
   counts['CONNECT']+=1;status=403 if counts['CONNECT']==1 else 429;receipts.append({'method':'CONNECT','authority':self.path,'status':status})
  self.send_error(status)

 def do_POST(self):
  u=urllib.parse.urlsplit(self.path)
  if u.netloc!='provider.example:8000' or u.path!='/v1/chat/completions' or self.headers.get('Transfer-Encoding'):self.send_error(403);return
  with guard:
   if counts['proxy_POST']>=1:self.send_error(429);return
   counts['proxy_POST']+=1;receipts.append({'method':'POST','authority':u.netloc,'status':400})
  n=int(self.headers.get('Content-Length','0'))
  if not 0<=n<=4096:self.send_error(413);return
  self.connection.settimeout(3);body=self.rfile.read(n);c=http.client.HTTPConnection('127.0.0.1',mock.server_address[1],timeout=3)
  try:c.request('POST',u.path,body,{'Content-Type':'application/json'});z=c.getresponse();raw=z.read(4096);self.send_response(z.status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(raw)
  finally:c.close()
mock=http.server.HTTPServer(('127.0.0.1',0),Mock);proxy=http.server.HTTPServer(('127.0.0.1',0),Proxy)
threads=[]
for server in [mock,proxy]:
 t=threading.Thread(target=server.serve_forever,daemon=True);t.start();threads.append(t)
try:
 env={'HOME':'/tmp/home','HTTP_PROXY':'http://127.0.0.1:'+str(proxy.server_address[1]),'HTTPS_PROXY':'http://127.0.0.1:'+str(proxy.server_address[1]),'NO_PROXY':'','PATH':'/usr/bin:/bin'}
 artifact=pathlib.Path('/artifacts');artifact.mkdir(exist_ok=True)
 z=None;failure=None
 try:z=subprocess.run(['/opt/cursor/bin/node','--use-env-proxy','/app/probe.mjs'],env=env,capture_output=True,text=True,timeout=6)
 except subprocess.TimeoutExpired as e:
  failure='SDK_timeout';stdout=e.stdout or b'';stderr=e.stderr or b''
  stdout=stdout.decode(errors='replace') if isinstance(stdout,bytes) else stdout;stderr=stderr.decode(errors='replace') if isinstance(stderr,bytes) else stderr
 else:stdout=z.stdout;stderr=z.stderr
 for name,value in [('sdk.stdout',stdout),('sdk.stderr',stderr)]:
  f=artifact/name;f.write_text(value[:65536]);f.chmod(0o600)
 try:result=json.loads(stdout)
 except ValueError:result={'status':None,'expectedMock400':False}
 report={'counts':counts,'method_receipts':receipts,'sdk_exit':z.returncode if z else None,'sdk_status':result.get('status'),'expectedMock400':result.get('expectedMock400'),'failure':failure,'models':0,'real_provider_calls':0,'private_stream_hashes':{n:hashlib.sha256((artifact/n).read_bytes()).hexdigest() for n in ['sdk.stdout','sdk.stderr']}}
 (artifact/'sdk-status.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
 if z is None or z.returncode or counts['proxy_POST']!=1 or counts['mock_POST']!=1 or counts['CONNECT']>1 or result.get('expectedMock400') is not True:sys.exit(1)

finally:
 for server in [proxy,mock]:server.shutdown();server.server_close()
 for t in threads:t.join(1)
 if any(t.is_alive() for t in threads):raise RuntimeError('owned mock workers remain')
