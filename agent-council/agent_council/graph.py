"""Graph orchestration — runs the debate protocol as a state machine."""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from agent_council.state import CouncilState
from agent_council.phases.compose import compose_personas
from agent_council.phases.select import select_by_names, select_by_question
from agent_council.phases.premortem import run_premortems
from agent_council.phases.position import run_positions
from agent_council.phases.cross_examine import run_cross_examination
from agent_council.phases.synthesis import synthesize
from agent_council.convergence import should_stop, compute_round_metrics


def _stream(msg: str, end: str = "\n") -> None:
    """Print a progress message immediately to stdout."""
    print(msg, end=end, flush=True)


def _run_dir() -> Path:
    """Create and return a timestamped run directory."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = Path(f"/tmp/agent-council/{ts}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _identity_for(
    state: CouncilState,
    name: str,
    fallback_persona=None,
) -> str:
    """Build an identity block for a debate agent.

    If real profiles are loaded, uses the SOUL.md content.
    Otherwise falls back to fabricated persona fields.
    """
    # Prefer real profiles
    for p in state.profiles:
        if p.name == name:
            return (
                f"You are {name}.\n\n"
                f"Your identity and operating principles:\n"
                f"{p.soul_content}\n\n"
                f"Description: {p.description}"
            )

    # Fallback to fabricated persona
    if fallback_persona:
        return (
            f"You are {fallback_persona.name}.\n"
            f"Background: {fallback_persona.background}\n"
            f"Expertise: {fallback_persona.expertise}\n"
            f"Approach: {fallback_persona.approach}\n"
            f"Bias: {fallback_persona.bias}"
        )

    return f"You are {name}."


async def run_debate(
    question: str,
    num_agents: int = 5,
    mode: str = "medium",
    max_rounds: int = 4,
    convergence_threshold: float = 0.10,
    verbose: bool = False,
    persona_file: str | None = None,
    profile_names: list[str] | None = None,
) -> CouncilState:
    """Run the full debate protocol with live progress output.

    Phases:
      1. Select/Compose — pick real profiles or generate personas
      2. Premortem — each agent envisions failure
      3. Position — each agent forms initial position
      4. Cross-examine — iterative, convergence-checked rounds
      5. Synthesis — produce decision landscape
    """
    rundir = _run_dir()
    state = CouncilState(
        question=question,
        mode=mode,
        max_rounds=max_rounds,
        convergence_threshold=convergence_threshold,
    )

    # Phase 1: Select or Compose agents
    _stream("🏛  Council assembling...")

    if profile_names:
        # Explicit profile selection
        state.profiles = select_by_names(profile_names)
        _stream(f"   📂 Loaded {len(state.profiles)} profiles (explicit)")
    else:
        # Try auto-selecting profiles from the library
        state.profiles = select_by_question(question, num_agents)
        if state.profiles:
            _stream(f"   📂 Auto-selected {len(state.profiles)} profiles from library")
        else:
            # Fallback: compose fabricated personas
            _stream("   ⚡ No profile library found, composing personas...")
            if persona_file:
                from agent_council.state import AgentPersona
                with open(persona_file) as f:
                    data = json.load(f)
                    state.personas = [AgentPersona(**p) for p in data]
                _stream(f"   Loaded {len(state.personas)} personas from file")
            else:
                state.personas = await compose_personas(question, num_agents)

    if verbose:
        for p in state.profiles or state.personas:
            name = p.name if hasattr(p, 'name') else p
            _stream(f"   👤 {name}")

    # Write agent identities to run dir
    with open(rundir / "agents.json", "w") as f:
        agents = {
            "profiles": [
                {"name": p.name, "description": p.description}
                for p in state.profiles
            ],
            "personas": [
                {"name": p.name, "expertise": p.expertise}
                for p in state.personas
            ],
        }
        f.write(json.dumps(agents, indent=2, default=str))
        _stream(f"   ✅ {len(state.profiles or state.personas)} agents ready")

    # Phase 2: Premortem
    _stream("   🔮 Pre-mortem phase...")
    t0 = time.time()
    state.premortems = await run_premortems(question, state, verbose)
    _stream(f"   ✅ Pre-mortem complete ({len(state.premortems)} agents, {time.time()-t0:.0f}s)")

    with open(rundir / "premortems.json", "w") as f:
        f.write(json.dumps(
            {k: v.model_dump() for k, v in state.premortems.items()},
            indent=2,
            default=str,
        ))

    # Phase 3: Position
    _stream("   📋 Position phase...")
    t0 = time.time()
    state.positions = await run_positions(question, state, verbose)
    confidences = [p.confidence for p in state.positions.values()]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    _stream(f"   ✅ Positions formed ({len(state.positions)} agents, avg confidence {avg_conf:.2f}, {time.time()-t0:.0f}s)")

    if verbose:
        for pos in state.positions.values():
            _stream(f"      {pos.agent_name}: {pos.stance[:80]}...")

    with open(rundir / "positions.json", "w") as f:
        f.write(json.dumps(
            {k: v.model_dump() for k, v in state.positions.items()},
            indent=2,
            default=str,
        ))

    # Phase 4: Iterative cross-examination
    _stream("   💬 Cross-examination rounds...")

    round_num = 0
    while round_num < max_rounds:
        round_num += 1
        state.round_number = round_num

        _stream(f"      Round {round_num}... ", end="")
        t0 = time.time()
        cross_results = await run_cross_examination(question, state, verbose)
        state.cross_examination_rounds.append(cross_results)

        metrics = compute_round_metrics(state)
        stop_reason = should_stop(state, metrics)

        elapsed = time.time() - t0
        _stream(
            f"dispersion={metrics.dispersion:.3f} "
            f"concessions={metrics.concessions_made} "
            f"new_args={metrics.new_arguments} "
            f"({elapsed:.0f}s) → {stop_reason}"
        )

        with open(rundir / f"round_{round_num}.json", "w") as f:
            f.write(json.dumps(
                {k: v.model_dump() for k, v in cross_results.items()},
                indent=2,
                default=str,
            ))

        if stop_reason != "continue":
            object.__setattr__(state, "_stopped_reason", stop_reason)
            break

    # Phase 5: Synthesis
    _stream("   📝 Synthesizing final report...")
    t0 = time.time()
    state.synthesis = await synthesize(state)
    _stream(f"   ✅ Synthesis complete ({time.time()-t0:.0f}s)")

    stop_reason = getattr(state, "_stopped_reason", "max_rounds")
    state.synthesis.stopped_reason = stop_reason  # type: ignore

    with open(rundir / "synthesis.json", "w") as f:
        f.write(state.synthesis.model_dump_json(indent=2))

    with open(rundir / "synthesis.md", "w") as f:
        from agent_council.cli import format_synthesis_markdown
        f.write(format_synthesis_markdown(state.synthesis))

    _stream(f"\n📁 Full debate output: {rundir}/\n")

    return state
