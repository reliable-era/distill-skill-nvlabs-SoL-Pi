"""ExecuteACTUALdraftASTcallbackswithdeclaredFAKEDocker/session;0POST/native/model."""
import ast,pathlib,json,tempfile,types,threading,time,tarfile,io,contextlib,hashlib,unittest
from prospective_controller_cell import run_cell
from prospective_task_capture import build
R=pathlib.Path(__file__).resolve().parent;D=R/'prepared-failure-safe-fasttext-r2'
class Tests(unittest.TestCase):
 def test_actual_callbacks_capture_failure(self):
  manifest=json.loads((D/'manifest.json').read_text());code=(D/'controller.py').read_text();self.assertEqual(hashlib.sha256(code.encode()).hexdigest(),manifest['controller_sha256']);tree=ast.parse(code);callbacks=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in ['stop_owned_issuer','capture_callback','grade_callback','accounting_callback','teardown_cell']];self.assertEqual(len(callbacks),5)
  for expired in [False,True]:
   with self.subTest(expired=expired),tempfile.TemporaryDirectory(prefix='solpi-draft-callback-') as tmp:
    d=pathlib.Path(tmp);row={'arm':'none','native_exit':1,'actor_seconds':.001};image='sha256:FAKE';name='FAKE-owned-only';calls=[];s=types.SimpleNamespace(active='none',deadline=time.monotonic()+600,posts=1,lock=threading.Lock(),connections={1:True} if expired else {},forward_lock=threading.Lock());s.accounting_rows=lambda arm:[{'request':1,'usage_complete':False,'error':None,'provider_status':200,'provider_backend':'FAKE'}];s.abort_owned_connections=lambda:(calls.append('abortowned'),s.connections.clear())
    def docker(*args):
     self.assertEqual(args[-1],name);calls.append(args[0])
     if args[0]=='inspect':return json.dumps([{'Image':image,'State':{'Running':False,'Paused':False},'Mounts':[]}])
     self.assertEqual(args[:3],('stop','-t','0'));return ''
    private=build(R,hashlib.sha256((R/'task_artifacts.py').read_bytes()).hexdigest(),hashlib.sha256((R/'artifact_capture.py').read_bytes()).hexdigest(),d/'capture-rejections.json')
    private.__globals__['subprocess']=types.SimpleNamespace(run=lambda *a,**kw:types.SimpleNamespace(stdout=docker('inspect',name)))
    @contextlib.contextmanager
    def archive(container,path):
     self.assertEqual((container,path),(name,'/app/model.bin'));header=tarfile.TarInfo('model.bin');header.size=167772161;yield io.BytesIO(header.tobuf())
    private.__globals__['docker_archive']=archive
    ns={'row':row,'d':d,'name':name,'arm':'none','actor_image':image,'docker':docker,'json':json,'time':time,'SOURCE':types.SimpleNamespace(name='train-fasttext'),'private_capture':private,'stopped_output_present':lambda *a:True,'session':s,'known_cost_lower_bound':lambda requests:0}
    exec(compile(ast.fix_missing_locations(ast.Module(body=callbacks,type_ignores=[])),'actualdraftcallbacks','exec'),ns)
    kwargs={'now':lambda:s.deadline-10+240+.01} if expired else {}
    run_cell(s,row,d/'partial-row.json',ns['stop_owned_issuer'],ns['capture_callback'],ns['grade_callback'],ns['teardown_cell'],ns['accounting_callback'],**kwargs)
    self.assertEqual(row['failure']['type'],'CaptureError');self.assertFalse(row['official_grade_available']);self.assertTrue(row['teardown_complete']);self.assertEqual(row['actor_seconds'],.001);self.assertEqual(row['unknown_cost_requests'],[1]);self.assertFalse(row['cost_complete']);self.assertFalse((d/'captured/payload-0').exists());self.assertEqual(json.loads((d/'capture-rejections.json').read_text())[0]['reason'],'size_cap');self.assertEqual(s.posts,1);self.assertNotIn('grade',row);self.assertTrue(calls.count('stop')==2);self.assertEqual(row['completion_drain']['drained'],not expired);self.assertEqual(calls.count('abortowned'),1 if expired else 0)
 def test_main_is_inert_and_unstarted_only(self):
  tree=ast.parse((D/'controller.py').read_text());main=next(n for n in tree.body if isinstance(n,ast.If) and '__name__' in ast.unparse(n.test));self.assertIsInstance(main.body[0],ast.Raise);code=ast.unparse(tree);self.assertIn("arms = ['none', 'K']",code);self.assertNotIn('rows.append(row)',code[code.index('session.finish(True)'):]);self.assertIn('consumed_original_POST=31',code)
if __name__=='__main__':unittest.main()
