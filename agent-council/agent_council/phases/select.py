"""Select phase — picks real profiles from the hermes-profiles library."""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

from agent_council.state import ProfileInfo


# Path to the profiles submodule within the skill directory
PROFILES_DIR = Path(__file__).resolve().parent.parent.parent / "profiles" / "profiles"


def _update_submodule() -> None:
    """Pull the latest profiles from the hermes-profiles submodule."""
    skill_root = PROFILES_DIR.parent  # agent-council/profiles/
    try:
        subprocess.run(
            ["git", "submodule", "update", "--remote", "--init"],
            cwd=skill_root.parent,  # agent-council/
            capture_output=True,
            timeout=30,
        )
    except Exception:
        pass  # Non-fatal — use whatever version we have


def _list_available() -> list[str]:
    """List all available profile names."""
    if not PROFILES_DIR.exists():
        return []
    return sorted(
        d.name for d in PROFILES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def _load_profile(name: str) -> ProfileInfo | None:
    """Load a single profile's SOUL.md and profile.yaml."""
    profile_dir = PROFILES_DIR / name
    soul_path = profile_dir / "SOUL.md"
    yaml_path = profile_dir / "profile.yaml"

    if not soul_path.exists():
        return None

    soul_content = soul_path.read_text(encoding="utf-8")

    description = ""
    if yaml_path.exists():
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            description = data.get("description", "") or ""
        except Exception:
            pass

    return ProfileInfo(name=name, description=description, soul_content=soul_content)


def load_all() -> list[ProfileInfo]:
    """Load all available profiles. Updates submodule first."""
    _update_submodule()
    profiles = []
    for name in _list_available():
        p = _load_profile(name)
        if p:
            profiles.append(p)
    return profiles


def select_by_names(names: list[str]) -> list[ProfileInfo]:
    """Load specific profiles by name."""
    _update_submodule()
    profiles = []
    for name in names:
        name = name.strip().lower()
        p = _load_profile(name)
        if p:
            profiles.append(p)
        else:
            print(
                f"Warning: profile '{name}' not found. "
                f"Available: {', '.join(_list_available())}",
                file=sys.stderr,
            )
    return profiles


def select_by_question(question: str, count: int = 5) -> list[ProfileInfo]:
    """Auto-select the most relevant profiles for a question.

    Scores each profile by keyword overlap between the question
    and the profile's description. Returns the top N profiles.
    """
    all_profiles = load_all()
    if not all_profiles:
        return []

    question_lower = question.lower()
    question_words = set(question_lower.split())

    scored = []
    for p in all_profiles:
        desc_words = set(p.description.lower().split())
        # Also score on profile name
        name_words = set(p.name.lower().replace("-", " ").split())

        # Count overlapping words
        overlap = len(question_words & desc_words) + len(question_words & name_words)

        # Bonus for exact phrase matches
        if p.name.lower().replace("-", " ") in question_lower:
            overlap += 3

        scored.append((overlap, p))

    scored.sort(key=lambda x: -x[0])

    # Pick top N, ensure diversity (skip if too similar description)
    selected = []
    seen_descriptions = set()
    for _, p in scored:
        desc_key = p.description[:80]
        if desc_key not in seen_descriptions or len(selected) < 3:
            selected.append(p)
            seen_descriptions.add(desc_key)
        if len(selected) >= count:
            break

    # Fallback: if somehow empty, grab first N
    if not selected and all_profiles:
        selected = all_profiles[:count]

    return selected
