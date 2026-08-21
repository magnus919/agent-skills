# Migration And Coexistence

Architecture decides whether a target boundary is justified and what properties the transition must preserve. `migration-engineering` owns the current-to-target execution method: compatibility windows, dual-running, reconciliation, cutover, recovery classification, deprecation, and cleanup.

## Handoff fields

Before handoff, provide:

- current and target boundaries;
- decision drivers and rejected alternatives;
- authority and ownership changes;
- interface and data contracts to be designed by specialists;
- coupling and consumer inventory with evidence gaps;
- consistency and failure invariants;
- coexistence assumptions and selectable paths;
- fitness evidence and cutover conditions;
- irreversible steps and explicit acceptance needs;
- named architecture, migration, implementation, platform, security, data, and operations owners.

## Patterns as roles

Name a transition pattern by the risk it controls: routing controls traffic selection, an abstraction controls call-site change, a translation boundary protects semantic ownership, change capture carries state, and parallel comparison creates evidence. Do not select a pattern merely because extraction was requested. Load `migration-engineering` once the boundary is approved.

## Retain the monolith when

The candidate still needs shared writes, frequent cross-boundary transactions, unowned data, hidden consumers, untestable recovery, or no measurable independent scaling or ownership benefit. Record modular improvements and the evidence that would reopen the decision.
