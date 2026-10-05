"""Uniformread-onlygenericPython/RDFsoftware;NOtaskanswer/data/target delivery."""
import hashlib,json,pathlib
from actor_public_inputs import recipe as base
from regex_actor_inputs import ROOT,manifest
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def cache():
 x=json.loads((R/'public-sparql-dependency-cache.json').read_text());assert x['prepared'];root=pathlib.Path(x['root']);assert not root.is_symlink();wheels=root/'wheels';packages=root/'packages';assert {p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in wheels.iterdir() if p.is_file() and not p.is_symlink()}=={n:{'bytes':v['bytes'],'sha256':v['sha256']} for n,v in x['artifacts'].items()};assert not any(p.is_symlink() for p in root.rglob('*'));assert {str(p.relative_to(packages)):sha(p) for p in packages.rglob('*') if p.is_file()}==x['packages_manifest'];return x

def recipe(task):
 if task!='sparql-university':raise ValueError('Sparql-onlyprospectiveinputs')
 x=cache();binding=json.loads((R/'regex-public-python-binding.json').read_text());assert binding['verified'] and manifest()==binding['files'];result=base(task);result['mounts']=[str(ROOT)+':/opt/public-python:ro',str(pathlib.Path(x['root'])/'packages')+':/opt/public-rdf:ro'];result['environment']={'PATH':'/opt/public-python/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','PYTHONPATH':'/opt/public-rdf','PYTHONDONTWRITEBYTECODE':'1'};result['guidance']='Generic public Python 3.13.7 and rdflib 7.1.4 are available through read-only software caches. Original task data is supplied by the image; no query, tests or solution are provided.';return result
