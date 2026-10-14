#!/usr/bin/env python3
"""Run the 29 preregistered B/C nginx-502 reruns (attempt 2) with Pi's own G4 cell runners.

Only admission differs from g4/BC_retry_scheduler.py. By user instruction (2026-10-12), runs
call 127.0.0.1:8000 as a plain client, with no /get_load gating, so the runners'
zero-waiting check is switched off here. Each admission record states this.
Attempt 3 reruns cells whose attempt 2 Codex dropped with "idle timeout waiting for SSE" while
its request was still queued at 8000; it raises only Codex's client-side stream idle timeout
to the 1800 s cell cap (stream_idle_timeout_ms), leaving the hash-checked runner files unchanged.
Attempt 4, same settings, reruns attempt-3 cells killed by an nginx 502 from 8000.
Usage: rerun_BC.py [--slots 8] [--attempt 3|4 --cells CELL ...]
"""
import argparse, concurrent.futures, datetime, json, pathlib, sys, threading

G4 = pathlib.Path(__file__).resolve().parents[1] / 'g4'
sys.path.insert(0, str(G4))
from native import sha
from scheduler_v2 import load_committed
from transport import save
import native, run_swe_cell_v2, run_terminal_cell

COMMIT = '61e14182430f1eeb4a9e63823d41be0cc88b2147'
PLAN, WINDOW = G4 / 'BC-retry-preregistration.json', G4 / 'windows/BC-retry.json'
ROOT = pathlib.Path('/tmp/solpi-g4-BC-retry-8b389db7b117')
run_swe_cell_v2.waiting_zero = run_terminal_cell.waiting_zero = lambda load: True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slots', type=int, default=8)
    ap.add_argument('--attempt', type=int, default=2, choices=(2, 3, 4))
    ap.add_argument('--cells', nargs='*')
    a = ap.parse_args()
    if a.attempt >= 3:
        idle = ['-c', 'model_providers.local.stream_idle_timeout_ms=1800000']
        run_swe_cell_v2.argv = run_terminal_cell.argv = lambda prompt: native.argv(prompt)[:-1] + idle + [prompt]
    plan, w = load_committed(PLAN, COMMIT), load_committed(WINDOW, COMMIT)
    window = dict(w, file=str(WINDOW), commit=COMMIT)
    lookup = {c['cell_id']: c for rows in json.loads((G4 / 'queue-order.json').read_text())['parts'].values() for c in rows}
    cells = [lookup[i] for i in w['cells']]
    assert len(cells) == 29 and all(c['part'] in ('B', 'C') for c in cells)
    if a.cells:
        cells = [c for c in cells if c['cell_id'] in a.cells]
        assert len(cells) == len(a.cells)
    active, lock = set(), threading.Lock()

    def admit(cell, n):
        assert n == a.attempt
        with lock:
            return dict(load=None, admission='no /get_load gating: user instruction 2026-10-12, call 8000 as a plain client',
                        occupied_slots_after_admission=len(active), cell_id=cell['cell_id'], attempt=n,
                        utc=datetime.datetime.now(datetime.timezone.utc).isoformat())

    def run(cell):
        suffix = '' if a.attempt == 2 else f'-a{a.attempt}'
        out = ROOT / (cell['cell_id'] + '-attempts' + suffix + '.json')
        if out.exists():
            return json.loads(out.read_text())[0]
        with lock:
            active.add(cell['cell_id'])
        try:
            fn = run_swe_cell_v2.attempt if cell['part'] == 'C' else run_terminal_cell.attempt
            row = fn(cell, a.attempt, ROOT / (cell['cell_id'] + f'-a{a.attempt}'), plan, window, admit)
            save(out, [row])
        except Exception as e:
            row = dict(cell_id=cell['cell_id'], error=f'{type(e).__name__}: {e}')
            save(ROOT / (cell['cell_id'] + '-execution-error' + suffix + '.json'), row)
        finally:
            with lock:
                active.discard(cell['cell_id'])
        print(json.dumps({k: row.get(k) for k in ('cell_id', 'arm', 'solved', 'timeout', 'native_exit', 'error')}), flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(a.slots) as ex:
        rows = list(ex.map(run, cells))
    print('DONE', len(rows), 'reruns', sum(bool(r.get('solved')) for r in rows), 'solved', flush=True)


if __name__ == '__main__':
    main()
