# Source index

This skill was built from the public repository [agessaman/meshcore-packet-capture](https://github.com/agessaman/meshcore-packet-capture), inspected at commit `1d69230fbd2959412f77788a430c91e1b11cd765` on 2026-07-11. The checkout reported release `v2.0.0`, published 2026-06-22. Upstream is the source of truth when this skill conflicts with a newer release.

## Coverage inventory

- [x] `README.md`: scope, install modes, configuration precedence, CLI, Docker, output, topics, troubleshooting
- [x] `pyproject.toml`, `requirements.txt`: Python/runtime dependency floor and CLI entry point
- [x] `src/meshcore_packet_capture/__main__.py`: installed command dispatch
- [x] `src/meshcore_packet_capture/packet_capture.py`: transports, retries, health checks, MQTT, topics, stats, filters, output, shutdown
- [x] `src/meshcore_packet_capture/config_loader.py`: TOML loading, deep merge, named broker merge, environment flattening
- [x] `src/meshcore_packet_capture/auth_token.py`: device/Python/decoder signing and key format
- [x] `src/meshcore_packet_capture/enums.py`: packet and route type vocabulary
- [x] `config.toml.example`, `.env`: configuration surface and legacy aliases
- [x] `presets/*.toml`: broker preset shape and sequential broker behavior
- [x] `DOCKER.md`, `docker-compose.yml`, `Dockerfile`: container deployment and hardware access
- [x] `NIXOS.md`, `nix/`: NixOS package/module deployment
- [x] `install.sh`, `installer/`: bootstrap, release resolution, interactive install, update, migrate
- [x] `packaging/systemd/`, `packaging/launchd/`: service supervision and platform permissions
- [x] `uninstall.sh`: backup and destructive cleanup boundaries
- [x] `devtools/`: BLE/network diagnostic helpers, treated as optional development tools
- [x] `tests/`: configuration, installer, CLI, packet parsing, JWT, presets, and lifecycle behavior
- [x] `.github/workflows/`: Docker, Nix, pytest, and release automation

## Reconciliation notes

- The README says the recommended meshcore dependency is `>=2.2.31`; `pyproject.toml` confirms that floor.
- TOML is described as primary, but the actual precedence depends on whether a value came from the real process environment or a dotenv file. The skill documents the implementation's snapshot behavior.
- The README says the installer installs the latest release by default; `installer/__main__.py` and `install.sh` confirm explicit `--tag`/`--branch` overrides.
- Older README examples mention `docker-compose`; current `DOCKER.md` uses `docker compose`. Prefer the Compose v2 form.
- `NIXOS.md` documents a bounded broker example; `config_loader.py` and tests show the Python runtime supports more than four enabled brokers. The skill follows the runtime for the general rule and treats Nix option count as module-specific.
- Upstream contains compatibility/development helpers and a large implementation file. This skill distills operation and diagnosis rather than copying source code.

## Refresh procedure

1. Fetch the current default branch and latest release with `gh`.
2. Re-read `README.md`, `pyproject.toml`, `config.toml.example`, `DOCKER.md`, `NIXOS.md`, service templates, installer entry points, config loader, and CLI parser.
3. Run the upstream tests if dependencies and hardware-independent fixtures are available.
4. Update this index's commit/date and reconcile every changed command, default, version, and environment variable before changing executable guidance.
