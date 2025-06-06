# core/providers/openAIProvider.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from .providerClass import Provider

# Load environment variables from .env file
load_dotenv()

class OpenAIProvider(Provider):
    def __init__(self, API_KEY=None):
        super().__init__(API_KEY)
        if self.API_KEY is None:
            self.API_KEY = os.getenv('OPENAI_API_KEY')
        
        if self.API_KEY:
            self.client = OpenAI(api_key=self.API_KEY)
            self.ready = True
        else:
            self.client = None
            self.ready = False

    def initialize(self):
        if not self.ready and self.API_KEY:
            self.client = OpenAI(api_key=self.API_KEY)
            self.ready = True

    def list_models(self):
        """List available models from OpenAI"""
        if not self.ready:
            return []
        
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception:
            # Return empty list if API call fails
            return []

    async def generate_response(self, history, model, mcp_client=None):
        if not self.ready:
            raise Exception("OpenAI provider not ready. Please provide API key.")
        
        # Convert history to OpenAI format (already in correct format)
        openai_history = self.history_to_provider_format(history)
        
        try:
            tools = await self.tools_to_provider_format(mcp_client) if mcp_client else []
            response = self.client.chat.completions.create(
                model=model,
                messages=openai_history,
                tools=tools
            )
            
            message = response.choices[0].message.content
            tool_calls = self.provider_to_std_tool_calls_format(response.choices[0].message.tool_calls or [])
            return tool_calls, message
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def tool_calls_to_provider_format(self, tool_calls):

        provider_tool_calls = []
        for tool_call in tool_calls:
            provider_tool_calls.append({
                'id': tool_call['id'],
                'type': 'function',
                'function': {
                    'name': tool_call['name'],
                    'arguments': tool_call['parameters']
                }
            })
        return provider_tool_calls

    def history_to_provider_format(self, history):
        # Convert tool calls from history format to openai format
        provider_history = []
        for message in history:
            if message.get('tool_calls'):
                # For assistant messages with tool calls, content should be None
                formatted_message = {
                    'role': message['role'],
                    'content': None,
                    'tool_calls': self.tool_calls_to_provider_format(message['tool_calls'])
                }
            elif message.get('role') == 'tool':
                # Tool messages need special formatting
                formatted_message = {
                    'role': 'tool',
                    'tool_call_id': message['tool_call_id'],
                    'content': str(message['content'])  # Ensure content is a string
                }
            else:
                # Regular messages (system, user, assistant without tool calls)
                formatted_message = message.copy()
            
            provider_history.append(formatted_message)
        return provider_history

    def provider_to_std_history_format(self, provider_history):
        # OpenAI format is already the standard format
        return provider_history
    
    def provider_to_std_tool_calls_format(self, provider_tool_calls):
        # [ChatCompletionMessageToolCall(id='call_Wr7T6N0FLLphmxz2nRlaGCLq', function=Function(arguments='{"a":123,"b":456}', name='add'), type='function')]
        # to
        # [{'id': 'call_Wr7T6N0FLLphmxz2nRlaGCLq', 'parameters': '{"a":123,"b":456}', 'name': 'add'}]
        tool_calls = []
        for tool_call in provider_tool_calls:
            tool_calls.append({
                'id': tool_call.id,
                'parameters': tool_call.function.arguments,
                'name': tool_call.function.name
            })
        return tool_calls

    async def tools_to_provider_format(self, mcp_client):
        if mcp_client is None:
            return []
        tools = await mcp_client.get_tools()

        openai_tools = []
        for tool in tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "No description provided",
                    "parameters": tool.inputSchema
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools
