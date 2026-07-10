# DSPy — Programming, Not Prompting Language Models (Stanford)

An expert-level skill for **programmatic prompt optimization** with Stanford's DSPy framework. You write Python programs with typed signatures; DSPy optimizes the prompts automatically. This is the framework for prompt engineering that doesn't feel like engineering.

## Why Install This Skill

When your agent loads this skill, it becomes a DSPy expert who can:

- **Define typed signatures** — input/output schemas with descriptions
- **Build program modules** — Predict, ChainOfThought, ReAct, and custom Module subclasses
- **Select optimizers** — MIPROv2, BootstrapFewShot, BootstrapFinetune — matching optimizer to bottleneck
- **Compile programs** — transform a Python program into an optimized, prompt-efficient artifact
- **Evaluate and iterate** — metrics, datasets, and optimization loops

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core paradigm, optimizer cheat sheet, compilation pipeline |
| `references/` | Signatures deep dive, module patterns, optimizer selection guide, evaluation methodology |

## Framework Comparison

DSPy is **not** a chain or RAG framework. It operates at the compiler layer — you define the program structure, DSPy optimizes the prompts. Use this when you want prompt engineering to be deterministic and testable, not a manual tuning exercise.

## Requirements

Python 3.8+ with `dspy` package.
