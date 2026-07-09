#!/usr/bin/env python3
"""Customer support crew: triage -> specialist -> response."""

from crewai import Agent, Task, Crew, Process

triage = Agent(role="Triage Agent", goal="Categorize and route support tickets",
               backstory="Support specialist", verbose=True)

specialist = Agent(role="Product Specialist",
                   goal="Resolve complex technical issues",
                   backstory="Senior support engineer", verbose=True)

response = Agent(role="Response Writer",
                 goal="Write clear, empathetic customer responses",
                 backstory="Customer communication expert", verbose=True)

triage_task = Task(description="Categorize the support ticket and route it",
                   expected_output="Categorized ticket with routing info",
                   agent=triage)

resolve_task = Task(description="Resolve the technical issue",
                    expected_output="Solution steps for the issue",
                    agent=specialist, context=[triage_task])

respond_task = Task(description="Write a customer-facing response",
                    expected_output="Empathetic response with solution",
                    agent=response, context=[resolve_task])

crew = Crew(agents=[triage, specialist, response],
            tasks=[triage_task, resolve_task, respond_task],
            process=Process.sequential, verbose=True)

result = crew.kickoff()
print(result)
