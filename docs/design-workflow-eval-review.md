# Design workflow eval challenge review

New cases supplement existing stable cases. No existing IDs or rubrics changed.
These are authored challenge fixtures for reviewer discrimination, not model runs,
human-adjudicated labels or measured behavioral improvement. Each row aligns with
the corresponding assertion index (1-based). Semantic assertions remain manual review.

| Skill / case / assertion | Satisfying example | Contradictory near miss | Missing evidence |
|---|---|---|---|
| product-design-and-ux / reference-led-flow-exploration / 1 | Use the first reference for spacing and assess the second for sequence. | Copy the first reference wholesale. | Says only that both references look useful. |
| product-design-and-ux / reference-led-flow-exploration / 2 | Create an editable three-step wireframe with skip/recovery states. | Only generate a flat final image and declare the flow done. | No artifact is proposed. |
| product-design-and-ux / reference-led-flow-exploration / 3 | Owner preference is established; usability remains untested. | The preferred reference proves this onboarding is usable. | No evidence status is stated. |
| product-design-and-ux / scoped-design-approval / 1 | Retain v3 sequencing; confirm where optional invitation enters and rejoins. | Replace the approved flow with a new five-step flow without review. | Does not discuss the approved sequence. |
| product-design-and-ux / scoped-design-approval / 2 | Illustration remains proposed. | Prototype approval makes the illustration canonical. | Omits illustration status. |
| product-design-and-ux / scoped-design-approval / 3 | Record v3, sequence-only approval and invitation as pending. | Approved: the entire design system. | No durable approval record is offered. |
| brand-designer / rough-brief-to-style-guide / 1 | Compare two compact directions with different typography and contrast. | First fill in every brand template and specify exact fonts and CMYK. | No exploratory artifact or approach is given. |
| brand-designer / rough-brief-to-style-guide / 2 | Keep generous spacing and compare readable text treatments. | Use the reference unchanged, including pale text. | The reference feedback is not discussed. |
| brand-designer / rough-brief-to-style-guide / 3 | This is visual guidance; behavior/components need their own work. | These color swatches are your complete design system. | Only labels the output brand documentation. |
| brand-designer / approved-mockup-vector-boundary / 1 | Reuse approved layout within its scope; global standard is not approved. | Make the entire mockup the permanent standard. | Approval scope is not discussed. |
| brand-designer / approved-mockup-vector-boundary / 2 | An embedded bitmap remains raster; create editable paths for vector delivery. | Saving the PNG inside SVG makes it a vector logo. | No distinction between raster and vector is made. |
| brand-designer / approved-mockup-vector-boundary / 3 | Logo remains a proposal pending review. | The approved mockup implicitly approves the logo. | No logo approval status is given. |
| frontend-engineering / reuse-approved-dashboard-components / 1 | Map new columns to DataTable and filters to FilterBar; inspect missing sorting behavior. | Keep the freshly generated replacements just because they look better. | No component mapping is stated. |
| frontend-engineering / reuse-approved-dashboard-components / 2 | Compare v4 with rendered long-name fixtures at narrow and wide widths. | Approve fidelity from source-code inspection alone. | No comparison to v4 is described. |
| frontend-engineering / reuse-approved-dashboard-components / 3 | Exercise keyboard sorting, loading and error fixtures. | Only test the populated mouse-driven desktop screen. | Verification states are omitted. |
| frontend-engineering / cheaper-model-design-continuity / 1 | Freeze brief and reference v2 for both candidates. | Give the larger model a detailed reference and the local model only a slogan. | No common inputs are specified. |
| frontend-engineering / cheaper-model-design-continuity / 2 | Measure generation plus reviewer and correction time. | Token price alone proves lower total cost. | No cost basis is described. |
| frontend-engineering / cheaper-model-design-continuity / 3 | Both equivalence and savings remain unmeasured. | The local model is proven equivalent and cheaper. | Does not distinguish proposal from observed result. |
