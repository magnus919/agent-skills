# Synthetic Scenario Probes

Use these probes to review a proposed design artifact. They use synthetic fixtures only and grade force coverage, traceability, privacy, accessibility routing, recovery, and observable evidence, not numbers of screens, states, or participants.

## Transactional Partial Commit

`Northstar Travel` reserves `DEMO-ITINERARY-42`. A submit may reserve an itinerary before payment confirmation times out. A later retry can duplicate a reservation. Cancellation becomes irreversible after a stated fulfillment boundary.

Expect entry conditions, validation preservation, pending/partial-commit visibility, retry and deduplication behavior, interruption/re-entry, cancellation, irreversible warning, recovery/support route, completion receipt, and no real payment fixture.

## Permissions-Heavy Workspace

`Atlas Review` has synthetic items owned by teams. Reviewers can annotate, owners can submit, administrators can archive, and auditors can only view history. Ownership can change while a reviewer has an item open; filters can return stale results and simultaneous edits can conflict.

Expect IA grounded in roles/findability, view versus action permissions, ownership change behavior, stale/conflict recovery, dense-data filtering tradeoffs, audit and recovery path, and completion evidence.

## Interrupted Responsive Flow

`Civic Permit Demo` saves a draft request. Content may be narrow or reflowed at zoom, localized text can expand, orientation can change, a keyboard/touch/assistive input method can be used, and connectivity can degrade before final submission.

Expect preserved context, save/re-entry, applicable offline/degraded behavior, text/reflow and input-mode contract, reduced-motion consideration, validation/recovery, and routing of detailed accessibility verification to `web-accessibility`.

## Review Questions

For each probe, ask: Which evidence supports the behavior? Which forces were considered or ruled out? What recovery is available? Which accessibility questions were routed? What data is synthetic? Which criterion can be observed after deployment?
