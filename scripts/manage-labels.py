#!/usr/bin/env python3
"""Manage GitHub issue labels for consistent priority, type, and area classification.

Run with GITHUB_TOKEN set to manage labels on the agent-skills repository.
Without a token, prints the recommended label configuration for manual setup.

Usage:
  GITHUB_TOKEN=... python3 scripts/manage-labels.py          # apply labels
  GITHUB_TOKEN=... python3 scripts/manage-labels.py --dry-run  # preview only
  python3 scripts/manage-labels.py                            # print config
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

REPO = "magnus919/agent-skills"
API_BASE = f"https://api.github.com/repos/{REPO}"

LABELS: dict[str, dict[str, str]] = {
    # Priority labels (P0-P3)
    "priority/P0-critical": {
        "color": "b60205",
        "description": "Drop everything: blocks releases, security incidents, data loss",
    },
    "priority/P1-high": {
        "color": "d93f0b",
        "description": "Must fix this sprint: user-facing broken, deadline at risk",
    },
    "priority/P2-medium": {
        "color": "fbca04",
        "description": "Should fix soon: important but not blocking",
    },
    "priority/P3-low": {
        "color": "0e8a16",
        "description": "Nice to have: backlog grooming, minor improvements",
    },
    # Type labels
    "type/bug": {
        "color": "d73a4a",
        "description": "Something is broken",
    },
    "type/feature": {
        "color": "a2eeef",
        "description": "New capability or enhancement",
    },
    "type/chore": {
        "color": "c5def5",
        "description": "Maintenance, refactoring, dependency updates",
    },
    "type/documentation": {
        "color": "0075ca",
        "description": "Documentation improvements",
    },
    "type/question": {
        "color": "d876e3",
        "description": "Needs discussion or clarification",
    },
    # Area labels
    "area/ci-cd": {
        "color": "5319e7",
        "description": "CI/CD pipelines, GitHub Actions, automation",
    },
    "area/validation": {
        "color": "006b75",
        "description": "Skill validation, eval manifests, quality checks",
    },
    "area/skills": {
        "color": "bfdadc",
        "description": "Individual skill content and structure",
    },
    "area/docs": {
        "color": "c2e0c6",
        "description": "READMEs, AGENTS.md, CONTRIBUTING.md, architecture",
    },
    "area/tooling": {
        "color": "f9d0c4",
        "description": "Scripts, generators, CLI tools",
    },
    "area/security": {
        "color": "b60205",
        "description": "Security concerns, vulnerabilities, auditing",
    },
    # Status labels
    "status/blocked": {
        "color": "000000",
        "description": "Cannot proceed due to dependency or external factor",
    },
    "status/needs-triage": {
        "color": "ededed",
        "description": "New issue awaiting triage",
    },
}


def _api_request(method: str, path: str, data: dict[str, Any] | None = None) -> Any:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN environment variable is not set")

    url = f"{API_BASE}{path}"
    body = json.dumps(data).encode("utf-8") if data else None

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
        raise


def get_existing_labels() -> dict[str, dict[str, Any]]:
    """Fetch existing labels from the repository."""
    labels: dict[str, dict[str, Any]] = {}
    page = 1
    while True:
        result: list[dict[str, Any]] = _api_request("GET", f"/labels?per_page=100&page={page}")
        if not result:
            break
        for label in result:
            labels[label["name"]] = label
        page += 1
    return labels


def create_label(name: str, config: dict[str, str]) -> None:
    """Create a new label."""
    print(f"  Creating: {name}")
    _api_request("POST", "/labels", {"name": name, **config})


def update_label(name: str, config: dict[str, str]) -> None:
    """Update an existing label."""
    print(f"  Updating: {name}")
    _api_request("PATCH", f"/labels/{urllib.parse.quote(name)}", dict(config))


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    if not os.environ.get("GITHUB_TOKEN"):
        print("# Recommended label configuration for agent-skills\n")
        print("To apply, set GITHUB_TOKEN and run:")
        print("  python3 scripts/manage-labels.py\n")
        for name, config in LABELS.items():
            print(f"  {name}: #{config['color']} - {config['description']}")
        print(f"\n{len(LABELS)} labels total.")
        return 0

    existing = get_existing_labels()
    print(f"Found {len(existing)} existing labels.\n")

    for name, config in LABELS.items():
        if name in existing:
            if (
                existing[name]["color"] != config["color"]
                or existing[name]["description"] != config["description"]
            ):
                if dry_run:
                    print(f"  [DRY RUN] Would update: {name}")
                else:
                    update_label(name, config)
            else:
                print(f"  OK: {name}")
        else:
            if dry_run:
                print(f"  [DRY RUN] Would create: {name}")
            else:
                create_label(name, config)

    if dry_run:
        print(f"\nDry run complete. {len(LABELS)} labels would be reconciled.")
    else:
        print(f"\nDone. {len(LABELS)} labels reconciled.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
