"""Pure synthetic teaching models, not a credential broker or memory store.

No network, credential access, file persistence, or permission changes. Caller
supplies already classified synthetic claims and observed canary sinks. Production
adapters must independently enforce authority and sanitize unknown secret forms.
"""

from copy import deepcopy


def credential_decision(grant, request):
    """Exact-match synthetic grant; authentication never implies action approval."""
    if grant["revoked"] or request["now"] >= grant["expires"]:
        return "deny_expired_or_revoked"
    if request["origin"] != grant["origin"] or request["frame_origin"] != grant["origin"]:
        return "deny_origin"
    if request["worker"] != grant["owner"]:
        return "deny_owner"  # Sharing requires a new recipient-scoped grant.
    if request["operation"] not in grant["operations"]:
        return "deny_operation"
    return "allow_declared_operation"


def leaked_sinks(canary, sinks):
    """Test-only exact canary scan, not a general sanitizer or secret detector."""
    return sorted(name for name, content in sinks.items() if canary in content)


def stage_claims(claims, batch, cutoff):
    """Return sanitized proposals, not accepted memory or imported authority."""
    staged = []
    for claim in claims:
        item = {"id": claim["id"], "batch": batch, "status": "review"}
        if claim.get("sensitive"):
            item["status"] = "reject_secret"  # Discard payload before staging.
        elif claim["kind"] == "instruction":
            item["status"] = "reject_authority"
        else:
            item.update({key: claim[key] for key in ("key", "value", "kind", "source", "date")})
            if not claim["source"] or not claim["date"]:
                item["status"] = "review_unknown"
            elif claim["date"] < cutoff:
                item["status"] = "review_stale"
            elif claim["kind"] == "inference":
                item["status"] = "review_inference"
        staged.append(item)
    return {"batch": batch, "state": "staged", "claims": staged}


def accept_batch(memory, journal, accepted_ids):
    """All-or-nothing in-memory example; caller records an owner-reviewed decision."""
    if journal["state"] != "staged":
        raise ValueError("batch is not staged")
    accepted = set(accepted_ids)
    eligible = {c["id"]: c for c in journal["claims"] if c["status"] == "review"}
    if not accepted <= eligible.keys():
        raise ValueError("unknown or ineligible claim")
    selected = [eligible[cid] for cid in sorted(accepted)]
    if len({c["key"] for c in selected}) != len(selected):
        raise ValueError("resolve same-key conflict before acceptance")
    result, receipt = deepcopy(memory), deepcopy(journal)
    receipt["before"] = {}
    for claim in selected:
        key = claim["key"]
        receipt["before"][key] = deepcopy(result.get(key))
        result[key] = {"value": claim["value"], "batch": journal["batch"], "claim": claim["id"]}
    receipt["after"] = {key: deepcopy(result[key]) for key in receipt["before"]}
    receipt["state"] = "committed"
    return result, receipt


def rollback_batch(memory, receipt):
    """Restore batch-owned values; retain later corrections and report conflicts."""
    if receipt["state"] != "committed":
        raise ValueError("batch is not committed")
    result, conflicts = deepcopy(memory), []
    for key, previous in receipt["before"].items():
        if result.get(key) != receipt["after"][key]:
            conflicts.append(key)
        elif previous is None:
            result.pop(key)
        else:
            result[key] = deepcopy(previous)
    state = "rollback_conflict" if conflicts else "rolled_back"
    return result, {**deepcopy(receipt), "state": state, "conflicts": conflicts}
