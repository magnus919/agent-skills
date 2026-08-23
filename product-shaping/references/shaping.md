# Shaping

The pre-work that turns a raw idea into a bettable pitch: set boundaries, sketch the
solution's elements, patch the rabbit holes, write the pitch. Method from Ryan Singer's
*Shape Up* (free at [basecamp.com/shapeup](https://basecamp.com/shapeup)); problem-
narrowing craft owes its lineage to demand-side interviews (Moesta/Spiek, thanked in
the book).

## Step 1 — Set boundaries

Two decisions frame everything after:

**Set the appetite.** How much time is this idea worth? Two sizes cover most cases:
small batch (a fraction of a box, buildable alongside other small work) and big batch
(the whole box). If no version of the idea fits any appetite you'd pay, that is a real
answer — walk away and let it come back if it matters.

**Narrow the problem.** Take requests at face value and most are six-week projects.
Ask instead what is actually going wrong. The book's calendar story is the canonical
move: don't ask *why* do you want a feature (you'll get a feature list), ask *when*
the need occurred — what was happening when the status quo broke? That story converts
"do everything a calendar does" into "help me see free spaces," which is buildable.

Watch for grab-bags: "redesign X", "X 2.0", "clean up Y" have no defined start or end.
Re-anchor them on one specific problem ("sharing files takes eleven steps") or refuse
them as projects. A grab-bag routed here should either gain a specific problem or route
to product-discovery for proper investigation.

Default response to raw ideas: "Interesting. Maybe some day." A soft no keeps options
open without committing to work you don't understand yet. Ideas that matter come back;
see references/betting.md for why there is no backlog to forget them in.

## Step 2 — Find the elements

Sketch the solution at deliberately low fidelity so you can explore widely and leave
room for builders.

**Breadboarding (for flows).** Three primitives only: **places** (screens, pages,
states you navigate to), **affordances** (things acted on: buttons, fields, copy),
and **connection lines** (what leads where). Words and arrows, no visuals. The value:
writing out the flow provokes the real questions ("does enabling autopay also settle
the current invoice?") without anyone sinking hours into pixels that get thrown away.
Text form works fine:

```
[Invoice page]
  - "Turn on Autopay" button  --> [Setup Autopay]
[Setup Autopay]
  - card field, bank field
  - "Enable" button           --> [Confirmation + receipt]
```

**Fat-marker sketches (for visual problems).** When 2D arrangement IS the problem,
sketch with strokes too fat to permit detail. The constraint is the point: it keeps
the exploration at arrangement-level and makes premature polish physically difficult.
Annotate with words.

**Shaping non-UI work.** Most of what agents and platform teams build has no screen.
The equivalents translate directly:

| UI concept | Non-UI equivalent |
|---|---|
| Places | Components, services, data stores |
| Affordances | API endpoints, CLI verbs, events, contracts |
| Connection lines | Call graphs, data flows, event sequences |

A backend breadboard is a components-and-interfaces sketch: boxes for the pieces, named
arrows for contracts between them, deliberately silent on implementation internals. An
infrastructure change gets an interface sketch (who calls what, what changes for each
caller) plus explicit out-of-bounds lines. This is the same territory RFC/design-doc/
ADR culture covers before code; those documents are fine carriers for shaped output as
long as the fidelity stays at elements-and-connections.

**Output of step 2:** a short list of concrete elements. "A two-up month grid, dots for
events, agenda below that scrolls on tap" — narrow enough to bound the project, rough
enough that every downstream decision stays open.

## Step 3 — Address risks and rabbit holes

Slow down and attack your own sketch. Walk one use case through the solution in slow
motion and hunt for gaps. Then interrogate viability:

- Does this require technical work we've never done?
- Are we assuming parts fit together without evidence?
- Are we assuming someone can solve a design problem we haven't solved?
- Is there a hard decision better settled now than mid-box under deadline?

When a hole appears, choose: patch it by dictating the answer in the pitch (the book's
completed-to-dos example: keep legacy rendering, append group names — ugly but bounded),
declare the case out of bounds, or cut the element. De-risking trades elegance for
thin-tailed odds, and that is the correct trade when the box is fixed.

Present the sketch to people who know the code or the data before writing the pitch —
privately, framed as "something I'm shaping, not committed." Ask "is X possible within
this appetite?" never bare "is X possible?" Everything is possible; nothing is free.

## Step 4 — Write the pitch

Package the shaped concept using [templates/PITCH.md](../templates/PITCH.md): problem
(one story), appetite (budget + team shape), solution (elements at readable fidelity —
selectively more concrete than step 2 where readers must "see" it), rabbit holes (each
patch spelled out), no-gos (explicit fences). A pitch missing problem+appetite+solution
together is not ready: solution-without-problem invites design debates, problem-without-
solution pushes research onto the building team where the risk profile misaligns.

The pitch is the handoff artifact. At kick-off it becomes the team's whole context; a
reader with zero session history should be able to evaluate the bet from the document
alone.

## When not to shape

- The problem isn't validated → route to `product-discovery` first; shaping narrows
  validated problems, it doesn't discover them.
- The question is strategic (positioning, portfolio weight, whether to enter a market)
  → `product-strategy` owns that layer.
- The work is genuinely small, routine, and fully understood — shaping overhead exceeds
  its risk reduction. Just do it and note why no bet was needed.
