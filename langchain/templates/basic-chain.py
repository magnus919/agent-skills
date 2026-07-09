#!/usr/bin/env python3
"""Minimal LangChain chain using LCEL."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "You are a helpful assistant. Answer concisely.\n\nQuestion: {question}"
)
model = ChatOpenAI(model="gpt-4o-mini")
chain = prompt | model | StrOutputParser()

result = chain.invoke({"question": "What is LangChain?"})
print(result)
