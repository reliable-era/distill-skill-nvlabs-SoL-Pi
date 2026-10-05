"""Owned Unix HTTP synthetic upstream ONLY. Constant output, zero inference."""
import socketserver,http.server,json,hashlib,threading
from provider_fixture import MODEL,final_stream
class Upstream(socketserver.UnixStreamServer):
 def __init__(self,path,root):self.root=root;self.records=[];self.lock=threading.Lock();super().__init__(path,Handler)
 def persist(self):(self.root/'upstream-ledger.json').write_text(json.dumps({'synthetic_ONLY':True,'inference_calls':0,'records':self.records},indent=2)+'\n')
class Handler(http.server.BaseHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,*args):pass
 def do_POST(self):
  self.connection.settimeout(3)
  n=int(self.headers.get('Content-Length','-1'))
  if not 0<=n<=262144 or self.path!='/v1/chat/completions':self.send_error(429);return
  body=self.rfile.read(n);obj=json.loads(body)
  with self.server.lock:
   if self.server.records or len(body)!=n or obj.get('model')!=MODEL or obj.get('stream') is not True:self.send_error(429);return
   payload=final_stream();record={'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'response_bytes':len(payload),'response_sha256':hashlib.sha256(payload).hexdigest(),'status':200,'inference_calls':0,'synthetic_ONLY':True,'response_write_complete':False};self.server.records.append(record);self.server.persist()
  self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Transfer-Encoding','chunked');self.send_header('Connection','close');self.end_headers()
  try:
   for i in range(0,len(payload),13):
    chunk=payload[i:i+13];self.wfile.write(('%x\r\n'%len(chunk)).encode()+chunk+b'\r\n');self.wfile.flush()
   self.wfile.write(b'0\r\n\r\n');self.wfile.flush();record['response_write_complete']=True
  finally:self.close_connection=True;self.server.persist()
