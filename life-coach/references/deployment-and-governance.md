# Deployment and Governance

Use this reference when embedding the skill in a product or service. A skill file can shape conversation; it cannot implement identity, privacy, retention, safety response, accessibility, human review, monitoring, or legal compliance.

## Activation declarations

Follow [capability onboarding](capability-onboarding.md). Completed manifests and evidence belong in host-owned configuration outside the skill and repository. The tracked example remains blank. Validate a host-owned copy with:

```sh
python3 scripts/validate-capabilities.py /host/config/capability-contract.json
```

The validator distinguishes structural validity, declaration validity, and valid active declarations. It does not inspect live controls or establish deployment readiness. `DECLARATIONS VALID` means only that non-disabled static declarations passed validation; deployment decisions require applicable live evidence and accountable authorization. Unknown or disputed facts remain off.

### Routine baseline

`routine-adult-no-coaching-memory` permits bounded adult, routine, nonclinical conversation without coaching memory or any optional capability. It requires:

- deployment and environment identity;
- verification provenance, a policy-set review due date, and an accountable operator;
- a real user support route;
- fixed adult-only scope and code-shaped uppercase jurisdiction declarations whose actual coverage is verified by the attestor and evidence;
- evidence for AI/scope disclosure, the narrow safety fallback, and the user-facing data notice.

Without this verified baseline, ordinary invocation may still use the no-capability fallback described in `SKILL.md`; a deployed service that cannot support its narrow safety fallback must remain disabled.

### Optional capabilities

`capability-enabled` requires at least one enabled capability, an overall governance profile, and a current capability-specific control profile for each enabled item. Profiles must point to host-owned evidence for actual behavior, owners, consent and notices, data handling, acceptance tests, incident handling, disablement, and change review.

| Capability | Minimum control-profile concerns |
|---|---|
| `coaching_memory` | Exact proposed record preview, consent, access, retention, correction/export, deletion propagation, record separation, and write verification |
| `sponsored_coaching` | Separate agreements, coercion and retaliation review, technical separation, exact reportable fields, access controls, and re-identification review |
| `proactive_contact` | Exact content/channel/timing, notification privacy, frequency and stop controls, reliance monitoring, and disablement |
| `sensitive_actions` | Exact per-action preview and confirmation, authorization, visibility, reversibility, safety/coercion lockout, and result verification |
| `human_review` | Reviewer role and qualifications, purpose limitation, consent, minimization, sponsor separation, access audit, retention, and complaint route |

This public skill is adult-only and has no minor activation route. Safeguarding, therapy, clinical care, and specialist advice remain outside coaching regardless of optional capabilities.

## Layer map

| Layer | Can enforce |
|---|---|
| Skill | mode choice, AI/scope language, micro-agreement, inquiry behavior, referral language, anti-dependency, action preview |
| Host/platform | memory controls, tool permissions, sponsor separation, accessibility surface, human handoff, correction/export/deletion |
| Provider/infrastructure | authentication, authorization, encryption, isolation, availability, secure logging, retention mechanics, incident response |
| Human governance | attestations, specialist review, incident adjudication, evidence maintenance, release and disablement decisions |

Expose missing capabilities instead of pretending the skill implements them.

## Evaluation and release

Maintain ordinary, adversarial, false-positive, and multi-turn cases for mode routing, user ownership, therapy drift, cultural context, safety fallback, privacy, sponsor coercion, record control, human review, tool authorization, dependency behavior, accessibility, and endings.

A confirmed critical failure in imminent-danger handling, therapy scope, privacy disclosure, sponsor leakage, coercion, romantic boundaries, violent-harm facilitation, or sensitive action authorization blocks release. Aggregate scores cannot compensate. Rerun critical tests after model, prompt, provider, retrieval, tool, policy, data-flow, or platform changes.

## Claims and change control

Never claim credentials, professional conformance, equivalence to trained human coaching, confidentiality, legal privilege, duty of care, intervention capability, secure storage, deletion, accessibility, human escalation, or jurisdiction coverage without applicable live evidence.

On complaint, control failure, drift, stale evidence, or material change: disable or restrict the affected capability; preserve only necessary incident evidence under host controls; obtain the appropriate human review; fix the enforceable layer; add a regression case; rerun the actual deployment; and restore only after the accountable operator accepts current evidence and rollback remains available.

The authorized reviewer sets `review_due_on` according to the applicable control or review policy. Material changes trigger revalidation before that date.
