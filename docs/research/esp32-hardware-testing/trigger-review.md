# Description boundary review

2026-10-11. Author inspection of metadata routing, not a measured activation run. These probes are separate from the portable output-quality eval manifest.

| Probe | Expected route | Description evidence |
|---|---|---|
| Automate ESP32 hardware tests with a Pi, including MQTT outages. | esp32-development | Hardware tests and fault injection are explicit. |
| Commission a shared ESP32-C3 bench before repeatedly flashing it. | esp32-development | ESP32 family, flashing and testing are explicit; entrypoint routes to commissioning. |
| My ESP32 meter passes parser tests but loses data after reboot; design acceptance tests. | esp32-development | Firmware testing/debug/recovery and peripheral integration are claimed. |
| Build a TCP fault-injection suite for a web service with no embedded target. | General test/tool discipline, not esp32-development | No ESP32 target; the positive trigger is ESP32-family firmware. |
| Certify the RF/antenna layout of an ESP32 PCB from this skill alone. | Qualified RF/electrical discipline; skill may supply context only | Exact artifacts are required; When not to use excludes RF/antenna certification. |
