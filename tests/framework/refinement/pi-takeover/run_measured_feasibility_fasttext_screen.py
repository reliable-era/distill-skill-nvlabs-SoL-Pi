"""ONEnewconditionalmeasurementhypothesis/exposedfixedtask4arms/0oldactorreplay."""
import pathlib
import run_byte_bounded_fasttext_screen as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
code=code.replace('pi-takeover-qwen-byte-bounded-admission-16k','pi-takeover-qwen-measured-feasibility-admission-16k').replace('byte-bounded-fasttext-','measured-feasibility-fasttext-').replace('byte-bounded-failure-safe-admission16k-fasttext-development-v1','measured-feasibility-failure-safe-admission16k-fasttext-development-v1').replace("'/tmp/solpi-bb16-'","'/tmp/solpi-mf16-'").replace("prefix='solpi-bb16-'","prefix='solpi-mf16-'")
old="scope='ONEbyteboundedlogbullet/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/failure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'";assert code.count(old)==1;code=code.replace(old,"scope='ONEconditionalcheapconstraint-drivermeasurement/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/samefailure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'")
old="'run_byte_bounded_fasttext_screen.py','prepare_byte_bounded_runtime.py','task_artifacts.py'";assert code.count(old)==1;code=code.replace(old,"'run_byte_bounded_fasttext_screen.py','prepare_byte_bounded_runtime.py','run_measured_feasibility_fasttext_screen.py','prepare_measured_feasibility_runtime.py','task_artifacts.py'")
compile(code,'measured-feasibility-fasttext-generated','exec')
if __name__=='__main__':
 assert not (R/'measured-feasibility-fasttext-plan.json').exists(),'ONEnewcandidate/no oldactorretry/planoverwrite'
 exec(compile(code,'measured-feasibility-fasttext-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
