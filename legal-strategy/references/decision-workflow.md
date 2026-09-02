# Legal Strategy Decision Workflow

This is a structured issue-spotting and escalation method, not legal advice. A licensed lawyer or qualified local counsel must review jurisdiction-specific conclusions before reliance or action.

## Repeatable Method

1. **Frame inputs:** jurisdictions, entities, data/users, product behavior, contract text, dates, business objective, and known facts versus assumptions.
2. **Issue-spot:** identify applicable regimes, rights/obligations, trigger facts, conflicts, uncertainty, and potential harm. Cite primary sources or counsel questions; do not state an unverified conclusion as law.
3. **Triage:** classify impact and urgency (low/medium/high/critical), identify a reversible interim control, and escalate high-impact, novel, regulated, cross-border, dispute, employment, or filing matters to counsel.
4. **Validate:** counsel confirms interpretation, owner, deadline, control, and evidence. Revisit when jurisdiction, product, vendor, or law changes.
5. **Package evidence:** produce a dated jurisdictional risk/escalation memo with sources, assumptions, open questions, counsel disposition, and review date. Use `artifact-pyramids` for the evidence index.

## Worked Example

A startup plans EU and US rollout of an AI feature that profiles business users. The memo separates known processing facts from assumptions, flags GDPR/AI Act and state privacy questions, rates the cross-border and automated-decision uncertainty high, and pauses launch of profiling until privacy counsel validates lawful basis, notices, transfer controls, and any required assessment. It routes security controls to security owners and records counsel's written disposition; it does not claim that the memo itself determines compliance.

## Reusable Artifact

```text
Jurisdictional risk and escalation memo
Matter / business decision / owner / date / review date
Jurisdictions and facts (known vs assumed):
Potential regimes and trigger facts:
Risk, uncertainty, urgency, reversible interim control:
Questions for licensed counsel:
Counsel disposition / conditions / deadline:
Evidence, decision log, and next review:
```

## Routing Matrix

| Need | Route to | Handoff in / out |
|---|---|---|
| Strategic trade-off | [strategy-frameworks](../../strategy-frameworks/SKILL.md) | Legal constraints in; strategic options out |
| Cost, reserve, or unit economics | [financial-modeling](../../financial-modeling/SKILL.md) | Exposure assumptions in; modeled scenarios out |
| Technical controls or architecture | [technology-radar](../../technology-radar/SKILL.md) | Legal requirement in; feasible controls out |
| Remediation sequencing | [implementation-planning](../../implementation-planning/SKILL.md) | Counsel-approved work in; delivery sequence out |
| Evidence dossier | [artifact-pyramids](../../artifact-pyramids/SKILL.md) | Memo and sources in; durable index out |

Do not invent a Phase 2 legal specialty skill. Escalate to licensed counsel for legal interpretation, filings, advice, or jurisdiction-specific action.
