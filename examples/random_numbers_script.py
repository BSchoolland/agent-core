from core.agent.agent import Agent
import asyncio

async def main():
    agent = await Agent.create(
        model='gpt-4o-mini',  # specified model requirement
        mcp_servers=['examples/mcp_server.py']
    )
    await agent.run("Generate 2 random numbers between 1-100, add them together and save the result in a file called 'result.txt'")
    await agent.close()

if __name__ == '__main__':
    asyncio.run(main())