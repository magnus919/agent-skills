"""Typed state model and phase output schemas."""

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field


# ── Phase output schemas (validated Pydantic models) ──


class AgentPersona(BaseModel):
    """Profile for a single debate agent."""

    name: str
    background: str = Field(description="One-paragraph career background")
    expertise: str = Field(description="Specific domain expertise")
    approach: str = Field(description="Analytical approach they bring")
    bias: str = Field(description="What experience or bias they bring to THIS question")


class Premortem(BaseModel):
    """Pre-mortem: agent envisions how the decision already failed."""

    agent_name: str
    failure_scenario: str = Field(description="Narrative of how the decision failed")
    root_causes: list[str] = Field(description="What went wrong")
    early_warning_signals: list[str] = Field(description="What to watch for")


class Position(BaseModel):
    """Agent's initial position on the question."""

    agent_name: str
    stance: str = Field(description="Position on the question")
    reasoning: list[str] = Field(description="Chain of reasoning")
    confidence: float = Field(ge=0, le=1, description="Confidence in this position")
    key_assumptions: list[str] = Field(description="Assumptions that must hold")


class CrossExamination(BaseModel):
    """Agent's response after reading all other positions."""

    agent_name: str
    concessions: list[str] = Field(description="Points where the agent conceded or shifted")
    remaining_disagreements: list[str] = Field(description="Points still in dispute")
    updated_position: str | None = Field(
        default=None, description="Revised position, if changed"
    )
    updated_confidence: float | None = Field(
        default=None, ge=0, le=1, description="Updated confidence, if changed"
    )
    reflection: str = Field(
        description="What the agent learned from other perspectives"
    )
    new_evidence_needed: list[str] = Field(
        default_factory=list,
        description="What evidence would close remaining gaps",
    )


class RiskVector(BaseModel):
    """A risk identified during the debate, with position-relative context."""

    description: str
    agents_who_flagged: list[str]
    severity: Literal["low", "medium", "high"]
    phase_discovered: Literal["premortem", "position", "cross_examine"] = Field(
        description="Which phase first surfaced this risk. "
        "Premortem risks are seen BEFORE positional commitment."
    )


class RoundMetrics(BaseModel):
    """Convergence metrics for a single cross-examination round."""

    round: int
    mean_confidence: float
    dispersion: float = Field(description="Standard deviation of agent confidences")
    new_arguments: int = Field(description="Arguments not seen in prior rounds")
    concessions_made: int
    stopped_early: bool = Field(
        default=False,
        description="True if this round was cut short by convergence detection",
    )


class Disagreement(BaseModel):
    """A point of genuine disagreement that survived cross-examination."""

    topic: str
    positions: dict[str, str] = Field(
        description="Agent name -> summary of their position on this topic"
    )
    unresolved: bool = Field(
        default=True,
        description="Whether this disagreement persisted after all rounds",
    )


class Synthesis(BaseModel):
    """Structured output of a completed council debate."""

    # Metadata
    question: str
    mode: str
    num_agents: int
    rounds_completed: int
    stopped_reason: Literal[
        "converged",
        "max_rounds",
        "diminishing_returns",
        "genuine_disagreement",
    ] = Field(description="Why the debate stopped")

    # Convergence diagnostics
    confidence_history: list[RoundMetrics] = Field(
        description="One entry per cross-examination round"
    )
    final_dispersion: float
    mean_confidence_delta: float = Field(
        description="Change in mean confidence from first to last round"
    )

    # Content: premortem phase (pre-positional)
    shared_risks: list[RiskVector] = Field(
        description="Risks identified during pre-mortem before any agent "
        "formed a position. Compare with shared_concerns to see which "
        "worries survived cross-examination."
    )

    # Content: cross-examination phase (post-positional)
    shared_concerns: list[str] = Field(
        description="Concerns that survived cross-examination and are shared "
        "across agents. A risk in shared_risks that also appears here was "
        "confirmed by debate. A risk in shared_risks absent here is either "
        "resolved or buried by positional commitment."
    )
    disagreements: list[Disagreement]
    assumptions_per_position: dict[str, list[str]] = Field(
        description="Agent name -> assumptions that would need to hold "
        "for their position to be correct"
    )
    risk_vectors: list[RiskVector]
    principal_path: str = Field(description="Narrative synthesis of the decision landscape")


# ── Orchestration state (mutable dataclass) ──


@dataclass
class CouncilState:
    """Mutable state that flows through the debate graph."""

    question: str
    mode: str = "medium"
    max_rounds: int = 4
    convergence_threshold: float = 0.10

    personas: list[AgentPersona] = field(default_factory=list)
    premortems: dict[str, Premortem] = field(default_factory=dict)
    positions: dict[str, Position] = field(default_factory=dict)
    cross_examination_rounds: list[dict[str, CrossExamination]] = field(
        default_factory=list
    )
    synthesis: Synthesis | None = None
    round_number: int = 0
