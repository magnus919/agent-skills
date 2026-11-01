# Evidence base: what code review research actually shows

This file separates measured findings from widely repeated folklore. Every claim
names its source; the full list is in the source index. Where the evidence is
vendor-produced, old, or contested, it says so.

The practical consequence for a reviewer: review is worth doing, but not for the
reason most teams state, and not at the scale most teams attempt.

## 1. Review is primarily about understanding, not defect detection

Bacchelli and Bird studied modern code review at Microsoft across 16 product
teams. They observed and interviewed 17 developers, surveyed 165 managers and 873
programmers, and manually classified 570 review comments from 200 comment threads.

Their central finding: **finding defects is the top stated motivation, but the
outcome does not match the expectation.** Defect comments were the fourth most
frequent of nine categories — 78 of 570 comments (14%). Of those, 65 concerned
logic issues (a wrong expression, an unhandled corner case), 6 high-level design
issues, 5 security, and 3 exception handling. Most comments concerned code
improvements and understanding.

Understanding was the dominant challenge. 91% of surveyed developers said
reviewing unfamiliar files takes longer, because "big-picture impact analysis
requires contextual understanding"; 82% said reviewers who own the changed files
give deeper comments — "more likely to find subtle defects, feedback is more
conceptual … instead of superficial".

**What this supports:** the review method in this skill spends its first move on
intent and context, and treats understanding questions as first-class findings
rather than noise. It also supports a modest claim about defects: a review that
looks only for bugs will miss what review is actually good at.

**What it does not support:** any defect-detection rate. The comment sample is
570 comments from one company, classified by hand; the authors explicitly flag the
sample size and single-company setting.

## 2. Review at Google is small, single-reviewer, and fast — and still valued

Sadowski, Söderberg, Church, Sipko, and Bacchelli analyzed review logs for
approximately 9 million changes at Google between January 2014 and July 2016,
produced by more than 25,000 authors and reviewers, plus 13 million comments, 12
interviews, and a 44-response survey.

Measured characteristics:

| Property | Measured value |
|---|---|
| Changes per workday | about 20,000 |
| Median lines modified per change | 24 |
| Changes with more than one reviewer | fewer than 25% |
| Median reviewer count | 1 |
| Changes committed within 24 hours of being mailed | 70% |
| Average reviewer time | 3.2 hours/week (median 2.6) |
| Average comments per change | peaks at 12.5 for changes of about 1,250 lines |
| Changes with comments from more than one commenter | about 30% |

The authors attribute the speed to culture, small changes, and single-reviewer
reviews, and note that size is a known driver of both latency and comment quality:
prior studies found useful comments decrease and latency increases as change size
grows. All 44 survey respondents agreed code review is valuable; 97% were
satisfied with the tool.

**What this supports:** the size and budget defaults in this skill (hundreds, not
thousands, of effective lines; one accountable reviewer; fast first response) are
not aspirational — they describe the practice at one of the largest review
pipelines in existence. It also supports treating "no comments besides the
approval" as a normal outcome rather than a sign of a careless reviewer.

**What it does not support:** copying Google's numbers as targets. Theirs is a
monorepo with owner-based approval, strong tooling, and a specific culture; a
regulated medical-device codebase needs a different tiering. The paper is a case
study, and its own threats-to-validity section says so.

## 3. Size and pace limits: vendor evidence, useful but not peer-reviewed

SmartBear's widely cited guidance, derived from a study of a Cisco Systems
programming team, states:

- Review 200-400 lines of code at a time; beyond 400 LOC the ability to find
  defects diminishes.
- A 200-400 LOC review over 60-90 minutes should yield 70-90% defect discovery.
- Inspection rates above 500 LOC/hour show a significant drop in defect density.
- Do not review for more than 60 minutes in one sitting; performance drops after
  about an hour.
- Lightweight review takes less than 20% of the time of formal inspection and
  finds as many bugs; formal inspection averages about nine hours per 200 LOC.

This is the origin of nearly every "400 lines / 60 minutes / 500 LOC per hour"
number in circulation. Treat it as **vendor research**: a single-company case
study, published as marketing material, not peer-reviewed, with no published
confidence intervals. The direction of the effect is corroborated by the academic
findings above (size drives latency and comment quality); the precise thresholds
are not independently established.

**How this skill uses it:** the bundled scope tool plans at 300 effective LOC/hour
with a 60-minute session cap, and calls the result a *floor for attention*, not a
target. If your team's data disagrees, your data wins — but measure it.

