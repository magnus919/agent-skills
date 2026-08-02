# Landscape-backed decision framework

The goal is not to find the most famous project. The goal is to identify a small set of candidates that could satisfy the user's constraints, explain what the catalog evidence does and does not establish, and choose the cheapest next validation step.

## 1. Decision intake

Write these down before filtering:

| Dimension | Questions |
|---|---|
| Capability | What outcome must the technology provide? What is explicitly out of scope? |
| Workload | Protocols, data shape, latency/throughput, durability, tenancy, failure behavior, and peak conditions? |
| Boundary | Cloud, self-hosted, air-gapped, managed service, Kubernetes, VMs, edge, or mixed? |
| Integration | Existing APIs, languages, storage, identity, networking, observability, and deployment tooling? |
| Operations | Who owns it at 02:00? What skills, on-call burden, upgrade cadence, and support path are acceptable? |
| Governance | License policy, security review, data residency, supply-chain rules, and required project governance? |
| Decision economics | Time to first useful result, migration cost, recurring cost, lock-in, and reversibility? |
| Evidence bar | What must be proven before a proof of concept, production approval, or adoption decision? |

Mark each requirement as `hard`, `preferred`, or `unknown`. Do not silently convert an unstated preference into a hard filter.

## 2. Candidate discovery and filtering

Use the Landscape category/subcategory and search fields to find a broad candidate set, then filter in this order:

1. **Capability relevance:** Does the project actually address the requested outcome? A category label is only a discovery hint.
2. **Hard constraints:** Remove candidates that fail explicit deployment, license, maturity, language, or repository requirements. Explain every exclusion.
3. **Evidence completeness:** Prefer candidates whose current documentation, source, release, security, and operations evidence can be inspected. Missing evidence is a risk, not proof of failure.
4. **Operational fit:** Compare the work the team must operate, integrate, secure, upgrade, and recover. This usually requires sources outside the Landscape.
5. **Ecosystem signals:** Use repository activity, release recency, contributors, and CNCF lifecycle as directional evidence. Keep each signal separate so a large star count cannot hide weak operational fit.

A shortlist should be bounded enough to compare. Three to five candidates is a useful working target, not a quota; keep more when the decision genuinely has several distinct solution families.

## 3. Comparison dimensions

For each finalist, fill in a table like this:

| Dimension | Evidence | Judgment |
|---|---|---|
| Capability fit | What the project and current docs explicitly provide | How directly it satisfies the stated outcome |
| Deployment fit | Supported runtime and topology | Whether it fits the target boundary without an unproven adapter |
| Operational burden | Components, dependencies, upgrades, backups, failure recovery | Who can operate it and what must be built around it |
| Integration fit | APIs, protocols, SDKs, identity, observability | Migration and adoption friction |
| Lifecycle and governance | CNCF maturity plus project release/security/governance evidence | Risk appropriate to the user's horizon |
| Community and ecosystem | Repository and ecosystem signals | How much external evidence exists, without treating popularity as support |
| License and policy | Exact repository/dependency/license sources | Whether review is required before adoption |
| Reversibility | Data and API portability, exit path, migration options | Cost of being wrong |
| Unknowns | Unverified assumptions and missing evidence | The next probe or experiment |

Use labels such as `observed`, `inferred`, and `unknown` in the evidence or judgment column. Do not collapse them into one confidence number unless the user supplies the weighting model.

## 4. Recommendation shape

A decision-safe recommendation contains:

1. **Conditional preference:** “Choose A if the hard constraints remain X and Y.”
2. **Credible alternative:** “Choose B instead if Z matters more.”
3. **Exclusions:** What was filtered out and why, including candidates that looked popular but failed a real constraint.
4. **Trade-offs:** The principal operational, integration, security, economic, and lock-in costs.
5. **Disproof test:** The smallest experiment or source check that could overturn the preference.
6. **Adoption boundary:** What is safe to prototype now, what needs review, and what should not be promised yet.

Do not write “best,” “production-ready,” “most secure,” or “standard” without a source and scope that supports the claim. Prefer “best fit for the stated constraints” and name the constraints.

## 5. Validation plan

Turn the recommendation into a bounded sequence:

- verify the project's current installation and compatibility documentation;
- build the smallest representative path using the user's real interface or protocol;
- exercise a realistic workload, tenant/security boundary, and failure mode;
- measure latency, throughput, resource use, recovery, and operator steps against explicit thresholds;
- test upgrades, rollback, data/API export, and observability;
- review license, security advisories, dependency provenance, and ownership;
- record the result in an ADR or technology-radar entry.

A successful catalog query is discovery evidence. It is not a successful proof of concept.
