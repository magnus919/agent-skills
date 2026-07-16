#!/usr/bin/env python3
"""Report ESP32-related host tools and candidate serial ports without opening them."""

from __future__ import annotations

import argparse
import glob
import json
import platform
import shutil
from pathlib import Path

TOOLS = (
    "idf.py",
    "esptool",
    "esptool.py",
    "arduino-cli",
    "pio",
    "mpremote",
    "circup",
    "esphome",
    "west",
    "espflash",
    "cargo-espflash",
)
PORT_PATTERNS = {
    "Darwin": ("/dev/cu.usb*", "/dev/cu.SLAB*", "/dev/cu.wchusb*"),
    "Linux": ("/dev/ttyUSB*", "/dev/ttyACM*", "/dev/serial/by-id/*"),
}


def candidate_ports(system: str) -> list[str]:
    ports = {
        str(Path(path))
        for pattern in PORT_PATTERNS.get(system, ())
        for path in glob.glob(pattern)
    }
    return sorted(ports)


def report(system: str | None = None) -> dict[str, object]:
    system = system or platform.system()
    port_enumeration = (
        "filesystem patterns"
        if system in PORT_PATTERNS
        else "not available without a native device-list tool on this platform"
    )
    return {
        "host": {"system": system, "machine": platform.machine()},
        "tools": {name: shutil.which(name) for name in TOOLS},
        "candidate_ports": candidate_ports(system),
        "port_enumeration": port_enumeration,
        "opened_ports": False,
        "next": "Identify the exact board before opening or flashing a port.",
    }


def self_test() -> None:
    assert "/dev/cu.Bluetooth-Incoming-Port" not in candidate_ports("Darwin")
    assert candidate_ports("Windows") == []
    windows = report("Windows")
    assert str(windows["port_enumeration"]).startswith("not available")
    data = report("TestOS")
    assert data["opened_ports"] is False
    tools = data["tools"]
    assert isinstance(tools, dict)
    assert set(tools) == set(TOOLS)
    print("self-test: PASS")


def print_text(data: dict[str, object]) -> None:
    host = data["host"]
    assert isinstance(host, dict)
    print(f"host: {host['system']} {host['machine']}")
    print("tools:")
    tools = data["tools"]
    assert isinstance(tools, dict)
    for name, path in tools.items():
        print(f"  {name}: {path or 'missing'}")
    print(f"port enumeration: {data['port_enumeration']}")
    print("candidate ports:")
    ports = data["candidate_ports"]
    assert isinstance(ports, list)
    if ports:
        for port in ports:
            print(f"  {port}")
    else:
        print("  none found (use the framework's native device-list command)")
    print(f"next: {data['next']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List ESP32-related tools and candidate ports without opening serial devices."
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--self-test", action="store_true", help="run deterministic checks")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    data = report()
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_text(data)


if __name__ == "__main__":
    main()
