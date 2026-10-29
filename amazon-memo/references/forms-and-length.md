# Choose the form and the reading budget

These routing and budgeting choices are recommendations unless a source or a local
rule is identified. Begin with the decision and audience, not with a page target.

## Forms that solve different problems

**Decision or strategy narrative.** Explain why a change is needed, the evidence,
alternatives, recommended mechanism, resource commitment, and consequences. A staffing
proposal usually belongs here: the reader must compare capacity, sequencing, cost,
and alternatives, not read an imaginary launch announcement. For planning-cycle
documents, add goals, lessons, and priorities only when they help the choice.

**PR/FAQ.** Explore a future customer experience before committing to build it.
The release communicates the problem and benefit in customer language. The customer
FAQ addresses use, limits, price, and trust. The internal FAQ confronts demand
evidence, feasibility, economics, dependencies, risks, alternatives, and validation.
AWS describes a single-page future press release; that does not mean the entire
PR/FAQ is one page. A process proposal can use this form when the future user
experience is the central uncertainty. A routine process approval may need only a brief.

**Short decision brief.** For one bounded choice, start with the ask, concise context,
options, recommendation, downside, and next checkpoint. A one-page target is a useful
adaptation, not an established universal Amazon template. If the decision is trivial,
use a clear message rather than generating a ceremonial memo.

**Other patterns.** A business review needs metric definitions, periods, variance,
drivers, and actions; a narrative should explain the numbers rather than bury them.
An incident report needs impact, timeline, contributing conditions, and accountable
follow-up. A design document needs interfaces, constraints, failure modes, and review.
An ADR preserves context, decision, consequences, and alternatives. A procedure must
remain executable. Route detailed domain work to the owning skill; do not recast
every document as a strategy memo or PR/FAQ.

## Length is a constraint, not a quality target

Amazon's 2024 Jassy letter establishes a maximum six-page narrative. It does not
establish exactly six pages or a fixed word budget. Bryar and Carr recommend up to
six body pages with 15–20 minutes reading in a one-hour meeting, or up to three
pages with 7–10 minutes reading in a half-hour meeting. This is practitioner guidance,
not a universal Amazon timetable. Their appendix allowance is not a place to hide
material costs or risks.

For a local 20-minute review, a short brief plus a small evidence appendix may be
more useful than a six-pager. As an illustrative planning split, reserve about five
minutes for reading, twelve for the consequential disagreement, and three to record
the decision. Revise that split for reader familiarity, accessibility, numeric density,
and the stakes. An async window may remove the meeting entirely.

Choose the shortest draft that retains enough context and evidence for the reader
to challenge the decision. If asked for six pages with only two pages of substance,
deliver a concise draft and explain the unused ceiling. If a hard local minimum
exists, ask for the missing analysis; do not fill space with repetition.

Word counts can help plan effort. If using a reading-rate estimate, state the assumed
rate and call it a rough estimate; tables, unfamiliar concepts, and checking evidence
take additional time. Word count does not measure comprehension. Prefer a timed
read by a representative reader before an important review.

For actual pages, agree on paper size, readable type, margins, line spacing, headers,
and whether appendices count. Render and inspect the document after changes.
Until then say “draft intended for about two pages; pagination unverified.” Do not
equate a Markdown page break, token count, or fixed words-per-page rule with proof.

## Adaptation without invented lineage

Keep Amazon-specific labels when requested, but borrow only mechanisms that fit
the local team. The following independent practices are documented in the source
index; none is claimed here to descend from Amazon.

| Local context | Useful adaptation | Boundary |
|---|---|---|
| GitLab architecture review | Living design document, named DRI, explicit review roles and deadlines; begin small and elaborate as needed | No universal six-page cap; preserve technical design and ADR requirements |
| Basecamp Shape Up pitch | Problem, appetite, solution, rabbit holes, no-gos; allow helpful sketches and async comments before betting | Appetite is willingness to spend time, not a completion estimate; six weeks is not document length |
| Coinbase operational choice | Lightweight Problem/Proposed Solution for routine issues; stronger decision ownership and RAPID for consequential cross-functional choices | Its 2021 post describes one-page averages and sub-15-minute drafting targets, not absolute limits; credits other influences |
| Automattic async work | Durable discussion and decision record with shared facts, assumptions, owner and outcome | A specialty team's project brief is not a company-wide memo template |
| Netflix context and accountability | Commentable context, solicited dissent, accountable informed captain, later reflection | No verified universal operational template, six-page cap, or silent-reading rule |

When a user requests a named company's format without providing a local template,
use the verified mechanisms and label the resulting scaffold as an adaptation.
Do not invent that company's headings, approval rules, or origin story.
