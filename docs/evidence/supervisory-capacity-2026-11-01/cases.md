# Three public reconstructed cases

These are source-bounded reconstructions, not interviews, independent observations,
current audits of the organizations or assertions that private facts are absent.
Unknown means **not available in the selected public evidence**, not nonexistent.
The same worksheet fields are applied to each. All decisions below are analyst
recommendations for the reconstruction; no real organization adopted them here.

## Source facts and evidence classes

**S1 — high-volume customer service.** In its 27 February 2024 announcement, Klarna
reported 2.3 million assistant conversations in the first month, roughly two thirds
of service chats, and retained a live-agent choice. Those are historical company
claims, not this audit's measured workload or reviewer staffing. The public release
is [provided by Klarna](https://www.prnewswire.com/news-releases/klarna-ai-assistant-handles-two-thirds-of-customer-service-chats-in-its-first-month-302072744.html).
A claimed full-time-worker equivalent is not available human review capacity.

**S2 — software development and review.** GitLab Developer Experience's handbook
requires review of AI-assisted code, retains human expertise for security-sensitive
work, and describes AI summary/initial feedback before human review. It uses scoped
AI-assistance labels. This is published workflow/policy, not observed compliance,
review throughput or queue performance. [Primary handbook](https://handbook.gitlab.com/handbook/engineering/infrastructure-platforms/developer-experience/ai/), retrieved 2026-11-01.

**S3 — research/engineering agents with layered monitoring.** Anthropic's August
2026 snapshot reports about 30,000 simultaneous agents on one internal platform,
full online/offline action coverage, and about 50 highest-priority flags per week
sent to humans after classifier triage. These are provider-reported measurements,
not independent evidence of monitor recall, human competence or adequate staffing.
[Primary disclosure](https://www.anthropic.com/institute/measuring-pace-of-ai-development), retrieved 2026-11-01.

No employee identities, private incidents, transcripts, customer data or personnel
scores were collected. Company names identify public contexts, not participants.
Source periods differ and must not be compared as a performance ranking.

## Filled common worksheet

Cells marked “infer” are analyst implications, not additional source facts.

| Worksheet dimension | S1 customer service | S2 software DevEx | S3 research/engineering |
|---|---|---|---|
| Output volume/variability | Reported chat scale; risk/task mix unknown | Per-MR arrival mix and volume unknown | Reported platform agent scale; action/task mix not a human-review denominator |
| Work requiring review | Complaint/escalation and consequential-action review requirements unknown; infer: separate task/risk classes | Published human-review boundary; inspect review unit/complexity, not generated lines alone | Classifier triage precedes selected human flags; human review unit differs from raw actions |
| Reviewer capacity | Staff availability, review minutes and competing work unknown | Available qualified reviewer hours and service rates unknown | Reviewer hours, per-case time and surge coverage unknown |
| Competence/qualification | Domain, language and consequential-action competence unknown | Security work retains human expertise; actual reviewer qualifications not audited | Investigator qualification and calibration not available in selected evidence |
| Queue age/backlog | Not disclosed here; instrument waiting and oldest unresolved case | Not measured here; instrument age by risk and author/reviewer stage | Human-priority backlog/age distribution not available here; inspect by severity |
| Escalation volume/severity | Live-agent path exists; severity mix and acknowledgement timing unknown | Human review exists; exception/severity volume unknown | Reported human-priority stream exists; adequacy requires severity and response evidence |
| Missing-context rework | Not quantified; preserve handoff context and correction effort | Not quantified; inspect summaries against code/intent and re-review effort | Not quantified; inspect information loss in successive triage stages |
| Undocumented decisions | Unknown; require authority/provenance for consequential action | Policy does not prove each decision is recorded; inspect actual review evidence | Reported monitoring does not supply each decision's authority record |
| Meeting/coordination load | Unknown; do not invent a staffing meeting schedule | Unknown; test asynchronous ownership before adding meetings | Unknown; escalation meetings and handoff effort require bounded records |
| Agent-generated meta-work | Review summaries/retries not quantified; include them in workload | AI summaries/review feedback are an extra artifact stream; net human burden unknown | Automated triage itself creates classification/review work; full load/cost not measured here |
| Human-reserved decisions and stop ability | Current grants and stop controls unavailable here; infer no expansion from chat totals | Keep review/security boundary; published policy is not verified enforcement | Preserve independent monitoring/containment; current human stop authority not audited |
| Conditions to constrain automation | **Constrain proposed unattended consequential scope** until review/escalation capacity, competence and control evidence exist | Do not bypass human review to absorb more generated output; cap intake if review backlog breaches approved bounds | Do not broaden autonomous scope from coverage/agent count alone; hold affected scope if required supervision is unproved |
| Cost/outcome effects | Company outcomes are reported, not independently attributed; full review/exception cost unknown | Accepted quality, rework and reviewer cost unknown; no net speed/value claim | Monitoring/review cost and accepted-task outcomes unknown; no cost-effectiveness inference |

## Four distinct constraints in each case

| Case | Capacity | Competence | Authority | Attention |
|---|---|---|---|---|
| S1 | Available staffed service/review time is unknown | Required domain/language judgment not established here | Chat volume cannot grant consequential action rights | A live-agent option does not prove urgent cases are noticed in time |
| S2 | Reviewer throughput/availability is unknown | Security expertise is explicitly retained; actual coverage needs evidence | Human-review policy is distinct from technical permission | Summaries and labels may aid orientation, but timely attention is unmeasured |
| S3 | Human investigator time and surge capacity are unknown | Monitor/triage agreement is not human qualification | Monitoring coverage does not authorize new research actions | Alert delivery and priority/latency need evidence beyond raw coverage |

These constraints cannot substitute for one another: more available hours do not
create expertise or grant rights; rights do not guarantee timely attention.

## Decision test against route-only baseline

`baseline.json` freezes the route-only recommendations before this worksheet fill.
The worksheet adds a uniform view of gaps but **does not change the substantive
recommendation in any of these three reconstructions**:

| Case | Baseline → worksheet recommendation | Material change? |
|---|---|---|
| S1 | Constrain expansion; preserve human path and obtain qualified review/escalation evidence → same | No; more organized missing-data list, not a new staffing or authority decision |
| S2 | Retain human review; instrument queue/rework/availability → same | No; existing owners and policy already supply the boundary |
| S3 | Preserve layered controls; verify severity/latency and independent evidence before expanding → same | No; the monitoring/evaluation owners already require that evidence |

This comparison is authored and unblinded, and does not measure actual decision
change. Incomplete public data makes it unsuitable for sizing staff, choosing a
sampling rate, alleging organizational under-supervision, or validating outcomes.
It is sufficient to show that these records do not support building a new bundle.
