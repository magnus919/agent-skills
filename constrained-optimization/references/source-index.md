# Primary sources and applicability

Checked 2026-09-14. These links support interpretation of solver evidence; this methodology does not install or operate these tools. Record the installed solver version, selected method, options, and matching documentation in each solution audit.

| Source | Documentation scope observed | Use and limit |
|---|---|---|
| [SciPy OptimizeResult](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.OptimizeResult.html) | SciPy 1.18.0 reference | Explains success, status, termination messages, and optional result fields. Available fields and status meanings depend on the solver; successful termination alone is not a universal global-optimality certificate. |
| [SciPy linprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html) | SciPy 1.18.0 reference | Defines linear objectives, constraints, bounds, residuals, and method-specific results. Recompute constraints from the original formulation and declared tolerance. Do not transfer linear-programming guarantees to nonlinear or heuristic methods. |
| [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver) | Unversioned official guide, checked on the date above | Describes integer constraint models and distinct optimal, feasible, infeasible, invalid-model, and unknown outcomes. Preserve the returned status; a search limit does not establish infeasibility. Integer scaling and finite domains must preserve the intended formulation. |

Re-check the exact release and algorithm before relying on a field, tolerance, gap, or certificate. These sources illustrate evidence interpretation; they do not make one solver suitable for every formulation or validate an application model.
