# A checkpoint for research evidence sufficiency

Use this pattern when an agent produces research whose downstream use requires
more than a plausible answer. [Research methodology](../../research-methodology/SKILL.md)
owns what makes evidence credible and sufficient. This pattern implements a
durable checkpoint and stopping rule for decisions under a declared evidence bar.
A model can propose claim links and missing-evidence queries; it cannot mark
its own claims verified or decide that the report has been accepted.

## Record and screen before drafting

1. **Pin the material claim roster.** Give each claim an ID, scope, required
   primary evidence, and number or types of independent origins when warranted.
   Define an owner for unresolved contradictions and a follow-up budget covering
   requests, time, and cost. A publication hold is separate from retrieval success.
2. **Keep sources, relationships, and gaps separate.** Record retrieval status,
   timestamp, URL, snapshot revision, and original or derivative provenance on
   the source. A claim link records supports/contradicts, evidence locator,
   applicability and origin **for that claim**. A record may be captured without
   supporting anything. A proposed link or a high model score is not a reviewed
   link. Preserve rejected links and their reasons rather than deleting the audit
   trail. A correction affecting one claim need not invalidate unrelated evidence.
3. **Consolidate shared origins.** Count the underlying observation, study, audit,
   or accountable record, not websites, titles, or even separately quoted
   articles. Two independent editorial teams can still repeat one press release.
   If independence is unknown, preserve that status without counting it.
4. **Choose disposition.** A plausible unresolved contradiction goes to a
   reviewer with the exact competing evidence, even if numerically enough
   sources support the claim. A missing primary source or insufficient
   independence can motivate one targeted retrieval per gap if budget allows.
   Otherwise return incomplete plus the named gap. Clearing this checkpoint
   means ready for acceptance review, not verified world state or permission
   to publish. The acceptance owner checks the actual delivered report and its
   claim roster against the reviewed record.
5. **Make recovery bounded.** Persist the reviewed revision and reserve the
   candidate's stable operation ID and budget atomically before dispatch.
   Separately persist settled receipts. On restart, reconcile unsettled
   reservations before any repeat; a missing receipt is not proof nothing ran.
   Revalidate affected links if the source, brief, or verifier changed. Leave
   incomplete results present when budget expires.

## Worked example and reproducible exercise

A synthetic project claims that a neighborhood pilot cut outages by 30%.
A municipal announcement and its newspaper rewrite describe the same
measurement. Capturing both URLs does not add an independent origin. Before
verifying the underlying table against the population and date range, the
link from the proposed primary item is only a candidate. A utility record
showing a different outage definition produces a contradiction for review,
not an automatic average or a third vote.

From the skill directory, run the bundled offline challenges:

```sh
python3 -B -m unittest discover -s scripts -p test_research_checkpoint.py
```

The synthetic tests exercise redundancy, proposed versus reviewed support,
unknown origin, contradiction, missing or stale capture, readiness versus
acceptance, and a restored budget reservation. The checker is a read-only
example; it trusts caller-provided reviewer decisions and origin labels, does
not fetch or verify evidence, does not create real reservations or guarantee
atomicity, and never approves publication. The runtime must protect the
review ledger from the drafting agent's writes. Test the real integration by
interrupting after a dispatched retrieval but before its receipt is recorded,
then observe reconciliation and budget accounting across restart.

## Evidence and boundaries

- [Diogo Almeida’s CODE Summit talk, 15:22](https://www.youtube.com/watch?v=Cyt3LU8TyNc&t=922s)
  argues for decomposing automated work into verifiable stages and managing
  state explicitly. The organizer’s posted talk and its transcript informed
  the question; they do not validate this checkpoint. Inspected November 20, 2026.
- [W3C PROV-DM, derivation](https://www.w3.org/TR/prov-dm/#term-Derivation)
  gives vocabulary for tracking derived evidence; it does not prove
  independence. Read through authenticated retrieval November 20, 2026.
- [Cochrane Handbook §4.6](https://training.cochrane.org/handbook/current/chapter-04#section-4-6)
  uses underlying studies rather than individual reports as review units and
  retains conflicting reports. This motivates a provenance check, not an
  assertion that software research is a clinical systematic review.
  Read through authenticated retrieval November 20, 2026.
- The public search returned secondary runtime explainers and the framework
  document extraction did not substantiate precise replay guarantees. Neither
  is used to claim production behavior. Reservation design and the worked
  scenario are proposed operational patterns, not a measured comparison.

To test value, compare against the same model and budget without this
checkpoint on held-out research briefs with independent labels. Count
unsupported material claims that pass, useful abstentions, redundant searches,
missed contradictions, and time/cost per accepted report. Do not infer field
improvement from the fixture.
