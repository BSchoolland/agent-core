# core/providers/anthropicProvider.py
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from .providerClass import Provider

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

    def generate_response(self, history, model):
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
            
            response = self.client.messages.create(**kwargs)
            
            message = response.content[0].text
            tool_calls = None  # Not implementing tool calls yet
            
            return tool_calls, message
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def history_to_provider_format(self, history):
        # Anthropic uses the same format as OpenAI: [{"role": "system/user/assistant", "content": "..."}]
        return history

    def provider_to_std_history_format(self, provider_history):
        # Anthropic format is the same as standard format
        return provider_history

    def tool_to_provider_format(self, tool):
        # Not implementing tool calls yet
        return tool