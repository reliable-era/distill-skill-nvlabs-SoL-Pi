"""Creates only uniquely named owned containers/networks, cleans them in finally."""
import subprocess,json,pathlib,uuid,time,hashlib,http.server,threading,urllib.request,ipaddress
root=pathlib.Path(__file__).resolve().parent;prefix='solpi-egress-'+uuid.uuid4().hex[:10];image='sol-pi-eval-polyglot-login:2026-10-04';created=[];nets=[]
def cmd(*a):return subprocess.check_output(['docker',*a],text=True).strip()
class Canary(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  self.send_response(200);self.end_headers();self.wfile.write(b'owned-host-canary')
canary=http.server.HTTPServer(('0.0.0.0',0),Canary)
worker=threading.Thread(target=canary.serve_forever,daemon=True);worker.start()
canary_port=canary.server_address[1]
assert urllib.request.urlopen('http://127.0.0.1:'+str(canary_port),timeout=2).read()==b'owned-host-canary'

try:
 for suffix in ['actor','provider']:
  n=prefix+'-'+suffix;options=['--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated'] if suffix=='actor' else [];cmd('network','create','--internal','--ipv6=false',*options,n);nets.append(n)
 for suffix,script,net,extra in [('mock','mock.py',nets[1],[]),('proxy','proxy.py',nets[0],['-e','EGRESS_ALLOWLIST={"provider.example:8000":"mock"}'])]:
  name=prefix+'-'+suffix;cmd('run','-d','--name',name,'--network',net,'--network-alias',suffix,'--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--user','65534:65534','--entrypoint','python3','-v',str(root)+':/app:ro',*extra,image,'/app/'+script);created.append(name)
 cmd('network','connect',nets[1],created[1]);time.sleep(1)
 inspect=json.loads(cmd('inspect',created[0]))[0];ip=inspect['NetworkSettings']['Networks'][nets[1]]['IPAddress']
 actor_network=json.loads(cmd('network','inspect',nets[0]))[0];ipam=actor_network['IPAM']['Config'][0];gateway=ipam.get('Gateway') or str(ipaddress.ip_network(ipam['Subnet']).network_address+1)
 run=subprocess.run(['docker','run','--rm','--network',nets[0],'--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--user','65534:65534','--entrypoint','python3','-e','MOCK_IP='+ip,'-e','HOST_GATEWAY='+gateway,'-e','HOST_CANARY_PORT='+str(canary_port),'-v',str(root)+':/app:ro',image,'/app/probe.py'],capture_output=True,text=True)
 verifier=cmd('run','--rm','--network','none','--cap-drop','ALL','--entrypoint','python3',image,'-c','import socket;print(socket.gethostbyname("localhost"))')
 report={'prototype_only':True,'actor_gateway_mode':'isolated','actor_gateway_assigned':bool(ipam.get('Gateway')),'actor_ipv6_enabled':actor_network['EnableIPv6'],'host_canary_positive':True,'docker_server_version':cmd('version','--format','{{.Server.Version}}'),'image_id':json.loads(cmd('image','inspect',image))[0]['Id'],'tests':json.loads(run.stdout),'exit_code':run.returncode,'verifier_network':'none','source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.py')},'real_model_calls':0,'credentials_used':False,'production_oauth_support':'TBD: endpoint set and native proxy/TLS integration unverified'}
 (root/'docker-test-evidence.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(run.returncode)
finally:
 canary.shutdown();canary.server_close();worker.join(timeout=2)
 for n in reversed(created):subprocess.run(['docker','rm','-f',n],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for n in reversed(nets):subprocess.run(['docker','network','rm',n],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
