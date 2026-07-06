# Stakeholder Mapping & Interview Sequencing

## The Discovery Role Quadrant

Before any interview, map stakeholders into four distinct roles:

| Role | Primary Question | Who This Describes |
|------|-----------------|-------------------|
| **Knowledge holders** | What's the problem? | Domain experts, support staff, power users, people who do the work daily |
| **Authority holders** | Is this worth solving? | Executives, budget owners, product sponsors, compliance |
| **Affected parties** | How will this change what they do? | End users, downstream teams, support, operations |
| **Implementation knowers** | Can we actually build this? | Engineers, architects, data owners, security, platform teams |

**Key rule:** Knowledge holders come first. Authority holders validate — they don't originate.

## Interview Sequencing

```
Phase A: Problem Discovery
  1. Knowledge holders (domain experts, support, power users)
     → What's broken? What do people actually need?

Phase B: Feasibility & Constraint Mapping
  2. Implementation knowers (engineers, architects, security)
     → What's technically feasible? What are the hard constraints?

Phase C: Validation & Commitment
  3. Authority holders (executives, sponsors, compliance)
     → Here's what we learned. Does this align with your priorities?
```

Affected parties (end users, downstream teams) should be consulted throughout, consulted in Phase A alongside knowledge holders.

## The Reverse Map

When you suspect missing stakeholders, work backward from impact:

- Who will have to change their workflow if this ships?
- Who will be asked to support or maintain the result?
- Who will lose something if this succeeds?
- Whose data or systems will be affected?
- Who has tried to solve this before and why did they fail?

## The "Three Questions" Per Interview

| # | Question | Purpose |
|---|----------|---------|
| 1 | "What's the biggest problem you're trying to solve?" | Surface their stake |
| 2 | "Who else should I talk to?" | Snowball sampling |
| 3 | "What would you do if you were in my shoes?" | Reveals assumptions about solution space |

## Common Patterns

**The one-stakeholder trap:** One person cannot represent an entire stakeholder category. Require minimum 3 sources per requirement category.

**The silent stakeholder:** The most important stakeholder is often the one who doesn't show up — the downstream team, operations, compliance. Ask "who else should we be talking to?" in every interview.

**The authority-first trap:** Natural instinct is to talk to the most powerful person first. This produces a spec that reflects their understanding — which may be outdated or politically colored. Authority holders go last.

## Output

For each stakeholder, produce a structured record:

```markdown
## Stakeholder: [Name / Role]
**Role type:** Knowledge / Authority / Affected / Implementation
**Key inputs:**
- Their understanding of the problem
- Their constraints and concerns
- Their definition of success
**Gaps noted:** What they deferred, what they didn't know
**Priority:** Must interview / Should interview / Optional
```

## Sources

- Power/Interest Grid: Mendelow (1981), Eden & Ackermann (1998)
- Stakeholder Salience: Mitchell, Agle & Wood (1997)
- Four-phase sequencing pattern: synthesized from practitioner sources
