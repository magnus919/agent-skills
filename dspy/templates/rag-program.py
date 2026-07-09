#!/usr/bin/env python3
"""RAG program with DSPy using ColBERT retrieval and ChainOfThought."""

import dspy

lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

class RAG(dspy.Module):
    def __init__(self, k=5):
        self.retrieve = dspy.Retrieve(k=k)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = "\n".join(self.retrieve(question).passages)
        return self.generate(question=question, context=context)

def correct(example, pred, trace=None):
    return example.answer in pred.answer

trainset = [
    dspy.Example(question="What is DSPy?", answer="A compiler for prompt programs").with_inputs("question"),
]

program = RAG()
optimizer = dspy.BootstrapFewShot(metric=correct)
compiled = optimizer.compile(program, trainset=trainset)

result = compiled(question="What is DSPy used for?")
print(f"Answer: {result.answer}")
