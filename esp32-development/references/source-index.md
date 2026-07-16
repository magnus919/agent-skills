# Source index

Checked 2026-07-15. Prefer stable or versioned pages for implementation. `latest` pages are discovery aids and must be rechecked when a command, default, supported target, or security behavior matters.

## Coverage matrix

| Requested dimension | Primary evidence group | Skill reference | Status |
|---|---|---|---|
| Board, SoC, memory, USB, and port identification | ESP-IDF, esptool, development-board docs, family datasheets | `decisions-and-preflight.md` | Covered; exact board artifacts remain task inputs. |
| Electrical limits, strapping, pins, and power | Family datasheets and hardware design guidelines | `hardware-and-electrical-safety.md` | Covered by procedure; no universal pin table is asserted. |
| ESP-IDF C/C++ | ESP-IDF Programming Guide | `firmware-frameworks.md`, `native-tool-workflows.md` | Covered. |
| Arduino and PlatformIO | Arduino-ESP32 and PlatformIO official docs | `firmware-frameworks.md`, `native-tool-workflows.md` | Covered. |
| MicroPython and CircuitPython | Project docs, downloads, and ESP32 quick start | `firmware-frameworks.md`, `native-tool-workflows.md` | Covered with board-support boundaries. |
| ESPHome | ESPHome CLI, ESP32 platform, and component index | `firmware-frameworks.md`, `native-tool-workflows.md` | Covered. |
| Zephyr | Zephyr getting-started, board, devicetree, and runner docs | `firmware-frameworks.md`, `native-tool-workflows.md` | Covered. |
| Rust on ESP | Official Rust on ESP book, `esp-generate`, and `espflash` | `firmware-frameworks.md`, `native-tool-workflows.md` | Covered; support must be refreshed by chip/toolchain. |
| NuttX and additional firmware | Apache NuttX family pages | `firmware-frameworks.md` | Covered as an intentional secondary path, not the default. |
| GPIO, ADC/DAC, PWM, touch, buses, timers, USB/JTAG | ESP-IDF peripheral catalog plus framework APIs | `peripherals-and-buses.md` | Covered by capability and diagnostic workflow. |
| Sensors, displays, and actuators | Manufacturer datasheets, module schematics, maintained drivers | `sensors-actuators-and-calibration.md` | Covered by reusable component contract; individual parts are task inputs. |
| Wi-Fi, BLE, other radios, sleep, storage, and OTA | ESP-IDF and framework update/network docs | `connectivity-power-and-ota.md` | Covered with family-support checks. |
| Flashing, logs, crashes, recovery, and security | esptool, ESP-IDF monitor/fatal/JTAG/security docs | `debugging-recovery-and-security.md` | Covered, including irreversible-operation boundaries. |
| Validation and physical verification | All framework build/test docs plus hardware boundary checks | `native-tool-workflows.md` | Covered; successful component tests are not promoted to hardware proof. |

## Espressif hardware and ESP-IDF

