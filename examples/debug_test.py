# Debug test for agent with detailed logging
from core.agent.agent import Agent
import asyncio
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_provider(provider_name, model_name):
    print(f"\n{'='*80}")
    print(f"TESTING {provider_name.upper()} PROVIDER WITH {model_name}")
    print(f"{'='*80}")
    
    try:
        agent = await Agent.create(
            provider=provider_name,
            model=model_name,
            mcp_servers=['examples/mcp_server.py'],
            type='react'
        )
        
        # Simple multi-step task
        goal = "Generate 2 random numbers between 1-10, then add them together"
        
        print(f"GOAL: {goal}")
        print("-" * 80)
        
        result = await agent.run(goal)
        await agent.close()
        
        print(f"\nFINAL RESULT: {result['state']}")
        if result.get('error'):
            print(f"ERROR: {result['error']}")
            
        return result
        
    except Exception as e:
        print(f"FAILED TO CREATE/RUN AGENT: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    # Test different providers
    providers_to_test = [
        ('openai', 'gpt-4o-mini'),
        ('gemini', 'gemini-1.5-flash')
    ]
    
    for provider, model in providers_to_test:
        result = await test_provider(provider, model)
        if result:
            print(f"\n{provider.upper()} RESULT: {result['state']}")
        else:
            print(f"\n{provider.upper()} FAILED")
        
        # Pause between tests
        await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(main()) 