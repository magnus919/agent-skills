# Jev release feature selection: rubric review

Case: `jev-release-feature-selection`, added 2026-10-15. No existing case IDs
or historical benchmark evidence changed. These authored response fragments
check whether a reviewer can distinguish met, contradicted, and not shown;
they are not observed inference or held-out quality results.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Alias resolution | Checks official mapping: latest=1.13, preview=1.14 on the stated date; refresh before use | Says latest already means 1.14 because it is newest | Names latest without checking resolution |
| Image transport | Assets map binds a UUID reference used in state; explicit images header | Sends a filename alone as if pixels were uploaded | Says multimodal without a request contract |
| Box model support | Selects preview or 1.14 pin after checking support | Uses stable latest=1.13 for Box without qualification | Omits model selection |
| Box validation | Finite normalized edges and strict left/right, top/bottom ordering checked before crop | Treats normalized values as pixel coordinates | Shows a box but no validation |
| Presence | Noul presence gates whether to use the Box | Treats a returned Box as proof of presence | Never addresses absent objects |
| Context extension | Separate long-context header; evaluate latency and accuracy on target data | Assumes images header enables 262k | Omits context behavior |
| Helper scope | States bundled text probe lacks assets/Box validation and experimental transport | Claims offline probe validates image/Box support | Names probe without describing its limits |
| Qualification | Keeps prototype and vendor claims distinct from measured application outcomes | Claims production accuracy from release announcement | Omits evaluation evidence |
