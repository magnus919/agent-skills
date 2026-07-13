# Interaction Pattern Selection

Patterns are reusable hypotheses, not prescriptions. A familiar component can still be wrong for the task, risk, frequency, data shape, permission model, platform, or recovery requirement.

## Decision Record

For every consequential pattern, record:

1. the user goal and context;
2. forces: frequency, urgency, reversibility, data volume, uncertainty, comparison, permissions, connectivity, interruption, and accessibility;
3. plausible alternatives, including a simpler native interaction;
4. tradeoffs and failure modes of each alternative;
5. supporting and disconfirming evidence;
6. the selected approach, owner, assumptions, and revisit trigger.

Do not present a design-system example as proof. If no evidence distinguishes alternatives, name the choice as provisional and define the observation that would change it.

## Common Pattern Forces

| Pattern family | Questions that determine fit |
|---|---|
| Forms and validation | When can validity be known? Is input preserved? Can errors be associated, summarized, and corrected without losing context? |
| Search and filtering | Is the person locating, exploring, comparing, or narrowing? How are active filters, zero results, stale results, saved views, and re-entry handled? |
| Dense tables and dashboards | Which comparisons and actions matter? What does sorting, truncation, horizontal movement, personalization, or narrow width do to meaning? |
| Onboarding and guidance | Is instruction needed before action, at the decision point, or only after failure? Can experienced users bypass it? |
| Disclosures and progressive detail | Is hidden information nonessential to the current decision? Is the reveal discoverable, reachable, stateful, and safe? |
| Destructive or consequential actions | Is the effect reversible, delayed, repeated, or rare? Would confirmation, typed intent, preview, undo, delayed commit, or approval reduce the actual risk? |
| Autosave and optimistic update | What is the commit boundary? How are pending, failed, conflicting, offline, and restored states communicated? |
| Pagination, load-more, and streaming | Is the task exploration, exhaustive review, comparison, return-to-position, or audit? How are total, order, updates, failure, and re-entry represented? |

## Tradeoff Examples

- Confirmation can reduce accidental irreversible action, but repeated confirmations can become automatic dismissal. Prefer a risk-matched barrier and preserve a recovery path where the domain permits it.
- Undo can improve recovery, but only when retention, authorization, synchronization, and user-visible time boundaries make restoration real.
- Infinite scroll can support exploration, but it can weaken location, comparison, footer access, completion sense, and re-entry. Pagination or load-more may fit bounded review better.
- Optimistic updates can improve perceived responsiveness, but they require truthful pending/failure/conflict behavior and must not imply a side effect committed when it did not.
- Wizards can sequence complex dependencies, but may hide overview, make branching awkward, and complicate interruption. A reviewable single flow or staged checklist may be better.

## Evidence and Revisit Gate

Use authorized task evidence, support/search data, domain constraints, accessibility evidence, production failures, and implementation feasibility. Do not count preference alone as task success. Define a revisit condition such as a recurring recovery failure, unexpected permission path, inability to resume, or observed comparison burden.

GOV.UK and USWDS are useful rolling government examples, not universal standards. Link to their live guidance through `source-index.md`; do not copy a component or infer that government context matches the product.
