# Recovery Classification

Deep reference on the four recovery paths with decision rules, examples, and
anti-patterns. Load this reference when classifying recovery for concrete
migration steps.

## The four recovery paths

### Rollback

Reverse to the prior state by undoing the change.

**Decision rule:** Rollback is possible when the old state still exists and can
be reactivated, OR the change is purely additive and can be removed without side
effects.

**Examples:**
- Undo a feature-flag-controlled code path by turning off the flag.
- Restore read traffic to the old database by reverting the connection string.
- Drop a newly added nullable column that is not yet consumed.
- Cancel a deprecation notice and keep the old API endpoint live.

**Anti-patterns:**
- Claiming rollback is possible because "we can fix it in the next deploy."
  That is roll-forward, not rollback.
- Claiming rollback is possible when the old system has been decommissioned.
  That is restore or irreversible.

### Roll-forward

Fix forward in the new state. The old state is no longer reachable, but a fix
can be deployed to the new system.

**Decision rule:** Roll-forward is the correct path when (a) reversal is
impossible or more expensive than fixing forward, AND (b) a fix can be deployed
within the acceptable recovery window.

**Examples:**
- A data migration cutover has completed and the old store is read-only; a bug
  in the new service is discovered. Deploy a fix to the new service.
- An API migration has removed the old endpoint; a consumer reports a
  regression. Fix the new endpoint.
- A configuration error in the new infrastructure is causing errors. Correct
  the configuration and redeploy.

**Anti-patterns:**
- Using roll-forward as the default recovery path without assessing whether
  rollback is simpler and safer.
- Failing to define the acceptable fix-forward window (how long can the system
  be degraded before the fix lands?).

### Restore

Restore the prior state from a backup or snapshot.

**Decision rule:** Restore is the path when the old system is no longer
operational but a backup exists and a restore procedure is tested and has a
known recovery time.

**Examples:**
- A schema migration dropped the wrong table; restore from the pre-migration
  backup.
- A data migration corrupted the target store; restore the target from the
  pre-migration snapshot and re-run the migration.
- An infrastructure migration destroyed the old environment; restore from the
  infrastructure-as-code state and redeploy.

**Anti-patterns:**
- Assuming restore is possible because "we have backups." A backup that has not
  been tested with a restore drill is not a recovery path — it is a hope.
- Failing to define the Recovery Time Objective (RTO) and Recovery Point
  Objective (RPO) for the restore.

### Irreversible

Reversal is impossible. The change cannot be undone at any level.

**Decision rule:** Irreversible when (a) the old state is physically destroyed,
(b) the operation is one-way by design (e.g., cryptographic erasure), or (c) a
third-party action cannot be recalled.

**Examples:**
- Physical hardware decommissioning where the device is shipped back and
  wiped.
- Cryptographic key rotation where old keys are destroyed after rotation.
- Third-party data export where the receiving party cannot be compelled to
  delete the data.
- Permanent data deletion to satisfy a regulatory requirement (e.g., GDPR
  right-to-erasure).

**Required for every irreversible step:**
1. **Acceptance criteria** — what conditions must be met before the
   irreversible step is executed (e.g., "reconciliation passed at 100% for 7
   consecutive days").
2. **Stakeholder communication** — who must be informed and who must approve
   before the step executes.
3. **Contingency plan** — what happens if the irreversible step succeeds but
   the overall migration subsequently fails (e.g., "rebuild from source of
   truth," "accept data loss within defined scope").

**Anti-patterns:**
- Treating an irreversible step as if it were reversible — stating "rollback:
  N/A" without the acceptance, communication, and contingency requirements.
- Claiming "irreversible" for a step that is merely expensive or inconvenient to
  reverse. Irreversible means physically or logically impossible, not merely
  costly.

## Classification decision tree

```
Can the old state be reactivated without data loss?
  ├── YES → Rollback is possible
  └── NO:
      ├── Can the new state be fixed within the acceptable recovery window?
      │   └── YES → Roll-forward is possible
      └── Can the old state be restored from backup?
          ├── YES, and restore procedure is tested → Restore is possible
          └── NO → Irreversible
```

## When not to claim rollback

Never claim rollback is possible when:
- The old system has been decommissioned and cannot be restarted.
- The old data has been deleted and no backup exists.
- The old API has been removed and cannot be redeployed.
- A third-party action cannot be reversed.
- The rollback procedure has never been tested.

In these cases, classify as roll-forward, restore, or irreversible — not as
rollback with caveats.
