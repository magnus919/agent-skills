# Composite Widgets

Custom tabs, comboboxes, listboxes, grids, tree views, toolbars, sliders, radio groups, and application menus have a complete contract: role, name, state/value, relationships, keyboard commands, focus model, pointer behavior, disabled behavior, error/recovery behavior, and announced changes.

## Decision Path

1. Can a native element or ordinary disclosure solve the user task?
2. Can a maintained component in the selected stack meet the requirements and support target environments?
3. If custom behavior is necessary, use [APG](https://www.w3.org/WAI/ARIA/apg/) as informative pattern guidance, document the whole contract, and test the audience-relevant browser/AT combinations.

## Pattern Contracts

| Pattern | Minimum contract to define and verify |
|---|---|
| Tabs | `tablist`, named `tab` controls, `tabpanel` relationships, one selected tab, roving Tab stop, Left/Right navigation for horizontal tabs, orientation-aware keys, Home/End where supported, and manual versus automatic activation chosen from loading latency and task behavior. |
| Combobox | Named input or button, synchronized expanded state, popup role and relationship, current option/value, editing behavior, filtering, selection, Escape/close behavior, and either DOM focus or `aria-activedescendant` managed consistently. |
| Listbox | Label, options, single/multiple selection model, active option, arrow navigation, type-ahead where useful, selection-follow-focus decision, and entry/exit behavior. Do not use it for ordinary links or checkboxes. |
| Application menu | Named menu button, expanded state, `menu`/`menuitem` structure, arrow-key movement, Home/End, Escape, focus entry/return, and activation. Ordinary site navigation is not this pattern. |
| Grid/tree | Row/item structure, selection versus focus, roving or active-descendant model, directional navigation, editing mode, announcements, and a practical alternative if the interaction is too complex. |

APG key assignments describe a pattern contract, not a reason to implement it. Account for writing direction and orientation, and do not make every descendant a Tab stop when the adopted composite pattern uses arrow-key navigation.

Do not mix roles from different patterns or add ARIA roles merely to style an ordinary list. Accessibility-tree inspection and task testing are required because valid attributes alone do not prove usable interaction.
