# Deployment and troubleshooting

Source basis: `agessaman/meshcore-packet-capture` commit `c011f4e` (v2.2.0), inspected 2026-08-09. These commands are operational guidance, not proof that a target host has the required hardware or credentials.

## Manual install

For a CLI/manual run:

```bash
pipx install meshcore-packet-capture
meshcore-packet-capture --help
meshcore-packet-capture --debug --no-mqtt
```

The package requires Python 3.11+ and installs `meshcore==2.3.8` (pinned as of v2.2.0), `paho-mqtt`, BLE, serial, telemetry, and signing dependencies. A pipx install does not create a service or write `/etc` configuration.

## Managed installer

The bootstrap installer is interactive and must run with root privileges:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/agessaman/meshcore-packet-capture/main/install.sh)"
```

Avoid `curl | sudo bash` for an interactive install. The bootstrap explicitly rejects stdin being consumed by the script. Download it to a temporary file if stdin is not a terminal.

By default, the installer resolves the latest published GitHub release for the payload and falls back to `main` when no release exists. Pin explicitly when needed:

```bash
sudo bash install.sh --tag v2.0.0
sudo bash install.sh --branch main
```

The installer creates `/opt/meshcore-packet-capture`, `/etc/meshcore-packet-capture/config.toml`, `/etc/meshcore-packet-capture/config.d/`, a virtual environment, and state under `/var/lib/meshcore-packet-capture`. It can select systemd, launchd, Docker, or manual mode. It also supports `python3 -m installer update` and `python3 -m installer migrate` for legacy `~/.meshcore-packet-capture` layouts.

After installation, finish the user config and confirm the installer did not report missing MQTT broker or placeholder IATA. On Linux:

```bash
sudo systemctl status meshcore-packet-capture
sudo journalctl -u meshcore-packet-capture -f
sudo systemctl restart meshcore-packet-capture
```

## User service (v2.1.0+)

For a local checkout on Linux, install a per-user systemd service that runs from the checkout's `.venv`:

```bash
./install.sh --user-service               # from the checkout root
./install.sh --user-service --repo-dir /path/to/checkout
```

Config files live in the repo itself: `.env`, `.env.local`, `config.toml`, and `config.d/*.toml` (loaded in sorted order). Manage it with user-level systemd:

```bash
systemctl --user status meshcore-packet-capture
systemctl --user restart meshcore-packet-capture
journalctl --user -u meshcore-packet-capture -f
```

Remove with `./uninstall.sh --user-service` from the same checkout; add `--remove-venv` to also delete the local `.venv`. The user-service path is distinct from the root managed install: no `/opt`, `/etc`, or root service is created.

On macOS, BLE uses a per-user LaunchAgent because Bluetooth permissions are granted to the login user. Serial/TCP can use the system LaunchDaemon:

```bash
launchctl list | grep meshcore-packet-capture
 tail -f /var/log/meshcore-packet-capture.log
```

## Docker

The published Compose file uses `ghcr.io/agessaman/meshcore-packet-capture:latest`, persists `./data` at `/app/data`, and defaults to serial. Start and inspect it with:

```bash
docker compose config
docker compose up -d
docker compose ps
docker compose logs -f meshcore-capture
```

For serial, map a stable host path from `/dev/serial/by-id/` to `/dev/ttyUSB0`. Do not default to `privileged: true` for serial. For BLE, set `privileged: true`, use `PACKETCAPTURE_CONNECTION_TYPE=ble`, optionally set `PACKETCAPTURE_BLE_ADDRESS` or `PACKETCAPTURE_BLE_DEVICE_NAME`, and try `network_mode: host` if discovery fails. Linux is the reliable container target; macOS and Windows container hardware access is limited.

Mount TOML at `/etc/meshcore-packet-capture` for non-trivial configuration. Environment variables still win over the mounted TOML. `.env.local` is legacy and lower precedence than TOML.

## NixOS

The repository includes a NixOS module under `services.meshcore-packet-capture`. Configure `connectionType`, the radio transport, `mqtt1`/`mqtt2`/additional brokers, IATA, and optional key settings, then run:

```bash
sudo nixos-rebuild switch
journalctl -u meshcore-packet-capture -f
```

The module's documentation shows LetsMesh WebSocket/TLS examples and custom password-authenticated brokers. Verify the module source against the current checkout before copying options because Nix attribute names can drift independently of the Python environment-variable names.

## Evidence-first troubleshooting

### No device connection

1. Run `meshcore-packet-capture --debug --no-mqtt` outside the service/container.
2. Confirm `PACKETCAPTURE_CONNECTION_TYPE` is one of `ble`, `serial`, or `tcp`.
3. For BLE, check Bluetooth permission, adapter visibility, address/name, `ble_pin` match, and container privileges. On Linux, BlueZ may require a first-time pairing even when a PIN is configured.
4. For serial, verify the host device exists and the service user/container sees the mapped path.
5. For TCP, verify host/port reachability and inspect SDK reconnect messages.

Do not jump to MQTT diagnosis until local device connection succeeds.

### Packets connect but no MQTT data

1. Confirm the broker's `ENABLED`, `SERVER`, and `PORT` values.
2. Check that broker numbering has no gap.
3. Confirm transport/TLS pairing: WebSockets commonly uses port 443 with TLS; raw MQTT commonly uses TCP.
4. For token auth, verify audience, token TTL, device signing capability, and private-key fallback availability.
5. Inspect resolved topic templates and IATA without exposing credentials.
6. If packet filtering is configured, confirm the numeric packet type is included.
7. If expecting a `decoded` object, verify `decode_payloads` is enabled and the target broker sets `include_decoded = true`. If expecting a neighbors snapshot, verify the broker sets `neighbors = true` and an IATA (or explicit `[broker.topics] neighbors`) exists; the cycle only runs when at least one enabled broker opts in.

The process tolerates transient disconnects, retries commands, and uses MQTT grace periods. A single reconnect warning is not proof of a permanent failure; look for the later connected/failed state.

### Service starts then exits

Run the exact runtime manually with `--debug --no-mqtt` to separate application failure from service supervision. Check Python version, installed package, permissions on the serial/BLE device, writable `data_dir`, and TOML parse errors. A service may intentionally exit after configured failure thresholds so systemd/launchd can restart it.

### Safe update or removal

Before updating or uninstalling, identify the active service/container and back up `config.d/99-user.toml`. Stop and verify the old process before removing anything. The upstream uninstaller is interactive, backs up user configuration when selected, and can remove services, container/image, install files, logs, `/etc/meshcore-packet-capture`, and `/var/lib/meshcore-packet-capture`. Do not reproduce its `rm -rf` actions casually during troubleshooting.
