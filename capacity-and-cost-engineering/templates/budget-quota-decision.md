# Budget / Quota Decision

Fill this template to define a budget threshold or quota/rate-limit enforcement decision with operational consequences.

## Budget definition

- **Scope:** _[fill: service, team, project, or platform — what this budget covers]_
- **Budget owner:** _[fill: name or role accountable for budget decisions]_
- **Period:** _[fill: monthly / quarterly / annual]_
- **Budget amount:** _[fill: $X per period]_
- **Cost attribution method:** _[fill: how costs are attributed to this scope — tags, account structure, manual allocation]_

## Threshold configuration

| Threshold | Type | Value | Trigger | Operational consequence | User-facing impact |
|-----------|------|-------|---------|------------------------|---------------------|
| _[fill: 70%]_ | Alert | _[fill: $Y]_ | _[fill: notification to budget owner + cost channel]_ | _[fill: review spending trend; no automated action]_ | _[fill: none]_ |
| _[fill: 90%]_ | Soft cap | _[fill: $Z]_ | _[fill: throttle non-critical workloads; reduce provisioning]_ | _[fill: autoscaling ceiling lowered; batch jobs deferred]_ | _[fill: degraded performance for non-core functions]_ |
| _[fill: 100%]_ | Hard cap | _[fill: $BUDGET]_ | _[fill: deny new resource provisioning; rate-limit ingress]_ | _[fill: requests above cap rejected with 429]_ | _[fill: service unavailable for requests exceeding cap]_ |

## Quota / rate-limit enforcement

- **Enforcement mechanism:** _[fill: API gateway rate limiter, resource-quota admission controller, cloud budget action, or equivalent]_
- **Rate-limit scope:** _[fill: per-user, per-IP, per-API-key, per-service, or global]_
- **Rate-limit value:** _[fill: e.g., 1000 requests/second, 500 concurrent connections]_
- **Quota period:** _[fill: per-second, per-minute, per-day, per-month]_
- **Hard vs burst:** _[fill: is there a burst allowance above the steady rate? what multiplier and duration?]_
- **Response when exceeded:** _[fill: HTTP 429 with Retry-After header, queued with backpressure, or denied]_
- **Monitoring:** _[fill: how is enforcement measured? rate-limit hit counter, quota-usage dashboard, alert on near-exhaustion]_

## Cost attribution

- **Attribution method:** _[fill: resource tags, account/project structure, label-based allocation, or manual]_
- **Shared cost allocation:** _[fill: how shared infrastructure costs are divided — proportional to usage, fixed split, or other]_
- **Attribution review cadence:** _[fill: monthly / quarterly]_

## Anomaly detection

- **Anomaly trigger:** _[fill: e.g., spend increase >30% day-over-day, or >15% week-over-week]_
- **Notification:** _[fill: who is notified and through what channel]_
- **Response procedure:** _[fill: triage steps — is it legitimate demand, a bug, a misconfiguration, or an attack?]_
- **Escalation:** _[fill: when does this become an incident? who is the incident commander?]_

## Assumptions

- [ ] _[fill: current spending pattern is representative of normal operation]_
- [ ] _[fill: cost attribution is accurate and complete — state assumption or evidence]_
- [ ] _[fill: budget amount is adequate for projected demand — or state what happens if not]_
- [ ] _[fill: any other unverified assumption]_

## Evidence sources

| Source | What it provides |
|--------|-----------------|
| _[fill: cost dashboard / cloud bill]_ | _[fill: current and historical spend data]_ |
| _[fill: capacity model]_ | _[fill: projected spend at demand forecast]_ |
| _[fill: ...]_ | _[fill: ...]_ |

## Ownership

- **Budget owner:** _[fill: name or role]_
- **Quota/rate-limit config owner:** _[fill: name or team that configures enforcement]_
- **Anomaly responder:** _[fill: name or on-call rotation]_
- **Approver:** _[fill: name of person who approved this budget/quota decision]_

## Tradeoffs

- _[fill: e.g., tighter quotas → earlier denial but more predictable cost]_
- _[fill: e.g., generous burst allowance → better user experience but cost-spike risk]_
- _[fill: e.g., hard cap at 100% budget → service may be unavailable; soft cap preferred if core functions can degrade gracefully]_
