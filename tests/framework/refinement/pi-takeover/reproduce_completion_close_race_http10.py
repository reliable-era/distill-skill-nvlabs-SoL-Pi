"""ONEcontrolledrealLOCALHTTPchunkedread/close race;0models/native/benchmarks."""
import http.server,http.client,threading,time,json,pathlib,hashlib,types
from prospective_completion_drain import drain
R=pathlib.Path(__file__).resolve().parent
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  self.send_response(200);self.send_header('Transfer-Encoding','chunked');self.end_headers();self.wfile.write(b'3\r\nACK\r\n0\r\n\r\n');self.wfile.flush()
def scenario(early_close):
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);serve=threading.Thread(target=server.serve_forever);serve.start();c=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3);c.request('GET','/synthetic');response=c.getresponse();barrier=threading.Event();release=threading.Event();original=response._get_chunk_left;first=[True];raw=types.SimpleNamespace(active='synthetic-only',deadline=time.monotonic()+10,posts=1,lock=threading.Lock(),connections={c:True});session=types.SimpleNamespace(raw_session=raw,forward_lock=threading.Lock());result={}
 def controlled():
  value=original()
  if first[0]:first[0]=False;barrier.set();assert release.wait(2)
  return value
 response._get_chunk_left=controlled
 def read():
  with session.forward_lock:
   try:
    chunks=[]
    while True:
     chunk=response.read1(8192)
     if not chunk:break
     chunks.append(chunk)
    result.update(body=b''.join(chunks).decode(),stream_eof=True)
   except Exception as e:result.update(error=type(e).__name__,message=str(e),stream_eof=False)
   finally:
    with raw.lock:raw.connections.clear()
 worker=threading.Thread(target=read);worker.start()
 try:
  assert barrier.wait(2)
  if early_close:c.close();release.set()
  else:
   timer=threading.Timer(.05,release.set);timer.start();result['passive_drain']=drain(session);timer.join()
  worker.join(3);assert not worker.is_alive();result['deadline_unchanged']=raw.deadline==session.raw_session.deadline
 finally:
  release.set();worker.join(3);c.close();server.shutdown();server.server_close();serve.join(3)
 result['workers_exited']=not worker.is_alive() and not serve.is_alive();return result
if __name__=='__main__':
 assert not (R/'completion-close-race-proof.json').exists();old=scenario(True);new=scenario(False);assert old['error']=='AttributeError' and not old['stream_eof'] and new['body']=='ACK' and new['stream_eof'] and new['passive_drain']['drained'];p=R/'prospective_completion_drain.py';proof={'old_early_close':old,'prospective_drain_before_close':new,'real_model_POST':0,'native_jobs':0,'benchmark_or_gold_runs':0,'historical_request31_exact_stack_proven':False,'mechanism':'HTTPResponse._get_chunk_leftreturnslen thenconcurrentconnection.closeclearsfp beforefp.read1','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'stdlib_HTTP_client_sha256':hashlib.sha256(pathlib.Path(http.client.__file__).read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'deployed':False};(R/'completion-close-race-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
