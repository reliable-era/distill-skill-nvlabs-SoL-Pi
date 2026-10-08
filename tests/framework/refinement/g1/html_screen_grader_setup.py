"""Task-local offline HTML verifier dependencies; original tests unchanged."""
import json, pathlib, hashlib
import cached_grader_setup as base
G=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/tmp/solpi-g1-html-wheels')

def inputs():
    value=base.inputs();pins=json.loads((G/'mechanisms/html-public-wheels.json').read_text())['wheel_hashes']
    actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.whl')}
    if actual!=pins:raise RuntimeError('HTML public verifier wheels changed')
    return {**value,'mounts':value['mounts']+[str(ROOT)+':/opt/html-wheels:ro'],'html_wheel_hashes':pins}

def prepare(container,image_id,root):
    inputs()
    return base.prepare(container,image_id,root)

def grade_argv(container):
    argv=base.grade_argv(container)
    old='UV_FIND_LINKS=/opt/public-wheels'
    assert argv.count(old)==1
    argv[argv.index(old)]='UV_FIND_LINKS=/opt/html-wheels'
    return argv
