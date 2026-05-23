"""
CLI entry point for interacting with the master_agent orchestrator.
"""
import asyncio
from masterAgent import master_agent

async def main():
    """
    Starts a CLI chat loop with the master_agent orchestrator.
    """
    messages = []
    while True:
        query = input("\nYou: ")
        if query.lower() == "exit":
            break
        messages.append(("human", query))
        response = await master_agent.ainvoke({"messages": messages})
        ai_response = response["messages"][-1].content
        print("\nAI:")
        print(ai_response)
        messages.append(("assistant", ai_response))

if __name__ == "__main__":
    asyncio.run(main())