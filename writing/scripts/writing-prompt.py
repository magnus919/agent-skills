#!/usr/bin/env python3
"""Generate position-aware writing prompt sets.

Each prompt set follows the three-part structure used by writing coaches:
an affirmation, one plot element matched to the story's current position,
and a writing assignment that advances the plot. A record block closes
the set so the writer can log the session.

Non-interactive; deterministic when --seed is given.

Examples:
    writing-prompt.py --position crisis
    writing-prompt.py --position beginning --count 3 --seed 42
    writing-prompt.py --all --count 1 --json
"""

import argparse
import json
import random
import sys

# One structural element per story position, plus a short rationale used to
# brief the writer. Original formulations, not quotations.
POSITIONS = {
    "beginning": [
        ("goal", "make the protagonist's want concrete enough to act on"),
        ("stakes", "make what she stands to lose visible"),
        ("antagonist", "introduce the opposing force with a memorable first move"),
        ("flaw", "show the coping mechanism without explaining its origin"),
        ("fear", "hint at the fear she must eventually face"),
        ("dream", "plant the dream that will pay off as a twist"),
        ("backstory withheld", "let the past show in behavior, not explanation"),
        ("threshold", "write the moment of no return"),
    ],
    "halfway": [
        ("recommitment", "make the choice to continue costly and deliberate"),
        ("escalation", "raise the antagonist's power and the stakes"),
        ("cause and effect", "chain three scenes so each causes the next"),
        ("goal restated", "re-establish the goal in the new world"),
        ("fear confronted", "face a version of the fear, smaller than the final one"),
        ("mirror moment", "show the protagonist a glimpse of who she is becoming"),
        ("ally", "let an ally say what the protagonist cannot yet see"),
        ("subplot", "weave a subplot that changes the main story's outcome"),
    ],
    "crisis": [
        ("crisis", "take everything away in the worst order"),
        ("backstory reveal", "surface the full wound, in less than a paragraph if possible"),
        ("missing skill", "show her failing at the thing she must master by the climax"),
        ("self-revelation", "let her see the part she played in her own failure"),
        ("deadline", "put a clock on the story"),
        ("threshold guardian", "test whether she is ready to cross"),
        ("defenses stripped", "remove the excuse she has been hiding behind"),
        ("culpability", "name her responsibility without self-pity"),
    ],
    "climax": [
        ("transformed action", "have her do the thing the old self could not"),
        ("climax", "resolve the dramatic question at the moment all seems lost"),
        ("new belief", "show the belief that replaced the old one"),
        ("cause and effect final", "chain the final events so each is earned"),
        ("allies", "let the allies' goals resolve"),
        ("resolution", "return to a changed world, circling an early setting"),
        ("loose end", "choose deliberately which thread stays open"),
        ("dream payoff", "reveal what the dream actually meant"),
    ],
}

# Assignment builders: each takes a protagonist placeholder and an element
# name, returns an imperative scene-or-summary assignment.
ASSIGNMENTS = {
    "goal": "Write {protagonist} taking one active step toward her goal for the first time, in a scene that shows why it matters and what she will lose. Do not name her emotion; render it as action.",
    "stakes": "Write a scene that makes the cost of failure concrete and personal. Show someone else who would be hurt, or a future that would be lost.",
    "antagonist": "Give the antagonist a first move that raises the protagonist's problem and makes the antagonist memorable. Let the antagonist's want be visible.",
    "flaw": "Show the flaw operating in ordinary life — a habit, a rule, a flinch — without explaining where it came from.",
    "fear": "Write a quiet moment where the fear brushes against the surface. Do not resolve it.",
    "dream": "Plant a dream the protagonist privately holds, and give it one concrete object or image the reader will remember.",
    "backstory withheld": "Let the past appear in behavior only: a reflex, a rule, an avoidance. The explanation comes later.",
    "threshold": "Write the scene where the old world breaks apart and there is no turning back. End at the moment of no return.",
    "recommitment": "Give the protagonist a real chance to go back — and have her choose to continue. Show the cost, and let her name the stakes out loud for the first time.",
    "escalation": "Bring the antagonist's power into full view. Give the protagonist a small win that costs more than it gains.",
    "cause and effect": "Write a three-scene chain in which each scene's action causes the next. Keep every link visible.",
    "goal restated": "Have the protagonist restate her goal in the new world, changed by what she has learned. Show what is now missing from it.",
    "cause and effect final": "Chain the final events so each is earned by the one before. No luck, no convenience.",
    "fear confronted": "Write a scene where the protagonist faces a small version of her fear and survives it — at a price.",
    "mirror moment": "Show the protagonist catching a glimpse of who she is becoming, and not liking or not believing it.",
    "ally": "Let an ally say the one thing the protagonist cannot yet say about herself.",
    "subplot": "Write a subplot scene that, if removed, would change the main story's outcome or emotional impact. Make that link visible.",
    "crisis": "Take everything from the protagonist — the goal, the ally, the belief — in the worst order. End with her seeing the part she played in her own failure. This is not the ending.",
    "backstory reveal": "At the threshold after the crisis, let the full backstory wound surface. The reader has earned it; the character finally names it.",
    "missing skill": "Show the protagonist failing at exactly the thing she will succeed at in the climax. Make the reader see why she cannot do it yet.",
    "self-revelation": "Write the moment she recognizes her own contribution to the disaster. No self-pity; fact only.",
    "deadline": "Put a clock on the story: an event that will happen whether she is ready or not. Show her racing it.",
    "threshold guardian": "Write the test that decides whether she crosses into the final quarter: a fear, a guilt, or a person she must answer to.",
    "defenses stripped": "Remove the excuse she has been hiding behind and show her without it.",
    "culpability": "Name her responsibility for her own failure in one honest paragraph of scene, not summary.",
    "transformed action": "Write the climax scene: she does the thing the old self could not, at the moment all seems lost. Moment by moment, no summary.",
    "climax": "Resolve the dramatic question posed at the start. The transformed protagonist performs the decisive action; show the consequence.",
    "new belief": "Show the belief that replaced the old one, proven in action rather than stated.",
    "allies": "Resolve the allies' goals in the aftermath, each changed by the protagonist's transformation.",
    "resolution": "After the climax, show the protagonist returning to a changed world — circle back to an early setting or character.",
    "loose end": "Choose deliberately: which subplot question stays open? Write the resolution without closing it.",
    "dream payoff": "Reveal what the dream actually meant, as a twist the beginning did not predict.",
}

