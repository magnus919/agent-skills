# Escalation Path and Closed-Loop Feedback Closure

> Two related records: (A) the escalation path definition — from signal to
> decision-maker, with explicit human-judgment gates — and (B) the closed-loop
> feedback closure record — tracing customer insight through product change
> to customer communication.

---

## A. Escalation Path

### Path Definition

| Field | Value |
|---|---|
| **Escalation path name** | _[e.g., "Account Health Decline — Tier 1"]_ |
| **Trigger signal** | _[what evidence triggers this escalation]_ |
| **Trigger threshold** | _[e.g., "2 consecutive health reviews with declining trend in any dimension"]_ |
| **Escalation owner** | _[named role, not a system]_ |
| **Review cadence** | _[how often the escalation is reviewed]_ |

### Decision Options

The decision-maker must have at least two options. A single forced path is not
permitted.

| Option | Description | When Appropriate |
|---|---|---|
| 1. _[option name]_ | _[description]_ | _[criteria]_ |
| 2. _[option name]_ | _[description]_ | _[criteria]_ |
| 3. _[option name]_ | _[description]_ | _[criteria]_ |

### Evidence Package

What evidence accompanies the escalation to the decision-maker:

- [ ] Health/risk record (current assessment)
- [ ] Trend data (last N reviews)
- [ ] Success-plan status (milestone achievement)
- [ ] Previous escalation history (if any)
- [ ] Recommended action (from CS team, advisory only)

### Decision Record

| Field | Value |
|---|---|
| **Escalation date** | _[date]_ |
| **Decision-maker** | _[name and role]_ |
| **Decision** | _[which option was chosen]_ |
| **Rationale** | _[why this option]_ |
| **Action assigned to** | _[name]_ |
| **Action deadline** | _[date]_ |
| **Follow-up review date** | _[date]_ |

### Fallback (No-Decision Path)

If no decision is made by the deadline:

- **Escalate to**: _[next level of authority — named role]_
- **Never**: auto-act, silently do nothing, or close without a decision.

### Escalation History

| Date | Trigger | Decision | Outcome | Reviewer |
|---|---|---|---|---|
| _[date]_ | _[signal]_ | _[decision]_ | _[outcome]_ | _[name]_ |

---

## B. Closed-Loop Feedback Closure

### The Loop

```
Customer Insight → Validate → Product Decision → Implement → Communicate Back → Close Loop
```

Every step is recorded. "Communicate Back" is mandatory.

### Step 1: Customer Insight

| Field | Value |
|---|---|
| **Source** | _[customer name, QBR, support interaction, survey, etc.]_ |
| **Date received** | _[date]_ |
| **Insight** | _[what the customer said or what was observed]_ |
| **Type** | _[feature request / defect / friction / praise / suggestion]_ |
| **Recorded by** | _[name]_ |

### Step 2: Validation

Is this a pattern or an isolated observation?

| Field | Value |
|---|---|
| **Validation method** | _[e.g., "checked 3 similar accounts; pattern confirmed in 2 of 3"]_ |
| **Finding** | _[pattern confirmed / isolated / needs more data]_ |
| **Evidence** | _[what was checked and what was found]_ |

### Step 3: Product Decision

| Field | Value |
|---|---|
| **Decision** | _[build / defer / decline]_ |
| **Decision-maker** | _[name and role]_ |
| **Rationale** | _[why this decision]_ |
| **If build**: target release | _[release or timeframe]_ |
| **If defer**: revisit date | _[when to reconsider]_ |
| **If decline**: reason communicated | _[why it was declined]_ |

### Step 4: Implementation

_Only if decision is "build."_

| Field | Value |
|---|---|
| **What changed** | _[the product change made]_ |
| **Release date** | _[date]_ |
| **Verified by** | _[name]_ |

### Step 5: Communicate Back to Customer

**Mandatory.** The customer must know what happened with their feedback.

| Field | Value |
|---|---|
| **Communication date** | _[date]_ |
| **Method** | _[email, QBR, call, in-product message, etc.]_ |
| **Message** | _[summary of what was communicated]_ |
| **Customer response** | _[acknowledgment, satisfaction, follow-up needed]_ |

### Step 6: Close Loop

| Field | Value |
|---|---|
| **Closure date** | _[date]_ |
| **Loop status** | _[closed / partially closed (communication sent but response pending) / blocked]_ |
| **Closed by** | _[name]_ |

### Feedback-Loop Summary (for QBR)

| Open Loops | In Progress | Closed (this period) |
|---|---|---|
| _[count]_ | _[count]_ | _[count]_ |

---

## Combined Record Reference

For a single customer engagement that combines escalation and feedback
closure — e.g., an escalation triggered by a customer insight that leads
to a product change — reference both sections. The escalation path (A)
handles the governance of the decision; the feedback closure (B) handles
the traceability of the customer's voice through to communication.
