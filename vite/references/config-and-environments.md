# Vite Configuration And Environments

## Inspect the loading model

Vite loads `vite.config.js`, `vite.config.ts`, or an equivalent config from the project root unless the command supplies another root/config. Read the package script and config together: a monorepo may set `root`, and a config may be asynchronous or mode-aware.

Common precedence for variables loaded by Vite is mode-specific local, mode-specific, general local, then general env files, with existing process environment taking precedence. Confirm the exact behavior against the installed Vite version before relying on subtle precedence. `.env*` files are loaded at startup, so restart the dev server after edits.

Only variables with the configured public prefix (normally `VITE_`) are exposed to client code through `import.meta.env`. This is an exposure boundary, not a secret store. Keep API keys, passwords, signing material, and internal credentials server-side. Do not print env values in diagnostics or commit `.env.local`.

## Config review checklist

- `base` matches the URL prefix where static files are served; use `/` for domain-root hosting and a repository path only when hosting requires it.
- `root` and `publicDir` point at intended directories; public files are copied as-is and should not contain secrets.
- Aliases resolve consistently in Vite, TypeScript, tests, and the editor; prefer absolute filesystem paths in config.
- Framework plugins match the framework and installed Vite major; inspect plugin peer dependencies before upgrading.
- `define` contains only deliberate compile-time constants. Never interpolate untrusted or secret process values into it.
- `server.proxy` is development-only unless the deployment has an equivalent reverse proxy; document target and path rewriting.
- `resolve.dedupe` and dependency optimization settings are added only for a demonstrated duplicate or prebundle problem.

## Modes and scripts

Keep mode selection explicit (`vite --mode staging`, `vite build --mode production`) and ensure the build script's mode matches the deployment contract. Avoid assuming `NODE_ENV` selects a Vite mode. Test required variables by name and presence, not by logging their values.

For SSR or library mode, use the project's framework and package contract: client-only assumptions about `import.meta.env`, HTML entry files, and `outDir` may not apply. A library build has different externalization and output expectations than an application build.

## Change and verify

Make one config change at a time. Run the project's typecheck/lint if available, then a production build. Inspect the generated HTML and asset references under `outDir`; if `base` is non-root, test a deep link and an asset URL at that prefix. Route browser-level verification to [Playwright](../../playwright/SKILL.md) and accessibility verification to [web-accessibility](../../web-accessibility/SKILL.md).
