# Pedagogy evidence and its limits

Evidence checked 2026-10-15. This is a focused design review, not a systematic
review or evidence that Teach Me improves human learning. The workflow combines
research-informed principles with testable product defaults. Sources below ground
teaching choices; each actual lesson still needs separate subject evidence.

## Source-level findings and decisions

| Source and inspected scope | Finding retained | Design implication and limit |
|---|---|---|
| [Roediger & Karpicke (2006), university-hosted abstract](https://profiles.wustl.edu/en/publications/test-enhanced-learning-taking-memory-tests-improves-long-term-ret/) | In prose-learning experiments, testing benefited delayed recall relative to repeated study; the immediate comparison differed. | Invite retrieval and separate immediate performance from later retention. Does not establish transfer or an optimum for every task. |
| [Cepeda et al. (2006), university-hosted abstract](https://digitalcommons.usf.edu/psy_facpub/1771/) | Distributed-practice review found that useful spacing depends jointly on the study and retention intervals. | Offer later review matched to the goal; no universal schedule or automatic reminder. Evidence concerns verbal recall. |
| [Renkl & Atkinson (2003), article](https://doi.org/10.1207/S15326985EP3801_3) | Fading worked steps bridges example study and independent problem solving. | Use examples and progressively remove support. Publisher full text was inaccessible in the initial check; the accessible KLI review below independently supports this design. No universal fading threshold is asserted. |
| [Koedinger, Corbett, & Perfetti (2012), KLI, sections 5–6](https://pact.cs.cmu.edu/pubs/Koedinger,%20Corbett,%20Perfetti%202012-KLI.pdf) | Instruction interacts with the knowledge component being learned. The review discusses feedback, worked examples, self-explanation, and changing support as expertise grows. Self-explanation may need prerequisite knowledge or training. | Match the move to the task and observed gap; do not force explanations for every simple association. A framework and review, not validation of this chat policy. |
| [Kalyuga et al. (2003), publisher record/abstract](https://doi.org/10.1207/S15326985EP3801_4) | Support useful to less experienced learners can become redundant as expertise grows. | Compress scaffolding after demonstrated success. Expertise is local, not a permanent identity; much evidence concerns structured cognitive tasks. |
| [Koedinger & Aleven (2007), author-hosted paper](https://pact.cs.cmu.edu/koedinger/pubs/paper%20%2314.pdf) | Providing and withholding information creates an assistance dilemma. | Respond to the learner's need for a cue or explanation; a universal hint ladder is not established. |
| [Wisniewski, Zierer, & Hattie (2020), meta-analysis](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.03087/full) | Feedback effects vary; information content matters. | Correct the specific task or strategy gap. Neither generic praise nor longer feedback guarantees benefit. |
| [Pashler et al. (2008), review](https://doi.org/10.1111/j.1539-6053.2009.01038.x) | Evidence necessary to justify matching teaching to assessed learning styles was largely absent. | Honor accessibility and requested formats without assigning fixed learning types. This does not imply representations are interchangeable. |
| [IES/WWC (2007), practice guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/1) | Recommends spacing, alternating worked examples and exercises, and explanatory questioning with differing evidence ratings. | Choose practices conditionally; selectively mix usable, confusable procedures to exercise method choice. This is not a mandate for random topic switching. |
| [Soderstrom & Bjork (2015), author-hosted review](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/11/soderstorm_ra_learningvsperformance.pdf) | Observed performance during instruction and durable learning can diverge. | Report assisted performance, independent application, transfer, and delayed retention separately. No invented mastery percentage. |

## AI tutoring evidence is bounded

- [Maurya et al. (2025), MRBench](https://aclanthology.org/2025.naacl-long.57/):
  the inspected abstract describes a taxonomy of eight pedagogical dimensions and
  human annotations for mathematical tutoring conversations. Useful for evaluating
  tutor responses; response ratings are not measurements of durable learner gains.
- [Kestin et al. (2025), trial and methods](https://www.nature.com/articles/s41598-025-97652-6):
  a custom tutor in two undergraduate physics lessons produced stronger immediate
  post-test results than the study's active-learning comparison. It used carefully
  designed content and assessment. It does not validate arbitrary prompts, all
  domains, long-term retention, or this skill.
- [Bastani et al. (2025), author-hosted manuscript](https://hamsabastani.github.io/education_llm.pdf),
  [journal DOI](https://doi.org/10.1073/pnas.2422633122): the high-school mathematics
  experiment distinguishes assisted performance from later unaided performance;
  teacher-informed tutor safeguards mitigated the harm observed with unguarded
  assistance. The author manuscript was inspected in the supporting research;
  publisher/PMC full-text retrieval did not succeed. Do not claim every manuscript
  detail was checked against the final journal version. Different interventions,
  populations, and outcomes prevent a simple winner claim across these studies.

## Explicit design inferences

A brief local diagnosis, bounded research pass, small next step, and concrete
pivot after repeated failure are usability and epistemic-quality choices. Research
supports adaptation and contingent help in broad terms; it does not prescribe an
exact question count, frustration threshold, response length, or mastery cutoff.
Explicit frustration warrants respectful alternatives because the learner has
reported a problem. Do not infer emotions or deliberately manufacture confusion.

The source gate is also a quality requirement, not proof of causal learning gains.
Retrieval can still yield false, irrelevant, outdated, or hostile text; evaluate
support and source quality rather than counting citations. A reliable synthesis
may be more useful than an isolated primary study for a broad question.

## Research log and preservation

Question: Which evidence-informed decisions can improve the behavior of a portable
adaptive tutor without making unsupported efficacy claims? Depth: focused review.
The table and AI-study records preserve retained findings, implications, access
scope, and limits; teaching-decisions.md is the operational synthesis.

Search route: inspected the named foundational and AI-tutoring sources, followed
university/author-hosted alternatives when publisher retrieval failed, and integrated
a separate source-grounding and pivot-policy review checked on the same date.
PubMed retrieval for the 2006 testing paper returned no usable abstract; the
university record supplied it. The Renkl publisher page was inaccessible; KLI
provides the retained worked-example rationale. Unrelated search results were
excluded. The inspirational video and external learn repository were not used as
teaching evidence or copied into the skill. No external exercises, source code,
figures, or full-text papers are redistributed; this is original synthesis with
attribution. Citation is not permission to redistribute source material.

Open questions: Does this policy improve real learners' unassisted transfer and
retention? What research overhead is acceptable in short sessions? Which pivots
help specific populations and domains? Answer through the validation protocol,
not simulated success or promotional language.
