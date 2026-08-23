# Hybrid Adaptation — Shaping for Human + AI-Agent Teams

The source book predates agentic development; its build teams were human designers and
programmers. This reference translates the method to work where builders are AI agents
(or mixed human/agent teams) and the human acts as shaper, bettor, and steering
oversight. The basic truths carry over intact; every specific practice gets re-derived.
Method base: Ryan Singer's *Shape Up* ([basecamp.com/shapeup](https://basecamp.com/shapeup)).

## Who plays which role

Shape Up's division of labor maps cleanly:

| Shape Up role | Hybrid equivalent |
|---|---|
| Shaper | Human (alone, or with an agent as sketchpad — never as decision-maker) |
| Betting table | The human accountable for the budget; optionally a structured debate (council-style) to stress-test competing pitches |
| Building team | One or more delegated agents with a defined verification path |
| QA / edge-case pass | Separate reviewer agent or human review, late in the box |

Shaping stays human because it is judgment: choosing what's worth an appetite and where
the fences go. Agents can draft breadboards or pitch text on request, but a pitch whose
appetite and no-gos were chosen by the same system that wants the work built has lost
the separation that makes betting meaningful. Keep the closed-door, private-sphere
property too: shaping in progress is not broadcast to stakeholders.

## Appetite in budget units

An agent team's appetite is still "how much are we willing to spend," but the unit is
yours to choose. Practical currencies, in increasing precision:

- **Work sessions** — "two agent sessions" (a session = one bounded delegation with its
  own context). Coarse but robust to model-price churn.
- **Wall-clock boxes** — "one working day of supervised run time." Good when latency
  matters (someone must be present to steer).
- **Cost ceilings** — token or dollar caps enforced by the harness. Most literal
  translation of appetite-as-budget, and the only one the machine can hard-stop on.
- **Review-round allowances** — caps on fix/review iterations, spent like money (see
  kill criteria below).

Pick ONE primary currency per bet and state it in the pitch. Mixed-currency appetites
produce disputes at exactly the moment clarity matters — when deciding whether the box
is spent.

## Uninterrupted time means batched steering

The commitment that builders get the whole box uninterrupted survives translation with
a twist: agents don't resent interruptions, but *you* pay for them. Every mid-run
course correction burns your attention and resets the agent's momentum; worse,
human steering injected mid-box tends to inject scope changes without appetite checks —
precisely the behavior fixed-time-variable-scope exists to prevent.

So: batch your oversight. Define checkpoints up front ("demo after the first integrated
slice", "hill-state update at box midpoint") and steer at those points rather than
continuously. Between checkpoints the running work is protected — including from you.
This is the same discipline Basecamp applies with cool-downs and self-serve hill charts:
status should be observable without being requested.

## Verification cost lives inside scope

With human teams, review was someone's job inside the cycle. With agent builders,
verification is often the dominant cost: reviewing generated output takes longer than
generating it, and every fix round re-spends that cost. An appetite that prices only
generation is fiction.

Practical rules:

- Budget the full loop: generation + your review + expected fix rounds. If you cannot
  afford the review, you cannot afford the bet — shrink the slice until you can.
- Prefer slices whose correctness can be checked mechanically (tests, type checks,
  linters, schema validation, rendered-output probes). Mechanical verification scales;
  reading every line does not.
- Treat evidence state as perishable: any push invalidates prior green results, so a
  fix round costs more than it looks. Price remediation rounds into the original
  appetite instead of discovering them later.

## Kill criteria for non-converging loops

The circuit breaker's hybrid form. Agent work fails differently from human work: the
characteristic failure is not slippage but non-convergence — loops that feed on their
own findings. Recorded first-party patterns, each of which ran nine-plus rounds before
being structurally stopped:

1. **Reviewer ping-pong.** Automated reviewer finds issues → fixes spawn new issues →
   re-review finds more. Two sub-signatures: severity stops improving across rounds,
   or fixes introduce regressions of their own (our record includes two regressions born
   of rapid-fire fixes under review pressure).
2. **Findings-driven improvement.** Machine-generated finding feeds produce the next
   finding forever. If each fix summons the next finding, the mechanism — not the work —
   is converging. Change the mechanism (narrow the generator's domain, pin its version,
   raise its threshold) or bound the loop; don't assume round N+1 converges.

Standing kill rules to adopt BEFORE betting:

- **Round cap.** A declared maximum number of fix/review rounds per bet (three is a
  sane default). Reaching the cap ends the loop: ship what's green, document residue,
  and route the remainder back through shaping if it still matters. Never extend the
  cap mid-loop — that is the breaker being softened (see references/anti-patterns.md).
- **Severity gate.** Stop when consecutive rounds stop reducing the highest-severity
  class of finding, regardless of round count.
- **Regression veto.** Any fix round that introduces a new defect of equal-or-worse
  severity than what it fixed counts double against the cap.
- **Fresh-context restart.** When a loop stalls, prefer restarting the slice in a clean
  context over iterating further in the polluted one. Cursor's scaling write-up reports
  the same discovery at fleet scale: periodic fresh starts combat drift better than
  pushing through.

Trip conditions route back to shaping, exactly like a human-team breaker trip: either
the concept had a rabbit hole nobody patched (re-shape it), or the problem was wrong
(route to discovery).

## Scoping slices for delegated builders

The building-side practices translate with emphasis shifted toward integration:

- **One piece done, early.** The walking-skeleton discipline matters MORE with agents:
  integration is where conceptual gaps surface, and cheap generation makes fragmented
  parts even more tempting than with humans. Demand a demoable end-to-end slice before
  breadth.
- **Affordances before polish, literally.** Stub interfaces and hard-coded data first;
  let the human judge flow before anyone invests in refinement that scope hammering may
  cut anyway.
- **Mechanically checkable scopes.** Draw scope lines so each one's "done" is verifiable
  by machine where possible — a test suite passing, a schema validating, a probe
  returning expected output. Ambiguous done-states invite both gold-plating and false
  completion claims.
- **Hill states in the tracking artifact.** Four text states per scope (figuring out /
  validated / known / done) in whatever board or file the team shares. A scope parked at
  "figuring out" across two checkpoints is the raised hand — investigate it at the next
  steering point instead of asking for status continuously.

## Earned autonomy

Grant delegation authority the way bets grant budgets: scoped, observed, and widened
only by demonstrated results. The pattern: start new agents, new domains, or new tools
with narrow appetites, mechanical verification, and tight caps; widen scope and raise
caps as slices ship cleanly. Authority earned this way is also revocable — a regression
pattern narrows autonomy back down without ceremony. Autonomy is priced into the bet,
not assumed as a standing permission.

## What does NOT translate

- **Six-week cadence.** With cheap generation, most useful bets fit in hours to days.
  Long boxes mainly add drift risk for agents and fatigue for the human steering them.
  Size boxes to the smallest unit that produces a demoable payout.
- **Team-size assumptions.** The book's designer+programmer pairs assume humans who
  need uninterrupted flow. Agent fleets need orchestration structure instead — but note
  the practitioner finding that structure extremes fail in BOTH directions; add roles
  only when observed failure demands them.
- **Cool-down as calendar.** Between-box slack becomes: clear stale branches and
  contexts, triage accumulated nice-to-haves honestly (most die here, correctly), and
  shape the next pitch. Shorter, more frequent, less ceremonial.
