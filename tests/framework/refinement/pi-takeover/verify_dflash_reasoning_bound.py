"""Execute copied exact DFLASH CPU functions/Req methods;never load models or CUDA."""
import ast,hashlib,itertools,json,pathlib,types
import torch
torch.set_num_threads(1)
R=pathlib.Path(__file__).resolve().parent;SOURCE=pathlib.Path('/tmp/solpi-dflash-bound-review');REQ=pathlib.Path('/tmp/solpi-provider-receipt-review/schedule_batch.py')
def load_functions(path,names,namespace):
 tree=ast.parse(path.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(nodes)==len(names)
 module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),*nodes],type_ignores=[]);exec(compile(ast.fix_missing_locations(module),str(path),'exec'),namespace)
ns={'torch':torch};load_functions(SOURCE/'dflash_worker_v2.py',{'_commit_accept'},ns);load_functions(SOURCE/'dflash_utils.py',{'compute_dflash_correct_drafts_and_bonus'},ns)
commit_lengths=[]
for pattern in itertools.product([False,True],repeat=7):
 candidates=torch.arange(8,device='cpu').reshape(1,8);target=torch.zeros((1,8),dtype=torch.int64,device='cpu')
 for i,match in enumerate(pattern):target[0,i]=candidates[0,i+1] if match else 1000+i
 target[0,7]=99
 accepted,bonus=ns['compute_dflash_correct_drafts_and_bonus'](candidates=candidates,target_predict=target)
 out,lengths=ns['_commit_accept'](candidates,accepted,bonus);length=int(lengths[0]);assert 1<=length<=8 and out.shape==(1,8);commit_lengths.append(length)
class Matcher:
 def __init__(self,ids):self.marker=ids[0]
 def __len__(self):return 1
 def advance(self,state,token):return int(token==self.marker)
tree=ast.parse(REQ.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Req');names={'update_reasoning_tokens','update_finish_state','output_ids_through_stop'};methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(methods)==3
namespace={'TokenSequenceMatcher':Matcher,'FINISH_LENGTH':lambda length:types.SimpleNamespace(length=length)}
module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),ast.ClassDef(name='ExtractedReq',bases=[],keywords=[],body=methods,decorator_list=[])],type_ignores=[]);exec(compile(ast.fix_missing_locations(module),str(REQ),'exec'),namespace)
cases=0;overshoots=[]
for accepted in range(1,9):
 for remaining in range(1,9):
  for think_end in [None,*range(accepted)]:
   cap=8190;before=cap-remaining;req=namespace['ExtractedReq']();req._is_reasoning_over=False;req._think_end_matcher=None;req._think_end_match_len=0;req.reasoning_tokens=before;req.output_ids=[1]*before;req.finished_len=None;req.finished_reason=None;req.to_finish=None;req.grammar=None;req.sampling_params=types.SimpleNamespace(max_new_tokens=cap);req.finished=lambda:req.finished_reason is not None;req._check_vocab_boundary_finish=lambda _:False;req._check_str_based_finish=lambda _:False;req._check_token_based_finish=lambda _:False
   batch=[2]*accepted
   if think_end is not None:batch[think_end]=-1
   req.output_ids.extend(batch);req.update_reasoning_tokens(batch,[-1]);req.update_finish_state(accepted)
   emitted=len(req.output_ids_through_stop);expected=before+min(accepted,remaining,(think_end+1) if think_end is not None else accepted)
   assert min(req.reasoning_tokens,emitted)==expected
   delta=max(0,req.reasoning_tokens-emitted);assert delta<=7;overshoots.append(delta);cases+=1
assert min(commit_lengths)==1 and max(commit_lengths)==8 and max(overshoots)==7
report={'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'dflash_worker_v2.py',SOURCE/'dflash_utils.py',REQ]},'exact_cpu_greedy_commit_cases':len(commit_lengths),'exact_req_length_think_end_cases':cases,'maximum_committed_batch':8,'maximum_length_boundary_reasoning_overshoot':7,'derived_min_equals_emitted_reasoning_in_all_cases':True,'cuda_initialized':torch.cuda.is_initialized(),'model_POSTs':0,'server_changes':False,'limits':'CPU eager greedy commit exhaustively tested;sampling/selector/Triton paths need code-bound review. Req tests isolate lengthfinish andsingle-token think-end,not tokenizer/model billing or SSE integration.'};assert report['cuda_initialized'] is False
(R/'dflash-reasoning-bound-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
