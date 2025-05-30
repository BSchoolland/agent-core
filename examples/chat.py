# quick chat example with an mcp server and anthropic provider
from core.chatbot.conversation import Conversation
import asyncio

async def main():
    conversation = await Conversation.create(
        model='claude-3-5-haiku-20241022',
        provider='anthropic',
        mcp_servers=['examples/mcp_server.py']
    )
    text = await conversation.generate_response('Test your add tool by adding 123 and 456 together.  If you have no such tool, warn me instead of trying to add manually.')
    await conversation.close()
    return text
if __name__ == '__main__':
    print(asyncio.run(main()))