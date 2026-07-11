# Woodpecker CI Incident Checklist

## Scope

- Woodpecker version and image tags:
- Forge and forge URL:
- Server URL:
- Backend: Docker / Kubernetes / Local:
- Repository and pipeline event:
- First failing step and exact error:

## Evidence

- [ ] `docker compose config` or rendered deployment config captured
- [ ] Server logs captured around the first failure
- [ ] Agent logs captured around scheduling/execution
- [ ] Agent shows connected in the UI
- [ ] Repository webhook and OAuth callback checked
- [ ] Image pull and registry access tested
- [ ] Secret name/scope/event/plugin filter checked without exposing its value
- [ ] Failure reproduced with a minimal workflow where possible

## Boundary classification

- [ ] Forge/OAuth/webhook
- [ ] Server/database
- [ ] Agent registration/scheduling
- [ ] Backend/container/pod
- [ ] Checkout/network/credentials
- [ ] Workflow syntax/condition
- [ ] Application or test command

## Recovery notes

- Root cause:
- Smallest fix:
- Verification command:
- Remaining risk:
