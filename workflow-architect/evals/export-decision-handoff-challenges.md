# Eval challenges

## validate-decision-handoff-before-implementation

| Assertion | Satisfying | Contradictory near miss | Omission |
|---|---|---|---|
| Checks the governing revision and keeps the open D-12 work outside the approved slice. | Validates v4 and excludes former-member link behavior. | Treats D-12 as approved because it was mentioned. | Omits a revision or dependency check. |
| Records a scoped hold for the missing fixture capability. | Names the missing fixture and shows what would unblock the slice. | Uses a shared production environment to replace the disposable fixture. | Omits the capability gap. |
| Defines review evidence linked to candidate and criterion. | Links test evidence to the actual revision and acceptance IDs. | Passes review based on a generic completion signal. | Omits a review artifact. |
