# ESP-Mosaico kit: first use and development

Checked 2026-10-29 against the official sources below; no physical kit was available for bench verification. Read this for ESP-Mosaico tasks, then verify the delivered PCB markings, selected firmware revision and current upstream instructions before hardware operations. Mainboard and camera PCB version numbers are independent. Do not substitute ESP32-S3 pin maps or firmware.

## Identify the hardware

The [CoreBoard V1.2 hardware guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp-mosaico/user_guide.html) specifies:

| Resource | Specification / useful starting point |
|---|---|
| Processor | ESP32-S31NRV16: dual-core 32-bit RISC-V, up to 320 MHz |
| Memory | 16 MB PSRAM; 16 MB SPI NOR for firmware/data; separate 128 MB SPI NAND for assets |
| Display | 2.16-inch, 480 × 480 QSPI touch display, CO5300 driver |
| Audio | ES8311 codec, onboard microphone, NS4150B amplifier and speaker |
| Sensors | BMI270 IMU; two BMM150 magnetometers; BQ27220 battery gauge |
| Feedback/input | Vibration GPIO8 active-high; AI button GPIO7 active-low |
| Radio hardware | 2.4 GHz Wi-Fi 6; Bluetooth 5.4 LE and BR/EDR; IEEE 802.15.4 |
| Power | USB-C 5 V or onboard 3.7 V / 65 mAh battery |

Use USB power for development. Radio hardware capability does not establish firmware profile availability. The hardware guide names CST9220-series touch while the BSP README names CST9217: inspect the delivered board and selected driver instead of silently resolving that disagreement. Use revision-aware BSP initialization rather than transplanting raw GPIO setup.

## Unpack, inspect, and establish a baseline

