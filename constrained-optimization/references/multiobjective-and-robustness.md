# Pareto and robustness decisions

When objectives conflict, first identify dominated candidates. A candidate is dominated if another is at least as good on every objective and strictly better on one, under the same feasibility rules. Present the remaining nondominated set with units and constraint residuals. Choose a point only after the decision maker states weights, lexicographic priorities, epsilon limits, or a policy preference. A weighted sum is a decision choice, not a neutral truth.

For noisy or stochastic objectives, define the randomization source and evaluation protocol. Use equal evaluation budgets, paired seeds where appropriate, and report mean/median, spread, worst observed feasible result, and failure/violation rate. Separate uncertainty in the objective measurement from uncertainty in the search procedure. Investigate a candidate that wins only because it has more attempts or a lucky seed.

Stress the selected solution against plausible parameter, demand, and constraint-bound changes. Record which constraints become active, which objective moves first, and whether a nearby feasible alternative is safer. Robustness evidence can justify a less optimal nominal point, but the preference must be explicit and the solution must remain feasible under the stated scenario.
