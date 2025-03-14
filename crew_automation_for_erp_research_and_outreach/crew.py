from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from typing import Dict, Any

class CrewAutomationForErpResearchAndOutreachCrew:
    def __init__(self):
        self.company_researcher = Agent(
            role='Company Data Researcher',
            goal='Research company information and ERP usage',
            backstory='Expert at finding and analyzing company information',
            verbose=True,
            allow_delegation=False
        )
        
        self.erp_specialist = Agent(
            role='ERP Solutions Specialist',
            goal='Analyze ERP needs and opportunities',
            backstory='Expert in ERP systems and business processes',
            verbose=True,
            allow_delegation=False
        )
        
        self.content_creator = Agent(
            role='Content Creator',
            goal='Create compelling content for outreach',
            backstory='Expert in creating persuasive business content',
            verbose=True,
            allow_delegation=False
        )

    def crew(self) -> Crew:
        crew = Crew(
            agents=[
                self.company_researcher,
                self.erp_specialist,
                self.content_creator
            ],
            tasks=[
                Task(
                    description="Research company information",
                    agent=self.company_researcher
                ),
                Task(
                    description="Analyze ERP opportunities",
                    agent=self.erp_specialist
                ),
                Task(
                    description="Create outreach content",
                    agent=self.content_creator
                )
            ],
            verbose=True,
            process=Process.sequential
        )
        return crew 