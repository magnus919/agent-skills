# Evidence Base

This file separates directly inspected evidence from repository design decisions. Access date for all web sources below: 2026-07-26.

## Retained Sources

### CISA / NCSWIC: Leveraging the PACE Plan into the Emergency Communications Ecosystem

- Publication page: https://www.cisa.gov/resources-tools/resources/leveraging-pace-plan-emergency-communications-ecosystem
- Inspected PDF: https://www.cisa.gov/sites/default/files/2024-10/2024_NCSWICPTE_Leveraging_PACE_Plan_Emergency_Comms_Ecosystems.pdf
- Issuer: Cybersecurity and Infrastructure Security Agency, with the National Council of Statewide Interoperability Coordinators Planning, Training, and Exercise Committee
- Availability: live; publication page uses a 2024 file path, while the document footer says "As of 2023"
- Authority class: primary-direct

Supported claims and locators:

| Claim | Locator |
|---|---|
| PACE plans establish redundant options when primary communications are disrupted or degraded | PDF page 1, Overview |
| A proposed plan should be feasible, acceptable, suitable, distinguishable, and complete | PDF page 1, Groundwork |
| Distinguishable backup paths must not rely on the impacted method or transmission medium | PDF page 1, Groundwork |
| Plans should identify essential functions, authorized and available capabilities, limitations, personnel, and logistics | PDF page 1, Groundwork |
| Users should be comfortable with backup systems, and organizations should practice plans in training and exercises | PDF page 2, Developing the PACE Plan |
| Primary is day-to-day; Alternate backs up Primary; Contingency follows failure of Primary and Alternate; Emergency follows failure of the other levels | PDF page 2, Developing the PACE Plan |
| Reusing a shared device or communications path does not provide useful progression | PDF page 2, Developing the PACE Plan |
| Planning should account for outgoing and incoming capability and geographic effects at both ends | PDF page 2, Developing the PACE Plan |
| PACE planning is collaborative and needs technical, operational, and administrative expertise | PDF page 3, Considerations |
| Some organizations may lack resources for four communication methods, and Emergency may need to represent a no-communications condition | PDF page 3, Considerations |
| Organizations must define trigger points between levels based on confirmed failure of the current mode | PDF page 4, PACE Triggers |
| Regular training and exercises identify issues and lead to improvements | PDF page 4, Training and Exercises |

This document does not prescribe a daily, monthly, quarterly, semiannual, or annual exercise cadence. It does not mention HSEEP, hot washes, AAR/IP workflows, corrective-action matrices, setup-time metrics, or success-rate metrics.

### GitHub Issue #159

- URL: https://github.com/magnus919/agent-skills/issues/159
- Issuer: repository owner
- Publication date: 2026-07-27T00:25:33Z
- Availability: live at access time
- Authority class: primary-direct design contract
- Locator: issue body, "Proposed change" and "Scope"
- Contribution: defines the requested skill scope, required path fields, four reusable artifacts, authority and unknown-fact safeguards, five eval scenarios, and owner-approved completion condition.

Issue requirements are repository product requirements, not external PACE doctrine.

### Wikipedia: PACE (communication methodology)

- URL: https://en.wikipedia.org/wiki/PACE_(communication_methodology)
- Issuer: Wikimedia community contributors
- Publication date: continuously edited; inspected revision was last edited 2026-07-01
- Availability: live at access time
- Authority class: secondary-direct
- Locator: lead, "Order and scope," and "Development of PACE plans"
- Contribution: discovery aid and summary of military-origin terminology.

Normative skill instructions do not depend on this source where the inspected CISA guide or issue contract provides direct support.

## Excluded Or Limited Sources

| Source | Decision | Reason |
|---|---|---|
| Michael S. Ryan, "A Short Note on PACE Plans" | Indirect only | The original link was unavailable during research; only a secondary quotation was inspected. |
| DHS NIFOG v1.4 | Indirect only | The original link was archived and its relevant text was observed only through a secondary source. |
| ARRL ARES Plan, July 2025 | Excluded from normative claims | The earlier research asserted PACE content without preserving a directly inspected supporting passage. |
| CISA "What is a PACE Plan" announcement | Excluded as redundant | It adds awareness messaging but no needed operational detail beyond the retained guide. |
| HSEEP doctrine | Excluded | No directly inspected HSEEP source was retained for this implementation, and issue #159 does not require HSEEP conformance. |

## Repository Design Decisions

The six-stage workflow, explicit `UNKNOWN / OWNER / VALIDATION ACTION` notation, combined exercise/AAR template, troubleshooting sequence, and completion checklist are design decisions derived from issue #159 and repository conventions. They are not represented as universal PACE doctrine.

The skill deliberately omits a CLI. The work is judgment- and plan-local-data-heavy; no repeated deterministic computation justifies executable code.
