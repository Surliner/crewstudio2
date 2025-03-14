#!/usr/bin/env python
import sys
import os
from pathlib import Path
from .crew import CrewAutomationForErpResearchAndOutreachCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
