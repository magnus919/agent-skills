# Compatibility and setup checks

Run `scripts/spring_ai_check.py` before changing a project. It reads, without executing, `pom.xml`, `build.gradle`, `build.gradle.kts`, `gradle.properties`, `application.properties`, and `application.yml`/`yaml`, plus Java source under conventional source roots.

## Interpret findings

- A detected Spring AI BOM/starter version is a project fact, not proof that every starter is compatible with the Spring Boot or JDK version.
- A missing BOM is a maintainability warning when multiple Spring AI modules are present; confirm the project’s chosen dependency-management policy before adding one.
- A provider API key is reported only as present/missing. Values are never printed.
- Streaming requires the reactive stack in the current ChatClient reference; verify the project’s requested mode and test the actual endpoint.
- Configuration names and advisor classes are version-sensitive. Resolve a finding against the matching official version docs and release notes.

## Safe smoke boundary

The checker can establish static readiness only. A real smoke test requires a provider, credentials, network policy, and a test model. Keep it separate from static checks and use a synthetic prompt and non-sensitive fixture. Verify response content, metadata, timeout/error mapping, and cleanup. Never report provider integration as tested when the run was skipped or blocked.
