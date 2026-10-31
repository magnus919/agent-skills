# Engineer a software factory

Load when recurring requests should flow through an agent-operated production system. A software factory is the system that converts demand into accepted deliverables repeatedly; a director is its conversational coordinator, and a harness is the execution/control infrastructure. A collection of personas or one parallel task is not sufficient. The factory may produce code, documents or creative artifacts. This procedure is source-informed synthesis; see the research brief and source records.

## Start from the production contract

Use templates/factory-charter.md. Name incoming work, customer, input completeness, exclusions, artifact types, delivery surface and acceptance owner. Map intake → clarification → production → integration → acceptance → authorized delivery → feedback. These are responsibility boundaries, not mandatory separate agents. Define rejection, cancellation, quarantine and rollback paths alongside success.

Start with one representative job and a single-agent baseline. Add one coordinator and only the specialists needed for independent context, authority, tools or verification. Stable transformations may be scripts. Adaptive decomposition can coexist with fixed prerequisite, security and release gates. More agents, instructions or tokens do not establish factory maturity.

## Minimal director recipe

1. Inspect host capabilities: permitted delegation, concurrency, asynchronous messaging, interrupt/resume, model selection, durable storage and event visibility. Record unsupported features. A prompt cannot make a blocking host responsive or create a persistent scheduler.
2. Configure startup so the main session discovers the director charter while workers receive only their assignment, applicable shared policies and selected skills. Workers must not accidentally inherit the obligation to recruit a whole factory. Verify this in a fresh session before relying on it; do not hardcode a provider's file layout as universal.
3. Give each assignment the job/attempt ID, accepted requirement version, role revision, input artifact versions, authority, budget reservation, ownership/lease, deliverable and verifier. Use templates/factory-role.md. A skill supplies procedure; a role supplies responsibility; a worker is a particular execution. One role can use multiple skills.
4. Keep director work bounded to intake, clarification, decomposition, dispatch, progress interpretation and integration decisions. Delegate substantial production where that preserves availability. Complete trivial work directly if delegation costs more; explain that choice. Coordinator responsibility includes the integrated outcome even when all workers report done.
5. Establish observable status: current version, owned tasks, verified artifacts, blockers, pending changes, spend and next decision. Choose a bounded cadence or state-change events within the host's capabilities. A heartbeat proves liveness at most; never invent progress, imply a worker adopted a change, or promise continuous availability without testing it.
6. Exercise one job, an in-flight change, lost worker, cancellation and fresh-session recovery. Bind accepted artifacts and checks to exact versions. Finish only at the authorized delivery surface or an explicit blocked disposition with owner and next action.

## Responsibility boundaries and topology

Split when context can be summarized without losing critical constraints, authority differs, or acceptance can be independently checked. Combine decisions that continually invalidate each other. For a poster, concept/copy/date/color may need one coherent brief before artwork and gallery implementation diverge. For software, API contract changes precede dependent implementation. Assign one integration owner and serialize shared contract edits; a shared folder is not a merge strategy.

Put a busy subsystem behind a sub-director only if measured coordination load warrants it. The parent receives a subsystem contract and evidence, not every internal message. Bound depth, fan-out, retries and shared spend; propagate cancellation and narrowed authority to descendants and queued work. No department can expand its ancestor's authority or reset its budget. If the host cannot enforce nesting, flatten or serialize the design and report the limit.

## Production flow and capacity

Set work-in-progress limits at constrained stages, especially verification and integration. Admit a job only with required inputs and capacity/budget; queue the rest visibly. Backpressure upstream when review cannot keep up. Prioritize by accepted business policy; the director cannot invent customer commitments. Track accepted delivery rate, end-to-end lead time, queue age, rework, escaped defects, cancellations, full cost and human interventions. Keep failed and timed-out jobs in the denominator.

Use ai-operating-economics for full cost/value and operational-design for demand and organizational capacity. Do not prescribe headcount, ROI or a universal worker count from this harness recipe. Compare topology on the same representative tasks including integration and review time; faster generation alone is not success.

## Acceptance and safe evolution

Use separate component and integrated acceptance. For creative artifacts, separate factual accuracy, functional delivery and taste; a human/domain owner defines taste criteria. For software, exercise the real user journey and dependency boundaries. Protected scenarios are a useful defense against self-grading, but a model judge is not ground truth and a test double is not live-service acceptance. Keep protected criteria and withheld fixtures outside maker control; verify enforcement rather than listing paths in a prompt.

Role and factory changes are proposals through lesson-to-PR. Version the role, evaluate the motivating failure plus near misses and held-out regressions, authorize promotion and retain rollback. A new role applies to queued/running work only through explicit migration or pinning. One repeated correction can justify investigation; it does not automatically justify a permanent rule or another agent.

## Worked software example

Intake: export invoices, accepted contract v1. Contract owner defines paid/unpaid semantics; implementer produces CSV export; verifier exercises invoice→export; release owner controls delivery. While implementation runs, owner requests v2 currency grouping. Record change C1, identify implementer and verifier as affected, fence v1 integration, obtain v2 acknowledgements and reserve rework within the same budget. Continue unrelated documentation only with explicit unchanged-input evidence. An old v1 export arriving later stays quarantined. Component green plus an old v1 scenario is not v2 acceptance. Use factory-steering.md and the snapshot helper for declaration-level impact screening.

## Exit

Deliver the charter, role/assignment contracts, bounded production flow, versioned artifacts and actual acceptance/recovery evidence for the requested scope. A design-only request ends with a reviewable plan and unverified assumptions. A running factory requires observed host behavior; the bundled reconciliation helper cannot grant production readiness.
