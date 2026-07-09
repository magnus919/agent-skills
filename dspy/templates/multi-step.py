#!/usr/bin/env python3
"""Multi-step reasoning with DSPy — decompose, answer, synthesize."""

import dspy

lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

class MultiStepQA(dspy.Module):
    def __init__(self):
        self.decompose = dspy.ChainOfThought("question -> sub_questions")
        self.answer = dspy.ChainOfThought("sub_question -> answer")
        self.synthesize = dspy.ChainOfThought("answers -> final_answer")

    def forward(self, question):
        sub_qs = self.decompose(question=question).sub_questions
        answers = []
        for q in sub_qs:
            answers.append(self.answer(sub_question=q).answer)
        combined = "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(sub_qs, answers))
        return self.synthesize(answers=combined)

program = MultiStepQA()
result = program(question="What are the benefits of using DSPy for prompt optimization?")
print(f"Final Answer: {result.final_answer}")
