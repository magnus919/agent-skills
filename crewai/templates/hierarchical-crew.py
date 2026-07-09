#!/usr/bin/env python3
"""Hierarchical crew with manager agent delegating to specialists."""

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

researcher = Agent(role="Researcher", goal="Find accurate information",
                   backstory="Expert researcher", verbose=True)

analyst = Agent(role="Analyst", goal="Analyze findings for insights",
                backstory="Data analyst", verbose=True)

writer = Agent(role="Writer", goal="Write clear reports",
               backstory="Technical writer", verbose=True)

research = Task(description="Research the topic",
                expected_output="Research findings", agent=researcher)

analysis = Task(description="Analyze research findings",
                expected_output="Analysis with key insights", agent=analyst,
                context=[research])

report = Task(description="Write final report",
              expected_output="Completed report", agent=writer,
              context=[analysis])

crew = Crew(agents=[researcher, analyst, writer], tasks=[research, analysis, report],
            process=Process.hierarchical,
            manager_llm=ChatOpenAI(model="gpt-4"),  # Required for hierarchical
            verbose=True)

result = crew.kickoff()
print(result)
