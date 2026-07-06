# AI-Conducted Discovery

## When an AI Conducts Discovery Interviews

AI agents conducting discovery have unique failure modes that differ from human-led discovery. The most dangerous is sycophancy — the architectural tendency of RLHF-trained models to validate rather than challenge (Sharma et al. 2023, arXiv:2310.13548).

## Failure Modes

**Sycophancy:** Models are predisposed to agree with stakeholder statements. An AI asking "Wouldn't a dashboard be useful?" is structurally likely to validate the suggestion rather than probe it. The "are you sure?" problem means models abandon correct lines of inquiry after simple pushback.

**Confirmation bias in synthesis:** AI agents over-weight findings matching common training patterns (SaaS architectures, dashboard UIs) and under-weight novel or domain-specific requirements. They may hallucinate consensus where none exists.

**Leading questions through prompt structure:** Order effects, inference from prior context, and question framing steer conversations before the interviewer consciously chooses a direction.

**The trust paradox:** Stakeholders may be more honest with an AI (no social judgment) or less honest (dismissive, strategic self-editing, expectation of agenda).

## Mitigation Techniques

### Pre-Interview
- **Anti-sycophancy prompting:** "Your role is to challenge assumptions and probe for inconsistencies. Prioritize accuracy over agreement."
- **Bias audit of interview script:** Have a human review the question set for leading structure
- **Stakeholder priming:** Inform stakeholders the AI is programmed to challenge assumptions

### During Interview
- **Structured disagreement:** Offer counterpoints explicitly: "Some teams find that approach increases maintenance burden. Does that apply here?"
- **Multi-pass questioning:** Run the same topic from different angles; surface inconsistencies non-judgmentally
- **Triangulation questions:** Ask about the same requirement from different stakeholder roles

### Post-Interview
- **Confidence tagging:** Each finding carries a score based on consistency, specificity, and whether volunteered or elicited
- **Deviation reporting:** Explicitly call out where stakeholder testimony contradicts known data
- **Human review gate:** AI-conducted outputs must be reviewed by a human PM before acceptance
- **Stakeholder validation loop:** Share synthesized findings back before proceeding

## When the Spec Consumer Is Also an Agent

When discovery feeds directly into a coding agent (not a human team):

- **Precision requirements increase:** A coding agent cannot infer missing context. Every ambiguous statement produces random implementation.
- **No re-clarification loop:** The agent processes the entire spec in one shot. Include an ambiguity inventory flagging every point with multiple interpretations.
- **Explicit constraint encoding:** Non-functional constraints (compliance, architectural preferences, performance SLAs) must be first-class artifacts, not context.
- **Example-driven specs:** Coding agents benefit more from concrete input/output examples than abstract descriptions (CodeGen multi-turn research, Nijkamp et al. 2022).
- **Context window budgeting:** Most critical information (core behavior, key constraints) first; secondary details later.

## Sources

- Sharma et al. (2023) — "Towards Understanding Sycophancy in Language Models," arXiv:2310.13548
- Carro (2024) — "Flattering to Deceive," arXiv:2412.02802
- CodeGen (Nijkamp et al., 2022) — Multi-turn program synthesis, arXiv:2203.13474
- Anthropic (2025) — Persona vectors for sycophancy detection
