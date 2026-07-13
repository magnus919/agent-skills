# Accessibility Implementation Review

- [ ] Native HTML provides the primary semantics; ARIA is used only where necessary and does not duplicate or contradict it.
- [ ] Controls have intended computed role, name, state, value, and relationships in each key state.
- [ ] Keyboard entry, operation, reverse navigation, exit, escape/cancel, focus visibility, and restoration work.
- [ ] Modal background is unavailable/inert without hiding the dialog's ancestor or applying `aria-hidden` to a backdrop.
- [ ] Forms use visible labels and native semantics where appropriate; error behavior is contextual and recoverable.
- [ ] Responsive navigation remains ordinary links unless an application-menu keyboard contract is implemented.
- [ ] Composite widgets have the full documented contract and no role-pattern mixing.
- [ ] Adaptive layout, motion, media, target exceptions, and drag alternatives are implemented where applicable.
