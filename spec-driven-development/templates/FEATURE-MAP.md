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

## Example: settings to export

These illustrative entries share a seeded profile with two known rows and a
requirement that users select the columns applied to future downloads.

| User language / feature | Entry and setup | Action and expected transition | Reusable driver / evidence | Requirement / owner |
|---|---|---|---|---|
| “Remember my export columns” | Settings → Export columns, disposable profile with optional reference column off | Enable the column, save, and reopen the same profile. The preference remains enabled. On a rejected save the prior value remains. | Drive the normal settings path and capture the acknowledgement and reopened value. | EX-1, settings owner |
| “Include the reference column in my CSV” | Reports → Download CSV, reopened profile with the same two seeded rows | Download the CSV. The optional column follows the saved preference and the file still contains both expected rows. Repeat with the option off as a control. | Retain and parse the file outside the profile. Compare header and row identities with the fixture. | EX-2, export owner |
| “Download from the scheduled export panel” | Scheduled exports entitlement | Exercise that entry point if it is in the accepted scope. | If the entitlement is unavailable, record the blocked path and prerequisite in the review record. | EX-3, scheduled exports owner |

Keep paths and driver references fresh when UI labels or contracts change.
Use a disposable profile or fixture for writes. Record candidate, environment,
and exact observed outcome in the review record rather than on this map.
