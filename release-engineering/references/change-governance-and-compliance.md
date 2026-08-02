# Change Governance and Compliance

Release engineering is where change control stops being a bureaucratic form and becomes an **evidence pipeline**. Auditors (SOC 2, SOX, PCI DSS, ISO 27001, EU DORA) do not actually care about your CAB meetings — they care whether every change can be traced, unbroken, from business request through review, test, approval, deployment, and verification. A well-designed pipeline produces that evidence as a **byproduct**; a poorly designed one forces engineers to reconstruct it after the fact. This reference covers evidence-based change control, the artifact-by-artifact evidence chain, emergency/break-glass paths, the major regulatory frameworks, audit-friendly pipeline design, separation of duties, and the pitfalls that destroy evidence.

## Evidence-Based Change Control vs CAB Bureaucracy

The Change Advisory Board (CAB) — ITIL's cross-functional committee that reviews and approves changes — is the traditional governance model. ITIL 4 distinguishes **standard** (pre-authorized, low-risk, repeatable), **normal** (assessed and scheduled, may go to CAB), and **emergency** (expedited) changes.

The empirical case against heavy external approval is decisive. DORA/Accelerate found that external approval (CAB/manager sign-off) is **negatively correlated** with lead time, deployment frequency, and restore time, and has **no correlation** with change failure rate — it slows delivery without improving stability, and is "worse than no approval process." The evidence-backed replacement is **lightweight peer review** (code review, pair programming) **combined with a deployment pipeline that detects and rejects bad changes**.

Modern change control therefore keeps the *evidence*, not the *committee*:

| Dimension | CAB-era governance | Evidence-based control |
|-----------|--------------------|------------------------|
| Gate | Human committee approval | Peer review + automated pipeline gates |
| Evidence | Meeting minutes, sign-off forms | Immutable artifacts: PRs, CI logs, deploy records |
| Cadence | Scheduled change windows | Continuous, small batches |
| Emergency path | Exception to the committee | Pre-documented break-glass procedure with retroactive audit |
| Failure mode | Slow without being safer | Fast with machine-checkable safety |

**Retain a CAB-like review only where it adds value**: high-risk changes (data migrations, security boundaries), regulated launches, and audit-after-the-fact review boards. For everything else, the pipeline is the control. This is not a license to skip documentation — it is a mandate to *automate* it.

## The SOC 2 CC8.1 Evidence Chain

SOC 2's **CC8.1** control requires that the entity "authorizes, designs, develops or acquires, configures, documents, tests, approves, and implements changes to infrastructure, data, software, and procedures to meet its objectives." Its points of focus span the whole SDLC: manage changes, authorize before implementation, design/develop with controls, document for traceability, track to confirm intended outcomes, configure with approved settings, and test before implementation.

For a code change, auditors trace a specific artifact chain. **Every link must exist and connect**:

| # | Artifact | Must Contain | Where Stored |
|---|----------|--------------|--------------|
| 1 | **Change request / ticket** | Business justification, risk assessment, testing plan, requester, timestamp | Ticketing system (Jira, Linear) |
| 2 | **Design / review doc** (significant changes) | Architecture decision, security impact, alternatives | Wiki / RFC repo / ticket attachments |
| 3 | **Peer code review (PR/MR)** | Diff, reviewer comments, approval by an engineer **other than the author**, timestamp | GitHub/GitLab with branch protection enforced |
| 4 | **CI / build / test results** | Unit + integration test results, SAST/DAST scan, lint, build success, **commit SHA tested** | CI platform logs, exported to a centralized store |
| 5 | **Change approval (deployment gate)** | Approver identity (**not** the code author), timestamp, decision, target environment | GitHub Environments required-reviewer, GitLab protected environments, or CAB record |
| 6 | **Deployment log** | Who/what (commit SHA, **artifact digest**), when (UTC), target environment, **pipeline run ID**, deployer identity | CI/CD deployment records, Argo CD sync log, cloud audit logs (CloudTrail, GCP Audit Logs) |
| 7 | **Post-deployment verification** | Smoke/synthetic check results, health metric confirmation, rollback trigger status, ticket closure | Monitoring system, ticketing system status change |

