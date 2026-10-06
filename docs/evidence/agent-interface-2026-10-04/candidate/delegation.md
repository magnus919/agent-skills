# Cross-service billing correction flow

## Roles and authority

The customer owns the desired outcome and remains the decision-maker. Identify the verified customer principal, external agent host/client, authenticated agent or integration principal, billing account, and both service identities. A request typed to the customer’s agent communicates intent; it is not automatically product-recognized authorization. Before each consequential service operation, verify the integration principal, target account, exact correction, scope, and current permission. If the product cannot distinguish the customer from the agent or cannot constrain the change to the approved target and payload, surface that limitation before execution and route to an authorized manual path.

## Proposed flow

1. The agent submits a request with a stable task reference. The product displays a reviewable plan naming both services, the billing object, requested correction, expected effect, and data to be shared. Show what each service may read or change and what requires separate approval.
2. The customer can correct the amount/reason, narrow scope, approve the exact proposed action, reject, or leave the work pending. Bind approval to the normalized target, operation, payload/version, actor, and expiry. Any change to target or material payload invalidates approval and requires a new decision.
3. After approval, recheck authorization at each service’s commit boundary. Track each action independently as pending, confirmed, failed, denied, or unknown. Acknowledge progress with an operation reference and timestamp. Confirm only from each product’s observable state or audit evidence, not from the agent’s statement or a request acknowledgment.
4. If service one commits while service two is pending, present “partially applied” and identify the confirmed correction, unresolved action, and risk of waiting. Do not claim the overall correction is complete. If customer authorization is revoked, stop initiating new actions immediately and send cancellation to in-flight work where supported. Explain that revocation may not reverse a completed commit or prevent an in-flight action from finishing until the service confirms its state.

## Recovery

On cancel/revoke race, reconcile both service states before retry or compensation. Preserve operation IDs, exact approved payload, confirmed product state, last update, and owner so the customer can return after app/agent closure. If an action timed out, label it unknown and query status; never blindly replay. Retry only when the service contract guarantees deduplication or confirms no effect. A completed correction may require a separately authorized compensating transaction; cancellation does not imply rollback. If compensation is unavailable or unsafe, provide a support/escalation route and show the remaining state plainly. Offer manual completion through the product, with the same context and permission checks. If the return reference expires, reauthenticate, reauthorize, and retrieve status from durable operation identity; do not assume the external conversation is available.

## Acceptance evidence

Test correct and mismatched human/integration identities, scope overreach, target/payload changes after approval, permission revoked before service two, revoke racing with each commit, timeouts with and without effects, duplicate retries, and host disconnection. Evidence should include the approval binding, each service’s authorization decision, operation state/audit record, and current billing object. Review copy for clear distinctions among cancel requested, cancellation confirmed, partial effect, unknown effect, and completed outcome. Product and service owners must decide whether service one can be compensated, who owns pending work after revocation, and what audit evidence is exposed. Keep these as explicit decisions if unresolved; do not infer a cross-service transaction or atomic rollback.
