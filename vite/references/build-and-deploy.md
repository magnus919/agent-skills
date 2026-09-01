# Vite Builds And Deployment

## Build diagnosis

Start with the first actionable error from the project's declared build script. Record Node, package-manager, Vite, framework-plugin, and lockfile evidence before changing dependencies. Typical layers are: config loading, dependency resolution, plugin transform, TypeScript/type checking, asset URL generation, chunking, and output writing.

Do not fix a missing module by adding a broad alias or deleting the lockfile. Check whether the import is misspelled, whether the dependency is declared in the correct workspace, whether an optional peer is missing, and whether the package manager install is reproducible. Only reinstall or clear a cache after confirming the cache is generated and the target is safe to remove.

## Output contract

`build.outDir` is relative to the Vite root unless configured otherwise. Confirm that deployment publishes that exact directory and does not accidentally publish source or a stale prior build. Keep generated output out of source control unless the host explicitly requires it.

`base` rewrites asset URLs. A root-relative build can work locally and fail under `/docs/` or a reverse proxy prefix. Verify HTML references, CSS URLs, dynamic imports, and client-side router fallback under the real prefix. Static hosting needs an SPA fallback for routes that are not physical files; alternatively use a routing strategy compatible with the host.

Treat build warnings as evidence, not noise. Review large chunks, dynamic-import boundaries, circular dependencies, and mixed ESM/CJS warnings. Performance budgets and UI architecture route to [frontend-engineering](../../frontend-engineering/SKILL.md); CI and hosting topology route to [platform-engineering](../../platform-engineering/SKILL.md).

## Safe verification sequence

1. Run typecheck/lint where declared.
2. Run the package manager's build script with a bounded timeout.
3. List output files and inspect generated HTML for expected asset paths.
4. Start preview only on the intended interface and port.
5. Check the deployed or previewed root and representative deep route with [Playwright](../../playwright/SKILL.md).
6. Run accessibility checks through [web-accessibility](../../web-accessibility/SKILL.md) when the task makes accessibility claims.

A successful build proves compilation and output generation, not correct routing, browser behavior, or accessibility.
