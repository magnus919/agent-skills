# Method Selection

How to choose the right experiment method for a given hypothesis. The core principle: start at the lightest-weight method that can falsify the hypothesis, and only move down the ladder when the question cannot be answered at the current level.

## The Method Ladder

| Method | What it tests | Sample size | Statistical rigor | When to use | When NOT to use |
|--------|--------------|-------------|-------------------|-------------|-----------------|
| **Qualitative interviews** | Mental models, problem validation, unknown unknowns | 5-15 | None (descriptive) | You do not understand the problem space yet; the riskiest assumption is about user behavior or motivation | You need a precise effect size estimate; the hypothesis is about a quantitative change |
| **Prototype tests** | Interaction flow, usability, concept desirability | 5-20 | None (observational) | The question is "can users figure this out?" or "does this concept resonate?" | You need causal attribution to a business metric; the prototype cannot simulate the real experience |
| **Concierge tests** | Value delivery, willingness to pay, operational feasibility | 1-20 | None (manual) | You need to test whether anyone will pay for or use the service before building automation | The manual delivery cannot approximate the automated experience closely enough |
| **Fake doors** | Demand signals, willingness to click/commit | 100+ | Low (conversion rate difference) | You need to size demand before building; the cost of the real feature is high | The fake door deceives users and the deception risk is unacceptable; the feature is trivial to build |
| **Feature flags** | Operational safety, incremental rollout, kill-switch | Configurable | Medium (controlled rollout) | You have a feature ready and need to validate it safely in production with the ability to turn it off | You have not validated the underlying assumption; a flag controls risk but does not test value |
| **A/B tests** | Causal attribution of a specific change to a metric | Statistical minimum (power analysis) | High (randomized controlled) | You need causal evidence that a change moves a metric; the sample size is achievable | The question can be answered with a lighter method; the sample is too small for adequate power; the ethics of randomization are questionable |

## Selection Decision Tree

```
Can you learn enough from talking to 5-10 users?
  └─ YES → Qualitative interviews
  └─ NO  → Can you build a clickable prototype in a day and test it with 5-20 people?
              └─ YES → Prototype test
              └─ NO  → Can you manually deliver the value for 1-20 users?
                          └─ YES → Concierge test
                          └─ NO  → Can you measure demand with a button that does not yet work?
                                      └─ YES → Fake door
                                      └─ NO  → Do you have the feature built and need safe rollout?
                                                  └─ YES → Feature flag
                                                  └─ NO  → Do you need causal attribution with statistical rigor?
                                                              └─ YES → A/B test
                                                              └─ NO  → Revisit the hypothesis — is it testable?
```

## Anti-Patterns

### Defaulting to A/B testing

The most common experimentation failure. A/B testing is expensive: it requires engineering time to build the variant, statistical design (power analysis, sample-size calculation), enough traffic to detect the effect, and time to run. Before committing to an A/B test, ask: "Could I learn enough from 5 interviews to make this decision?" If yes, do the interviews.

### Testing the wrong thing

If the hypothesis is "users want this feature" and you A/B test whether a blue button outperforms a green button, you are testing execution, not value. Execution testing is only useful after value is confirmed.

### Ignoring method limitations

Every method has blind spots. Qualitative interviews cannot tell you how many users will convert. A/B tests cannot tell you why users behave differently. Use multiple methods together when the decision is consequential.

## Measuring Method Adequacy

Before committing to a method, verify:

1. **Falsifiability:** Can this method produce evidence that would convince you the assumption is wrong?
2. **Timeliness:** Can you get the evidence fast enough to affect the decision?
3. **Cost proportionality:** Is the cost of the method proportionate to the cost of being wrong?
4. **Ethical fit:** Does the method respect user autonomy, consent, and dignity?
