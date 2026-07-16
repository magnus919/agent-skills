# Peripherals and buses

The GPIO matrix makes many signals routable, but not every pin is safe, exposed, fast enough, or available on every ESP32 family. Select pins from the exact SoC and board documentation.

## GPIO

Bring up a digital signal with explicit direction, initial state, pull configuration, active polarity, and reset-time safety. For outputs attached to a driver, set the inactive level before enabling the driver. For interrupts, log edge counts and timestamps before performing work in callbacks/ISRs.

Verify:

- input-only and output-capable pins;
- internal pull availability;
- strapping and boot state;
- onboard LED/button polarity and shared hardware;
- interrupt trigger and debounce;
- sleep retention and wake capability.

## ADC

Treat ADC conversion as a measurement chain:

`physical quantity → sensor transfer function → source impedance/filter → pin voltage → attenuation/range → raw code → calibration → engineering unit`

1. Prove the pin is an ADC channel on this SoC and board.
2. Keep input within documented range under normal and fault conditions.
3. Use a source impedance compatible with the ADC and sampling mode.
4. Select attenuation/range deliberately.
5. Read raw and calibrated voltage where the framework supports it.
6. Characterize offset, gain, noise, and nonlinearity against known references.
7. Record sample rate, averaging/filtering, and radio state.

Classic ESP32 ADC2 contention with Wi-Fi is a family/API-specific concern. Check the current driver documentation rather than applying that rule universally.

## DAC, PWM, RMT, MCPWM, and pulse counting

Hardware DAC availability varies and is absent on several ESP32 variants. When no DAC exists, PWM plus filtering may be sufficient only if ripple, bandwidth, and load requirements allow it.

For PWM, record frequency, resolution, duty range, timer/channel allocation, polarity, and load driver. LEDC resources and APIs vary by SoC and framework. Servos and motors need external power stages; PWM timing does not make a GPIO power-capable.

Use RMT for precisely timed pulse protocols and carrier generation, MCPWM for motor/power-control timing, and PCNT for hardware edge counting when those peripherals are present. Verify channel/resource conflicts with cameras, audio, or other framework components.

## I2C

Electrical gate:

- SDA/SCL voltage and open-drain behavior are compatible;
- effective pull-up resistance and bus capacitance are reasonable;
- address straps and voltage rails are correct;
- wires are short and grounded appropriately;
- no device holds a line low.

Bring-up:

1. Start at 100 kHz or the device's conservative documented rate.
2. Run a scan as an electrical/address clue, not proof of device identity.
3. Compare the observed 7-bit address with datasheet straps. Watch for 8-bit address notation in datasheets.
4. Read a manufacturer/device/revision register.
5. Perform reset, configuration, readiness polling, and measurement in datasheet order.
6. Check repeated-start, clock stretching, timeout, and endian requirements.

A missing scan address points first to power, ground, pin selection, pull-ups, address, and line state. A found address can still be the wrong device or a bus ghost.

## SPI

Record controller, clock pin, MOSI/MISO direction, chip select, mode (CPOL/CPHA), bit order, word length, maximum clock, and transaction framing. Start slowly and inspect with a logic analyzer when identity reads fail.

Each device normally gets a separate chip select. Ensure inactive CS levels during reset. Some displays, SD cards, radios, and touch controllers share a bus but require different modes/frequencies; drivers must delimit transactions correctly.

## UART

Record voltage standard, TX/RX pins, baud, data bits, parity, stop bits, flow control, message framing, and whether the port is shared with boot logs or flashing. Cross TX/RX for TTL UART. Do not connect RS-232 levels directly. RS-485 requires a transceiver and direction/termination design.

Use loopback before blaming a peripheral. Capture raw bytes and timestamps. Decode the protocol only after physical framing is stable.

## I2S, audio, camera, LCD, and SD

These interfaces consume multiple pins, DMA, clocks, memory, and bandwidth. Start from a framework example for the exact board or peripheral. Verify:

- clock source and expected frequencies;
- pin matrix and fixed-function restrictions;
- DMA-capable buffers and memory placement;
- PSRAM requirements and limitations;
- bus sharing/resource conflicts;
- signal integrity and connector length.

## TWAI/CAN

ESP32 TWAI is the controller interface where supported; it still needs an external CAN transceiver. Match bus voltage, common-mode range, bit timing, termination at physical ends, topology, and isolation needs. Do not describe TWAI as a complete CAN physical interface.

## USB and JTAG

USB device/host/OTG and built-in USB Serial/JTAG support vary by family and board routing. Verify which connector reaches which controller. JTAG uses 3.3 V-level signals on classic ESP32 and requires an ESP32-compatible OpenOCD adapter/configuration; classic ESP32 does not use SWD. Production security configuration may disable or restrict debugging.

## Driver selection

Use this order:

1. framework-maintained driver/component for the exact device;
2. component vendor's maintained driver that supports the selected framework;
3. small local driver implementing only required datasheet operations;
4. custom framework component only when integration/lifecycle requires it.

Before adopting a library, inspect supported chip families, bus API, license, release activity, examples, error handling, calibration support, and open issues. A matching part number in a package name is not compatibility evidence.
