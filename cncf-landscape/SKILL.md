---
name: cncf-landscape
description: >-
  Use this skill when discovering and comparing cloud-native technologies from the
  CNCF Landscape for an architecture or engineering decision. Query the live public
  Landscape API, filter candidates by capability, category, maturity, license, and
  repository signals, then produce an evidence-backed shortlist with trade-offs,
  unknowns, and validation steps. Do not use it as a substitute for project
  documentation, production-readiness testing, legal review, or general
  architecture methodology.
license: MIT
compatibility: Requires Python 3.8+ and outbound HTTPS access to landscape.cncf.io for live queries; no API key is required.
metadata:
  source_repo: https://github.com/cncf/landscape2
  api: https://landscape.cncf.io/api/
---

# CNCF Landscape technology selection

Use this skill to turn a capability or architecture problem into a defensible shortlist of cloud-native technologies. The Landscape is a discovery and evidence source, not a recommendation engine.

## When to load

Load this skill when someone:

- asks what projects or tools exist for a capability that is not in the current stack;
- wants to compare CNCF projects by maturity, category, repository signals, license, or ecosystem evidence;
- asks for a shortlist for an architecture decision, proof of concept, technology radar entry, or build-versus-buy discussion;
- needs to discover a CNCF project before reading its documentation or source repository.

## When not to use

- For operating or configuring a named technology, load its operational skill or use its authoritative documentation.
- For the general adoption/hold governance process, load [technology-radar](../technology-radar/SKILL.md) and use this skill only for candidate discovery and evidence.
- For broad platform architecture, data architecture, or API design without a Landscape discovery question, use the matching methodology skill.
- For procurement, contract, export-control, or licensing advice, treat this skill's license fields as discovery evidence and obtain qualified review.

## Decision workflow

1. **Frame the decision before searching.** Capture the capability, workload, interfaces, runtime and topology, scale and SLOs, data sensitivity, deployment model, team ownership, operational skills, budget, timeline, license constraints, and acceptable maturity risk. Separate hard constraints from preferences. If the user has not supplied these, ask for the smallest missing set rather than pretending that a category name is a requirement.
2. **Discover candidates from the live API.** Start with the bundled query tool:
   ```bash
   python3 scripts/landscape_query.py --help
   python3 scripts/landscape_query.py \
     --category "Observability and Analysis" \
     --subcategory Observability \
     --search tracing \
     --maturity graduated \
     --has-license --has-release \
     --sort stars --limit 10
   ```
   Load [references/api.md](references/api.md) when selecting an endpoint, interpreting a field, or diagnosing a response. Use the projects source for technology candidates. Use members or end-users only for ecosystem context; membership is not a product-quality signal.
3. **Apply hard filters first.** Filter by capability and category, then by explicit maturity, license, repository evidence, deployment constraints, or other user-supplied requirements. Do not turn stars, contributor counts, or CNCF maturity into implicit hard requirements unless the user asks for them.
4. **Inspect the shortlist.** Use the `id` returned by `projects/all.json` to fetch each project's per-record endpoint. Record the API endpoint and retrieval time. Read the project's own documentation, supported deployment paths, release history, source repository, license, and security/advisory material before making implementation claims.
5. **Compare fit, not fame.** Use [references/decision-framework.md](references/decision-framework.md) and [references/output-template.md](references/output-template.md). Distinguish:
   - **Observed:** fields returned by the Landscape or statements verified in project documentation;
   - **Inferred:** a reasoned implication, such as likely ecosystem reach from repository activity;
   - **Unknown:** a requirement the available evidence does not establish.
   Never rank a project solely by stars, CNCF maturity, membership, or a generated score.
6. **Make the recommendation conditional.** Name a best fit only against the stated constraints. Include credible alternatives, excluded candidates and the reason for exclusion, material trade-offs, reversibility and migration concerns, and the next experiment that could disprove the recommendation.
7. **Close with a validation plan.** Define a bounded proof of concept or documentation/source review that exercises the user's real interfaces, workload, security boundary, operability, upgrade path, and failure modes. A Landscape record can identify what to investigate; it cannot prove production readiness.

## Query tool contract

`scripts/landscape_query.py` is a read-only, non-interactive, standard-library client. It fetches one generated JSON snapshot, applies local filters, and writes JSON to stdout. Diagnostics go to stderr and failures return a non-zero exit code.

Useful filters include `--search`, `--category`, `--subcategory`, repeated `--maturity`, `--license`, `--country`, `--oss-only`, `--has-license`, `--has-release`, `--min-stars`, `--min-contributors`, `--sort`, and `--limit`. The default limit is deliberately bounded; use `--limit 0` only when the complete result set is needed.

The query tool does not score or recommend projects. Keep the raw records and explain any ranking or weighting in the decision artifact.

## Evidence discipline

- The CNCF maturity value describes the project's CNCF lifecycle status, not its fit, security, support contract, or operational simplicity.
- Repository stars and contributors are directional activity signals with snapshot and repository-selection caveats. They are not adoption, reliability, or support guarantees.
- A repository license field is a discovery signal, not a legal conclusion. Verify the exact repository, version, dependencies, and organizational policy.
- A latest-release field does not establish release quality, compatibility, patch policy, or support duration.
- Category and subcategory labels help find candidates; they do not establish that a project implements every part of the requested capability.
- When the API is unavailable or returns non-JSON content, report that limitation. Do not invent a current catalog, counts, or project status from memory.

## Completion criteria

The skill is complete when the response contains a bounded candidate set, the query/source evidence used to create it, explicit hard filters and assumptions, observed-versus-inferred distinctions, trade-offs and exclusions, unresolved risks, and a concrete validation next step. Stop and report the blocker if the Landscape API and the authoritative project sources needed for the decision are unavailable.
