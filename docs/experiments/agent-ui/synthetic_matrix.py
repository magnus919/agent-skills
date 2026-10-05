"""Offline policy experiment; no browser, model, credentials, or network.

Run: python3 docs/experiments/agent-ui/synthetic_matrix.py --output /tmp/ui-results.json
Python 3.8+, stdlib. Writes only the explicitly selected JSON output.
"""
import argparse
import hashlib
import json
import sqlite3
import time
from pathlib import Path

FAULTS = ('clean', 'persistence_loss', 'wrong_account', 'stale_replay',
          'duplicate_effect', 'weakened_assertion', 'required_skip')
MODES = ('banner_only', 'fixed_exact', 'simulated_agent_exact', 'verified_replay')


def trial(fault, mode):
    """Execute real SQLite effects behind a simulated navigation boundary."""
    start = time.perf_counter()
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE effects(account TEXT, operation TEXT, quantity INT)')
    actual_account = 'B' if fault == 'wrong_account' else 'A'
    build = 'v2' if fault == 'stale_replay' else 'v1'
    before = db.execute('SELECT * FROM effects').fetchall()
    required = ['save', 'read_back']
    observed = ['save'] if fault == 'required_skip' else list(required)
    actions = 0
    reason = None
    if mode == 'verified_replay' and (actual_account != 'A' or build != 'v1'):
        reason = 'identity_mismatch' if actual_account != 'A' else 'build_mismatch'
    else:
        actions = 1
        # The visible Save result is optimistic even if storage loses the write.
        if fault != 'persistence_loss':
            quantity = 2 if fault in ('weakened_assertion', 'stale_replay') else 1
            db.execute('INSERT INTO effects VALUES (?, ?, ?)', (actual_account, 'op-1', quantity))
            if fault == 'duplicate_effect':
                db.execute('INSERT INTO effects VALUES (?, ?, ?)', (actual_account, 'op-1', quantity))
            db.commit()
    # Independent store read, not navigator output or a stale UI cache.
    after = db.execute('SELECT * FROM effects').fetchall()
    exact = after == [('A', 'op-1', 1)]
    coverage = observed == required
    if reason:
        verdict = 'blocked'
    elif mode == 'banner_only':
        verdict = 'passed'  # Deliberately weak comparator.
    else:
        verdict = 'passed' if exact and coverage else 'failed'
    # A stale recording is a contract violation even if its effect looks right.
    contract_ok = exact and coverage and (mode != 'verified_replay' or build == 'v1')
    db.close()
    return dict(fault=fault, mode=mode, verdict=verdict, false_green=verdict == 'passed' and not contract_ok,
                before=before, after=after, expected_ids=required, observed_ids=observed,
                invalidation=reason, actions=actions, exact_oracle=exact, coverage_oracle=coverage,
                model_calls=0, billed_model_cost=None, elapsed_ms=(time.perf_counter()-start)*1000)


def run(repeats=10):
    rows = [trial(fault, mode) for _ in range(repeats) for fault in FAULTS for mode in MODES]
    summary = {}
    for mode in MODES:
        faulty = [r for r in rows if r['mode'] == mode and r['fault'] != 'clean']
        clean = [r for r in rows if r['mode'] == mode and r['fault'] == 'clean']
        summary[mode] = dict(faulty_trials=len(faulty), false_greens=sum(r['false_green'] for r in faulty),
                            functional_failures=sum(r['verdict'] == 'failed' for r in faulty),
                            safe_blocks=sum(r['verdict'] == 'blocked' for r in faulty),
                            clean_false_blocks=sum(r['verdict'] != 'passed' for r in clean),
                            outcome_disagreement=any(len({r['verdict'] for r in rows if r['mode']==mode and r['fault']==f}) > 1 for f in FAULTS))
    return dict(schema_version=1, kind='offline_policy_simulation', repeats=repeats,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                limitations=['No UI executor or live inference', 'Simulated agent uses the same scripted action as fixed navigation',
                             'Elapsed time is SQLite policy time, not browser/model latency', 'Not a vendor comparison or model accuracy estimate'],
                summary=summary, trials=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(), indent=2) + '\n')


if __name__ == '__main__':
    main()
