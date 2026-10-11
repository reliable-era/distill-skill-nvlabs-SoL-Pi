"""Container-local TCP to Unix relay. --network none: only loopback and socket.
No Internet, DNS, HTTP proxy, configurable upstream, or secret material.
"""
import select,socket,socketserver,threading
class Handler(socketserver.BaseRequestHandler):
 def handle(self):
  upstream=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
  try:
   upstream.connect('/broker/broker.sock');sockets=[self.request,upstream]
   while True:
    ready,_,_=select.select(sockets,[],[],7500)
    if not ready:return
    for source in ready:
     data=source.recv(65536)
     if not data:return
     (upstream if source is self.request else self.request).sendall(data)
  except OSError:pass
  finally:upstream.close()
class Server(socketserver.ThreadingMixIn,socketserver.TCPServer):
 allow_reuse_address=True;daemon_threads=True
if __name__=='__main__':
 with Server(('127.0.0.1',8080),Handler) as server:server.serve_forever()
