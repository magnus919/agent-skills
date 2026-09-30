# YouTube thumbnail — make the promise clear before the click

## Why Install This Skill

A thumbnail has a split second to tell the right person, “this is for me.” Generic advice like “add a shocked face” or “use three words” can flatten a real video into clickbait. This skill helps your agent find the actual promise in the video, develop distinct visual directions, pair each one with the title, and pressure-test the result at the sizes people really see.

It also gives your agent a repeatable way to learn after publishing. The workflow favors YouTube's native experiments and watch-time outcomes over unsupported CTR promises, and it flags when the data cannot support a conclusion.

## What You Get

| File | Purpose |
|---|---|
| `SKILL.md` | End-to-end thumbnail concept, creation, review, and measurement workflow |
| `references/design-principles.md` | Research-informed concepting, references, visual hierarchy, and image direction |
| `references/platform-and-policy.md` | Current YouTube specs, integrity boundaries, and preflight use |
| `references/testing-and-measurement.md` | Native Test & Compare, analytics context, and interpretation limits |
| `templates/thumbnail-brief.md` | Reusable video promise, reference board, and three-concept brief |
| `templates/experiment-log.md` | Variant hypotheses, test setup, results, and caveats |
| `scripts/thumbnail_preflight.py` | Image-spec checks and small/device-size proof images |
| `scripts/test_thumbnail_preflight.py` | Offline tests for the preflight script |
| `requirements.txt` | Pillow dependency for image inspection and proof generation |
| `evals/evals.json` | Representative quality cases for the skill |
| `evals/trigger-queries.json` | Harness-specific positive and near-miss routing probes |

## Quick Start

From this directory, install the one script dependency in an isolated environment and inspect an export:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/thumbnail_preflight.py ~/Videos/thumbnail.jpg \
  --profile video --upload-device desktop --proof-dir ~/Videos/thumbnail-proofs
```

The command prints a JSON report and writes 426×240, 160×90, and upper-half-stress-test previews into the proof directory. Inspect those images visually; the script cannot judge meaning, truthfulness, or design quality.

## Triggers

- Develop or critique a YouTube thumbnail or preview card.
- Pair a title and thumbnail so they tell one accurate story together.
- Create visual concepts or image-generation direction for a specific video.
- Check a candidate at small size or against current YouTube export requirements.
- Plan a native thumbnail experiment or diagnose its results.

## Requirements

The skill guidance itself needs no external service. The optional preflight script requires Python 3.9+ and Pillow; install it with the command above. Checking current YouTube upload and testing eligibility requires access to YouTube's official help pages and, for channel-specific analysis, YouTube Studio Analytics. No paid thumbnail tool or image-generation provider is required.
