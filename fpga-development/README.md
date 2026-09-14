# FPGA Development

Make FPGA design decisions traceable from interface contract through verification and implementation evidence.

## Why Install This Skill

Passing simulation is only one part of FPGA correctness. Clock-domain transfers can lose data, arithmetic can silently overflow, and apparently green timing reports can omit important paths. This skill helps your agent find those gaps and turn them into concrete design, verification and release decisions.

Detailed references and reusable templates cover RTL, arithmetic, testbenches, clocks and resets, timing constraints, resource tradeoffs and hardware verification. An original ready/valid buffer example provides a small executable demonstration of backpressure and transaction checking. Device-specific commands and electrical limits still come from the actual board and tool documentation.

## What You Get

| Contents | Purpose |
|---|---|
| `SKILL.md` | Design and verification workflow with clear completion criteria |
| `references/` | Seven detailed guides from interface contracts to release evidence |
| `templates/` | Six target, RTL, simulation, CDC, timing and release worksheets |
| `assets/` and `scripts/` | Original buffer example and offline simulation/synthesis verification |
| `evals/` | Eight output-quality scenarios covering CDC, arithmetic, timing, protocols and provenance |

## Quick Start

Start with: “Review this clock-domain crossing and produce a CDC review with throughput, reset and data-coherency assumptions.” From this skill directory, run the offline example with a new or empty output directory:

```sh
python3 scripts/fpga_fixture.py --json --output /tmp/fpga-example-results
```

With the required tools installed, expect separate passing simulation and generic synthesis results. Missing tools report an incomplete run. Logs, source hashes and tool versions are retained with the results.

## Triggers

- Design or review synthesizable HDL and fixed-point arithmetic.
- Investigate simulation, reset, handshake or clock-domain problems.
- Review timing coverage and exceptions or plan timing closure.
- Assess implementation reports and reproducible release evidence.

## Requirements

Methodology and review need only the relevant design artifacts. Executable example checks require Python 3, Icarus Verilog and Yosys. Target implementation and hardware verification require the exact device/board, supported toolchain, constraints and programming access. Generic simulation and synthesis do not establish device timing or physical operation.
