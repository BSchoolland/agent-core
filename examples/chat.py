# quick chat example with an mcp server and gemini provider
from core.chatbot.conversation import Conversation
import asyncio

async def main():
    conversation = await Conversation.create(
        model='gemini-1.5-flash',  # Using a small, cost-effective model
        provider='gemini',
        mcp_servers=['examples/mcp_server.py']
    )
    await conversation.generate_response('Hello, how are you?')
    await conversation.generate_response('Tell me a joke.')
    await conversation.close()
    return text
if __name__ == '__main__':
    print(asyncio.run(main()))