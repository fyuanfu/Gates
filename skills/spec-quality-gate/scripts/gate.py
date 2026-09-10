#!/usr/bin/env python3
"""Prepare read-only text evidence; validate reviews and compute verdicts. Python stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path

STAGES = {'coverage', 'clarity_verifiability', 'consistency', 'confirmation'}
LEVELS = ['P0', 'P1', 'P2', 'P3']

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(value, schema, where='$'):
    """Validate the deliberately bounded keyword subset used by review.schema.json."""
    types = {'object': dict, 'array': list, 'string': str, 'integer': int}
    require(type(value) is types[schema['type']], f'{where}: invalid type')
    if 'enum' in schema:
        require(value in schema['enum'], f'{where}: invalid enum')
    if isinstance(value, str):
        require(len(value.strip()) >= schema.get('minLength', 0), f'{where}: blank string')
    if type(value) is int:
        require(value >= schema.get('minimum', value), f'{where}: below minimum')
    if isinstance(value, dict):
        require(set(schema['required']) <= set(value), f'{where}: missing fields')
        require(set(value) <= set(schema['properties']), f'{where}: unknown fields')
        for key, item in value.items():
            validate(item, schema['properties'][key], f'{where}.{key}')
    if isinstance(value, list):
        require(len(value) >= schema.get('minItems', 0), f'{where}: too few items')
        for i, item in enumerate(value):
            validate(item, schema['items'], f'{where}[{i}]')

def prepare(manifest, out):
    config = read(manifest)
    require(isinstance(config, dict), 'manifest must be object')
    require(set(config) <= {'primary_documents', 'authoritative_references'}, 'unsupported manifest fields')
    require(isinstance(config.get('primary_documents'), list) and config['primary_documents'], 'primary documents required')
    documents = []
    for key, role in [('primary_documents', 'primary'), ('authoritative_references', 'authoritative')]:
        require(isinstance(config.get(key, []), list), f'{key}: list required')
        for name in config.get(key, []):
            require(isinstance(name, str) and name.strip(), 'document path required')
            path = (Path(manifest).resolve().parent / name).resolve()
            require(path.suffix.lower() in {'.md', '.txt'}, f'unsupported format: {path}')
            raw = path.read_bytes()
            content = raw.decode('utf-8')
            require(content.strip(), f'empty document: {path}')
            documents.append({'path': str(path), 'role': role, 'sha256': hashlib.sha256(raw).hexdigest(), 'lines': content.splitlines()})
    require(len({d['path'] for d in documents}) == len(documents), 'duplicate input documents')
    packet = {'documents': documents}
    write(out / 'packet.json', packet)
    return packet

def finalize(out, review_path):
    packet = read(out / 'packet.json')
    review = read(review_path)
    validate(review, read(Path(__file__).resolve().parents[1] / 'assets/review.schema.json'))
    docs = {d['path']: d for d in packet['documents']}
    for path, doc in docs.items():
        require(hashlib.sha256(Path(path).read_bytes()).hexdigest() == doc['sha256'], f'input changed: {path}')
    require(set(review['documents_reviewed']) == set(docs) and len(review['documents_reviewed']) == len(docs), 'document coverage incomplete')
    require(set(review['stages_completed']) == STAGES and len(review['stages_completed']) == len(STAGES), 'review stages incomplete')
    require(len({f['id'] for f in review['findings']}) == len(review['findings']), 'duplicate finding IDs')
    require(len({f['id'] for f in review['inventory']}) == len(review['inventory']), 'duplicate inventory IDs')
    def location(e):
        require(e['path'] in docs, 'unauthorized evidence path')
        lines = docs[e['path']]['lines']
        require(e['line'] <= len(lines), 'evidence line out of range')
        if 'quote' in e:
            require(e['quote'] in lines[e['line'] - 1], 'evidence quote does not match source')
    for item in review['inventory']:
        location(item['source'])
    for f in review['findings']:
        for e in f['evidence'] + f['counter_evidence']:
            location(e)
        require({s['path'] for s in f['search_log']} == set(docs), 'counter-evidence search coverage incomplete')
        if f['type'] == 'INCONSISTENT':
            require(len({(e['path'], e['line'], e['quote']) for e in f['evidence']}) >= 2, 'conflict requires two evidence excerpts')
    confirmed = [f for f in review['findings'] if f['confirmation_status'] == 'confirmed']
    pending = [f for f in review['findings'] if f['confirmation_status'] == 'pending']
    blocking = [f['id'] for f in confirmed if f['severity'] in LEVELS[:2]]
    unresolved = [f['id'] for f in pending if f['severity'] in LEVELS[:2]]
    status = 'review_failed' if blocking else 'review_inconclusive' if unresolved else 'review_passed'
    result = {'status': status, 'highest_severity': next((p for p in LEVELS if any(f['severity'] == p for f in confirmed)), None), 'counts': {p: sum(f['severity'] == p for f in confirmed) for p in LEVELS}, 'pending_counts': {p: sum(f['severity'] == p for f in pending) for p in LEVELS}, 'blocking_finding_ids': blocking, 'pending_high_finding_ids': unresolved, 'documents_reviewed': len(docs)}
    write(out / 'findings.json', review['findings'])
    report = ['# 需求质量评审', '', '状态：' + status, '', '通过仅表示本次完整评审未发现已确认 P0/P1；不代表整体开发就绪。', '']
    for f in review['findings']:
        report += [f"## {f['id']} · {f['severity']} · {f['confirmation_status']} · {f['type']}", '', f['claim'], '', '影响：' + f['impact'], '', '待决问题：' + f['question'], '', '确认依据：' + f['resolution_reason'], '']
        for e in f['evidence']:
            report += [f"- {e['path']}:{e['line']} — {e['quote']}"]
        report += ['', '反证检索：' + json.dumps(f['search_log'], ensure_ascii=False), '反证：' + json.dumps(f['counter_evidence'], ensure_ascii=False), '']
    (out / 'gate-report.md').write_text('\n'.join(report), encoding='utf-8')
    # Publish verdict last, after successful report generation.
    write(out / 'gate-result.json', result)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'finalize'])
    parser.add_argument('first')
    parser.add_argument('second')
    args = parser.parse_args()
    out = Path(args.second if args.command == 'prepare' else args.first)
    owns_run = False
    try:
        if args.command == 'prepare':
            out.mkdir(parents=True, exist_ok=False)
            owns_run = True
            prepare(args.first, out)
            print(json.dumps({'status': 'prepared', 'packet': str(out / 'packet.json')}))
        else:
            require(out.is_dir(), 'run directory missing')
            require(not (out / 'gate-result.json').exists(), 'run already finalized; create a new run')
            owns_run = True
            print(json.dumps(finalize(out, args.second), ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'status': 'execution_error', 'error': str(exc)}
        # Never replace a previously completed run or arbitrary existing directory.
        if owns_run and out.is_dir() and not (out / 'gate-result.json').exists():
            write(out / 'gate-result.json', result)
        print(json.dumps(result, ensure_ascii=False))
        return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
