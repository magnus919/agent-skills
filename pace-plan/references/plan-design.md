# Plan Design

Load this reference when creating a plan, adding a communication pair, or auditing path completeness and independence.

## 1. Define The Planning Unit

Create a separate worksheet for one mission or essential function. Identify every sender/receiver pair that must exchange information. Do not assume an organization-wide list of technologies is a PACE plan; paths must be usable by the named endpoints for the named function.

For each pair, record:

- information or operational purpose;
- sender and receiver;
- required timeliness, volume, format, confidentiality, and acknowledgment;
- operating environment and anticipated degradation;
- authorized and available capabilities at both ends.

## 2. Select Paths In Order

For each P/A/C/E tier, capture the full path record in `templates/pace-plan-worksheet.md`. Select only plan-local capabilities supplied or verified by the user.

Primary is the normal method. Alternate, Contingency, and Emergency are progressively used when the approved trigger confirms the current method cannot meet the need. If the group has no feasible Emergency communications method, keep that tier as an owned gap. A preauthorized no-communications procedure may describe what happens in that condition, but it does not turn the missing communications path into a feasible tier.

## 3. Map Dependencies

List dependencies before deciding that paths are distinguishable:

- endpoint device and operator;
- local and remote power;
- network, provider, tower, repeater, gateway, or relay;
- physical site and geographic route;
- authentication, account, directory, or addressing service;
- specialized staff, transport, supplies, or environmental conditions.

Compare each fallback with every preceding tier. Different product names do not prove independence. Mark shared dependencies and ask the plan owner whether the remaining risk is acceptable.

## 4. Apply The Quality Gate

For every tier, answer with evidence:

| Test | Pass evidence |
|---|---|
| Feasible | Both endpoints have working capability and trained participants. |
| Acceptable | Establishing the path does not interfere with concurrent operations. |
| Suitable | The path can carry the required information in the required conditions. |
| Distinguishable | Failure of the preceding path does not predictably disable this path. |
| Complete | The method, trigger, procedures, evidence, owner, and handoff are explicit. |

Use `UNKNOWN`, an owner, and a validation action when evidence is missing. Never convert an unknown into a pass.

## 5. Review The Whole Plan

Check for uncovered communication pairs, one-sided endpoint capability, shared power or infrastructure, undocumented authorities, ambiguous transition criteria, sensitive details stored in an inappropriate location, and paths that have never been exercised.

Return the plan for owner review when any blocking unknown remains. Do not solve a missing local fact by generating an example that resembles a real operational value.