| Area | Primary source | Scope |
|---|---|---|
| ESP-IDF documentation and version selector | [ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/) | Select the exact SoC family; stable classic ESP32 was v6.0.2 at review. |
| SoC selection | [ESP Product Selector](https://products.espressif.com/#/product-comparison) | Compare current CPU, memory, radio, and peripheral capabilities; verify the resulting chip-specific datasheet. |
| Build, flash, and monitor | [Build the Project](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/start-project.html) | `idf.py build`, generated images/offsets, flash, monitor. |
| `idf.py` | [IDF Frontend](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/tools/idf-py.html) | Native project control plane and command behavior. |
| Serial monitoring | [IDF Monitor](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/tools/idf-monitor.html) | Decoding, reset behavior, `--no-reset`, filtering. |
| Flash failures | [Flashing Troubleshooting](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/flashing-troubleshooting.html) | Port, boot mode, reset wiring, power, and connection failures. |
| Classic ESP32 GPIO | [GPIO and RTC GPIO](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html) | Pin restrictions for classic ESP32 only. Switch URL family for S/C/H/P targets. |
| Peripheral catalog | [Peripherals API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/index.html) | Current ESP-IDF drivers and supported peripherals. |
| ADC | [ADC driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc.html) | Conversion modes, calibration, SoC limitations. |
| Sleep | [Sleep Modes](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/sleep_modes.html) | Power domains and wake behavior. |
| Runtime power | [Power Management](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/power_management.html) | Frequency scaling, automatic light sleep, locks, and profiling. |
| Partitions | [Partition Tables](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/partition-tables.html) | CSV layout, offsets, types, generated tables, erase implications. |
| OTA | [Over-the-Air Updates](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/ota.html) | OTA slots, data, rollback APIs, image validation. |
| HTTPS OTA | [ESP HTTPS OTA](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/esp_https_ota.html) | Certificate verification, partial download, resume, and encrypted-image boundaries. |
| Crashes | [Fatal Errors](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/fatal-errors.html) | Panic, watchdog, brownout, core dump, and backtrace evidence. |
| Postmortem data | [Core Dump](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/core_dump.html) | Capture and decode task/register state against the matching ELF. |
| JTAG | [JTAG Debugging](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/jtag-debugging/index.html) | OpenOCD/GDB, adapters, voltage, and classic ESP32 constraints. |
| Security | [ESP-IDF Security](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/index.html) | Entry point for secure boot, flash encryption, eFuses, signing, and hardening. |
| Hardware design | [ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/) | Family-specific schematic, power, reset, flash/PSRAM, RF, and strapping guidance. |
| Silicon limitations | [ESP Chip Errata](https://docs.espressif.com/projects/esp-chip-errata/en/latest/) | Family/revision-specific defects and workarounds. |
| Classic ESP32 datasheet | [ESP32 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf) | Absolute limits, electrical characteristics, pins, boot configuration. Use matching family datasheet for other SoCs. |
| Board hardware | [Espressif Development Boards](https://docs.espressif.com/projects/esp-dev-kits/en/latest/) | Board-specific guides, schematics, ports, headers, and jumpers. |

## Flashing and C/C++ ecosystems

| Area | Primary source | Scope |
|---|---|---|
| esptool commands | [Basic Commands](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html) | Identification, read/write/erase, image inspection; select exact chip docs. |
| esptool diagnosis | [Troubleshooting](https://docs.espressif.com/projects/esptool/en/latest/esp32/troubleshooting.html) | Connection and flashing failure signatures. |
| Arduino core | [Arduino-ESP32 documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/) | Install, APIs, board pages, migration, OTA, troubleshooting. Version 3.3.10 was documented at review. |
| Arduino APIs | [Arduino-ESP32 Libraries](https://docs.espressif.com/projects/arduino-esp32/en/latest/libraries.html) | GPIO, ADC, I2C, SPI, UART, BLE, USB, networking, and family support. |
| PlatformIO | [Espressif 32 platform](https://docs.platformio.org/en/latest/platforms/espressif32.html) | Board IDs, frameworks, build settings, partitions, filesystems, OTA. |
| PlatformIO CLI | [PlatformIO Core CLI](https://docs.platformio.org/en/latest/core/index.html) | Project, run, upload, device, test, and debug commands. |

## Python firmware and ESPHome

| Area | Primary source | Scope |
|---|---|---|
| MicroPython ESP32 | [ESP32 quick reference](https://docs.micropython.org/en/latest/esp32/quickref.html) | Port-specific networking, pins, ADC/PWM, buses, timers, sleep. v1.28.0 was current at review. |
| MicroPython host tool | [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html) | Discovery, REPL, filesystem, run, mount, reset, packages. |
| MicroPython images | [ESP32 downloads](https://micropython.org/download/?mcu=esp32) | Board/SoC image selection and exact installation instructions. |
| CircuitPython boards | [CircuitPython downloads](https://circuitpython.org/downloads) | Exact supported board, firmware, and install method. |
| CircuitPython on ESP32 | [ESP32 quick start](https://learn.adafruit.com/circuitpython-with-esp32-quick-start) | Serial esptool and web workflow boundaries for ESP32 boards. |
| CircuitPython APIs | [CircuitPython Documentation](https://docs.circuitpython.org/) | `board`, `busio`, `digitalio`, `analogio`, `pwmio`, library compatibility. |
| CircuitPython libraries | [`circup`](https://docs.circuitpython.org/projects/circup/en/latest/) | Discover, install, freeze, and update libraries on mounted or Web Workflow devices. |
| ESPHome CLI | [Command Line ESPHome](https://esphome.io/guides/getting_started_command_line/) | `config`, `compile`, `upload`, `logs`, `run`. |
| ESPHome ESP32 platform | [ESP32 Platform](https://esphome.io/components/esp32/) | Families, boards, framework choice, flash/PSRAM options. |
| ESPHome components | [Component index](https://esphome.io/components/) | Supported sensors, buses, outputs, displays, automations, and exact config. |

## Wireless detail

| Area | Primary source | Use |
|---|---|---|
| Wi-Fi | [ESP-IDF Wi-Fi Driver Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/wifi-driver/index.html) | Initialization, events, modes, reconnect behavior, and chip-specific driver boundaries. |
| BLE with NimBLE | [NimBLE Host APIs](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/bluetooth/nimble/index.html) | Host architecture, initialization, threading, and BLE feature support. |

## Zephyr, Rust, and NuttX

| Area | Primary source | Scope |
|---|---|---|
| Zephyr setup | [Getting Started](https://docs.zephyrproject.org/latest/develop/getting_started/index.html) | `west`, SDK, build, flash, and board discovery. Latest was 4.4.0 at review. |
| Zephyr ESP32 board | [ESP32-DevKitC](https://docs.zephyrproject.org/latest/boards/espressif/esp32_devkitc/doc/index.html) | Board target, supported features, flash/debug and reset details. Use exact board page. |
| Zephyr hardware model | [Devicetree](https://docs.zephyrproject.org/latest/build/dts/index.html) | Board overlays, bindings, aliases, and generated hardware description. |
| Zephyr flash/debug | [Flash and Debug](https://docs.zephyrproject.org/latest/develop/flash_debug/index.html) | West runners, host tools, debug probes. |
| Zephyr on Espressif status | [Espressif Zephyr Support Status](https://developer.espressif.com/software/zephyr-support-status/) | Current chip/peripheral support and known gaps; check before committing to Zephyr. |
| Rust on ESP | [The Rust on ESP Book](https://docs.espressif.com/projects/rust/book/) | Official environment, architecture choice, generation, build, flash, and debugging. |
| Rust generator | [`esp-generate`](https://docs.espressif.com/projects/rust/book/getting-started/tooling/esp-generate.html) | Current generator installation, project layouts, and options. |
| Rust flasher | [`espflash`](https://docs.espressif.com/projects/rust/book/getting-started/tooling/espflash.html) | Installation, supported chips, flashing, serial monitor. |
| NuttX classic ESP32 | [Espressif ESP32](https://nuttx.apache.org/docs/latest/platforms/xtensa/esp32/index.html) | Board configs, build/flash, JTAG, wireless, crash decoding. |
| NuttX ESP32-C3 | [Espressif ESP32-C3](https://nuttx.apache.org/docs/latest/platforms/risc-v/esp32c3/index.html) | RISC-V C3-specific board and build support. |
| NuttX ESP32-S3 | [Espressif ESP32-S3](https://nuttx.apache.org/docs/latest/platforms/xtensa/esp32s3/index.html) | S3-specific board and build support. |

## Component sources

For every attached device, prefer:

1. component manufacturer's current datasheet and errata;
2. breakout/module vendor schematic and pinout;
3. framework-maintained component/driver documentation;
4. vendor-maintained driver source and examples;
5. independent tutorials only as clearly labeled practice evidence.

Record URLs, document revisions, access date, exact claims used, and gaps in `templates/component-contract.md`.

## Refresh rules

Recheck sources when changing ESP-IDF major/minor version, Arduino core major version, ESPHome release train, MicroPython/CircuitPython major version, Zephyr release, Rust toolchain/HAL generation, NuttX release, SoC family/revision, bootloader/partition/security state, board revision, or attached component revision. Always recheck irreversible security commands and flash offsets immediately before execution.