AFFIRMATIONS = [
    "I am writing the story that only I can tell, and today I move it forward.",
    "My first draft is raw material; today I add to it without judgment.",
    "The words will come if I keep moving; today I keep moving.",
    "I trust the story I cannot see yet; today I write toward it.",
    "My voice is enough; today I let it speak.",
]


def build_set(position, element_name, protagonist, rng, index):
    """Build one three-part prompt set for a position and element."""
    element, brief = element_name
    assignment = ASSIGNMENTS[element]
    affirmation = AFFIRMATIONS[index % len(AFFIRMATIONS)]
    return {
        "position": position,
        "element": element,
        "brief": brief,
        "affirmation": affirmation,
        "assignment": assignment.format(protagonist=protagonist),
        "record_block": {
            "start": "",
            "stop": "",
            "words": "",
            "daily_goal": "",
            "energy": "",
            "above_or_below_line": "",
            "trait_surfaced": "",
        },
    }


def emit(prompt_sets, as_json, output):
    if as_json:
        payload = json.dumps(prompt_sets, indent=2)
        if output:
            with open(output, "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
        else:
            print(payload)
        return
    lines = []
    for index, item in enumerate(prompt_sets, start=1):
        lines.append(f"### Prompt set {index} — {item['position'].title()}")
        lines.append("")
        lines.append(f"**Affirmation:** {item['affirmation']}")
        lines.append("")
        lines.append(f"**Plot element — {item['element']}:** {item['brief'].capitalize()}.")
        lines.append("")
        lines.append(f"**Writing assignment:** {item['assignment']}")
        lines.append("")
        lines.append("**Record block:**")
        lines.append("- Start: ___  Stop: ___  Words: ___  Daily goal: ___/___")
        lines.append("- Energy (1-10): ___  Above/below the line: ___")
        lines.append("- Trait surfaced (character profile): ___")
        lines.append("")
    text = "\n".join(lines)
    if output:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate position-aware three-part writing prompt sets."
    )
    parser.add_argument(
        "--position",
        choices=sorted(POSITIONS),
        help="Story position: beginning, halfway, crisis, or climax.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate one prompt per story position.",
    )
    parser.add_argument("--count", type=int, default=1, help="Prompt sets per position.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for determinism.")
    parser.add_argument(
        "--protagonist", default="the protagonist", help="Protagonist name for assignments."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", default=None, help="Write to a file instead of stdout.")
    args = parser.parse_args(argv)

    if args.all and args.position:
        parser.error("use either --position or --all, not both")
    if not args.all and not args.position:
        parser.error("--position or --all is required")
    if args.count < 1:
        parser.error("--count must be >= 1")

    positions = sorted(POSITIONS) if args.all else [args.position]
    rng = random.Random(args.seed)
    prompt_sets = []
    for position in positions:
        elements = list(POSITIONS[position])
        for index in range(args.count):
            element = elements[rng.randrange(len(elements))]
            prompt_sets.append(build_set(position, element, args.protagonist, rng, index))

    try:
        emit(prompt_sets, args.json, args.output)
    except OSError as error:
        print(f"error: cannot write output: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
