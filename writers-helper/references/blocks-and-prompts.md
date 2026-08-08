# Creative Blocks and Prompts

The psychological machinery of writing: how to diagnose a block, the matched fixes, how to generate prompts that actually advance a story, and an exercise library. Use this in Coach mode whenever a writer is stuck, stalled, or needs an entry point.

## Diagnose before prescribing

Writer's block is not one thing. Name the cause, then match the fix:

| Diagnosis | Signs | Fix |
|-----------|-------|-----|
| **Fear of failure** | Won't start; procrastinates; perfects endlessly | Permission to write badly; tiny timed next action; slop-on-the-page draft; deadline contract |
| **Fear of success / exposure** | Stops near completion; sabotages finished work | Name the fear; write the next sentence anyway; share small pieces; the "one specific reader" reframe |
| **Low energy / biochemistry** | Can't focus even when motivated | Short walk, brief nap, protein-first snack; move the session; a five-minute sprint counts |
| **Thin material** | Doesn't know what happens next | New scene/character/element; position-aware prompt; what-if chain; research the gap |
| **Broken story** | Draft stalls in the middle; keeps restarting | Structural diagnosis (markers, scene elements); outline-after-draft; cut and re-choreograph; push forward |
| **Fixing the wrong problem** | Editing prose when structure is the issue | Gate the sequence: structure first, prose later |
| **Over-control** | Perfectionism, over-planning, judging while writing | The ten-minute continuous freewrite; fast drafting; no re-reading mid-draft |
| **Avoidance mislabeled** | "Thinking about writing" for months | 1,000-words-a-day floor; don't leave the chair; boomerang submissions |

- **Block types:** task-related (structure/topic/research), energy-related, or person-related (fear, guilt, old authority battles) — each takes a different remedy.
- **Procrastination vs. perfectionism:** can't write = procrastination; can't start = perfectionism. Both dissolve into a small, timed, low-stakes next action.
- **The two voices:** blocks often look like a war between the logical voice and the emotional voice. Don't deny the emotional brain — supply it: contract for a reward up front (at least half the session time) and it stops hijacking time.
- **The inner critic at thresholds:** at each major turning point a voice insists the work is worthless. Name and date the voice; gather counter-evidence; never become that voice for another writer.
- **The 75% writer's crisis:** many writers hit their own crisis three-quarters through — denial, anger, bargaining. Recognize the pattern, take a walk, write the emotions down, and hand them to the character.
- **Respect boundaries:** if the user describes depression, serious anxiety, or other clinical concerns, stop the coaching and route to qualified professional help; creative exercises are not a substitute for clinical support.

## The position-aware prompt formula

A prompt's value depends on where the story is. Asking a story at 70% to do first-quarter work wastes a day. The single most useful question before generating: **which quarter of the story are you in, and which energetic marker are you approaching?**

Generate three-part prompt sets:

1. **Affirmation** — one to two sentences, first person present tense, restating willingness and commitment (fresh wording, never someone else's).
2. **Plot element** — exactly one structural element the story's position demands: goal, setting, antagonist, ally, flaw, fear, dream, secret, theme, subplot, cause-and-effect chain, threshold, foreshadowing, symbol, cliffhanger, deadline, backstory reveal, recommitment, crisis, climax, resolution, loose end.
3. **Writing assignment** — a concrete scene-or-summary task that forces that element onto the page and continues prior material, with anti-cliché and show-don't-tell constraints built in.
4. **Record block** — start/stop time, word count, daily goal, 1–10 energy reading, above/below-the-line placement, and which character-profile trait the scene revealed.

**Position-to-element rotation (restated):**

- **Beginning:** goal, ordinary world, protagonist's voice and reaction pattern, antagonist introduction, ally, flaw, fear, dream planting, stakes/loss, theme planting, sensory signature, threshold crossing.
- **Halfway:** exotic-new-world contrast, deepening the new world, goal re-establishment, primary antagonist escalation, subplot chain, motivation questions, fear confrontation, mirror moment, recommitment.
- **Crisis:** confidence before the fall, missing-skill setup, real risk of loss, power fully transferred to the antagonist, deadline countdown, horrible event, defenses and excuses, self-revelation, the crisis itself, the emptied prize and backstory reveal, the pull-herself-up moment.
- **Climax & resolution:** first step into the final quarter, threshold-guardian test, new belief system, cause-and-effect pairs, the transformed action, the climax, allies' goals realized, resolution with deliberately loose ends, dream payoff as twist.

**The anti-freewriting rule:** freewriting and fragments are fine as warm-up but not as product. Everything must advance the plot; a fragment must promise a scene. Redirect "I don't know what to write" to "what does the character want right now, and what will she do next that advances the goal?"

**Never repeat, deepen:** when a prompt reuses a beat (goal, fear, antagonist encounter), deliberately escalate — wider consequences, higher stakes, a new angle.

Use `scripts/writing-prompt.py` for deterministic, seeded prompt generation, and `templates/prompt-cards.md` for the formula and original examples.

## Exercise library (original formulations)

- **What-if chains:** from any premise, chain hypotheticals; invented logic may outrank literal truth.
- **I-wonder questions:** same move, curious rather than dramatic.
- **The ten-minute freewrite:** no stopping, no correcting; if stuck, write "I can't think of anything to write because..." until it unblocks.
- **Combinatorial lists:** one character type × one conflict × one setting; love-list vs. hate-list as two characters' values.
- **Eavesdrop and people-watch:** a notebook habit; dialogue transcribed and then edited down.
- **One emotion, five scenarios:** render the same feeling in five different situations, each as behavior.
- **The alternate branch:** replay a decision you made with its alternate path — memoir and fiction alike.
- **Word-association chains:** free-associate from a trigger word; circles on paper release the linear mind.
- **Animate an object:** tell the story from a thing's point of view — a constraint that forces concreteness.
- **The PA interview:** for an underdeveloped character, ask three open questions at length — if you were a road where would you lead; if you were an animal what would you be; what one life event made you who you are. Short answers = secondary character; long answers = lead.
- **The "20s" originality exercise:** force twenty versions of any moment (a meeting, a chase, an entrance); the first few are clichés and the ninth or tenth is usually golden. Never settle for the first idea.
- **Scene entry drill:** write the same scene starting at three different points; keep the latest entry that still works.
- **The letter-to-a-friend trick:** to find a natural voice for a synopsis, proposal, or pitch, first write a plain letter to a trusted friend describing the book; then lightly edit the letter into the formal document.

## Daily prompting practice

- **Write every day at the same time**; the repetition is the technique.
- **Position-aware prompt sequence:** a 120-day sequence built in four parts (beginning, halfway, crisis, climax) where each part's final prompt is the marker scene itself — completing the sequence writes a structurally complete draft.
- **Record everything:** energy trend (1–10) is self-diagnostic; falling energy = the story or the process is out of balance.
- **Rotate the spotlight:** protagonist one day, antagonist next, love interest after — keeps every character developing.
- **The anti-snippet rule:** a prompt book that produces only pretty fragments has failed; every page should accumulate into the story.

## What the assistant does at this stage

- Ask where the story is before generating anything; never produce generic prompts detached from position.
- Diagnose the block type explicitly and apply the matched fix; name the pattern (procrastination, restart syndrome, inner critic at the threshold, 75% crisis) and address the psychology before adding more craft.
- Generate fresh three-part prompt sets with a record block; never reproduce a book's prompts verbatim.
- Enforce the anti-freewriting rule in coaching mode; redirect fragments toward plot-advancing scenes.
- Escalate rather than repeat when beats come up again.
- Route clinical concerns to professional help without diagnosing.
