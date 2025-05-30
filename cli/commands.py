"""
Command implementations for the CLI.
"""

import sys
import os
from typing import Optional
import concurrent.futures

# Add the parent directory to the path so we can import from core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.chatbot.conversation import Conversation


def run_command(args):
    """
    Start an interactive chat session with the specified model.
    
    Args:
        args: Parsed command line arguments containing model, system_prompt, and provider
    """
    model = args.model
    system_prompt = args.system_prompt
    provider = args.provider
    
    print(f"🤖 Starting chat session with {model}")
    if system_prompt:
        print(f"📝 System prompt: {system_prompt}")
    if provider:
        print(f"🔧 Using provider: {provider}")
    print("💬 Type 'quit', 'exit', or press Ctrl+C to end the session")
    print("-" * 50)
    
    try:
        # Initialize conversation
        conversation_kwargs = {
            'model': model,
            'system_prompt': system_prompt
        }
        if provider:
            conversation_kwargs['provider'] = _get_provider_instance(provider)
            
        conversation = Conversation(**conversation_kwargs)
        
        # Start interactive loop
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 Thinking...")
                
                # Generate response
                tool_calls, response = conversation.generate_response(user_input)
                
                # Display response
                print(f"\n🤖 {model}: {response}")
                
                # Display tool calls if any
                if tool_calls:
                    print(f"\n🔧 Tool calls made: {len(tool_calls)}")
                    for i, tool_call in enumerate(tool_calls, 1):
                        print(f"  {i}. {tool_call.get('function', {}).get('name', 'Unknown tool')}")
                
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error generating response: {e}")
                continue
                
    except ValueError as e:
        print(f"❌ Model error: {e}")
        _suggest_available_models()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to initialize conversation: {e}")
        sys.exit(1)


def list_command(args):
    """List all available models from all providers."""
    print("🔍 Fetching available models from all providers...")
    _suggest_available_models()


def _get_provider_instance(provider_name: str):
    """Get a provider instance by name."""
    from core.providers.anthropicProvider import AnthropicProvider
    from core.providers.googleGeminiProvider import GoogleGeminiProvider
    from core.providers.ollamaProvider import OllamaProvider
    from core.providers.openAIProvider import OpenAIProvider
    
    providers = {
        'openai': OpenAIProvider(),
        'anthropic': AnthropicProvider(),
        'google': GoogleGeminiProvider(),
        'ollama': OllamaProvider()
    }
    
    provider_name = provider_name.lower()
    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {', '.join(providers.keys())}")
    
    return providers[provider_name]


def _suggest_available_models():
    """Dynamically fetch and suggest available models from all providers."""
    from core.providers.anthropicProvider import AnthropicProvider
    from core.providers.googleGeminiProvider import GoogleGeminiProvider
    from core.providers.ollamaProvider import OllamaProvider
    from core.providers.openAIProvider import OpenAIProvider
    
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
        except Exception as e:
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
    
    print("\n💡 Available models:")
    
    # Display models by provider
    found_models = False
    for provider_name, models in provider_models.items():
        if models:
            found_models = True
            print(f"\n{provider_name}:")
            for model in sorted(models):
                print(f"  • {model}")
        else:
            print(f"\n{provider_name}: No models available (check API key or connection)")
    
    if not found_models:
        print("\n❌ No models found from any provider.")
        print("Please check your API keys and internet connection.")
        print("\nRequired environment variables:")
        print("  • OPENAI_API_KEY for OpenAI models")
        print("  • ANTHROPIC_API_KEY for Anthropic models") 
        print("  • GEMINI_API_KEY for Google Gemini models")
        print("  • Ollama should be running locally for Ollama models")
    else:
        print(f"\n💡 Usage: agentcore run <model-name>")
        
        # Show some example commands with actual available models
        examples = []
        for provider_name, models in provider_models.items():
            if models:
                # Pick the first model as an example
                example_model = sorted(models)[0]
                examples.append(f"agentcore run {example_model}")
        
        if examples:
            print(f"\n📝 Examples:")
            for example in examples[:3]:  # Show max 3 examples
                print(f"  {example}") 