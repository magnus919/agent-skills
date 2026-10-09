"""Offline checks of the reference code; requires pydantic-ai-slim and Pydantic 2."""

import asyncio
import json
from pathlib import Path

from pydantic_ai import models
from pydantic_ai.models.test import TestModel

models.ALLOW_MODEL_REQUESTS = False
reference = Path(__file__).resolve().parents[1] / "references/application-proposals.md"
code = reference.read_text().split("```python\n", 1)[1].split("```", 1)[0]
namespace = {}
exec(compile(code, str(reference), "exec"), namespace)


async def main():
    evidence = namespace["Evidence"]("REQ-DEMO-042", 12, ("ITEM-DEMO-7",), ("inventory-12",), "{}")
    good = dict(
        item_id="ITEM-DEMO-7",
        rationale="Available in the supplied inventory.",
        evidence_ids=["inventory-12"],
    )
    model = TestModel(custom_output_args=good)
    proposal = await namespace["propose"](evidence, model)
    assert proposal.item_id == "ITEM-DEMO-7"
    for changes, message in [
        ({"item_id": "outside-scope"}, "Unknown candidate"),
        ({"evidence_ids": ["invented"]}, "Unknown evidence"),
    ]:
        try:
            await namespace["propose"](evidence, TestModel(custom_output_args={**good, **changes}))
        except ValueError as exc:
            assert message in str(exc)
        else:
            raise AssertionError("Invalid scoped proposal accepted")
    assert not model.last_model_request_parameters.function_tools
    print(json.dumps({"offline_cases_passed": 3, "command_tools_registered": 0}))


asyncio.run(main())
