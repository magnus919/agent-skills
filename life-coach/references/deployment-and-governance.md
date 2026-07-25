# Deployment and Governance

Use this reference when embedding the skill in a product or service. A skill file can shape conversation; it cannot implement encryption, identity, retention, crisis response, accessibility, supervision, monitoring, or legal compliance.

## Activation contract

Complete `templates/capability-contract.json` from verified deployment facts and run:

```sh
python3 scripts/validate-capabilities.py templates/capability-contract.json
```

The validator checks structure and conservative activation rules. It does not prove that declarations are true. Verify each capability through the host, provider, policy owner, and live acceptance tests.

### Full-service prerequisites

A deployment offering durable coaching, memory, sponsors, proactive contact, minors, human review, or tools needs named ownership and tested behavior for:

- AI identity and accountable operator;
- current crisis, medical-emergency, self-harm, harm-to-others, domestic-violence, trafficking, age, and safeguarding routes;
- jurisdiction and location handling without inferred or stale data;
- human contact and escalation where advertised;
- privacy, subprocessors, training use, embeddings, telemetry, backups, access, breach handling, retention, correction, export, and deletion propagation;
- technical separation of coaching, telemetry, incident, evaluation, supervision, and sponsor records;
- sponsor authorization, coercion review, role-based access, and re-identification controls;
- per-action previews and authorization;
- accessibility across relevant interfaces and languages;
- independent coaching supervision and separate licensed clinical or safeguarding consultation;
- complaint, incident, change, rollback, and disablement ownership.

Unknown or untested critical capabilities fail closed.

### No-capability fallback

Without a verified contract, restrict the skill to adult, routine, nonclinical, ephemeral conversation. Do not store, schedule, contact, report, serve sponsors or minors, claim human escalation, or invite high-sensitivity disclosures. The mandatory safety reference's narrow fallback still applies. Disable the skill if even that fallback cannot be supported.

## Layer map

| Layer | Can enforce |
|---|---|
| Skill | mode choice, disclosure language, consent prompts, inquiry behavior, scope, uncertainty, referral language, anti-dependency, action preview |
| Host/platform | memory controls, tool permissions, age routing, sponsor separation, accessibility surface, human handoff, user-visible correction and deletion |
| Provider/infrastructure | authentication, authorization, encryption, isolation, availability, secure logging, retention mechanics, incident response |
| Human governance | coaching supervision, clinical and safeguarding consultation, legal/privacy review, incident adjudication, evidence maintenance, release decisions |

Expose missing capabilities instead of pretending the skill implements them.

## Evaluation and release

Maintain ordinary, adversarial, false-positive, and multi-turn cases across:

- mode routing and direct-answer precedence;
- agreement, listening, user agenda, and rupture repair;
- method fit and therapy drift;
- structural and cultural context;
- crisis, medical emergency, self-harm, harm to others, abuse, safeguarding, and unsafe guardians;
- privacy, sponsor coercion and leakage, record control, human review, and tools;
- romantic or dependency behavior and proactive contact;
- unsupported credentials, privacy, safety, supervision, efficacy, and conformance claims;
- accessibility and language variation;
- endings and increasing independence.

A single confirmed critical failure in crisis handling, safeguarding, therapy scope, privacy disclosure, sponsor leakage, coercion, sexual or romantic boundaries, violent-harm facilitation, or sensitive tool authorization blocks release. Aggregate scores cannot compensate.

Use repeated stochastic runs and adversarial multi-turn trajectories. Test false positives as well as missed danger. Keep eval data synthetic or explicitly consented, minimized, and governed. Rerun after model, prompt, provider, retrieval, tool, policy, or platform changes.

## Professional review

Before a safety-sensitive service claims production readiness, obtain real, independent review from:

- a qualified coaching supervisor or credentialed senior coach;
- a licensed mental-health or safeguarding specialist;
- privacy and security expertise;
- accessibility and relevant cultural or language expertise.

Document who reviewed what, disagreements, limitations, and required changes. Simulated personas and model critiques are not credentialed review.

## Claims discipline

Never claim:

- ICF, EMCC, NBHWC, or other certification, endorsement, accreditation, or conformance;
- equivalence or superiority to trained human coaching;
- confidentiality, legal privilege, duty of care, or mandated reporting not actually provided;
- clinical validation or therapeutic effect;
- secure storage, deletion, accessibility, human escalation, uptime, or jurisdiction coverage without live evidence;
- that passing static skill evals establishes coaching efficacy or safety.

Publish the tested scope, model and host context, known failures, and recency of evidence instead.

## Change and incident loop

1. Detect a complaint, critical failure, drift, or standards change.
2. Disable or restrict the affected capability when risk warrants it.
3. Preserve minimum necessary evidence under incident controls.
4. Obtain the appropriate human review.
5. Fix the enforceable layer, not only the wording.
6. Add or strengthen a regression case.
7. rerun the critical suite on the actual deployment.
8. restore only after a named owner accepts evidence and rollback remains available.
