# Editing and Revision

Turning a finished draft into a submission-ready manuscript: the correct order of operations, the critique protocol, layered revision passes, line editing, and proofreading. Use this in Editor mode. Never run this while a draft is still being written.

## The order of operations (non-negotiable)

1. **Rest.** Set the draft aside for at least a week to ten days (a month is better) before touching it. You cannot edit what you are still composing.
2. **Trusted readers.** Recruit 2–5 advance readers; get big-picture reactions before any polish.
3. **Structure-first passes.** Plot, character, pacing, chronology — the bones. No line editing until the bones hold.
4. **Prose passes.** Voice, sentence craft, word choice, show-don't-tell.
5. **Line editing and mechanics.** Grammar, punctuation, consistency.
6. **Proofreading.** The six passes in `prose-and-style.md`, then a fresh external read.

Expect revision to take roughly half the draft's time or longer, and to run several rounds. A common failure is polishing structure that is about to be cut.

## The critique protocol

Whether you are the critic or you are coaching the writer to gather feedback:

- **Choose a trusted, honest reader** — one who wants the writer to succeed and tells the truth about the work.
- **Ask big-picture questions first:** Does it make sense? Is the message the intended one? Did the sequencing work? Was it interesting and believable? Where are the weak spots? Is it submission-ready?
- **Then targeted, page-referenced questions:** "Is the metaphor on page 6 too much?" "Does the scene at the diner earn its length?"
- **Structure the feedback:** what works first, then what doesn't, then a suggested fix — never a verdict without a fix.
- **Treat criticism as about the work, not the self.** Agree-to-disagree is allowed; if every reader flags the same problem, fix it.
- **The agent as critic** must preserve the author's voice, give suggestions provisionally, and state what works before what doesn't.

## Revision passes, in order

### 1. Structural pass (the big picture)

- Read the whole draft, then **outline after the draft**: a scene-by-scene list is the primary instrument for diagnosing pacing, chronology, subplot balance, and cause-and-effect.
- Run the **plot lens** from `craft-and-structure.md`: where are the four markers; does each scene touch the protagonist; do scenes chain by cause and effect?
- Run the **scene lens**: the seven essential elements, enter late / end early, one change per scene. Move, add, cut, or reorder — expressed as change requests, not prose edits.
- Check the **three plot lines** are all advancing and converging at the climax: dramatic action, character emotional development, thematic significance.
- Fix subplots: a subplot survives only if removing it would change the main story's outcome or emotional impact.
- Expect to cut 35–100 pages from the beginning; the story's real start is often several chapters in.
- Selective read-throughs: by subplot, by character, by setting — each line woven through the whole draft.

### 2. Scene-level questions (one per scene)

1. Does it establish when and where?
2. How does it develop the character's emotional makeup?
3. Is it driven by a specific character goal?
4. What dramatic action is shown?
5. How much conflict, tension, suspense, or curiosity?
6. Does the character show emotional change within the scene?
7. Does it reveal thematic significance?

### 3. Prose passes (one focus at a time)

- **Verb strength:** replace weak verbs; prefer precise verbs over verb + adverb ("flinched" not "drew back quickly").
- **Passive-voice reduction:** convert to active unless the object or unknown agent is the point.
- **Adjective/adverb trimming:** delete filler adjectives and transition-style adverbs; split the sentences that relied on them.
- **Wordcraft:** strong nouns, killed clichés and dead/mixed metaphors, varied sentence length, key words at sentence ends.
- **Show-don't-tell sweep:** label the spots where emotion is named rather than rendered; give a concrete rewrite per spot.
- **Dialogue pass:** the blind test per speaker; subtext over on-the-nose; invisible tags.

### 4. Consistency and mechanics

- POV, tense, person, tone, and style consistency.
- Character consistency: names, ages, traits, timelines (keep a character sheet up to date).
- Grammar and punctuation per `prose-and-style.md`.
- Chronology and continuity: dates, seasons, times of day, distances, technology.

### 5. Proofreading

The six passes: read aloud, read backward, targeted weak spots, spelling-only, tense/person, fresh external reader.

## Revision aids

- **The before/after character profile.** Re-fill the character profile from memory of the finished draft and compare with the original; drift reveals what the character actually became.
- **The one-page synopsis** written from the finished draft exposes structural gaps and reveals whether the pitch writes itself.
- **The jacket blurb exercise:** write blurbs for ten admired books, then one for your own without giving away the plot; if you can't, the story's appeal isn't clear yet.
- **A deadline to stop.** Revision needs an end; without one, polish is infinite. Set "good enough for submission" and mean it.

## Manuscript metrics (numbers as questions)

Run `scripts/manuscript-stats.py` and use the output as a diagnostic, not a verdict:

- **Word count vs. format contract** (`genres-and-formats.md`): is the length right for the genre and age category?
- **Sentence length distribution:** monotony reads as flatness.
- **Passive-voice ratio and adverb density:** spikes point to weak verbs.
- **Crutch words:** repeated pet words ("just", "really", "very", "that", character tics) that readers notice.
- **Per-chapter pacing:** chapter length outliers; sagging middles show up as flat word counts with no events.
- **Readability index:** verify against the intended audience.

## The final polish checklist (before any submission)

- Does the opening hook in the first pages (the "deadly ten")?
- Is the antagonist stronger than the protagonist? Does the lead have an arc someone would want to play?
- Any clichéd lines or scenes left? A strong climax?
- Does every scene start as late as possible and end as soon as possible while pushing the story forward?
- Is the manuscript formatted per its market's conventions (see `genres-and-formats.md`)?
- **Wait, reread, then send:** after the final polish, wait at least a week, reread once, fix what jars, then submit. You get one first impression; a bad first read can persist in a company's records.

## What the assistant does at this stage

- Gate the sequence: refuse to line-edit a draft that hasn't had structural passes; enforce the rest period.
- Run one pass at a time, with concrete before/after examples.
- Act as a structured critic (what works → what doesn't → suggested fix) and as the fresh external reader for comprehension.
- Compute manuscript metrics and turn them into questions.
- Help draft the revision plan (template: `templates/revision-plan.md`) and track passes to completion.
