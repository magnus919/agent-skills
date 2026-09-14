# Compatibility and setup checks

Run `scripts/spring_ai_check.py` before changing a project. It reads, without executing, `pom.xml`, `build.gradle`, `build.gradle.kts`, `gradle.properties`, `application.properties`, and `application.yml`/`yaml`, plus Java source under conventional source roots.

## Interpret findings

- A detected Spring AI BOM version or conventional version property is a declared build clue, not proof that every starter is compatible with the Spring Boot or JDK version.
- A missing BOM is a maintainability warning when multiple Spring AI modules are present; confirm the project’s chosen dependency-management policy before adding one.
- A suspected literal provider API key produces a redacted finding. This scan does not prove that a usable credential exists; values are never printed.
- Streaming requires the reactive stack in the current ChatClient reference; verify the project’s requested mode and test the actual endpoint.
- Configuration names and advisor classes are version-sensitive. Resolve a finding against the matching official version docs and release notes.

## Safe smoke boundary

The checker reports static clues and potential hazards; it cannot establish readiness. A real smoke test requires a provider, credentials, network policy, and a test model. Keep it separate from static checks and use a synthetic prompt and non-sensitive fixture. Verify response content, metadata, timeout/error mapping, and cleanup. Never report provider integration as tested when the run was skipped or blocked.

## Static scan limits

Maven versions are read from scoped XML elements and local properties. Gradle scanning recognizes common literal BOM coordinates and quoted local variables; it does not evaluate build logic, resolve remote parents, or load version catalogs. Configuration and Java checks are lexical heuristics, not YAML or Java semantic analysis. Nested YAML, profile-specific files, Kotlin source, generated configuration, and dynamic values can be missed. A clean result means only that no implemented heuristic matched; verify effective dependencies and runtime behavior separately.
