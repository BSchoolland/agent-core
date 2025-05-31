# quick chat example with an mcp server and gemini provider
from core.agent.agent import Agent
import asyncio

async def main():
    agent = await Agent.create(
        model='gemini-2.0-flash', # great for testing because it has a free tier
        mcp_servers=['examples/mcp_server.py'],
        type='hybrid'
    )
    result = await agent.run("Generate 2 random numbers between 1-10, then add them together")
    await agent.close()
    return result
if __name__ == '__main__':
    result = asyncio.run(main())
    error_msg = result.get('error', 'no error')
    print("Agent of type " + result['type'] + " completed with state " + result['state'] + " and error " + error_msg)
    print('want to see the history? (y/n)')
    if input() == 'y':
        for msg in result['history']:
            print(msg)