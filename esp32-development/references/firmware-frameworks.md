# Firmware frameworks

This reference defines the boundary and native workflow for each supported firmware family. Read the framework's current official documentation before using version-sensitive flags or APIs.

## ESP-IDF C/C++

Use for canonical Espressif support, production security, custom partitions, advanced networking, low-level drivers, FreeRTOS integration, and exact SoC capabilities.

```sh
idf.py set-target esp32s3       # use the exact target
idf.py menuconfig
idf.py build
idf.py -p PORT flash monitor
```

`idf.py flash` builds as needed and uses generated flash arguments. Prefer it over manually reconstructing `esptool write-flash` offsets. Start from an official example under the installed ESP-IDF version and preserve `sdkconfig.defaults` for intentional project settings. Treat generated `sdkconfig` and build output as version-specific.

## Arduino core for ESP32

Use when the project benefits from Arduino APIs/libraries and does not require ESP-IDF as its primary interface. Use the official board package, select the exact board and flash/partition options, and test ESP32-specific APIs rather than assuming AVR behavior.

For CLI automation, prefer Arduino CLI or PlatformIO over GUI-only instructions. Inspect the official Arduino-ESP32 API page for GPIO, ADC, I2C, SPI, UART, BLE, USB, and the exact chip family. Core 2.x and 3.x have material API migrations; do not copy old signatures without checking the migration guide.

## PlatformIO

Use when a project needs a reproducible CLI wrapper around Arduino or ESP-IDF, per-environment board/framework declarations, serial monitoring, unit tests, or debugger integration.

```sh
pio project init --board BOARD_ID
pio run
pio run --target upload --upload-port PORT
pio device monitor --port PORT --baud 115200
pio test
```

Pin `platform = platformio/espressif32@VERSION` once a known-good platform version exists. The board ID selects memory and upload defaults; do not substitute a vaguely similar board without checking its definition. PlatformIO does not erase the behavioral differences between Arduino and ESP-IDF.

## MicroPython

Use for quick interactive development, education, and applications that fit the supported port's memory, timing, and library constraints.

1. Download firmware for the exact board/SoC from MicroPython.
2. Follow that image's documented erase and flash address. Do not reuse an address from another ESP32 family.
3. Use `mpremote` for discovery, REPL, files, execution, reset, and package installation.

```sh
mpremote connect list
mpremote connect PORT repl
mpremote connect PORT run main.py
mpremote connect PORT fs cp main.py :main.py
mpremote connect PORT soft-reset repl
```

MicroPython is not CPython: APIs, keyword support, heap behavior, threading, packages, and filesystem semantics differ. Use `machine.Pin`, `ADC`, `PWM`, `I2C`/`SoftI2C`, `SPI`/`SoftSPI`, `UART`, timers, and sleep APIs from the current port documentation. Validate a driver on-device before integrating it.

## CircuitPython

Use when the exact board is supported and the project benefits from CircuitPython's board aliases, filesystem workflow, and library bundle. Verify the board download page first. Classic ESP32 lacks native USB mass storage, while some S2/S3/C3-class boards expose different USB workflows; do not assume a `CIRCUITPY` drive appears on every target.

Use `board` aliases rather than raw numbers when the board definition provides them, inspect `dir(board)` at the REPL, and install libraries matching the CircuitPython major version. Keep `settings.toml` secrets out of source control. Use the documented serial or web workflow for the exact board.

## ESPHome

Use for declarative devices integrated with Home Assistant or MQTT and covered by ESPHome components. Declare the exact board and framework rather than relying on a stale implicit default.

```sh
esphome config device.yaml
esphome compile device.yaml
esphome upload device.yaml --device PORT_OR_HOST
esphome logs device.yaml --device PORT_OR_HOST
# esphome run combines validation/build/upload/logs
```

Search the official component index before writing a custom lambda or external component. Keep Wi-Fi, API encryption, and OTA values in `secrets.yaml`. Validate, compile, and capture logs; successful YAML validation alone does not prove the generated firmware builds or the hardware works.

## Zephyr

Use when Zephyr's Kconfig, devicetree, RTOS services, portability, or driver model is a product requirement and the target board/peripherals are supported.

```sh
west boards
west build -p=always -b BOARD samples/basic/blinky
west flash
west debug
```

Copy or extend the closest official board definition only after checking its SoC, flash, PSRAM, console, runner, and devicetree. Put hardware description in a board overlay and application behavior in source/Kconfig. A successful build for a board target does not prove a custom board's pin routing or flash layout.

## Rust on ESP

Choose between:

- `no_std` with `esp-hal` for direct hardware control and Rust-native embedded patterns;
- `std` with ESP-IDF integration when ESP-IDF services and its runtime are required.

Use the official Rust on ESP book and `esp-generate`; avoid hand-assembling an obsolete template. `espflash` is the native serial flasher for `esp-hal`-compatible chips:

```sh
cargo install espflash --locked
espflash board-info
espflash flash --monitor target/...
```

Toolchains and chip support move quickly. Pin the Rust toolchain and crate versions, use the generated target configuration, and check the current support table before selecting a chip.

## NuttX

Use for an existing NuttX product, NuttShell, POSIX-like APIs, or a requirement specifically served by NuttX. Official NuttX documentation covers classic ESP32 and several C/S variants with board configurations and `make flash` integration.

```sh
./tools/configure.sh esp32-devkitc:nsh
make -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)"
make flash ESPTOOL_PORT=PORT
```

These commands show the classic NuttX build flow. Check the selected release and board documentation first because current targets may use CMake. Use the exact board configuration and current NuttX instructions. NuttX is supported but intentionally not the default path for a new general ESP32 sensor prototype because its setup and RTOS model add complexity without improving that common case.
