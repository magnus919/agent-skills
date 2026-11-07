# Domain architecture and renewal economics

Read when choosing independent domains, subdomains or sections for a portfolio. Cost savings and search effectiveness are different hypotheses. Use `templates/domain-decision-record.md`; do not infer deployment or purchase permission.

## Compare alternatives before choosing

- **Separate registrable domains:** independent registration/transfer assets, but shared registrar credentials, code, hosting and acquisition channels can still correlate failures. Use the Public Suffix List rather than assuming the last two labels identify a registrable domain.
- **Subdomains:** fewer registrations, separate browser origins, but parent registration/DNS dependency and potentially broad cookie scope. Independent hostnames are not independently transferable registrations.
- **Subdirectories:** fewer registrations and one origin; routing to separate backends does not create browser-origin isolation.

Map brand ownership, audience/intent overlap, provider relationships, exit/transfer requirements, access boundaries and recovery owners. Choose for useful destinations and verifiable business identity, not to manufacture search-result diversity. Google supports site names at domain/subdomain level, while its site-diversity system generally groups subdomains with the parent. Neither observation establishes equal ranking or conversion performance. Avoid guarantees about shared authority, isolation, or penalties across architectures.

## Renewal-first model

For each architecture compute annual registration renewal as sum of exact-name renewal prices, not promotional acquisition prices. Record extension, premium status, currency, taxes/fees, quote date and future-price uncertainty. Then add DNS, TLS, hosting, traffic/build costs, backups, email, monitoring, privacy/compliance work, support labor, migrations and failed/retired experiments. Allocate shared costs explicitly; report cash cost separately from labor and opportunity cost.

Illustration only: 1,000 registrations at US$11.81 annual renewal cost US$11,810, versus US$118.10 for 10 parent registrations. This arithmetic excludes every other cost and proves no commercial equivalence. The nonpremium .com price was observed at Porkbun on 2026-11-06; re-quote before any decision. Model price increases and delayed revenue, and show break-even against collected contribution rather than gross customer sales.

## Capacity and failure checklist

A thousand hostnames do not imply a thousand free hosting projects. Verify project/account limits, custom-domain/wildcard support, DNS record quotas, certificate issuance/renewal limits, build/API/traffic quotas, commercial-use terms and billing alerts. Distinguish wildcard DNS, wildcard certificates and wildcard application routing: one does not supply the others. Define tenant routing, unknown-host rejection, cookie boundaries, credential isolation, renewal alerts and recovery tests with the owning infrastructure skills.

For example, Cloudflare Pages documentation checked 2026-11-06 specifies no wildcard custom domains and a 100-project/account limit that is not routinely increased (larger portfolios are directed to Workers for Platforms); its Free DNS record limit for newly created zones is 200. These are dated provider constraints, not universal limits or a recommendation to evade quotas. A deliberately designed multi-tenant service may fit better, but needs architecture/security review. Route implementation to `data-architect`, the hosting/tool skill and security owners; SEO owns the search decision, not deployment.

## Evidence-generating pilot

Compare matched audience/intent and site-age cohorts; record content quality, brand, link history, geography, template and offer confounders. Track renewal/operating costs, index coverage, search clicks, observed handoffs, partner-confirmed outcomes and collected contribution separately. Use cluster-aware experiment design with `data-scientist` because sites on a parent domain share exposure. A cheap architecture with weak outcomes is not a win; one successful domain is not portfolio evidence. Set a bounded budget, observation period and expand/repair/consolidate/retire criteria before rollout.

## Primary sources

Reviewed 2026-11-06; recheck before implementation or pricing decisions.
- https://porkbun.com/products/domains — renewal price example, not future quote.
- https://developers.google.com/search/docs/appearance/site-names — domain/subdomain site-name scope.
- https://developers.google.com/search/docs/appearance/ranking-systems-guide — site diversity, not an architecture experiment.
- https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy — browser origin distinction.
- https://developers.cloudflare.com/pages/platform/limits/ — project constraints.
- https://developers.cloudflare.com/pages/configuration/custom-domains/ — custom-domain support.
- https://developers.cloudflare.com/dns/manage-dns-records/reference/wildcard-dns-records/ — wildcard DNS scope.
- https://developers.cloudflare.com/dns/manage-dns-records/ — documented record quotas; verify account applicability.
