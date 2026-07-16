# Native tool workflows

Use the selected framework's native control plane. A second wrapper is justified only when repeated execution proves a missing safety or portability function.

## Host preparation

1. Install the framework from its current official guide.
2. Record tool versions in the project or issue.
3. Confirm a data-capable cable and stable USB identity.
4. Close monitors and IDEs that hold the port.
5. On Linux, fix serial permissions with the distribution's documented group/udev mechanism rather than routinely running the toolchain as root.
6. Keep one known-good serial recovery path even when normal updates are OTA.

## Read-only and low-impact discovery

```sh
python3 scripts/esp32-preflight.py --json
pio device list --json-output
mpremote connect list
```

After mapping a specific port to the intended board, `esptool --port PORT chip-id` and `flash-id` query the ROM loader but may reset the device and require download mode:

```sh
esptool --port PORT chip-id
esptool --port PORT flash-id
```

Treat them as targeted probes, not harmless enumeration. If the first handshake fails, inspect the failure signature before changing boot state. If a second genuinely different approach also fails, report the evidence instead of escalating through erase, alternate images, or random reset sequences.

## ESP-IDF

```sh
idf.py --version
idf.py set-target TARGET
idf.py menuconfig
idf.py build
idf.py -p PORT flash
idf.py monitor --no-reset -p PORT
# common combined path when reset is acceptable
idf.py -p PORT flash monitor
```

The build emits bootloader, partition table, application images, and exact flash arguments. Preserve `build/flasher_args.json` or the generated command in CI artifacts when another station will flash the image. Use `idf.py erase-flash` only when loss of NVS, calibration, credentials, application data, and all partitions is understood and authorized.

For tests, start with ESP-IDF's supported host or target test mechanisms and official examples. A host unit test does not prove GPIO timing, RF, sleep current, or an attached device.

## esptool

Use `esptool` directly for board identification, vendor firmware images, backup/read operations, and recovery when the firmware project does not own the flash command. Prefer the hyphenated esptool v5 commands shown by current help; older examples may use underscores or `esptool.py`.

```sh
esptool --help
esptool --port PORT chip-id
esptool --port PORT flash-id
esptool --port PORT read-flash 0 ALL backup.bin
esptool --port PORT image-info firmware.bin
esptool --port PORT write-flash OFFSET firmware.bin
```

Never infer `OFFSET` from a different framework or chip. Use the firmware vendor's manifest or the project's generated flash arguments. A write success verifies transfer and flash readback, not application boot or peripheral behavior.

## Arduino CLI and PlatformIO

For a pure Arduino CLI project, use the fully qualified board name selected from `arduino-cli board listall` and the official ESP32 core install instructions. For PlatformIO:

```sh
pio project init --board BOARD_ID
pio run
pio run --target upload --upload-port PORT
pio device monitor --port PORT --baud 115200
pio test
pio run --target clean
```

Use `pio boards espressif32` to find board IDs. Inspect the selected board page and generated build/upload settings. Cleaning is a stale-build diagnostic, not a first response to a wiring failure.

## MicroPython

Use the exact firmware download page's flash instructions. After firmware is running:

```sh
mpremote connect list
mpremote connect PORT repl
mpremote connect PORT fs ls
mpremote connect PORT run probe.py
mpremote connect PORT fs cp main.py :main.py
mpremote connect PORT soft-reset repl
```

`run` is ideal for a non-persistent probe. Copy only after it works. Keep `boot.py` minimal because failures there can make every boot difficult to diagnose. Use `mpremote mip install PACKAGE` only for packages documented as MicroPython-compatible.

## CircuitPython

Download only from the exact board page. After flashing, confirm `CIRCUITPY` and the serial REPL. Use `board` aliases from the running firmware, not ESP32 GPIO assumptions copied from another board. Use the official `circup` CLI to inspect and install libraries from the matching bundle:

```sh
circup show SENSOR_NAME
circup install LIBRARY_NAME
circup list
```

Keep library major versions compatible with the running firmware. `circup` discovers a mounted or Web Workflow device; verify which board it selected before changing libraries when multiple devices are connected.

## ESPHome

```sh
esphome version
esphome config device.yaml
esphome compile device.yaml
esphome upload device.yaml --device PORT
esphome logs device.yaml --device PORT
```

Use serial for initial provisioning and recovery. Use OTA only after API/OTA credentials and network identity are confirmed. `esphome run` is convenient for the normal combined path, but separate commands preserve the failing layer during diagnosis.

## Zephyr

```sh
west boards
west build -p always -b BOARD samples/hello_world
west flash
west debug
```

Use the board page's runner and reset instructions. Some built-in USB Serial/JTAG targets may remain in download mode after flashing; current Zephyr board documentation may prescribe `west flash --reset-type watchdog-reset`. Apply it only to a documented target.

## Rust

Use `esp-generate` to create a current project and the generated Cargo aliases/configuration. For `esp-hal` projects, use `espflash`:

```sh
espflash --help
espflash board-info
cargo build --release
espflash flash --monitor TARGET_BINARY
```

For ESP-IDF-backed Rust, follow the generated project and `cargo-espflash`/ESP-IDF integration documentation. Do not mix `no_std` and `std` setup instructions.

## Verification ladder

1. Build or configuration validation passes.
2. Image metadata matches target chip and intended partition layout.
3. Flash command completes against the confirmed port.
4. Boot log identifies the intended firmware/version.
5. Reset and power-cycle return to normal operation.
6. Peripheral identity and raw behavior pass.
7. Calibrated application behavior passes under realistic power/network/load conditions.
8. Recovery path is exercised when the deployment relies on OTA, encryption, or inaccessible hardware.
