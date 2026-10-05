"""Task-specificgenericRDFpreload;unchangeddisconnectedoriginaltests."""
import pathlib
from prospective_output_budget import module
import cached_grader_setup as base
from sparql_public_inputs import cache
R=pathlib.Path(__file__).resolve().parent

def inputs():
 result=base.inputs();x=cache();result.update(mounts=[str(pathlib.Path(x['root'])/'wheels')+':/opt/public-wheels:ro'],wheel_hashes={n:v['sha256'] for n,v in x['artifacts'].items()},setup_module_sha256=base.sha(pathlib.Path(__file__)),public_RDF_cache_manifest_sha256=base.sha(R/'public-sparql-dependency-cache.json'),software_scope='genericuv0.9.5/CP3137/pytest8.4.1/plugin0.3.5/rdflib7.1.4/pyparsing3.2.5;no targets/testanswers');return result
source=(R/'cached_grader_setup.py').read_text();old='-w pytest-json-ctrf==0.3.5 pytest --version';assert source.count(old)==1;source=source.replace(old,'-w pytest-json-ctrf==0.3.5 -w rdflib==7.1.4 pytest --version');private=module('sparql_generic_preload',source,{'__file__':str(R/'cached_grader_setup.py')});private.inputs=inputs;prepare=private.prepare;grade_argv=private.grade_argv;ENV=private.ENV
