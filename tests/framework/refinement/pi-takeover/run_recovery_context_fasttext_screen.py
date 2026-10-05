"""ONEnewrecoverycontexthypothesis/exposedfixedtask4arms/0oldactorreplay."""
import pathlib
import run_byte_bounded_fasttext_screen as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
code=code.replace('pi-takeover-qwen-byte-bounded-admission-16k','pi-takeover-qwen-recovery-context-admission-16k').replace('byte-bounded-fasttext-','recovery-context-fasttext-').replace('byte-bounded-failure-safe-admission16k-fasttext-development-v1','recovery-context-failure-safe-admission16k-fasttext-development-v1').replace("'/tmp/solpi-bb16-'","'/tmp/solpi-rc16-'").replace("prefix='solpi-bb16-'","prefix='solpi-rc16-'")
old="scope='ONEbyteboundedlogbullet/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/failure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'";assert code.count(old)==1;code=code.replace(old,"scope='ONEcheckedsuccessfulrecoverycontextretentiondependentcalls/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/samefailure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'")
old="'run_byte_bounded_fasttext_screen.py','prepare_byte_bounded_runtime.py','task_artifacts.py'";assert code.count(old)==1;code=code.replace(old,"'run_byte_bounded_fasttext_screen.py','prepare_byte_bounded_runtime.py','run_recovery_context_fasttext_screen.py','prepare_recovery_context_runtime.py','task_artifacts.py'")
compile(code,'recovery-context-fasttext-generated','exec')
if __name__=='__main__':
 assert not (R/'recovery-context-fasttext-plan.json').exists(),'ONEnewcandidate/no oldactorretry/planoverwrite'
 exec(compile(code,'recovery-context-fasttext-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
