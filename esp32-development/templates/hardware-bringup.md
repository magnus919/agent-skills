# ESP32 hardware bring-up

## Target identity

- Board product and revision:
- SoC family and revision:
- Module marking:
- Flash / PSRAM:
- USB connector and transport:
- Stable port identity:
- Existing firmware / bootloader:

## Authoritative sources

| Artifact | URL or local document | Revision / access date | Decision supported |
|---|---|---|---|
| Board schematic | | | |
| Board pinout/user guide | | | |
| Module datasheet | | | |
| SoC datasheet/errata | | | |
| Framework board definition | | | |
| Attached component datasheet | | | |
| Breakout/module schematic | | | |

## Power budget

| Rail / source | Voltage | Continuous limit | Peak load | Consumers | Measured |
|---|---:|---:|---:|---|---|
| | | | | | |

- Logic voltage:
- Shared ground or isolation:
- Decoupling / bulk capacitance:
- Brownout margin:
- Worst-case radio + actuator condition:

## Pin plan

| Function | GPIO / board alias | Direction | Reset state | Pull / level | Conflicts checked | Source |
|---|---|---|---|---|---|---|
| | | | | | | |

Check for strapping, flash/PSRAM, USB/JTAG, console, input-only, ADC, RTC/wake, onboard peripherals, and boot-time pulses.

## Attached devices

| Device | Interface | Address / CS | Supply | Peak current | Driver / protection | Identity check |
|---|---|---|---:|---:|---|---|
| | | | | | | |

## Firmware path

- Framework and pinned version:
- Exact board/target identifier:
- Project generator/example:
- Build command:
- Flash command and source of offsets:
- Monitor/log command:
- Debugger/test command:
- OTA/update path:
- Known-good recovery image and procedure:

## Layered verification

- [ ] Rails and polarity checked before attaching signals
- [ ] Board-only boot log captured
- [ ] Exact target and memory confirmed
- [ ] One GPIO proved with a benign load
- [ ] Bus electrical idle/loopback/scan proved
- [ ] Device identity/status register proved
- [ ] Raw readings or unloaded control signal proved
- [ ] Calibration or loaded actuator behavior proved
- [ ] Reset and power-cycle behavior proved
- [ ] Network loss/reconnect proved when applicable
- [ ] OTA rollback or serial recovery proved when applicable

## Known gaps and risks

-
