# Capability admission and update review

Use for a decision about allowing a component into an agent environment. Use the existing
owner and approval process; a second committee is unnecessary. Admission and authority are
linked decisions: an admitted component does not authorize any agent to use it for every action.
These documents propose decisions; they do not install components or change permissions.

## Intake, comparison and disposition

1. Record the business purpose, consuming agents, accountable internal owner and independent
   human approver. Identify source, maintainer, revision/digest and effective configuration,
   including discovered operations, credentials by reference, data classes, destinations and
   delegated agents. Never copy secrets into the record. Unknown provenance is an evidence gap,
   not a passing scan: hold deployment until the missing source and contents are verified.
2. Compare existing approved capabilities and trigger boundaries. Prefer routing to an existing
   skill when it meets the need. Record collisions, functional differences and the reason for
   retaining both; broad overlapping descriptions are not proof of extra value.
3. Gather dated, scoped evidence with source links, reviewer, uncertainty and counterevidence.
   Assess provenance, security, representative behavior, data handling, operational authority,
   update behavior and exit readiness. Set freshness and sufficiency criteria before evaluating
   results. A clean scan, catalog listing, advertised identity or model confidence cannot supply
   missing authorization or operational evidence.
4. Choose **admit**, **admit with restrictions**, **hold**, **reject**, **update**, **disable** or
   **retire**, with rationale, owner, approver, scope, expiry/review date and unresolved conditions.
   Scale diligence to impact. A public read-only lookup need not repeat enterprise vendor review
   when its boundary and current evidence are sufficient. Reuse evidence only within its scope.
5. Link admitted revision/configuration to each consuming authority decision using
   `templates/earned-autonomy-decision.md` from the skill root. Record human approval and pass the
   plan to the runtime owner. Activation requires independently verified enforcement and receipt;
   narrative approval alone is not enforcement. Initial grants, bounded promotion and protective
   restrictions follow `references/earned-autonomy.md` from the skill root.

## Type-specific questions and routing

| Component | Inspect beyond a README or scanner | Existing owner of specialist work |
|---|---|---|
| Agent Skill | Instructions, scripts and fetched resources; trigger collisions; environment/network access; actual host enforcement of declared tools | [agent-skills](../../agent-skills/SKILL.md), especially its third-party vetting reference |
| MCP server | Effective tool discovery, transport, server identity, OAuth audiences, scopes, roots, egress and configuration; annotations are untrusted hints | [secure-software-engineering](../../secure-software-engineering/SKILL.md) for controls; [security-audit-methodology](../../security-audit-methodology/SKILL.md) for assessment |
| A2A agent | Identity/authentication, advertised capabilities versus backend authorization, delegation chain, downstream data/action boundaries and revocation propagation | [agent-production-operations](../../agent-production-operations/SKILL.md) for runtime contracts and containment |
| Ordinary library | Dependency and build provenance, executed code and application privileges; it is not inherently an independently authorized agent | [secure-software-engineering](../../secure-software-engineering/SKILL.md) for dependency controls |

Route evaluation design to [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md),
operational evidence to [site-reliability-engineering](../../site-reliability-engineering/SKILL.md),
data-purpose/retention questions to [privacy-engineering](../../privacy-engineering/SKILL.md), and
material cost tradeoffs to [ai-operating-economics](../../ai-operating-economics/SKILL.md).
Use existing third-party diligence and agentic governance worksheets only when the risk warrants
their depth. These routes supply evidence, not substitute approval authorities.

## Update, disable and retirement

Compare the approved and proposed effective states, even if the package version is unchanged.
Changes to toolsets, roots, credentials, destinations, discovery, model behavior, delegation or
policy can change authority. List affected consumers and grants; invalidate affected evidence,
hold expansion and commission targeted re-evaluation. Preserve unaffected scope only if its
boundary remains demonstrably valid. No new approval is needed for unchanged scope with valid
approval and evidence.

For compromise, control failure or lost evidence required for continued operation, invoke the
pre-approved containment plan through the runtime owner: disable affected capability paths and
suspend/revoke linked authority, address in-flight work and credential exposure, and retain audit
evidence. A rollback is valid only to a known-good artifact **and configuration**. Restoration
requires a new authorized decision and verified controls, not simply reinstalling the old package.

For replacement or retirement, identify consumers, migration/fallback, retained data and records,
credential and grant revocation, owner and completion receipts. Verify old paths no longer work;
removing a catalog entry does not prove disablement. Finish with the linked record and operational
handoff, or a hold identifying missing evidence and its owner. Do not invent receipts.

## Three worked reviews

These are illustrative decisions grounded in actual component interfaces, not executed security
reviews, human validation results or permission changes. Names below are example accountable roles.

1. **Public-data Skill — local openlibrary.** The client sends public search terms via GET;
   `OL_SERVER` can change the destination and `OL_EMAIL` can populate a User-Agent. The platform
   owner proposes admit with restrictions: public queries only, approved endpoint configuration,
   no private context or contact data without a purpose decision, and review in 90 days. Record
   the inspected commit and configuration before approval. Compare existing public-book lookup
   routing before installing another skill. Existing egress/vetting guidance already catches this;
   the admission record makes the decision traceable rather than discovering a new risk.
2. **Private-data filesystem MCP.** Roots can replace the server's initial allowed directories;
   unchanged package version therefore does not mean unchanged data access. The data owner holds
   a proposed expansion from a project directory to all personnel files. Retain the old read-only
   scope only after enforcement proves the effective roots and operations remain restricted.
   Snapshot both states, link affected grants, request purpose/access evidence and review in seven
   days. Scanner success cannot resolve excessive data scope.
3. **Consequential GitHub MCP — promotion and suspension.** Toolsets and individually selected
   tools can combine; admitting the server does not authorize comments or merges. Suppose the
   repository owner set acceptance criteria in advance and receives representative held-out
   comment tasks, denominators, near misses, override records and successful expiry/denial tests.
   The decision proposes expanding an L2 grant to L3 for comments in one repository for 30 days,
   with rate limits, no merge/delete, independent human approval and controller receipt still
   required. If the actual evidence packet is absent, hold that promotion. Subsequently, an
   unreviewed tool configuration exposes write paths outside that repository: the runtime owner
   applies pre-approved suspension of affected writes, reconciles in-flight actions and requests
   review within one day. Reads continue only with independently demonstrated isolation.
   Reinstatement needs authorized review of the corrected configuration and fresh negative tests.

## Primary sources and limits

Reviewed 2026-10-09; recheck protocol and implementation details for the target version.

- [Agent Skills specification](https://agentskills.io/specification): format and experimental host-dependent `allowed-tools`, not a trust certification.
- [MCP security best practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices): token, consent and transport boundaries.
- [MCP tool annotations](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/): hints are not enforcement.
- [A2A enterprise readiness](https://a2a-protocol.org/latest/topics/enterprise-ready/): authentication discovery does not replace implementation authorization.
- [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem): roots and read/write operations.
- [GitHub MCP](https://github.com/github/github-mcp-server): tool selection, read-only and lockdown behavior; lockdown is not authorization.
- [NIST agent identity comment synthesis](https://pages.nist.gov/nccoe-ai-identity/summary-of-comments.html): stakeholder input on delegation and revocation, not a normative standard.
