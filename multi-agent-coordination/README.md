# Multi-agent coordination

Make several agents deliver one coherent result.

## Why Install This Skill

Agent teams can generate plenty of activity while losing ownership, repeating
work or drifting away from the original request. This skill helps you decide
when collaboration pays off, divide work cleanly and verify the combined result.

Your agent gains a practical method for coordinating persistent teams across
harnesses, recovering interrupted work and correcting bad shared practices.
Research and lessons from OpenRig, HERDR and Block/Buzz inform the guidance,
with explicit limits on what has actually been demonstrated.

## What You Get

| Contents | Provides |
|---|---|
| `SKILL.md` | A complete coordination workflow and specialist handoffs |
| `references/` | Topology, ownership, communication, recovery, diagnosis, evaluation and source-linked research |
| `templates/` | Team charter, assignment, handoff, decision packet, experiment, recovery and knowledge correction |
| `scripts/coordination.py` | Offline snapshot audit and knowledge-exposure tracing |
| `scripts/test_coordination.py` | Adverse-input and coordination-failure tests |
| `evals/` | Representative quality cases and validation boundaries |

## Quick Start

From the installed skill directory:

```sh
python3 scripts/coordination.py audit --file templates/team-snapshot.json --json
```

The example returns `"findings": []` and `"runtime_acceptance": "not_assessed"`.
Copy the team charter for your project and adapt the snapshot to inspect ownership,
stale intent and blocked work. The helper never launches agents or changes a fleet.

## Triggers

- Designing a team that spans multiple agent sessions or harnesses.
- Choosing between sequential work, delegation and peer collaboration.
- Diagnosing lost handoffs, scope drift, endless checking or shared-memory errors.
- Comparing coordination mechanisms from emerging tools.

## Requirements

No framework, service account or API key is required. The optional helper and
its tests use Python 3.10+ and the standard library. Operating a real team
requires a host with the necessary authorized capabilities.
