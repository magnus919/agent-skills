# Failure-Mode-to-Skill Index

Use this index when the work is blocked by a recognizable failure pattern rather than a named technology. Load the most specific skill first.

| Failure mode | Signals | Load |
|---|---|---|
| The premise may be wrong | A plausible explanation has not been checked against source or live output | [systematic-debugging](systematic-debugging/SKILL.md) |
| A tool or API may be missing | You are about to build a workaround without checking the native capability | [agent-skills](agent-skills/SKILL.md), then the domain skill |
| Work keeps escalating | Two materially different approaches failed | [systematic-debugging](systematic-debugging/SKILL.md) |
| A multi-agent decision is converging too early | One perspective appears sufficient but alternatives have not been tested | [agent-council](agent-council/SKILL.md) |
| A contribution may duplicate existing work | The requested feature sounds like something already in the repository | [opensource-contributions](opensource-contributions/SKILL.md) |
| A workflow is repeated manually | The same sequence of skills is executed more than once | [workflow-architect](bundles/workflow-architect/SKILL.md) |

This is a routing aid, not a replacement for reading the selected skill. Add a row only when the failure mode has a concrete trigger and an existing skill that addresses it.
