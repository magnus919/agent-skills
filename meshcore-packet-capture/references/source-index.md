# Source index

This skill was built from the public repository [agessaman/meshcore-packet-capture](https://github.com/agessaman/meshcore-packet-capture), inspected at commit `c011f4e` on 2026-08-09. The checkout reported release `v2.2.0`, published 2026-07-30. Upstream is the source of truth when this skill conflicts with a newer release.

## Coverage inventory

- [x] `README.md`: scope, install modes, configuration precedence, CLI, Docker, output, topics, troubleshooting
- [x] `pyproject.toml`, `requirements.txt`: Python/runtime dependency floor (meshcore pinned `==2.3.8` as of v2.2.0) and CLI entry point
- [x] `src/meshcore_packet_capture/__main__.py`: installed command dispatch
- [x] `src/meshcore_packet_capture/packet_capture.py`: transports, retries, health checks, MQTT, topics, stats, filters, output, shutdown, neighbors CLI flags (`--neighbors-now`, `--neighbors-exit`)
- [x] `src/meshcore_packet_capture/config_loader.py`: TOML loading, deep merge, named broker merge, environment flattening, decoding/neighbors/log-rotation keys
- [x] `src/meshcore_packet_capture/auth_token.py`: device/Python/decoder signing and key format
- [x] `src/meshcore_packet_capture/enums.py`: packet and route type vocabulary
- [x] `src/meshcore_packet_capture/payload_decode.py`: GRP_TXT decryption, ADVERT parsing, structured decode fields (v2.1.0+)
- [x] `src/meshcore_packet_capture/neighbors.py`: zero-hop neighbor discovery + region-scope collection for the neighbors topic (v2.1.0+)
- [x] `config.toml.example`, `.env`: configuration surface and legacy aliases (decode/neighbors/log-rotation blocks, `ble_pin`, per-broker `include_decoded`/`neighbors`/`owner`/`email`)
- [x] `presets/*.toml`: broker preset shape and sequential broker behavior
- [x] `DOCKER.md`, `docker-compose.yml`, `Dockerfile`: container deployment and hardware access
- [x] `NIXOS.md`, `nix/`: NixOS package/module deployment
- [x] `install.sh`, `installer/`: bootstrap, release resolution, interactive install, update, migrate, `--user-service` flow
- [x] `packaging/systemd/`, `packaging/launchd/`: service supervision and platform permissions
- [x] `uninstall.sh`: backup, `--user-service` removal, and destructive cleanup boundaries
- [x] `devtools/`: BLE/network diagnostic helpers, treated as optional development tools
- [x] `tests/`: configuration, installer, CLI, packet parsing, JWT, presets, and lifecycle behavior
- [x] `.github/workflows/`: Docker, Nix, pytest, and release automation

## Reconciliation notes

- The README says the recommended meshcore dependency is `>=2.2.31`; `pyproject.toml` at v2.2.0 pins `==2.3.8` and the contact-injection shim was removed. The skill follows the pin.
- TOML is described as primary, but the actual precedence depends on whether a value came from the real process environment or a dotenv file. The skill documents the implementation's snapshot behavior.
- The README says the installer installs the latest release by default; `installer/__main__.py` and `install.sh` confirm explicit `--tag`/`--branch` overrides, plus the v2.1.0+ `--user-service` local-checkout flow.
- Older README examples mention `docker-compose`; current `DOCKER.md` uses `docker compose`. Prefer the Compose v2 form.
- `NIXOS.md` documents a bounded broker example; `config_loader.py` and tests show the Python runtime supports more than four enabled brokers. The skill follows the runtime for the general rule and treats Nix option count as module-specific.
- Upstream contains compatibility/development helpers and a large implementation file. This skill distills operation and diagnosis rather than copying source code.

## Refresh procedure

1. Fetch the current default branch and latest release with `gh`.
2. Re-read `README.md`, `pyproject.toml`, `config.toml.example`, `DOCKER.md`, `NIXOS.md`, service templates, installer entry points, config loader, CLI parser, `payload_decode.py`, and `neighbors.py`.
3. Run the upstream tests if dependencies and hardware-independent fixtures are available.
4. Update this index's commit/date and reconcile every changed command, default, version, and environment variable before changing executable guidance.
