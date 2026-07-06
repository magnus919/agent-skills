# Critiques & Tradeoffs

SDD is not a silver bullet. This reference covers when it fails, the hard tradeoffs, and how to mitigate them.

## 1. Spec as Bottleneck

**The problem:** SDD creates a serial dependency at the spec phase — no code can be written until the spec is approved. In fast-moving projects, this causes:
- Developer/agent idle time while waiting for spec approval
- Pressure to deliver specs faster, reducing quality
- Specs that pass the gate check but aren't actually good enough

**Mitigation:**
- Write specs iteratively — one feature at a time, not the entire system
- Use AI-assisted spec authoring to accelerate spec writing
- Tighten the spec scope to what's necessary for the next implementation phase
- Distinguish between "specs that drive the factory" vs "light specs for prototypes"

**Truth:** SDD shifts the bottleneck from debugging code to writing specs. Depending on your team's skills, this may or may not be a net improvement.

## 2. Garbage In, Garbage Out (GIGO)

**The hardest problem in AI code generation:** Spec quality is the most difficult engineering problem. It's easy to verify code against a spec. It's hard to verify a spec against stakeholder intent.

**Root cause:** AI agents cannot ask clarifying questions. A vague spec produces working-but-wrong code. An ambiguous term produces code implementing the wrong interpretation. A missing edge case produces code that crashes in production.

**Mitigation:**
- The 7 quality gates in this skill exist specifically to catch GIGO before code generation
- Spec quality checks should be automated (see `spec-quality-check.sh`)
- Spec review should have the same rigor as code review
- Invest in spec templates and spec quality infrastructure before scaling the factory

## 3. Spec Drift vs Code Drift

Two failure modes that compound over time:

| Failure Mode | Description | Prevention |
|-------------|-------------|-----------|
| **Spec drift** | Spec changes but code doesn't → spec becomes outdated, verification passes wrong things | Spec-as-code discipline: spec changes follow the same PR process as code changes |
| **Code drift** | Code changes but spec doesn't → spec no longer reflects the actual system | Living documentation: when spec IS the test, drift is impossible (for behavioral specs) |

**The hard truth:** Even with living documentation, only behavioral specs stay synced. Architecture specs, NFR specs, and design decision docs will drift without active maintenance.

## 4. The Precision-Clarity Tradeoff

This is the defining tension of SDD:

**For human developers:** clarity > precision. Some ambiguity is acceptable because humans clarify through conversation.

**For AI agents:** precision > clarity. The spec must be exact even if it's dense. The agent cannot ask for clarification.

The result: **specs optimized for AI consumption are harder for humans to write and review.** Business stakeholders may struggle to validate dense, technical specs. Spec reviewers need a different skill set than traditional requirements review.

**Mitigation:**
- Dual-format specs: AI-precise format for the agent, human-readable summary for stakeholders
- AI-assisted spec authoring (AI produces the dense spec, human reviews for intent)

## 5. Over-Specification

Specs that are too rigid cause:
- AI agents produce suboptimal code because the spec constrains the implementation unnecessarily
- False precision — specifying things that should be implementation details
- Spec maintenance burden for decisions that could have been left open

**The threshold:** A good spec specifies WHAT but not HOW — except when the HOW matters (performance, security, compliance, maintainability). Determining this boundary is a judgment call.

**Anti-pattern:** Specifying the algorithm, data structure, or UI framework in the spec when it's an implementation detail.

## 6. Under-Specification

The opposite problem — specs too vague for AI agents:
- Agents fill gaps with random interpretations
- Different agents produce incompatible implementations from the same spec
- Reviewers cannot assess completeness
- Edge cases are discovered in production, not in specification

**The trap:** "Good enough to be understood by a human" is not "good enough for an AI agent." Human readers correct for ambiguity unconsciously; agents propagate it faithfully.

## 7. The "Formal Methods Tax"

TLA+, Alloy, and formal verification provide the strongest guarantees but at high cost:
- Requires specialized mathematical training
- Slow to write (hours for what a paragraph describes in minutes)
- Covers specific properties only (safety/liveness), not full system behavior
- Model checking is limited by scope size (Alloy's "small scope hypothesis")

**Verdict:** Use formal methods only for critical subsystems where the cost of failure exceeds the cost of formal specification. Not for entire codebases.

## 8. Maintenance Burden

Every requirement change requires:
- Spec update (same effort as updating code)
- Re-review through the SDD gate
- Re-verification of existing functionality
- Version management across multiple spec iterations

**When this hurts most:** Rapidly changing requirements during early exploration. If requirements change faster than you can write specs, SDD is the wrong approach.

## 9. When NOT to Use SDD

| Context | Why SDD Fails | Better Approach |
|---------|--------------|-----------------|
| Throwaway prototypes | Spec cost > bug-fix cost | Just code it |
| Genuinely unknown requirements | You can't specify what you don't know | Exploration-first, spec later |
| Rapid exploration phase | Requirements change faster than spec updates | Agile/iterative, no formal gate |
| Single-developer greenfield | Overhead of gates slows velocity | Lightweight spec only |
| UI-heavy with dynamic requirements | Spec for visual/interaction behavior is fragile | Click-through prototypes, spec only core logic |
| Team won't maintain specs | Spec becomes shelf-ware within weeks | Don't start — the drift will be worse than no spec |

## The SDD Paradox

The fundamental tension that every SDD practitioner must accept:

> The more valuable a spec is for AI code generation (precise, structured, testable), the harder it is for humans to write, maintain, and validate.

This creates the market for:
- **AI-assisted spec authoring** — AI writes the structured spec from natural language, human reviews
- **Spec quality automation** — linting, validation, gap detection
- **Spec inference from code** — reverse-engineering specs from existing systems

The paradox doesn't invalidate SDD. It defines where SDD is worth the investment and where it isn't.
