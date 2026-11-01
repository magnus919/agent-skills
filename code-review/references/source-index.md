# Source index

Sources behind the claims in this skill, with what each supports and its
limitations. Retrieved 2026-11-01.

## Primary engineering guidance

**Google, "The Standard of Code Review"**
https://google.github.io/eng-practices/review/reviewer/standard.html
Supports: the standard that reviewers favour approval once a change definitely
improves overall code health; the "Nit:" convention; technical facts over
opinions; style guide as authority; conflict resolution and escalation.
Limits: Google's internal practice and culture; prescriptive, not empirical.

**Google, "What to look for in a code review"**
https://google.github.io/eng-practices/review/reviewer/looking-for.html
Supports: the review content categories (design, functionality, complexity, tests,
naming, comments, style, consistency, documentation), the "review every line" norm
with explicit exceptions, reading context beyond the diff, and praising good work.
Limits: as above; assumes a monorepo with owners and style guides.

**Google, "Speed of Code Reviews"**
https://google.github.io/eng-practices/review/reviewer/speed.html
Supports: one business day maximum first response; response time matters more than
total process time; "LGTM With Comments"; ask for large changes to be split;
emergencies are narrowly defined.
Limits: as above.

**Google, "How to write code review comments"**
https://google.github.io/eng-practices/review/reviewer/comments.html
Supports: comment on code not the developer; explain why; balance direction against
pointing out problems; label severity (`Nit:`, `Optional`/`Consider`, `FYI`);
explanations belong in the code, not only in the review thread.
Limits: as above.

## Empirical studies

**Bacchelli & Bird (2013), "Expectations, Outcomes, and Challenges of Modern Code
Review", ICSE 2013.** PDF: https://sback.it/publications/icse2013.pdf
DOI: https://doi.org/10.1145/2486788.2486882
Method: 17 developers observed and interviewed across 16 Microsoft product teams,
165 managers and 873 programmers surveyed, 570 review comments manually classified.
Supports: defect comments are a minority (78/570, 14%) and mostly micro-level;
understanding is the dominant review challenge; 91% say unfamiliar files take
longer; 82% say file owners give deeper comments; review outcomes include knowledge
transfer and team awareness beyond defect finding.
Limits: single company, hand-classified comment sample, self-reported survey data;
authors state they cannot discuss relative frequencies from interviews.

**Sadowski, Söderberg, Church, Sipko & Bacchelli (2018), "Modern Code Review: A
Case Study at Google", ICSE-SEIP 2018.** PDF:
https://sback.it/publications/icse2018seip.pdf
DOI: https://doi.org/10.1145/3183519.3183525
Method: logs for about 9 million changes (Jan 2014 – Jul 2016), 13 million
comments, 12 interviews, 44 survey responses.
Supports: median 24 lines changed; fewer than 25% of changes have more than one
reviewer (median 1); 70% of changes committed within 24 hours; reviewers average
3.2 hours/week (median 2.6); comments per change peak at 12.5 around 1,250 lines;
about 30% of changes have comments from more than one commenter; code review is
valued (all survey respondents) and satisfaction is high (97% for the tool); size
drives latency and comment quality; reviewer recommendation prioritizes recent
editors/reviewers of the files.
Limits: single company and a monorepo with unusual tooling; the authors enumerate
threats to validity, including transferability.

**Rigby & Bird (2013), "Convergent contemporary software peer review practices",
FSE 2013.**
Supports (as summarized in Table 1 of Sadowski et al.): five convergent practices —
lightweight process, early and frequent reviews, small change sizes, two reviewers
finding an optimal number of defects, and review as group problem solving.
Limits: this skill did not re-read the original paper; the summary and the
comparison with Google's divergence on reviewer count come from Sadowski et al.

## Vendor research

**SmartBear, "Best Practices for Code Review"** (study of a Cisco Systems team)
https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/
Supports: review 200-400 LOC at a time; 70-90% defect discovery for a 200-400 LOC
review over 60-90 minutes; inspection under 500 LOC/hour; sessions under 60
minutes; lightweight review under 20% of formal inspection time with comparable
defect finding; checklists help with omissions; defect metrics must not be used in
performance reports.
Limits: marketing content describing a single-company case study; no peer review,
no published confidence intervals. Its thresholds are widely repeated as fact and
should be treated as practice defaults, not established constants.

## AI-assisted review

**Cihan, Haratian, İçöz, Gül, Devran, Bayendur, Uçar & Tüzün (2024), "Automated
Code Review In Practice", ICSE SEIP 2025.** https://arxiv.org/abs/2412.18531
Method: industrial deployment of an LLM-based review tool (Qodo PR Agent based)
across 10 projects with about 238 practitioners; 3 projects analyzed with 4,335
pull requests, 1,568 automatically reviewed; PR data, per-PR surveys, and a
22-practitioner survey.
Supports: 73.8% of automated comments resolved; average PR closure time rose from
5h52m to 8h20m; most practitioners report a minor quality improvement; drawbacks
include faulty reviews, unnecessary corrections, and irrelevant comments.
Limits: one organization, three projects analyzed; resolution is a proxy for
usefulness, not precision.

**Zeng et al. (2025), "SWR-Bench: Assessing LLM Performance in Real-World Code
Review Comment Generation".** https://arxiv.org/abs/2509.01494
Method: 1,000 manually verified pull requests with full project context; LLM-based
evaluation aligned with human judgment at about 90% agreement.
Supports: current automated review tools and LLMs underperform on realistic review;
tools are more adept at functional errors; multi-review aggregation raises F1 by up
to 43.67%.
Limits: benchmark results, not deployment outcomes; the evaluation itself uses an
LLM judge.

**Alshahwan et al. (2024), "Automated Unit Test Improvement using Large Language
Models at Meta", FSE 2024.** https://arxiv.org/abs/2402.09171
Supports: 75% of generated test cases built correctly, 57% passed reliably, 25%
increased coverage; 11.5% of targeted classes improved; 73% of recommendations
accepted for production after filtering for measurable improvement.
Limits: generated tests target coverage improvement of existing human-written
tests; acceptance reflects a filtered candidate set.

## Not relied on, worth reading

- Fagan (1976), "Design and code inspections to reduce errors in program
  development", IBM Systems Journal — the origin of formal inspection; useful for
  understanding why modern review is deliberately lighter, but its defect rates do
  not transfer to tool-based review.
- Czerwonka, Greiler & Tilford (2015), "Code Reviews Do Not Find Bugs", ICSE-SEIP —
  a Microsoft argument that review's defect-finding reputation is overstated and
  that best-practice guidance can slow teams down. Cited in Sadowski et al.; this
  skill did not independently review the paper.

## How to use this index

When a claim in this skill matters to a decision, cite the source and, more
importantly, the *kind* of source: peer-reviewed study, company case study, vendor
research, or engineering convention. The distinction is usually more informative
than the number itself.
