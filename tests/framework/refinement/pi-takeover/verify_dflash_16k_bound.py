"""CPU-onlyexactReq/DFLASHproofat16Kboundaries;no oldproofartifactoverwrites."""
import pathlib,hashlib
R=pathlib.Path(__file__).resolve().parent
if __name__=='__main__':
 source=(R/'verify_dflash_reasoning_bound.py').read_text();start=source.index('for accepted in range(1,9):');end=source.index('assert min(commit_lengths)',start);block=source[start:end]
 assert block.count('cap=8190;')==1;block=block.replace('cap=8190;','')
 source=source[:start]+'for cap in [16382,16383,16384]:\n'+''.join(' '+line+'\n' for line in block.splitlines())+source[end:]
 source=source.replace("(R/'dflash-reasoning-bound-verification.json')", "(R/'dflash-16k-bound-verification.json')")
 marker="(R/'dflash-16k-bound-verification.json').write_text"
 assert source.count(marker)==1
 source=source.replace(marker,"report.update(configured_request_output_cap=16384,effective_length_caps_exercised=[16382,16383,16384],proof_template_sha256='"+hashlib.sha256((R/'verify_dflash_reasoning_bound.py').read_bytes()).hexdigest()+"')\n"+marker)
 exec(compile(source,'<16k-exact-CPU-bound>','exec'),{'__name__':'__main__','__file__':str(__file__)})
