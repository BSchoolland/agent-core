# core/providers/anthropicProvider.py
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from .providerClass import Provider
import json

# Load environment variables from .env file
load_dotenv()

class AnthropicProvider(Provider):
    def __init__(self, API_KEY=None):
        super().__init__(API_KEY)
        if self.API_KEY is None:
            self.API_KEY = os.getenv('ANTHROPIC_API_KEY')
        
        if self.API_KEY:
            self.client = Anthropic(api_key=self.API_KEY)
            self.ready = True
        else:
            self.client = None
            self.ready = False

    def initialize(self):
        if not self.ready and self.API_KEY:
            self.client = Anthropic(api_key=self.API_KEY)
            self.ready = True

    def list_models(self):
        """List available models from Anthropic"""
        if not self.ready:
            return []
        
        try:
            # Use the Anthropic API to get the list of models
            response = self.client.models.list()
            
            # Extract model IDs from the response
            models = []
            for model in response.data:
                models.append(model.id)
            
            return models
        except Exception as e:
            print(f"Error fetching models from Anthropic API: {str(e)}")
            # Fallback to a basic list of known models if API call fails
            return [
                "claude-3-5-haiku-20241022",
                "claude-3-5-sonnet-20241022", 
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]

    async def generate_response(self, history, model, mcp_client=None):
        if not self.ready:
            raise Exception("Anthropic provider not ready. Please provide API key.")
        
        # Convert history to Anthropic format
        anthropic_history = self.history_to_provider_format(history)
        
        try:
            # Extract system message if present
            system_message = None
            messages = []
            
            for msg in anthropic_history:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    messages.append(msg)
            
            # Create the request
            kwargs = {
                "model": model,
                "max_tokens": 1024,
                "messages": messages
            }
            
            if system_message:
                kwargs["system"] = system_message
                
            # Add tools if available
            tools = await self.tools_to_provider_format(mcp_client) if mcp_client else []
            if tools:
                kwargs["tools"] = tools
            
            response = self.client.messages.create(**kwargs)
            
            # Extract message content and tool calls
            message_content = ""
            tool_calls = []
            
            for content_block in response.content:
                if content_block.type == "text":
                    message_content += content_block.text
                elif content_block.type == "tool_use":
                    tool_calls.append({
                        'id': content_block.id,
                        'name': content_block.name,
                        'parameters': json.dumps(content_block.input)
                    })
            
            return tool_calls, message_content
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def tool_calls_to_provider_format(self, tool_calls):
        """Convert standard tool calls to Anthropic format"""
        # Anthropic doesn't need this conversion in the same way as other providers
        # Tool calls are handled in the content blocks
        return tool_calls

    def history_to_provider_format(self, history):
        """Convert history to Anthropic format"""
        provider_history = []
        for message in history:
            if message.get('tool_calls'):
                # For assistant messages with tool calls
                content_blocks = []
                
                # Add text content if present
                if message.get('content'):
                    content_blocks.append({
                        "type": "text",
                        "text": message['content']
                    })
                
                # Add tool use blocks
                for tool_call in message['tool_calls']:
                    parameters = tool_call['parameters']
                    if isinstance(parameters, str):
                        try:
                            parameters = json.loads(parameters)
                        except json.JSONDecodeError:
                            parameters = {}
                    
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tool_call['id'],
                        "name": tool_call['name'],
                        "input": parameters
                    })
                
                formatted_message = {
                    'role': message['role'],
                    'content': content_blocks
                }
            elif message.get('role') == 'tool':
                # Tool result messages
                formatted_message = {
                    'role': 'user',
                    'content': [{
                        "type": "tool_result",
                        "tool_use_id": message['tool_call_id'],
                        "content": str(message['content'])
                    }]
                }
            else:
                # Regular messages (system, user, assistant without tool calls)
                # Only include standard fields that Anthropic API accepts
                formatted_message = {
                    'role': message['role'],
                    'content': message['content']
                }
                # Add any other standard fields if they exist
                if 'name' in message:
                    formatted_message['name'] = message['name']
            
            provider_history.append(formatted_message)
        return provider_history

    def provider_to_std_history_format(self, provider_history):
        """Convert Anthropic format to standard format"""
        return provider_history

    async def tools_to_provider_format(self, mcp_client):
        """Convert MCP tools to Anthropic format"""
        if mcp_client is None:
            return []
        
        tools = await mcp_client.get_tools()
        anthropic_tools = []
        
        for tool in tools:
            anthropic_tool = {
                "name": tool.name,
                "description": tool.description or "No description provided",
                "input_schema": tool.inputSchema
            }
            anthropic_tools.append(anthropic_tool)
        
        return anthropic_tools