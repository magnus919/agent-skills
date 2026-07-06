# Question Patterns for Discovery Interviews

## Core Principle

Closed questions confirm what you already think. Open questions discover what you didn't know to ask.

**Rule of thumb:** If the answer can be "yes" or "no," you're validating, not discovering.

## Question Pattern Catalog

### Story-Eliciting (highest signal density)

| Pattern | Example | Why It Works |
|---------|---------|-------------|
| **Tell me about a time** | "Tell me about the last time this process broke down." | Grounds in real experience |
| **Walk me through** | "Walk me through what you do when a new request comes in." | Surfaces steps too obvious to mention |
| **What happened next?** | Follow-up to any story | Extends narrative past comfortable stopping point |

### Assumption-Surfacing

| Pattern | Example | Why It Works |
|---------|---------|-------------|
| **What would have to be true?** | "For this to work, what would have to be true that isn't today?" | Exposes dependencies and preconditions |
| **Pre-mortem** | "It's a year from now and this failed completely. What went wrong?" | Surfaces risk without defensiveness |
| **The opposite** | "What would you do if we told you that approach won't work?" | Reveals real priorities |
| **Five whys** | Iterative "why" on any requirement | Traces surface want to root need |

### Laddering (Surface Want → Underlying Value)

1. **Attribute:** "What feature are you looking for?"
2. **Functional consequence:** "What would that let you do?"
3. **Psychosocial consequence:** "Why is being able to do that important?"
4. **Instrumental value:** "What does achieving that give you?"
5. **Terminal value:** "Deep down, why does that matter?"

**Only ladder the 2-3 most important items.** Don't ladder trivial features.

### Contrast Questions

| Pattern | Example |
|---------|---------|
| **Difference** | "How is this different from what you do today?" |
| **Absence** | "What would you do with unlimited resources?" |
| **Negative space** | "What would a bad solution look like to you?" |

### Validation Questions

| Pattern | Example |
|---------|---------|
| **Summarize and check** | "Let me make sure I understand. You're saying [summary]. Is that right?" |
| **Priority forcing** | "If you could only solve one of those problems, which one?" |
| **The disconfirming question** | "What would prove this theory wrong?" |

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| "So you need a faster approval workflow?" | "Tell me about what happens when you need approval today." |
| "Would a mobile app solve that?" | "When this problem comes up, where are you?" |
| "Don't you think this is inefficient?" | "Walk me through the process." |

## The Question Stack Protocol

Design interviews as a stack from broad to narrow:

```
Level 1: Broad exploration — "Tell me about your work with [domain]."
Level 2: Problem discovery — "Tell me about a time things didn't work."
Level 3: Deepening — "Why does that matter?" (repeat as ladder)
Level 4: Assumption testing — "What would have to be true for that to work?"
Level 5: Validation — "Let me summarize what I'm hearing..."
```

Move down only when current level stops producing novel information.

## Socratic Questioning (6 Types)

From the Socratic method, six systematic categories for disciplined inquiry:

**Type 1 — Clarification:** "What exactly do you mean by 'better'?" / "When you say 'slow,' what threshold?" / "Help me understand the distinction you're drawing."

**Type 2 — Probing Assumptions:** "What are you assuming about the user's willingness to change?" / "Is this always the case, or only in certain situations?" / "What would need to be different for that assumption to be false?"

**Type 3 — Probing Evidence:** "What evidence do you have that this is the actual cause?" / "How do you know this is a widespread issue vs. isolated complaints?"

**Type 4 — Alternative Perspectives:** "How would customer support describe this problem differently?" / "Who benefits from keeping things as they are?" / "Is there another way to interpret this?"

**Type 5 — Implications:** "If we build this, what else changes downstream?" / "And then what happens?" / "What are the second-order effects of solving it this way?"

**Type 6 — Meta-Questions:** "Why are we asking about this feature instead of that one?" / "Whose question are we really trying to answer?" / "Is this the right question to be asking?"

## Tacit Knowledge Extraction

Stakeholders know more than they can tell. These techniques surface what they do automatically:

**Master-Apprentice:** "Pretend I'm the new person. Walk me through how you handle a typical escalation." "What took you the longest to learn that you now do automatically?"

**Think-Aloud:** "As you go through this process, please narrate what you're thinking." "What cue made you decide to do that step?"

**Critical Incident:** "Tell me about the most difficult case you handled last month." "Describe the last time you had to work around the system because it couldn't do what you needed."

**Artifact Walkthrough:** "Show me your system and walk me through what you do." "What's that spreadsheet you keep open that isn't part of the official system?"

## Interview Protocol Design

Structure interviews as a phased progression:

| Phase | Duration | Question Types | Goal |
|-------|----------|----------------|------|
| Warm-up | 5 min | Context: "Tell me about your role" | Build rapport |
| Walkthrough | 15 min | Process: "Walk me through yesterday" | Observe actual workflow |
| Pain points | 15 min | Incident: "Last time it broke" | Surface tacit knowledge |
| Latent needs | 10 min | Laddering: "Why does that matter?" | Surface underlying need |
| Assumption check | 5 min | Socratic: "What would have to be true?" | Test assumptions |
| Close | 5 min | Meta: "What did I not ask?" | Capture blind spots |

## Sources

- The Mom Test (Fitzpatrick) — past behavior over hypotheticals
- Laddering — Reynolds & Gutman (1988), Means-End Chain theory
- Socratic questioning — Paul & Elder (2006)
- Pre-mortem — Klein (2007)
- "What Would Have to Be True" — Lafley & Martin, Playing to Win
- Tacit knowledge extraction — Beyer & Holtzblatt, Contextual Design
