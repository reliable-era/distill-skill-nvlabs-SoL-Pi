"""Newgrader-onlyphase;honornever-startedreplay API;old2failurespreserved."""
import pathlib
R=pathlib.Path(__file__).resolve().parent
code=(R/'probe_fasttext_wiring_r2.py').read_text();assert code.count("docker('start',grader);out['replay']")==1;code=code.replace("docker('start',grader);out['replay']","out['replay']").replace("assert not (R/'fasttext-readiness-probe-r2.json').exists()","assert not (R/'fasttext-readiness-probe-r3.json').exists()").replace("(R/'fasttext-readiness-probe-r2.json').write_text","(R/'fasttext-readiness-probe-r3.json').write_text").replace('/tmp/solpi-fasttext-wiring-r2-','/tmp/solpi-fasttext-wiring-r3-');assert code.count("out['setup']=prepare")==1;code=code.replace("out['setup']=prepare","out['never_started_replay_api_respected']=True;out['second_wiring_failure_sha256']=sha(R/'fasttext-readiness-probe-r2.json');out['setup']=prepare")
if __name__=='__main__':exec(compile(code,'fasttext-wiring-r3','exec'),{'__name__':'__main__','__file__':str(__file__)})
