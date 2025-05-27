# core/providers/ollamaProvider.py
import ollama
from .providerClass import Provider

class OllamaProvider(Provider):
    def __init__(self, API_KEY=None):
        super().__init__(API_KEY)
        # Ollama doesn't require an API key for local usage
        self.client = ollama.Client()
        self.ready = True

    def initialize(self):
        # Ollama is ready by default for local usage
        self.ready = True

    def generate_response(self, history, model):
        if not self.ready:
            raise Exception("Ollama provider not ready.")
        
        # Convert history to Ollama format
        ollama_history = self.history_to_provider_format(history)
        
        try:
            response = self.client.chat(
                model=model,
                messages=ollama_history
            )
            
            message = response['message']['content']
            tool_calls = None  # Not implementing tool calls yet
            
            return tool_calls, message
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def history_to_provider_format(self, history):
        # Ollama uses the same format as OpenAI: [{"role": "system/user/assistant", "content": "..."}]
        return history

    def provider_to_std_history_format(self, provider_history):
        # Ollama format is the same as standard format
        return provider_history

    def tool_to_provider_format(self, tool):
        # Not implementing tool calls yet
        return tool