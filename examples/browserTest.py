# Screenshot agent - navigates to a visually interesting website and captures it
from agent_core.agent.agent import Agent
import asyncio

async def main():
    # Configure Playwright MCP server to save to testing directory
    playwright_server = {
        'command': 'npx',
        'args': ['@playwright/mcp@latest', '--headless', '--output-dir', './testing']
    }
    
    agent = await Agent.create(
        model='gpt-4.1',
        mcp_servers=[playwright_server],
        type='react'
    )
    
    result = await agent.run(
        "Navigate to https://www.apple.com and take a screenshot of the homepage"
    )
    
    await agent.close()
    return result

if __name__ == '__main__':
    result = asyncio.run(main())
    print(f"Screenshot agent completed: {result['state']}") 