# quick chat example with an mcp server and gemini provider
from core.chatbot.conversation import Conversation
import asyncio

async def main():
    conversation = await Conversation.create(
        model='gemini-1.5-flash',  # Using a small, cost-effective model
        provider='gemini',
        mcp_servers=['examples/mcp_server.py']
    )
    text = await conversation.generate_response('Test your add tool by adding 123 and 456 together.  If you have no such tool, warn me instead of trying to add manually.')
    await conversation.close()
    return text
if __name__ == '__main__':
    print(asyncio.run(main()))