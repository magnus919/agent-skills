# Specialist Route Selection

The stage lists in `manifest.yaml` are candidate routes, not an instruction to
load every listed skill. Load one primary specialist when its entry condition is
true. Add a secondary specialist only for a named blocker, risk, or handoff. If
one specialist fully owns the request, leave the FDE lifecycle and route the
bounded task directly.

| Stage | Candidate | Load only when | Do not load when |
|---|---|---|---|
| Discover | [product-discovery](../../product-discovery/SKILL.md) | The user, workflow, problem, outcome, or stakeholder interpretation is unvalidated | The problem and acceptance boundary are already explicit |
| Discover | [data-engineering](../../data-engineering/SKILL.md) | Discovery depends on data sources, contracts, quality, lineage, or pipeline feasibility | Data is incidental to the workflow question |
| Discover | [remote-systems-administration](../../remote-systems-administration/SKILL.md) | Relevant evidence or action sits behind remote access, privilege, egress, bastion, or recovery constraints | No remote or constrained system is involved |
| Frame | [product-design-and-ux](../../product-design-and-ux/SKILL.md) | The frame depends on user journeys, interaction behavior, service experience, or usability constraints | The work has no user-facing or workflow-experience question |
| Frame | [privacy-engineering](../../privacy-engineering/SKILL.md) | The frame includes personal data, consent, retention, disclosure, or privacy rights | No privacy-relevant data or processing is in scope |
| Frame | [secure-software-engineering](../../secure-software-engineering/SKILL.md) | The frame requires threat, trust-boundary, authentication, authorization, or secure-design decisions | Security is not a material part of the proposed intervention |
| Hypothesize | [product-experimentation](../../product-experimentation/SKILL.md) | The intervention needs a causal or comparative product/workflow experiment | The hypothesis is verified through engineering acceptance rather than an experiment |
| Hypothesize | [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md) | An agent, LLM, model, or nondeterministic workflow needs a decision/risk contract and evaluation plan | The capability is deterministic and ordinary test methods are sufficient |
| Build | [implementation-planning](../../implementation-planning/SKILL.md) | An authorized decision-maker has approved the requirement or specification and a dependency-aware delivery plan is needed | The requirement is not approved; stop and return upstream |
| Build | [backend-engineering](../../backend-engineering/SKILL.md) | The approved slice requires backend service or API implementation | No backend component is in scope |
| Build | [frontend-engineering](../../frontend-engineering/SKILL.md) | The approved slice requires a web frontend or client implementation | No frontend component is in scope |
| Build | [data-engineering](../../data-engineering/SKILL.md) | The approved slice requires data pipelines, contracts, storage, or transformation | Data work is not part of the implementation |
| Evaluate | [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md) | Agent, LLM, model, or nondeterministic behavior needs representative, adversarial, trajectory, or production-feedback evaluation | Ordinary deterministic verification is sufficient |
| Evaluate | [qa-methodology](../../qa-methodology/SKILL.md) | A risk-scaled test strategy or coverage model is needed | Acceptance criteria can be verified directly without a broader QA design |
| Evaluate | [verification-methodology](../../verification-methodology/SKILL.md) | Explicit acceptance criteria need direct pass/fail evidence | Criteria are not yet defined; return to framing or hypothesis work |
| Deploy | [production-readiness](../../production-readiness/SKILL.md) | A production or high-impact release needs a risk-scaled readiness verdict | The change is not crossing a production-like boundary |
| Deploy | [release-engineering](../../release-engineering/SKILL.md) | Release mechanics, versioning, promotion, rollback, or delivery automation are needed | No release artifact or promotion path exists |
| Deploy | [platform-engineering](../../platform-engineering/SKILL.md) | Deployment is blocked on an internal platform capability or platform-owned interface | The engagement itself is ongoing platform ownership; route directly instead |
| Deploy | [remote-systems-administration](../../remote-systems-administration/SKILL.md) | Deployment occurs through a constrained remote access or recovery path | The environment is local and unconstrained |
| Adopt | [product-adoption](../../product-adoption/SKILL.md) | Activation, onboarding, feature discovery, behavior change, or sustained use is below the decision rule | Intended workflow adoption is already evidenced |
| Adopt | [product-design-and-ux](../../product-design-and-ux/SKILL.md) | Adoption evidence points to usability or workflow-experience friction | The barrier is access, support, incentive, or ownership rather than UX |
| Measure | [product-analytics-and-measurement](../../product-analytics-and-measurement/SKILL.md) | Outcome metrics, instrumentation, events, funnels, cohorts, or governance are needed | Existing measurement evidence already answers the decision rule |
| Measure | [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md) | Model or agent quality needs production feedback and evaluation drift evidence | No agentic or nondeterministic component exists |
| Measure | [site-reliability-engineering](../../site-reliability-engineering/SKILL.md) | Reliability is an agreed outcome or a blocker to workflow impact | The request is ongoing SRE ownership; route directly instead |
| Generalize | [product-lifecycle-learning](../../product-lifecycle-learning/SKILL.md) | Expected and observed outcomes must be compared to choose continue, improve, pivot, pause, or retire | There is no post-launch evidence to compare |
| Generalize | [product-methodology](../../product-methodology/SKILL.md) | A bounded classification, prioritization, or decision log is needed for the local pattern | The question is portfolio investment or full product lifecycle governance |

## Approval boundaries

- `implementation-planning` is never a pre-approval route. A hypothesis,
  prototype, or promising field pattern is not an approved requirement.
- `product-operations-and-governance` is not a Frame-stage route for a single
  engagement decision. Load it only outside this bundle when the request is to
  design a recurring governance system.
- A Generalize-stage classification may hand an approved requirement to
  `implementation-planning` as the next owner's work. The planning skill is not
  part of the Generalize decision itself.
