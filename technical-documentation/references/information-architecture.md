# Organize documentation around what the reader needs to do

Start with the reader's situation and the result they need. The same
product can require different documents at different moments.

| Reader's need | Shape | Evidence the page works |
| --- | --- | --- |
| Learn a skill by doing it | Tutorial | A new reader completes a safe, worked path and can recognize each meaningful result. |
| Complete a real task they already understand | How-to | A reader with the stated prerequisites reaches the outcome and knows what to do when the common path branches or fails. |
| Look up an exact contract | Reference | Names, defaults, accepted inputs, outputs, limits, and errors match the authoritative version. |
| Understand how something fits together or why it works that way | Explanation | The reader can describe the mechanism and tradeoff. Recorded rationale is distinguished from inference. |

Give each substantive section a clear job. A README can orient, offer a
short quickstart, and link to dedicated docs. A how-to can explain a decision
in a sentence when it changes what the reader should do. Split material only
when it interrupts the current task or creates a second place to maintain the
same contract.

## Example: scheduled exports

- **Tutorial:** create one export in a sandbox and open the resulting file.
  Give a sample input and show how to recognize the first successful result.
- **How-to:** resume a failed nightly export without duplicating it. Put the
  required access and checks up front; distinguish resuming from rerunning.
- **Reference:** describe the retry setting, including its default, limits,
  and errors, using the versioned schema and tests.
- **Explanation:** show why retrying and publishing use separate steps and
  what tradeoff that creates. Cite the system's decision record when claiming
  that was the maintainers' rationale.

## Keep a growing site navigable

Use task names and terms readers actually search for in titles and headings.
Link from a guide to the authoritative contract when a field or operation
first matters. Use landing pages to route readers rather than copy a contract.
Check links and key entry paths; give each public promise an owner and a
source that can be verified after a change. Before moving or retiring a page,
check inbound links and preserve redirects where the old address is in use.

The four reader needs are drawn from [Daniele Procida's Diátaxis
compass](https://diataxis.fr/compass/).
