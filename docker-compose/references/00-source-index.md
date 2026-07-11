# Source Index and Freshness

This skill was researched with GroktoCrawl against the following primary sources. The Compose Specification is the semantic authority; Docker documentation is the operational authority for Docker Compose CLI behavior.

## Primary sources

- [Docker Compose overview](https://docs.docker.com/compose/) — purpose, lifecycle, and environments.
- [Compose file reference](https://docs.docker.com/reference/compose-file/) — current field reference.
- [Compose Specification](https://github.com/compose-spec/compose-spec/blob/main/spec.md) — application model and syntax.
- [Startup and shutdown order](https://docs.docker.com/compose/how-tos/startup-order/) — dependency conditions and healthchecks.
- [Networking](https://docs.docker.com/compose/how-tos/networking/) — service DNS, ports, networks, and diagnostics.
- [Interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) — `.env`, `--env-file`, precedence, and syntax.
- [Profiles](https://docs.docker.com/compose/how-tos/profiles/) — activation and dependency behavior.
- [Compose Watch](https://docs.docker.com/compose/how-tos/file-watch/) — sync, restart, rebuild, ignore rules, and permissions.
- [Secrets](https://docs.docker.com/compose/how-tos/use-secrets/) — runtime and build secret injection.
- [Merge](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/) — file order, path resolution, and merge classes.
- [Compose CLI reference](https://docs.docker.com/reference/cli/docker/compose/) — command flags and lifecycle operations.
- [Compose releases](https://docs.docker.com/compose/releases/release-notes/) — implementation release history.

## Source discipline

- Do not infer a feature's availability from a tutorial's publication date. Check release notes or the field's version marker.
- The Specification marks some attributes optional and platform-dependent. A file can parse while an implementation ignores part of it.
- Docker Compose CLI interpolation is not identical to every deployment target's interpolation; verify the target.
- Secondary tutorials are useful for worked patterns and failure stories, not for settling current syntax or compatibility.
