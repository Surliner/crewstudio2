from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
    SerpApiGoogleSearchTool,
    ScrapeWebsiteTool,
    FileWriterTool,
)
import os
from typing import Optional
from datetime import datetime
import logging
import warnings

# Filter out deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Configure logging with custom format
logging.basicConfig(
    level=logging.INFO,
    format='\n%(asctime)s - %(levelname)s\n%(message)s\n',  # Added newlines for better readability
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add a divider function for visual separation in logs
def log_divider(message: str):
    logger.info("="*50)
    logger.info(message)
    logger.info("="*50)

@CrewBase
class CrewAutomationForErpResearchAndOutreachCrew():
    """CrewAutomationForErpResearchAndOutreach crew"""

    def __init__(self):
        super().__init__()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = os.path.join('output', self.timestamp)
        os.makedirs(self.output_dir, exist_ok=True)
        log_divider("Initialization")
        logger.info(f"Created output directory: {self.output_dir}")

    def get_output_path(self, filename: str) -> str:
        """Generate a unique output file path with timestamp"""
        path = os.path.join(self.output_dir, filename)
        logger.info(f"Generated output path: {path}")
        return path

    def safe_scrape(self, url: str) -> Optional[str]:
        """Safely scrape a website with error handling"""
        try:
            log_divider(f"Scraping Website: {url}")
            scraper = ScrapeWebsiteTool()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            result = scraper.run(website_url=url, headers=headers)
            if result:
                logger.info("Scraping successful")
                # Store the result in the output directory
                filename = f"scrape_{datetime.now().strftime('%H%M%S')}_{url.split('/')[-1]}.txt"
                with open(self.get_output_path(filename), 'w') as f:
                    f.write(f"Source: {url}\n\n{result}")
                logger.info(f"Saved scraping results to {filename}")
            return result
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return None

    def collect_search_results(self, search_results: dict) -> None:
        """Collect and store search results"""
        if not search_results:
            return
        
        filename = f"search_results_{datetime.now().strftime('%H%M%S')}.md"
        filepath = self.get_output_path(filename)
        
        with open(filepath, 'w') as f:
            f.write("# Search Results\n\n")
            if 'organic_results' in search_results:
                f.write("## Organic Results\n\n")
                for result in search_results['organic_results']:
                    f.write(f"### {result.get('title', 'No Title')}\n")
                    f.write(f"- URL: {result.get('link', 'No Link')}\n")
                    f.write(f"- Snippet: {result.get('snippet', 'No Snippet')}\n\n")
            
            if 'related_searches' in search_results:
                f.write("## Related Searches\n\n")
                for related in search_results['related_searches']:
                    f.write(f"- {related.get('query', 'No Query')}\n")
        
        logger.info(f"Saved search results to {filename}")

    @agent
    def company_data_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['company_data_researcher'],
            tools=[
                SerpApiGoogleSearchTool(),
                ScrapeWebsiteTool(),
            ],
            llm_config={
                "model": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 4000,
            },
            instructions="""
            Follow these steps for company research:
            1. Use SerpApiGoogleSearchTool with specific queries:
               - "site:societe.com {siren_number}"
               - "site:infogreffe.fr {siren_number}"
               - "site:pappers.fr {siren_number}"
               - "{company_name} site:linkedin.com"
               - "{company_name} ERP système d'information"
               - "{company_name} news OR actualités -site:linkedin.com"
               - "{company_name} press release OR communiqué de presse"
            2. For each relevant URL found:
               - Save ALL relevant information including news, contacts with their email, phone number, linkedin profile and developments of the target company
               - Store URLs and snippets for reference
               - Pay special attention to recent company developments
               - Collect any mentioned employee names and roles
            3. Structure findings into:
            - Company Overview
            - Recent Developments (with dates and sources)
            - IT Systems & Infrastructure
            - Current ERP Status
            - Financial Performance
            - Company Culture
            - Key Contacts Found (with roles and sources)

            Important: ALL found information must be preserved and included in the output.
            """
        )

    @agent
    def person_identifier(self) -> Agent:
        return Agent(
            config=self.agents_config['person_identifier'],
            tools=[
                SerpApiGoogleSearchTool(),
                ScrapeWebsiteTool(),
            ],
            llm_config={
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 4000,
            },
            instructions="""
            Follow these steps to identify decision makers:
            1. Use SerpApiGoogleSearchTool with specific queries:
               - "site:societe.com {siren_number} dirigeants"
               - "site:linkedin.com {company_name} (CIO OR DSI OR Directeur Système Information)"
               - "site:linkedin.com {company_name} (CEO OR DG OR Directeur Général)"
               - "site:linkedin.com {company_name} (CFO OR DAF OR Directeur Financier)"
               - "{company_name} management team"
               - "{company_name} équipe dirigeante"
            2. For each found profile or mention:
               - ALWAYS save the full name and title
               - ALWAYS save the LinkedIn URL if available
               - ALWAYS preserve any contact information found
               - Document the source of information
               - Note any technology-related responsibilities
               - Track their career progression if available
            3. Create detailed profiles for each person:
               - Full name and current role
               - Professional history with the company
               - Technology decision-making authority
               - Contact information (ALL found methods)
               - LinkedIn and other professional profiles
               - Source URLs for each piece of information

            Important: 
            - Save ALL found contacts, even if not certain of their current status
            - Include EVERY piece of contact information found
            - Preserve ALL source URLs for verification
            - Note any recent role changes or appointments
            """
        )

    @agent
    def email_report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['email_report_generator'],
            tools=[FileWriterTool()],
            llm_config={
                "model": "o1",
                "temperature": 0.7,  # More creative for email writing
                "max_tokens": 40000,
            },
            instructions="""
            Use FileWriterTool to create:
            1. A persuasive and short email highlighting:
               - Specific pain points identified about {company_name} which activity is {activity_type}
               - Relevant {our_product} benefits
               - Clear call to action
            2. A detailed report including:
               - {company_name} research findings
               - Decision maker profile and contact information of {company_name} 
               - Customized value proposition for integration of {our_product} considering {company_name} {activity_type} and your findings
            Save outputs to the specified file paths.
            """
        )

    @task
    def data_collection_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_collection_task'],
            tools=[
                SerpApiGoogleSearchTool(),
                ScrapeWebsiteTool(),
            ],
            output_file=self.get_output_path("company_research.md")
        )

    @task
    def person_identification_task(self) -> Task:
        return Task(
            config=self.tasks_config['person_identification_task'],
            tools=[
                SerpApiGoogleSearchTool(),
                ScrapeWebsiteTool(),
            ],
            output_file=self.get_output_path("person_info.md")
        )

    @task
    def benefit_idea_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['benefit_idea_generation_task'],
            tools=[],
            output_file=self.get_output_path("benefit_ideas.md")
        )

    @task
    def email_drafting_task(self) -> Task:
        return Task(
            config=self.tasks_config['email_drafting_task'],
            tools=[FileWriterTool()],
            output_file=self.get_output_path("email_draft.md")
        )

    @task
    def report_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_summary_task'],
            tools=[FileWriterTool()],
            output_file=self.get_output_path("final_report.md")
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewAutomationForErpResearchAndOutreach crew"""
        log_divider("Creating Crew")
        logger.info("Initializing agents and tasks...")
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
        logger.info("Crew initialization complete")
        return crew
