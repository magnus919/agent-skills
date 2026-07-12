# MeshCore Packet Capture — Companion Radio Operations

Operate MeshCore Companion radio packet capture without reconstructing the upstream repository each time. The skill covers BLE, serial, and TCP connections, MQTT output, authentication, Docker, system services, NixOS, and evidence-first troubleshooting.

## Why Install This Skill

After installing it, your agent can configure and run the right transport, distinguish Companion radios from repeaters and RoomServers, publish packets to one or more MQTT brokers, and troubleshoot failures at the radio, broker, container, and service layers.

It also preserves the details that are easy to get wrong: TOML/environment precedence, sequential MQTT broker slots, IATA-based topics, device-signing fallback, macOS BLE permissions, and Docker hardware access.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Operational workflow, safety boundaries, routing, and completion checks |
| `references/configuration.md` | TOML/env schema, broker auth, topic templates, and packet filters |
| `references/deployment-and-troubleshooting.md` | Manual, managed, Docker, NixOS, and diagnostic procedures |
| `references/source-index.md` | Upstream commit, coverage inventory, and refresh notes |

## Quick Start

```bash
pipx install meshcore-packet-capture
meshcore-packet-capture --debug --no-mqtt
# Configure IATA + MQTT, then run:
meshcore-packet-capture --debug
```

## Triggers

Use this skill for `meshcore-packet-capture`, MeshCore Companion radios, BLE/serial/TCP packet capture, MQTT packet publishing, LetsMesh, `PACKETCAPTURE_*`, `config.toml`, Docker Compose deployment, systemd, launchd, NixOS, or connection troubleshooting.

## Requirements

Python 3.11+, the upstream runtime dependencies, a MeshCore Companion radio, and access to the selected transport. MQTT publishing additionally requires a reachable broker and either password or token authentication. Docker hardware access is most reliable on Linux.
