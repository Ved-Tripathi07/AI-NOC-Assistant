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
# LOAD ENV
# --------------------------------
load_dotenv()

MAX_HISTORY = 6


# --------------------------------
# MAIN AGENT FUNCTION
# --------------------------------
async def run_cisco_agent(query: str, history=None) -> str:

    if history is None:
        history = []

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
    # START MCP CLIENT
    # --------------------------------
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            print("✅ MCP Session Started")

            await session.initialize()

            # --------------------------------
            # LOAD MCP TOOLS
            # --------------------------------
            tools = await load_mcp_tools(session)

            print("\n✅ Loaded Tools:")
            for tool in tools:
                print(f"- {tool.name}")

            # --------------------------------
            # LLM
            # --------------------------------
            llm = ChatGroq(
                model=os.getenv("Model"),
                temperature=0,
                max_tokens=512,
                api_key=os.getenv("GROQ_API_KEY")
            )

            # --------------------------------
            # SYSTEM PROMPT
            # --------------------------------
            system_prompt = """
You are a Cisco Network Troubleshooting Assistant.

Responsibilities:
- Analyze network incidents
- Identify probable Cisco router/switch issue
- Generate exactly 3 safe read-only troubleshooting commands
- Use ssh_connect tool ONLY when enough device information exists

Rules:
- Only use read-only Cisco IOS commands
- Never generate configuration/change commands
- Never hallucinate IPs, hostnames, usernames, or passwords
- Ask for missing details if required
- Keep responses concise

Output Format:
Command 1: <command>
Command 2: <command>
Command 3: <command>
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
            # MANAGE MEMORY
            # --------------------------------
            history.append(("human", query))

            history = history[-MAX_HISTORY:]

            # --------------------------------
            # INVOKE AGENT
            # --------------------------------
            response = await agent.ainvoke({
                "messages": history
            })

            ai_response = response["messages"][-1].content

            history.append(("assistant", ai_response))

            history = history[-MAX_HISTORY:]

            return ai_response


# --------------------------------
# OPTIONAL CHAT LOOP
# --------------------------------
async def main():

    history = []

    while True:

        query = input("\nYou: ")

        if query.lower() == "exit":
            break

        try:

            response = await run_cisco_agent(
                query=query,
                history=history
            )

            print("\nAI:")
            print(response)

        except Exception as e:

            print("\n❌ ERROR:")
            print(str(e))


# --------------------------------
# ENTRY POINT
# --------------------------------
if __name__ == "__main__":
    asyncio.run(main())