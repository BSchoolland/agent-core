# quick chat example with an mcp server and gemini provider
from core.chatbot.conversation import Conversation
import asyncio

async def main():
    conversation = await Conversation.create(
        model='gemini-2.0-flash',  # Using a small, cost-effective model
        mcp_servers=['examples/mcp_server.py']
    )
    print(await conversation.generate_response('Hello, how are you?'))
    print(await conversation.generate_response('Tell me a joke.'))
    await conversation.close()

if __name__ == '__main__':
    print(asyncio.run(main()))