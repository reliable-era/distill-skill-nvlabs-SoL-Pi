"""Freeze a metadata-only sample; never read scores or model outcomes."""
import argparse
import hashlib
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def select(rows, size, seed, strata=('benchmark', 'language'), exclude=(), balance_within=()):
    if size < 1:
        raise ValueError('size must be positive')
    excluded = set(exclude)
    identities = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
            raise ValueError('each task requires a nonempty string id')
        if not isinstance(row.get('benchmark'), str) or not row['benchmark']:
            raise ValueError('each task requires a benchmark')
        # Explicit canonical_id allows overlap across benchmark distributions.
        identity = row.get('canonical_id', row['id'])
        if not isinstance(identity, str) or not identity:
            raise ValueError('canonical_id must be a nonempty string')
        if identity in excluded or row['id'] in excluded:
            continue
        # Pick a stable duplicate representative, independent of input order.
        if identity not in identities or canonical(row) < canonical(identities[identity]):
            identities[identity] = row
    groups = {}
    for identity, row in identities.items():
        key = tuple(str(row.get(field, 'unknown')) for field in strata)
        groups.setdefault(key, []).append((identity, row))
    rank = lambda identity: digest({'seed': seed, 'identity': identity})
    for key, group in groups.items():
        group.sort(key=lambda pair: (rank(pair[0]), pair[0]))
        if balance_within:
            subgroups = {}
            for pair in group:
                subkey=tuple(str(pair[1].get(f,'unknown')) for f in balance_within)
                subgroups.setdefault(subkey,[]).append(pair)
            subkeys=sorted(subgroups,key=lambda k:(rank(list(k)),k))
            groups[key]=[subgroups[k][i] for i in range(max(map(len,subgroups.values())))
                         for k in subkeys if i<len(subgroups[k])]
    keys = sorted(groups, key=lambda key: (rank(list(key)), key))
    chosen = []
    depth = 0
    while len(chosen) < min(size, len(identities)):
        for key in keys:
            if depth < len(groups[key]) and len(chosen) < size:
                chosen.append(groups[key][depth][1])
        depth += 1
    return {
        'schema_version': 1,
        'selection_method': 'sha256-ranked strata round-robin; no outcomes',
        'seed': seed, 'requested_size': size, 'selected_size': len(chosen),
        'eligible_unique_tasks': len(identities), 'strata': list(strata),
        'balance_within': list(balance_within), 'stratum_count': len(groups), 'all_strata_covered': size >= len(groups),
        'exclusions': sorted(excluded),
        'candidate_metadata_sha256': digest(sorted(rows, key=canonical)),
        'selected_tasks': chosen,
        'selection_sha256': digest(chosen),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tasks', type=Path, help='metadata-only task JSONL; no scores/solutions')
    parser.add_argument('--size', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--strata', nargs='+', default=['benchmark', 'language'])
    parser.add_argument('--balance-within', nargs='+', default=[], help='Prioritize breadth within each primary stratum')
    parser.add_argument('--exclude', type=Path, help='JSON list of previously exposed canonical ids')
    parser.add_argument('--source', required=True, help='dataset URL or local provenance identifier')
    parser.add_argument('--revision', required=True, help='pinned dataset revision or sha256')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.tasks.read_text().splitlines() if line.strip()]
    forbidden = {'score', 'solved', 'success', 'outcome', 'result', 'patch', 'solution', 'test_patch'}
    if any(forbidden.intersection(row) for row in rows):
        parser.error('supply metadata only; outcomes and solutions must not influence selection')
    excluded = json.loads(args.exclude.read_text()) if args.exclude else []
    result = select(rows, args.size, args.seed, args.strata, excluded, args.balance_within)
    result['provenance'] = {'source': args.source, 'revision': args.revision,
                            'source_file_sha256': hashlib.sha256(args.tasks.read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # A frozen plan is never silently replaced.
    with args.output.open('x') as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write('\n')


if __name__ == '__main__':
    main()
