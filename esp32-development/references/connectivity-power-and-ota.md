# Connectivity, power, and OTA

## Radio and protocol selection

Verify radio support on the exact SoC. The ESP32 family does not share one wireless feature set.

| Need | Candidate | Boundary |
|---|---|---|
| IP networking through an access point | Wi-Fi station | Provisioning, credential protection, reconnect, DHCP/DNS/TLS, and power behavior remain application concerns. |
| Device-hosted setup or local UI | Wi-Fi AP/captive portal | An AP is not authentication or Internet access. Define timeout and recovery. |
| Nearby phone/device interaction | BLE | Services, permissions, bonding, privacy, MTU, reconnect, and coexistence require design. |
| Espressif peer communication | ESP-NOW | Verify family/channel/security constraints and coexistence with infrastructure Wi-Fi. |
| 802.15.4 mesh | Zigbee or Thread on supported C/H variants | Requires the correct radio-capable SoC and ecosystem stack; not classic ESP32 functionality. |
| Wired network | Ethernet MAC or SPI Ethernet device where supported | PHY/transceiver, clocks, magnetics, board routing, and driver support are separate. |

Use official framework examples for first association/advertising. Log state transitions and reason codes rather than reducing connectivity to a Boolean.

## Network bring-up

1. Prove radio initialization with no application services.
2. Join or advertise using temporary development credentials kept outside source control.
3. Record IP/address, RSSI, channel, negotiated parameters, and disconnect reason.
4. Verify DNS, time synchronization, and route before debugging TLS or application protocols.
5. Bound retries with backoff and expose a local recovery/provisioning path.
6. Test AP loss, wrong credentials, DHCP/DNS failure, weak signal, server unavailability, and reboot.
7. Measure current and timing during reconnect storms.

For TLS, provision trust anchors and time correctly. Do not disable certificate verification as a production fix. Store secrets using the framework's supported provisioning/storage controls and model physical access honestly.

## Low-power design

Start with a current budget by state:

| State | Duration/frequency | Expected consumers |
|---|---|---|
| Deep sleep | longest period | RTC domain, wake circuit, regulator quiescent current, attached-device leakage |
| Wake/startup | each cycle | oscillator, bootloader, flash/PSRAM, sensor warm-up |
| Radio connect | variable | Wi-Fi/BLE peak current, retries, DNS/time/TLS |
| Measure/actuate | application-specific | sensors, buses, displays, drivers, loads |
| Persist/update | occasional | flash writes, OTA download/verification |

Use a meter capable of capturing both sleep leakage and radio peaks. Development-board USB bridges, LEDs, regulators, level shifters, and sensors can dominate deep-sleep current; measuring the SoC in isolation is not measuring the product.

Select wake sources supported by the exact SoC and pin. Verify wake polarity and pull state through sleep. After wake, inspect the wake cause and reinitialize peripherals deliberately. Test timer and external wake separately before combining them.

## Flash persistence

Frequent writes wear flash and increase energy use. Batch state, use framework-supported wear leveling/NVS/filesystems, and define which data may be lost on reset. Power failure can occur during a write: use atomic update patterns and recovery checks appropriate to the storage layer.

Do not put high-frequency telemetry logging on internal flash without a retention and wear model.

## OTA design

OTA is a system, not an upload command. Define:

- artifact identity, target chip/board, version, and compatibility metadata;
- signed/authenticated transport and image verification;
- partition sizes and at least one known-good bootable image where rollback is required;
- download resume or bounded retry behavior;
- health/confirmation criterion after boot;
- rollback policy and boot-attempt limit;
- serial/JTAG/manual recovery path;
- preservation or migration of NVS, filesystem, calibration, and user data;
- staged rollout and observability.

### ESP-IDF

Use the current OTA APIs and partition-table documentation. Rollback requires appropriate OTA partitions, bootloader/app configuration, and application confirmation. Test an intentionally bad or unconfirmed image on disposable hardware.

### Arduino and PlatformIO

ArduinoOTA or web-update examples add a transport path; they do not automatically create a production trust, compatibility, or rollback design. PlatformIO's OTA uploader requires firmware support and the correct upload protocol/host.

### ESPHome

Keep the serial recovery path and OTA credentials. Validate and compile before upload. Version/framework changes can alter generated partitions and dependencies; read release notes before fleet updates.

### Other frameworks

Use Zephyr's documented MCUboot/update path or the Rust/NuttX project's supported boot/update stack. CircuitPython has no generic native OTA path on ESP32; use the exact board's documented firmware and code update workflow. Do not transplant ESP-IDF partition assumptions into another bootloader.

## Power and update verification

- measure sleep current at the product boundary;
- test wake after the maximum intended sleep duration;
- test low battery or marginal supply during radio transmit and flash write;
- interrupt power during a disposable-device update at multiple stages;
- verify the device either boots a valid prior image or enters a documented recovery state;
- confirm calibration and user data behavior across update and rollback.
