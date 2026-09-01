# Vite Diagnostics And Release Checks

## Environment values

Vite substitutes client-exposed variables at build time. Only variables with the
configured public prefix (commonly `VITE_`) should be read by browser code.
Treat every such value as public: it is not a secret merely because it lives in
`.env`. Keep credentials and server-only configuration outside the client
bundle. Check `.env.example`, Vite config, deployment configuration, and the
actual built assets for accidental exposure.

Vite loads mode-specific files with a defined precedence. Confirm the intended
mode (`development`, `production`, or a custom mode) and do not assume a local
`.env` matches CI. When diagnosing a value, inspect its name and source without
printing its value. Re-run the build after changing env configuration because
substitution is compile-time.

## Build and asset paths

Inspect `base` in `vite.config.*` when the app is served below `/`. A wrong base
usually appears as 404s for module, CSS, or asset URLs after deployment even
though the root-local dev server works. Validate the generated HTML and asset
references against the real deployment path. For SPA history fallback, confirm
the host serves the app entry point for non-root routes; Vite does not configure
that server rule for every deployment target.

## Dependency and output checks

Use the project's package manager lockfile and scripts. Check that `react` and
`react-dom` versions are compatible and that duplicate React copies are not
being pulled into the bundle, which can produce invalid hook call errors. Do not
blindly delete lockfiles or upgrade dependencies while diagnosing.

For release verification, run the existing typecheck/lint/test commands before
`vite build`, inspect warnings, and use a preview server for a smoke check at
the deployed base path. Keep source maps and reports out of user-facing output
unless the project intentionally publishes them.

## Safe diagnostic sequence

1. Record the package manager and available scripts from `package.json`.
2. Identify the active mode and public-prefix configuration without exposing
   values.
3. Inspect `base`, route fallback, and generated asset URLs.
4. Check lockfile consistency and React package version alignment.
5. Run the narrowest reproducible check, then the production build.
6. Confirm the browser flow with [playwright](../../playwright/SKILL.md) when
   route, asset, or navigation behavior is involved.
7. Ask [frontend-engineering](../../frontend-engineering/SKILL.md) for broader
   performance/component strategy and [web-accessibility](../../web-accessibility/SKILL.md)
   for a dedicated accessibility audit.