## 4. Convergent practice across organizations

Rigby and Bird's cross-project analysis identified five practices that open-source
projects using email review, Gerrit, and Microsoft's CodeFlow converged on:

| ID | Practice |
|---|---|
| CP1 | Contemporary peer review follows a lightweight, flexible process |
| CP2 | Reviews happen early, quickly, and frequently |
| CP3 | Change sizes are small |
| CP4 | Two reviewers find an optimal number of defects |
| CP5 | Review has shifted from defect finding to group problem solving |

Google's data diverges on CP4: fewer than 25% of their changes have more than one
reviewer, and their median is one. Sadowski et al. posit that the single reviewer
is what keeps their reviews fast.

**What this means for reviewer assignment:** there is no universal correct number.
Two reviewers add perspective at the cost of latency and duplicated attention;
one reviewer with domain ownership plus a specialist for a sensitive area is a
defensible default. Assign for *knowledge*, not for headcount.

## 5. What review reliably misses

The empirical picture across both studies:

- Defect comments are a minority of review output and mostly concern "micro"
  logic issues — corner cases, operator precedence, common configuration values.
- Reviewers working outside their expertise produce shallower comments.
- Review does not substitute for tests: the reviewers in these studies were not
  executing the code as a rule, and Google's guide explicitly expects authors to
  have tested before review.
- Review happens before merge, so it cannot see production behavior, data volume,
  concurrency under real load, or dependency drift after the fact.

**Consequence:** a clean review is evidence that someone with context examined the
change, not evidence that the change is correct. Treat review and automated
verification as complementary controls with different blind spots, and say which
one produced your evidence.

## 6. AI-assisted review: real gains, real false positives, longer cycles

Measured in an industrial deployment (Cihan et al., ICSE SEIP 2025): 238
practitioners across ten projects; three projects analyzed with 4,335 pull
requests, 1,568 of which received automated LLM review. **73.8% of automated
comments were resolved**, but average pull-request closure time rose from 5h52m to
8h20m. Most practitioners reported only a minor quality improvement. Reported
drawbacks: faulty reviews, unnecessary corrections, and irrelevant comments.

Benchmark evidence (Zeng et al., SWR-Bench, 2025): on 1,000 manually verified
pull requests with full project context, mainstream automated review tools and
LLMs underperform; the tools are better at functional errors than other classes.
Aggregating multiple review passes raised F1 by up to 43.67%, which is a statement
about ensembles, not about any single reviewer.

Evidence on AI-generated tests (Alshahwan et al., Meta TestGen-LLM, FSE 2024): of
generated test cases, 75% built correctly, 57% passed reliably, and 25% increased
coverage; 73% of recommendations were accepted for production by engineers. The
tool filtered candidates against measurable improvement before proposing them —
which is why the accepted rate is high. An unfiltered generator would not have
that property.

**What this supports:** AI review output is a candidate list that needs human
triage; a high resolution rate does not imply high precision; and AI-generated
tests need an independent oracle, because a test derived from the patch can only
prove the patch agrees with itself.

## 7. Folklore, and what to do with it

| Common claim | Status |
|---|---|
| "Review finds 60-90% of defects" | Vendor figure for a specific inspection protocol, not a property of your process. Do not quote it as a guarantee. |
| "Two reviewers are always better than one" | Contradicted by Google's data; supported by cross-project convergence. Depends on change type. |
| "Checklists catch most defects" | Checklists help with *omissions of known categories*. They do not find unknown failure modes, and list-driven reviewers find fewer unlisted problems. |
| "More comments means better review" | Comments per change peak around 1,250 lines at Google and then fall — volume tracks size, not quality. |
| "Approval rate is a quality metric" | It measures reviewer leniency and queue pressure. |
| "AI review can replace a reviewer" | Measured precision and closure-time effects do not support it; accountability cannot be delegated to a model. |

## 8. Evidence quality, stated plainly

- Two of the strongest sources are single-company case studies (Microsoft,
  Google). Their internal validity is good; their generalizability is explicitly
  limited by their authors.
- The size/pace thresholds come from vendor research with no peer review.
- The AI-review evidence is recent, fast-moving, and mostly from a handful of
  industrial deployments and benchmarks. Numbers will move.
- None of these studies measures *your* codebase. The point of the evidence is to
  set defensible defaults and to justify measuring your own process, not to
  outsource judgment to a citation.

See the source index for URLs and what each source supports.
