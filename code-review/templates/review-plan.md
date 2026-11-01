# Review plan — <change title or PR number>

<!-- For large and oversized changes only. A change that needs a plan needs a
     split; the plan exists to make the split explicit and to stop a reviewer
     from pretending one pass covered it. Delete guidance comments before use. -->

## 1. What the change claims to do

<One paragraph. Link the issue, spec, ADR, or PR description that states the intent.
 If no artifact states it, ask the author for one before reviewing the diff.>

## 2. Shape of the diff

| Item | Value | Source |
|---|---|---|
| Files changed | <n> | `python3 scripts/review_scope.py --base <base> --head <head> --markdown` |
| Effective lines | <n> | same |
| Generated / lockfile lines | <n> | same |
| Attention tier | <small / standard / large / oversized> | same |
| Risk-bearing paths | <auth, migration, dependency, CI, public contract…> | same |
| Source without a matched test | <paths or none> | same |

## 3. Split into reviewable units

<!-- Each unit is something a reviewer can hold in working memory in one sitting
     (roughly 200-400 effective lines). Cut along behavior boundaries, not file
     boundaries: "the new endpoint", "the migration and its backfill", "the
     config change". -->

| # | Unit | Paths | Effective lines | Review order | Why this order |
|---|---|---|---|---|---|
| 1 | <unit> | <paths> | <n> | 1 | <risk first, or prerequisite for the next unit> |
| 2 | <unit> | <paths> | <n> | 2 | <...> |

## 4. Evidence to demand before reading

<!-- Ask for these up front; reviewing without them is guessing. -->

- [ ] The command that proves the change works, and its output (<command> → <result>)
- [ ] A test that fails before the change and passes after, for the main behavior
- [ ] For a migration: forward and rollback evidence, plus a dry run on representative data
- [ ] For a contract change: the consumer list and their compatibility evidence
- [ ] For a dependency change: why this version, and what it pulls in
- [ ] For an AI-assisted change: which parts a human wrote, and how the tests were validated independently

## 5. Session plan

| Session | Unit(s) | Timebox | Focus | Stop condition |
|---|---|---|---|---|
| 1 | <unit 1> | <25 min> | <correctness of the main path> | <unit read end-to-end or rescheduled> |
| 2 | <unit 2> | <25 min> | <failure and error paths> | <same> |

Stop when the timebox ends. A longer session does not produce more findings; it
produces the same findings slower and fewer of them.

## 6. Explicitly out of scope

- <Generated code, vendored dependencies, files under a code-owner you are not reviewing…>
- <Behavior that cannot be exercised in this environment — say so in the record>

## 7. Decision this review feeds

- <Merge, promote, incident closure, release gate, architecture approval…>
- <Who else must sign off, and on what evidence — not on your approval.>
