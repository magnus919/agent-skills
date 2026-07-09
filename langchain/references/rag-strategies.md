# LangChain RAG Strategies

## The Canonical RAG Chain

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load -> Split -> Embed -> Retrieve -> Generate
loader = WebBaseLoader("https://example.com/docs")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
vectorstore = Chroma.from_documents(
    splitter.split_documents(loader.load()),
    OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

def fmt(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | fmt, "question": RunnablePassthrough()}
    | ChatPromptTemplate.from_template("Answer using context:\n{context}\n\nQ: {question}")
    | ChatOpenAI()
    | StrOutputParser()
)
```

## Document Loaders (150+ Sources)

| Loader | Source | Package |
|--------|--------|---------|
| `WebBaseLoader` | Web pages | `langchain-community` |
| `PyPDFLoader` | PDF files | `langchain-community` |
| `TextLoader` | Plain text | `langchain-core` |
| `NotionDBLoader` | Notion | `langchain-community` |
| `S3FileLoader` | AWS S3 | `langchain-community` |

## Text Splitters

| Splitter | Method | Best For |
|----------|--------|----------|
| `RecursiveCharacterTextSplitter` | Recursive character | General purpose (default) |
| `TokenTextSplitter` | Token-count-based | LLM context optimization |
| `MarkdownHeaderTextSplitter` | Header-aware | Markdown documents |
| `SemanticChunker` | Embedding similarity | Coherent semantic units |

## Vector Store Integrations

All 40+ vector stores share the same interface: `from_documents`, `as_retriever`, `similarity_search`.

| Store | Production | Install |
|-------|-----------|---------|
| Chroma | Local dev | `pip install chromadb` |
| Pinecone | Yes | `pip install langchain-pinecone` |
| pgvector | Yes | `pip install langchain-postgres` |
| Weaviate | Yes | `pip install langchain-weaviate` |
| Qdrant | Yes | `pip install langchain-qdrant` |
| FAISS | Local | `pip install faiss-cpu` |

## Advanced Retrieval Patterns

| Technique | When to use | Implementation |
|-----------|-------------|----------------|
| Multi-query retrieval | Broad topics need diverse sources | Generate query variants, retrieve for each |
| ParentDocumentRetriever | Need small chunks + rich context | Retrieve child chunks, return parent documents |
| SelfQueryRetriever | Queries with filters | Extract semantic filter + query from natural language |
| EnsembleRetriever | Multiple retrieval methods | Weighted combination of BM25 + vector |

## Structured Document Chains (Migration Path)

These chain factories exist in `langchain_classic.chains` (the pre-v1.0 classic module):

| Chain | Purpose | Import |
|-------|---------|--------|
| `create_history_aware_retriever` | Rephrase question with chat history | `langchain_classic.chains` |
| `create_stuff_documents_chain` | LCEL-style Stuff documents chain | `langchain.chains` (v1.0 path) |

> **v1.0 recommendation:** Use LCEL directly rather than factory chains. The canonical RAG chain at the top of this page is the recommended pattern.
