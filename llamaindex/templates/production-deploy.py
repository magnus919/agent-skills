#!/usr/bin/env python3
"""
Deploy a LlamaIndex Workflow as a production microservice using llama-deploy.
Requires: `pip install llama-deploy`, running Redis instance.
"""

import asyncio
from llama_deploy import (
    deploy_workflow,
    WorkflowServiceConfig,
    ControlPlaneConfig,
)
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step


class MyRAGWorkflow(Workflow):
    """Your workflow class — replace with your actual Workflow."""

    @step
    async def process(self, ev: StartEvent) -> StopEvent:
        # Your workflow logic here
        return StopEvent(result=f"Processed: {ev.query}")


async def main():
    await deploy_workflow(
        workflow=MyRAGWorkflow(timeout=60),
        workflow_config=WorkflowServiceConfig(
            service_name="my-rag-service",
        ),
        control_plane_config=ControlPlaneConfig(),
    )


if __name__ == "__main__":
    asyncio.run(main())
