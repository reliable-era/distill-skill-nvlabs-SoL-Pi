import json,pathlib,random,socket,tempfile,time,unittest
from five_xx import Circuit,backoff,decision
from transport import Broker
from retry_policy import native_http5xx
class Policy(unittest.TestCase):
 def test_terminal_only_and_five_attempt_limit(self):
  raw=b'{"type":"error","message":"unexpected status 502 Bad Gateway"}\n{"type":"turn.failed","error":{"message":"unexpected status 502 Bad Gateway"}}\n';r=dict(timeout=False,grader_timeout=False)
  self.assertTrue(decision(r,4,raw)['retry']);self.assertTrue(decision(r,5,raw)['infra_exhausted']);self.assertFalse(decision(r,5,raw)['retry']);self.assertFalse(decision(r,1,raw+b'{"type":"turn.completed"}\n')['retry']);self.assertFalse(decision(dict(timeout=True),1,raw)['retry']);self.assertFalse(decision(r,1,b'{"type":"turn.failed","error":{"message":"ordinary model failure"}}')['retry'])
 def test_exponential_backoff_jitter_cap(self):
  rng=random.Random(7)
  for n in range(1,9):
   d=backoff(n,rng);base=min(900,60*2**(n-1));self.assertGreaterEqual(d,base);self.assertLessEqual(d,min(900,base*1.2))
 def test_circuit_eight_of_last_sixteen(self):
  with tempfile.TemporaryDirectory(prefix='g5-circuit-test-') as d:
   clock=[1000];c=Circuit(pathlib.Path(d)/'pauses.jsonl',clock=lambda:clock[0])
   for i in range(15):c.finish(i<8,'cell',i)
   self.assertEqual(c.until,0);c.finish(False,'cell',16);self.assertEqual(c.until,1600);clock[0]=1601;c.wait();self.assertEqual(len(c.recent),16)
 def test_longest_dataset_task_all_arms_short_socket(self):
  h=pathlib.Path(__file__).resolve().parent;dataset=h.parents[2]/'eval/swebench_verified.jsonl';tasks=[json.loads(l)['instance_id'] for l in dataset.read_text().splitlines()];task=max(tasks,key=lambda x:len(x.encode()))
  with tempfile.TemporaryDirectory(prefix='solpi-g5-socket-regression-') as t:
   for arm in ('none','K','ours','Both'):
    root=pathlib.Path(t)/'models'/task/('g5-029-'+arm+'-a1')/'transport';root.parent.mkdir(parents=True,exist_ok=True);self.assertGreater(len(str(root/'socket/broker.sock').encode()),107);b=Broker(root,time.monotonic()+60,arm);b.start();short=b.short_socket_dir;self.assertLessEqual(len(str(short/'broker.sock').encode()),107);self.assertTrue((root/'socket').is_symlink())
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:s.settimeout(2);s.connect(str(short/'broker.sock'));s.sendall(b'GET / HTTP/1.0\r\n\r\n');self.assertIn(b'405',s.recv(4096))
    b.close();self.assertFalse(short.exists());self.assertEqual(b.posts,0)
if __name__=='__main__':unittest.main()
