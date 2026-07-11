# Pipeline syntax and reusable workflow patterns

## Minimal workflow

Woodpecker loads `.woodpecker.yml` or files under the configured `.woodpecker/` directory. A workflow is a serial list of steps by default; a non-zero step exits the workflow unless failure handling or a failure-status step applies.

```yaml
when:
  - event: [push, pull_request]
steps:
  - name: test
    image: golang:1.23
    commands:
      - go test ./...
```

The implicit clone step checks out the commit into the shared workspace. Changes made by one step are available to later steps.

## Step fields

- `image`: container image, plugin image, or shell source for the local backend.
- `commands`: serial shell commands for a build step. Do not combine with a plugin or service-only step.
- `environment`: step variables; use `from_secret` for Woodpecker-managed secrets.
- `settings`: plugin settings; a secret setting becomes a `PLUGIN_<NAME>` environment variable.
- `when`: conditional execution.
- `failure`: `fail` (default), `ignore`, or `cancel`.
- `depends_on`: allow independent steps to run in parallel and express ordering.
- `pull: true`: pull an updated image instead of using an already-present image.
- `detach: true`: run a long-lived step until the pipeline ends.
- `services`: service containers available by their step name as a hostname.
- `volumes`: backend-specific mounts; treat host mounts as privileged operations.
- `backend_options`: backend-specific settings such as Kubernetes resources.

## Conditions

A `when` list is OR across entries; predicates inside one entry are AND. Use `event` with `branch` when a branch filter must apply only to pushes. Available event names include `push`, `pull_request`, `pull_request_closed`, `pull_request_metadata`, `tag`, `release`, `deployment`, `cron`, and `manual`.

```yaml
when:
  - event: push
    branch: main
  - event: tag
    ref: refs/tags/v*
```

`status` accepts `success` and `failure` and is useful for notifications:

```yaml
- name: notify
  image: alpine:3.20
  commands: ["notify-command"]
  when:
    - status: [success, failure]
```

`path` conditions apply to push and pull-request events. `cron` filters cron event names. `platform` and `matrix` are useful with matrix workflows. Check the current workflow-syntax page for the complete condition list and glob semantics.

## Services and readiness

Services are reachable by their declared name and container port:

```yaml
services:
  - name: database
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: example
steps:
  - name: test
    image: postgres:16
    commands:
      - sleep 10
      - pg_isready -h database
```

A service being created does not mean it is ready. Prefer a bounded retry loop or a native readiness probe over an arbitrary long sleep. Service containers receive SIGTERM at the end of the pipeline and may be force-killed.

## Secrets

```yaml
steps:
  - name: publish
    image: registry.example/publisher:1
    environment:
      TOKEN:
        from_secret: publish-token
    settings:
      api_token:
        from_secret: publish-token
```

Woodpecker has repository, organization, and global secret scopes; the more specific scope wins according to the current documentation's precedence rules. Secrets are not exposed to pull requests by default. Restrict secrets by event and plugin image. When a shell must receive a literal variable expression, escape preprocessing with `$${TOKEN}`.

## Plugins

Plugins are pipeline steps with pre-defined behavior, configured through `settings`. Treat plugin images as executable code. Pin versions, restrict secret use by image, and prefer trusted or reviewed plugins for deployments.

## Matrices and labels

A matrix expands a workflow into one execution per combination. Use labels to route combinations to agents with the required platform or toolchain. Keep the matrix small and make the selected values visible in step names or logs.

```yaml
matrix:
  GO_VERSION: ["1.22", "1.23"]
  platform: [linux/amd64, linux/arm64]
labels:
  platform: ${platform}
steps:
  - name: test-${GO_VERSION}
    image: golang:${GO_VERSION}
    commands: ["go test ./..."]
```

## Multiple workflows

Files in `.woodpecker/` become separate workflows. Their names derive from filenames without the path, leading dots, or `.yml`/`.yaml` extension when used in `depends_on`. Use dependencies to express a DAG, not to create an accidental serial bottleneck.

## Advanced YAML

The official advanced-usage documentation covers YAML anchors and aliases for reducing duplication. Use them sparingly: explicit repeated steps are easier to review when the configuration is security-sensitive or contains different conditions.

## Local checks

```bash
woodpecker-cli lint .woodpecker.yml
woodpecker-cli exec .woodpecker.yml
```

Local execution does not reproduce forge webhooks, server-side secret scope, or every backend behavior. Treat it as a fast syntax/command check, then run a real pipeline.