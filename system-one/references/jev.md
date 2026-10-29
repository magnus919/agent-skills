# TypeSafe Jev: hosted integration guide

Checked 2026-10-15 against the live documentation index and release notes. Verify the endpoint, model IDs, pricing, limits, gateway
availability, and SDK version again before a production cutover.

## Refresh provider documentation before implementation

This file is a dated integration snapshot. At the start of new Jev integration
work, fetch the [live documentation index](https://docs.typesafe.ai/llms.txt)
and use it to locate current pages. Read the current [HTTP API](https://docs.typesafe.ai/api.md)
or the selected SDK reference, then the question guidance and closest cookbook
for the workflow. Follow linked pages rather than treating this snapshot's
endpoint, model alias, request shape, or SDK examples as current guarantees.

If the index is unavailable, try its direct page links and the site's normal
HTML pages. If live access remains unavailable, inspect local documentation or
installed SDK types, mark version-dependent details unverified, and avoid
inventing current behavior. Preserve a deterministic fallback and do not
silently turn provider errors into a confident answer.

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

## Release selection and experimental capabilities

The [model catalog](https://docs.typesafe.ai/models) currently distinguishes:

| Request model | Resolved revision on 2026-10-15 | Use |
|---|---|---|
| `jev-latest` | `jev-1.13.0` | Preferred moving stable alias for general examples |
| `jev-preview` | `jev-1.14.0` | Moving newest-release alias for explicit preview trials |
| `jev-1.14.0` | Fixed 1.14.0 | Reproducible qualification of the new release |

Responses name the versioned model, not the alias. Log that identity; do not
compare it literally to an alias or claim `latest` already means 1.14.
[Release notes](https://typesafe.ai/blog/jev-1-14) announce an eventual stable
alias promotion, not evidence it has happened. They report incremental quality
improvements, especially multilingual; test these on the target workload.
Pin revisions for calibrated policy and benchmarks; requalify before switching.

### Images (experimental)

[Images](https://docs.typesafe.ai/images) work on both 1.13 and 1.14 with
`TypeSafe-Danger-Zone-Images: true`. A top-level `assets` map binds unique
reference strings to images; references in state, instructions, or criteria
values insert those images. Keys are not substituted. Use collision-resistant
references; unused assets fail, and repeated insertions consume capacity.
For JSON use `{"type":"image","format":"png","data_base64":"..."}`
with actual base64, no data-URL prefix. Prefer multipart for files: first part
`request` contains JSON; each asset's `part` names its unique image file part.
PNG/JPEG still images only; check current size/dimension/expanded-input limits.
No native audio or video input is established; frame histories are still images.
These features are prototypes, not provider-qualified production capabilities.

### Box (experimental, 1.14 required)

[Box](https://docs.typesafe.ai/primitives/box) requires `jev-preview` or a
1.14 pin plus the images header. Ask `{"type":"box","instructions":"the mug in photo"}`
with an image asset; there is no `criteria`. The answer contains `type: box`,
`box: {top, bottom, left, right}`, and `confidence`. Validate finite normalized
edges in `[0,1]`, `left < right`, `top < bottom`, and finite confidence in
`[0,1]`. Scale horizontal edges by width and vertical edges by height.
One question returns one box; an absent target still produces edges. Pair with
a Noul presence question and ignore the box when presence is insufficient.
Calibrate presence and localization separately; confidence does not prove a
correct crop. Do not assume local Choice/Score/Noul adapters implement Box.

### Long context (experimental)

The [context limits](https://docs.typesafe.ai/models#context-length) are 64k
per request and 32k per question by default. On either release,
`TypeSafe-Danger-Zone-Long-Context: true` raises both to 262k tokens. The provider
warns of slower and less accurate inference; enable per request only after
workload qualification. Context extension does not enable images or Box.

The bundled probe/demo and QA helpers cover the text Choice/Score/Noul subset;
they do not validate image assets, transport multipart, add experimental
headers, or validate Box. Use the current HTTP/SDK documentation for those
paths and qualify a dedicated adapter before relying on its output. An offline
text-probe pass does not establish multimodal or extended-context support.

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

## Raw HTTP versus helper validation

The [raw Choice API](https://docs.typesafe.ai/primitives/choice) requires an
object map of option names to descriptions. The generic bundled probe also
accepts lists for other adapters; offline acceptance does not qualify a raw
Jev request. Use the current provider schema when preparing a live request.

## SDK compatibility for the new surfaces

The [Python 0.7.5 changelog](https://docs.typesafe.ai/sdk/python/changelog)
adds `Image`, `Box`, and `attach_assets`, with zstd request compression enabled
by default; verify compatibility before sending compressed bodies to a gateway.
The [JavaScript 0.7.0 changelog](https://docs.typesafe.ai/sdk/javascript/changelog)
adds image/Box support, requires Node.js 22+, and stops exporting request
payload types. It compresses bodies of at least 1 KiB on Node.js 22.15+;
`compression: false` disables that transport feature. Check installed SDK
versions before copying these APIs; a model alias alone cannot upgrade a client.

The new release-selection eval and its satisfying, contradictory, and
missing-evidence challenges are in `evals/jev-release-feature-challenges.md`.
They review the rubric, not measured model quality.

## SDK pattern

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        model="jev-latest",
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
