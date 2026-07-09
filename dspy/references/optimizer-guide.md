# DSPy Optimizer Guide

DSPy ships a dozen optimizers (teleprompters). This reference covers selection, configuration, and cost.

## The Three Knobs

Every optimizer tunes one or more of: **instructions** (the natural-language docstring on each predictor's signature), **demos** (in-context examples each predictor sees), or **weights** (model parameters via fine-tuning).

## Selection Cheat Sheet

| Situation | Try |
|-----------|-----|
| Just starting; no idea what helps | `BootstrapFewShot` |
| Demos vary in quality across attempts | `BootstrapFewShotWithRandomSearch` |
| Large trainset; inputs need different demos | `KNNFewShot` |
| Instructions look wrong; demos look fine | `COPRO` or `GEPA` |
| Both look weak; you have budget | `MIPROv2` or `GEPA` |
| Failure cases share a pattern you can name | `SIMBA` or `InferRules` |
| Prompt-only has plateaued; model is tunable | `BootstrapFinetune` |
| Combine prompt + weight tuning | `BetterTogether` |
| Multiple competent programs to combine | `Ensemble` |
| Agent / tool-use task | `AvatarOptimizer` or `GEPA` |

## Quick Start Optimizers

### LabeledFewShot (zero-cost baseline)

```python
from dspy.teleprompt import LabeledFewShot

optimizer = LabeledFewShot(k=16)
compiled = optimizer.compile(program, trainset=trainset)
```

No LM calls during compile. Samples up to k examples from trainset. If this works, stop here.

### BootstrapFewShot (safe first try)

```python
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=dspy.answer_exact_match,
                             max_bootstrapped_demos=4,
                             max_labeled_demos=16)
compiled = optimizer.compile(program, trainset=trainset)
```

Runs the program on training examples, keeps traces where the metric passes. Almost always beats zero-shot.

## Instruction Optimizers

### COPRO — Lightweight Instruction Fixes

```python
from dspy.teleprompt import COPRO

optimizer = COPRO(prompt_model=lm, metric=metric, breadth=10, depth=3)
```

Breadth-first proposer. Generates candidate instructions, scores them, keeps the best. Total cost: breadth x depth x num_predictors. Good when demos are strong and you only need wording fixes.

### GEPA — Evolutionary Instruction Search

```python
from dspy.teleprompt import GEPA

optimizer = GEPA(metric=metric, auto="light", reflection_lm=strong_lm)
```

Evolutionary search guided by reflection. Maintains a population of programs, reads per-predictor feedback from the metric, proposes edits informed by that feedback. Wins on prompt-only optimization when you have a strong reflection LM and a feedback-shaped metric. **Only optimizer that reads `Prediction(score, feedback)`.**

### MIPROv2 — Joint Instruction + Demo Optimization (SOTA)

```python
from dspy.teleprompt import MIPROv2

optimizer = MIPROv2(metric=metric, auto="medium",
                    prompt_model=strong_lm, task_model=lm)
compiled = optimizer.compile(program, trainset=trainset)
```

Bayesian optimization over joint instruction + demo space. State of the art when both need tuning. Auto modes: "light", "medium", "heavy" control the budget (proposals and evaluations).

## Demo Optimizers

### BootstrapFewShotWithRandomSearch

```python
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

optimizer = BootstrapFewShotWithRandomSearch(metric=metric,
    num_candidate_programs=16, num_threads=10, stop_at_score=0.95)
compiled = optimizer.compile(program, trainset=trainset)
```

Runs BootstrapFewShot N times with different random seeds, returns highest scoring.

### KNNFewShot — Dynamic Demo Selection

```python
from dspy.teleprompt import KNNFewShot

optimizer = KNNFewShot(k=5, trainset=trainset)
```

Demos chosen at inference time — embeds the input, retrieves k nearest training examples. Good when no single demo set generalizes across the input distribution.

## Weight Optimizers

### BootstrapFinetune

```python
from dspy.teleprompt import BootstrapFinetune

optimizer = BootstrapFinetune(metric=metric)
compiled = optimizer.compile(program, trainset=trainset)
```

Bootstraps successful traces, writes them as training data, fine-tunes the LM. Requires an LM with a `.finetune()` method.

## Compose Optimizers

### BetterTogether — Prompt + Weight Tuning

```python
from dspy.teleprompt import BetterTogether, GEPA, BootstrapFinetune

optimizer = BetterTogether(metric=metric,
    prompt_optimizer=GEPA(...),
    weight_optimizer=BootstrapFinetune(...))
```

Meta-optimizer that runs a sequence: prompt -> weight -> prompt.

## Key Configuration Rules

- `auto` modes ("light"/"medium"/"heavy") control budget. Cannot set `num_candidates` or `num_trials` when `auto` is set.
- `_compiled = True` flag prevents sub-modules from being re-optimized. Set to False before recompiling.
- `.compile()` returns a new copy; the original isn't mutated.
- Prompt-only optimizers work with any LM (including closed-source). Finetune optimizers need a tunable model.
- Demo-tuning tends to overfit; instruction-tuning tends to generalize.
