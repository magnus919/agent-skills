# Advisory content review: job-interview-coaching

Reviewer kind: `model_teacher`. Model ID: `not exposed by runtime`. This is a bounded advisory model review, not human adjudication, independent ground truth, or release approval. Repository files were not modified. No external provider, browsing, or task rerun was used.

## Material finding

**P2 — The worked factual rewrite imports timing from a different incident.**

File: `references/transcript-worked-case.md`.

- Lines 75–77 advertise a stronger answer “using only supplied facts,” then assert: “A volunteer could not cover a shift shortly before a rota was finalized.”
- The source incident at line 21 (T06) says only: “A volunteer could not cover a shift. I checked the current rota and called two people who had said they could cover.” It does not establish when the absence became known or proximity to finalization.
- The only nearby deadline is in a different example, T12 at line 33: the candidate was checking a rota while handling an expenses question and finished the rota because “the lead was about to send it.” The record never establishes that this is the same event as T06.

Why it matters: the skill's central factuality rule is to rewrite only confirmed facts (SKILL.md lines 73, 79, 83, 103; transcript-analysis.md line 52). The substantial worked example teaches that rule by demonstration. Adding urgency can materially strengthen a candidate's example and invites the very cross-incident embellishment the skill rejects. The synthetic nature of the record does not remove the fidelity requirement for a purported factual rewrite.

Suggested fix: begin the rewrite “A volunteer could not cover a shift. I checked the current rota…” Remove “shortly before a rota was finalized” unless the source record explicitly supplies it. Preserve the original action sequence (“I told the group lead and updated the shared sheet”) rather than reversing those actions in the rewrite if sequence has not been clarified. The timing addition is the substantive defect; the order reversal is a secondary fidelity concern because the source's conjunction alone does not prove strict chronology.

Suggested focused challenge: present two different incidents where only one has a deadline. Require a rewrite of the other that preserves its facts without borrowing urgency. Review the resulting text for event attribution, rather than merely looking for “do not invent” wording.

## Coverage of the original goal

The requested functionality is substantially present in the inspected content:

- **Practitioner research and reference materials:** practitioner-methods.md lines 7–17 compares seven named public approaches; lines 29–42 distinguish guides, books, course outlines, and actual reading status. It explicitly excludes a private-session or industry-wide survey claim. research-evidence-and-design.md lines 7–17 separates empirical designs and access limits, and lines 27–41 maps evidence to authored procedures without claiming demonstrated hiring efficacy.
- **Candidate and interviewer coaching:** SKILL.md lines 81–97 gives distinct modes. interviewer-coaching.md lines 5–36 covers role analysis, neutral probing, administration, independent rating, candidate conditions, and debrief. assessment-and-calibration.md lines 5–38 separates evidence, criteria, and accountable hiring decisions.
- **Substantial transcript critique:** transcript-analysis.md lines 48–54 requires whole-sequence review, counterexamples, prioritization, and transfer exercises. transcript-worked-case.md lines 11–71 supplies a substantial synthetic record and review accounting for later probes, shared credit, and bounded outcomes. The finding above concerns factual fidelity within its rewrite, not absence of transcript functionality.
- **Full practice cycles:** practice-and-feedback.md lines 7–23 distinguishes coached and simulation timing; lines 53–66 provides baseline, retrieval, assisted practice, independent variation, realistic round, and close. coaching-diagnosis.md lines 5–15 supplies competing explanations and discriminating checks; lines 38–48 keeps interventions bounded and framework choice task-dependent. A few one-turn trials cannot establish whether an agent sustains these cycles across real conversations, but the instructions are present.
- **Profession adaptation:** trades-maintenance-interviews.md lines 7–21 and 33–47 distinguish apprentice learning from qualified diagnosis and require actual standards for safety correctness. education-interviews.md lines 7–21 and 33–47 addresses lesson briefs, checks for understanding, adaptation, reflection, and subject review. software-interviews.md lines 7–21 and 33–47 distinguishes code, design, troubleshooting, conceptual claims, and executed checks. leadership-interviews.md lines 7–21 and 33–47 addresses mandate, authority, tradeoffs, shared credit, and differing IC/management scope. These are coaching playbooks, not exhaustive professional curricula; that boundary is explicit in SKILL.md line 66.
- **Seniority and generality:** responsibility-levels.md lines 3–25 uses actual scope rather than titles, includes first-job through executive paths, and treats IC seniority separately. SKILL.md lines 19–21 and 83 permits user-supplied context and noncorporate evidence; inspected files have no dependency on the author's identity, résumé, prior conversations, or private context.

