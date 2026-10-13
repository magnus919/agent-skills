"""Verify public Jev study artifacts offline; no provider or network access."""
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ndcg(grades, order):
    def dcg(values):
        return sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(values[:5]))
    ideal = dcg(sorted(grades, reverse=True))
    return dcg([grades[i] for i in order]) / ideal if ideal else None


def verify():
    manifest = read('evidence-manifest.json')
    for name, expected in manifest['sha256'].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, 'hash mismatch: ' + name)
    freeze = read('freeze.json')
    require(hashlib.sha256((ROOT / 'experiment.py.txt').read_bytes()).hexdigest() == freeze['code_sha256'], 'final source pin mismatch')
    for name, registration in [('experiment-development-v1.py.txt', 'development-registration.json'),
                               ('experiment-development-v2.py.txt', 'development-registration-v2.json')]:
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == read(registration)['code_sha256'], 'pilot source pin mismatch')
    cases = {c['id']: c for c in read('cases-public.json')}
    final = {qid for qid, c in cases.items() if c['split'] == 'final'}
    require(final == set(freeze['final_ids']) and len(final) == 83, 'assigned final roster mismatch')
    require(sum(c['split'] == 'development' for c in cases.values()) == 12, 'development roster mismatch')
    require(sum(c['split'] == 'terminal-v1' for c in cases.values()) == 1, 'terminal case missing')
    rows = [json.loads(s) for s in (ROOT / 'outcomes-final-v2.jsonl').read_text().splitlines()]
    require(len(rows) == 332, 'final outcome count mismatch')
    require({(r['id'], r['arm']) for r in rows} == {(qid, arm) for qid in final for arm in ['S','P','B','C']}, 'outcome roster mismatch')
    analysis = read('analysis-final.json')
    for arm in ['S','P','B','C']:
        outcomes = [r for r in rows if r['arm'] == arm]
        values = []
        for r in outcomes:
            require(sorted(r['order']) == list(range(8)), 'invalid rank permutation')
            expected = ndcg([p['grade'] for p in cases[r['id']]['passages']], r['order'])
            require(expected == r['ndcg5'] or expected is not None and abs(expected - r['ndcg5']) < 1e-12, 'nDCG replay mismatch')
            if expected is not None:
                values.append(expected)
            if arm != 'S':
                require(len(r['edges']) == {'P':28,'B':8,'C':7}[arm], 'graph edge count mismatch')
                require(len({tuple(sorted((i,j))) for i,j,y in r['edges']}) == len(r['edges']), 'duplicate edge')
                reached = {0}
                for _ in range(8):
                    for i,j,y in r['edges']:
                        require(0 <= i < 8 and 0 <= j < 8 and i != j and y in [0., .5, 1.], 'invalid edge')
                        if i in reached or j in reached:
                            reached.update([i,j])
                require(len(reached) == 8, 'disconnected observed graph')
            else:
                require(all(0 <= score <= 3 for score in r['scores']), 'Score range mismatch')
        require(len(values) == 77, 'defined nDCG denominator mismatch')
        require(abs(sum(values) / len(values) - analysis['arms'][arm]['ndcg5']) < 1e-12, 'aggregate metric mismatch')
        require(sum(r['input_tokens'] for r in outcomes) == analysis['arms'][arm]['input_tokens'], 'arm token mismatch')
    diagnostics = [json.loads(s) for s in (ROOT / 'outcomes-final-v2-diagnostics.jsonl').read_text().splitlines()]
    require(len(diagnostics) == 80, 'diagnostic count mismatch')
    require({(r['id'],r['arm'],r['variant']) for r in diagnostics} ==
            {(qid,arm,v) for qid in freeze['diagnostic_ids'] for arm in ['S','P','B','C'] for v in ['repeat','reverse']}, 'diagnostic roster mismatch')
    ledger = json.loads(gzip.decompress((ROOT / 'response-ledger-public.json.gz').read_bytes()))
    require(len(ledger) == 6242, 'paid attempt count mismatch')
    require(len({(r['phase'],r['id']) for r in ledger}) == len(ledger), 'duplicate paid receipt')
    require(sum(bool(r.get('error') or r.get('validation_error')) for r in ledger) == 1, 'terminal failure history mismatch')
    for r in ledger:
        require('payload' not in r and 'state' not in r, 'public request state unexpectedly retained')
        require(r['response']['model'] == freeze['model'], 'model drift')
        require(r['status'] == 200, 'HTTP failure')
        answers = r['response']['answers']
        require(len(answers) == 1, 'answer count mismatch')
        a = next(iter(answers.values()))
        probs = a['probabilities']
        require(all(math.isfinite(v) and 0 <= v <= 1 for v in probs.values()), 'invalid probability')
        # Old failure is preserved under its original stricter contract.
        if r.get('validation_error'):
            require(r['phase'] == 'calls-development' and r['validation_error'] == 'score expectation mismatch', 'unexpected failure')
        else:
            require(abs(sum(probs.values()) - 1) <= .005 * len(probs) + 1e-8, 'probability sum outside registered precision')
    cost = read('cost-ledger.json')
    tokens = sum(r['response']['usage']['input_tokens'] for r in ledger)
    require(tokens == cost['total_input_tokens'] == 3291912, 'total token mismatch')
    require(abs(tokens * .042 / 1_000_000 - cost['estimated_total_usd']) < 1e-12, 'published-rate estimate mismatch')
    require(cost['estimated_total_usd'] <= freeze['budget']['total_usd'] and len(ledger) <= freeze['budget']['total_attempts'], 'budget exceeded')
    challenges = read('challenge-results.json')
    require(len(challenges) == 12 and len({r['id'] for r in challenges}) == 12, 'challenge roster mismatch')
    print('Verified file/source pins, 83-query final roster, 77 defined nDCG units, 80 diagnostic outcomes, 12 challenge groups, 6242 paid receipts and token accounting.')
    print('Decision remains no default adoption; verification does not establish human-label correctness, calibration or skill behavioral uplift.')


if __name__ == '__main__':
    verify()
