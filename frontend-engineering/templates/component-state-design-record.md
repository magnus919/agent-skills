# Component / State Design Record

Fill this record when designing a component tree or choosing state ownership
for a feature. It captures the decomposition and the state decisions before
implementation, so reviewers can validate the structure and future
maintainers can see why state lives where it does.

## Feature

- Feature or screen: `[fill: what is being built]`
- Users and primary tasks: `[fill: who uses this and what they accomplish]`
- Entry points: `[fill: routes, modals, or embed points that render this]`

## Component Tree

Sketch the component decomposition:

```
[fill: top-level component]
├── [fill: child component]
│   └── [fill: leaf component]
├── [fill: child component]
└── [fill: child component]
```

- Composition rules: `[fill: which components are reusable vs feature-specific]`
- Props interfaces: `[fill: the props each component takes and why they are minimal]`
- What is NOT a component here: `[fill: repeated markup that should stay a component vs markup that stays inline]`

## State Ownership

| State | Owner | Kind (local / shared / server) | Why here |
|---|---|---|---|
| `[fill: state]` | `[fill: component or context/store]` | `[fill: kind]` | `[fill: justification]` |

- Local state: `[fill: what stays in useState/useReducer inside a component]`
- Shared state: `[fill: what is shared and at what scope (component context, route, global)]`
- Server state: `[fill: what is fetched and cached, and the cache/invalidation strategy]`

## Data Fetching

| Data | Source endpoint | Cache key | Invalidation | States handled |
|---|---|---|---|---|
| `[fill: data]` | `[fill: endpoint]` | `[fill: key]` | `[fill: when it refetches]` | `[fill: loading/error/empty/success]` |

- Optimistic updates: `[fill: which mutations update the cache optimistically and the rollback plan]`
- Race handling: `[fill: how stale responses and rapid re-fetches are handled]`

## Error and Loading UX

- Loading presentation: `[fill: skeletons, spinners, aria-busy usage]`
- Error presentation: `[fill: per-error-state UI, retry affordances, 404 vs 5xx handling]`
- Empty states: `[fill: what renders when data is valid but empty]`

## Accessibility and Responsive Notes

- Keyboard and focus behavior: `[fill: focus management for modals/forms/loading transitions]`
- Breakpoint behavior: `[fill: how the layout adapts and what changes per breakpoint]`

## Testing Plan

- Component tests: `[fill: the interactions and states covered per component]`
- Integration tests: `[fill: flows covered end to end through the component tree]`
- Visual regression: `[fill: which screens are snapshotted]`

## Alternatives Considered

- Alternative 1: `[fill: option considered]` — rejected because `[fill: reason]`
- Alternative 2: `[fill: option considered]` — rejected because `[fill: reason]`

## Open Questions

- `[fill: unresolved decision needing input before implementation]`
