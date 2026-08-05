# dsm5

An evidence-based companion to the DSM-5-TR for serious conversations about mental
health and neurocognitive conditions.

## Why Install This Skill

Mental health questions are everywhere, and most answers online are vibes, not
criteria. This skill grounds those conversations in the real diagnostic framework of
the DSM-5-TR (text revision) so that "could this be X?" becomes a structured
comparison — symptoms weighed against actual criteria, with met, unmet, and unknown
kept separate — instead of a guess. It was built from a copy of the DSM-5-TR text
revision and organized as a searchable reference library, with safety handling and
calibrated language built into every answer.

Who it is for: clinicians and practitioners double-checking criteria, specifiers, or
differentials; patients and family members who want an evidence-based understanding
of a condition and good questions to take to a provider; and anyone who needs to
explain a mental health topic accurately and without stigma.

What it is not: it is not a diagnostic tool, it does not render "you have X"
verdicts, it gives no treatment or medication advice, and it is not the manual
itself. It is a paraphrased companion for orientation and education, and it always
says so.

## What You Get

| Item | What it provides |
|---|---|
| `SKILL.md` | The conversation workflow: safety triage first, question/audience clarification, reference routing, criteria comparison, differential reasoning, and calibrated communication. |
| `references/00-overview-and-method.md`, `01-safety-and-boundaries.md`, `02-assessment-and-differential.md` | Foundation files: how the DSM-5-TR is organized and how to read a diagnosis, the skill's scope and crisis protocol, and how a clinical assessment and differential are structured. |
| `references/10`–`31` | Per-chapter references for every DSM-5-TR diagnostic class — criteria, specifiers, ICD-10-CM codes, prevalence, onset, course, and differential sections — with extra depth on neurocognitive and deficit conditions. |
| `references/32`–`33` | Part III material: assessment measures and cultural formulation, plus the Alternative DSM-5 Model for Personality Disorders and conditions for further study. |
| `references/40-cross-cutting-differentials.md` | Overlapping-symptom comparisons across conditions, for questions that span chapters. |
| `scripts/lookup.py` | A keyword search across every reference file — finds where a topic lives and which files to read first. |
| `evals/evals.json` | Output-quality test cases that keep the skill's answers honest across safety, criteria fidelity, and plain-language scenarios. |

## Quick Start

No setup, no API keys, no dependencies. Two ways to use it:

- **Browse by chapter.** Open `references/` and pick the file for the condition in
  question (for example, `13-depressive-disorders.md` for depression).
- **Search by keyword.** Find where any topic lives:

  ```sh
  python3 scripts/lookup.py 'insomnia'
  ```

  The script prints matching lines grouped by file and a short list of the best
  reference files to read. Add `--list` to see every reference file with its
  one-line description, or `--json` for machine-readable output.

## Triggers

Load this skill when someone asks about:

- What a set of symptoms "could be" or whether a description matches a known
  condition.
- Diagnostic criteria, specifiers, or codes for a mental health condition.
- The difference between two conditions (for example, ADHD vs. anxiety, or delirium
  vs. dementia).
- How common a condition is, when it starts, or how it typically runs its course.
- A plain-language explanation of a diagnosis for a patient or family member.
- What questions to bring to a clinician or therapist.

## Requirements

- Python 3 (standard library only) if you want to use `scripts/lookup.py`.
- The reference files, which ship with the skill — no downloads needed.
- For exact verbatim criteria, codes, and recording procedures, consult the official
  DSM-5-TR (the user's copy). This skill is a companion, not the authoritative text.

DSM-5-TR is © American Psychiatric Association (2022). This skill is an independent
companion reference; it paraphrases and summarizes the manual for orientation and
education and is not a substitute for the manual, for clinical training, or for
professional evaluation. Always verify criteria and codes against the official
DSM-5-TR before formal use.
