# Implementation and hardware release record

## Build identity

- Source revision:
- Target device/package:
- Tool versions and commands/project archive:
- HDL/constraint/IP manifests:
- Bitstream filename and SHA-256:

## Implementation evidence

- Synthesis result and warnings:
- Resource/utilization report:
- Place-and-route result:
- Timing report:
- CDC report:
- Power/thermal estimate, if applicable:

## Hardware observation

| Test | Setup/instrument | Expected | Observed | Artifact |
|---|---|---|---|---|
| identity/reset | | | | |
| GPIO polarity | | | | |
| interface pattern | | | | |
| reset/reprogram | | | | |
| power cycle | | | | |

## Release gate

- Programmed target identity verified: yes/no
- Bitstream hash verified: yes/no
- Recovery image/path tested: yes/no
- Remaining unknowns and limits:
- Decision: RELEASE / HOLD / INCONCLUSIVE

## Review instructions

The bitstream hash must be calculated from the exact reviewed artifact and matched after programming where the transport permits verification. Link each report to the same source and constraint revision. Repeat hardware checks after any pin, clock, reset, generated-IP, or tool-version change.

## Example decision

`HOLD`: build reports meet timing, but the programmed target ID is not captured and the recovery image was never tested. Preserve the candidate, verify identity, and prove recovery before release.
