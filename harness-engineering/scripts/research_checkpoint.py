"""Offline teaching fixture: screen a reviewed evidence ledger, never accept a report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def screen(ledger):
    """Return a disposition and material gaps from the supplied snapshot."""
    require(isinstance(ledger, dict), "ledger must be an object")
    claims, sources, links = (ledger.get(k) for k in ("claims", "sources", "links"))
    require(all(isinstance(v, dict) for v in (claims, sources)), "invalid claims or sources")
    require(isinstance(links, list), "invalid links")
    budget, attempted = ledger.get("followup_budget"), ledger.get("reserved_followups")
    require(type(budget) is int and budget >= 0, "invalid follow-up budget")
    require(isinstance(attempted, list) and all(isinstance(x, str) for x in attempted), "invalid reservations")
    require(len(attempted) == len(set(attempted)) <= budget, "duplicate or excess follow-up reservations")
    require(bool(claims), "missing claim roster")

    reviews = {claim_id: [] for claim_id in claims}
    for link in links:
        require(isinstance(link, dict), "invalid claim link")
        c, s = link.get("claim"), link.get("source")
        require(isinstance(c, str) and c in claims and isinstance(s, str) and s in sources, "unknown claim or source")
        evidence = sources[s]
        require(isinstance(evidence, dict), "invalid source")
        state = link.get("review")
        relation = link.get("relation")
        require(state in ("proposed", "verified", "rejected"), "invalid review")
        require(relation in ("supports", "contradicts"), "invalid relation")
        if state == "verified":
            require(evidence.get("retrieval") == "captured", "verified link without capture")
            require(isinstance(evidence.get("revision"), str) and evidence["revision"]
                    and evidence["revision"] == link.get("source_revision"), "verified link has missing or stale revision")
            require(isinstance(link.get("locator"), str) and link["locator"].strip(),
                    "verified link without an evidence locator")
        reviews[c].append((link, evidence))

    gaps = []
    contradiction = False
    for c, rule in sorted(claims.items()):
        require(isinstance(rule, dict) and type(rule.get("primary_required")) is bool
                and type(rule.get("min_independent_origins")) is int
                and rule["min_independent_origins"] >= 1, "invalid claim requirements")
        support = [(l, s) for l, s in reviews[c] if l["review"] == "verified" and l["relation"] == "supports"]
        opposing = [l for l, _ in reviews[c] if l["review"] != "rejected" and l["relation"] == "contradicts"]
        # Independence is claim-relative. Empty/unknown origin earns no credit.
        normalized_origins = (l["origin"].strip() for l, _ in support if isinstance(l.get("origin"), str))
        origins = {origin for origin in normalized_origins if origin and origin.casefold() != "unknown"}
        if opposing:
            contradiction = True
            gaps.append({"claim": c, "reason": "unresolved_contradiction"})
        if rule["primary_required"] and not any(l.get("primary_for_claim") is True for l, _ in support):
            gaps.append({"claim": c, "reason": "missing_primary"})
        if len(origins) < rule["min_independent_origins"]:
            gaps.append({"claim": c, "reason": "insufficient_independent_origins"})

    candidates = [
        {**g, "reservation_key": f'{g["claim"]}:{g["reason"]}'}
        for g in gaps
        if g["reason"] != "unresolved_contradiction"
        and f'{g["claim"]}:{g["reason"]}' not in attempted
    ]
    if contradiction:
        disposition = "needs_review"
    elif not gaps:
        disposition = "ready_for_acceptance_review"
    elif candidates and len(attempted) < budget:
        disposition = "targeted_followup_available"
    else:
        disposition = "incomplete"
    return {
        "disposition": disposition,
        "material_gaps": gaps,
        "next_candidate": candidates[0] if disposition == "targeted_followup_available" else None,
        "captures": sum(isinstance(s, dict) and s.get("retrieval") == "captured" for s in sources.values()),
        "proposed_links": sum(l["review"] == "proposed" for ls in reviews.values() for l, _ in ls),
        "verified_links": sum(l["review"] == "verified" for ls in reviews.values() for l, _ in ls),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="JSON fixture file")
    args = parser.parse_args()
    try:
        print(json.dumps(screen(json.loads(args.ledger.read_text(encoding="utf-8"))), indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Invalid checkpoint: {exc}\n")


if __name__ == "__main__":
    main()
