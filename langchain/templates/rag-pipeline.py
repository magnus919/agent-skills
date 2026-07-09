#!/usr/bin/env python3
"""RAG pipeline: load, split, embed, retrieve, generate."""
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

# Embed + index
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# RAG chain
prompt = ChatPromptTemplate.from_template(
    "Answer using the context.\n\nContext: {context}\n\nQuestion: {question}"
)
model = ChatOpenAI(model="gpt-4o-mini")

def fmt(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    {"context": retriever | fmt, "question": RunnablePassthrough()}
    | prompt | model | StrOutputParser()
)

result = chain.invoke("What is this documentation about?")
print(result)
