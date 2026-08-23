# Betting

How shaped pitches become commitments — and how the commitment machinery keeps one
project from eating everything. Method from Ryan Singer's *Shape Up*
([basecamp.com/shapeup](https://basecamp.com/shapeup)).

## Bets, not backlogs

A backlog is a promise to re-read every old idea forever. The costs are real: grooming
time that produces nothing, ambient guilt proportional to list length, and stale items
that block attention from fresh ones. Shape Up replaces the backlog with a short list of
shaped pitches considered at each betting point — nothing else is on the table.

Two supporting moves:

- **Decentralized lists are fine.** Anyone can track ideas their own way (support's
  complaint tally, an engineer's bug list). What's banned is a *central* queue that
  feeds scheduling directly.
- **Important ideas come back.** If a request is real, it resurfaces — another
  customer hits it, the workaround gets more painful. If it never comes back, dropping
  it was correct.

Field-record caution: "come back" fails silently when there is no channel for the idea
to return through — a single requester with no way to re-raise, or requests arriving
through a firehose where genuinely important ones drown. If your intake is noisy,
keep lightweight per-source tallies so recurrence is observable; that preserves bets-
not-backlogs without pretending memory is free. See references/anti-patterns.md.

## The meaning of a bet

A bet is not a plan with better vocabulary. Three properties define it:

1. **Payout** — the pitch defines what exists at the end that doesn't exist now. A box
   full of tasks is not a bet; a shippable increment is.
2. **Commitment** — the team gets the whole box, uninterrupted. Pulling people out for
   side quests breaks the bet and destroys momentum, which compounds: lose an hour to
   context-switching and you lose most of a day regaining it.
3. **Capped downside** — if it doesn't ship inside the box, the default is stop, not
   extend. This is the circuit breaker: one project can never overload the system, and
   failure routes back to shaping (which mis-shaped it?) instead of deeper into the
   same hole.

Extensions are rare and require both conditions: every remaining item survived genuine
scope hammering as a true must-have, AND all outstanding work is downhill (no open
questions). Uphill work at the end of a box means shaping missed something — extending
just buys more time in the wrong place.

## Cycles are optional scaffolding

Basecamp runs six-week cycles with two-week cool-downs because at their scale the
rhythm standardizes capacity and forces trade-offs early. The cycle length itself is a
tunable parameter — shorter boxes cap downside harder but fragment meaningful work;
longer ones allow substance but let teams wander before the deadline feels real.

The basic truth underneath: commit in bounded units, only one unit ahead, keeping the
slate clean each time. Solo operators and small teams can run the loop fluidly — set an
appetite, shape, build, then shape the next thing — deliberately alternating the shaper
and builder hats. What does NOT flex well: interrupting committed work. If you cannot
protect a box from interruption at your scale, make boxes small enough that protection
is realistic (see references/hybrid-adaptation.md for agent-team sizing).

## Where bets get placed

At scale this is a betting-table meeting during cool-down: few well-shaped options,
short meeting, decisions made by people with authority to make them stick — no second
approval layer where bets go to die. The standing questions translate anywhere:

- Does the problem matter? (Weigh against other problems, not against zero.)
- Is the appetite right? ("How would you feel if it were half the size?" reveals
  whether the objection is really about time.)
- Is the solution attractive? (Watch for hidden real-estate or dependency costs.)
- Is this the right time? (Well-shaped and valuable still loses to badly-timed.)
- Are the right builders available?

Keep design and implementation debates out of the betting conversation; if it takes
more than moments, the pitch needs more shaping, not louder arguing.

## Product maturity changes the bet

- **Existing product:** normal flow — shape, bet, build, ship into the current system.
- **New product, R&D phase:** don't pretend to shape what nobody understands yet. Bet
  on spikes by senior builders; the goal is learning plus load-bearing architectural
  decisions, not shipping. Still one box at a time.
- **Production phase:** architecture settled, formal shaping resumes, shipping means
  merged-and-left-alone even before public launch.
- **Cleanup phase:** structure drops away deliberately near launch — unstructured
  must-have fixing, bounded to avoid becoming a way of life.

## Handling defects between bets

Bugs are not automatically interrupts. Three channels absorb them without breaking
bets: fix them in uncommitted time between boxes; bring genuinely large ones through
shaping and bet on them like anything else; and periodically dedicate a whole box to a
bug smash when debt accumulates. Reserve interrupts for actual crises — data loss,
everything broken — which are rare by definition.
