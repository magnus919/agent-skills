#!/usr/bin/env python3
"""Classification with DSPy using BootstrapFewShot."""

import dspy

lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

class IntentClassify(dspy.Signature):
    """Classify customer support intent."""
    text: str = dspy.InputField()
    intent: str = dspy.OutputField(desc="billing, technical, account, or sales")

class Classifier(dspy.Module):
    def __init__(self):
        self.classify = dspy.ChainOfThought(IntentClassify)
    def forward(self, text):
        return self.classify(text=text)

def accuracy(example, pred, trace=None):
    return example.intent == pred.intent

# Example training data
trainset = [
    dspy.Example(text="My card was charged twice", intent="billing").with_inputs("text"),
    dspy.Example(text="The login page won't load", intent="technical").with_inputs("text"),
    dspy.Example(text="I want to upgrade my plan", intent="account").with_inputs("text"),
]

program = Classifier()
optimizer = dspy.BootstrapFewShot(metric=accuracy)
compiled = optimizer.compile(program, trainset=trainset)

# Use
result = compiled(text="Where is my refund?")
print(f"Intent: {result.intent}")
