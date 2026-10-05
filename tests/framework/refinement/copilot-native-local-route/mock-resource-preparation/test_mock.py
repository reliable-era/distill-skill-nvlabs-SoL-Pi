import unittest,pathlib,json
import run_mock as r
from worker import SAFE
class Guards(unittest.TestCase):
 def test_pass_requires_complete_cleanup(self):
  a={'routing_candidate':True,'container_absent':True,'docker_client_terminal':True,'broker_workers_remaining':0,'socket_absent':True,'errors':[]}
  self.assertTrue(r.final_pass(a));a['broker_workers_remaining']=1;self.assertFalse(r.final_pass(a));a['broker_workers_remaining']=0;a['container_absent']=False;self.assertFalse(r.final_pass(a))
 def test_socket_path_guard(self):
  self.assertTrue(r.socket_path_ok('/tmp/solpi-cpm-'+('a'*16)+'/socket/broker.sock'))
  self.assertTrue(r.socket_path_ok('a'*100));self.assertFalse(r.socket_path_ok('a'*101));self.assertFalse(r.socket_path_ok('a'*108))
 def test_no_global_file_limit_capture(self):
  import io,tempfile,hashlib
  from worker import capture
  data=b'x'*100000
  with tempfile.TemporaryDirectory() as t:
   out=pathlib.Path(t)/'out';v=capture(io.BytesIO(data),out);self.assertEqual(out.stat().st_size,65536);self.assertEqual(v['total_bytes'],100000)
  self.assertNotIn('setrlimit',(pathlib.Path(__file__).parent/'worker.py').read_text())
 def test_old_memory_rejected(self):
  private=pathlib.Path('/tmp/private');p={'host_uid':r.os.getuid(),'host_gid':r.os.getgid()}
  a={'Config':{'User':str(p['host_uid'])+':'+str(p['host_gid'])},'HostConfig':{'NetworkMode':'none','NanoCpus':1000000000,'Memory':536870912,'Tmpfs':{'/tmp':'rw,noexec,nosuid,size=512m'},'ReadonlyRootfs':True,'PidsLimit':128,'CapDrop':['ALL'],'SecurityOpt':['no-new-privileges']},'Mounts':[{'Destination':'/probe','Source':str(r.R),'RW':False},{'Destination':'/broker','Source':str(private/'socket'),'RW':False},{'Destination':'/output','Source':str(private/'output'),'RW':True}]}
  self.assertFalse(r.caps(a,p,private))
 def test_budget(self):
  p={'native_starts_cap':2,'POST_cap':2,'native_seconds':30,'models':0,'retries':0,'source_hashes':{},'host_uid':r.os.getuid(),'host_gid':r.os.getgid()}
  with self.assertRaises(ValueError):r.validate(p)
 def test_no_auth_or_credentials(self):
  self.assertFalse(set(SAFE)&{'GH_TOKEN','GITHUB_TOKEN','COPILOT_PROVIDER_API_KEY','COPILOT_PROVIDER_BEARER_TOKEN'})
  self.assertEqual(SAFE['COPILOT_OFFLINE'],'true')
 def test_actual_network_mount_caps(self):
  private=pathlib.Path('/tmp/private')
  p={'host_uid':r.os.getuid(),'host_gid':r.os.getgid()}
  a={'Config':{'User':str(p['host_uid'])+':'+str(p['host_gid'])},'HostConfig':{'NetworkMode':'none','NanoCpus':1000000000,'Memory':2147483648,'Tmpfs':{'/tmp':'rw,noexec,nosuid,size=512m'},'ReadonlyRootfs':True,'PidsLimit':128,'CapDrop':['ALL'],'SecurityOpt':['no-new-privileges']},'Mounts':[{'Destination':'/probe','Source':str(r.R),'RW':False},{'Destination':'/broker','Source':str(private/'socket'),'RW':False},{'Destination':'/output','Source':str(private/'output'),'RW':True}]}
  self.assertTrue(r.caps(a,p,private));a['Config']['User']='0:0';self.assertFalse(r.caps(a,p,private));a['Config']['User']=str(p['host_uid'])+':'+str(p['host_gid']);a['HostConfig']['NetworkMode']='bridge';self.assertFalse(r.caps(a,p,private))
 def test_proxy_authority(self):
  from tunnel_proxy import TunnelProxy
  self.assertEqual(TunnelProxy.authority,'provider.example:8000')
  self.assertEqual(TunnelProxy.unix_socket,'/broker/broker.sock')
  self.assertEqual(TunnelProxy.max_tunnel_seconds,30)
class BrokerGuards(unittest.TestCase):
 def setUp(self):
  import tempfile,threading
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name)
  self.b=r.Broker(str(self.root/'sock'),self.root);self.t=threading.Thread(target=self.b.serve_forever,daemon=True);self.t.start()
 def tearDown(self):
  self.b.shutdown()
  for sock in list(self.b.sockets):
   try:sock.shutdown(2)
   except OSError:pass
  self.b.server_close();self.t.join(2);self.tmp.cleanup()
 def request(self,raw):
  import socket
  s=socket.socket(socket.AF_UNIX);s.settimeout(4);s.connect(str(self.root/'sock'));s.sendall(raw);data=s.recv(4096);s.close();return data
 def test_wrong_verb_and_route_denied(self):
  self.assertIn(b'403',self.request(b'GET /x HTTP/1.0\r\n\r\n'))
  self.assertIn(b'429',self.request(b'POST /foreign HTTP/1.0\r\nHost: provider.example:8000\r\nContent-Length: 0\r\n\r\n'))
  self.assertEqual(self.b.posts,0);self.assertEqual(self.b.POST_headers,1)
 def test_stalled_header_socket_prebounded(self):
  import socket,time
  s=socket.socket(socket.AF_UNIX);s.settimeout(4);s.connect(str(self.root/'sock'));s.sendall(b'POST ')
  self.assertEqual(s.recv(1),b'');s.close();deadline=time.monotonic()+1
  while self.b.workers and time.monotonic()<deadline:time.sleep(.01)
  self.assertEqual(self.b.workers,0)
 def test_two_accepted_distinct_attempt_counter(self):
  raw=b'POST /v1/chat/completions HTTP/1.0\r\nHost: provider.example:8000\r\nContent-Length: 0\r\n\r\n'
  self.request(raw);self.request(raw);self.assertIn(b'429',self.request(raw))
  self.assertEqual(self.b.posts,2);self.assertEqual(self.b.POST_headers,3)
if __name__=='__main__':unittest.main()

