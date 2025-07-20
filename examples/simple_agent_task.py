from core.agent.agent import Agent
import asyncio

async def main():
    agent = await Agent.create(
        model='gpt-4o-mini',  # using the specified model
        mcp_servers=['examples/mcp_server.py']
    )
    await agent.run("Calculate 5 factorial and write the result to a file named 'factorial_result.txt'")
    await agent.close()

if __name__ == '__main__':
    asyncio.run(main())