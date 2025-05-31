# Single complex task testing
from core.agent.agent import Agent
import asyncio

async def main():
    agent = await Agent.create(
        model='gemini-1.5-flash',
        mcp_servers=['examples/mcp_server.py'],
        type='react'  # Using react for better reasoning
    )
    
    # Test a complex multi-step task
    goal = "Generate 5 random numbers between 1-50, save them to a file called 'numbers.txt', then calculate and display their average, max, and min values"
    
    print(f"GOAL: {goal}")
    print("="*80)
    
    result = await agent.run(goal)
    await agent.close()
    
    print(f"\nFINAL RESULT: {result['state']}")
    if result.get('error'):
        print(f"ERROR: {result['error']}")
    
    print("\nDo you want to see the full conversation history? (y/n)")
    if input().lower() == 'y':
        print("\nCONVERSATION HISTORY:")
        print("="*80)
        for i, message in enumerate(result['history']):
            print(f"\n[{i+1}] {message['role'].upper()}:")
            if message.get('content'):
                print(message['content'])
            if message.get('tool_calls'):
                print(f"Tool calls: {message['tool_calls']}")

if __name__ == '__main__':
    asyncio.run(main()) 