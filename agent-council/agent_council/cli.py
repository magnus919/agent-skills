"""CLI entry point for agent-council."""

import argparse
import asyncio
import json
import sys


def main():
    """Entry point for `agent-council` CLI."""
    parser = argparse.ArgumentParser(
        description="Multi-agent structured debate system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  agent-council \"Should we use Postgres or SQLite?\"\n"
            "  agent-council --mode quick --agents 3 \"Quick check on this idea\"\n"
            "  agent-council --json \"Output as machine-readable JSON\"\n"
            "  agent-council --persona-file personas.json \"Custom agent lineup\"\n\n"
            "Environment:\n"
            "  AGENT_COUNCIL_API_KEY   API key (required)\n"
            "  AGENT_COUNCIL_MODEL     Model string (default: openai/gpt-4o-mini)\n"
            "  AGENT_COUNCIL_BASE_URL  Custom API endpoint\n"
        ),
    )
    parser.add_argument(
        "question",
        type=str,
        help="The question to debate",
    )
    parser.add_argument(
        "--agents", "-n",
        type=int,
        default=5,
        choices=range(3, 8),
        help="Number of debate agents (3-7, default: 5)",
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        default="medium",
        choices=["quick", "medium", "deep"],
        help="Debate depth (default: medium)",
    )
    parser.add_argument(
        "--persona-file",
        type=str,
        default=None,
        help="JSON file with custom agent persona definitions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as structured JSON instead of markdown",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show phase-by-phase progress",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=4,
        help="Maximum cross-examination rounds (default: 4)",
    )
    parser.add_argument(
        "--convergence",
        type=float,
        default=0.10,
        help="Convergence threshold for confidence dispersion (default: 0.10)",
    )
    parser.add_argument(
        "--profiles",
        type=str,
        default=None,
        help="Comma-separated profile names from the hermes-profiles library "
             "(e.g. 'debugger,researcher,product-manager'). "
             "Omit for auto-selection based on the question.",
    )

    args = parser.parse_args()

    if not args.question.strip():
        print("Error: Question cannot be empty.", file=sys.stderr)
        sys.exit(3)

    # Map mode to agent count
    agent_map = {"quick": 3, "medium": 5, "deep": 7}
    num_agents = args.agents or agent_map.get(args.mode, 5)

    # Import here so CLI help is fast even without pydantic-ai installed
    try:
        from agent_council.graph import run_debate
    except ImportError as e:
        print(
            f"Error: Could not import agent_council: {e}",
            file=sys.stderr,
        )
        print(
            "Make sure pydantic-ai is installed: pip install pydantic-ai",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse explicit profile list
    profile_names = None
    if args.profiles:
        profile_names = [n.strip() for n in args.profiles.split(",")]

    try:
        state = asyncio.run(
            run_debate(
                question=args.question,
                num_agents=num_agents,
                mode=args.mode,
                max_rounds=args.max_rounds,
                convergence_threshold=args.convergence,
                verbose=args.verbose,
                persona_file=args.persona_file,
                profile_names=profile_names,
            )
        )
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Debate failed: {e}", file=sys.stderr)
        sys.exit(2)

    synthesis = state.synthesis
    if not synthesis:
        print("Error: Debate completed but no synthesis was produced.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(synthesis.model_dump_json(indent=2))
    else:
        print(format_synthesis_markdown(synthesis))


def format_synthesis_markdown(synthesis) -> str:
    """Format synthesis as human-readable markdown."""
    from agent_council.state import Synthesis

    lines = []
    lines.append(f"# Council Synthesis")
    lines.append(f"")
    lines.append(f"**Question:** {synthesis.question}")
    lines.append(f"**Mode:** {synthesis.mode} ({synthesis.num_agents} agents, {synthesis.rounds_completed} rounds)")
    lines.append(f"**Stopped because:** {synthesis.stopped_reason}")
    lines.append(f"")

    # Confidence dispersion
    lines.append(f"## Confidence Dispersion")
    lines.append(f"")
    lines.append(f"| Round | Mean Confidence | Dispersion | New Args | Concessions |")
    lines.append(f"|-------|----------------|------------|----------|-------------|")
    for m in synthesis.confidence_history:
        lines.append(
            f"| {m.round} | {m.mean_confidence:.3f} | {m.dispersion:.3f} | "
            f"{m.new_arguments} | {m.concessions_made} |"
        )
    lines.append(f"")
    lines.append(f"**Final dispersion:** {synthesis.final_dispersion:.3f}")
    lines.append(f"**Mean confidence delta:** {synthesis.mean_confidence_delta:+.3f}")
    lines.append(f"")

    # Diagnostic
    if synthesis.final_dispersion < 0.08:
        diag = "Confidence converged — agents reached alignment."
    elif synthesis.final_dispersion > 0.15:
        diag = "Confidence remained dispersed — genuine disagreement persisted."
    else:
        diag = "Moderate agreement with meaningful remaining tension."
    lines.append(f"> **Diagnostic:** {diag}")
    lines.append(f"")

    # Shared risks (from premortem)
    if synthesis.shared_risks:
        lines.append(f"## Shared Risks (Pre-Mortem)")
        lines.append(f"")
        for risk in synthesis.shared_risks:
            agents = ", ".join(risk.agents_who_flagged)
            lines.append(f"- **{risk.severity.upper()}** — {risk.description}")
            lines.append(f"  *Flagged by: {agents}*")
        lines.append(f"")

    # Shared concerns
    if synthesis.shared_concerns:
        lines.append(f"## Shared Concerns (Confirmed by Debate)")
        lines.append(f"")
        for concern in synthesis.shared_concerns:
            lines.append(f"- {concern}")
        lines.append(f"")

    # Disagreements
    if synthesis.disagreements:
        lines.append(f"## Remaining Disagreements")
        lines.append(f"")
        for d in synthesis.disagreements:
            lines.append(f"- **{d.topic}**")
            for agent, pos in d.positions.items():
                lines.append(f"  - {agent}: {pos[:120]}")
        lines.append(f"")

    # Assumptions
    if synthesis.assumptions_per_position:
        lines.append(f"## Assumptions per Position")
        lines.append(f"")
        for agent, assumptions in synthesis.assumptions_per_position.items():
            lines.append(f"- **{agent}**")
            for a in assumptions:
                lines.append(f"  - {a}")
        lines.append(f"")

    # Principal's path
    if synthesis.principal_path:
        lines.append(f"## Principal's Path")
        lines.append(f"")
        lines.append(synthesis.principal_path)
        lines.append(f"")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
