# Independent UI oracle experiment

This controlled experiment supports the QA reference; it is not a vendor
benchmark. All accounts and effects are synthetic. No keys, private data or
production systems were used. Research and implementation were AI-assisted.

## Reproduce the offline matrix

```sh
python3 docs/experiments/agent-ui/synthetic_matrix.py --output /tmp/ui-results.json
python3 -m pytest docs/experiments/agent-ui/test_synthetic_matrix.py docs/experiments/agent-ui/test_live_fixture.py -q -o addopts=''
```

`results.json` retains 280 trial records (7 conditions × 4 policies × 10
repeats), source hash, store snapshots, independent checks, coverage and elapsed
SQLite time. The weak policy deliberately trusts presentation. The simulated
agent policy is scripted, with no live inference. Fixed and simulated navigation
use identical actions and exact oracles; their agreement is expected, not a
model-quality finding. Stale replay injects a changed build/wrong target effect;
the qualified replay policy blocks before mutation. Clean controls pass all paths.

| Policy | Faulty trials | False greens | Functional detections | Safe blocks |
|---|---:|---:|---:|---:|
| Banner only | 60 | 60 | 0 | 0 |
| Fixed exact | 60 | 0 | 60 | 0 |
| Simulated agent + exact | 60 | 0 | 60 | 0 |
| Verified replay policy | 60 | 0 | 40 | 20 |

No repeated outcome disagreement or clean false blocks occurred. This is a
policy ablation: expected by construction and checked against real SQLite
writes. It neither estimates flake in a real app nor establishes statistical
agent accuracy. Timings in the JSON are measured local policy time, not browser
or inference latency. Model calls are zero; billed model cost is unknown rather
than an asserted zero. Cache preparation and repair economics are unmeasured.

## Illustrative live observations (2026-10-05)

The current conversational agent used fresh accessibility observations to choose
controls on `live_fixture.py`, a loopback HTML/SQLite app. Seven single trials:
clean plus six fault labels. The retained trials contain six clicks; an earlier
clean attempt was discarded after discovering the favicon-reset bug, then
rerun, so seven clicks occurred across the whole session. Account B was observed
and the agent chose not to click. For the renamed control, the agent selected
Apply order from fresh state and wrote one correct effect. No automated replay,
cache invalidation or executor handoff was run on this live fixture. Persistence loss, duplicate effects and quantity corruption
all showed Saved but failed the independent store oracle. Required-skip injection
was in the offline coverage harness, not the live UI. `live-evidence.json`
retains author-recorded presentation summaries and the separate final store read.
It is an illustrative observation packet, **not independently verified live
performance evidence**: raw browser traces, per-attempt timestamps and a frozen
coverage manifest were not retained. Fixture/query hashes and a record ID
identify what was recorded; they cannot establish the missing action provenance.
The implementing agent recorded the observations; no separate UI verifier
reproduced them. Quantitative detections and false-green rates above apply only
to the reproducible offline matrix.

Start with an unused disposable store:

```sh
python3 docs/experiments/agent-ui/live_fixture.py --store /tmp/ui-live.sqlite
```

Visit the printed-in-docs loopback URL for each named condition, inspect account,
click only the current authorized control, then query SQLite separately. Each
GET of `/` resets that condition; **reload is not a persistence oracle for this
fixture**. Non-root requests are rejected. Stop with Ctrl-C. This fixture owns
only disposable state and has no model client. The first run revealed favicon
requests resetting the clean condition; the fixture was fixed and the clean
control independently rerun before retaining results.

The live slice uses actual current-agent inference for control selection, but
has no isolated model billing/tokens/latency telemetry and only one trial per
condition. Browser tool calls include observation/transport overhead. No live
Jev call or third-party cached-replay executor was tested on this fixture. The
PR workflow intentionally skips model/Jev jobs: they are restricted to main
pushes or explicit main-branch dispatch. The merge triggers the configured live
skill-output evaluation and advisory Jev audit with existing CI credentials.
Those jobs evaluate generated responses, not browser navigation, state
persistence or cached execution. Check the linked workflow run before claiming
execution or coverage: an enabled job is not a completed evaluation. See the
[workflow conditions](../../../.github/workflows/skill-eval.yml) and
[post-merge run](https://github.com/magnus919/agent-skills/actions/runs/37386915894).
No new credentials or provider recommendation are needed for these deliverables.

## Fixture hardening after the initial observations

The current fixture rejects `required_skip` with HTTP 400; required skips are
injected only in the offline report harness. The archived observation packet
records a legacy visit to that label, which behaved like clean and did not
exercise live coverage loss. Its fixture hash and source commit refer to the
historical version, not the hardened server.

The server and SQLite connection now close on Ctrl-C or server-loop exceptions.
Request-time SQLite errors return HTTP 500 with a sanitized diagnostic category,
and a failed transaction rolls back. The UI shows Storage error for a failed
HTTP response and Request failed for a transport rejection. Optimistic Saved
remains intentional for the injected persistence/count/quantity faults, so it
still cannot replace the independent store oracle. Focused tests exercise HTTP
parsing, real SQLite effects, rollback, unsupported cases and shutdown ownership.

## Review and evidence boundaries

The new eval challenges are in `eval-challenges.md`. The QA reference links the
primary research sources with their scope limits. Exact independent oracles,
replay invalidation, bounded repair and coverage reconciliation generalize;
the illustrative counts do not predict another app's detection rate.
