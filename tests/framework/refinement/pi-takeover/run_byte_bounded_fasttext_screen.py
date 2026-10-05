"""ONEnewcandidatefourarmexposeddevelopment;no oldactorretry/receiptpooling."""
import pathlib,hashlib,json
import prepare_failure_safe_fasttext_controller_r3 as source
R=pathlib.Path(__file__).resolve().parent
code=source.materialize()
def replace(old,new):
 global code
 assert code.count(old)==1,old[:90];code=code.replace(old,new)
replace('R=pathlib.Path(__file__).resolve().parent.parent;D=','R=pathlib.Path(__file__).resolve().parent;D=')
code=code.replace('pi-takeover-qwen-coalesced-verification-admission-16k','pi-takeover-qwen-byte-bounded-admission-16k')
replace("arms=['none','K']","arms=['none','K','candidate','Both']")
replace("'native_starts_cap':2,'provider_POST_cap':32","'native_starts_cap':4,'provider_POST_cap':64")
replace("protocol='failure-safe-cell-admission16k-fasttext-unstarted-only-v1'","protocol='byte-bounded-failure-safe-admission16k-fasttext-development-v1'")
replace("consumed_original_starts=2,consumed_original_POST=31,started_arms_never_repeated=['candidate','Both'],new_protocol_no_comparator_or_promotion_claim=True","historical_stage_closed_starts=2,historical_stage_closed_POST=31,historical_stage_not_replayed=True,exposed_development_not_confirmation=True,transport_skill_causal_claim=False,old_cohort_pooling=False")
replace("scope='ONEverificationsequencingbullet/nextfixedindex8fastText/uniform16K/privateadmission/publictrainingsoftwareALLarms;freshdevelopmentnotsealedconfirmation/nomatrixoldcohortpoolorcausalclaim'","scope='ONEbyteboundedlogbullet/exposedfixedindex8fastText/newcandidateALL4arms/uniform16K/failure-safeownedepoch;notconfirmation/nooldcohortpooling/noautomaticmatrix/noqualityeconomypromotionclaim'")
replace("'prospective_owned_epoch.py','task_artifacts.py'","'prospective_owned_epoch.py','run_byte_bounded_fasttext_screen.py','prepare_byte_bounded_runtime.py','task_artifacts.py'")
replace("  raise SystemExit('prepared-only draft;not scheduled;no actor/model execution')\n",'')
code=code.replace('failure-safe-fasttext-plan.json','byte-bounded-fasttext-plan.json').replace('failure-safe-fasttext-progress.json','byte-bounded-fasttext-progress.json').replace('failure-safe-fasttext-result.json','byte-bounded-fasttext-result.json').replace("'/tmp/solpi-fs16-'","'/tmp/solpi-bb16-'").replace("prefix='solpi-fs16-'","prefix='solpi-bb16-'")
replace("  controls=json.loads(","  assert json.loads((R/'owned-docker-failure-gate-audit.json').read_text())['passed']\n  assert json.loads((R/'failure-cell-integration-r3-audit.json').read_text())['passed']\n  controls=json.loads(")
compile(code,'byte-bounded-fasttext-generated','exec')
if __name__=='__main__':
 assert not (R/'byte-bounded-fasttext-plan.json').exists(),'ONEnewhypothesiscohort/no actorretry/planoverwrite'
 exec(compile(code,'byte-bounded-fasttext-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
