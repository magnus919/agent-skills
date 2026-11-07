# Tool-service trust and containment

Load when a harness exposes local tools over a service, mixes native file handlers
with sandboxed commands, or launches integrations from project configuration.
Harness engineering owns the runtime contracts and acceptance evidence. Use
[secure software engineering](../../secure-software-engineering/SKILL.md) for
threat modeling and implementation details; this is not an exploit runbook.

## Trace every execution path

Follow a requested operation from transport admission through authorization to the
process that performs the effect. Record actual enforcement, not a tool name or
an advertised sandbox mode:

| Path | Record before claiming containment |
|---|---|
| Native read/edit/create handler | Server identity; allowed roots; read/write policy; path-resolution and symlink boundary; enforcement at the actual file operation |
| Shell command | Effective user; mounts/read/write scope; inherited environment/credentials; network policy; subprocess inheritance |
| Helper, integration or child process | Which controls propagate; shared services/handles; any host-side effect performed outside the command sandbox |
| Listener and callback route | Bind/reachability; authenticated caller; authorized operation/resource scope; session lifetime and revocation |

Mark missing guarantees unknown. A shell sandbox does not constrain a file handler
running directly in the host server; a worktree does not isolate secrets or egress.
Read-only host access can still expose confidential data. Review resource
resolution and enforcement with the security owner, including path changes between
validation and use. Do not claim a string-prefix or initial path check alone is a
complete filesystem boundary.

## Authenticate service callers before dispatch

Choose the smallest reachable surface the workflow needs. Document the listener's
bind address, transport and intended callers, including other local users/processes
and browser origins where applicable. Loopback, random ports and conversation IDs
are routing properties, not caller authentication. A private network is a separate
exposure control.

Authenticate each request at the trusted service boundary, then authorize the
current caller/session for the exact operation, workspace/resource and task scope.
Do not trust a supplied thread ID as ownership. Bind grants to the intended service
and lifetime; recheck expiry/revocation after reconnect. Keep credentials outside
model context and logs, following [credential/session authority](credential-session-authority.md).
Reject missing credentials, wrong caller/resource bindings and expired grants
before tool effects; return a non-secret denial. Apply this contract to ordinary
file/command routes as well as asynchronous callbacks. Changing to a remote
transport requires a new exposure and identity review.

## Trust configuration before process activation

Treat project-defined executable, argv, environment, working directory and
integration endpoints as executable input. Discover/parse configuration without
starting the declared processes. Resolve its source and effective merged values,
then check existing user/organization authorization for those concrete capabilities.
When authorization is missing, present the effective launch and scope for trust
review before activating it; do not ask again when current authorization covers it.
A checked-out config file or a valid schema is not an execution grant.

Bind activation to the reviewed configuration identity and launch scope. Recheck
when executable arguments, environment, source revision or endpoints change;
reject scope expansion under a cached trust decision. Keep ambient credentials
and privileges limited to the integration's needs. State precedence between user
and project configuration so project values cannot silently broaden an approved
launch. Restore/reconnect must revalidate trust rather than boot processes merely
because conversation history references them.

## Challenge the actual boundaries

Use disposable fixtures and invented canaries, with authorized probes only:

| Challenge | Required observable evidence |
|---|---|
| Missing credential, wrong workspace or expired caller grant | Service rejects before file changes or process launch; response/stream/artifact bytes contain no protected synthetic canary (nor logs if emitted); correct authorized call still works |
| Absolute, parent-relative and symlink paths through every native file route | Out-of-scope read/write is denied at the operation boundary; allowed workspace operation succeeds |
| Shell/helper/child access to a synthetic secret and controlled network sink | Observe actual denied/allowed reads and destination traffic for each claimed policy; shell success says nothing about native handlers |
| Untrusted project config, then authorized launch, then scope-changing config | No process before trust; expected process after authorization; changed capabilities do not reuse the old grant |

Record tested path, configuration/revision, OS/runtime, effect oracle and remaining
unknowns. A proposed probe or fixture pass is not proof for an installed backend.
Stop deployment claims when a required boundary is unknown or contradicted; retain
the failing path and accountable repair owner. Do not compensate for one denied
route by silently retrying through a less constrained handler.

Use the [assertion challenges](../evals/tool-service-challenges.md) to review
satisfying, contradictory and missing-evidence answers separately from execution.

## Source scope

The Infinity audit motivated these checks; these are established security
principles applied to harness architecture, not inventions attributed to Infinity.
At commit `1abc6fcff1f186124f924b56aa92c3a3684c90c5`, static review identified
an all-interface [local listener](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-local/src/server.rs),
host-side [file routes](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-core/src/server.rs),
separate [command sandboxing](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/sandbox-local/src/backend.rs),
and [configuration-driven process launch](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-daemon/src/rap_servers.rs).
These paths motivate checking caller authentication, filesystem containment,
read/egress guarantees and activation trust independently. No exploit, live
exposure, packet capture or complete dependency audit is claimed. Earlier
[design findings](infinity-design-findings.md#s13--tool-session-and-workspace-lifetime)
explicitly excluded full backend security assessment; this reference does not
retroactively expand that investigation's scope.
