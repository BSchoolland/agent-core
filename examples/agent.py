# quick chat example with an mcp server and gemini provider
from agent_core import Agent
import asyncio

async def main():
    agent = await Agent.create(
        model='gpt-4o-mini',
        mcp_servers=['examples/mcp_server.py'],
        type='react'
    )
    result = await agent.run("Generate 2 random numbers between 1-100, add them together and save the result in a file called 'result.txt' in the form 'a + b = c'")
    await agent.close()
    return result

if __name__ == '__main__':
    result = asyncio.run(main())
