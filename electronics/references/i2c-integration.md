# I2C integration

Treat I2C as an electrical bus plus a transaction contract.

## Electrical budget

Confirm every device's logic rail, open-drain behavior, input thresholds,
leakage, sink current, clock-stretch support, and address straps. Calculate the
effective parallel pull-up resistance, including module defaults. Choose `Rp`
between the sink-current lower bound and rise-time upper bound:

`Rp(min) = (VDD(max) - VOL(max)) / IOL(guaranteed)`

Use the weakest guaranteed sink capability of every line driver at the
required low voltage, not an absolute-maximum pin-current rating. Include rail
and resistor tolerances; a buffer or rise-time accelerator changes the simple
RC model and needs its own segment analysis.

For the usual 30%-to-70% definition, `tr = 0.8473 × Rp × Cb`, so
`Rp(max) = tr(max)/(0.8473 × Cb)`. TI's SLVA689 lists 1000/300/120 ns
rise-time limits for Standard/Fast/Fm+ and 400/400/550 pF reference loads;
the target datasheets and selected mode control. A smaller resistor improves
rise time but increases low-level current and power. Measure actual rise time;
do not treat a nominal resistor as proof of compliance.

Source: TI SLVA689:
https://www.ti.com/lit/an/slva689/slva689.pdf
NXP UM10204 sections 3 and 7:
https://www.nxp.com/docs/en/user-guide/UM10204.pdf

### Worked design check

Suppose the measured/estimated line capacitance is 120 pF, the rail is 3.3 V,
and Fast-mode operation is required. The TI relation gives
`Rp(max) ≈ 300 ns/(0.8473 × 120 pF) ≈ 2.95 kΩ`. If the device's low-level
specification is 0.4 V at 3 mA, the simple lower bound is approximately
`(3.3 - 0.4)/3 mA ≈ 967 Ω`. That interval still needs device-specific leakage,
rail tolerance, parallel pull-ups, series resistors, and measured waveform
checks. A 2.2 kΩ candidate may be reasonable for this stated case; it is not a
portable default.

If two 4.7 kΩ pull-ups are fitted on separate modules, their effective value is
2.35 kΩ before any other pull-up is counted. Removing one may improve low-level
current margin while preserving rise time. Conversely, replacing 4.7 kΩ with
10 kΩ without measuring Cb can create a slow edge that a nominal frequency
setting hides.

## Bring-up and transaction evidence

1. With power removed and stored energy discharged, check for unintended shorts.
   Then power the intended domains in their documented sequence and measure idle
   SDA/SCL levels. Do not apply pull-up power to an unpowered device unless its
   powered-off pin behavior permits it; protection structures may back-power it.
2. At conservative speed, capture idle levels and one transaction. Record
   start/repeated-start/stop, 7-bit address, direction, ACK/NAK, register bytes,
   data, and clock stretching.
3. Use a scan only as an address-response clue. Some probe methods can alter a
   device state; write-only devices may not respond to reads. A found address
   is not identity. Read a documented manufacturer/device/revision or status
   register before trusting the driver.
4. Check reset state, register pointer semantics, endian/order, readiness delay,
   and documented repeated-start requirements.

### Scan decision table

| Scan result | Next test | Do not conclude |
|---|---|---|
| Both lines low | isolate power/devices; identify holder | that the controller API is wrong |
| Both lines high, no ACK | verify rail, reset, pins, straps, address notation | that the device is dead |
| One or more ACKs | read documented identity/status register | that ACK proves device identity |
| Unexpected extra ACK | remove modules one at a time; inspect parallel pull-ups/ghosts | that every responder is intended |
| ACK then hang | capture phase and line owner; enforce timeout | that lower speed fixes root cause |

Before a scan, decide whether the probing operation is read, write, or a
controller-specific “quick” transaction, and whether the target permits it.
Store that decision with the capture. For a write-capable device, a scan that
touches a command register is a state mutation and needs an explicit rollback
or reset plan.

## Recovery ownership

The controller owns timeout and recovery policy. Every wait for SCL, ACK, or a
device-ready state has a deadline and reports the phase. If SDA is stuck low,
NXP's bus-clear procedure calls for nine clock pulses; if it remains low, use
hardware reset or power-cycle. If SCL is stuck low, reset or power-cycle first.
Only pulse lines when the controller is electrically allowed to take ownership,
all other controllers are quiescent, and the action cannot trigger an unsafe
write. Capture line state before and after recovery and identify the holder if
possible.

## Fault localization

If 0x48 ACKs but ADC identity/readback is wrong, capture address and direction,
resolve 7-bit versus shifted 8-bit notation, then check identity register,
pointer byte, repeated-start, reset readiness, and endian order. This localizes
the fault to selection, transaction contract, reset, or bus corruption; it does
not prove the library is at fault.

If SDA is low before START, isolate modules and measure each branch. If it falls
after a byte, capture ACK and ownership. If SCL is low, distinguish documented
clock stretching from a stuck output using a deadline and waveform. Recovery
records before/after state, pulse count, reset/power action, and line owner.
