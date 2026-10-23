# Job interview coaching: research and skill blueprint

Research pass: 2026-10-23. Status: research foundation and implemented prototype; independent behavioral and domain validation remains incomplete.

The intended skill helps candidates demonstrate their actual capabilities and helps interviewers obtain useful, comparable evidence while giving candidates a respectful experience. It should work for a first job, a skilled trade, a professional specialty, or an executive appointment. No personal interview material was used in this research.

## Recommendation

Create one methodology skill, provisionally **job-interview-coaching**, with a shared evidence model and separate candidate and interviewer modes. Route by the user's purpose, then by occupation, responsibility level, interview format, and available artifacts. Avoid separate skills for each profession: the shared workflow is substantial, and profession-specific differences belong in conditional references.

The most valuable feature should be an evidence-to-practice loop: identify a specific difficulty, show its evidence, explain its consequence, practise a targeted change, and test it on a different question. A polished rewritten answer alone does not demonstrate learning.

## Read this dossier

| Document | Contents |
|---|---|
| [Methods and workflows](methods.md) | What a coach does; candidate preparation, transcript critique, mock interviews, interviewer design and debrief |
| [Coverage and architecture](coverage-and-architecture.md) | Profession and seniority matrix, reference plan, routing, templates, acceptance cases |
| [Initial validation](validation.md) | Two model-generated forward trials and explicit untested areas |
| [Sources and research gaps](sources.md) | Annotated primary-source ledger, access limitations, evidence strength, further research priorities |

## Findings that should shape the skill

1. **Start with the work.** Interview criteria should connect to real responsibilities; candidate examples should answer the actual question. OPM's structured-interview guidance provides a practical foundation. [S01]
2. **Separate interview formats.** Behavioral examples, hypothetical situations, technical demonstrations, business cases, portfolios, and teaching demonstrations reveal different evidence. Employer and professional guidance confirms these differences; one answer formula cannot cover them all. [S04, S07–S10]
3. **Coach a person, not a script.** Establish a useful goal, listen, invite self-assessment, and agree a next action. ICF provides general coaching standards, while national careers guidance supports conversational preparation. Neither proves that an AI coach improves hiring outcomes. [S05, S06]
4. **Assess what is observable.** A transcript can show relevance, reasoning, specificity, ownership, and questions asked. It cannot reliably establish body language, vocal delivery, honesty, personality, or likely hiring decisions. This is a proposed evidence boundary for the skill.
5. **Interviewer experience and candidate experience belong together.** Clear expectations, accessible arrangements, job-related questions, disciplined probing, and independent ratings can support both. Canada's detailed guide provides operational examples; its page is under review and its legal context needs refreshing. [S02]

Source IDs resolve in [the source ledger](sources.md). All uncited workflow designs and matrices in this dossier are proposed synthesis, not validated coaching protocols.

## What this pass establishes

There is enough grounded material to design the shared workflow and begin a prototype. There is not yet enough profession-specific research or independent behavioral evidence to claim world-class coverage. Strong initial sources cover structured interviewing, behavioral preparation, technical interviews, consulting cases, academic interviews, and residency selection. Trades, frontline work, education, creative practice, legal practice, and jurisdiction-specific requirements need deeper research before specialist references are presented as authoritative.

The local catalog contains `workflow-architect/skills/interviewer`, which discovers repeatable workflows. That is a different purpose. The proposed skill should explicitly exclude stakeholder research, journalism, workflow discovery, and general application writing. `org-design` remains the owner of organization design; `life-coach` covers broader life goals. Installed personal career skills should not become dependencies for a portable catalog skill.

## Further validation and research

1. Close the highest-risk source gaps and capture claim-level notes with limits.
2. Author the shared coaching workflow, mode-specific references, and representative profession packs.
3. Build the transcript worksheet, interview-plan template, practice log, and output-quality eval manifest together.
4. Challenge the prototype with realistic transcripts and multi-turn mocks across professions and responsibility levels. Include near misses and missing evidence; preserve failures.
5. Validate repository structure and eval schema separately from behavior. Review sample outputs with experienced interview coaches, hiring practitioners, and domain specialists before making quality or outcome claims.

The prototype is now cataloged as `job-interview-coaching`. This dossier preserves the reasoning and evidence limits; it is not a behavioral-validation report.
