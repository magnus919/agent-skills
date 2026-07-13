# Security Acceptance Criteria

> **Confidentiality:** Completed criteria can describe security boundaries. Keep them within the project's appropriate access controls.

## When To Use

Use while writing a feature specification, design decision, or pull request description. Replace prompts with observable, feature-specific criteria and direct evidence.

## When Not To Use

Do not treat unchecked items or headings as semantic validation. Use `verification-methodology` to assess evidence and record a verdict.

## Scope And Threat Model Link

- Feature or change: <description>
- Assets and trust boundaries affected: <link or summary>
- Security owner and review date: <owner/date>

## Authentication And Authorization

- [ ] Identity is verified at <boundary> using <trust basis>; evidence: <test/configuration>.
- [ ] Server-side authorization permits <actor> to perform <action> on <resource> only under <conditions>; denied cases tested: <cases>.
- [ ] Object and tenant checks cover direct, bulk, asynchronous, and tool-mediated paths: <evidence>.

## Input, Output, And Data

- [ ] Inputs from <sources> have schemas, limits, and rejection behavior: <evidence>.
- [ ] Outputs for <contexts> are encoded or constrained appropriately: <evidence>.
- [ ] Data classification, retention, export, and deletion decision: <decision/evidence>.

## Secrets And Dependencies

- [ ] New or changed secret material has owner, scope, storage, revocation, and event/risk-driven rotation plan: <evidence or not applicable>.
- [ ] Dependencies, models, plugins, and build inputs have version, origin, affectedness, and update decision: <evidence>.

## Logging And Release

- [ ] Security-relevant events logged: <events>; excluded or redacted data: <data>; access and retention: <decision>.
- [ ] Release evidence includes <SBOM/provenance/tests/approvals>; limitations and exceptions: <limits/owner>.
- [ ] Rollback and response path: <path/owner>.

## AI-Specific Boundaries (If Applicable)

- [ ] Prompts, retrieved content, and tool output are treated as untrusted: <evidence>.
- [ ] Every tool action is authorized server-side and constrained to <capability/data scope>: <evidence>.
- [ ] Material or irreversible actions require <approval/policy>: <evidence>.
