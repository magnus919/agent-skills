# Effect and recovery qualification matrix

Record tool/release/commit, current intent revision, environment, authorized scope,
rollback owner, evidence location, and whether each row is proposed, source-read,
test-read, executed or observed. Do not turn a test name into a passing receipt.

| Transition / entry paths | Durable record and atomic set | External effect / uncertainty window | Recipient generation / final check | Retry identity / reconciliation | Recovery authority / forbidden advancement | Failure injection / negative control | Exact evidence / result / coverage |
|---|---|---|---|---|---|---|---|
| Transfer work | Source closure + successor + wake intent | Crash after commit before dispatch | Current claimant and execution | Same intent; inspect ledger before resend | Restore liveness, preserve acceptance owner | Crash boundary; ordinary non-workflow item | |
| Delayed delivery | Accepted/retained intent | Paste then submit; human input or replacement | Bound occupant/pane; check at final write | Preserve uncertain effect, no blind replay | Cleanup permission does not grant input | Replacement after await; sibling unaffected | |
| Workflow completion | Frontier and acceptance evidence | Convenience route bypass | Authorized actor and current task revision | Reconcile accepted state before retry | Only designated transition can advance | Direct queue closure; terminal workflow | |
| Health diagnosis | Evidence basis and coverage | Alert/repair may amplify traffic | Current diagnosis owner | New basis invalidates old disposition | Suspicion cannot authorize repair | Truncated history; legitimate review burst | |
| Context/package transfer | Manifest, resolved refs and declared files | Import/launch outside archive assembly | Recipient grant and host resources | Re-resolve overrides; reject escapes | Producer defaults do not grant authority | Same-name collision; escaping symlink | |

For each executed challenge: record setup, expected invariant, exact revision,
actual state and side effects, pass/fail/blocked/inconclusive, and cleanup receipt.
Unobserved outcomes remain unknown. Qualify actual startup and post-compaction
retrieval separately from pack discovery. Measure accepted product change separately
from transitions, proofs and diagnostic activity; report omitted observation scope.
