#!/usr/bin/env python3
"""Validate the lifecycle evaluation corpus coverage index (#204).

Checks, all of which must hold for exit 0:
  (a) every behavioral category has >= 1 case tagged with it,
  (b) every integrated scenario has >= 1 case tagged with it,
  (c) every case ID referenced by the index exists in its declared manifest,
  (d) the committed coverage index is current (equal to the index regenerated
      from the corpus manifests + the embedded category map below).

The behavioral-category and integrated-scenario tags live in the CATEGORY_MAP
below (the single source of truth for corpus-level tagging). The committed
machine-readable index at references/coverage-index.json is a serialization of
what this script regenerates; check mode fails when the committed file drifts.
Use --write-index after changing manifests or tags to refresh the committed
index.

Python stdlib only; runs under .venv/bin/python.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

BEHAVIORAL_CATEGORIES = (
    "ambiguity",
    "conflicting-evidence",
    "unsafe-authority",
    "failure",
    "stop-retire",
)

INTEGRATED_SCENARIOS = (
    "product-launch",
    "failed-experiment",
    "migration-reconciliation-failure",
    "blocked-readiness-review",
    "agent-tool-failure",
    "privacy-boundary-escalation",
)

MANIFESTS = (
    "implementation-planning/evals/evals.json",
    "product-analytics-and-measurement/evals/evals.json",
    "product-roadmapping-and-portfolio/evals/evals.json",
    "product-experimentation/evals/evals.json",
    "product-adoption/evals/evals.json",
    "conditional-customer-success/evals/evals.json",
    "product-operations-and-governance/evals/evals.json",
    "product-lifecycle-learning/evals/evals.json",
    "production-readiness/evals/evals.json",
    "migration-engineering/evals/evals.json",
    "resilience-and-recovery/evals/evals.json",
    "capacity-and-cost-engineering/evals/evals.json",
    "incident-learning/evals/evals.json",
    "privacy-engineering/evals/evals.json",
    "bundles/product-lifecycle/evals/evals.json",
    "bundles/production-excellence/evals/evals.json",
    "bundles/agent-production-operations/evals/evals.json",
)

INDEX_PATH = ROOT / "lifecycle-evals" / "references" / "coverage-index.json"

# Skill name -> case id -> (behavioral categories, integrated scenarios).
# Untagged cases are regenerated with empty tag lists automatically; only
# corpus-relevant tags need to be declared here. Keys are the full case IDs
# from the manifests; the manifest membership is derived from MANIFESTS.
CATEGORY_MAP: dict[str, dict[str, tuple[list[str], list[str]]]] = {
    "implementation-planning": {
        "ambiguous-conflicting-requirements": (["ambiguity", "conflicting-evidence"], []),
        "cross-repository-dependencies": ([], []),
        "data-migration-with-rollback": ([], []),
        "risky-rollout-with-observability": ([], []),
        "reject-unapproved-prerequisite": (["unsafe-authority"], []),
        "multi-team-ownership-conflict": (["conflicting-evidence"], []),
    },
    "product-analytics-and-measurement": {
        "new-feature-metrics": ([], []),
        "internal-product-metrics": ([], []),
        "public-service-measurement": ([], []),
        "conflicting-metrics-resolution": (["conflicting-evidence"], []),
        "unmeasurable-north-star-rejection": (["unsafe-authority"], []),
        "privacy-boundary-measurement": ([], []),
    },
    "product-roadmapping-and-portfolio": {
        "competing-strategic-bets": ([], []),
        "dependency-invalidates-date": ([], []),
        "low-confidence-opportunity": (["ambiguity"], []),
        "capacity-shortfall": ([], []),
        "stop-bet-with-evidence": (["stop-retire"], []),
    },
    "product-experimentation": {
        "prototype-test-method-selection": ([], []),
        "feature-flag-rollout-with-guardrails": ([], []),
        "underpowered-experiment-rejection": (["failure"], []),
        "guardrail-omission-withholds-ship": (["failure"], []),
        "significant-but-no-ship-boundary": (["unsafe-authority"], []),
    },
    "product-adoption": {
        "internal-tool-adoption-diagnostic": ([], []),
        "public-service-accessibility-adoption": ([], []),
        "low-feature-discovery-diagnostic": ([], []),
        "enterprise-rollout-cohort-gates": ([], []),
        "pause-expansion-on-cohort-evidence": (["stop-retire"], []),
        "anti-trigger-acquisition-campaign": ([], []),
        "anti-trigger-analytics-instrumentation": ([], []),
    },
    "conditional-customer-success": {
        "b2b-subscription-success-plan-and-health": ([], []),
        "internal-tool-customer-success-decline": (["unsafe-authority"], []),
        "public-service-accessibility-cs-routing": ([], []),
        "renewal-risk-with-mixed-signals": (["conflicting-evidence"], []),
        "conflicting-health-evidence-decision-path": (["ambiguity", "conflicting-evidence"], []),
    },
    "product-operations-and-governance": {
        "lightweight-startup-operating-model": ([], []),
        "high-assurance-medical-device": ([], []),
        "contested-roadmap-decision": (["conflicting-evidence"], []),
        "exception-request-launch-evidence": (["unsafe-authority"], []),
        "escalation-missing-evidence": (["failure", "unsafe-authority"], []),
        "adversarial-universal-org-chart": (["unsafe-authority"], []),
    },
    "product-lifecycle-learning": {
        "successful-feature-outcomes-exceed-expectations": ([], []),
        "feature-with-clear-non-adoption": ([], []),
        "ambiguous-mixed-results-with-confounds": (["ambiguity", "conflicting-evidence"], []),
        "feature-that-should-be-retired": (["stop-retire"], []),
        "retirement-requiring-migration-and-customer-communication": (["stop-retire"], []),
        "anti-pattern-arbitrary-threshold-rejection": (["unsafe-authority"], []),
        "anti-pattern-incident-postmortem-routing": ([], []),
    },
    "production-readiness": {
        "low-risk-documentation-release": ([], []),
        "user-facing-service-launch": ([], []),
        "migration-dependent-release": ([], []),
        "missing-owner-evidence-blocked": (["failure"], []),
        "exception-requiring-human-approval": (["unsafe-authority"], []),
    },
    "migration-engineering": {
        "additive-schema-change": ([], []),
        "backfill-with-reconciliation": ([], []),
        "api-version-migration": ([], []),
        "irreversible-cutover": (["failure"], []),
        "reconciliation-failure": (["failure"], []),
    },
    "resilience-and-recovery": {
        "dependency-outage-degradation-choice": ([], []),
        "restore-test-with-data-integrity": ([], []),
        "regional-failure-dr-failover": ([], []),
        "degraded-but-available-path": ([], []),
        "recovery-exercise-unowned-gap": (["failure"], []),
    },
    "capacity-and-cost-engineering": {
        "growth-forecast": ([], []),
        "peak-event": ([], []),
        "slo-cost-conflict": (["conflicting-evidence"], []),
        "quota-decision": ([], []),
        "misleading-unit-cost": (["conflicting-evidence"], []),
    },
    "incident-learning": {
        "noisy-incident-report-evidence-separation": ([], []),
        "genuine-monitoring-gap": ([], []),
        "process-failure-incident": (["failure"], []),
        "agent-authority-failure": (["unsafe-authority"], []),
        "non-actionable-follow-up-rejection": (["stop-retire"], []),
    },
    "privacy-engineering": {
        "analytics-telemetry-privacy": ([], []),
        "agent-traces-privacy": ([], []),
        "multi-tenant-data-isolation": ([], []),
        "deletion-revocation-verification": ([], []),
        "residency-constraint-engineering": (["unsafe-authority"], []),
        "jurisdiction-escalation-legal-review": (["unsafe-authority"], []),
    },
    "product-lifecycle": {
        "new-product-complete-lifecycle": ([], ["product-launch"]),
        "ambiguous-stakeholder-request": (["ambiguity"], []),
        "failed-experiment-stop-path": (["failure", "stop-retire"], ["failed-experiment"]),
        "non-adoption-outcome": ([], []),
        "justified-retirement-decision": (["stop-retire"], []),
        "cross-phase-evidence-handoff": ([], []),
    },
    "production-excellence": {
        "normal-release-safe-launch": ([], []),
        "blocked-launch-untested-rollback": (["failure", "unsafe-authority"], ["blocked-readiness-review"]),
        "data-migration-routes-to-migration-engineering": ([], []),
        "dependency-outage-routes-to-resilience": (["conflicting-evidence", "failure"], []),
        "cost-slo-conflict": (["conflicting-evidence"], []),
        "integrated-migration-reconciliation-failure": (["failure"], ["migration-reconciliation-failure"]),
    },
    "agent-production-operations": {
        "read-only-agent-production-contract": ([], []),
        "tool-using-agent-authority-contract": (["unsafe-authority"], []),
        "model-regression-detection-and-fallback": (["failure"], []),
        "tool-outage-degraded-authority": (["failure"], ["agent-tool-failure"]),
        "cost-budget-breach-disablement": (["failure"], []),
        "human-escalation-authority-breach": (["unsafe-authority"], []),
        "incident-learning-driven-disablement": (["stop-retire"], []),
        "integrated-privacy-boundary-escalation": (["unsafe-authority"], ["privacy-boundary-escalation"]),
    },
}


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"error: unable to read {path}: {exc}") from exc


def regenerate_index() -> dict:
    """Rebuild the coverage index from the manifests + CATEGORY_MAP."""
    manifests_out = []
    for rel in MANIFESTS:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"error: corpus manifest missing: {rel}")
        data = _load_json(path)
        skill = data.get("skill_name")
        if skill is None:
            raise SystemExit(f"error: manifest has no skill_name: {rel}")
        mapping = CATEGORY_MAP.get(skill, {})
        cases_out = []
        for case in data.get("evals", []):
            case_id = case.get("id")
            if not isinstance(case_id, str):
                raise SystemExit(f"error: case without id in {rel}")
            categories, scenarios = mapping.get(case_id, ([], []))
            if not isinstance(categories, list) or not isinstance(scenarios, list):
                raise SystemExit(
                    f"error: malformed tag entry for {skill}:{case_id} in CATEGORY_MAP"
                )
            for tag in categories:
                if tag not in BEHAVIORAL_CATEGORIES:
                    raise SystemExit(
                        f"error: unknown behavioral category {tag!r} for {skill}:{case_id}"
                    )
            for tag in scenarios:
                if tag not in INTEGRATED_SCENARIOS:
                    raise SystemExit(
                        f"error: unknown integrated scenario {tag!r} for {skill}:{case_id}"
                    )
            cases_out.append(
                {
                    "case_id": case_id,
                    "behavioral_categories": list(categories),
                    "integrated_scenarios": list(scenarios),
                }
            )
        cases_out.sort(key=lambda c: c["case_id"])
        manifests_out.append(
            {
                "skill": skill,
                "manifest": rel,
                "cases": cases_out,
            }
        )
    manifests_out.sort(key=lambda m: m["manifest"])
    return {
        "schema_version": 1,
        "generated_by": "lifecycle-evals/scripts/validate-corpus-coverage.py",
        "behavioral_categories": list(BEHAVIORAL_CATEGORIES),
        "integrated_scenarios": list(INTEGRATED_SCENARIOS),
        "manifests": manifests_out,
    }


def validate(index: dict) -> list[str]:
    """Run checks (a)-(d); return a list of error strings (empty == pass)."""
    errors: list[str] = []

    tagged_categories: set[str] = set()
    tagged_scenarios: set[str] = set()
    referenced: list[tuple[str, str]] = []  # (manifest relpath, case id)

    for manifest_entry in index.get("manifests", []):
        manifest_rel = manifest_entry.get("manifest")
        for case in manifest_entry.get("cases", []):
            case_id = case.get("case_id")
            categories = case.get("behavioral_categories", [])
            scenarios = case.get("integrated_scenarios", [])
            tagged_categories.update(categories)
            tagged_scenarios.update(scenarios)
            if manifest_rel and case_id:
                referenced.append((manifest_rel, case_id))

    # (a) behavioral category coverage
    for category in BEHAVIORAL_CATEGORIES:
        if category not in tagged_categories:
            errors.append(
                f"behavioral category {category!r} has no tagged case in the coverage index"
            )

    # (b) integrated scenario coverage
    for scenario in INTEGRATED_SCENARIOS:
        if scenario not in tagged_scenarios:
            errors.append(
                f"integrated scenario {scenario!r} has no tagged case in the coverage index"
            )

    # (c) every referenced case ID exists in its declared manifest
    for manifest_rel, case_id in referenced:
        path = ROOT / manifest_rel
        if not path.is_file():
            errors.append(f"index references missing manifest {manifest_rel!r}")
            continue
        data = _load_json(path)
        ids = {case.get("id") for case in data.get("evals", [])}
        if case_id not in ids:
            errors.append(
                f"index references case {case_id!r} in {manifest_rel!r} but no such case exists"
            )

    # (d) index is current: committed file equals regenerated index
    regenerated = regenerate_index()
    if regenerated != index:
        errors.append(
            "committed coverage-index.json is stale: regenerate it with "
            "lifecycle-evals/scripts/validate-corpus-coverage.py --write-index"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-index",
        action="store_true",
        help="regenerate and write references/coverage-index.json",
    )
    args = parser.parse_args()

    if args.write_index:
        regenerated = regenerate_index()
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        INDEX_PATH.write_text(
            json.dumps(regenerated, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {INDEX_PATH.relative_to(ROOT)}")
        return 0

    if not INDEX_PATH.is_file():
        print(
            f"error: coverage index missing at {INDEX_PATH.relative_to(ROOT)}; "
            "run with --write-index to generate it",
            file=sys.stderr,
        )
        return 1

    index = _load_json(INDEX_PATH)
    errors = validate(index)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1

    total_cases = sum(len(entry.get("cases", [])) for entry in index.get("manifests", []))
    print(
        f"lifecycle corpus coverage OK: {len(index.get('manifests', []))} manifests, "
        f"{total_cases} cases, all 5 behavioral categories and all 6 integrated scenarios covered, "
        "index current."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
