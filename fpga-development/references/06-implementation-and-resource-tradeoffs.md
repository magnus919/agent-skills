# Implementation and resource tradeoffs

Synthesis maps intent to a device architecture; implementation chooses physical resources and routes. Resource reports are evidence for design decisions, not merely capacity totals.

## Review dimensions

- LUT/ALM usage and logic depth;
- flip-flops and control-set pressure;
- BRAM/DSP/PLL usage and port/width limitations;
- I/O and clock-resource use;
- fanout, congestion, placement, and routing delay;
- latency, throughput, power, and bitstream size;
- portability cost of vendor primitives or generated IP.

Infer generic structures when portability matters; instantiate primitives when the performance/resource requirement and target documentation justify it. Record the portability boundary and generated-IP version. A smaller LUT count can still worsen timing through routing or fanout.

## Experiment discipline

Change one material design choice at a time. Preserve baseline netlist, constraints, utilization, timing, and power estimates where available. Compare identical seeds/options or record that the placer is stochastic. Define the acceptance metric before running the experiment: for example, positive worst slack with BRAM use below a stated budget and latency no greater than the interface contract.

Yosys documents synthesis phases and representations in [its synthesis guide](https://yosyshq.readthedocs.io/projects/yosys/en/v0.65/using_yosys/synthesis/). nextpnr describes itself as timing-driven and architecture-specific in its [project documentation](https://github.com/YosysHQ/nextpnr). These sources support flow roles; they do not establish support for a particular device build.

## Inference and reproducibility depth

For block RAM record depth/width mapping, synchronous versus asynchronous read, read-during-write mode, initialization, byte enables, and collision behavior. For DSP inference record signedness, operand widths, pre-adders, pipeline registers, saturation/rounding, and cascade use. A generic array can simulate one collision result and map to another primitive behavior.

Clock enables preserve a clock-tree relationship while gated clocks create a new clock object requiring timing analysis. Record fanout replication, congestion, route delay, switching activity, and whether power is an estimate or signoff result. Compare identical seed, constraints, effort, generated IP, speed grade, and corner; a better stochastic run is not a reproducible baseline until repeated.

## Failure gates

- resource utilization near device limits without margin policy: blocked;
- primitive/IP generated for an unrecorded device or tool version: blocked;
- optimization changes latency or protocol without contract update: blocked;
- implementation report missing timing/utilization artifacts: incomplete;
- benchmark compares different constraints, seeds, or tool versions without disclosure: inconclusive.

## Worked scenario: pipeline versus area

A multiplier-plus-add datapath meets functionally in simulation but misses timing by 1.2 ns. Adding a register between multiply and add may close timing but increases latency by one cycle and requires `valid`, `ready`, and reset alignment. The decision is acceptable only if the interface contract allows the new latency and the register does not break a CDC or feedback loop.

| Option | Timing effect | Resource/effect contract |
|---|---|---|
| pipeline stage | shorter combinational path | +FFs, +latency, valid alignment |
| DSP inference | dedicated arithmetic | target-specific availability |
| LUT arithmetic | portable | area and timing may worsen |
| time-multiplex unit | lower area | lower throughput and controller complexity |
| widen memory port | fewer cycles | BRAM shape and routing constraints |

Run a baseline and one change with identical target, constraints, tool release, and documented seed/options. Compare worst setup/hold slack, utilization by class, fanout/congestion, latency, throughput, and power estimate where available. If the placer is stochastic, repeat only under a declared experiment plan; do not select the best run silently.

Failure investigation starts with whether the report’s worst path is actually the changed logic. Then inspect inferred resources, control-set/fanout changes, and placement. A lower LUT count with worse route delay is a legitimate tradeoff that must be reported. Acceptance artifacts are paired build manifests, reports, latency proof, and the decision record.
