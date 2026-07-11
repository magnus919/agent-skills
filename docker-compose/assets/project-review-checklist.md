# Compose Project Review Checklist

Use this checklist before starting or handing off a Compose project.

- [ ] `compose.yaml` is the canonical base file and has no obsolete `version` key.
- [ ] `docker compose config --quiet` passes with the intended env file(s).
- [ ] The resolved model was reviewed with `docker compose config`.
- [ ] Internal URLs use service names and container ports, not host ports.
- [ ] Dependencies have readiness healthchecks or an explicit retry strategy.
- [ ] Persistent state uses named or externally managed volumes.
- [ ] Secrets are excluded from Git and granted only to required services.
- [ ] Optional services are behind documented profiles.
- [ ] Development watch rules ignore generated and host-native dependency trees.
- [ ] Production images are immutable enough to identify and roll back.
- [ ] Resource, restart, logging, and shutdown behavior is intentional.
- [ ] CI uses an isolated project name and cleans up only its own resources.
- [ ] Backup and restore procedures for persistent data were tested.
- [ ] Runtime health and the externally reachable endpoint were verified after deployment.
