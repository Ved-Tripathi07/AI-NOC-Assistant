"""
ServiceNow incident agent for MCP-based automation.
"""
import asyncio
import os
import sys

from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools


# --------------------------------
# LOAD ENV VARIABLES
# --------------------------------
load_dotenv()


# --------------------------------
# MAIN AGENT FUNCTION
# --------------------------------
async def run_snow_agent(query: str) -> str:
    """
    Run ServiceNow incident agent with MCP tools.
    Args:
        query (str): User's incident query or question.
    Returns:
        str: Agent's response.
    """

    # --------------------------------
    # MCP SERVER CONFIG
    # --------------------------------
    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "server.py"
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path],
    )

    # --------------------------------
    # START MCP SESSION
    # --------------------------------
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            print("Initializing MCP session...")
            await session.initialize()
            print("MCP initialized")

            # --------------------------------
            # LOAD TOOLS FROM MCP SERVER
            # --------------------------------
            print("Loading MCP tools...")
            tools = await load_mcp_tools(session)
            print(f"Loaded {len(tools)} tools")

            # --------------------------------
            # GROQ MODEL
            # --------------------------------
            llm = ChatGroq(
                model=os.getenv("Model"),
                temperature=0,
                api_key=os.getenv("GROQ_API_KEY")
            )

            # --------------------------------
            # SYSTEM PROMPT
            # --------------------------------
            system_prompt = """
You are an AI assistant responsible for fetching incident details 
from ServiceNow using MCP tools and summarizing the response.

Rules:
- Call get_incident_details when user asks about incidents
- Never hallucinate tool parameters
- Always provide structured summaries
"""

            # --------------------------------
            # CREATE AGENT
            # --------------------------------
            agent = create_agent(
                llm,
                tools,
                system_prompt=system_prompt
            )

            # --------------------------------
            # INVOKE AGENT
            # --------------------------------
            print("Calling agent...")

            response = await agent.ainvoke({
                "messages": [
                    ("human", query)
                ]
            })

            print("Agent execution completed")

            # --------------------------------
            # RETURN FINAL RESPONSE
            # --------------------------------
            return response["messages"][-1].content


# --------------------------------
# OPTIONAL TERMINAL CHAT LOOP
# --------------------------------
def main():
    """
    CLI entry point for running the ServiceNow agent interactively.
    """
    while True:
        query = input("\nYou: ")
        if query.lower() == "exit":
            break
        try:
            result = asyncio.run(run_snow_agent(query))
            print("\nAI:", result)
        except Exception as e:
            print("\nERROR:", str(e))


# --------------------------------
# ENTRY POINT
# --------------------------------
if __name__ == "__main__":
    main()