# Instrumentation QA Checklist

Use this checklist to verify that event instrumentation produces trustworthy data before any metric computed from those events appears on a dashboard or feeds a decision. Run the checklist for every new event and for existing events after any change to the instrumentation, pipeline, or metric definition.

## Checklist Header

| Field | Value |
|-------|-------|
| **Event(s) under test** | _[fill: event name(s)]_ |
| **QA owner** | _[fill: person running the QA]_ |
| **Date** | _[fill: date]_ |
| **App version** | _[fill: version that includes this instrumentation]_ |
| **Environment** | _[fill: staging / production / both]_ |

## 1. Client-Side Verification

Verify that events fire correctly at the point of instrumentation.

- [ ] **Trigger correctness:** Event fires on the intended user action or system condition, and only on that condition. No false positives (firing when it shouldn't) or false negatives (not firing when it should).
- [ ] **Property completeness:** All required properties are present on every event occurrence. Optional properties are present when their condition is met.
- [ ] **Property accuracy:** Property values reflect the actual application state at the time of the event. No stale values from previous screen state, no default values where a real value should be.
- [ ] **No duplicate firing:** The event does not fire multiple times for a single user action. Verify across: double-click, rapid navigation, page refresh, back-button, and app background/foreground transitions.
- [ ] **Timing accuracy:** The event timestamp reflects when the action occurred, not when the event was queued or flushed. Skew between client time and server time is within acceptable bounds.
- [ ] **Offline handling:** Events generated while offline are queued and sent when connectivity returns. Order is preserved or explicitly documented as not guaranteed.

## 2. Server-Side Verification

Verify that events are correctly received and processed.

- [ ] **Ingestion:** Event reaches the ingestion endpoint. HTTP 200 for valid events. Appropriate error codes for malformed events (4xx, not 5xx for client errors).
- [ ] **Schema validation:** Event structure matches the tracking plan schema. Unknown properties are handled per policy (dropped, logged, or passed through). Missing required properties trigger an alert.
- [ ] **Identity stitching:** Events from the same user across sessions, devices, and authentication states are attributed to the correct user identity. Anonymous-to-known-user transitions are handled correctly. Identity merge rules produce the expected attribution.
- [ ] **Timestamp integrity:** Server timestamp is recorded at ingestion time. Client timestamp is preserved. Late-arriving events (beyond acceptable delay) are flagged.
- [ ] **Deduplication:** Duplicate events (same event_id) are detected and handled. Exactly-once semantics or at-least-once with idempotent consumers is confirmed.

## 3. Pipeline Verification

Verify that events survive the data pipeline intact.

- [ ] **Schema compatibility:** Event schema is compatible with downstream consumers (data warehouse tables, analytics models). No silent column drops or type coercion.
- [ ] **No silent drops:** Events are not dropped by pipeline filters, sampling, or rate limiting without explicit configuration. Drop rate is monitored and within SLA.
- [ ] **Latency:** End-to-end latency from event fire to availability in the analytics system is within SLA. Pipeline backlog is monitored.
- [ ] **Transformation correctness:** Any pipeline transformations (enrichment, filtering, aggregation) produce correct results. Test with known input and verify output.

## 4. End-to-End Verification

Verify that the metric computed from events matches reality.

- [ ] **Manual walkthrough:** Perform a known set of actions that should produce a predictable metric value. Verify that the metric on the dashboard matches the expected value within acceptable tolerance.
- [ ] **Metric formula verification:** The SQL or analytics query that produces the metric is reviewed and confirmed to match the metric definition in the tracking plan. No off-by-one errors, incorrect join conditions, or misunderstood filter semantics.
- [ ] **Edge case coverage:** Test edge cases: new user (no history), returning user after long absence, user with very high activity volume, user who authenticates mid-session, user who opts out of tracking.
- [ ] **Dashboard reconciliation:** For metrics that appear on multiple dashboards, verify that values are consistent across dashboards or that any differences are explained by documented filter or timing differences.

## 5. Data Quality Monitoring Setup

Verify that ongoing data quality monitoring is configured.

- [ ] **Null rate alert:** Alert fires when required property null rate exceeds threshold.
- [ ] **Freshness alert:** Alert fires when events are delayed beyond SLA.
- [ ] **Volume anomaly alert:** Alert fires when event volume deviates significantly from baseline.
- [ ] **Cardinality alert:** Alert fires when property cardinality exceeds expected bounds.
- [ ] **Distribution drift alert:** Alert fires when property value distribution shifts significantly (for categorical properties).

## Summary

| Layer | Status | Notes |
|-------|--------|-------|
| Client-side | _[fill: pass / fail / partial]_ | _[fill: issues found]_ |
| Server-side | _[fill: pass / fail / partial]_ | _[fill: issues found]_ |
| Pipeline | _[fill: pass / fail / partial]_ | _[fill: issues found]_ |
| End-to-end | _[fill: pass / fail / partial]_ | _[fill: issues found]_ |
| Monitoring | _[fill: pass / fail / partial]_ | _[fill: issues found]_ |

**QA verdict:** _[fill: approved / conditionally approved (list conditions) / rejected]_

**Conditions for re-QA:** _[fill: what changes would require re-running this checklist]_
