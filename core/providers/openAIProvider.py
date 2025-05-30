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
            tool_calls = None  # Not implementing tool calls yet
            
            return tool_calls, message
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        

    def history_to_provider_format(self, history):
        # OpenAI format is already the standard format: [{"role": "system/user/assistant", "content": "..."}]
        return history

    def provider_to_std_history_format(self, provider_history):
        # OpenAI format is already the standard format
        return provider_history

    async def tools_to_provider_format(self, mcp_client):
        # Not implementing tool calls yet
        if mcp_client is None:
            return []
        tools = await mcp_client.get_tools()
        print('tools look like:', tools)
        # TODO: convert tools to OpenAI format
        return []  # Return empty list for now since tools aren't fully implemented