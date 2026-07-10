# Debate Protocol

## Phase Structure

### Phase 1: Compose

A single LLM call generates `N` expert personas. The prompt prioritizes **diversity of initial position** over diversity of expertise. Each persona includes:
- Name
- Career background (one paragraph)
- Specific expertise
- Analytical approach
- Bias or experience they bring to the specific question

At least one agent is structurally skeptical (light red-team). At least one approaches from a fundamentally different cognitive frame.

### Phase 2: Premortem

Each agent independently writes how the decision **already failed** — before any positions are formed. This bypasses positional commitment bias. Agents do NOT see each other's premortems.

The premortem output includes:
- Failure scenario (narrative)
- Root causes
- Early warning signals

### Phase 3: Position

Each agent forms an independent position. They see their own premortem (for continuity) but NOT other agents' positions or premortems.

Position output includes:
- Stance
- Reasoning chain
- Confidence score (0-1)
- Key assumptions

### Phase 4: Cross-Examination (Iterative)

Each agent reads all other agents' positions and responds. They see:
- Every other agent's stance, reasoning, confidence, and assumptions
- Their own previous round's reflection, concessions, and remaining disagreements

Cross-examination output includes:
- Concessions (where the other agent's reasoning was stronger)
- Remaining disagreements (what's still in dispute)
- Updated position (if changed)
- Updated confidence (if changed)
- Reflection on what they learned
- New evidence needed to close gaps

After each round, convergence detection runs:
- If converged → proceed to synthesis
- If diminishing returns → proceed to synthesis
- If genuine disagreement → proceed to synthesis (with divergence report)
- If more debate needed → run another round (up to max_rounds)

### Phase 5: Synthesis

The synthesis combines algorithmic metrics (confidence dispersion, argument novelty) with an LLM-generated narrative. The output preserves the distinction between:
- **Pre-positional risks** (from premortem — uncontaminated by positional commitment)
- **Post-positional concerns** (survived cross-examination — tested against alternatives)

## Design Principles

1. **Independent thought first** — agents form positions before seeing others'
2. **Diversity over expertise** — different approaches beat more expertise with shared framing
3. **Pre-mortem before position** — surface failure modes before committing to a stance
4. **Convergence is measured, not assumed** — algorithmic stopping conditions prevent premature or interminable debate
5. **Tension is the output** — the synthesis surfaces genuine disagreement, not forced consensus
