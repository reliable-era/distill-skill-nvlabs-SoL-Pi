"""ONE output-contract preflight candidate/fixed exposed task/no old actor retry."""
import pathlib
import run_recovery_context_fasttext_screen as base
R=pathlib.Path(__file__).resolve().parent
code=base.code.replace('pi-takeover-qwen-recovery-context-admission-16k','pi-takeover-qwen-output-contract-preflight-admission-16k').replace('recovery-context-fasttext-','output-contract-preflight-fasttext-').replace('recovery-context-failure-safe-admission16k-fasttext-development-v1','output-contract-preflight-failure-safe-admission16k-fasttext-development-v1').replace("'/tmp/solpi-rc16-'","'/tmp/solpi-oc16-'").replace("prefix='solpi-rc16-'","prefix='solpi-oc16-'")
old="scope='ONEcheckedsuccessfulrecoverycontextretentiondependentcalls/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/samefailure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'";assert code.count(old)==1;code=code.replace(old,"scope='ONEconditionalcheapdownstreamoutputcontractpreflight/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/samefailure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'")
old="'run_recovery_context_fasttext_screen.py','prepare_recovery_context_runtime.py','task_artifacts.py'";assert code.count(old)==1;code=code.replace(old,"'run_recovery_context_fasttext_screen.py','prepare_recovery_context_runtime.py','run_output_contract_preflight_fasttext_screen.py','prepare_output_contract_preflight_runtime.py','task_artifacts.py'")
compile(code,'output-contract-preflight-fasttext-generated','exec')
if __name__=='__main__':
 assert not (R/'output-contract-preflight-fasttext-plan.json').exists(),'ONEnewcandidate/no oldactorretry/planoverwrite'
 exec(compile(code,'output-contract-preflight-fasttext-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
