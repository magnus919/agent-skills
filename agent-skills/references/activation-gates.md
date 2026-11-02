# Activation gates and reachability

Read this when a skill is installed but absent from a session, or when reviewing
client-specific eligibility conditions. Installation, eligibility, selection and
successful loading are separate states.

## Establish the actual client contract

The Agent Skills format does not define a universal capability-gating vocabulary.
A client may filter skills by tools, toolsets, host OS, session channel or fallback
capability. Field names, nesting, all/any matching, unknown-name handling and error
visibility depend on that client's implementation and version. Do not copy another
client's metadata keys or assume an enabled listing proves session eligibility.

Before editing a gate, record:

- Client/version or source revision and the implementation or documentation path.
- Exact key, permitted values and where the client reads it.
- Whether multiple requirements mean all or any; behavior for unknown names.
- Actual session capabilities, platform and channel; supported diagnostics.

If those facts are unavailable, label the gate semantics unverified and inspect
current client evidence before prescribing fields. See [client implementation
guidance](client-implementation.md) for the broader loading boundary.

## Gate required capabilities, describe optional paths

A hard gate should reflect a capability genuinely necessary for the skill's primary
workflow. Keep optional browser, board or alternate execution paths in body-level
instructions with an explicit unavailable-capability fallback.

A required capability may ship disabled by default. Retain the truthful requirement,
document how an authorized operator enables it, and report the unmet prerequisite.
Removing a genuine requirement only to make the skill appear creates false
reachability. Conversely, requiring an optional capability unnecessarily excludes
usable workflows. Neither case grants permission to enable tools or change policy.

## Verify the complete path

1. Confirm the installed artifact's source and revision. Registry-name collisions
   can resolve a familiar slug to a different artifact.
2. Inspect the affected session's index and eligibility diagnostics, not only the
   global installed/enabled listing. Distinguish automatic selection from explicit
   loading; some clients give them different rules.
3. In an isolated configuration or approved reversible test, vary one suspected
   condition. Record before/after eligibility and restore the configuration. Do
   not silently weaken a production gate or infer causality from several changes.
4. Exercise actual loading and a bounded primary task in the affected session.
   Index appearance proves visibility; it does not prove loading or task success.

Complete when the failure is located in discovery, eligibility, selection, loading
or execution and a supported repair is verified at that layer. If a client cannot
expose or exercise the needed state, report the evidence gap and next diagnostic;
do not call installation or a metadata edit proof of runtime reachability.
