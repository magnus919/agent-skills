# Exploratory Testing Charter

> Fill in for each SBTM session. One charter per session. See [exploratory-testing.md](../references/exploratory-testing.md) for charter quality guidance and oracle heuristics.

## Charter

**Explore** <target area / feature / component>
**with** <resources, constraints, or test conditions>
**to discover** <information or risks sought>.

## Session Setup

| Field | Value |
|-------|-------|
| Tester(s) | <name(s)> |
| Date | <YYYY-MM-DD> |
| Timebox | <60 / 90 / 120> minutes |
| Environment | <local / staging / specific config> |
| Test Data / Tools | <specific data sets, proxies, throttling, accounts> |

## Charter Quality Checklist

Before starting, confirm:

- [ ] Target is specific (not "the app")
- [ ] Resources or constraints are named (test data, tools, conditions)
- [ ] Information goal is stated (not just "find bugs")
- [ ] Scope fits within the timebox

## Heuristics Applied

Select oracles and coverage heuristics to guide exploration (see [exploratory-testing.md](../references/exploratory-testing.md)):

- [ ] SFDIPOT coverage (Structure, Function, Data, Interfaces, Platform, Operations, Time)
- [ ] HICCUPPS oracle (History, Image, Comparable, Claims, Users, Product, Purpose, Standards)
- [ ] Tours (e.g., Guidebook, Money, Supermodel, Saboteur, Back-Alley)
- [ ] Other: <specify>

## Notes

<Record observations, questions, areas explored, anomalies, and hunches during the session. Append chronologically.>

-

## T/B/B Metrics

Track time allocation at session end:

| Metric | Minutes | Percentage |
|--------|--------:|-----------:|
| **T** — Test time (designing + executing) | | ___% |
| **B** — Bug investigation | | ___% |
| **B** — Setup / Interruption | | ___% |
| **Total** | | 100% |

> Target: T ≥ 70%, Setup ≤ 10%. If T < 60%, fix environmental blockers before scheduling more sessions.

## Debrief

### What did you test?

<Areas covered, charters fulfilled, techniques used.>

### What did you find?

<Bugs filed (IDs), risks identified, questions raised.>

| Finding | Type (Bug / Risk / Question) | Severity / Priority | Bug ID |
|---------|------------------------------|---------------------|--------|
| <description> | | | |
| <description> | | | |

### What is left untested?

<Scope not reached, new areas discovered, follow-up needed.>

### Follow-Up Actions

- [ ] <New charter needed: ___>
- [ ] <Automation candidate: ___>
- [ ] <Risk register update: ___>
- [ ] <Spec clarification needed: ___>
- [ ] <Other: ___>
