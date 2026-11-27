# Assessment examples

- **Idea without an accepted brief.** “Build a dashboard” is a proposed solution. Start with Product Discovery to identify the users and what decisions the dashboard should support. A read-only inventory of the available data can proceed in parallel after the question is framed. Stop before design approval or implementation.
- **Tests pass but an access rule was never approved.** Keep the candidate and its test evidence, but go back to the missing decision about who should have access. Route the policy decision to its human owner with Privacy Engineering as relevant; then reassess the affected spec and tests. Unrelated checks stay valid.
- **Small docs correction.** A scoped spelling fix in explanatory docs can use Neckbeard's lightweight path with targeted verification. The same file type in an authoritative restore runbook may change operator behavior and require recovery evidence. Route that verification to Resilience and Recovery and coordinate with Release Engineering. Do not execute a restore as part of assessment.
- **Merged and awaiting authorized rollout.** Verify the merge on the relevant revision. Check readiness and rollout authority separately. With authority and readiness in hand, Release Engineering owns the rollout and SRE owns observation of the live service; without them, stop with the gap named.

## Attribution

[Lauren Tan's P-stack](https://github.com/cursor/plugins/tree/b7b93c36be9bcc36a74db438e0fd385d660bc559/pstack) showed how an explicit entry point can route to specialist playbooks. [Addy Osmani's lifecycle meta-skill](https://github.com/addyosmani/agent-skills/blob/e997ac5b9a74eab332d5e9793bb38a38c8cfdd74/skills/using-agent-skills/SKILL.md) informed the broad phases and entry by current evidence. This map is an original adaptation for this catalog. Its discovery, planning, approval, and evidence rules come from the catalog's own specialist skills.
