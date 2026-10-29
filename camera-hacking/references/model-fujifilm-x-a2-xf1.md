# Fujifilm X-A2 and XF1

Accessed 2026-10-29. Primary source: [Fujifilm X-A2 and XF1 project documentation](https://fujihack.org/). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Target identity

The project identifies **X-A2 1.30** and **XF1 1.01** for code runners. These are explicit research targets, not a proxy for all Fuji RTOS bodies.

## Mechanism and evidence

[Fujihack source](https://github.com/fujihack/fujihack) describes patched firmware, USB execution and RTOS bindings. The public project distinguishes research achievements from public-use readiness. It also describes boot-ROM recovery as not reverse-engineered; do not replace that gap with a generic “flash stock again” instruction.

## Next evidence

For a chosen feature, inspect its target stubs, patch identity, device validation record and cold-start behavior. For newer X/GFX interoperability, investigate libfuji's per-model controls rather than borrowing these firmware patches. No patcher was executed or camera contacted here.
