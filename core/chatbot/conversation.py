import concurrent.futures
from difflib import get_close_matches
from core.providers.anthropicProvider import AnthropicProvider
from core.providers.googleGeminiProvider import GoogleGeminiProvider
from core.providers.ollamaProvider import OllamaProvider
from core.providers.openAIProvider import OpenAIProvider

class Conversation:
    def __init__(self, **kwargs):
        self.model = kwargs.get('model')
        self.provider = kwargs.get('provider') or self.infer_provider(self.model)
        self.system_prompt = kwargs.get('system_prompt') or None
        if self.system_prompt:
            self.history = [{'role': 'system', 'content': self.system_prompt}]
        else:
            self.history = []

    def infer_provider(self, model: str):
        """
        Infer which provider a model belongs to by checking all providers in parallel.
        Returns the appropriate provider instance or raises ValueError with suggestions.
        """
        # Initialize all providers
        providers = {
            'OpenAI': OpenAIProvider(),
            'Anthropic': AnthropicProvider(),
            'Google Gemini': GoogleGeminiProvider(),
            'Ollama': OllamaProvider()
        }
        
        # Function to get models from a single provider
        def get_provider_models(provider_name, provider_instance):
            try:
                models = provider_instance.list_models()
                return provider_name, models
            except Exception:
                return provider_name, []
        
        # Get all models from all providers in parallel
        provider_models = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_provider = {
                executor.submit(get_provider_models, name, provider): name 
                for name, provider in providers.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_provider):
                provider_name, models = future.result()
                provider_models[provider_name] = models
        
        # Check which provider contains the model
        for provider_name, models in provider_models.items():
            if model in models:
                return providers[provider_name]
        
        # If no exact match found throw ValueError
        raise ValueError(f"Model '{model}' not found.")
    


    def generate_response(self, message: str):
        self.history.append({'role': 'user', 'content': message})
        tool_calls, message = self.provider.generate_response(self.history, self.model)
        self.history.append({'role': 'assistant', 'content': message})
        return tool_calls, message
    
    