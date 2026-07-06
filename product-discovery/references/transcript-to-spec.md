# Transcript-to-Spec Distillation

## The Critical Bridge

This is where the most information loss occurs. Raw conversation notes enter one end; a structured SPEC.md exits the other. The methodology makes the translation visible and auditable.

## The 9-Step Workflow

### PREP: Before the Conversation
Load the gap detection reference to prepare for recognizing what stakeholders don't say.

### STEP 1: Segment the Transcript
Tag each utterance by type:

| Segment Type | Example |
|-------------|---------|
| **Statement of desire** | "We need to be able to export reports as CSV" |
| **Anecdote / narrative** | "Last week a customer spent 45 minutes trying to..." |
| **Rule / constraint** | "Only admins can delete projects" |
| **Hedge / weasel word** | "We should probably handle that eventually" |
| **Question** | "What happens when the payment fails?" |
| **Deflection** | Topic change, non-answer |

### STEP 2: Identify Candidate ACs Using Linguistic Markers

| Stakeholder Says | → | What It Yields |
|-----------------|---|----------------|
| "We need to [capability]" | → | 1:1 AC — explicit requirement |
| "When X happens, Y breaks" | → | Implied AC — inverse of complaint |
| "Only X can do Y" | → | Rule/constraint — needs positive + negative scenarios |
| "What about X?" | → | Edge case cue |
| "Remember when X happened?" | → | Error scenario — apply freeze-frame |

### STEP 3: Classify Each AC by Origin

| Category | Definition | Becomes |
|----------|-----------|---------|
| **SAID** | Explicitly stated by stakeholder | Direct AC |
| **IMPLIED** | Logically necessary for a SAID requirement | Infrastructure AC |
| **INTERPRETED** | Added by distiller from domain knowledge | Additional AC — flag for validation |
| **INFERRED** | Derived from a gap or avoided topic | Open Question — NOT an AC |

### STEP 4: Apply the Anecdote-Freeze-Frame Technique

For every anecdote, freeze at three points. Each freeze frame generates 1-2 ACs:

1. **FF1 — BEFORE:** State and user action preceding failure
2. **FF2 — DURING:** What happens during failure (system state, UX)
3. **FF3 — AFTER:** Outcome and what the user learns

**Ratio:** 1 anecdote → 3-5 ACs minimum.

### STEP 5: Convert to Given/When/Then

Use the "Friends Episode" naming convention — memorable titles stakeholders can recognize:

```
❌ "Validate pagination parameters when exceeding max limit"
✅ "The one where someone tries to export the whole internet"
```

### STEP 6: Flag Interpretation Risk

| Level | When | Action |
|-------|------|--------|
| **LOW** | AC maps 1:1 to explicit statement | Source attribution only |
| **MEDIUM** | Clear statement, but edge cases unstated | Flag in Open Questions |
| **HIGH** | Vague language, multiple interpretations | MUST validate with stakeholder |

### STEP 7: Identify and Log Conflicts

Cross-reference all AC candidates. Classify by type:

| Type | Example | Resolution |
|------|---------|------------|
| Genuine disagreement | Different stakeholders want different behaviors | Escalate to decision-maker |
| Role-dependent | Each role needs different rules | Role-based behavior is often correct |
| Temporal | "Now" vs "later" | Priority question |
| Terminology | Different meanings for same word | Agree on shared glossary |
| Assumption clash | Different beliefs about what's feasible | Translate to NFR threshold |

### STEP 8: Identify Gaps (Inferred Requirements)

Review the transcript for what stakeholders DID NOT discuss. Use the gap detection checklist:

- Abstract nouns never unpacked
- Decisions deferred without trigger/owner/deadline
- People absent from the conversation
- Edge cases that follow naturally from stated requirements but were never mentioned

Convert gaps to Open Questions, NOT to ACs.

### STEP 9: Validate with Stakeholders

- HIGH-risk interpretations → validate with original speaker first
- Conflicts → present to decision-maker with both positions documented
- Formalized ACs → run the "would you say yes to this?" test

## The Interpretation Audit Trail

Every AC in the spec should trace to a specific discovery artifact:

```markdown
### AC-001.1: Request generates confirmation
**Source:** Sarah (Support), quote: "The worst is when you submit and it just vanishes."
**Interpretation risk:** LOW — explicit concern about visibility
**Cross-reference:** Bob (Engineering) confirmed email notifications are feasible
```

## Sources

- Specification by Example (Adzic) — deriving executable specs from conversations
- Example Mapping — Wynne/Cucumber — 4-color card technique
- Deliberate Discovery (North) — learning as the constraint
- Acceptance Criteria vs Scenarios (Keogh) — rules vs. examples
