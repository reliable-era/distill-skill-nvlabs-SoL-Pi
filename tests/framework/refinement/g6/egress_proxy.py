"""CONNECT-only allowlist. No TLS interception,headers,payload or auth logs."""
import http.server,select,socket,socketserver,time
ALLOWED='api.anthropic.com:443'
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_CONNECT(self):
        if self.path.lower()!=ALLOWED:
            self.send_error(403,'G6 destination denied');return
        try: upstream=socket.create_connection(('api.anthropic.com',443),timeout=30)
        except OSError: self.send_error(503,'G6 API connect unavailable');return
        self.send_response(200,'Connection Established');self.end_headers()
        upstream.settimeout(7500);self.connection.settimeout(7500)
        try:
            until=time.monotonic()+7500
            while time.monotonic()<until:
                ready,_,_=select.select([self.connection,upstream],[],[],10)
                for source in ready:
                    data=source.recv(65536)
                    if not data:return
                    (upstream if source is self.connection else self.connection).sendall(data)
                    until=time.monotonic()+7500
        except (OSError,ValueError): pass
        finally: upstream.close()
    def do_GET(self):self.send_error(403,'G6 CONNECT only')
    do_POST=do_GET
class Server(socketserver.ThreadingMixIn,http.server.HTTPServer):
    daemon_threads=True
    def handle_error(self,*args):pass
if __name__=='__main__':Server(('0.0.0.0',3128),Handler).serve_forever()
