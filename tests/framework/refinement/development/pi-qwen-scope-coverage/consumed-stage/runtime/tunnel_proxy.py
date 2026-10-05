"""Exact authority CONNECT-to-owned-Unix broker, no TCP destination selection."""
import http.server,socket,selectors,time,threading,os,importlib.util,pathlib
R=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('stream_proxy',R/'stream_proxy.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
class TunnelProxy(base.StreamingProxy):
 authority='provider.example:8000';unix_socket='/broker/broker.sock'
 max_tunnel_seconds=600;max_client_bytes=262144;max_upstream_bytes=2097152
 stats={'CONNECT':0,'denied':0,'completed':0,'errors':0};guard=threading.Lock()
 def do_CONNECT(self):
  with self.guard:type(self).stats['CONNECT']+=1
  if self.path!='provider.example:8000':
   with self.guard:type(self).stats['denied']+=1
   self.send_error(403);return
  upstream=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);selector=selectors.DefaultSelector();deadline=time.monotonic()+self.max_tunnel_seconds;counts={'client':0,'upstream':0}
  try:
   upstream.settimeout(min(3,self.max_tunnel_seconds));upstream.connect(self.unix_socket)
   self.send_response(200,'Connection Established');self.end_headers();self.wfile.flush()
   self.connection.setblocking(False);upstream.setblocking(False);selector.register(self.connection,selectors.EVENT_READ,('client',upstream));selector.register(upstream,selectors.EVENT_READ,('upstream',self.connection))
   while True:
    remaining=deadline-time.monotonic()
    if remaining<=0:raise TimeoutError('tunnel deadline')
    events=selector.select(min(remaining,1))
    for key,_ in events:
     kind,target=key.data;chunk=key.fileobj.recv(8192)
     if not chunk:
      with self.guard:type(self).stats['completed']+=1
      return
     counts[kind]+=len(chunk);limit=self.max_client_bytes if kind=='client' else self.max_upstream_bytes
     if counts[kind]>limit:raise ValueError('tunnel byte cap')
     # Temporarily blocking bounded write; deadline, no unbounded bufferedrelay.
     target.settimeout(max(.001,deadline-time.monotonic()));target.sendall(chunk);target.setblocking(False)
  except Exception:
   with self.guard:type(self).stats['errors']+=1
  finally:
   selector.close()
   for sock in [upstream,self.connection]:
    try:sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   upstream.close();self.close_connection=True
if __name__=='__main__':
 s=importlib.util.spec_from_file_location('server',R/'server.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
 if os.environ.get('BROKER_SOCKET')!='/broker/broker.sock':raise SystemExit('fixed socket required')
 server=b.OwnedServer(('0.0.0.0',8080),TunnelProxy)
 import signal
 signal.signal(signal.SIGTERM,lambda *a:threading.Thread(target=server.shutdown,daemon=True).start())
 try:server.serve_forever()
 finally:server.cleanup()
