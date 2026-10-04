import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('trace_audit',Path(__file__).with_name('audit.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class AuditTests(unittest.TestCase):
    def test_stream_updates_do_not_duplicate_calls(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'trace.jsonl'
            event={'event':'step_update','step_update':{'step_type':'tool','state':'DONE','step_index':2,'tool_name':'view_file','tool_info':{'parameters':{'AbsolutePath':'x'},'output':'3 lines'}}}
            active=json.loads(json.dumps(event));active['step_update']['state']='ACTIVE'
            p.write_text('\n'.join(json.dumps(e) for e in [active,event,event]))
            self.assertEqual(len(list(a.calls(p,'agy'))),1)
    def test_all_real_attempts_included_once(self):
        audit=json.loads(Path(__file__).with_name('trace-audit.json').read_text())
        original=json.loads((a.TRIALS/'collection.json').read_text())['attempts']
        self.assertEqual(len(audit['records']),40)
        self.assertEqual({(r['harness'],r['arm'],r['task']) for r in audit['records']},{(r['harness'],r['arm'],r['task']) for r in original})
        for r in audit['records']:
            self.assertEqual(r['sha256'],a.digest(a.ROOT/r['transcript']))
if __name__=='__main__':unittest.main()
