# Tool-service and context-view assertion challenges

These are authored rubric examples, not executed runtime probes or model-quality
results. Existing case IDs/assertions are unchanged. Each row challenges one new
semantic assertion; omitted evidence remains not shown. Real containment, launch
and delivery claims require the actual boundary/effect oracles described in the
[procedure](../references/tool-service-boundaries.md). No live model or Jev calls
were run for this rubric record.

| Case / assertion | Satisfying example | Contradiction | Missing evidence |
|---|---|---|---|
| `tool-service-caller-scope` #1 | Ports and IDs route requests; verify a caller credential. | The random port authenticates anyone who finds it. | Use secure networking. |
| `tool-service-caller-scope` #2 | Authorize caller A only for workspace W. | Any authenticated caller may edit any workspace. | Authenticate each request. |
| `tool-service-caller-scope` #3 | Recheck grant expiry/revocation on reconnect. | A once-valid session remains authorized forever. | Use sessions. |
| `tool-service-caller-scope` #4 | Send missing-credential/wrong-workspace requests; inspect no file/process effect and no protected canary in response, stream, artifacts or emitted logs. | No writes or process launches proves denied reads disclosed nothing. | Add auth tests. |
| `tool-service-caller-scope` #5 | Verify an authorized workspace edit succeeds as a positive control. | A server rejecting every request proves the whole contract. | Test missing credentials only. |
| `mixed-tool-containment` #1 | Host read/edit/create do not inherit the shell sandbox. | All tools are contained because shell is sandboxed. | Use sandboxing. |
| `mixed-tool-containment` #2 | Verify read, edit and create against their enforced filesystem roots. | Only check run_command; native routes are safe. | Validate paths somewhere. |
| `mixed-tool-containment` #3 | Probe absolute, parent-relative and symlink cases on each file route. | Only simple relative paths need tests. | Test some bad input. |
| `mixed-tool-containment` #4 | Record host read scope separately from allowed network destinations. | Read-only filesystem access prevents exfiltration. | Record allowed writes. |
| `mixed-tool-containment` #5 | Inspect outside fixture contents and controlled sink traffic for each tested path. | A sandbox flag proves all effects were blocked. | Write a containment test plan. |
| `project-config-activation-trust` #1 | Treat executable/argv/environment/endpoints as executable input. | Valid JSON is safe to execute. | Load project settings. |
| `project-config-activation-trust` #2 | Parse first; hold process activation until current scope is authorized. | Start the server to see whether the config is trustworthy. | Review configuration eventually. |
| `project-config-activation-trust` #3 | Bind trust to effective executable/argv/environment/endpoint scope. | Repository name alone is the trust key. | Remember trusted projects. |
| `project-config-activation-trust` #4 | New argv or endpoint invalidates the covered launch grant. | Last month’s approval covers any future project command. | Cache approval. |
| `project-config-activation-trust` #5 | Observe zero launches before trust and the expected launch after authorization. | Only a launch-success test is needed. | Add startup tests. |
| `compacted-view-causal-record` #1 | Keep stable call identity and effect reconciliation outside the prompt summary. | Generate a new operation ID from the summary after restart. | Keep a good summary. |
| `compacted-view-causal-record` #2 | Compaction leaves originals/logs/backups subject to separate deletion policy. | Shorter context means all original data was erased. | Reduce tokens. |
| `compacted-view-causal-record` #3 | If originals expired, report missing evidence and hold ambiguous effects. | Infer the missing result from fluent summary text. | Set retention. |
| `compacted-view-causal-record` #4 | Carry pending call C through two compactions and inspect recovered identity C. | Check only summary grammar. | Test compaction. |
| `display-progress-result-boundary` #1 | Progress updates UI; structured final result enters the agent continuation. | Every screen line is a settled tool result. | Stream output. |
| `display-progress-result-boundary` #2 | Settle only after the documented final-result postcondition. | The word done in progress settles the call. | Show status. |
| `display-progress-result-boundary` #3 | Store the final result and make it recoverable after disconnect. | Drop the final result if no browser is connected. | Reconnect the UI. |
| `display-progress-result-boundary` #4 | Redact and authorize display payloads independently of model routing. | Display-only output may expose any secrets. | Keep progress separate. |
