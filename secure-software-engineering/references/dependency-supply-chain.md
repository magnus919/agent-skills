# Dependency And Supply Chain

## Make The Decision Now

Decide whether a dependency, model, plugin, action, base image, or build tool is necessary; identify its maintainer, update path, permissions, licensing constraints, and compromise impact. Pin or constrain versions according to the ecosystem, then document how updates and vulnerabilities are evaluated.

## Evidence To Collect

- A reviewed dependency change, resolved lockfile or equivalent, source location, and documented license-obligation review by the authorized owner.
- Vulnerability assessment showing affectedness and disposition, not only scanner output.
- An SBOM in an agreed format such as CycloneDX 1.7 or SPDX 3.0.1, with component scope and generation time.
- Build provenance appropriate to the risk. SLSA v1.2 helps describe supply-chain integrity properties and evidence expectations.
- For AI systems, model, embedding, dataset, prompt-template, plugin, and tool-provider origin, version, access rights, and update path.

## What The Evidence Does Not Prove

An SBOM inventories declared components; it does not prove completeness, absence of vulnerabilities, secure configuration, or safe behavior. A provenance attestation supports a claim about a build's origin and process; it does not prove that source code, dependencies, or a model are benign. Verify signatures and predicates against the intended identity and policy rather than treating their presence as sufficient.

## Misuse To Avoid

- Floating version tags, unreviewed transitive upgrades, or dependency ownership assumptions.
- Giving CI, package installers, model plugins, or AI tools more permissions than their build task needs.
- Blocking a release on a raw vulnerability count without assessing reachability, exploitability, compensating controls, and an accountable exception.

Use SLSA v1.2, CycloneDX 1.7, and SPDX 3.0.1 from [source-index.md](source-index.md) as adopted standards or evidence formats, not universal requirements.
