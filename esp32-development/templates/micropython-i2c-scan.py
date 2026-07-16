"""Temporary MicroPython I2C identity probe. Run with mpremote before copying."""

from machine import I2C, Pin

# Replace from the exact board schematic and MicroPython port documentation.
SDA_PIN = None
SCL_PIN = None
I2C_ID = 0
FREQUENCY_HZ = 100_000

if not isinstance(SDA_PIN, int) or not isinstance(SCL_PIN, int):
    raise ValueError("Set SDA_PIN and SCL_PIN from authoritative board documentation")

bus = I2C(I2C_ID, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=FREQUENCY_HZ)
addresses = bus.scan()
print("I2C addresses:", [f"0x{address:02x}" for address in addresses])
print("A scan is an electrical/address clue; verify device identity next.")
