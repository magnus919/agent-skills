#!/usr/bin/env python3
"""Check local discovery records. This does not validate camera behavior."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-dir', type=Path, help='Optional private manufacturer captures directory')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = []
    for path in root.rglob('*.json'):
        try:
            json.loads(path.read_text())
        except (ValueError, OSError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
    index = json.loads((root / 'manufacturer-model-index.json').read_text())['manufacturers']
    status = json.loads((root / 'manufacturer-audit-status.json').read_text())['manufacturers']
    sources = json.loads((root / 'manufacturer-source-captures.json').read_text())['sources']
    expected = {p.stem.removeprefix('manufacturer-') for p in (root / 'references').glob('manufacturer-*.md')}
    if len(expected) != 43:
        errors.append('expected 43 manufacturer/brand-family references')
    if set(index) != expected or {r['id'] for r in status} != expected:
        errors.append('manufacturer index, status and reference roster differ')
    page_count = row_count = 0
    for maker, record in index.items():
        if not record['completeness_finding'] or not record['project_finding']:
            errors.append(f'{maker}: missing audit finding')
        rows = {k: [] for k in ('official', 'gphoto', 'libraw')}
        for name in record['model_ledger_pages']:
            page_count += 1
            path = root / name
            if not path.exists():
                errors.append(f'missing {name}')
                continue
            page = json.loads(path.read_text())
            if page['manufacturer'] != maker:
                errors.append(f'{name}: manufacturer mismatch')
            rows[page['evidence_kind']].extend(page['rows'])
            if len(path.read_text()) > 60000:
                errors.append(f'{name}: exceeds 60000 characters')
        for kind, values in rows.items():
            row_count += len(values)
            if len(values) != record[f'{kind}_source_rows']:
                errors.append(f'{maker}/{kind}: count mismatch')
            for row in values:
                if not row.get('name'):
                    errors.append(f'{maker}/{kind}: empty name')
                if kind == 'official' and (row['source'] not in sources or not row['url'].startswith('https://')):
                    errors.append(f'{maker}: missing official provenance')
        if len({r['name'] for r in rows['official']}) != record['distinct_official_labels']:
            errors.append(f'{maker}: distinct vendor-label count mismatch')
        for name in record['inventory_references']:
            if not (root / name).exists():
                errors.append(f'missing {name}')
        for key in record['source_keys']:
            if key not in sources:
                errors.append(f'{maker}: unknown source {key}')
    reference_sizes = [len(p.read_text()) for p in (root / 'references').glob('*') if p.is_file()]
    if max(reference_sizes, default=0) > 60000:
        errors.append('oversized reference')
    links_checked = 0
    for path in root.rglob('*.md'):
        for target in re.findall(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)', path.read_text()):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            links_checked += 1
            if not (path.parent / target.split('#')[0]).exists():
                errors.append(f'{path.relative_to(root)}: missing link {target}')
    family = json.loads((root / 'family-coverage.json').read_text())
    family_counts = {}
    for maker in ('fujifilm', 'ricoh'):
        models = family[maker]['models']
        family_counts[maker] = len(models)
        if len({r['model'] for r in models}) != len(models):
            errors.append(f'{maker}: duplicate family identity')
        for row in models:
            if not (root / row['reference']).exists():
                errors.append(f'{maker}: missing family reference')
    hashes = 0
    if args.capture_dir:
        for key, source in sources.items():
            if source['status'] != 'retrieved':
                continue
            path = args.capture_dir / (key + '.html')
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
                errors.append(f'{key}: captured body missing or digest mismatch')
            else:
                hashes += 1
    print(json.dumps({'status': 'fail' if errors else 'pass', 'manufacturers': len(index),
                      'model_ledger_pages': page_count, 'source_rows': row_count,
                      'family_identities': family_counts, 'local_links_checked': links_checked,
                      'largest_reference_characters': max(reference_sizes, default=0),
                      'private_capture_hashes_checked': hashes if args.capture_dir else 'not_assessed',
                      'camera_behavior': 'not_assessed', 'errors': errors}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
