# ESP32 Development Skill

Build and troubleshoot complete ESP32 systems, from the USB cable and pin wiring through firmware, sensors, actuators, networking, OTA, and recovery.

## Why Install This Skill

ESP32 development is fragmented across chip families and firmware ecosystems. A command that works for one board can flash the wrong image layout on another; a GPIO that is harmless on an ESP32 can be a strapping, flash, USB, or input-only pin elsewhere. Most costly failures happen at those boundaries, not in the application loop.

This skill gives an agent a source-backed workflow for identifying the actual board, choosing an appropriate framework, using its native command-line tools, and proving attached hardware one layer at a time. It covers ESP-IDF C/C++, Arduino and PlatformIO, MicroPython, CircuitPython, ESPHome, Zephyr, Rust, and NuttX without tying the process to one agent harness.

## What You Get

| Resource | Purpose |
|---|---|
| `SKILL.md` | Safety-first workflow and routing table |
| `references/` | Framework, hardware, peripheral, networking, recovery, security, and source guidance |
| `templates/` | Bring-up worksheet plus minimal framework and bus examples |
| `scripts/esp32-preflight.py` | Dependency-free host, toolchain, and candidate-port discovery without opening a port |
| `evals/evals.json` | Safety and troubleshooting scenarios for regression evaluation |

## Quick Start

Run the non-mutating preflight from the skill directory:

```sh
python3 scripts/esp32-preflight.py
```

Example shape of the output:

```text
host: Darwin arm64
tools:
  esptool: /path/to/esptool
  pio: /path/to/pio
  mpremote: missing
candidate ports:
  /dev/cu.usbmodem1101
next: identify the exact board before opening or flashing a port
```

Then copy `templates/hardware-bringup.md` into the project and record the exact board, SoC, power, pin, attached-component, and recovery sources before wiring or flashing.

## Triggers

Use this skill for ESP32 board identification, framework selection, C/C++ firmware, Arduino or PlatformIO projects, MicroPython or CircuitPython, ESPHome configuration, Zephyr, Rust, NuttX, serial flashing, OTA, GPIO and bus wiring, sensors, displays, relays, motors, LEDs, deep sleep, Wi-Fi/BLE, ESP-NOW, Zigbee/Thread, JTAG, secure boot, flash encryption, eFuses, crash decoding, brownouts, or bootloader recovery.

## Requirements

Python 3.9+ is sufficient for the bundled preflight. Live development requires a supported ESP32-family board, a data-capable USB cable or debugger, host serial permissions, and the native toolchain for the chosen framework. Attached circuits require their own datasheets, safe power supplies, level shifting or drivers where needed, and suitable test equipment. No API key is required.
