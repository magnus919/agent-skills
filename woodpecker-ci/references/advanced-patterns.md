# Advanced patterns

## Parallel fan-out and fan-in

Steps run serially unless their dependency graph allows parallel work. Use empty `depends_on` for independent roots and explicit dependencies for the join:

```yaml
steps:
  - name: lint
    depends_on: []
    image: golangci/golangci-lint:v2
    commands: ["golangci-lint run"]
  - name: test
    depends_on: []
    image: golang:1.23
    commands: ["go test ./..."]
  - name: package
    depends_on: [lint, test]
    image: alpine:3.20
    commands: ["./package.sh"]
```

For multiple files under `.woodpecker/`, a workflow name is derived from its filename without the leading dot and extension. `depends_on` can include an optional dependency when a path filter may skip it. Use optional dependencies deliberately; a skipped check should not silently remove a required quality gate.

## Concurrency control

Use a workflow concurrency limit for deployments that must not overlap:

```yaml
concurrency:
  limit: 1
  group: deploy-${CI_COMMIT_BRANCH}
```

The official workflows documentation notes that queued workflows in the same group start in pipeline-creation order, not in the order they become ready. This is useful for preserving deployment commit order.

## Matrix and platform routing

Matrices create a workflow for each combination. Use `include` for an explicit set of combinations, interpolate matrix variables with `${VARIABLE}`, and map a platform value to an agent label. Keep the expansion bounded and inspect the installed version's documented matrix limits before generating a large Cartesian product.

```yaml
matrix:
  include:
    - GO_VERSION: "1.22"
      platform: linux/amd64
    - GO_VERSION: "1.23"
      platform: linux/arm64
labels:
  platform: ${platform}
steps:
  - name: test
    image: golang:${GO_VERSION}
    commands: ["go test ./..."]
```

## Reusable YAML

The advanced-usage documentation supports YAML anchors and aliases. Use them for image names, plugin settings, and repeated conditions, but keep security-sensitive differences explicit enough to review. Test the rendered workflow with the CLI linter because interpolation happens before pipeline execution and may alter the value being parsed.

## Private registries and local images

Register private registry credentials in the Woodpecker UI or the documented backend mechanism. The server configuration documents `WOODPECKER_DOCKER_CONFIG` for a shared Docker credential file. Local images built during one step are backend- and host-dependent; a workflow that assumes a local image must be pinned to one suitable agent and normally requires trusted access to the Docker socket.

## Caching

Woodpecker shares the workspace between steps in one workflow, but separate workflows do not share that workspace. For cross-workflow or persistent caching, use a backend-appropriate named volume, PVC, or reviewed cache/artifact plugin. On Kubernetes, confirm the storage class supports the access mode and that the cache is not a hidden cross-branch contamination path.

## Autoscaling and ephemeral agents

The agent configuration supports one-shot execution for an agent that should run one workflow and exit. The optional autoscaler can create agents based on queue demand, but treat it as a separate operational component: verify provider credentials, min/max agent bounds, gRPC reachability, and its current feature coverage before relying on it for production capacity.

## Sources

- https://woodpecker-ci.org/docs/usage/workflows
- https://woodpecker-ci.org/docs/usage/workflow-syntax
- https://woodpecker-ci.org/docs/usage/matrix-workflows
- https://woodpecker-ci.org/docs/usage/advanced-usage
- https://woodpecker-ci.org/docs/usage/registries
- https://woodpecker-ci.org/docs/administration/configuration/autoscaler
- https://woodpecker-ci.org/docs/administration/configuration/agent