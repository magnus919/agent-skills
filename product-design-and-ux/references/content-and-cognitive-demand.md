# Content, Heuristic Review, and Cognitive Demand

Content is part of behavior. Labels, instructions, status, errors, and confirmation evidence determine what a person understands and can recover from; they are not decoration added after the interaction model.

## Content Contract

For consequential content, record:

- audience, task, decision, and moment of use;
- source and accountable owner;
- terminology and evidence for the chosen label;
- required facts, uncertainty, consequence, and next action;
- state variants such as loading, empty, pending, stale, denied, partial, failed, and complete;
- localization, text expansion, formatting, and fallback behavior;
- review and freshness requirements.

Use the person's domain language unless technical or legal precision requires another term; explain unavoidable specialized language at the point of use. Prefer a concrete action or outcome over a vague label. Error content should say what happened, what was preserved, what the person can do, and where to get help when self-recovery is unavailable. Do not blame the person or claim success before the side effect is known.

Plain language is contextual, not a sentence-length formula. Preserve necessary nuance, risk, and legal meaning. Test whether intended people can find, understand, and act on the content rather than relying on a readability score alone.

## Cognitive Demand Review

Inspect the task for demands created by the design:

| Demand | Questions and possible responses |
|---|---|
| Recall | Must people remember an identifier, rule, prior value, or hidden choice? Keep context visible or make recognition possible. |
| Choice and comparison | Are options distinguishable by consequences that matter? Group or stage only when it preserves overview and comparison. |
| Context switching | Does the task require moving between surfaces, channels, or documents? Preserve state, references, and return paths. |
| Interruption | Can a person tell what is saved, pending, expired, or changed when they return? |
| Error interpretation | Does feedback identify the affected field/action, retained input, consequence, and recovery? |
| Time or attention pressure | Are irreversible actions, expiring state, or background work communicated without forcing premature decisions? |
| Unfamiliar sequence | Is guidance available at the decision point, and can experienced people bypass it safely? |

Reduce unnecessary demand without hiding decisions, removing control, or oversimplifying risk. Defaults can reduce effort but must be safe, visible, reversible where possible, and appropriate to the role. Progressive disclosure can reduce scanning but becomes harmful when it hides consequence, status, or recovery.

Do not use a magic limit for steps, options, or memory. The stopping criterion is whether the task's demands are supported in the actual context and whether evidence exposes avoidable confusion or recovery failure.

## Heuristic Review as a Hypothesis Generator

Use these prompts to find questions, not to issue a usability verdict:

- Is system status timely and truthful, including pending and partial work?
- Does language match the domain and distinguish neighboring concepts?
- Can people cancel, undo, recover, or understand why they cannot?
- Are similar actions consistent without forcing unlike tasks into one pattern?
- Does the design prevent consequential mistakes at the right boundary?
- Is necessary context visible rather than dependent on memory?
- Can frequent and infrequent users complete the task without blocking each other?
- Is every piece of content relevant to the current decision or recovery?
- Do errors preserve work and provide a specific correction or support path?
- Is help available where the domain cannot make the task self-explanatory?

For every finding, identify the task, state, evidence, risk, affected role, and contract change. A heuristic match without task evidence is a review lead, not proof. Validate consequential findings through the appropriate evidence path: source review, domain/policy review, accessibility evaluation, authorized usability work, or deployed-boundary observation.
