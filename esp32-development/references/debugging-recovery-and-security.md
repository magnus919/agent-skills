# Debugging, recovery, and security

Diagnose from the lowest unproven layer. Do not rewrite application code while power, boot mode, port ownership, or bus electrical state remains unknown.

## Failure ladder

1. **Host/tool:** command exists, expected version/environment active, permissions correct.
2. **USB/serial:** data-capable cable, stable USB identity, correct port, no competing process.
3. **Power/reset/boot:** rails stable, EN/reset and BOOT/strapping levels correct, boot log captured.
4. **ROM loader/flash:** targeted `chip-id`, image target/layout, transfer, verification.
5. **Bootloader/partition:** valid image headers, selected slot, partition table, security state.
6. **Runtime:** crash reason, watchdog, heap/stack, task state, exception/backtrace.
7. **Peripheral:** pin routing, voltage, pulls, bus waveform, address/identity, driver sequence.
8. **Network/service:** radio state, IP, DNS/time/TLS, endpoint, auth, application protocol.
9. **Physical behavior:** calibration, load, thermal, EMI, mechanical/environmental constraints.

## Flash and connection failures

Capture the complete native-tool error. Common categories:

- `No serial data received`: wrong/non-ESP port, target not in download mode, reset wiring, cable, permissions, port owner, native-USB state, or power.
- Invalid packet/header or intermittent transfer: marginal power, signal/cable, excessive baud, USB hub, competing access, or boot-mode instability.
- Wrong chip argument/image: stop and obtain the exact target artifact; do not force it.
- Write succeeds but no boot: capture boot log; inspect reset loop, image target, flash mode/frequency/size, offsets, partition table, boot slot, and security state.

Try a lower baud only after the basic target/port/power checks. Manual BOOT/RESET sequencing is board-specific. Use the board guide instead of random button timing.

## Boot loops and crashes

Preserve the first complete boot log after power-on. Note reset reason, boot mode, image/partition choice, exception, program counter, and backtrace.

ESP-IDF Monitor can decode addresses against the matching ELF. A backtrace from another build is not evidence. Keep the ELF, map, `sdkconfig`, commit, and toolchain version for a released image.

Common classes:

- brownout: measure supply at the board during peaks;
- watchdog: find the blocked/starved task or interrupt path; do not merely extend the timeout;
- stack overflow: inspect task stack sizing and call depth;
- heap failure/fragmentation: capture free/largest-block metrics and allocation lifetime;
- illegal access/panic: decode against the exact ELF and inspect ownership/lifetime/concurrency;
- reset caused by serial DTR/RTS: reproduce with monitor `--no-reset` or equivalent;
- crash only with peripheral attached: isolate power, pin conflict, bus lock, interrupt storm, and driver sequence.

## Bus diagnosis

### I2C

Measure SDA/SCL idle high, effective pull-ups, and voltage. Scan at conservative speed, then inspect start/address/ACK with a logic analyzer. A device that ACKs but returns bad data points to register, timing, mode, endian, readiness, or signal-integrity issues.

### SPI

Inspect CS, clock, MOSI, and MISO together. Verify mode and transaction boundaries. Floating MISO, wrong CS polarity, and a reset pin left asserted can resemble a software driver failure.

### UART

Loop back the ESP32 UART, then loop back or independently test the peripheral. Verify voltage standard and framing. Capture bytes rather than relying on rendered text.

## Recovery order

Use the least destructive rung that can restore observability:

1. close port owners and capture logs with no-reset behavior;
2. reset/power-cycle using the documented board path;
3. enter documented ROM download or bootloader mode;
4. query chip/flash identity;
5. reflash the known-good build with generated/authoritative offsets;
6. reflash bootloader/partition/application set when the framework requires it;
7. erase only the specific corrupt data partition when supported and authorized;
8. full-chip erase only after backup/impact review and explicit authorization;
9. hardware debugger or board-level repair.

Before erase, preserve readable flash or at least record partition layout, MAC/identity, security state, calibration implications, credentials/data impact, and the known-good recovery artifact. Do not read or publish secret-bearing flash without authorization.

## JTAG and debugger use

Use an ESP32-compatible OpenOCD configuration and voltage-compatible adapter. The exact JTAG pins and built-in USB JTAG support vary by family. Confirm pin conflicts and production security state. A debugger can change timing; reproduce without it before concluding the race is fixed.

## Security provisioning

Secure boot, flash encryption, eFuses, JTAG/download-mode controls, signing keys, and anti-rollback are product lifecycle decisions. Some transitions are irreversible.

Before provisioning:

1. identify exact SoC revision and supported security scheme;
2. read the matching stable ESP-IDF security pages and eFuse documentation;
3. define development, manufacturing, RMA, field-update, and decommission paths;
4. protect signing/encryption keys outside source and build logs;
5. verify image signing and encrypted-flash behavior on disposable hardware;
6. verify OTA, rollback/anti-rollback, serial recovery restrictions, and RMA path;
7. record non-secret provisioning evidence without publishing key material.

Do not copy eFuse commands from a generic guide. Do not enable flash encryption or secure boot merely to satisfy a checklist. The correct state depends on the threat model and a proven update/recovery lifecycle.

## Bounded escalation

After two genuinely different approaches fail at the same layer, stop and report:

- exact board/SoC and evidence;
- wiring/power state;
- tool versions and commands;
- complete errors/logs;
- what each attempt proved or disproved;
- the next action and its risk.

A third blind reset, framework switch, erase, or guessed image adds risk faster than information.
