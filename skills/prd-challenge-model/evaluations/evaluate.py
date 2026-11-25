#!/usr/bin/env python3
"""Prepare blind review inputs and score human-adjudicated root matches."""
import argparse
import json
from pathlib import Path


def ratio(a, b):
    return a / b if b else None


def score(cases, runs):
    by_id = {c['id']: c for c in cases}
    results = {r['case_id']: r for r in runs}
    if len(results) != len(runs) or set(results) - set(by_id):
        raise ValueError('Duplicate or unknown case IDs')
    tp = fp = fn = duplicate = blocked_total = blocked_missed = blocking_fp = 0
    incomplete = 0
    for cid, case in by_id.items():
        expected = {d['id']: d for d in case['expected']}
        run = results.get(cid, {'completed': False, 'findings': []})
        if not run['completed']:
            incomplete += 1
        found = set()
        ids = set()
        for f in run['findings']:
            if f['id'] in ids or f['severity'] not in {'P0', 'P1', 'P2', 'P3'}:
                raise ValueError(f'{cid}: duplicate finding ID or invalid severity')
            ids.add(f['id'])
            root = f['root_id']
            if root is not None and root not in expected:
                raise ValueError(f'{cid}: unknown reference root {root}')
            if root is not None and root not in found:
                found.add(root)
                tp += 1
            else:
                fp += 1
                duplicate += int(root is not None)
            if f['severity'] in {'P0', 'P1'} and (root is None or expected[root]['severity'] not in {'P0', 'P1'}):
                blocking_fp += 1
        fn += len(set(expected) - found)
        for root, defect in expected.items():
            if defect['severity'] in {'P0', 'P1'}:
                blocked_total += 1
                if not any(f['root_id'] == root and f['severity'] in {'P0', 'P1'} for f in run['findings']):
                    blocked_missed += 1
    return {'case_count': len(cases), 'incomplete_or_missing_cases': incomplete,
            'true_positive_roots': tp, 'false_positive_or_duplicate_findings': fp,
            'missed_roots': fn, 'duplicate_findings': duplicate,
            'precision': ratio(tp, tp + fp), 'recall': ratio(tp, tp + fn),
            'blocking_miss_rate': ratio(blocked_missed, blocked_total),
            'false_blocking_findings': blocking_fp}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases', type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', type=Path)
    group.add_argument('--score', type=Path)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding='utf-8'))['cases']
    if args.prepare:
        args.prepare.mkdir(parents=True, exist_ok=True)
        for c in cases:
            (args.prepare / (c['id'] + '.md')).write_text('# Approved scope\n' + c['scope'] + '\n\n# Requirements\n' + c['prd'] + '\n', encoding='utf-8')
    else:
        runs = json.loads(args.score.read_text(encoding='utf-8'))['runs']
        print(json.dumps(score(cases, runs), indent=2))


if __name__ == '__main__':
    main()
