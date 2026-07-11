# Troubleshooting Playbook

Start with evidence, not a rewrite:

```bash
docker compose config --quiet
docker compose ps --all
docker compose logs --no-color --tail=200 SERVICE
docker compose events --json
docker compose top SERVICE
docker inspect CONTAINER --format '{{json .State}}'
```

| Symptom | Check first | Likely fix |
|---|---|---|
| Dependency connection refused | `depends_on`, healthcheck, service logs | Gate on `service_healthy`; use `SERVICE:CONTAINER_PORT`; make client retry |
| Name does not resolve | `docker network inspect`; service networks | Put services on the same network; remove accidental host mode |
| Host connects, sibling cannot | URL uses `localhost` or host port | Use service DNS and container port inside Compose |
| Container exits | logs, exit code, effective command | Fix command/entrypoint, missing file, permissions, or architecture |
| Health is unhealthy | health log and probe executable | Run probe manually; check endpoint, credentials, and startup grace |
| Port already allocated | `docker compose port`, host listeners | Change published host port or stop the conflicting project |
| Data disappeared | volume list, mount target, `down -v` history | Restore backup; use a named/external volume and verify mounts |
| Override surprises | `docker compose config` | Remember base-relative paths and merge rules; use `!reset`/`!override` deliberately |
| Environment is wrong | `config --environment`, `config` | Check shell/`--env-file`/`.env` precedence and required substitutions |
| Watch does nothing | `develop.watch`, build, target permissions | Use a built service, required tools, writable target, and ignore rules |
| OOM or throttling | `docker stats`, host memory, limits | Measure, adjust limits, reduce concurrency, or fix workload |
| Works on one machine only | image architecture, bind paths, runtime support | Pin compatible images, remove host-specific paths, verify optional fields |

Never fix connectivity by publishing every internal port or using host networking. That hides the model defect and widens exposure.

For destructive recovery, snapshot or back up first. Do not run `down -v`, `volume rm`, `system prune`, or delete host-mounted data as a diagnostic step.
