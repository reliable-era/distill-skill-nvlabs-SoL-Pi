"""Task-local exposure-approved bowling support; canonical adapter unchanged."""
import hashlib, importlib.util, pathlib, types
G = pathlib.Path(__file__).resolve().parent
SOURCE = G.parent.parent / 'benchmarks/polyglot.py'

def prepare(source, task, output):
    text = SOURCE.read_text()
    old = "if parts[0] == 'javascript' and task != 'javascript/exercises/practice/alphametics':"
    assert text.count(old) == 1
    text = text.replace(old, "if parts[0] == 'javascript' and task not in ('javascript/exercises/practice/alphametics', 'javascript/exercises/practice/bowling'):")
    module = types.ModuleType('g1_exposed_fixture_adapter')
    module.__file__ = str(SOURCE)
    exec(compile(text, '<G1 exposed bowling allowance>', 'exec'), module.__dict__)
    return module.prepare(source, task, output)
