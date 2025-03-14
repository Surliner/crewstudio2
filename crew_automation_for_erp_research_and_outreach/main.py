from crew import CrewAutomationForErpResearchAndOutreachCrew

def run(inputs=None):
    """Run the crew with the given inputs"""
    if inputs is None:
        inputs = {
            "company_name": "Example Company",
            "siren": "123456789",
            "city": "Paris",
            "activity_type": "Manufacturing",
            "website_url": "https://example.com"
        }
    
    # Create and run the crew
    crew_instance = CrewAutomationForErpResearchAndOutreachCrew()
    result = crew_instance.crew().kickoff(inputs=inputs)
    
    # Return the result
    return result 