#!/usr/bin/env python3
"""Sequential research crew: researcher -> writer -> reviewer."""

from crewai import Agent, Task, Crew, Process

researcher = Agent(role="Researcher", goal="Find accurate information",
                   backstory="Expert researcher", verbose=True)

writer = Agent(role="Writer", goal="Write clear reports",
               backstory="Technical writer", verbose=True)

reviewer = Agent(role="Reviewer", goal="Ensure quality and accuracy",
                 backstory="Senior editor", verbose=True)

research = Task(description="Research a given topic thoroughly",
                expected_output="A detailed research brief", agent=researcher)

write = Task(description="Write a report based on the research",
             expected_output="A well-structured report", agent=writer,
             context=[research])

review = Task(description="Review the report for accuracy and clarity",
              expected_output="Approved report with feedback", agent=reviewer,
              context=[write])

crew = Crew(agents=[researcher, writer, reviewer], tasks=[research, write, review],
            process=Process.sequential, verbose=True)

result = crew.kickoff()
print(result)
