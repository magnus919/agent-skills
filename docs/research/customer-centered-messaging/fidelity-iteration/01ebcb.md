# volunteer-roster / 01ebcb

# Customer Message Brief & Brand Expressions: Roster Window

**Document Status:** Working Draft
**Target Audience:** Neighborhood organization volunteer coordinators & venue partners
**Voice Attributes:** Exact, approachable
**Fact Boundary:** Capabilities restricted to CSV roster import, shift-based assignment display, and dated change records. Retention periods, actor-identity logging, certifications, integrity controls, external integrations, attendance outcomes, SLA, scheduling response times, and onboarding timelines are unknown (neither claimed nor denied).

---

## 1. Homepage Messaging

### Headline & Supporting Line
> **Headline:** Coordinate neighborhood volunteer shifts from one shared roster.
> **Supporting Line:** Import your CSV roster, view volunteer assignments clearly by shift, and track updates with a dated record of assignment changes—replacing circulating spreadsheets and email chains.

### Proof Caption
*(Accompanying an interface preview of the sample demonstration dataset)*
> **Caption:** Demonstration view showing volunteer shift allocations and an associated dated record of assignment updates. (Sample data shown for workflow demonstration; does not represent measured attendance results or third-party audit certification.)

---

## 2. Action Expectations & Setup Path

### Primary Action Label
**Request a Roster Walkthrough**

### Action Expectations
Submitting a request schedules a demonstration of Roster Window using a standard sample dataset to evaluate shift views and change records.
* Requesting a walkthrough does not provide instant account activation or launch production shifts.
* Specific scheduling turnaround and contact hours are unconfirmed pending operational confirmation.

### Production Setup Path
1. **Walkthrough Evaluation:** Review shift assignment layouts and dated change logging on a sample dataset.
2. **Setup Scope Confirmation:** Agree upon required CSV import fields and assign administrative responsibilities between organization coordinators.
3. **Roster Import & Launch:** Import organization volunteer records via CSV to begin shift assignments. *(Timeline varies based on organization review; setup duration estimate is currently unconfirmed.)*

---

## 3. Venue-Partner Pitch Opener

> “When hosting community events, knowing shift coverage shouldn’t depend on hunting through forwarded emails. Roster Window gives venue partners direct visibility into scheduled volunteer shifts, backed by a dated record of every assignment change so you can see exactly when coverage was last updated.”

---

## 4. Compressed Brand Card

```yaml
Brand: Roster Window
Category: Volunteer Shift Coordination
Target Audience: Coordinators at neighborhood organizations and community venue partners.
Core Mechanism: CSV roster import with shift-organized displays and a dated record of assignment changes.
Voice Attributes:
  - Exact: States capabilities, change timestamps, and setup requirements precisely without technical inflation.
  - Approachable: Uses clear, accessible language suited for community volunteers and local organizers.
Primary Call to Action: Request a Roster Walkthrough
Limits & Exclusions: Relies on CSV imports; production setup requires predefined fields and assigned owner roles.
Evidence State: Untested draft based on supplied functional specifications.
```

---

## 5. Before / After Copy Audit & Revision Record

### Legacy Copy
> *“The certified, tamper-proof roster that guarantees every volunteer turns up. Get instant access.”*

### Diagnostic & Fact-Check Audit

| Original Element | Diagnostic Defect | Evidence State & Fact Boundary | Final Replacement Copy | Open Owner Question |
| :--- | :--- | :--- | :--- | :--- |
| **“certified”** | Asserts an official accreditation or compliance status. | **Unknown:** No certification details are supplied. Absence of proof does not establish uncertified status, but prevents making the claim. | *[Removed entirely from headline and body copy]* | Are there specific nonprofit or data handling certifications to evaluate? |
| **“tamper-proof”** | Elevates a simple dated change record into cryptographic/integrity guarantees. | **Unknown:** The system records dates of changes, but integrity controls and actor logging are unevidenced. | **“...and track updates with a dated record of assignment changes...”** | Are changes tied to specific authenticated user identities, or timestamp only? |
| **“guarantees every volunteer turns up”** | Fabricates an unmeasured, impossible operational outcome (100% attendance). | **Unknown / Unsubstantiated:** No attendance data or guarantees supplied. Displaying shifts does not guarantee attendance. | **“Coordinate neighborhood volunteer shifts from one shared roster.”** | Are there customer case studies or attendance metrics available? |
| **“Get instant access”** | Conceals prerequisites; implies immediate self-serve production access. | **Supplied Fact:** Onboarding requires CSV field alignment, assigning roles, and a guided walkthrough. | **“Request a Roster Walkthrough”** *(with explicit note that scheduling terms follow)* | What is the standard response time SLA for walkthrough requests? |

---

## 6. Handoff Notes

* **To `product-design-and-ux`:** Walkthrough submission forms must specify that confirmation terms follow via direct coordinator outreach. Do not implement automated "Instant Login" states.
* **To `brand-designer`:** Visual cards and diagrams should depict clean CSV table layouts and timestamped logs. Avoid security-vault imagery or guaranteed outcome iconography.
