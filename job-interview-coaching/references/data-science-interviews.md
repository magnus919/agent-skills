# Data, analytics, and applied-science interviews

## Basis and task selection

[Amazon applied-scientist preparation](https://amazon.jobs/content/en/how-we-hire/applied-scientist-interview-prep) describes theoretical analysis, modeling assumptions, experimentation, implementation, and behavioral evidence for its roles. Use it as an employer example, not a universal role rubric.

Distinguish analyst, data engineer, data scientist, research scientist, and ML engineer. Obtain whether the task is SQL, experiment interpretation, modeling, pipeline design, or a research discussion. Clarify available data and whether the question is causal, predictive, or descriptive.

## Evidence to develop

Elicit how the candidate defines the decision and unit of analysis, checks data quality, selects a baseline, prevents leakage, evaluates uncertainty, and communicates limitations. For pipelines, add contracts, recoverability, and checks. For research, add hypotheses, ablations, and competing explanations. Do not let interview polish substitute for a sound analysis.

## Worked contrast

Original synthetic question: **A model has high offline accuracy but poor results after launch. How would you investigate?**

Weak example: “I would collect more data and use a bigger model.”

Stronger example using different, explicitly fictional facts: “I would first establish the production failure metric and who is affected. Then I would compare evaluation and production populations, check feature and label availability at prediction time, inspect data processing differences, and examine errors by relevant segment. I would use a baseline and targeted tests before deciding whether model capacity is the problem.”

The stronger answer proposes discriminating investigations rather than assuming a remedy. It does not prove that drift, leakage, or capacity caused the failure. Ask how each hypothesis would be checked and what evidence would change the plan. A concise specific investigation can be stronger than listing every possible ML term.

Use this contrast to explain evidence quality, not to put fictional achievements into the user's answer. For a real transcript, any improved autobiographical answer must use only supplied or subsequently confirmed facts.

## Neutral probes

- What would distinguish a data-pipeline fault from a model limitation?
- Which result would cause you to abandon your preferred explanation?
- What did your experiment establish, and what could it not establish?

## Candidate practice

Give a small synthetic table and ask for the decision, denominator, and caveats before calculating. Rehearse a research explanation for both technical peers and a nontechnical stakeholder. On a retry, remove unnecessary terminology while retaining assumptions. Do not require a numerical effect if none was measured.

Transfer task: Change the failure from average accuracy to one underserved segment, or reveal that a feature is unavailable at decision time. Ask the candidate to update the investigation.

Keep the baseline, coached retry, and independent transfer attempt distinct. Ask one question at a time and wait. If the user wants a simulation, withhold coaching until the agreed debrief. If they want an explanation or plan, do not force a mock.

## Responsibility-level adaptations

Entry: basic analysis and explicit assumptions. Independent: reliable work and validation. Senior: ambiguous objectives, evaluation strategy, and influence. Lead/manager: research portfolio, team review practices, and responsible deployment decisions, rather than taking credit for every model.

A title alone is insufficient. Ask what independence, complexity, impact, and decision authority the role actually requires. Early-career candidates may use relevant education, voluntary, caring, or project evidence; experienced candidates should explain the scope and limits of their contribution.

## Interviewer practice and candidate experience

Separate question understanding, method selection, calculations/code, interpretation, and verification. Provide sufficient data and state permitted tools. Domain reviewers must check specialized statistical claims. Do not reward a causal claim from a simple before/after comparison or call a model correct because the explanation sounds sophisticated.

For interviewer coaching, rehearse the probes against both a vague and a concrete answer. Record what evidence the question elicited, what remains missing, and whether a hint supplied the response. A friendly conversation is not itself a complete assessment. Give candidates space to understand the work and ask informed questions.
