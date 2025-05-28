# core/providers/googleGeminiProvider.py
import os
from dotenv import load_dotenv
from google import genai
from .providerClass import Provider

# Load environment variables from .env file
load_dotenv()

class GoogleGeminiProvider(Provider):
    def __init__(self, API_KEY=None):
        super().__init__(API_KEY)
        if self.API_KEY is None:
            self.API_KEY = os.getenv('GOOGLE_API_KEY')
        
        if self.API_KEY:
            self.client = genai.Client(api_key=self.API_KEY)
            self.ready = True
        else:
            self.client = None
            self.ready = False

    def initialize(self):
        if not self.ready and self.API_KEY:
            self.client = genai.Client(api_key=self.API_KEY)
            self.ready = True

    def list_models(self):
        """List available models from Google Gemini"""
        if not self.ready:
            return []
        
        try:
            models = self.client.models.list()
            return [model.name.replace('models/', '') for model in models]
        except Exception:
            # Return empty list if API call fails
            return []

    def generate_response(self, history, model):
        if not self.ready:
            raise Exception("Google Gemini provider not ready. Please provide API key.")
        
        # Convert history to Gemini format
        gemini_history = self.history_to_provider_format(history)
        
        try:
            # Create a chat session
            chat = self.client.chats.create(model=model)
            
            # Send all messages in history except the last one
            for msg in gemini_history[:-1]:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
                elif msg["role"] == "assistant":
                    # For assistant messages, we need to simulate the response
                    pass
            
            # Send the last message and get response
            last_message = gemini_history[-1]
            if last_message["role"] == "user":
                response = chat.send_message(last_message["content"])
                message = response.text
            else:
                # If last message is not from user, just return it
                message = last_message["content"]
            
            tool_calls = None  # Not implementing tool calls yet
            
            return tool_calls, message
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")

    def history_to_provider_format(self, history):
        # Convert standard format to Gemini format
        # Gemini uses the same structure but may handle system messages differently
        gemini_history = []
        
        for msg in history:
            if msg["role"] == "system":
                # Convert system message to user message with instruction prefix
                gemini_history.append({
                    "role": "user",
                    "content": f"System instruction: {msg['content']}"
                })
            else:
                gemini_history.append(msg)
        
        return gemini_history

    def provider_to_std_history_format(self, provider_history):
        # Convert Gemini format back to standard format
        standard_history = []
        
        for msg in provider_history:
            if msg["role"] == "user" and msg["content"].startswith("System instruction: "):
                # Convert back to system message
                standard_history.append({
                    "role": "system",
                    "content": msg["content"][19:]  # Remove "System instruction: " prefix
                })
            else:
                standard_history.append(msg)
        
        return standard_history

    def tool_to_provider_format(self, tool):
        # Not implementing tool calls yet
        return tool