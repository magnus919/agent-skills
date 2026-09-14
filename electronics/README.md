# Electronics

Design, review and troubleshoot circuits with calculations and measurements you can defend.

## Why Install This Skill

A circuit can look correct and still fail because a component is loaded differently than expected, a sensor saturates, a supply overheats or a probe changes the signal. This skill helps your agent connect component specifications, circuit models, physical assembly and measured behavior into one engineering decision.

It provides detailed references and reusable worksheets for selecting parts, bounding errors, reviewing power and protection, integrating sensors, diagnosing I2C and planning bench tests. You get concrete review artifacts and explicit evidence gaps, with ESP32 firmware work kept in its existing specialist skill.

## What You Get

| Contents | Purpose |
|---|---|
| `SKILL.md` | Task selection and the design-to-verification workflow |
| `references/` | Ten detailed guides for components, calculations, circuits, power, sensors, I2C, assembly and measurement |
| `templates/` | Eight reusable component, calculation, calibration, wiring, bus, measurement, fault and acceptance records |
| `evals/` | Eight output-quality scenarios covering calculations, uncertain evidence and diagnosis |

## Quick Start

Provide the schematic, exact component identities and the decision you need. Ask for a component contract, calculation record or measurement plan; the templates work without installing a toolchain.

## Triggers

- Review a schematic, component substitution or electrical interface.
- Calculate worst-case error, loading, power or thermal margin.
- Integrate sensors or diagnose an intermittent I2C bus.
- Plan bench measurements, localize a fault or verify an assembly.

Try: “Review this divider against the ADC input limit, including resistor tolerances and loading, and produce a calculation record.”

## Requirements

Reading and planning require no installed tools. Device-specific decisions require the exact datasheets, schematics and operating requirements. Physical verification requires appropriate instruments, target access and a safe measurement setup. This skill does not provide certification or replace specialized high-energy, RF or high-speed design review.
