# Exploratory Testing

Structured discovery testing through concurrent learning, design, and execution. Load when designing charters for new or changed features, investigating areas with unknown risk, or establishing session-based test management. Not for scripted regression suites (that's [regression-testing.md](./regression-testing.md)) or test design technique selection (that's [test-design-techniques.md](./test-design-techniques.md)).

## When to Explore

| Signal | Rationale |
|--------|-----------|
| New feature with incomplete or evolving requirements | Scripted tests can't be written yet; exploration discovers what to automate |
| Post-incident investigation | Reproduce conditions, find adjacent failure modes |
| Integration of a new third-party dependency | Unknown edge cases, error behaviors not in docs |
| Low test coverage in a high-risk area | Discover what's missing before designing automated tests |
| User-reported "it just feels wrong" | No repro steps; exploration builds a repro |
| Before a major release (time-boxed session) | Catch issues that scripted tests structurally miss |

> **Rule:** Exploration is not "random clicking." It is disciplined, time-boxed, charter-driven investigation with structured reporting.

## Session-Based Test Management (SBTM)

SBTM (Bach & Bach, 2000) provides accountability for exploratory work without destroying its creative advantage.

### Core Structure

| Element | Definition |
|---------|-----------|
| **Charter** | Mission statement defining the session's scope and goal |
| **Timebox** | Fixed duration (typically 60–120 minutes) with no interruptions |
| **Debrief** | Structured review of findings, metrics, and follow-up actions |

### T/B/B Metrics

Track time allocation per session:

| Metric | Definition | Target |
|--------|-----------|--------|
| **T** (Test time) | Time actively testing (designing + executing) | ≥ 70% of session |
| **B** (Bug investigation) | Time investigating issues found during the session | 10–25% |
| **B** (Setup/Interruption) | Time lost to environment issues, questions, context switches | ≤ 10% |

A session with T < 60% indicates environmental problems or scope confusion; fix the blocker before scheduling more sessions.

## Charter Format

```
Explore <target> with <resources/constraints> to discover <information>.
```

### Examples

| Charter | Analysis |
|---------|----------|
| Explore the new search autocomplete with slow network and unicode input to discover rendering and latency edge cases | Target: search autocomplete; Resources: throttled network, unicode; Goal: rendering/latency issues |
| Explore payment refund flow with expired cards and partial amounts to discover error handling gaps | Target: refund flow; Resources: expired test cards; Goal: error handling |
| Explore admin bulk-user-import with CSV files > 10MB to discover timeout and memory behavior | Target: bulk import; Resources: large CSV; Goal: timeout/memory |

### Charter Quality Checklist

- Contains a specific target (not "the app")
- Names resources or constraints (test data, tools, conditions)
- States what information you seek (not "find bugs" — too vague)
- Scope fits within the timebox (one session, one charter)

## Heuristics and Oracles

Oracles tell you when something might be wrong. Heuristics guide where to look. Neither is a checklist; they are thinking tools.

### SFDIPOT (Test Coverage Heuristic)

| Letter | Stands For | Question to Ask |
|--------|-----------|-----------------|
| **S** | Structure | What is this made of? (components, files, APIs) |
| **F** | Function | What does it do? (features, behaviors) |
| **D** | Data | What does it process? (inputs, outputs, formats) |
| **I** | Interfaces | What does it connect to? (APIs, UIs, protocols) |
| **P** | Platform | What does it run on? (OS, browser, hardware) |
| **O** | Operations | Who uses it and how? (workflows, personas) |
| **T** | Time | What happens over time? (concurrency, timeouts, aging) |

### HICCUPPS (Oracle Heuristic)

Sources of expectation when you lack a spec:

| Source | Question |
|--------|----------|
| **H**istory | What did previous versions do? |
| **I**mage | What would a comparable product do? (competitors, category norms) |
| **C**omparable | What do similar features in this product do? |
| **C**laims | What does documentation, marketing, or support say? |
| **U**sers' expectations | What would a reasonable user expect? |
| **P**roduct purpose | Does this serve the product's stated mission? |
| **P**urpose (feature) | Does this serve the feature's stated goal? |
| **S**tandards | Do relevant standards (WCAG, RFC, API conventions) apply? |

