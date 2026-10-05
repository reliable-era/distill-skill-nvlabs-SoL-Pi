"""Fail-closed, read-only aggregate of local and gpu01 scheduler loads."""
import http.client,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
BACKENDS=(('127.0.0.1',18002),('127.0.0.1',18001),
          ('10.193.104.97',18002),('10.193.104.97',18001))
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  status=200;rows=[]
  try:
   if self.path!='/get_load':raise ValueError('unsupported path')
   for host,port in BACKENDS:
    c=http.client.HTTPConnection(host,port,timeout=1)
    try:
     c.request('GET','/get_load');r=c.getresponse();raw=r.read(65537)
     if r.status!=200 or len(raw)>65536:raise ValueError('backend unavailable')
     data=json.loads(raw)
     if not isinstance(data,list) or not data:raise ValueError('missing backend load')
     for row in data:
      if not isinstance(row,dict) or any(type(row.get(k)) is not int or row[k]<0 for k in ['num_reqs','num_waiting_reqs']):raise ValueError('invalid backend load')
      rows.append(dict(row,backend=host+':'+str(port)))
    finally:c.close()
  except Exception:
   status=503;rows={'error':'complete backend load unavailable;do not infer idleness'}
  body=json.dumps(rows).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',18003),Handler).serve_forever()
