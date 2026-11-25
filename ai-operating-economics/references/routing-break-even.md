# Find the cheap-path break-even point

To isolate routing, compare it with an already acceptable fixed-model path,
not only the prior manual workflow. For the same eligible task mix, let `B`
be fixed-path cost per attempted task, `R` shared router overhead on each
attempt, `C` all-in cost conditional on finishing on the cheap path, and `F`
all-in cost conditional on leaving it. Include spent cheap inference, the
second attempt, cold-cache reprocessing, tool duplication and reviewer time
in the relevant conditional path, not in both it and `R`. Let `p` be the
fraction of eligible attempts that finish on the cheap path. In this simple
two-path model, routed cost is `R + p*C + (1-p)*F`. If `F > C`, it beats
the fixed cost when `p > (R + F - B)/(F - C)`. A threshold at or above 100%
means no strict savings in this scenario; if path costs don't follow this
ordering, compare the actual totals instead.

Synthetic example: `B = $1.00`, `R = $0.05`, `C = $0.30`, `F = $1.25`.
Break-even is about 31.6%; at 25% cheap-path completion it costs about $1.06
per attempt; at 60%, $0.73. This cost screen assumes equal acceptance and
hard-control behavior. If acceptance differs, compare cohort totals divided
by actually accepted outcomes, keep the quality floor binding, and include
unresolved work in attempted costs. Use more paths if direct premium routing
and a premium retry have different costs. Test low-volume, cold-cache and
elevated-fallback scenarios before inferring budget savings.

See [LangChain's Open SWE example](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)
for why losing a prompt cache can change the economics of a mid-thread switch.
