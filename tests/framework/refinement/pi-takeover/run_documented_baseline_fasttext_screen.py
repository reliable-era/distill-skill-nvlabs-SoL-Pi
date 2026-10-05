"""ONEnewdocumentedbaselinehypothesis/exposedfixedtask4arms/0oldactorreplay."""
import pathlib
import run_byte_bounded_fasttext_screen as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
code=code.replace('pi-takeover-qwen-byte-bounded-admission-16k','pi-takeover-qwen-documented-baseline-admission-16k').replace('byte-bounded-fasttext-','documented-baseline-fasttext-').replace('byte-bounded-failure-safe-admission16k-fasttext-development-v1','documented-baseline-failure-safe-admission16k-fasttext-development-v1').replace("'/tmp/solpi-bb16-'","'/tmp/solpi-db16-'").replace("prefix='solpi-bb16-'","prefix='solpi-ff16-'")
old="scope='ONEbyteboundedlogbullet/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/failure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'";assert code.count(old)==1;code=code.replace(old,"scope='ONEdocumentedidiomaticbaselinewithrequirementorobservedevidenceoverrides/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/samefailure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'")
old="'run_byte_bounded_fasttext_screen.py','prepare_byte_bounded_runtime.py','task_artifacts.py'";assert code.count(old)==1;code=code.replace(old,"'run_byte_bounded_fasttext_screen.py','prepare_byte_bounded_runtime.py','run_documented_baseline_fasttext_screen.py','prepare_documented_baseline_runtime.py','task_artifacts.py'")
compile(code,'documented-baseline-fasttext-generated','exec')
if __name__=='__main__':
 assert not (R/'documented-baseline-fasttext-plan.json').exists(),'ONEnewcandidate/no oldactorretry/planoverwrite'
 exec(compile(code,'documented-baseline-fasttext-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
