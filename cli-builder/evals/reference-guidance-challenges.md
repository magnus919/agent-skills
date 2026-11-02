# Reference-guidance assertion challenges

New cases only; existing IDs and assertions are unchanged. These author-reviewed examples clarify semantic rubrics; they are not model execution, independent adjudication or release evidence.

| Case/assertion | Satisfying | Contradictory near miss | Not shown |
|---|---|---|---|
| documented-command-grammar/1 | Reject unknown oneshot where a verb is required. | Treat oneshot as arbitrary positional and stop. | No oneshot disposition. |
| documented-command-grammar/2 | First list is label value, second is verb. | First list is a verb despite option arity. | No parse for the example. |
| documented-command-grammar/3 | Reject deploy --profile because propagation is absent. | Accept all ancestor flags everywhere. | No scope decision. |
| command-check-coverage/1 | Report multiline exclusions and checked-span count. | Ignore multiline examples while claiming full coverage. | No extraction coverage. |
| command-check-coverage/2 | Unknown quoting remains unresolved or fails required check. | Unknown quoting passes. | No unsupported-syntax state. |
| command-check-coverage/3 | Offline pass applies to captured version; live check pending. | Old capture proves installed version works. | No version boundary. |
