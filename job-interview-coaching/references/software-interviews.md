# Software, infrastructure, and security interviews

## Basis and task selection

[Microsoft technical interview guide](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing.html) describes problem solving, design, coding, and testing. The official McDowell book overview supports concept-based preparation; neither establishes every employer's format.

Establish coding versus system design versus troubleshooting, permitted language/tools, whether execution is available, and the actual scope. A junior role may emphasize implementation and tests; a senior specialist may need architecture and cross-team tradeoffs. Security work may add threat analysis, but do not assume security certification or attack authorization from an interview prompt.

## Evidence to develop

Use a small implementation, a failure investigation, and a retrospective decision. A technically correct result and a clear explanation are separate evidence. In coding, inspect actual code and checks before claiming correctness. In design, elicit requirements before introducing components. In troubleshooting, ask which observation discriminates among hypotheses.

## Worked contrast

Original synthetic question: **Implement a function that returns the first repeated customer ID from a sequence. What should it return when no ID repeats, and does input order matter?**

Weak example: “I would use a hash map because it is fast. It should work for everything.”

Stronger example using different, explicitly fictional facts: “I would clarify that first means the first repeated occurrence while scanning left to right, then use a set of IDs already seen. I would return the agreed sentinel if no ID repeats. I would test empty input, a repeat near the start, and distinct values. Memory grows with the number of distinct IDs.”

The stronger answer resolves the meaning of first, describes a coherent approach, and identifies tests and a resource tradeoff. It still does not prove an implementation works. In a coding round, the next step is actual code. A different interpretation is valid if explicitly agreed; do not grade by keyword matching.

Use this contrast to explain evidence quality, not to put fictional achievements into the user's answer. For a real transcript, any improved autobiographical answer must use only supplied or subsequently confirmed facts.

## Neutral probes

- What observation or test would show that your interpretation is wrong?
- What changes if the input cannot fit in memory?
- Which part of the production incident did you personally investigate?

## Candidate practice

First implement the small task without hints. Then explain a counterexample and revise. For system design, practise a two-minute requirements discussion before drawing components. For an incident story, separate symptom, evidence, hypothesis, action, verification, and later prevention. Track whether a hint supplied the algorithm.

Transfer task: Change “first repeat” to counting repeats, or change latency/cost requirements in a design. Ask the candidate to explain what changes and what remains valid.

Keep the baseline, coached retry, and independent transfer attempt distinct. Ask one question at a time and wait. If the user wants a simulation, withhold coaching until the agreed debrief. If they want an explanation or plan, do not force a mock.

## Responsibility-level adaptations

Trainee: understand a bounded problem and learn from feedback. Independent engineer: deliver and test within constraints. Senior IC: evaluate alternatives and system consequences. Manager: explain how the team reached and maintained quality; do not require the manager to claim every design decision.

A title alone is insufficient. Ask what independence, complexity, impact, and decision authority the role actually requires. Early-career candidates may use relevant education, voluntary, caring, or project evidence; experienced candidates should explain the scope and limits of their contribution.

## Interviewer practice and candidate experience

State whether compilation, documentation, and AI assistance are allowed. Use comparable problem difficulty and a recorded hint policy. Score correctness, reasoning, verification, and collaboration separately. Do not infer competence from terminology or eliminate a candidate for not choosing your favorite design when alternatives satisfy the stated constraints.

For interviewer coaching, rehearse the probes against both a vague and a concrete answer. Record what evidence the question elicited, what remains missing, and whether a hint supplied the response. A friendly conversation is not itself a complete assessment. Give candidates space to understand the work and ask informed questions.
