import unittest,tempfile,pathlib,json,types,threading,socketserver,http.server
from copilot_host_cutoff_controller import HostCutoffController
from copilot_owned_issuance_guard import relay_response
import importlib.util
PROXY=pathlib.Path(__file__).resolve().parent.parent/'copilot-native-local-route/mock-midstream-cutoff/stream_proxy.py'
spec=importlib.util.spec_from_file_location('saved_copilot_stream_proxy',PROXY);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Tests(unittest.TestCase):
 def controller(self,root,changed=False,stale=False,stop_hook=lambda:None):
  c={'arm':'candidate','deadline':123,'container_id':'exact-id','name':'owned-name','image':'pinned-image','row':{},'path':root/'row.json'};session=types.SimpleNamespace(active='candidate',deadline=999 if stale else 123);calls=[]
  def docker(*args):
   calls.append(args)
   if args[0]=='stop':
    self.assertIn('partial_provider_response',json.loads(c['path'].read_text()));stop_hook();return ''
   return json.dumps([{'Id':'changed' if changed else 'exact-id','Image':'pinned-image','State':{'Running':len(calls)==1,'Paused':False}}])
  return HostCutoffController(session,c,docker,{'owned-name'},root),calls
 def test_real_unix_HTTP_eof_after_identity_verified_stop(self):
  with tempfile.TemporaryDirectory(prefix='solpi-hostguard-') as tmp:
   root=pathlib.Path(tmp);entered=threading.Event();release=threading.Event();eof=threading.Event();errors=[];order=[]
   def stop_hook():entered.set();self.assertTrue(release.wait(3));order.append('stop')
   controller,calls=self.controller(root,stop_hook=stop_hook);body=b'data: {"content":"ACK"}\n\n';promised=len(body)+128
   class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
     try:
      if not controller.guard.admit():self.send_error(429);return
      controller.journal_partial(body,promised);self.send_response(200);self.send_header('Content-Length',str(promised));self.end_headers();self.wfile.write(body);self.wfile.flush();order.append('partial_written');controller.stop_before_eof();order.append('stop_receipt');self.close_connection=True
     except Exception as e:errors.append(type(e).__name__+':'+str(e))
   class Server(socketserver.UnixStreamServer):pass
   server=Server(str(root/'broker.sock'),Handler);thread=threading.Thread(target=server.serve_forever);thread.start()
   def client():
    c=module.UnixHTTPConnection(str(root/'broker.sock'),3)
    try:
     c.request('POST','/v1/chat/completions',b'{}');r=c.getresponse();self.assertEqual(r.read1(8192),body);order.append('partial_read');self.assertEqual(r.read1(8192),b'');order.append('EOF');eof.set()
    except Exception as e:errors.append(type(e).__name__+':'+str(e))
    finally:c.close()
   reader=threading.Thread(target=client);reader.start()
   try:
    self.assertTrue(entered.wait(3));self.assertFalse(eof.wait(.05));release.set();reader.join(3);self.assertFalse(reader.is_alive());self.assertEqual(errors,[]);self.assertTrue(eof.is_set());self.assertLess(order.index('stop_receipt'),order.index('EOF'));self.assertEqual([x[0] for x in calls],['inspect','stop','inspect']);row=json.loads((root/'row.json').read_text());self.assertTrue(row['issuer_stop_receipt']['owned_stop_verified']);self.assertIsNone(row['partial_provider_response']['usage'])
   finally:release.set();server.shutdown();thread.join(3);server.server_close();reader.join(3)
 def test_wrong_container_identity_never_stopped(self):
  with tempfile.TemporaryDirectory() as tmp:
   c,calls=self.controller(pathlib.Path(tmp),changed=True);c.journal_partial(b'x',2)
   with self.assertRaises(RuntimeError):c.stop_before_eof()
   self.assertEqual([x[0] for x in calls],['inspect']);self.assertFalse(c.guard.abort_result['owned_stop_verified'])
 def test_stale_epoch_never_touches_docker(self):
  with tempfile.TemporaryDirectory() as tmp:
   c,calls=self.controller(pathlib.Path(tmp),stale=True);c.journal_partial(b'x',2)
   with self.assertRaises(RuntimeError):c.stop_before_eof()
   self.assertEqual(calls,[])
 def test_missing_journal_no_stop(self):
  with tempfile.TemporaryDirectory() as tmp:
   c,calls=self.controller(pathlib.Path(tmp))
   with self.assertRaises(RuntimeError):c.stop_before_eof()
   self.assertEqual(calls,[])
 def test_no_partial_receipt_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   c,calls=self.controller(pathlib.Path(tmp));c.journal_partial(b'x',2)
   with self.assertRaises(FileExistsError):c.journal_partial(b'new',4)
   self.assertEqual((pathlib.Path(tmp)/'partial-response.sse').read_bytes(),b'x');self.assertEqual(calls,[])
if __name__=='__main__':unittest.main()
