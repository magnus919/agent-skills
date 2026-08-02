# Tracking Plan Template

A tracking plan is the contract that makes product events trustworthy. Fill one section per event or event group. This template is product-type-agnostic: use it for SaaS, internal tools, public services, or consumer products.

## Document Header

| Field | Value |
|-------|-------|
| **Product** | _[fill: product name]_ |
| **Version** | _[fill: semantic version, e.g. 1.0.0]_ |
| **Last updated** | _[fill: date]_ |
| **Owner** | _[fill: team or person accountable for this plan]_ |
| **Review cadence** | _[fill: e.g. quarterly, per-release]_ |

## Event Taxonomy

### Naming Convention

_[fill: Describe the naming pattern, e.g. `category_action_detail` (all lowercase, snake_case). Example: `search_query_submitted`, `checkout_payment_completed`.]_

### Standard Properties

These properties are included on every event unless otherwise noted:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `event_id` | UUID | yes | Unique identifier for this event occurrence |
| `timestamp` | ISO 8601 | yes | When the event occurred (client time) |
| `server_timestamp` | ISO 8601 | yes | When the server received the event |
| `user_id` | string | conditional | Authenticated user identifier (null if anonymous) |
| `anonymous_id` | string | conditional | Anonymous session identifier (null if authenticated) |
| `session_id` | UUID | yes | Session identifier (see Session Definition) |
| `platform` | string | yes | `web`, `ios`, `android`, `server`, `api` |
| `app_version` | string | yes | Application version that generated the event |

### Custom Property Rules

_[fill: Rules for custom properties — naming, types, allowed values, required vs optional, default behaviors, deprecation process.]_

## Identity Resolution

### User Identity Model

_[fill: Describe how users are identified across sessions, devices, and authentication states.]_

| State | Identifier | How assigned |
|-------|-----------|-------------|
| Anonymous (pre-signup) | `anonymous_id` | Generated client-side on first visit, stored in cookie/local storage |
| Authenticated (post-login) | `user_id` | Assigned by auth system, stable across sessions |
| Merged (multiple anonymous sessions) | `user_id` + `anonymous_id` history | Server-side identity graph merges anonymous IDs when user authenticates |

### Identity Merge Rules

_[fill: When a user authenticates, how are past anonymous events attributed? What happens on logout? What about shared devices?]_

## Session Definition

| Parameter | Value |
|-----------|-------|
| **Activity timeout** | _[fill: e.g. 30 minutes of inactivity ends a session]_ |
| **Absolute timeout** | _[fill: e.g. session ends after 4 hours regardless of activity]_ |
| **Midnight rollover** | _[fill: yes/no — does a new session start at midnight?]_ |
| **Cross-platform continuity** | _[fill: are web and mobile sessions linked? How?]_ |
| **Background/foreground** | _[fill: for mobile — does backgrounding end a session? After how long?]_ |

## Event Definitions

_[fill: One table per event. Create as many as needed.]_

### Event: _[fill: event name]_

| Field | Value |
|-------|-------|
| **Event name** | _[fill: exact event name per naming convention]_ |
| **Description** | _[fill: what user action or system event triggers this]_ |
| **Trigger** | _[fill: exact condition — e.g. "when user clicks 'Submit' and form validation passes"]_ |
| **Frequency** | _[fill: expected volume — e.g. "~10K/day at peak"]_ |
| **Owner (definition)** | _[fill: team or person]_ |
| **Owner (instrumentation)** | _[fill: team or person]_ |
| **Consumer(s)** | _[fill: which teams/dashboards/models depend on this event]_ |

#### Properties

| Property | Type | Required | Allowed values / constraints | Description |
|----------|------|----------|------------------------------|-------------|
| _[fill: property name]_ | _[fill: string, integer, float, boolean, enum, JSON]_ | _[yes/no/conditional]_ | _[fill: constraints]_ | _[fill: description]_ |

#### Data Quality Rules

| Rule | Threshold | Action on violation |
|------|-----------|-------------------|
| Null rate | _[fill: e.g. <1% for required properties]_ | _[fill: alert, investigation]_ |
| Freshness | _[fill: e.g. events received within 5 minutes of timestamp]_ | _[fill: alert]_ |
| Cardinality | _[fill: e.g. property X has <100 distinct values]_ | _[fill: alert if exceeds]_ |
| Volume | _[fill: e.g. ±50% of 7-day rolling average]_ | _[fill: alert]_ |
| Distribution | _[fill: e.g. no value >90% of events for enum properties]_ | _[fill: investigation]_ |

## Event Versioning and Deprecation

| Rule | Description |
|------|-------------|
| **Additive changes** | Adding new optional properties: minor version bump, no breaking change. |
| **Breaking changes** | Removing or renaming properties, changing types: major version bump, coordinate with consumers. |
| **Deprecation notice** | Events to be removed are marked deprecated for at least one review cycle before removal. |
| **Deprecation log** | _[fill: table of deprecated events with deprecation date, sunset date, and migration path]_ |

## Privacy and Consent

| Field | Value |
|-------|-------|
| **Consent boundary** | _[fill: which events require user consent before firing]_ |
| **Pre-consent events** | _[fill: which events are permitted before consent (must be minimal)]_ |
| **Opt-out handling** | _[fill: how events are handled when a user opts out of tracking]_ |
| **Data retention** | _[fill: how long raw events are retained]_ |
| **Deletion handling** | _[fill: how measurement continues when a user requests data deletion]_ |
| **Aggregation minimum** | _[fill: minimum cohort size for reporting — metrics with smaller cohorts are suppressed]_ |
| **Jurisdictional notes** | _[fill: GDPR, CCPA, or other regulatory considerations]_ |
