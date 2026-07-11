# Source index and freshness notes

The skill was researched with GroktoCrawl against primary Woodpecker documentation and the official repository. URLs below are the source of truth for claims; paths can move between major versions.

## Official documentation

- General administration: https://woodpecker-ci.org/docs/administration/general
- Docker Compose installation: https://woodpecker-ci.org/docs/administration/installation/docker-compose
- Server configuration: https://woodpecker-ci.org/docs/administration/configuration/server
- Agent configuration and registration: https://woodpecker-ci.org/docs/administration/configuration/agent
- Forge overview: https://woodpecker-ci.org/docs/administration/configuration/forges/overview
- Gitea integration: https://woodpecker-ci.org/docs/administration/configuration/forges/gitea
- Forgejo integration: https://woodpecker-ci.org/docs/administration/configuration/forges/forgejo
- Docker backend: https://woodpecker-ci.org/docs/administration/configuration/backends/docker
- Kubernetes backend: https://woodpecker-ci.org/docs/administration/configuration/backends/kubernetes
- First pipeline: https://woodpecker-ci.org/docs/usage/intro
- Workflow syntax: https://woodpecker-ci.org/docs/usage/workflow-syntax
- Multiple workflows/dependencies: https://woodpecker-ci.org/docs/usage/workflows
- Matrix workflows: https://woodpecker-ci.org/docs/usage/matrix-workflows
- Services: https://woodpecker-ci.org/docs/usage/services
- Secrets: https://woodpecker-ci.org/docs/usage/secrets
- Plugins: https://woodpecker-ci.org/docs/usage/plugins/overview
- Environment variables: https://woodpecker-ci.org/docs/usage/environment
- Advanced YAML: https://woodpecker-ci.org/docs/usage/advanced-usage
- Troubleshooting: https://woodpecker-ci.org/docs/usage/troubleshooting
- CLI: https://woodpecker-ci.org/docs/cli
- Helm chart and metrics: https://woodpecker-ci.org/docs/administration/installation/helm-chart
- Project settings, trust, and approval: https://woodpecker-ci.org/docs/usage/project-settings
- Registries: https://woodpecker-ci.org/docs/usage/registries
- Autoscaler: https://woodpecker-ci.org/docs/administration/configuration/autoscaler

## Official repository

- Source and release information: https://github.com/woodpecker-ci/woodpecker
- Compose example: https://github.com/woodpecker-ci/woodpecker/blob/main/docker-compose.example.yaml

## Freshness rules

- Verify environment-variable names against the provider page for the installed major version.
- Keep server and agent image majors aligned.
- Prefer a SemVer tag or controlled major/minor tag; do not use an unreviewed floating `latest` tag.
- Treat issue discussions and old examples as historical context, not current API documentation.
- If docs and a local `--help` output disagree, record the installed version and follow the local binary for that invocation while checking release notes for migration impact.