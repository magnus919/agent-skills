# Interface Contract

## Identity

- Interface/operation and owner:
- Consumer job and domain outcome:
- Style, direction, contract format, and exact contract/dialect version:
- Authentication scheme, credential transport, scopes/permissions, and object/action authorization requirement:

## Request Or Subscription

- Method/channel/operation and its protocol semantics:
- URI, parameters, content negotiation, media type/serialization, or channel binding:
- Inputs: type, requiredness, null/absence, defaults, units/time, validation:
- Preconditions, validators, concurrency token, and cache interaction:
- Idempotency/retry contract, if mutating:

## Response Or Delivery

- Success/acceptance/completion statuses or signals and representations:
- Cacheability, freshness, validators, `Vary`, and invalidation, if applicable:
- Collection filter/sort/order/pagination semantics, if applicable:
- Event/stream envelope, delivery, ordering, duplicate/gap/replay behavior, if applicable:
- Error type/code, retryability, correlation, safe detail, and rate/resource-limit behavior:

## Evolution And Evidence

- Known consumer assumptions and generated tooling:
- Examples and negative examples:
- Compatibility assessment reference:
- Provider, consumer, and deployed-boundary tests:
