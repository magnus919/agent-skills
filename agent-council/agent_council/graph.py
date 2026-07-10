"""Graph orchestration — runs the debate protocol as a state machine."""

import asyncio
import json
import sys
from agent_council.state import CouncilState
from agent_council.phases.compose import compose_personas
from agent_council.phases.premortem import run_premortems
from agent_council.phases.position import run_positions
from agent_council.phases.cross_examine import run_cross_examination
from agent_council.phases.synthesis import synthesize
from agent_council.convergence import should_stop, compute_round_metrics


async def run_debate(
    question: str,
    num_agents: int = 5,
    mode: str = "medium",
    max_rounds: int = 4,
    convergence_threshold: float = 0.10,
    verbose: bool = False,
    persona_file: str | None = None,
) -> CouncilState:
    """Run the full debate protocol.

    Phases:
      1. Compose — generate/load agent personas
      2. Premortem — each agent envisions failure
      3. Position — each agent forms initial position
      4. Cross-examine — iterative, convergence-checked rounds
      5. Synthesis — produce decision landscape
    """
    state = CouncilState(
        question=question,
        mode=mode,
        max_rounds=max_rounds,
        convergence_threshold=convergence_threshold,
    )

    # Phase 1: Compose personas
    if verbose:
        print("Phase 1/5: Composing agent personas...", file=sys.stderr)

    if persona_file:
        with open(persona_file) as f:
            data = json.load(f)
            from agent_council.state import AgentPersona
            state.personas = [AgentPersona(**p) for p in data]
    else:
        state.personas = await compose_personas(question, num_agents)

    if verbose:
        for p in state.personas:
            print(f"  {p.name}: {p.expertise}", file=sys.stderr)

    # Phase 2: Premortem
    if verbose:
        print("Phase 2/5: Running pre-mortems...", file=sys.stderr)
    state.premortems = await run_premortems(question, state.personas)

    # Phase 3: Position
    if verbose:
        print("Phase 3/5: Forming positions...", file=sys.stderr)
    state.positions = await run_positions(question, state.personas, state.premortems)

    if verbose:
        for pos in state.positions.values():
            print(
                f"  {pos.agent_name}: confidence {pos.confidence}",
                file=sys.stderr,
            )

    # Phase 4: Iterative cross-examination
    if verbose:
        print("Phase 4/5: Cross-examination...", file=sys.stderr)

    round_num = 0
    while round_num < max_rounds:
        round_num += 1
        state.round_number = round_num

        if verbose:
            print(f"  Round {round_num}...", file=sys.stderr)

        cross_results = await run_cross_examination(
            question,
            state.personas,
            state.positions,
            state.cross_examination_rounds if state.cross_examination_rounds else None,
        )
        state.cross_examination_rounds.append(cross_results)

        # Check convergence
        metrics = compute_round_metrics(state)
        stop_reason = should_stop(state, metrics)

        if verbose:
            print(
                f"    Dispersion: {metrics.dispersion}, "
                f"New args: {metrics.new_arguments}, "
                f"Concessions: {metrics.concessions_made}",
                file=sys.stderr,
            )
            print(f"    → {stop_reason}", file=sys.stderr)

        if stop_reason != "continue":
            # Store the stop reason for synthesis
            object.__setattr__(state, "_stopped_reason", stop_reason)
            break

    # Phase 5: Synthesis
    if verbose:
        print("Phase 5/5: Synthesizing...", file=sys.stderr)

    state.synthesis = await synthesize(state)

    # Set the stopped reason
    stop_reason = getattr(state, "_stopped_reason", "max_rounds")
    state.synthesis.stopped_reason = stop_reason  # type: ignore

    return state
