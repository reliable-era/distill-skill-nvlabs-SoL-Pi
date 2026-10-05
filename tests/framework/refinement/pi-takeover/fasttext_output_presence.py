"""Stopped-modelpresenceONLY;ambiguous/unsupportednotcheapqualityzero."""
import pathlib
from prospective_output_budget import module
R=pathlib.Path(__file__).resolve().parent
source=(R/'sparql_output_presence.py').read_text();assert source.count("PATH='/app/solution.sparql'")==1;source=source.replace("PATH='/app/solution.sparql'","PATH='/app/model.bin'");private=module('fasttext_presence',source,{'__file__':str(__file__)});stopped_output_present=private.stopped_output_present