1. Inventory the actual order: core, camera, interaction board, cable and any separately ordered accessories. Do not assume every retailer bundle contains every expansion module. The [FAQ](https://mosaico.ai/en/faq) identifies the current camera as a separate SC101IOT module; the interaction board has no enclosure.
2. Photograph PCB revisions and connector orientation; inspect for bent pins. Connect a known data-capable cable, power on, and record factory firmware identity before replacing anything.
3. Exercise the factory screen/touch and installed apps first. Keep a recovery source and record settings/data that reflashing could replace.
4. For [Chat Coding setup](https://mosaico.ai/en/guide), open Mosaico-Claw, configure Wi-Fi and the supported IM/ASR/LLM services. In Settings → AI Model, use the displayed IP on the same LAN for configuration; restart after changing control-panel settings. Factory model quota is finite; provider usage can incur charges. Store credentials outside source control.
5. For desktop coding, start from the official Vibe workspace below. Prototype and build before installing, then verify the app identity and actual device behavior.

FAQ battery figures are test conditions, not promises: approximately 15 minutes display-only, 10 with display/Wi-Fi, 5 with display/Wi-Fi/camera. Measure the intended workload. Its optional back-mount battery is approximately 1000 mAh: rear contacts on core v1.2, USB connection on v1.0.

## Included expansion components

### Camera

Follow the [camera hardware guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp-mosaico/user_guide_camera.html). Power off before installation; align the header in **left H2 only**, orange lens up, flash LEDs down. Camera PCB v1.2 uses OV3640, default 1024 × 768 UYVY; camera PCB v1.4 uses SC101IOT, default 1280 × 720 UYVY. SC101IOT lens variants have different optics; identify yours before choosing focus/FOV assumptions.

The FAQ permits camera hot insertion but **not hot removal**. Power off before removing it; if inserted on the right, power off and move it left. A generic “hot-pluggable slots” statement is not permission to remove a streaming camera.

Camera use claims GPIO33/34, disabling left-header USB Serial/JTAG; the Type-C USB-OTG console remains available. GPIO34 flash control is active-low and requires open-drain output. EEPROM access to the left slot is suspended while camera DVP owns GPIO14. Prefer the module driver over manual pin control.

Start with BSP `examples/camera_lcd_preview`, then `camera_photo_app`. Diagnose capture separately from LCD rendering and storage.

The [camera driver contract](https://github.com/esp-mosaico/esp-mosaico-bsp/blob/7cbfb390638dcb93522fc3cde094b2d43cf907c2/components/mosaico_module_camera/README.md) requires returning borrowed frames before stopping, closing, restarting or deleting capture. Before software reset, wait for PPA/LCD DMA completion and release capture resources; a DMA timeout does not cancel the transfer. Do not free a buffer still being consumed. Its CMake integration can patch the ESP-IDF checkout; inspect that change and patch warnings before relying on SC101IOT workarounds. Use a dedicated writable toolchain checkout.

### Multifunction Interaction Board

The [interaction hardware guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp-mosaico/user_guide_interact.html) describes GL5506 ambient light, AS312 PIR, NEC 38 kHz IR transmit, six WS2812 RGB LEDs, and two key/touch pads. Either slot is supported; rotate 180° for the right. Insert with power off or external rails disabled.

| Signal | Left H2 GPIO | Right H1 GPIO |
|---|---|---|
| PIR | 4 | 5 |
| LDR | 53 | 46 |
| IR transmit | 48 | 47 |
| Key/touch L; R | 13; 12 | 11; 10 |
| WS2812 data | 15 | 38 |
| EEPROM SDA; SCL | 0; 1 | 0; 1 |

Module discovery expects AT24C02 identity type `0x16`, address `0x50` left or `0x51` right. GPIO60 low enables external rails; use BSP power APIs. Keys are active-low and share touch pads. LDR percentage is relative brightness, not calibrated lux; PIR reports motion, not proof of continuous occupancy. IR hardware transmits; do not promise an IR receiver.

Start with [interaction_board_demo](https://github.com/esp-mosaico/esp-mosaico-bsp/tree/7cbfb390638dcb93522fc3cde094b2d43cf907c2/examples/interaction_board_demo): observe each input before adding automation, limit LED brightness, and check behavior in the selected slot. The demo supports interaction-board removal/reconnection; do not transfer that behavior to the camera. Motion-triggered screen wake and sleep timing are application policies, not properties of the PIR hardware.

## Power and shared-resource limits

The [product guide expansion I/O table](https://mosaico.ai/en/guide#hardware-development) rates exposed `5V` and `3V` outputs at up to 100 mA each. `IN` is a 5 V input. Do not use those rails for a servo/motor or infer a connector's rating from the USB port. Use an appropriate external supply/driver and confirm common reference and backfeed prevention from the schematic. CODEC pins are available as GPIO only with the internal ES8311 disabled.

The [BSP](https://github.com/esp-mosaico/esp-mosaico-bsp/tree/7cbfb390638dcb93522fc3cde094b2d43cf907c2) manages shared buses and exclusive slot claims. Use its module manager instead of opening duplicate drivers. Check initialization errors: revision discovery reads eFuse USER_DATA and rejects unsupported/unprogrammed revisions; do not “fix” that by writing eFuses. Start with `audio_loopback`, `imu_gesture`, or `hmi_demo` for the corresponding onboard component. Do not assume the v1.0 status LED exists on v1.2.

## Choose the software path

- **Desktop agent / native app:** use [esp-mosaico-vibe](https://github.com/esp-mosaico/esp-mosaico-vibe/tree/1872fd88c01d7807556d01fd2a19864e40a307c9). Read its `AGENTS.md` and relevant skills; initialize pinned dependencies, inspect CLI help, and use the product CLI for device operations. That snapshot requires Python 3.10+, Git 2.28+, and pins ESP-IDF master `7b9cc1ac79f865983f59bb8ff3ff43eb74ff1dbe`. Do not replace the pinned toolchain with an arbitrary stable release.
- **BSP C/C++:** follow the selected example README. The standalone BSP advertises ESP-IDF 6.2+ and may require `idf.py --preview set-target esp32s31`; select the exact toolchain supported by your checkout. This differs from the Vibe workspace pin.
- **Onboard Chat Coding:** ESP-Claw runs its runtime on the device and calls an external LLM service. A self-hosted server needs a supported API, reachable URL, model and credentials. ASR providers need their own integrations; changing an LLM-compatible endpoint does not implement speech recognition. See the FAQ and [ESP-Claw source](https://github.com/espressif/esp-claw). Do not claim frontier model inference runs on the kit.

The Vibe README's host-only starter (run inside its checkout) is:

```sh
git submodule update --init submodule/esp-mosaico-utils
python3 mosaico.py project init my_app
```

Creation writes `projects/my_app` as an independent Git project and does not require hardware or ESP-IDF. Use `--dry-run` first if inspecting the proposed layout. Follow that revision's simulator/build instructions; physical validation remains necessary for sensors, RF, sound and power.

Give the coding agent the API reference and a working starter/network example. Require existing APIs rather than invented calls. Iterate from simulator observations, device screenshots and logs; keep build success separate from physical success. The [Creator Magic demonstration](https://www.youtube.com/watch?v=zKLuih_9yIk) illustrates that loop, but its boot trouble and motion/sleep settings are version-specific observations, not universal requirements.

## Modes, recovery, and troubleshooting

Follow the selected workspace's [device-modes contract](https://github.com/esp-mosaico/esp-mosaico-vibe/blob/1872fd88c01d7807556d01fd2a19864e40a307c9/docs/device-modes.md):

| State | Entry / purpose |
|---|---|
| Normal app | Runs selected app; ESP-Iris is available only if integrated and started |
| Vibe Mode | Power off, hold **AI**, power on; release after Vibe starts. Retained firmware installs/manages apps |
| ROM download | Power off, hold **BOOT** left of USB-C, power on holding it. Low-level download, no ESP-Iris; black screen is expected |

A reboot can return to the selected custom app. Entering Vibe Mode is not a factory erase. `recover` writes base firmware; use it only after recording target, data impact and recovery need. App-only update requires matching complete partitions/resources; first provisioning and system updates are different operations. Download Ideas and a six-digit app code do not enter ROM download mode.

| Symptom | Next useful check |
|---|---|
| No port | Check power, data cable and USB enumeration, then target mode; do not infer corrupt firmware from a failed handshake |
| Flashing fails | Confirm selected target/port; use manual BOOT sequence when the chosen recovery workflow requests it |
| No Type-C logs | Native ROM USB lacks normal app logs; factory CDC/BSP USB-console support depends on firmware. For ESP-Claw logs, FAQ directs users to right-header UART TX/RX with an appropriate adapter |
| Module absent | Check orientation, rail enable, slot, EEPROM descriptor and ownership before rewriting a driver or EEPROM |
| Camera fails after restart | Check frame/DMA shutdown, supported sensor resolution and IDF patch warnings |
| Factory app missing | Use Vibe app management and the official Mosaico-Claw installation instructions; do not erase everything |

Before redistributing firmware/assets, inspect each dependency's license and bundled asset terms at the selected revision. ESP-Claw's Apache-2.0 license does not grant blanket rights over every kit firmware, model, game or service. Keep private settings and provider keys out of screenshots and public artifacts.

## Evidence to return

Record PCB revisions, source/toolchain commits, selected app, port/mode, build output and actual observations for touch, camera, interaction inputs, sound and power as applicable. Without hardware, report documentation review, project creation or simulator results explicitly and leave physical acceptance pending. Never report a successful flash, measured runtime or safe hot removal from compilation alone.
