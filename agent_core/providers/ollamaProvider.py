# core/providers/ollamaProvider.py
import re
import ollama
from .providerClass import Provider
import json

class OllamaProvider(Provider):
    def __init__(self, API_KEY=None):
        super().__init__(API_KEY)
        # Ollama doesn't require an API key for local usage
        self.client = ollama.Client()
        self.ready = True

    def initialize(self):
        # Ollama is ready by default for local usage
        self.ready = True

    def list_models(self):
        """List available models from Ollama"""
        if not self.ready:
            return []
        
        try:
            response = self.client.list()
            # The response is a ListResponse object with a models attribute
            # Each model in the list has a .model attribute with the model name
            return [model.model for model in response.models]
        except Exception:
            # Return empty list if API call fails
            return []

    async def generate_response(self, history, model, mcp_client=None):
        if not self.ready:
            raise Exception("Ollama provider not ready.")
        
        # Convert history to Ollama format
        ollama_history = self.history_to_provider_format(history)
        
        try:
            tools = await self.tools_to_provider_format(mcp_client) if mcp_client else []
            
            response = self.client.chat(
                model=model,
                messages=ollama_history,
                tools=tools,
                options={
                    'num_ctx': 32768  # Increase context window from default 2048 to 32768 tokens
                }
            )
            
            message = response['message']['content']
            # filter out thinking in messages.  <think>thoughts</think>
            think, message = self.filter_thinking(message)
            tool_calls = self.provider_to_std_tool_calls_format(response['message'].get('tool_calls', []))
            print('tool calls:', tool_calls)
            return tool_calls, message
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def filter_thinking(self, message): #TODO: the think seems to be cut off a bit, but this does work for now
        """Filter out thinking in messages.  <think>thoughts</think>"""
        think = re.search(r'<think>(.*?)</think>', message, re.DOTALL)
        if think:
            message = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
        return think, message


    def tool_calls_to_provider_format(self, tool_calls):
        """Convert standard tool calls to Ollama format"""
        provider_tool_calls = []
        for tool_call in tool_calls:
            # Convert parameters from JSON string to dict if needed
            parameters = tool_call['parameters']
            if isinstance(parameters, str):
                try:
                    parameters = json.loads(parameters)
                except json.JSONDecodeError:
                    parameters = {}
            
            provider_tool_calls.append({
                'function': {
                    'name': tool_call['name'],
                    'arguments': parameters
                }
            })
        return provider_tool_calls

    def history_to_provider_format(self, history):
        """Convert history to Ollama format"""
        provider_history = []
        for message in history:
            if message.get('tool_calls'):
                # For assistant messages with tool calls
                formatted_message = {
                    'role': message['role'],
                    'content': message['content'] or '',
                    'tool_calls': self.tool_calls_to_provider_format(message['tool_calls'])
                }
            elif message.get('role') == 'tool':
                # Tool messages need special formatting
                formatted_message = {
                    'role': 'tool',
                    'content': str(message['content'])
                }
            else:
                # Regular messages (system, user, assistant without tool calls)
                formatted_message = message.copy()
            
            provider_history.append(formatted_message)
        return provider_history

    def provider_to_std_history_format(self, provider_history):
        """Convert Ollama format to standard format"""
        return provider_history
    
    def provider_to_std_tool_calls_format(self, provider_tool_calls):
        """Convert Ollama tool calls to standard format"""
        if not provider_tool_calls:
            return []
            
        tool_calls = []
        for tool_call in provider_tool_calls:
            # Convert arguments from dict to JSON string
            arguments = tool_call['function']['arguments']
            if isinstance(arguments, dict):
                arguments = json.dumps(arguments)
            
            tool_calls.append({
                'id': f"call_{hash(str(tool_call))}",  # Generate an ID since Ollama doesn't provide one
                'parameters': arguments,
                'name': tool_call['function']['name']
            })
        return tool_calls

    async def tools_to_provider_format(self, mcp_client):
        """Convert MCP tools to Ollama format"""
        if mcp_client is None:
            return []
        
        tools = await mcp_client.get_tools()
        ollama_tools = []
        
        for tool in tools:
            ollama_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "No description provided",
                    "parameters": tool.inputSchema
                }
            }
            ollama_tools.append(ollama_tool)
        
        return ollama_tools