# Restore drill: [repository/source class]

## Objective
- Date/time and operator:
- Recovery objective tested:
- Selected snapshot ID, host, paths, and tags:
- Why this snapshot was selected:

## Preconditions
- [ ] Separate, empty restore target:
- [ ] Sufficient target disk space:
- [ ] Repository/password access tested without exposing secrets:
- [ ] Application/vendor recovery procedure available, if applicable:

## Commands
```sh
restic snapshots --host [host] --tag [tag]
restic ls [snapshot]
restic restore [snapshot] --target [separate-target]
```

## Evidence
- Restore exit code and duration:
- File-level checks performed:
- Ownership/permissions/xattrs checks performed:
- Application/database validation performed:
- Checksum or content sample evidence:

## Result
- [ ] Passed
- [ ] Failed
- [ ] Partial; limitation recorded below

## Findings and follow-up
- Gap:
- Owner:
- Due date:
- Next drill date:
