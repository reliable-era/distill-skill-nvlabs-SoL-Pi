"""Separatenewdependency-closedpreloader;originalfailedhelperunchanged."""
import pathlib
from prospective_output_budget import module
R=pathlib.Path(__file__).resolve().parent
source=(R/'fasttext_grader_setup.py').read_text();assert source.count("R/'fasttext-public-grader-cache.json'")==2;source=source.replace("R/'fasttext-public-grader-cache.json'","R/'fasttext-public-grader-cache-r2.json'");private=module('fasttext_public_inputs_closed',source,{'__file__':str(__file__)});inputs=private.inputs;prepare=private.prepare;grade_argv=private.grade_argv;ENV=private.ENV
