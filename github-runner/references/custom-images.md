# Custom Runner Images

## GitHub's Official Runner Image

Published at `ghcr.io/actions/actions-runner`. Based on `mcr.microsoft.com/dotnet/runtime-deps:8.0-jammy`.

**Contents:**
- Runner binaries
- Runner container hooks (for Kubernetes mode with ARC)
- Docker CLI (for Docker-in-Docker mode)

Tags accompany each runner release + `latest`.

## Building Custom Runner Images

Requirements:
1. Base image must run the runner application (Linux with standard system dependencies)
2. Runner binary at `/home/runner/`
3. Launch via `/home/runner/run.sh`
4. For ARC Kubernetes mode: container hooks at `/home/runner/k8s`

**Example Dockerfile:**

```dockerfile
FROM mcr.microsoft.com/dotnet/runtime-deps:6.0 as build

ARG RUNNER_VERSION="2.322.0"
ARG RUNNER_ARCH="x64"
ARG RUNNER_CONTAINER_HOOKS_VERSION="0.3.1"

ENV DEBIAN_FRONTEND=noninteractive
ENV RUNNER_MANUALLY_TRAP_SIG=1
ENV ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT=1

RUN apt update -y && apt install curl unzip -y

RUN adduser --disabled-password --gecos "" --uid 1001 runner \
    && groupadd docker --gid 123 \
    && usermod -aG sudo runner \
    && usermod -aG docker runner \
    && echo "%sudo ALL=(ALL:ALL) NOPASSWD:ALL" > /etc/sudoers

WORKDIR /home/runner

RUN curl -f -L -o runner.tar.gz \
      https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./runner.tar.gz && rm runner.tar.gz

RUN curl -f -L -o runner-container-hooks.zip \
      https://github.com/actions/runner-container-hooks/releases/download/v${RUNNER_CONTAINER_HOOKS_VERSION}/actions-runner-hooks-k8s-${RUNNER_CONTAINER_HOOKS_VERSION}.zip \
    && unzip ./runner-container-hooks.zip -d ./k8s && rm runner-container-hooks.zip

USER runner
```

## Installing Software

Options for adding tools to runner environments:

1. **Pre-installed image**: Build a custom Dockerfile with needed tools baked in
2. **Setup actions**: Use `actions/setup-*` in workflows — recommended for standard tools
3. **Inline install**: Add `apt-get` or `pip install` steps to workflow — adds to job runtime
4. **VM base image**: For VM runners, bake tools into the base image

## ARC Container Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Docker-in-Docker | Runner pod runs Docker inside; steps use Docker actions | Workflows that need containers |
| Kubernetes | Each step runs as its own K8s pod; no Docker needed | Lighter footprint, cleaner isolation |
| Default | Runner binary runs directly in container | Simple workflows, no containers needed |

## Runner Version Management

- Check latest release: https://github.com/actions/runner/releases
- Subscribe to releases for notifications
- **30-day update window** for `--disableupdate` runners — after 30 days, GitHub stops assigning jobs
- **Critical security updates** block jobs immediately until updated
- For Docker runners: update image tag and recreate containers
- For systemd runners: download new binary, stop service, replace, restart
