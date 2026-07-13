# Source Index

Use this manifest to select a source for a concrete decision, not to imply that every source is binding. A source becomes a requirement only when an organization, contract, regulator, or applicable policy adopts it. Versions and URLs were checked on 2026-07-13.

| Source | Exact version or release | Canonical URL | Source type and adoption context | Decision use |
|---|---|---|---|---|
| NIST Secure Software Development Framework | SP 800-218 v1.1, 2022-02 | https://doi.org/10.6028/NIST.SP.800-218 | U.S. guidance; adopt where policy or risk management calls for it | Organize security work and evidence across the lifecycle. |
| NIST SSDF AI Profile | SP 800-218A Final, 2024-07 | https://doi.org/10.6028/NIST.SP.800-218A | U.S. guidance for AI development practices | Adapt lifecycle controls for AI components and suppliers. |
| OWASP ASVS | stable 5.0.0, tag `v5.0.0_release`, 2025-05-30 | https://github.com/OWASP/ASVS/releases/tag/v5.0.0_release | Application security verification standard and control catalog | Select and test application control objectives. |
| OWASP Top 10 | 2025 | https://owasp.org/Top10/2025/ | Awareness and risk-categorization guidance | Communicate web application risk without substituting for a threat model. |
| OWASP API Security Top 10 | 2023 edition, verified 2026-07-13 | https://owasp.org/API-Security/editions/2023/en/0x11-t10/ | API risk-awareness guidance | Review object and function authorization, resource consumption, inventory, and third-party API use. |
| OWASP Cheat Sheet Series | retrieved 2026-07-13 | https://cheatsheetseries.owasp.org/ | Implementation guidance | Compare framework-specific patterns after choosing a control objective. |
| CISA Secure by Design | joint guidance, 2024 update | https://www.cisa.gov/securebydesign | Joint manufacturer guidance | Prefer secure defaults, ownership, and transparent evidence. |
| SLSA | v1.2 | https://slsa.dev/spec/v1.2/ | Supply-chain framework | Decide what build provenance claim to seek and verify. |
| CycloneDX | 1.7 | https://cyclonedx.org/specification/overview/ | SBOM and supply-chain standard | Choose an SBOM exchange format suited to consumers. |
| SPDX | 3.0.1 | https://spdx.github.io/spdx-spec/v3.0.1/ | SBOM, license, and software metadata standard | Choose interoperable component and license evidence. |
| MITRE ATLAS | retrieved 2026-07-13 | https://atlas.mitre.org/ | AI adversary behavior taxonomy | Describe AI threat techniques; it is not exhaustive. |
| OWASP Top 10 for Large Language Model Applications | release tag `2024`, titled `2025` | https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/releases/tag/2024 | LLM risk awareness guidance | Elicit prompt, tool, data, and model boundary risks. |

When citing a control, state the decision, selected source, version, evidence, and what would falsify the claim. Do not rely on unchecked section numbers; verify them against the exact release before using them.
