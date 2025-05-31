# Multi-step agent testing with enhanced MCP server
from core.agent.agent import Agent
import asyncio

async def test_task(agent, task_name, goal):
    """Test a single task and return results"""
    print(f"\n{'='*60}")
    print(f"TESTING: {task_name}")
    print(f"GOAL: {goal}")
    print(f"{'='*60}")
    
    result = await agent.run(goal)
    
    print(f"\nRESULT: {result['state']}")
    if result.get('error'):
        print(f"ERROR: {result['error']}")
    
    return result

async def main():
    # Test different agent types on complex tasks
    agent_types = ['simple', 'react', 'planner', 'hybrid']
    
    # Define complex multi-step tasks
    tasks = [
        {
            "name": "Data Analysis Pipeline",
            "goal": "Generate 10 random numbers between 1-100, save them to a file called 'numbers.txt', then calculate and display their average, max, min, and sort them in descending order"
        },
        {
            "name": "Text Processing Workflow", 
            "goal": "Create a text file called 'sample.txt' with the content 'Hello World! This is a TEST.', then count its words and characters, convert it to lowercase, reverse it, and save the reversed lowercase version to 'processed.txt'"
        },
        {
            "name": "Mathematical Computation",
            "goal": "Calculate 5 factorial, then raise the result to the power of 2, divide by 10, and create a JSON file called 'math_result.json' with the keys 'factorial', 'squared', 'final_result' containing the intermediate and final values"
        },
        {
            "name": "File Management Task",
            "goal": "List all files in the current directory, create a summary file called 'file_summary.txt' that contains the current time and the number of files found, then generate an MD5 hash of the summary content"
        }
    ]
    
    # Test each agent type on each task
    for agent_type in agent_types:
        print(f"\n{'#'*80}")
        print(f"TESTING AGENT TYPE: {agent_type.upper()}")
        print(f"{'#'*80}")
        
        for task in tasks:
            try:
                agent = await Agent.create(
                    model='gemini-1.5-flash',
                    mcp_servers=['examples/mcp_server.py'],
                    type=agent_type
                )
                
                result = await test_task(agent, task["name"], task["goal"])
                await agent.close()
                
                # Brief pause between tasks
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"ERROR with {agent_type} agent on {task['name']}: {str(e)}")
                continue

if __name__ == '__main__':
    asyncio.run(main()) 