"""Owned transport mock: emits method/path only; never logs headers/body."""
import http.server,json
class Mock(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  print(json.dumps({'method':self.command,'path':self.path.split('?',1)[0]}),flush=True)
  self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"error":{"message":"owned deterministic transport diagnostic","type":"mock_error"}}')
 def do_GET(self):self.do_POST()
http.server.ThreadingHTTPServer(('0.0.0.0',8000),Mock).serve_forever()
