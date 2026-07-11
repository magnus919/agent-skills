# Security and Trust Boundaries

## Secrets

Runtime secrets are explicitly granted and mounted as files:

```yaml
services:
  api:
    image: example/api:1.2
    secrets: [api_token]
secrets:
  api_token:
    file: ./secrets/api_token.txt
```

The file appears at `/run/secrets/api_token`. Some official images support `_FILE` variables; confirm the image documentation before using that convention. Build secrets belong under `build.secrets` and must not be baked into an image layer.

A local-file Compose secret protects against casual environment exposure, but is not equivalent to a managed secret store. Protect the source file, exclude it from version control, limit service grants, and use an external manager when the threat model requires it.

## Container hardening

Prefer a non-root `user`, drop unnecessary capabilities, use `read_only: true` where compatible, and add explicit writable `tmpfs` or volume mounts. Avoid mounting the Docker socket into untrusted containers: it is effectively host control. Avoid `privileged: true`, host networking, broad device access, and `cap_add: [ALL]` unless documented and reviewed.

## Supply chain

Pin image references, review base-image provenance, scan images, minimize build context with `.dockerignore`, and never pass secrets through build args or ordinary `ARG` values. Use least privilege for host paths and external networks.

## Portability caveat

The Compose Specification includes platform-dependent and optional attributes. Security settings that work on Linux may behave differently on another runtime. Verify the rendered model and runtime state on the target platform.
