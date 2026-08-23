# Building

How a team executes inside the box: own the whole project, integrate one slice early,
map discovered scopes, make uncertainty visible, and hammer scope until it fits.
Method from Ryan Singer's *Shape Up* ([basecamp.com/shapeup](https://basecamp.com/shapeup)).

## Hand over responsibility

Give the team the project, not tasks. Shredding the pitch into assigned tickets up
front loses the whole picture: each person executes their fragment without judging how
fragments fit, and planning done before real work begins is blind to what real work
reveals. The shaped pitch supplies direction and boundaries; the building team owns
task discovery, sequencing, and scope trade-offs within them.

This is not freedom to wander. The boundaries from shaping (appetite, elements,
no-gos) are guard rails; autonomy lives inside them.

**Kick-off reality check:** the first days look like nothing. People read code, poke at
the system, hit dead ends finding a starting point. That silence is legitimate work —
interrogating it too early pushes exploration underground instead of shortening it.

## Get one piece done

Do not build disconnected parts hoping they assemble in the final week. Pick one slice
that is **core** (central to the concept), **small** (days, not weeks), and preferably
**novel** (teaches something nobody knows yet) — and take it end-to-end first: working
interface wired to working behavior, demoable. A thin walking skeleton beats polished
fragments because it proves the concept while there is still time to react.

Supporting moves:

- **Affordances before polish.** Builders can start from stubs — plain buttons, plain
  fields, hard-coded data — long before visual design lands. First make it work; only
  then make it good-looking.
- **Program just enough for the next step.** Early backend work is strategically
  patchy: mock data where the point is UI judgment, hard-coded auth where the point is
  testing flows. Scaffolding is disposable by design.
- **Start in the middle.** Skip login pages and setup wizards; jump straight to the
  interesting problem and stub everything around it.
- **Designers don't block builders and vice versa.** With elements defined in the
  pitch, both ends work in parallel on the same slice and meet in the middle.

## Map the scopes

After the first integrated slice, organize remaining work by project structure, not by
role or person. A **scope** is an integrated slice of the project — bigger than a task,
smaller than the project — that can be finished independently in days. Scopes emerge
from doing real work: you cannot draw the map before walking some territory, so expect
the reliable map around end of week one and expect lines to move as interdependencies
reveal themselves.

Use [templates/SCOPE_MAP.md](../templates/SCOPE_MAP.md). Health checks:

- Right: you can see the whole project; scope names become the team's conversation
  language; new tasks have obvious buckets.
- Redraw when: "done" is undefinable for a scope (its tasks are unrelated), names would
  fit any project ("front-end", "bugs" = junk drawers), or a scope grows too big for
  near-term victory.

Shape patterns: most projects are **layer cakes** (UI + thin backend — judge by surface
area); watch for **icebergs** (small visible feature over massive hidden complexity)
and factor the mass into its own scopes so it can't hide. Keep a small **chowder**
list for genuinely homeless tasks; past three-to-five items, there's an undrawn scope.

## Show progress with the hill

Task counts lie in both directions: lists grow as work progresses (discovered tasks),
and an empty list can mean "done" or "nobody has looked yet." Estimates hide their own
uncertainty — four hours means nothing different for well-trodden work versus never-
done-before work that might take three days.

The hill chart fixes this by reporting unknowns instead of percentages. Each scope sits
at one point: **figuring out** (uphill, unknowns dominate) → **validated** (approach
proven on the hard part) → **known** (all downhill, execution only) → **done**. The
text-state table in the template replaces Basecamp's draggable chart; the semantics
carry. Second-order value comes from comparing snapshots: a dot that hasn't moved is
someone silently stuck, surfaced without anyone having to say "I'm stuck" out loud —
and the conversation becomes about the work ("what's keeping this uphill?") rather
than the person.

Two disciplines:

- **Earn the top.** Thinking you know the approach is the first third uphill;
  validating it is the second; being far enough into the build that surprises are
  unlikely is the top. Head-solved-but-never-touched work slides back down.
- **Solve in the right sequence.** Push the scariest scopes uphill first; leave routine
  work for last. If time runs out, you want the surprises behind you and only screw-
  tightening left — the inverted pyramid applied to risk.

## Decide when to stop

There is always more work than box. Shipping means shipping imperfect things, chosen
well:

- **Compare down to baseline, not up to ideal.** The question isn't "is this our best
  possible work?" but "is this clearly better than what customers have today?"
  Perfection has no finish line; better-than-baseline does.
- **Scope grows like grass** — not from bad people but from proximity. Every close look
  reveals improvements. Don't try to stop growth; constantly cut it.
- **Cutting scope is not lowering quality.** Being picky about what gets built at all
  differentiates the product; quality standards for what IS built stay high.
- **Scope hammering.** For every discovered addition ask: could we ship without this?
  What actually happens if we don't do it? Is it a new problem or one customers already
  live with? How likely is it, and who hits it? Must-haves go on the scope; everything
  else gets a `~` and is first against the wall when the box closes in. Marking the
  tilde IS the hammering.
- **QA is a level-up, not a gate.** Builders own basic quality of what they make; QA
  effort concentrates on edge cases late in the cycle, and its findings default to
  nice-to-haves that the team triages upward only if severity demands. Code review
  works the same way: valuable, welcome, and not a checkpoint that blocks shipping.

## Move on

Shipped features generate feedback storms — requests, complaints, "you ruined it."
Let the storm pass before reacting. Then handle input without taking on debt:

- Post-ship requests are raw ideas again. The gentle no ("interesting, maybe some day")
  keeps future options open; saying yes immediately is borrowing capacity you haven't
  budgeted.
- Anything that truly matters re-enters through shaping and competes at the next
  betting point like every other idea.

This closes the loop back to [references/shaping.md](shaping.md): feedback needs to be
shaped before it can be bet on.
