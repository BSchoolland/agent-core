import concurrent.futures
from difflib import get_close_matches
from core.providers.anthropicProvider import AnthropicProvider
from core.providers.googleGeminiProvider import GoogleGeminiProvider
from core.providers.ollamaProvider import OllamaProvider
from core.providers.openAIProvider import OpenAIProvider
from core.mcp.client import MCPClient
import asyncio
import logging
import json

# Set up logging for cleanup warnings
logger = logging.getLogger(__name__)

class Conversation:
    def __init__(self):
        raise RuntimeError("Conversation cannot be instantiated directly. Use Conversation.create() instead.")
    
    @classmethod
    async def create(cls, **kwargs):
        """
        Async factory method to create and initialize a Conversation instance.
        
        Args:
            model: The model to use
            provider: The provider to use (optional, will be inferred if not provided)
            system_prompt: System prompt for the conversation (optional)
            mcp_servers: List of MCP servers to connect to (optional)
        
        Returns:
            Conversation: Initialized conversation instance
        """
        # Create instance bypassing __init__
        instance = cls.__new__(cls)
        
        # Initialize instance variables
        instance.model = kwargs.get('model')
        instance._closed = False
        
        # Handle provider - can be string name or provider instance
        provider_param = kwargs.get('provider')
        if provider_param:
            if isinstance(provider_param, str):
                instance.provider = instance._get_provider_by_name(provider_param)
            else:
                instance.provider = provider_param
        else:
            instance.provider = await instance.infer_provider(instance.model)
            
        instance.system_prompt = kwargs.get('system_prompt') or None
        if instance.system_prompt:
            instance.history = [{'role': 'system', 'content': instance.system_prompt}]
        else:
            instance.history = []
        
        instance.mcp_servers = kwargs.get('mcp_servers') or None
        # FIXME: accept multiple mcp servers
        if instance.mcp_servers:
            instance.mcp_client = await MCPClient.create(instance.mcp_servers[0])
        else:
            instance.mcp_client = None
            
        return instance

    def __del__(self):
        """Automatic cleanup when object is garbage collected."""
        if hasattr(self, '_closed') and not self._closed and hasattr(self, 'mcp_client') and self.mcp_client:
            # Log a helpful warning instead of failing silently
            logger.warning(
                "Conversation was garbage collected without calling close(). "
                "For best practices, call 'await conversation.close()' when done. "
                "Attempting automatic cleanup..."
            )
            # Try to schedule cleanup, but don't fail if event loop is closed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule cleanup for next iteration
                    loop.create_task(self._safe_close())
                else:
                    # Event loop is not running, can't do async cleanup
                    logger.info("Event loop not running, skipping async cleanup")
            except RuntimeError:
                # No event loop available, that's okay
                logger.info("No event loop available for cleanup, resources will be cleaned up by OS")

    async def _safe_close(self):
        """Internal method for safe cleanup that won't raise exceptions."""
        try:
            await self.close()
        except Exception as e:
            logger.warning(f"Error during automatic cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        await self.close()
    
    async def close(self):
        """Clean up resources, especially MCP client connections."""
        if self._closed:
            return  # Already closed
            
        self._closed = True
        if hasattr(self, 'mcp_client') and self.mcp_client:
            await self.mcp_client.close()
            self.mcp_client = None

    def _get_provider_by_name(self, provider_name: str):
        """
        Get provider instance by name.
        """
        providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'google': GoogleGeminiProvider(),
            'gemini': GoogleGeminiProvider(),
            'ollama': OllamaProvider()
        }
        
        provider_name_lower = provider_name.lower()
        if provider_name_lower in providers:
            return providers[provider_name_lower]
        else:
            raise ValueError(f"Unknown provider: {provider_name}. Available providers: {list(providers.keys())}")

    async def infer_provider(self, model: str): 
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
        # FIXME: this is not the right way to do this in async
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
    


    async def generate_response(self, message: str):
        if self._closed:
            raise RuntimeError("Cannot use conversation after it has been closed")

        self.history.append({'role': 'user', 'content': message})

        while True:
            tool_calls, assistant_message = await self.provider.generate_response(self.history, self.model, self.mcp_client)

            if tool_calls:
                # Append the assistant's tool call message
                self.history.append({
                    'role': 'assistant',
                    'content': assistant_message,
                    'tool_calls': tool_calls
                })
                if assistant_message:
                    print('TODO: implement a solution to handle simultaneous tool calls + assistant message.  Current implementation simply ignores the assistant message.')

                for tool_call in tool_calls:
                    # Handle both string (OpenAI) and dict (Gemini) parameter formats
                    parameters = tool_call['parameters']
                    if isinstance(parameters, str):
                        parameters = json.loads(parameters)
                    
                    result = await self.mcp_client.call_tool(
                        tool_call['name'],
                        parameters
                    )

                    # Append tool result message
                    self.history.append({
                        'role': 'tool',
                        'tool_call_id': tool_call['id'],
                        'content': result
                    })
            else:
                # Final assistant message after tool calls
                self.history.append({'role': 'assistant', 'content': assistant_message})
                return assistant_message

    
    