CC8.1 intersects with **CC6.1** (only authorized people approve and deploy) and **CC7.1** (unauthorized changes generate alerts). It is the **second most common source of audit exceptions** in Type II audits — and those exceptions are "almost always process failures rather than technical ones": a missing ticket link, a deleted branch, an unrecorded manual deploy.

### Auditor Sampling

| | Type I | Type II |
|--|--------|---------|
| What it proves | Design exists at a point in time | Controls operated effectively over time |
| Evidence | 1–2 example tickets showing the full workflow | Population of **all** changes over 6–12 months; sample of **25–50** changes checked artifact-by-artifact |
| Exceptions tolerated | Design gaps are findings | **None** — a single missing link in a sampled change is an exception |
| When it applies | Readiness/pre-audit, initial certification | Renewal and continuous assurance |

Sample size guidance: 25 for well-controlled environments, scaling to 50+ when the population is large, high-risk, or control weaknesses are found. Auditors may pull changes directly from version control or request an export — either way, the evidence must be *discoverable without a human tour guide*.

> **Gotcha — The 25-change lie:** If only 24 of your changes have complete evidence chains, an auditor sampling 25 changes can fail you on one gap. The discipline is not "make sampled changes clean" — it is "make the pipeline incapable of producing a change without complete evidence."

### Tracing One Change, End to End

To internalize the chain, trace a single merged PR as an auditor would:

