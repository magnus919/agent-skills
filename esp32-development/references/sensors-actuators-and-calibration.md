# Sensors, actuators, and calibration

Do not try to memorize every breakout board. Use a repeatable component contract grounded in the exact component and board artifacts.

## Component contract

Fill `templates/component-contract.md` from primary sources:

- manufacturer and exact part/revision;
- breakout/module vendor and schematic, if not a bare component;
- supply and logic voltage ranges;
- typical and worst-case current, startup time, and power modes;
- interface, address/chip-select straps, register map, command timing, and reset behavior;
- measurement range, resolution, accuracy, repeatability, drift, warm-up, and calibration;
- actuator load voltage/current, stall/inrush, switching frequency, and protection;
- environmental and mechanical constraints;
- known identity register or observable self-test;
- safe inactive state and recovery procedure.

A breakout can add regulators, pull-ups, level shifters, address jumpers, LEDs, or transistors that materially change the bare component's behavior. Read both artifacts.

## Sensor bring-up

1. Measure the supply at the sensor while powered.
2. Verify idle bus levels and address/CS straps.
3. Run a bus scan or electrical loopback.
4. Read device/revision identity.
5. Issue documented reset and wait the required startup time.
6. Configure one conservative mode.
7. Capture raw registers/values before unit conversion or filters.
8. Compare against a known reference at multiple points.
9. Add compensation, calibration, rejection, and filtering separately.
10. Repeat across reset, power-cycle, network activity, and expected environment.

For interrupt-driven sensors, first poll status and log it. Add interrupt routing only after the status/clear sequence is understood. A stuck interrupt is often a missed clear/read requirement, wrong polarity, open-drain pull-up problem, or reset-state conflict.

## Calibration is part of the interface

Keep calibration values visible and replaceable. Record units and provenance. Common forms:

```text
corrected = (raw - offset) * scale
value = interpolate(raw, calibration_points)
filtered[n] = filtered[n-1] + alpha * (sample - filtered[n-1])
```

Do not invent calibration constants. Derive them from a datasheet, traceable reference, or measured calibration run. Preserve raw values alongside converted values during development. Filtering reduces visible noise; it does not correct range, wiring, aliasing, saturation, drift, or a wrong transfer function.

## Actuator bring-up

1. Identify normal, peak, stall/inrush, and fault current.
2. Select a driver and supply with voltage/current margin and thermal path.
3. Add flyback, snubber, current limiting, or isolation as the load requires.
4. Define the safe state during reset, bootloader, crash, disconnect, and firmware update.
5. Test the control signal with the load disconnected.
6. Test with a current-limited supply or benign load.
7. Add the real load and measure rail droop, driver temperature, EMI effects, and worst-case current.
8. Add timeouts, end stops, feedback, interlocks, and fault handling before unattended use.

Never rely solely on software to prevent an unsafe motion or energized state when a hardware interlock is feasible.

## Common device classes

### Environmental and analog sensors

Allow warm-up and settling. Place sensors away from regulator, ESP32, display, and actuator heat. Humidity, gas, particulate, light, sound, soil, pH, and electrochemical measurements are sensitive to enclosure, contamination, source impedance, and calibration. The code can be correct while the physical placement is wrong.

### One-wire sensors

Confirm bus voltage, pull-up, topology, cable length, parasite-power limits, unique ROM IDs, conversion timing, and CRC. Do not identify multiple devices by discovery order.

### Displays and LEDs

Confirm controller variant, dimensions, color order, address/CS, reset/backlight pins, memory needs, and current. LED strips require power injection, common reference or level shifting as appropriate, bulk capacitance, and a data-line protection strategy. Limit brightness in software only after the supply is electrically safe.

### Relays, motors, pumps, valves, solenoids, and servos

Use the actuator's rated driver and supply. Account for stall current, mechanical load, duty cycle, flyback, contact arcing, EMI, and sensor feedback. A relay module's contacts can be isolated while its control input is not.

### Radios and GNSS modules

Check logic voltage, peak current, antenna requirements, coexistence, UART/SPI flow control, reset/boot pins, regulatory constraints, and firmware version. RF failures can be power, antenna, enclosure, or coexistence problems rather than protocol bugs.

## Unknown component workflow

If a component lacks a reliable datasheet or schematic:

1. do not connect it to an ESP32 pin based on color labels or marketplace prose;
2. identify markings and trace the module circuit;
3. locate a manufacturer datasheet and vendor schematic;
4. verify voltage and pinout with current-limited power and instruments;
5. proceed only when the safe interface and expected identity are known.

If those artifacts cannot be established, label the integration unsupported rather than manufacturing confidence from a similar module.
