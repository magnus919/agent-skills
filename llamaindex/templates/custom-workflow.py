#!/usr/bin/env python3
"""
Custom event-driven workflow with typed events.
Shows branching, looping, and state management patterns.
"""

from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from pydantic import Field

Settings.llm = OpenAI(model="gpt-4o-mini")

# --- Custom Events ---
class RetrievedEvent(Event):
    """Documents have been retrieved."""
    query: str
    documents: list = Field(default_factory=list)

class EvaluatedEvent(Event):
    """Retrieved documents have been evaluated for relevance."""
    query: str
    is_relevant: bool = False
    documents: list = Field(default_factory=list)

class ResearchedEvent(Event):
    """Additional research has been performed."""
    query: str
    findings: str = ""

# --- Workflow ---
class SmartRAG(Workflow):
    llm = OpenAI(model="gpt-4o-mini")

    @step
    async def retrieve(self, ev: StartEvent) -> RetrievedEvent:
        """Initial retrieval."""
        from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
        documents = SimpleDirectoryReader("./data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        retriever = index.as_retriever(similarity_top_k=4)
        nodes = retriever.retrieve(ev.query)
        return RetrievedEvent(query=ev.query, documents=nodes)

    @step
    async def evaluate(self, ev: RetrievedEvent) -> EvaluatedEvent | ResearchedEvent:
        """Evaluate if retrieved docs are sufficient. If not, research more."""
        context = "\n\n".join([n.get_content()[:200] for n in ev.documents])
        prompt = f"Query: {ev.query}\nContext: {context}\nIs this context sufficient? Answer YES or NO."
        resp = await self.llm.acomplete(prompt)

        if "YES" in str(resp).upper():
            return EvaluatedEvent(
                query=ev.query, is_relevant=True, documents=ev.documents
            )
        else:
            # Research branch — loops back to evaluate after
            search_prompt = f"Research this topic: {ev.query}. Provide 3 key facts."
            research = await self.llm.acomplete(search_prompt)
            return ResearchedEvent(query=ev.query, findings=str(research))

    @step
    async def research(self, ev: ResearchedEvent) -> RetrievedEvent:
        """Generate synthetic context when retrieval was insufficient."""
        from llama_index.core.schema import TextNode
        extra_node = TextNode(text=ev.findings)
        return RetrievedEvent(
            query=ev.query,
            documents=[extra_node],  # Loop back to evaluate
        )

    @step
    async def synthesize(self, ev: EvaluatedEvent) -> StopEvent:
        """Final answer synthesis."""
        context = "\n\n".join([n.get_content() for n in ev.documents])
        prompt = f"Answer the query using the context.\n\nContext:\n{context}\n\nQuery: {ev.query}"
        resp = await self.llm.acomplete(prompt)
        return StopEvent(result=str(resp))

# --- Run ---
async def main():
    wf = SmartRAG(timeout=60, verbose=True)
    result = await wf.run(query="What are the key findings in this document?")
    print(f"Result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