1. **Ticket** `PROJ-2041` exists with justification ("fix rate-limit false positives"), risk tier, and requester.
2. **PR** `#4821` title carries the ticket ID (`[PROJ-2041] fix rate limiting`); branch protection required and recorded one reviewer who is **not** the author; approval timestamped.
3. **CI** run on the PR's commit SHA: unit + integration tests green, SAST scan clean, artifact built and pushed with digest `sha256:9f86d0…`; all logs retained.
4. **Approval** — a GitHub Environments required reviewer (again not the author) approved the production deployment; environment protection rules forbid direct pushes.
5. **Deployment log** — records `commit abc1234`, digest, environment `prod-us-east`, UTC timestamp, pipeline run ID `run-8871`, deployer identity (the pipeline's OIDC role).
6. **Post-deploy verification** — smoke test passed; error-rate dashboard confirmed baseline; ticket closed with verification link.

If any of these six links is missing or unlinkable, that change is an audit exception waiting to be sampled. This is exactly the evidence shape the `templates/change-governance-record.md` template captures per change.

## Emergency Change and Break-Glass

Auditors accept emergencies — but they require the emergency path to be **pre-documented, controlled, and logged in the same system** as normal changes:

| Requirement | Detail |
|-------------|--------|
| **Documented procedure** | Policy defines "emergency" narrowly (security exploit, production outage) *before* an emergency occurs |
| **Approval** | At least one authorized approver (senior manager / on-call lead), even if post-hoc |
| **Written justification** | Why the normal process was bypassed; what the urgency was |
| **Same-system logging** | Emergency changes appear in the same change tracking system as normal changes — no shadow log |
| **Retroactive window** | Post-hoc approval within a defined window (commonly 24–72 hours; set in org policy) |
| **Post-implementation review** | Formal review of root cause and the fix; documented postmortem |
| **Retrospective audit** | Emergency changes reviewed monthly/quarterly; track the ratio |
| **Separation of duties** | Where feasible, implementer ≠ approver ≠ tester; document why if bypassed |

The key constraint: **"CC8.1 requires that all changes are tested; there is no exception for emergencies."** Break-glass is an alternate, audited control path — it does not skip controls. **If everything is an emergency, the normal process is not working**; a high emergency ratio is itself an audit red flag and an organizational signal.

## Regulatory Frameworks

### SOX ITGC (Sarbanes-Oxley IT General Controls)

Applies to US public companies for systems impacting financial reporting (ERP, billing, payroll, AR/AP, financial reporting software). Auditors expect: formal multi-level **change authorization**, fine-grained **segregation of duties** with automated conflict detection, **documented testing** before deployment, comprehensive change documentation, and controlled emergency procedures. The evidence chain has the same shape as SOC 2 but is scoped to financial-reporting-relevant systems, and retention is the longest of any framework: **7 years** for financial system audit logs.

### PCI DSS (Requirement 6 — Change Control)

For cardholder-data environments (PCI DSS v4.0.1), the mandatory change-control sub-requirements include:

| Requirement | Mandate |
|-------------|---------|
| 6.4.1 | Separate dev/test environments from production with access controls |
| 6.4.2 | Separation of duties between development/testing and production personnel |
| 6.4.3 | No live PANs (production card data) in test/dev |
| 6.4.4 | Remove test data and accounts before going live |
| 6.4.5.1 | Document the impact of the change |
| 6.4.5.2 | Documented change approval by authorized parties |
| 6.4.5.3 | Functionality testing proving the change does not adversely affect security |
| 6.4.5.4 | **Establish back-out procedures** for changes |
| 6.4.6 | After significant changes, re-apply all relevant PCI DSS requirements and update documentation |

Additionally, **Req 6.3.2** requires code reviews by someone other than the code developer, with results reviewed and approved by management before publication. PCI DSS 4.0 explicitly covers the CI/CD pipeline itself — QSAs inspect pipeline configuration, not just runtime systems. Log retention: **12 months, with 3 months immediately available**.

### EU DORA (Digital Operational Resilience Act)

In force since 17 January 2025 for EU financial entities and their ICT third-party providers. **Article 9(4)(e)** requires documented policies ensuring that all ICT changes are **"recorded, tested, assessed, approved, implemented and verified"** in a controlled manner, with the process approved by appropriate lines of management. Article 9(4)(c) limits access to what is required for legitimate functions; Article 9(4)(f) requires documented patch/update policies; Article 9(4)(b) requires networks designed to be instantly severed or segmented. DORA is principle-level — but those six verbs map exactly onto the SOC 2 evidence chain, so one well-built pipeline satisfies both.

### EU Cyber Resilience Act (CRA)

Applies to manufacturers of digital products/software sold in the EU. Key deadlines: vulnerability reporting by **11 September 2026**; full compliance including SBOM by **11 December 2027**. Requirements relevant to release engineering: a **mandatory SBOM** for software products (SPDX 2.3 or CycloneDX per BSI TR-03183-2), covering **all components including transitive dependencies**, continuous vulnerability monitoring, secure-by-design development, and mandated vulnerability disclosure timelines. Fines up to €15M or 2.5% of global annual turnover. For release pipelines this makes **SBOM generation a build-time gate** — every release artifact ships with an associated SBOM. See [supply-chain-security.md](./supply-chain-security.md).

### ISO 27001 Annex A.8.32

Requires that changes to information processing facilities and systems are "properly controlled and authorized," with defined responsibilities for planning, evaluating, authorizing, implementing, reviewing, and communicating changes. Less prescriptive than SOC 2/PCI about artifact types, but the evidence expectations converge in practice (ticket, approval, test, deploy record). Adjacent controls: A.8.31 (separation of dev/test/production environments), A.8.33 (test information).

### Retention Requirements Summary

| Framework | Minimum Retention | Notes |
|-----------|-------------------|-------|
| SOC 2 | 12 months (industry standard) | Must cover the full Type II observation period (3–12 months) |
| PCI DSS | 12 months (3 months immediately available) | Req 10.7 |
| SOX | **7 years** | Financial system logs; Section 802 |
| ISO 27001 | Defined by org policy | Must demonstrate control over the certification period |
| DORA | Principle-based | Supervisory authorities may request historical records |
| Multi-regime best practice | 13 months hot + 7 years cold immutable | Stacked regimes, not one number |

## Building Audit-Friendly Pipelines

Audit-friendly means **complete-by-default**: the evidence trail is a byproduct of the pipeline, never reconstructed after the fact.

| Evidence type | Automation mechanism |
|---------------|----------------------|
| Code review record | Branch protection requires PR approval before merge; immutable timestamped record |
| CI/test results | Pipeline runs on every PR/commit; status checks block merge; logs exported to a centralized store |
| Deployment record | GitHub Environments / Argo CD sync / GitLab environments record who/what/when |
| Artifact provenance | SLSA provenance attestations (Sigstore, slsa-github-generator) prove the artifact was built from a specific commit by a specific workflow |
| SBOM | Generated in-pipeline (Syft, Trivy), attached as an attestation |
| Signing | Cosign/sigstore signs images and attestations; verifiable without shared secrets |
| Approval gate | GitHub Environments required-reviewer; GitLab `when: manual` on protected environments |
| Cloud audit correlation | CloudTrail / GCP Audit Logs / Azure Activity Log record every API call by pipeline role; cross-reference by pipeline run ID |

Design principles:

1. **Export configuration as evidence** — branch-protection settings, environment protection rules, and workflow definitions are themselves audit artifacts.
2. **Automate the linkage** — commit message references the ticket (`[PROJ-123]`), PR title carries the ticket ID, deployment metadata references PR + commit. The chain must be reconstructable by following references, not by human memory.
3. **Immutable audit log storage** — write-once, read-many (WORM) storage via S3 Object Lock in compliance mode, in a **separate logging account** with no trust relationship allowing production principals to modify logs; CloudTrail log-file validation adds cryptographic signing of each log file.
4. **Self-audit monthly** — sample your own changes before the auditor does; fix gaps while they are cheap.
5. **Retain deploy logs for the full observation period** — 12+ months hot, 7 years cold for SOX-relevant systems.

### A Stage Map for Evidence-Producing Pipelines

| Pipeline stage | Evidence emitted automatically |
|----------------|--------------------------------|
| PR open → merge | PR metadata, branch-protection enforcement, required review approvals, status checks |
| Build | Commit SHA, builder identity, artifact digest, SBOM, provenance attestation (signed) |
| Test | Test reports, scan results (SAST/DAST/dependency), coverage, all keyed to the commit SHA |
| Promotion to staging | Promotion ledger entry (digest, labels, pipeline run ID) |
| Approval gate | Environment protection approval record (approver ≠ author, timestamped) |
| Deploy to production | Deployment record (who/what/when/env), cloud audit log correlation |
| Post-deploy verification | Smoke/synthetic results, metric snapshots, rollback-trigger status |
| Close | Ticket closure referencing verification evidence |

Each stage writes immutable, linkable records; nothing is "documented" after the fact. A GitOps deploy (Argo CD, Flux) collapses several rows into one reconcilable commit — the git history *is* the approval and deployment record.

## Separation of Duties in Automated Pipelines

The principles translate directly from manual change control:

1. **No single identity builds AND deploys to production.**
2. **Code authors do not approve their own deployments.**
3. **Pipeline definitions are protected from the code they process.**
4. **Build artifacts are immutable once produced.**

| Mechanism | How it implements SoD |
|-----------|-----------------------|
| Per-stage identities | Build, test, sign, stage, deploy each use different IAM roles/service accounts |
| OIDC short-lived credentials | 15–60 minute tokens, no static secrets, scoped to a specific job |
| GitHub Environments | Required reviewers (2+ for production), wait timers, deployment branch restrictions, environment-scoped secrets |
| GitLab protected environments | `when: manual` + protected runners + protected variables (prod creds only on protected branches) |
| CODEOWNERS on workflow files | `.github/workflows/` owned by a platform/security team; their approval required to modify |
| Immutable pipeline templates | Reusable workflows pinned to version tags; teams cannot override protected stages |
| Canary as an SoD control | Second manual approval required to proceed beyond the canary stage |
| Alerting on SoD violations | Alert when approver == author, when a pipeline accesses secrets it should not, when branch protection is modified |

> **Gotcha — Emergency paths that delete controls:** "If a required check is failing, fix the check or use an emergency process that requires multiple approvals and creates an audit trail. Never disable branch protection." Manual SSH to production bypasses every control; when it is unavoidable it must go through the break-glass procedure with a post-incident review, not become a routine habit.

## Pitfalls That Destroy Evidence

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| **Manual console changes without a ticket** | Change invisible to the auditor; evidence gap | Restrict console write access; require a ticket for any manual change; detect drift (AWS Config) |
| **Overloaded emergency procedure** | Half of all changes labeled "emergency" makes the category meaningless; auditors question each one | Tighten the definition; review emergency changes monthly; track the ratio |
| **No ticket↔deployment linkage** | Auditor cannot trace approval → deployed change; chain breaks | Enforce ticket ID in PR title, commit message, and deploy metadata |
| **Approver-as-author** | Same person approved and deployed; violates SoD | Require separation; at minimum, document why it was not feasible |
| **Deleted branches / PRs** | Evidence destroyed; change unreconstructable | Retain merged PR data; export to an evidence store; never delete main/release branches |
| **Timestamp drift** | Tools on different clocks; events cannot be correlated across systems | UTC everywhere; NTP synchronization; record timezone explicitly |
| **Unrecorded manual deploys** | SSH to production bypasses all controls | Eliminate direct SSH; break-glass with audit trail; alert on direct access |
| **Disabling branch protection "temporarily"** | Unprotected window permits direct pushes bypassing review | Never disable; use the emergency process with multi-approval |
| **Shared runners (PR + production)** | A malicious PR could reach production credentials | Separate runner pools; ephemeral isolated runners for untrusted work |
| **Single admin token ("god token")** | Skeleton key; outlives its creator; never rotated | Per-stage OIDC; no static tokens; regular credential audit |
| **Logs stored in the production account** | An attacker who compromises prod can delete the evidence | Cross-account logging; WORM storage; no delete permission for prod roles |
| **Short log retention** | Evidence gone before the audit window closes | 12 months minimum (SOC 2); 7 years for SOX; multi-regime hot + cold |

## Gotchas

- **Manual evidence is a smell.** If your compliance evidence is a folder of PDF screenshots assembled before each audit, your pipeline is not doing its job. Auditors increasingly expect exported config files and CI logs covering the full window, not screenshots.
- **CC8.1 failures are process failures.** The control text is satisfied by process mechanics (who approved, what was tested, when deployed) — the most common exceptions are missing links, not missing security.
- **"Config as code" is also a change.** Terraform/OpenTofu, feature-flag changes, and pipeline YAML edits are changes under CC8.1 and PCI 6.4 — they need the same review/approval/deploy-record chain, not a separate informal path.
- **Version-pin your workflows and actions.** Pinning pipeline definitions and third-party actions to SHAs is both a security control (see [supply-chain-security.md](./supply-chain-security.md)) and an audit control: the "how" of a deployment must be reproducible from the recorded version.
- **AI-generated code is not a bypass.** If an agent or AI assistant authored a change, the change still needs the same ticket → review → test → approval → deploy chain. Auditors have not yet settled on AI-involvement attestation requirements; the defensible default is to record authorship transparently and apply exactly the same controls as human-authored code.
- **Sample with a calendar, not a feeling.** Run the monthly self-audit as a fixed ritual: pull N random changes from the last month, replay the six-link trace (ticket → PR → CI → approval → deploy → verify), and file the gaps. A standing "evidence debt" list is far cheaper than an audit exception.
- **DORA is not a compliance framework, but it predicts audit outcomes.** Evidence-based change control (peer review + automated gates) is both the high-throughput model and the model that produces the cleanest audit trails — the two goals converge. See [metrics-and-dora.md](./metrics-and-dora.md).

## Sources and Further Reading

- [SOC 2 Change Management Controls (soc2auditors.org)](https://soc2auditors.org/insights/soc-2-change-management-controls/) — CC8.1 interpretation, sampling, exceptions
- [SOC 2 CC8.1 framework guide (episki)](https://episki.com/frameworks/soc2/change-management) — control text and emergency-change requirements
- [PCI DSS Requirement 6 (pcidssguide.com)](https://pcidssguide.com/pci-dss-requirement-6/) — 6.4.x and 6.3.2 change control text
- [DORA Article 9 (digital-operational-resilience-act.com)](https://www.digital-operational-resilience-act.com/Article_9.html) — ICT change management requirement
- [EU CRA SBOM requirements (Anchore)](https://anchore.com/sbom/eu-cra/) — CRA deadlines and SBOM mandates
- [Separation of Duties & Least Privilege in CI/CD (secure-pipelines.com)](https://secure-pipelines.com/ci-cd-security/separation-of-duties-least-privilege/) — pipeline SoD implementation
- [SOC 2 Audit Log Requirements (AuditPath)](https://www.auditpath.io/blog/soc2-audit-log-requirements) — retention regimes, WORM storage
- [Is a Change Advisory Board Really Needed? (Harness)](https://www.harness.io/blog/change-advisory-board-really-needed) — DORA/Accelerate evidence on external approval
