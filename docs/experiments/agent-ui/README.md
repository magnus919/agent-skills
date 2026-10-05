# Independent UI oracle experiment

This controlled experiment supports the QA reference; it is not a vendor
benchmark. All accounts and effects are synthetic. No keys, private data or
production systems were used. Research and implementation were AI-assisted.

## Reproduce the offline matrix

```sh
python3 docs/experiments/agent-ui/synthetic_matrix.py --output /tmp/ui-results.json
python3 -m pytest docs/experiments/agent-ui/test_synthetic_matrix.py -q -o addopts=''
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

## Live browser slice (2026-10-05)

The current conversational agent used fresh accessibility observations to choose
controls on `live_fixture.py`, a loopback HTML/SQLite app. Seven single trials:
clean plus six fault labels. Six clicks total; wrong account was blocked before
a click. The renamed control took one live repair proposal/action, which wrote
one correct effect. Persistence loss, duplicate effects and quantity corruption
all showed Saved but failed the independent store oracle. Required-skip injection
was in the offline coverage harness, not the live UI. `live-evidence.json`
retains observed presentation and the separate final store read.

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
Jev call or third-party cached-replay executor was tested; repository CI model
and advisory Jev jobs are separate evidence, not substitutes for this slice.
No new credentials or provider recommendation are needed for these deliverables.

## Review and evidence boundaries

The new eval challenges are in `eval-challenges.md`. The QA reference links the
primary research sources with their scope limits. Exact independent oracles,
replay invalidation, bounded repair and coverage reconciliation generalize;
the illustrative counts do not predict another app's detection rate.
