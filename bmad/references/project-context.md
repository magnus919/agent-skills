# Project Context: Conservative Repository Rules

Project context is the mechanism by which BMad records rules that code alone cannot
express. The design principle: **persist expensive-to-rediscover truth, not every fact
about the repository.** If an agent can cheaply inspect something from the code,
duplicating it in permanent context creates stale noise.

## What belongs in project context (e.g. AGENTS.md)

- Organization policies that affect how work is done.
- Frozen paths or generated files that must not be edited by hand.
- Branch and security rules.
- Commands with non-obvious prerequisites.
- Conventions that differ from ecosystem defaults.
- Observed pitfalls (things agents get wrong here specifically).
- Cross-component rules and required versions.

## What does not belong

- A stale copy of the repository's directory tree or technology list.
- Anything an agent can reliably discover by reading the code.
- Transient state that will be wrong next week.
- Rules that apply to every repository anywhere (those belong in the harness, not the
  project).

## The workflow intents

| Intent | Purpose |
|---|---|
| **Setup** | Establish the initial project-context block for a repository |
| **Adopt** | Bring an existing repository under project-context discipline without rewriting its history |
| **Refresh** | Update rules when the repository or policy changes |
| **Record** | Add a specific observed pitfall or non-obvious command |
| **Audit** | Review the existing block for staleness, drift, or over-duplication |

## Operating rules

- Preserve human-authored content outside the owned markers; never rewrite the whole
  file.
- Keep the human in the loop for writes. A rule you are about to persist should be
  verifiable against the repository — if you cannot demonstrate it, do not record it.
- Verify commands before recording them as prerequisites. A command with an
  undocumented prerequisite recorded from memory is a liability.
- When a contested design decision surfaces during project-context work, route it back
  to architecture (an ADR or the architecture spine), not into local instructions.
- Mark the block so an audit can tell which lines are project-context-owned and which
  are human-authored.

## Adoption path for an existing repository

1. Inspect what already exists (AGENTS.md, CONTRIBUTING.md, CI, docs).
2. Extract only rules that are expensive to rediscover and not already enforced by CI.
3. Draft the block; show the human; get approval before writing.
4. Record the first observed pitfall when one actually occurs — do not invent pitfalls.
5. Re-audit on a schedule or when the repository changes materially.
