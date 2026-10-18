import io,json,os,pathlib,tempfile,unittest
from unittest.mock import patch
from security import env_file,filtered_copy,read_token
from stream import parse
from preregister import allocate
from source_patch import project
from patch_outcomes import empty_result
class Protocol(unittest.TestCase):
    def fixture(self,events):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'stream';p.write_text('\n'.join(map(json.dumps,events)));return parse(p)
    def result(self,**extra):
        value=dict(type='result',is_error=False,subtype='success',usage=dict(input_tokens=10,cache_creation_input_tokens=20,cache_read_input_tokens=30,output_tokens=40),modelUsage={'provider-opus':dict(inputTokens=10,cacheCreationInputTokens=20,cacheReadInputTokens=30,outputTokens=40)});value.update(extra);return value
    def test_all_categories_and_cache_proxy(self):
        r=self.fixture([self.result()]);self.assertTrue(r['usage_complete']);self.assertEqual(r['token_volume_lower_bound'],100);self.assertEqual(r['cache_adjusted_volume_5m_proxy'],78)
    def test_missing_usage_never_imputed(self):
        r=self.fixture([dict(type='result',is_error=False)]);self.assertFalse(r['usage_complete']);self.assertEqual(r['per_model'],{})
    def test_nested_usage_coverage_and_no_double_count(self):
        msg=dict(type='assistant',parent_tool_use_id='nested',message=dict(id='msg1',model='provider-opus',usage=dict(input_tokens=1,output_tokens=2),content=[]));r=self.fixture([msg,msg,self.result()]);self.assertTrue(r['usage_complete']);self.assertEqual(r['totals']['uncached_input'],10)
        msg['message']['usage']['input_tokens']=100;r=self.fixture([msg,self.result()]);self.assertFalse(r['usage_complete'])
    def test_partial_attempt_known_message_lower_bounds_retained(self):
        e=dict(type='assistant',message=dict(id='m1',model='provider-opus',usage=dict(input_tokens=12,output_tokens=3),content=[]));r=self.fixture([e,e]);self.assertFalse(r['usage_complete']);self.assertEqual(r['token_volume_lower_bound'],15)
    def test_terminal_529_and_recovery(self):
        err=dict(type='error',error=dict(message='API Error: 529 overloaded_error'));r=self.fixture([err]);self.assertTrue(r['terminal_5xx']);self.assertEqual(r['native_error_events'][0]['statuses'],[529]);self.assertFalse(self.fixture([err,self.result()])['terminal_5xx'])
    def test_task_and_tool_text_not_error_evidence(self):
        r=self.fixture([dict(type='user',message='API Error: 529 overloaded_error'),self.result()]);self.assertFalse(r['terminal_5xx'])
    def test_token_count_529_not_http_status(self):
        r=self.fixture([dict(type='result',is_error=True,result='maximum turns reached',usage=dict(output_tokens=529))]);self.assertFalse(r['terminal_5xx'])
    def test_429_explicit_reset(self):
        r=self.fixture([dict(type='rate_limit_event',rate_limit_info=dict(status='rejected',resetsAt=2000000000)),dict(type='error',error=dict(message='API Error: 429 rate_limit'))]);self.assertTrue(r['rate_limited']);self.assertEqual(r['reset_epoch'],2000000000)
    def test_429_unknown_reset_not_guessed(self):
        r=self.fixture([dict(type='error',error='rate_limit')]);self.assertTrue(r['rate_limited']);self.assertIsNone(r['reset_epoch'])
    def test_actual_provider_id_and_skill_invocation(self):
        e=dict(type='assistant',message=dict(model='provider-opus',content=[dict(type='tool_use',name='Skill',input=dict(skill='distill-sol-pi:efficient-coding'))]));r=self.fixture([dict(type='system',subtype='init',skills=['distill-sol-pi:efficient-coding'],claude_code_version='2.1.302'),e,self.result()]);self.assertEqual(r['provider_reported_model_ids'],['provider-opus']);self.assertTrue(r['ours_loaded']);self.assertTrue(r['ours_invoked'])
    def test_redaction_crosses_chunk_boundaries(self):
        token=b'not-a-real-token-0123456789';raw=b'a'*65530+token+b'z';out=io.BytesIO();n=filtered_copy(io.BytesIO(raw),out,token);self.assertEqual(n,1);self.assertNotIn(token,out.getvalue());self.assertEqual(len(raw),len(out.getvalue()))
    def test_runtime_env_tmpfs_permissions_and_deletion(self):
        token=b'not-a-real-token-0123456789'
        with env_file(token) as name:self.assertTrue(name.startswith('/dev/shm/'));self.assertEqual(os.stat(name).st_mode&0o777,0o600);self.assertIn(token,pathlib.Path(name).read_bytes())
        self.assertFalse(pathlib.Path(name).exists())
    def test_dedicated_token_rejects_symlinks_and_open_modes(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'token';p.write_bytes(b'sk-ant-'+b'oat01-'+b'0'*32);p.chmod(0o644)
            with self.assertRaises(RuntimeError):read_token(p)
            p.chmod(0o600);self.assertEqual(read_token(p),p.read_bytes());link=pathlib.Path(d)/'link';link.symlink_to(p)
            with self.assertRaises(OSError):read_token(link)
    def test_allocation_is_stratified_and_outcome_blind(self):
        ids=['r-'+str(i) for i in range(444)];ds={t:dict(repo='a' if i<229 else 'b',outcome='not consulted') for i,t in enumerate(ids)};sample,strata=allocate(ids,ds);self.assertEqual(len(sample),150);self.assertEqual(strata['a']['study'],77)
        for row in ds.values():row['outcome']='changed'
        self.assertEqual(allocate(ids,ds)[0],sample)
    def test_frozen_sample_disjoint_and_closed_study(self):
        p=json.loads((pathlib.Path(__file__).parent/'preregistration.json').read_text());self.assertEqual(len(p['study_sample']),150);self.assertEqual(len(p['smoke_sample']),2);self.assertFalse(set(p['smoke_sample'])&set(p['study_sample']));self.assertTrue(p['gates']['study_authorized']);self.assertFalse(p['gates']['study_admissions_open'])
    def test_generated_bytecode_removed_not_real_binary_asset(self):
        raw=b'diff --git a/__pycache__/x.pyc b/__pycache__/x.pyc\nnew file mode 100644\nindex 0000000..1111111\nGIT binary patch\nliteral 1\nA\n\ndiff --git a/asset.png b/asset.png\nnew file mode 100644\nindex 0000000..1111111\nGIT binary patch\nliteral 1\nA\n\n';clean,_=project(raw);self.assertNotIn(b'x.pyc',clean);self.assertIn(b'asset.png',clean)
    def test_native_argv_forwards_stdin_and_not_credential_value(self):
        from runner import native_argv
        args=native_argv('owned','/dev/shm/example/runtime.env','ours');self.assertEqual(args[:4],['docker','exec','-i','--env-file']);self.assertNotIn('not-a-real-token',args)
    def test_study_guard_stops_before_credential_access(self):
        import runner,hashlib,types
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);h=root/'g6';h.mkdir();(h/'preregistration.json').write_text('{}');stage=dict(preregistration_sha256=hashlib.sha256(b'{}').hexdigest(),authorized_phases=['smoke']);raw=json.dumps(stage).encode();(h/'runner-stage.json').write_bytes(raw)
            with patch.object(runner,'H',h),patch.object(runner,'R',root),patch.object(runner,'check_frozen',return_value={}),patch.object(runner,'private_root',return_value=root),patch.object(runner,'command',return_value=types.SimpleNamespace(stdout=raw)),patch.object(runner,'read_token') as token:
                with self.assertRaises(AssertionError):runner.guard('commit','study')
                token.assert_not_called()
    def test_empty_patch_valid_unsolved_no_grader(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'empty.patch';p.write_bytes(b'');r=empty_result('task',p);self.assertTrue(r['grade_valid']);self.assertFalse(r['solved'])
if __name__=='__main__':unittest.main()
