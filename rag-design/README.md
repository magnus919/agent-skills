# RAG Design

Design AI answers around evidence your users can access and verify.

## Why Install This Skill

Choosing a vector database leaves the hardest decisions open. Your assistant
helps you figure out whether your questions need exact search, semantic
matching, graph traversal, historical facts, or evidence from diagrams and
tables. It gives you a simple starting design and an evaluation plan for
deciding when to add complexity.

If several teams share one service, the skill helps you plan who can read,
contribute, publish, and share which evidence. It follows those decisions
through chunks, graph relationships, summaries, citations, and cached answers,
including what happens after an access change or a deletion.

## What You Get

| Content | What it provides |
|---|---|
| [Architecture guide](references/retrieval-architectures.md) | Patterns for vector, hybrid, graph, temporal, and multimodal RAG |
| [Temporal RAG](references/temporal-rag.md) | Join measurements, timelines, and evidence to report trends or calibrated forecasts |
| [RAG harness](references/rag-harness.md) | A predictable workflow for multimodal evidence, authorization, and recovery |
| [Memory workers](references/memory-workers.md) | Maintain indexes and agent memory with reviewable background work |
| [Authorization guide](references/authorization-and-tenancy.md) | Read and write policy, evidence lineage, and tenant isolation |
| [Implementation guide](references/implementation-and-evaluation.md) | Personal and enterprise examples with acceptance criteria |
| [Research brief](references/research-brief.md) | Findings and links to the primary-source evidence |
| [Design record](templates/rag-design-record.md) | A reusable format for an architecture decision |

## Quick Start

Give your agent a few questions and the places where the answers should come
from. For example, ask it to design an assistant for a shared handbook with a
restricted appendix and a dashboard that tracks changes over time. Ask for a
completed design record with a baseline, access rules, and acceptance cases.

## Triggers

- Plan RAG for a personal vault, an internal knowledge base, or several customers.
- Choose between vector search, graph traversal, and visual document retrieval.
- Determine who can read or write individual pieces of shared knowledge.
- Diagnose weak citations, stale facts, or uneven search quality across teams.

## Requirements

No installation dependencies beyond an agent that supports skills. Useful
inputs include sample questions, representative documents, and any existing
access and retention policies.
