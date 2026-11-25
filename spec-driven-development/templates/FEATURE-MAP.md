# Feature map

A feature map helps a person or agent find and exercise an existing user journey.
Point to its accepted requirements and reusable driver. Do not duplicate the
specification here or imply a mapped journey already passed.

| User language / feature | Entry and setup | Action and expected transition | Reusable driver / evidence | Requirement / owner |
|---|---|---|---|---|
| [What a user calls it] | [Surface, initial state, fixture and permissions] | [Action, observable success, important negative case] | [Exact repo command, artifact and independent readback] | [Spec and acceptance IDs; owning team] |

## Example: saved settings

| User language / feature | Entry and setup | Action and expected transition | Reusable driver / evidence | Requirement / owner |
|---|---|---|---|---|
| “The compact mode setting in the sidebar” | Settings → Appearance; isolated test profile with compact mode off | Turn it on, wait for the save acknowledgement, close and reopen, then confirm the setting is still on. A rejected save must leave the prior state intact and show an error. | Illustrative: `make verify-feature FEATURE=appearance.compact-mode`. Capture the visible state and the test profile's reopened value. The owner replaces this command with the real driver before use. | Example acceptance IDs AP-1 and AP-2; settings owner |

Keep paths and driver references fresh when UI labels or contracts change.
Use a disposable profile or fixture for writes. Record candidate, environment,
and exact observed outcome in the review record rather than on this map.
