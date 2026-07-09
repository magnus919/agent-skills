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

# Load
loader = WebBaseLoader("https://example.com/docs")
docs = loader.load()

# Split
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# Embed + store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# RAG chain
def format_docs(docs):
    return "\n\n".join(d.doc.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

## Document Loaders

| Loader | Source | Package |
|--------|--------|---------|
| `WebBaseLoader` | Web pages | langchain-community |
| `PyPDFLoader` | PDF files | langchain-community |
| `TextLoader` | Plain text | langchain-core |
| `NotionDBLoader` | Notion | langchain-community |
| `S3FileLoader` | AWS S3 | langchain-community |

## Text Splitters

| Splitter | Method | Best For |
|----------|--------|----------|
| `RecursiveCharacterTextSplitter` | Recursive character splitting | General purpose, default |
| `TokenTextSplitter` | Token-count-based | LLM context window optimization |
| `MarkdownHeaderTextSplitter` | Header-aware | Markdown documents |
| `SemanticChunker` | Embedding similarity | Coherent semantic units |

## Vector Store Integrations

| Store | Production | Setup |
|-------|-----------|-------|
| Chroma | Local dev | `pip install chromadb` |
| Pinecone | Yes | `pip install langchain-pinecone` |
| pgvector | Yes | `pip install langchain-postgres` |
| Weaviate | Yes | `pip install langchain-weaviate` |
| Qdrant | Yes | `pip install langchain-qdrant` |
| FAISS | Local | `pip install faiss-cpu` |

All stores use the same interface: `from_documents`, `as_retriever`, `similarity_search`.

## Advanced RAG Techniques

| Technique | Implementation |
|-----------|---------------|
| Multi-query retrieval | Generate multiple query variations, retrieve for each |
| Parent-document retriever | Retrieve small chunks, return parent context |
| Self-querying retriever | Extract query filters + semantic search |
| Ensemble retriever | Combine multiple retrieval methods with weighted scoring |
