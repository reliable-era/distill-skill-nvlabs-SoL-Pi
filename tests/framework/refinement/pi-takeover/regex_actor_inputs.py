"""ProspectiveuniformPUBLICPythonreadonlymountforRegex;notarget/testanswers."""
import json,pathlib,hashlib
from actor_public_inputs import recipe as base
R=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/tmp/solpi-tex-public-runtime-expanded/cpython/python')
def manifest():
 if ROOT.is_symlink():raise ValueError('linked public interpreter root')
 files={}
 for p in ROOT.rglob('*'):
  if p.is_symlink():
   if not p.resolve().is_relative_to(ROOT):raise ValueError('escaping public software link')
   files[p.relative_to(ROOT).as_posix()]={'link':str(p.readlink())}
  elif p.is_file():files[p.relative_to(ROOT).as_posix()]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
  elif not p.is_dir():raise ValueError('special public software member')
 return files
def recipe(task):
 if task!='regex-log':raise ValueError('Regex-onlyprospective public binding')
 binding=json.loads((R/'regex-public-python-binding.json').read_text());assert binding['verified'] and binding['files']==manifest()
 result=base(task);result['mounts']=[str(ROOT)+':/opt/public-python:ro'];result['environment']={'PATH':'/opt/public-python/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','PYTHONDONTWRITEBYTECODE':'1'};result['guidance']='Generic public Python 3.13.7 with the standard library is available as python3 through a read-only software cache. No task output, tests or solution are provided.';return result
