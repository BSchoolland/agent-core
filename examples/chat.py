# quick chat example with an mcp server and openai provider
from core.chatbot.conversation import Conversation
import asyncio
async def main():
    conversation = await Conversation.create(
        model='gpt-4o-mini',
        provider='openai',
        mcp_servers=['examples/mcp_server.py']
    )
    return await conversation.generate_response('You should have access to a custom tool called "add" that adds two numbers together. Use it to add 123 and 234 together')

if __name__ == '__main__':
    print(asyncio.run(main()))