### Tours (Exploration Patterns)

| Tour | Approach | Best For |
|------|----------|----------|
| **Guidebook tour** | Follow documented flows (user guide, API docs) | Verifying documentation accuracy |
| **Money tour** | Test the revenue-critical paths (checkout, billing) | Business-critical smoke |
| **Landmark tour** | Visit every major feature surface once | Broad coverage sweep |
| **Garbage collectors tour** | Try every error path (invalid input, cancel, timeout) | Error handling |
| **Bad-neighborhood tour** | Focus on historically buggy areas | Regression-prone zones |
| **Museum tour** | Test legacy/backward-compatible paths | Upgrade safety |
| **Back-alley tour** | Try unadvertised features (admin panels, debug endpoints) | Security, hidden behavior |
| **Obsessive-compulsive tour** | Repeat one action many times (submit, refresh) | Concurrency, rate limits |

## Bug Advocacy

Finding a bug is half the work; getting it fixed is the other half.

### Report Quality

| Element | Requirement |
|---------|-------------|
| Title | One line: what broke + where |
| Repro steps | Numbered, deterministic, minimal |
| Expected vs Actual | State both explicitly |
| Evidence | Screenshot, log excerpt, or recording |
| Impact statement | Who is affected, how often, severity |
| Environment | Exact versions, config, browser/device |

### Advocacy Principles

- **Reproduce before reporting.** A bug you can't reproduce is a hypothesis, not a bug.
- **Isolate the minimal repro.** 15 steps with 12 irrelevant ones gets triaged slower than 3 steps.
- **Separate observation from interpretation.** "Button returns 500" is observation; "the backend is broken" is interpretation.
- **Escalate unresolved P0/P1 bugs** with evidence, not emotion. Link to user impact data.

## Session Debrief Structure

After each session (5–10 minutes):

1. **What did you test?** (areas covered, charters fulfilled)
2. **What did you find?** (bugs filed, risks identified, questions raised)
3. **What is left untested?** (scope not reached, new areas discovered)
4. **Metrics:** T/B/B percentages
5. **Follow-up:** New charters needed? Automation candidates? Blockers?

Record in a session sheet. Aggregate across sessions to build a coverage picture for unscripted areas.

## Exploration → Automation Pipeline

| Session Finding | Next Step |
|----------------|-----------|
| Reproducible bug | Write regression test, file bug (see [regression-testing.md](./regression-testing.md)) |
| Repeated manual check | Automate as a scripted test |
| New risk area discovered | Add to risk register (see [risk-based-testing.md](./risk-based-testing.md)) |
| Spec gap identified | File clarification request; add AC |
| Performance concern | Schedule load test (see [performance-testing.md](./performance-testing.md)) |

## Gotchas

> **Gotcha — Exploration without accountability:** Unlogged "testing" that produces no session sheets, no bugs, and no coverage data is indistinguishable from not testing. SBTM's value is the debrief, not the timebox.

> **Gotcha — Using exploration to avoid automation:** If the same manual checks recur session after session, automate them. Exploration is for discovery; automation is for repetition.

> **Gotcha — Vague charters:** "Explore the app" produces random clicking. Every charter must name a target, resources, and information goal.

## Exit Condition

You are done applying this reference when: (1) charters are written in the "Explore X with Y to discover Z" format, (2) sessions are time-boxed with T/B/B tracking, (3) debriefs produce actionable follow-ups, and (4) repeatable findings are graduated to automation or the risk register.

## Composition Links

- Risk-based prioritization for charter selection: [risk-based-testing.md](./risk-based-testing.md)
- Regression test graduation: [regression-testing.md](./regression-testing.md)
- Test design techniques for structured scenarios: [test-design-techniques.md](./test-design-techniques.md)
- Verification methodology (evidence and verdicts): [verification-methodology](../../verification-methodology/SKILL.md)

---

*Sources: James Bach & Jon Bach, "Session-Based Test Management" (2000, bach.ch/sbtm), Cem Kaner et al. "Lessons Learned in Software Testing" (Wiley, 2002), Elisabeth Hendrickson "Explore It!" (Pragmatic Bookshelf, 2013), Michael Bolton (HICCUPPS oracle heuristics), James Bach (SFDIPOT coverage heuristic).*
