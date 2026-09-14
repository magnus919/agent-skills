# Data Engineering

Data engineering methodology — database operations (vector, relational, graph, time-series), ETL/ELT pipeline design (dbt patterns, incremental loading), SQL analytical patterns, data quality monitoring, schema migration, and storage infrastructure management. Grounded in operational patterns for production data systems.

## Why Install This Skill

Your agent gets operational patterns for production data systems — real SQL, dbt models, backup commands, and migration strategies instead of textbook theory.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core methodology, trigger conditions, reference index |
| `references/` | Database operations, analytical SQL, pipelines, quality, migrations, recovery, and AI transformation boundaries |
| `templates/ai-stage-contract.md` | Pilot, version, retry, budget and publication evidence for an AI stage |

For AI-assisted data work, the [boundary workflow](references/ai-transformation-boundaries.md) helps keep uncertain
proposals out of trusted datasets. Use the [companion record](templates/ai-stage-contract.md) to retain
validation and review evidence.

## Triggers

Designing ETL/ELT pipelines, writing analytical SQL, operating vector/graph/time-series databases, planning migrations, setting up data quality monitoring, or defining validated model-assisted transformation boundaries.

## Requirements

Platform-agnostic. References cover PostgreSQL, DuckDB, ClickHouse, BigQuery, Snowflake, Neo4j, InfluxDB, TimescaleDB, and dbt.

## Quick Start

Start with a concrete pipeline or dataset boundary. For an AI-assisted transformation, fill in `templates/ai-stage-contract.md` with its input keys, validation rules, retry policy and publication conditions before running a pilot.
