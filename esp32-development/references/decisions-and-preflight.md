# Decisions and preflight

Use this before selecting a framework, opening a serial port, or copying a pin map.

## Evidence to collect

| Question | Strong evidence | What it does not prove |
|---|---|---|
| What board is connected? | Silkscreen, product page, schematic, USB VID/PID/product string | A marketing name may cover multiple board revisions. |
| What SoC/module is fitted? | Module shield marking, board BOM/schematic, `esptool chip-id` after a successful bootloader connection | A serial device name alone does not identify the SoC. |
| What memory is present? | Module/board specification plus `esptool flash-id` or framework build metadata | Configured size is not measured size. |
| Which port is it? | Disconnect/reconnect diff, stable `/dev/serial/by-id/`, USB location/serial number | First port in a list is not necessarily the target. |
| What firmware is running? | Boot log, REPL banner, application version endpoint, image metadata | USB manufacturer text can describe the board, not the active firmware. |
| Can it be recovered? | Documented ROM download mode, BOOT/RESET access, known-good image and offsets | OTA availability is not a substitute for serial recovery. |

Run the bundled non-mutating classifier first:

```sh
python3 scripts/esp32-preflight.py --json
```

Then use whichever native enumerator is already installed:

```sh
pio device list --json-output
mpremote connect list
```

On Linux, prefer `/dev/serial/by-id/` over an unstable `/dev/ttyUSB0` assignment when available. Confirm group/udev permissions before using elevated privileges. On macOS, `/dev/cu.*` is normally appropriate for outgoing serial sessions. On Windows, use Device Manager or a framework-native device list to map the COM port to its USB descriptor.

## Do not open every port

Bluetooth pseudo-ports, debug consoles, unrelated radios, and non-ESP32 microcontrollers may appear beside the target. Probe only a port tied to the expected USB device. Opening a monitor or flasher can toggle DTR/RTS and reset hardware. ESP-IDF Monitor supports:

```sh
idf.py monitor --no-reset -p PORT
```

A failed `esptool chip-id` means only that the ROM loader handshake did not complete. Common explanations include the wrong port, charge-only cable, permission problem, port already open, target not in download mode, unsupported reset wiring, native-USB mode, weak power, or a non-Espressif device. Do not respond by erasing flash.

## Framework decision

Choose the smallest supported control plane that meets the product need:

| Constraint | Default | Why |
|---|---|---|
| Full Espressif feature access, production controls, C/C++ | ESP-IDF | Canonical SDK and source of partition, OTA, security, and low-level driver behavior. |
| Arduino libraries or beginner C++ workflow | Arduino core | Familiar API and large library ecosystem; still validate ESP32-specific pin and peripheral behavior. |
| Arduino/ESP-IDF with reproducible CLI environments and tests | PlatformIO | Project-level platform/framework/board declaration and native build/upload/monitor/test commands. |
| Fast interactive Python iteration on constrained hardware | MicroPython | REPL plus `mpremote`; API and board support differ from CPython. |
| Board-first Python library ecosystem and supported CircuitPython board | CircuitPython | `board` aliases and Adafruit library workflow; verify whether the exact ESP32 board/SoC is supported. |
| Declarative Home Assistant device | ESPHome | Generated firmware, native API/OTA, extensive component catalog, and config validation. |
| RTOS portability, devicetree, Kconfig, upstream drivers | Zephyr | Appropriate when the application needs Zephyr's architecture and the board/peripherals are supported. |
| Rust safety and ecosystem are explicit requirements | Rust on ESP | Use official Espressif Rust guidance; choose `no_std` `esp-hal` or ESP-IDF-based `std` deliberately. |
| POSIX-like RTOS/NuttShell or existing NuttX product | NuttX | Mature RTOS option, but not a default for a new general-purpose ESP32 prototype. |

Do not migrate a working project merely because another framework is listed. Cross-framework rewrites change drivers, timing, partitions, networking, and recovery behavior.

## Board and feature questions

Before committing to a family, verify the exact SoC documentation for:

- CPU architecture and core count;
- Wi-Fi generation and whether Bluetooth, BLE, Zigbee/Thread, Ethernet MAC, or no radio is present;
- native USB, USB Serial/JTAG, external bridge, or UART-only download path;
- flash and PSRAM interfaces and module-installed memory;
- GPIO count and restrictions;
- ADC/DAC/touch capabilities;
- low-power modes and wake sources;
- JTAG exposure and production security interactions.

The `ESP32` name is a family label. A feature present on classic ESP32 may be absent or materially different on C-, S-, H-, or P-series parts.
