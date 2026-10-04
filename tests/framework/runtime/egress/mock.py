import http.server
class Mock(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  self.send_response(200);self.end_headers();self.wfile.write(b'mock-provider-ok')
 def do_POST(self):self.do_GET()
http.server.ThreadingHTTPServer(('0.0.0.0',8000),Mock).serve_forever()
