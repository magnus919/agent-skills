# Secure Code Review Checklist

## When To Use

Use for a change that creates or alters a trust boundary, authority, data flow, dependency, release path, tenant behavior, or AI capability. Record evidence and findings, not just checked boxes.

## When Not To Use

Do not use this checklist as a substitute for a threat model, authorization test, or authorized security assessment. Escalate unclear boundaries rather than marking them passed.

## Change Context

- Change and intended behavior: <description>
- Threat-model or acceptance-criteria link: <link>
- Reviewer and evidence location: <reviewer/link>

## Boundary Review

- [ ] Every input reaches a defined parser, schema, limit, and safe sink.
- [ ] Query, process, path, URL, serialization, template, log, and output contexts are reviewed where present.
- [ ] Errors, retries, timeouts, exceptional conditions, and rollback do not leak data or bypass policy.

## Identity, Authority, And Tenancy

- [ ] Authentication is validated for the actual trust model.
- [ ] Server-side authorization checks every action and object, including jobs and bulk paths.
- [ ] Tenant context is derived and enforced in storage, cache, queues, search, logs, and resource controls.

## Secrets, Dependencies, And Release

- [ ] No credentials or sensitive values enter source, artifacts, logs, errors, or AI context.
- [ ] New dependencies, models, plugins, actions, and build inputs have a reviewed origin, version, permissions, and update plan.
- [ ] Release evidence and exception handling state what is supported and what remains unproven.

## AI Boundaries (If Applicable)

- [ ] Prompts, retrieval, model output, and tool output are untrusted.
- [ ] Tool actions are authorized server-side, narrowly scoped, and validated before execution.
- [ ] High-impact or irreversible actions have an appropriate approval gate.

## Findings And Verdict

| Finding or assumption | Evidence | Impact | Required action | Owner | Verification |
|---|---|---|---|---|---|
| <item> | <evidence> | <impact> | <action> | <owner> | <proof> |