## Routing and source boundaries

The SKILL.md routing table includes the reviewed mode, research, diagnosis, worked example, and focused profession files. All Markdown local links in this skill resolved in a local existence check. Named alternative skills `workflow-architect`, `product-discovery`, and `org-design` exist in the checkout. No dead routing target was found.

The content responsibly labels original synthesis and scenarios, recognizes commercial descriptions as limited evidence, and explicitly says when books or full texts were not read. Research references distinguish observations, design hypotheses, and efficacy claims. I found no additional material internal overclaim in those boundaries.

This review did **not** independently retrieve the cited sources, authenticate the recorded reading status, verify bibliographic summaries against the originals, or confirm the research dates. Consequently it cannot endorse external-source accuracy merely because the source matrix is carefully qualified. That is an evidence-verification limit, not proof a citation is wrong.

## Remaining evidence limits

No model content review or small synthetic trial establishes real coaching efficacy, independent skill transfer in candidates, reliability across professions, fair hiring outcomes, clinical/trade competence, psychometric validity, or effects on offers and job performance. The skill mostly states these limits itself (SKILL.md lines 66, 97, 105; research-evidence-and-design.md lines 37–41). These should not be converted into missing-functionality findings or release-pass claims.

The review read SKILL.md; practitioner-methods.md; coaching-diagnosis.md; research-evidence-and-design.md; transcript-worked-case.md; the four required focused profession playbooks (trades, education, software, leadership); practice-and-feedback.md; transcript-analysis.md; responsibility-levels.md; interviewer-coaching.md; and assessment-and-calibration.md. It did not audit every other focused profession playbook, reproduce all source research, or perform longitudinal interactive trials.

## Follow-up review: corrected rewrite and unfamiliar-profession routing

Provenance remains `reviewer_kind: model_teacher`, `model_id: not exposed by runtime`; this follow-up is advisory. Re-read the current T01–T22 record, revised factual rewrite, new unfamiliar-professions.md, and SKILL.md routing. No repository edits, provider calls, or source retrievals were performed.

**Original material finding: RESOLVED.** The current transcript-worked-case.md line 77 starts “A volunteer could not cover a shift” and no longer asserts proximity to rota finalization. Each remaining substantive detail is supported by T06 (line 21: checking rota, contacting two potential replacements, one agreement, informing lead, updating sheet, teammate contacting organizer), T08 (line 25: lead's second-hand confirmation and absence of personal attendance checking), or T10 (line 29: candidate's suggestion, lead's adoption decision, another person's maintenance). The rewrite does not borrow urgency from T12. “Offered to cover” is a reasonable paraphrase of “had said they could cover”; adoption is supported by both the decision and subsequent use of the column. No further material unsupported detail found.

The previously noted action-order difference remains (“updated the sheet and informed the lead” versus “told the group lead and updated the shared sheet”). Neither uses explicit before/after language for those two actions, so I do not classify this as a remaining factual contradiction or release-blocking defect. Preserving source order would still be an optional fidelity improvement. Omitting the separate boundary about approving new volunteers shortens the summary without falsely claiming that authority.

**New unfamiliar-profession method: no material finding.** SKILL.md line 64 explicitly routes unfamiliar professions, ambiguous titles, and cross-field tasks to the existing new file. Its instruction fits the general technical-standard boundary at SKILL.md line 67.

- unfamiliar-professions.md lines 7–9 starts from actual role artifacts, tasks, supervision, and entry expectations; it limits generic occupational sources and requires local standards for technical/regulatory judgments.
- Lines 13–22 offers evidence/task families, explicitly labeling musician/agricultural examples as plausible adaptations rather than researched universal hiring formats.
- Lines 26–28 requires realistic context and provisional criteria, and expressly prevents generic behavioral questions replacing required auditions or practical assessments.
- Lines 32–34 separates observable explanation quality from specialist correctness, uses “not assessed,” and calls for domain-owner review of realism, alternatives, safety, and anchors. This is a coherent adaptation process rather than an invented specialist answer key.
- Lines 38–40 tests whether feedback concerns actual work, seeks representative tasks when it remains generic, and supplies an observable completion condition with explicit limits.

No additional material defect identified within this follow-up scope. A live unfamiliar-profession trial would still be needed to assess whether an agent follows the method effectively; text coherence alone does not establish specialty coverage, technical correctness, successful transfer, or real coaching benefit. Original evidence limits and the original finding above are retained as historical review evidence.
