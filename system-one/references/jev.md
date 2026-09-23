# TypeSafe Jev: hosted integration guide

Checked 2026-09-22. Verify the endpoint, model IDs, pricing, limits, gateway
availability, and SDK version again before a production cutover.

## Current boundary

Jev is TypeSafe's first System One model. The official documentation describes
state plus typed questions in and typed answers/probabilities out. Jev is
currently a managed API: the public docs say there is no downloadable model
weight, so it cannot be self-hosted locally. Gateways may proxy the service but
do not turn it into an owned local model.

Official endpoint:

```text
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFE_API_KEY
Content-Type: application/json
```

The official Python package is `typesafe-sdk`; the raw HTTP contract is useful
when a project does not want a provider SDK. Keep keys server-side.

## Minimal request

```json
{
  "model": "jev-latest",
  "state": {
    "subject": "Duplicate charge",
    "body": "I was charged twice. Please refund the duplicate."
  },
  "questions": {
    "queue": {
      "type": "choice",
      "instructions": "Which team should handle this request?",
      "criteria": {
        "billing": "Payments, refunds, and invoices",
        "technical": "Bugs and integration failures",
        "other": "Anything else or insufficient information"
      }
    },
    "urgency": {
      "type": "score",
      "instructions": "How urgent is the request?",
      "criteria": ["routine", "soon", "blocking or time-critical"]
    },
    "refund_requested": {
      "type": "noul",
      "instructions": "Does the customer explicitly request a refund?"
    }
  }
}
```

Response consumers should validate that every requested answer exists, that the
answer type matches, that Choice keys are in the requested criteria, and that
probabilities/confidence are finite and within `[0, 1]`. Preserve the raw model
revision and request ID where the client exposes them.

## Reproducible integration walkthrough

From the skill root, run the bundled read-only synthetic ticket-routing path:

```bash
python3 scripts/systemone_probe.py --request examples/request.json
python3 scripts/decision_demo.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The first command validates request shape without network access. The second
loads `examples/response.synthetic.json`, validates every answer, and applies
an example policy; expected lane is `route_only`, queue `billing`, and a
`refund_flag` of `true`. **No refund or external routing action is executed.**
The example probabilities and `0.70`/`0.75`/`0.80` thresholds are invented
fixtures, not provider observations or recommended production thresholds.

Only after approving data egress and cost, set a server-side key and run:

```bash
python3 scripts/decision_demo.py --live
```

The live path uses one bounded request and does not print raw model output by
default. It raises on network, contract, or authorization failure; a calling
application should catch those errors and route to a review/fallback lane.
The probe's `--live` mode is a narrower connectivity check and supports
`--url` for a compatible gateway. A gateway's matching response schema does
not establish matching decision quality.

For a real integration, replace the fixture's state with a minimized,
authorized representation; keep question text trusted and versioned; choose
thresholds from a calibration split; and add a held-out test of wrong-route
and false-refund-flag rates. Separate the decision ID from the downstream
effect ID so an ambiguous API timeout cannot duplicate an external action.

## SDK pattern

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"message": "The integration fails for every customer."},
        questions={
            "route": Choice(
                instructions="Which handler should receive this?",
                criteria={"engineering": "Software failure", "support": "How-to", "other": "Unknown"},
            ),
            "urgent": Noul(instructions="Does this require immediate attention?"),
            "severity": Score(
                instructions="How severe is the reported impact?",
                criteria=["minor", "material", "blocking"],
            ),
        },
    )

answer = response.answers["route"]
if answer.confidence < 0.75:
    send_to_human_review()
elif answer.choice == "engineering":
    open_engineering_triage()
else:
    route_deterministically(answer.choice)
```

The threshold is an example only. Determine it from the target workflow's
error cost and held-out calibration data.

## Production practices

- Pin a Jev revision when thresholds or benchmarks matter; treat `jev-latest`
  as a moving alias. Include model revision and question/rubric hash in cache
  identity.
- Set a per-attempt timeout and a total retry budget. Retry only transient
  transport, overload, rate-limit, or server failures according to the current
  SDK behavior. A timed-out POST may have completed upstream and may be billed
  twice if retried.
- Distinguish 401/403 credential or permission failures, 400/422 contract
  failures, 429 throttling, 5xx/529 provider overload, transport failure, and
  malformed 2xx responses. Do not turn any of them into a confident default.
- Treat state as data sent to a third party. Minimize fields, redact secrets and
  unnecessary personal data, review retention/data-processing terms, and log a
  state hash rather than raw state by default.
- Keep a deterministic no-key/degraded path when the application requires
  availability without Jev. Make “unclassified,” “review,” and “retry later”
  explicit outcomes.
- Send independent questions together. Questions in the same call are not a
  dependency graph; a later question does not see an earlier answer.

## Terms and data boundary

The current TypeSafe master customer agreement describes the product as a
TypeSafe-hosted web interface/API and restricts using the Services or Output
for model distillation, imitation training, or development of a similar or
competing product. That matters when comparing Jev with Laya or training a
local replacement. Review the agreement attached to the actual account and
obtain legal guidance before using Jev outputs outside ordinary application
integration. The agreement also describes processing of customer input to
provide the service and telemetry; minimize and redact state accordingly.

## Fit and non-fit

Good fits are routing, closed-set classification, relevance scoring, safety or
prompt screening, tool selection, ranking, and choosing whether to escalate.
Poor fits are prose generation, open-ended research, long reasoning chains,
exact calculations, source verification, and policy authorization.

“Cannot hallucinate” means the answer shape is constrained by the requested
types/options. It does not mean the judgment is factually correct or that a
malicious/ambiguous state cannot induce a wrong choice.

## Primary sources

- Official introduction: https://docs.typesafe.ai/introduction
- Official quick start: https://docs.typesafe.ai/introduction/quickstart
- Official primitives: https://docs.typesafe.ai/primitives
- Official confidence: https://docs.typesafe.ai/confidence
- Official patterns: https://docs.typesafe.ai/patterns
- Official launch post: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- Official master customer agreement: https://typesafe.ai/legal/mca
- Official Python SDK: https://github.com/typesafe-ai/typesafe-sdk-python
