# Capability Onboarding

Use this field guide with the deployment operator, not with a person seeking ordinary coaching. The v2 manifest records verified host facts; it does not create controls or prove that references are accurate.

## Storage and starting point

Completed manifests, onboarding progress, attestations, and evidence belong in host-owned configuration outside the skill and repository. Apply the host's access control, backup, retention, change review, and secret-management rules. The tracked `templates/capability-contract.example.json` is a blank example only: create a new host-owned file from it and never edit the tracked example in place.

If the host cannot provide external configuration, `local/` is an ignored fallback. It is not canonical storage: ignored files can still be deleted by reinstall, checkout cleanup, workspace removal, or packaging. Do not put secrets in the manifest or evidence references.

## Modes

| `mode` | Meaning | Consequence |
|---|---|---|
| `disabled` | No coaching activation. Placeholders are allowed and every optional capability is off. | Structurally valid manifests return `VALID BUT DISABLED` with exit code 2. |
| `routine-adult-no-coaching-memory` | Adult-only routine nonclinical coaching with no coaching memory or other optional capability. | Requires a current verified baseline; every capability remains off. |
| `capability-enabled` | The baseline plus one or more verified optional capabilities. | Requires an overall governance profile and a control profile for each enabled capability. |

Unknown, untested, stale, or disputed capabilities stay off. This public contract is adult-only.

Machine-readable results include `active_declarations_valid`, which is `true` only when a non-disabled manifest has valid declarations. This field does not assert deployment readiness.

## Field guide

| Field | Acceptable value and evidence | Who may attest | Failure consequence |
|---|---|---|---|
| `schema_version` | Integer `2`. | Operator maintaining the manifest. | Other versions are invalid; v1 must be migrated. |
| `mode` | One of the three exact values above. | Accountable operator. | Unknown or contradictory mode is invalid. |
| `deployment.id` | Stable, non-secret service or deployment identifier. | Platform or service owner. | Required in active modes. |
| `deployment.environment` | Specific environment label such as `development`, `staging`, or `production`. | Platform or service owner. | Required in active modes; do not combine environments. |
| `verification.verified_on` | Real `YYYY-MM-DD` date that is not in the future. | Person completing the verification. | Missing, malformed, or future-dated verification blocks active declarations. |
| `verification.review_due_on` | Real `YYYY-MM-DD` date on or after `verified_on`. The authorized reviewer sets it according to the applicable control or review policy. | Human authorized to set the review interval for the cited evidence. | Missing, malformed, earlier-than-verification, or past due dates make active declarations invalid or stale. |
| `verification.attested_by` | Role, team, or accountable organizational identifier; do not add personal data unnecessarily. | A human authorized to accept the cited evidence. | Placeholder or unknown attestation invalidates active declarations. |
| `verification.basis_ref` | Host-owned review record showing what was inspected and how. | Authorized reviewer. | Missing provenance invalidates active declarations. |
| `accountability.operator` | Team or role accountable for operation and disablement. | Service owner. | Missing ownership invalidates active declarations. |
| `accountability.support_route` | Real user-facing support or complaint route. | Support owner or service owner. | Missing route invalidates active declarations. |
| `scope.adult_only` | Must be `true`. | Product/service owner with applicable review. | `false` is invalid; minors are outside this skill. |
| `scope.jurisdictions` | At least one code-shaped uppercase country or subdivision value, such as `GB` or `US-NC`; no blanks or duplicates. This is syntax only: the attestor and cited evidence must verify actual jurisdiction coverage. | Legal, policy, or service owner authorized for scope. | Empty values or values that do not match the uppercase code syntax make active declarations invalid. |
| `evidence.ai_scope_disclosure_ref` | Versioned user-facing disclosure that the system is AI and states coaching limits. | Product owner; specialist review as needed. | Missing evidence invalidates active declarations. |
| `evidence.safety_fallback_ref` | Tested narrow fallback for stopping coaching and directing urgent local help without false intervention claims. | Safety owner with qualified review appropriate to the deployment. | Missing evidence invalidates active declarations. |
| `evidence.data_notice_ref` | User-facing notice covering actual processing, retention, access, and routes for questions or rights. | Privacy/data owner. | Missing evidence invalidates active declarations. |
| `governance_profile_ref` | Host-owned overall governance profile; required only in `capability-enabled`, otherwise `null`. | Accountable operator after relevant reviews. | Missing or misplaced reference is contradictory. |
| `capabilities.<name>.enabled` | Boolean; defaults to `false`. Supported names are listed below. | Accountable operator relying on a current profile. | Unknown or unverified capability remains off. |
| `capabilities.<name>.control_profile_ref` | Host-owned, versioned evidence and controls for that exact capability when enabled; otherwise `null`. | Named control owner plus relevant specialist reviewers. | Enabled without a profile, or a profile on a disabled capability, is invalid. |

Supported optional capabilities are `coaching_memory`, `sponsored_coaching`, `proactive_contact`, `sensitive_actions`, and `human_review`. A profile must describe the real host behavior, acceptance tests, owner, failure/disable path, user notice and consent, data handling, and review date. Capability-specific expectations are in [privacy, sponsors, and tools](privacy-sponsors-and-tools.md) and [deployment and governance](deployment-and-governance.md).

## Collaborative workflow

1. Confirm the operator is configuring a deployment, the target deployment/environment, the host-owned destination, and how to disable or roll back before any write.
2. Inspect available host facts and existing evidence first. Do not ask the operator to retype facts the host can show.
3. Start from all capabilities off. Ask one focused question at a time, explain why the field matters, and accept “unknown”; unknown means off.
4. Record evidence references, not copied sensitive evidence, secrets, or unsupported claims. Only an authorized human may attest; an agent can organize evidence but cannot self-attest.
5. Present a complete redacted preview with the proposed mode, enabled capabilities, unresolved facts, destination, and consequences.
6. Write only after the operator confirms the target and preview. Never modify the tracked example.
7. Run `python3 scripts/validate-capabilities.py /host/config/capability-contract.json` and retain the result with the host-owned onboarding record.
8. Treat `DECLARATIONS VALID` and exit code 0 only as confirmation that active static declarations passed validation, not as deployment readiness. Leave or return the deployment to `disabled` after validation failure, stale evidence, disputed attestation, or incomplete write.

Structural and declaration validation are not implementation verification. Recheck live controls by `review_due_on`; material model, provider, prompt, policy, tool, data-flow, host, or control changes trigger earlier revalidation.
