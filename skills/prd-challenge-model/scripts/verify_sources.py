#!/usr/bin/env python3
"""Verify RGQ source hashes and literal evidence against authorized input files."""
import argparse
import hashlib
import json
from pathlib import Path

TEXT_EXTENSIONS = {'.md', '.txt', '.json', '.yaml', '.yml', '.html'}


def normalize(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


def verify(review, authorized_paths):
    allowed = {Path(p).resolve() for p in authorized_paths}
    errors = []
    texts = {}
    artifacts = {a['id']: a for a in review['artifacts']}
    requirements = {r['id']: r for r in review['requirements']}
    for aid, a in artifacts.items():
        path = Path(a['path']).resolve()
        if path not in allowed:
            errors.append(f'{aid}: path not in authorized input list')
            continue
        if a['parse_status'] != 'PARSED':
            if a['required']:
                errors.append(f'{aid}: required source not parsed')
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            errors.append(f'{aid}: cannot read source: {exc}')
            continue
        if hashlib.sha256(raw).hexdigest() != a['content_sha256']:
            errors.append(f'{aid}: source SHA-256 mismatch')
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            errors.append(f'{aid}: literal verification unavailable for this format')
            continue
        try:
            texts[aid] = normalize(raw.decode('utf-8-sig'))
        except UnicodeError:
            errors.append(f'{aid}: source is not UTF-8 text')
    represented = {Path(a['path']).resolve() for a in artifacts.values()}
    for path in sorted(allowed - represented):
        errors.append(f'Authorized source missing from Artifact Index: {path}')
    for rid, r in requirements.items():
        source = texts.get(r['artifact_id'])
        if source is None or not r['text'].strip() or normalize(r['text']) not in source:
            errors.append(f'{rid}: requirement text not verified in original source')
    for collection in ('findings', 'observations'):
        for item in review[collection]:
            for index, e in enumerate(item['evidence']):
                label = f"{item['id']}.evidence[{index}]"
                a = artifacts.get(e['artifact_id'])
                source = texts.get(e['artifact_id'])
                quote = normalize(e['quote'])
                if a is None or Path(e['source_path']).resolve() != Path(a['path']).resolve():
                    errors.append(f'{label}: source path or ID mismatch')
                if source is None or not quote.strip() or quote not in source:
                    errors.append(f'{label}: quote not found verbatim in original source')
                if e['requirement_id'] is not None:
                    r = requirements.get(e['requirement_id'])
                    if r is None or r['artifact_id'] != e['artifact_id']:
                        errors.append(f'{label}: requirement anchor mismatch')
                    elif quote not in normalize(r['text']):
                        errors.append(f'{label}: quote not within anchored requirement text')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review', type=Path)
    parser.add_argument('--source', action='append', required=True,
                        help='Authorized invocation artifact path; repeat for every artifact')
    args = parser.parse_args()
    try:
        review = json.loads(args.review.read_text(encoding='utf-8'))
        errors = verify(review, args.source)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors = [f'Unable to verify source evidence: {exc}']
    print(json.dumps({'passed': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
