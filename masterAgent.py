"""
Master agent orchestrator for ServiceNow and Cisco troubleshooting.
Provides two tools: fetch_incident_details and fetch_live_diagnostics.
"""
from langchain.tools import tool
from snowAgent2 import run_snow_agent
from NAA2 import run_cisco_agent

from langchain.agents import create_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os

load_dotenv()



@tool(
    "fetch_incident_details",
    description="Fetches ServiceNow incident details using incident number"
)
async def fetch_incident_details(
    incident_number: str
) -> str:
    """
    Fetch incident details from ServiceNow using the incident number.
    Args:
        incident_number (str): The ServiceNow incident number.
    Returns:
        str: The summarized incident details.
    """
    query = f"Get details for incident {incident_number}"
    response = await run_snow_agent(query)
    return response



@tool(
    "fetch_live_diagnostics",
    description="Runs Cisco network diagnostics and troubleshooting analysis"
)
async def fetch_live_diagnostics(
    issue_description: str
) -> str:
    """
    Run Cisco diagnostics based on the provided issue description.
    Args:
        issue_description (str): Description of the network issue.
    Returns:
        str: The diagnostic output.
    """
    response = await run_cisco_agent(issue_description)
    return response


llm = ChatGroq(
    model=os.getenv("Model"),
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


master_agent = create_agent(
    llm,
    tools=[
        fetch_incident_details,
        fetch_live_diagnostics
    ],
    system_prompt="""
You are a Network Incident Resolution Orchestrator.

You coordinate between:
1. A ServiceNow Incident Agent
2. A Cisco Network Diagnostics Agent

Responsibilities:
- Understand the user's network issue
- Fetch incident details when an incident number is provided
- Fetch live diagnostics when troubleshooting is required
- Correlate incident data with diagnostics
- Provide concise RCA-style responses

Tool Usage Rules:
- Use fetch_incident_details for ServiceNow incident lookups
- Use fetch_live_diagnostics for Cisco troubleshooting
- Never hallucinate incident details or diagnostics
- Ask for missing information if required
- Combine outputs from both tools intelligently
"""
)