# Formulation and solver evidence

## Formulation checklist

Write the problem in a unit-consistent form: decision vector and domains; objective(s) with minimize/maximize direction; hard constraints and tolerances; soft constraints and penalty units; data/configuration revision; and a feasibility predicate that can be run independently. Normalize objectives only when the scale and reference points are documented. A penalty coefficient must have an interpretable relationship to the objective and cannot make an unacceptable hard violation “worth it.”

Use a feasible incumbent whenever possible. If no feasible point is known, run a feasibility phase or report that the search has not established feasibility. A candidate with a better raw objective but any hard violation is not a solution to the stated problem.

## Method evidence

Use an exact or certifying baseline when the formulation and scale allow it. Report solver status, incumbent objective, bound, gap definition, time/memory limit, and tolerance. A feasible incumbent with a nonzero gap is evidence of a candidate and a bound, not proof of global optimality. A heuristic or metaheuristic should report initialization, seed/repeat policy, budget, best feasible value, violation summary, and comparison against the same checker and budget.

Solver status is evidence, not prose. For example, SciPy’s optimization results expose `success` and a termination `message`, while its linear-programming tutorial demonstrates checking constraint residuals independently. OR-Tools CP-SAT distinguishes `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `MODEL_INVALID`, and `UNKNOWN`; `UNKNOWN` includes stopping before infeasibility is proven. Preserve that distinction in any adapter. See [the source index](source-index.md) for direct official references, versions, and transfer limits.

## Fair comparison and validation

Freeze the formulation, data, checker, hardware class, wall-clock or evaluation budget, and stopping rule. Compare methods on the same feasible-best definition. For stochastic methods, use paired seeds or a declared repeat design and report the distribution, not only the best run. Validate returned decisions with an independent implementation that recomputes units, bounds, equality/inequality residuals, and objective. Keep raw solver output and checker output together.

An “infeasible” conclusion requires a certificate or a solver status that actually proves infeasibility. A timeout, memory stop, numerical failure, or unknown status means unresolved. Relax constraints only as a named scenario and rerun the full audit; never silently relax them in post-processing.
