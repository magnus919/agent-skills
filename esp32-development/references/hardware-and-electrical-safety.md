# Hardware and electrical safety

Read this before assigning pins, attaching a module, or driving a load. The exact board schematic, module datasheet, SoC datasheet, and attached-device datasheet override generic examples.

## Power first

Record these values before connecting anything:

- board input path: USB, `5V`/`VIN`, regulated `3V3`, battery input, or another rail;
- logic voltage and absolute maximum pin voltage;
- regulator continuous and transient current, including radio bursts;
- attached-device voltage, idle current, peak current, startup/inrush, and sleep current;
- whether two separately powered circuits share ground or require isolation;
- required decoupling, bulk capacitance, and power sequencing.

ESP32 GPIO is generally 3.3 V logic and must not be treated as 5 V tolerant. A `5V` board pin is usually a supply rail, not a 5 V GPIO permission. Use a suitable level shifter, divider, buffer, transistor, MOSFET, or isolated interface based on signal direction, speed, topology, and voltage.

A stable USB idle state does not prove the supply can handle Wi-Fi transmission, a display backlight, a radio PA, or an actuator startup. Brownout resets are power evidence. Fix the supply path instead of disabling the detector.

## Pin-selection gate

For every selected pin, check all of the following against the exact target:

1. Exposed on this board and not consumed by flash, PSRAM, antenna switching, Ethernet, camera, display, USB, or onboard peripherals.
2. Input/output capability matches the use. Some classic ESP32 GPIOs are input-only.
3. Not a boot-strapping pin, or its external pull/network preserves the required reset level.
4. Does not conflict with UART logging, USB Serial/JTAG, JTAG, or the intended recovery path.
5. Supports the requested analog, RTC, touch, wake, or peripheral function on this SoC.
6. Reset-time state is safe for the attached circuit. A pin can float or pulse before application initialization.
7. External pull-ups/pull-downs do not fight onboard components or exceed current limits.

Classic ESP32 examples such as GPIO0/2/5/12/15 strapping behavior, GPIO6–11 flash use, GPIO34–39 input-only behavior, and ADC2/Wi-Fi contention are not universal family rules. Treat them as prompts to inspect the matching family documentation, not as a portable pin table.

## Inputs

- Never leave a safety-relevant digital input floating. Use an internal or external pull as supported by the exact pin and required impedance.
- Debounce mechanical contacts in hardware, software, or both. Record the chosen interval instead of burying it in a magic number.
- Protect long wires and exposed connectors against ESD, transients, and induced noise.
- Scale analog inputs so the maximum possible voltage remains within the documented ADC range, including fault conditions.
- ADC readings vary with attenuation, calibration data, reference behavior, source impedance, noise, and radio activity. Average only after fixing wiring and range problems.

## Outputs and loads

A GPIO is a control signal, not a power supply.

| Load | Minimum external stage |
|---|---|
| Indicator LED | Series resistor sized for LED voltage and safe GPIO current |
| Logic input at another voltage | Appropriate unidirectional or bidirectional level translation |
| Relay/solenoid | Transistor or MOSFET driver, rated supply, flyback protection for DC coils |
| DC motor/pump | Motor driver or MOSFET stage, flyback/current handling, separate power budget |
| Servo | External supply sized for stall current; common reference when not isolated |
| High-current LED/strip | Constant-current or rated switching driver; power injection as required |
| AC/mains load | Certified isolated interface and qualified electrical design; do not prototype directly from GPIO |

Check whether a module marketed as a "relay board" or "motor driver" accepts 3.3 V logic. Optocouplers and input LEDs can still require more current or voltage than an ESP32 pin safely supplies.

## Bus electrical checks

- I2C needs pull-ups to the correct logic rail. Count onboard pull-ups in parallel and calculate the effective resistance.
- SPI needs a shared reference, correct voltage, dedicated chip selects, and signal integrity appropriate to wire length and clock rate.
- UART requires crossed TX/RX, common reference unless isolated, matching voltage levels, baud, data bits, parity, stop bits, and flow control.
- RS-232 is not TTL UART. RS-485 and CAN/TWAI need transceivers and topology-appropriate termination/biasing.
- I2S, camera, LCD, SD, Ethernet, and high-speed SPI wiring become board-layout problems quickly. Reduce speed only as a diagnostic, not as proof the physical design is sound.

## Hardware bring-up

1. Inspect for shorts and confirm supply polarity with power removed.
2. Power the ESP32 alone; measure rails and capture boot current/serial output.
3. Add the attached device's power only; verify rail stability and temperature.
4. Add ground/reference and one signal group at a time.
5. Verify idle voltage with a meter or oscilloscope before enabling outputs.
6. Use a bus scanner or loopback at conservative speed.
7. Read a stable identity/status register before trusting measurements.
8. Add the real load last and test worst-case startup, radio transmit, reset, and actuator conditions.

Use `templates/hardware-bringup.md` to keep these decisions reviewable.
