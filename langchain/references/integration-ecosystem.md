# LangChain Integration Ecosystem

LangChain provides a unified interface across 1000+ integrations. Switching providers requires changing one line.

## Model Providers

| Provider | Package | Class |
|----------|---------|-------|
| OpenAI | `langchain-openai` | `ChatOpenAI` |
| Anthropic | `langchain-anthropic` | `ChatAnthropic` |
| Google Gemini | `langchain-google` | `ChatGoogleGenerativeAI` |
| Mistral | `langchain-mistralai` | `ChatMistralAI` |
| AWS Bedrock | `langchain-aws` | `ChatBedrock` |
| Ollama (local) | `langchain-ollama` | `ChatOllama` |
| Fireworks | `langchain-fireworks` | `ChatFireworks` |

## Vector Stores

| Store | Package | Instantiation |
|-------|---------|---------------|
| Chroma | `langchain-chroma` | `Chroma.from_documents(docs, embeddings)` |
| Pinecone | `langchain-pinecone` | `PineconeVectorStore.from_documents(docs, embeddings)` |
| pgvector | `langchain-postgres` | `PGVector(embeddings=embeddings, connection=conn)` |
| Weaviate | `langchain-weaviate` | `WeaviateVectorStore.from_documents(docs, embeddings)` |
| Qdrant | `langchain-qdrant` | `QdrantVectorStore.from_documents(docs, embeddings)` |
| FAISS | `faiss-cpu` | `FAISS.from_documents(docs, embeddings)` |

## Tool Integrations

| Tool | Package | Purpose |
|------|---------|---------|
| Tavily Search | `langchain-community` | Web search for agents |
| MCP Servers | `langchain-mcp-adapters` | Connect any MCP server as a tool |
| SQL Database | `langchain-community` | Query SQL databases |
| ArXiv | `langchain-community` | Academic paper search |
| Wikipedia | `langchain-community` | Wikipedia lookup |

## MCP Adapter Pattern

Connect any MCP server as a LangChain tool:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async with MultiServerMCPClient() as client:
    tools = client.get_tools()
    agent = create_agent(model, tools)
```

## Quick-Swap Pattern

```python
# One-line swap between providers
model = ChatOpenAI(model="gpt-4o-mini")
# model = ChatAnthropic(model="claude-3-5-haiku")  # same interface
# model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")  # same interface
```

All models use the same interface: `model.invoke(messages)`.
