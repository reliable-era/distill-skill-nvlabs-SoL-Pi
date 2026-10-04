"""One exact pinned SDK request through owned Unix tunnel to owned HTTP400 mock."""
import pathlib,http.server,threading,subprocess,os,json,importlib.util,hashlib,time
R=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('tunnel',R/'tunnel_proxy.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
s=importlib.util.spec_from_file_location('server',R.parent/'native-readiness/server.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
counts={'POST':0};guard=threading.Lock();artifact=pathlib.Path('/artifacts');sockdir=pathlib.Path('/tmp/private-broker');sockdir.mkdir(mode=0o700,exist_ok=False);path=sockdir/'broker.sock'
class Mock(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):
  with guard:
   counts['POST']+=1
   if counts['POST']>1:self.send_error(429);return
  if self.path!='/v1/chat/completions' or self.headers.get('Transfer-Encoding'):self.send_error(403);return
  n=int(self.headers.get('Content-Length','0'))
  if not 0<=n<=4096:self.send_error(413);return
  self.connection.settimeout(3);self.rfile.read(n);self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"error":{"message":"owned mock","type":"mock_error"}}')
class Proxy(t.TunnelProxy):
 unix_socket=str(path);max_tunnel_seconds=6;max_client_bytes=4096;max_upstream_bytes=4096
 stats={'CONNECT':0,'denied':0,'completed':0,'errors':0};attempts=0
 def do_CONNECT(self):
  with self.guard:Proxy.attempts+=1
  if Proxy.attempts>1:self.send_error(429);return
  super().do_CONNECT()
broker=b.OwnedUnixServer(str(path),Mock);path.chmod(0o600);proxy=b.OwnedServer(('127.0.0.1',0),Proxy);result=None;errors=[];z=None
for server in [broker,proxy]:threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 plan=json.loads((R/'plan.json').read_text())
 for file,h in plan['image_file_sha256'].items():
  if hashlib.sha256(pathlib.Path(file).read_bytes()).hexdigest()!=h:raise RuntimeError('pinnedruntimefilechanged')
 env={'HOME':'/tmp/home','HTTP_PROXY':'http://127.0.0.1:'+str(proxy.server_address[1]),'HTTPS_PROXY':'http://127.0.0.1:'+str(proxy.server_address[1]),'NO_PROXY':'','PATH':'/usr/bin:/bin'}
 z=subprocess.run(['/opt/cursor/bin/node','--use-env-proxy','/app/pi-unix-tunnel/probe.mjs'],env=env,capture_output=True,text=True,timeout=8)
 for name,value in [('sdk.stdout',z.stdout),('sdk.stderr',z.stderr)]:
  f=artifact/name;f.write_text(value[:65536]);f.chmod(0o600)
 result=json.loads(z.stdout)
 if z.returncode or result.get('status')!=400 or result.get('expectedMock400') is not True or counts['POST']!=1 or Proxy.stats['CONNECT']!=1 or Proxy.attempts!=1:raise RuntimeError('exactSDKtunnelreceiptfailed')
except BaseException as e:
 if isinstance(e,subprocess.TimeoutExpired):
  for name,value in [('sdk.stdout',e.stdout or b''),('sdk.stderr',e.stderr or b'')]:
   f=artifact/name;f.write_bytes((value.encode() if isinstance(value,str) else value)[:65536]);f.chmod(0o600)
 errors.append({'type':type(e).__name__,'message':str(e)[:200]})
finally:
 for server in [proxy,broker]:
  try:server.cleanup()
  except Exception as e:errors.append({'cleanup':type(e).__name__})
 path.unlink(missing_ok=True)
 report={'POST':counts['POST'],'CONNECT':Proxy.stats['CONNECT'],'CONNECT_attempts':Proxy.attempts,'tunnel_counters':Proxy.stats,'sdk_exit':z.returncode if z else None,'sdk_status':result.get('status') if result else None,'expectedMock400':result.get('expectedMock400') if result else None,'workers':{'proxy':proxy.workers,'broker':broker.workers},'socket_absent':not path.exists(),'errors':errors,'models':0,'real_provider_calls':0}
 (artifact/'mock-status.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if errors:raise SystemExit(1)
