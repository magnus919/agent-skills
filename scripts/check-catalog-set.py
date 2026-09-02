#!/usr/bin/env python3
"""Compare canonical skill names with every committed catalog projection."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

EXCLUDED_DIRS = {"lifecycle-evals"}
LLMS_RE = re.compile(r"^- \[([^\]]+)\]\(([^)]+)\):", re.MULTILINE)


def canonical_names(root: Path) -> tuple[list[str], list[str]]:
    """Return canonical names and excluded infrastructure/nested entries."""
    names: list[str] = []
    excluded: list[str] = []
    for path in sorted(root.glob("*/SKILL.md")):
        name = path.parent.name
        if name in EXCLUDED_DIRS:
            excluded.append(name)
        else:
            names.append(name)
    for path in sorted(root.glob("**/SKILL.md")):
        if path.parent.parent == root or path.parent.parent.parent == root:
            continue
        excluded.append(str(path.relative_to(root)))
    return names, excluded


def _names(value: object, key: str) -> list[str]:
    if not isinstance(value, dict):
        return []
    entries = value.get(key, [])
    result: list[str] = []
    for entry in entries if isinstance(entries, list) else []:
        if isinstance(entry, str):
            result.append(Path(entry).name)
        elif isinstance(entry, dict) and isinstance(entry.get("name"), str):
            result.append(entry["name"])
    return result


def projection_sets(root: Path) -> dict[str, list[str]]:
    claude = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    codex = json.loads((root / ".codex-plugin/plugin.json").read_text())
    agents = json.loads((root / ".agents/plugins/marketplace.json").read_text())
    lines = (root / "llms.txt").read_text()
    # The Agents marketplace is a wrapper for the Codex plugin, so its plugin
    # identity is checked separately rather than mistaken for a skill list.
    agent_plugins = [x.get("name") for x in agents.get("plugins", []) if isinstance(x, dict)]
    return {
        "claude_marketplace": [x.get("name") for x in claude.get("plugins", []) if isinstance(x, dict)],
        "codex_plugin": _names(codex, "skills"),
        "llms": [match.group(1) for match in LLMS_RE.finditer(lines)],
        "agents_marketplace": agent_plugins,
    }


def compare(root: Path) -> dict[str, object]:
    canonical, excluded = canonical_names(root)
    sources = projection_sets(root)
    expected = set(canonical)
    retired = {"jira-cli", "jira-jql"}
    diffs: dict[str, dict[str, object]] = {}
    for source, values in sources.items():
        counts = Counter(values)
        actual = set(values)
        diffs[source] = {
            "missing": sorted(expected - actual) if source != "agents_marketplace" else [],
            "extra": sorted(actual - expected) if source != "agents_marketplace" else [],
            "duplicates": sorted(name for name, count in counts.items() if count > 1),
            "retired": sorted(retired & actual),
            "infrastructure": sorted(set(EXCLUDED_DIRS) & actual),
            "nested": sorted(name for name in actual if "/" in name),
            "entries": len(values),
        }
    # Retired Jira names and infrastructure must never reappear in projections.
    retired = {"jira-cli", "jira-jql"}
    all_projected = {name for values in sources.values() for name in values}
    diffs["policy"] = {
        "retired": sorted(retired & all_projected),
        "infrastructure": sorted(set(EXCLUDED_DIRS) & all_projected),
        "nested": sorted(name for name in all_projected if "/" in name),
        "excluded": excluded,
    }
    diffs["agents_marketplace"]["identity"] = sorted(set(sources["agents_marketplace"]) ^ {"magnus919"})
    errors = any(
        diffs[source].get(field)
        for source in diffs
        for field in ("missing", "extra", "duplicates", "retired", "infrastructure", "nested", "identity")
    )
    return {"ok": not errors, "canonical": sorted(canonical), "sources": diffs}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare canonical skills and generated catalogs")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        result = compare(args.root.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"ok": False, "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
