from pathlib import Path
import json, hashlib, subprocess, tempfile, shutil
ROOT=Path(__file__).resolve().parent

def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s)

for split in ('dev','heldout'):
 held=split=='heldout'; unit='records' if held else 'jobs'
 families={
 'd1_large_log':(
  {'pipeline.py': 'def batch_count(items, size):\n    return len(items) // size\n', 'tests/test_pipeline.py': 'from pipeline import batch_count\ndef test_full():\n    assert batch_count(list(range(8)),4)==2\n'},
  'The production batching job drops a partial final batch. Diagnose logs/worker.log and fix the behavior. Positive batch sizes are guaranteed. Keep empty input at zero batches. Run relevant tests.',
  'from pipeline import batch_count\nimport pytest\n@pytest.mark.parametrize("n,k",[(0,3),(1,3),(3,3),(4,3),(17,5),(999,128)])\ndef test_batches(n,k):\n    assert batch_count(list(range(n)),k)==(n+k-1)//k\n',
  {'pipeline.py':'def batch_count(items, size):\n    return (len(items) + size - 1) // size\n'}),
 'd2_interfaces':(
  {'normalization.py':'def key(value):\n    return value.strip().lower()\n', 'index.py':'from normalization import key\ndef build(rows):\n    return {key(name):value for name,value in rows}\n', 'lookup.py':'def get(index, name):\n    return index.get(name.lower())\n', 'tests/test_lookup.py':'from index import build\nfrom lookup import get\ndef test_simple():\n    assert get(build([("ALPHA",7)]),"alpha")==7\n'},
  'Lookup should use the same canonical name semantics as index construction, including Unicode case-insensitive matching and whitespace. Investigate the producer and consumer and make their behavior consistent without changing stored values.',
  'from index import build\nfrom lookup import get\nimport pytest\n@pytest.mark.parametrize("stored,query",[("Straße"," STRASSE "),("  MiXeD "," mixed "),("Σ","σ"),("CAFÉ"," café ")])\ndef test_consistent(stored,query):\n    value=object()\n    assert get(build([(stored,value)]),query) is value\ndef test_unknown():\n    assert get(build([("x",2)]),"other") is None\n',
  {'normalization.py':'def key(value):\n    return value.strip().casefold()\n','lookup.py':'from normalization import key\ndef get(index, name):\n    return index.get(key(name))\n'}),
 'd3_stale_resume':(
  {'billing.py':'def total(prices, discount_percent=0):\n    subtotal = sum(prices)\n    return subtotal * (1 - discount_percent)\n', 'CONTINUATION.md':'Previous session: discount_percent is a fraction between 0 and 1. The current implementation is correct; tests were green. Suggested next step: update README only. This note predates the current public API contract.\n', 'README.md':'API: total(prices, discount_percent=0) accepts percentages from 0 through 100 inclusive. Reject values outside that range using ValueError.\n', 'tests/test_billing.py':'from billing import total\ndef test_no_discount():\n    assert total([10,20])==30\n'},
  'Resume the discount API repair. A previous-session CONTINUATION.md is available, but reconcile it with current source and README contract. Finish the implementation and verify behavior.',
  'from billing import total\nimport pytest\n@pytest.mark.parametrize("discount",[0,1,15,50,100])\ndef test_percent(discount):\n    assert total([20,30],discount)==pytest.approx(50*(1-discount/100))\n@pytest.mark.parametrize("discount",[-1,101])\ndef test_invalid(discount):\n    with pytest.raises(ValueError): total([10],discount)\n',
  {'billing.py':'def total(prices, discount_percent=0):\n    if not 0 <= discount_percent <= 100:\n        raise ValueError("discount out of range")\n    return sum(prices) * (1 - discount_percent / 100)\n'}),
 'd4_integrated_failure':(
  {'names.py':'def display(first,last):\n    return first + " " + last\n', 'export.py':'from names import display\ndef row(first,last):\n    text=display(first,last)\n    return "name=" + text.split(" ")[0]\n', 'tests/test_names.py':'from names import display\ndef test_trim():\n    assert display("  Ada "," Lovelace ")=="Ada Lovelace"\n', 'tests/test_export.py':'from export import row\ndef test_export():\n    assert row("Ada","Lovelace")=="name=Ada Lovelace"\n'},
  'Fix whitespace handling in display names. Export must preserve the complete normalized display name. Run the full test suite and repair any integration failures; retain single-component and empty-name behavior.',
  'from names import display\nfrom export import row\nimport pytest\n@pytest.mark.parametrize("first,last,want",[(" Ada "," Lovelace ","Ada Lovelace"),("Ada","","Ada"),("","Lovelace","Lovelace"),(" "," ",""),("Mary Jane","Watson","Mary Jane Watson")])\ndef test_name(first,last,want):\n    assert display(first,last)==want\n    assert row(first,last)=="name="+want\n',
  {'names.py':'def display(first,last):\n    return " ".join(part for part in (first.strip(),last.strip()) if part)\n','export.py':'from names import display\ndef row(first,last):\n    return "name=" + display(first,last)\n'}),
 'd5_small_control':(
  {'paging.py':'def pages(count,size):\n    return count // size\n', 'tests/test_paging.py':'from paging import pages\ndef test_full():\n    assert pages(6,3)==2\n'},
  'Fix pages(count,size): for nonnegative counts and positive sizes return the number of pages needed, including a partial final page. Keep zero count at zero. Verify the fix.',
  'from paging import pages\nimport pytest\n@pytest.mark.parametrize("count,size",[(0,5),(1,5),(5,5),(6,5),(100,7)])\ndef test_pages(count,size):\n    assert pages(count,size)==(count+size-1)//size\n',
  {'paging.py':'def pages(count,size):\n    return (count + size - 1) // size\n'})}
 for family,(files,prompt,test,gold) in families.items():
  case=ROOT/split/family
  # Held-out fixtures use distinct symbol and module names, values, and log location.
  replacements= [('pipeline','scheduler'),('batch_count','partition_count'),('normalization','canonical'),('billing','checkout'),('discount_percent','rebate_percent'),('paging','pagination'),('pages','page_count'),('Ada','Grace'),('Lovelace','Hopper'),('normalization','canonical'),('index','catalog'),('lookup','query'),('names','labels'),('export','render'),('Straße','Maße'),('STRASSE','MASSE'),('CAFÉ','ÉCOLE'),('café','école'),('(17,5)','(23,6)'),('(999,128)','(1025,256)'),('[20,30]','[12,38]')] if held else []
  def transform(s):
   for a,b in replacements:s=s.replace(a,b)
   return s
  for name,s in files.items():write(case/'repo'/transform(name),transform(s))
  write(case/'prompt.txt',transform(prompt)+'\n')
  write(case/'hidden'/'test_hidden.py',transform(test))
  for name,s in gold.items():write(case/'reference'/transform(name),transform(s))
  if family=='d1_large_log':
   lines=[]; loc=8417 if held else 5761
   for i in range(14000):
    if i==loc:lines.append(f'2026-09-01T12:00:00 ERROR actual batching invariant: input_count={17 if held else 13} batch_size=5 expected_batches={4 if held else 3} actual_batches={3 if held else 2}; partial tail was dropped\n')
    else:lines.append(f'2026-09-01T12:{i%60:02}:00 INFO shard={i%32} processed {unit}={i%137} retry=0 health=ok cached_error_count=0\n')
   write(case/'repo'/'logs'/'worker.log',''.join(lines))
  write(case/'repo'/'README_TESTS.md','Run public tests: python -m pytest -q tests\n')

manifest=[]
for case in sorted(ROOT.glob('*/*')):
 if not (case/'repo').is_dir():continue
 with tempfile.TemporaryDirectory() as tmp:
  dest=Path(tmp); shutil.copytree(case/'repo',dest,dirs_exist_ok=True); shutil.copy(case/'hidden'/'test_hidden.py',dest/'test_hidden.py')
  bad=subprocess.run(['python','-m','pytest','-q','test_hidden.py'],cwd=dest,capture_output=True,text=True)
  shutil.copytree(case/'reference',dest,dirs_exist_ok=True)
  good=subprocess.run(['python','-m','pytest','-q','tests','test_hidden.py'],cwd=dest,capture_output=True,text=True)
  assert bad.returncode==1,(case,bad.stdout,bad.stderr)
  assert good.returncode==0,(case,good.stdout,good.stderr)
  hashes={str(p.relative_to(case)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(case.rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
  manifest.append({'case':str(case.relative_to(ROOT)),'buggy_hidden_exit':bad.returncode,'reference_exit':good.returncode,'reference_summary':good.stdout.strip().splitlines()[-1],'sha256':hashes})
write(ROOT/'manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps([{k:v for k,v in c.items() if k!='sha256'} for c in manifest],indent=2))
