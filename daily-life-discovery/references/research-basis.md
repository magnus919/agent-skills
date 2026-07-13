# Research Basis

This skill is a practical synthesis, not a clinical protocol. The sources below shaped its question design, pacing, personalization, agency, and memory boundaries. Accessed 2026-07-13.

## Evidence and design signals

1. **PITCH: Designing Agentic Conversational Support for Planning and Self-reflection** (ACM CUI)
   https://dl.acm.org/doi/10.1145/3719160.3736634
   A two-week field study with 12 graduate students found value in morning planning and evening reflection. It also reported wear-out over time: variation alone did not solve the problem, and participants preferred contextually grounded consistency over arbitrary topic rotation. The skill therefore adapts to the person's context and stops when enough signal exists rather than rotating through a fixed questionnaire.

2. **Reflection in Theory and Reflection in Practice** (CHI, 2022)
   https://dl.acm.org/doi/10.1145/3491102.3501991
   An analysis of 123 personal-informatics apps found that support for reflection was uneven. This motivates treating reflection as an interaction design problem: prompt at the right level, connect reflection to concrete experience, and provide a path from insight to action without forcing action.

3. **Designing for Workplace Reflection** (DIS, 2018)
   https://dl.acm.org/doi/10.1145/3196709.3196784
   The Robota conversational agent supported activity journaling and self-learning through reflection. It supports using conversational recall and guided questions rather than relying on a blank journal prompt.

4. **Embodied Conversational Agents Providing Motivational Interviewing to Improve Health-related Behaviors** (scoping review, 2024)
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10746972/
   Motivational interviewing contributes four useful conversational moves: open questions, affirmations, reflections, and summaries. Its principles include empathy, rolling with resistance, supporting self-efficacy, and emphasizing autonomy. This skill borrows the interaction pattern for general reflection, not the clinical claims or health intervention scope.

5. **The Personalization of Conversational Agents in Health Care** (systematic review, JMIR, 2019)
   https://www.jmir.org/2019/11/e15360
   Personalization can be explicit, implicit, or ongoing and can improve relevance, satisfaction, efficiency, and behavior-change outcomes. The skill favors explicit confirmation for durable memories and ongoing correction instead of silently turning every inference into a user model.

6. **How Users Perceive Mixed-Initiative AI** (IUI, 2026)
   https://arxiv.org/html/2602.01481v1
   Assistance timing changes perceived helpfulness and agency. On-demand help preserves control; proactive help can reduce burden but can intrude when intent or attention is misread. The skill therefore asks about preferred initiative and uses user-controlled boundaries for check-ins and actions.

7. **Towards Ethical Personal AI Applications: Practical Considerations for AI Assistants with Long-Term Memory** (arXiv, 2024)
   https://arxiv.org/html/2409.11192v1
   Long-term memory can personalize assistance, but data acquisition, processing, storage, and use require lifecycle management for privacy and security. The skill separates what was said from what was inferred and asks before saving sensitive or durable information.

## Synthesis

The strongest portable pattern is a bounded, adaptive conversation with five properties:

- Start with consent and the desired outcome, not an interrogation script.
- Ask about concrete recent episodes, then abstract recurring patterns.
- Use open questions, reflections, affirmations, and summaries, but avoid turning the exchange into therapy.
- Make initiative configurable: the person chooses whether the agent should notice, remember, prompt, prepare, act, or only explore.
- Close with a small reversible experiment and a reviewable memory summary.

The evidence is promising but limited. Several studies are small, domain-specific, or short-term. The skill must not promise improved well-being, productivity, or behavior from conversation alone. The agent should treat each proposed opportunity as a hypothesis to test with the person.
