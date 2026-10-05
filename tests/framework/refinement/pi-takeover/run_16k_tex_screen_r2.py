"""Zero-startpreflightrepair;preservesr1source/results;notanactorretry."""
import pathlib
import run_16k_tex_screen as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
old="prior=json.loads((R/'source-backed-doom-plan.json').read_text())";assert code.count(old)==1
code=code.replace(old,"prior=json.loads((R.parent/'development/pi-takeover-qwen-source-backed-verification/plan.json').read_text());assert len(prior['shared_inference_locks'])==2")
old="sha(R/'source-backed-doom-plan.json')";assert code.count(old)==1
code=code.replace(old,"sha(R.parent/'development/pi-takeover-qwen-source-backed-verification/plan.json')")
old="'run_16k_tex_screen.py','run_source_backed_doom_screen.py'";assert code.count(old)==1;code=code.replace(old,"'run_16k_tex_screen_r2.py','run_16k_tex_screen.py','run_source_backed_doom_screen.py'")
code=code.replace('16k-tex-plan.json','16k-tex-r2-plan.json').replace('16k-tex-result.json','16k-tex-r2-result.json').replace('16k-tex-progress.json','16k-tex-r2-progress.json')
code=code.replace("protocol='source-backed-16k-tex-development-v1'","protocol='source-backed-16k-tex-development-r2'")
compile(code,'16k-tex-r2-generated','exec')
if __name__=='__main__':exec(compile(code,'16k-tex-r2-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
