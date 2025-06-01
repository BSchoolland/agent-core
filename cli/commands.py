"""
Command implementations for the CLI.
"""

import sys
import os
import asyncio
from typing import Optional
import concurrent.futures

# Add the parent directory to the path so we can import from core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.chatbot.conversation import Conversation
from core.agent.agent import Agent


def chat_command(args):
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
    
    async def run_chat():
        try:
            # Initialize conversation
            conversation_kwargs = {
                'model': model,
                'system_prompt': system_prompt
            }
            if provider:
                conversation_kwargs['provider'] = provider
                
            conversation = await Conversation.create(**conversation_kwargs)
            
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
                    response = await conversation.generate_response(user_input)
                    
                    # Display response
                    print(f"\n🤖 {model}: {response}")
                    
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ Error generating response: {e}")
                    continue
            
            await conversation.close()
                    
        except ValueError as e:
            print(f"❌ Model error: {e}")
            _suggest_available_models()
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to initialize conversation: {e}")
            sys.exit(1)
    
    # Run the async function
    try:
        asyncio.run(run_chat())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)


def agent_command(args):
    """
    Run an AI agent with a specific goal.
    
    Args:
        args: Parsed command line arguments containing model, goal, system_prompt, provider, type, and mcp_servers
    """
    model = args.model
    goal = args.goal
    system_prompt = args.system_prompt
    provider = args.provider
    agent_type = args.type
    mcp_servers = args.mcp_servers
    
    print(f"🤖 Starting {agent_type} agent with {model}")
    print(f"🎯 Goal: {goal}")
    if system_prompt:
        print(f"📝 System prompt: {system_prompt}")
    if provider:
        print(f"🔧 Using provider: {provider}")
    if mcp_servers:
        print(f"🛠️ MCP servers: {', '.join(mcp_servers)}")
    print("-" * 50)
    
    async def run_agent():
        try:
            # Initialize agent
            agent_kwargs = {
                'model': model,
                'type': agent_type,
                'system_prompt': system_prompt
            }
            if provider:
                agent_kwargs['provider'] = provider
            if mcp_servers:
                agent_kwargs['mcp_servers'] = mcp_servers
                
            agent = await Agent.create(**agent_kwargs)
            
            print("🚀 Agent started, working on goal...")
            
            # Run the agent
            result = await agent.run(goal)
            
            # Display results
            print("\n" + "="*50)
            print("🏁 Agent completed!")
            print(f"📊 Status: {result['state']}")
            print(f"🔧 Agent type: {result['type']}")
            
            if result['state'] == 'success':
                print("✅ Goal achieved successfully!")
            elif result['state'] == 'failed':
                print("❌ Agent failed to complete the goal")
                if 'error' in result:
                    print(f"💥 Error: {result['error']}")
            
            # Show conversation history summary
            history = result.get('history', [])
            user_messages = [msg for msg in history if msg.get('role') == 'user' and not msg.get('temporary')]
            assistant_messages = [msg for msg in history if msg.get('role') == 'assistant']
            tool_messages = [msg for msg in history if msg.get('role') == 'tool']
            
            print(f"\n📈 Summary:")
            print(f"  • User messages: {len(user_messages)}")
            print(f"  • Assistant messages: {len(assistant_messages)}")
            print(f"  • Tool calls: {len(tool_messages)}")
            
            await agent.close()
            
        except ValueError as e:
            print(f"❌ Model error: {e}")
            _suggest_available_models()
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to run agent: {e}")
            sys.exit(1)
    
    # Run the async function
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\n🛑 Agent interrupted by user")
        sys.exit(0)


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
        print(f"\n💡 Usage:")
        print(f"  agentcore chat <model-name>")
        print(f"  agentcore agent <model-name> \"<goal>\"")
        
        # Show some example commands with actual available models
        examples = []
        for provider_name, models in provider_models.items():
            if models:
                # Pick the first model as an example
                example_model = sorted(models)[0]
                examples.append(f"agentcore chat {example_model}")
                examples.append(f"agentcore agent {example_model} \"Generate a random number and save it to a file\"")
        
        if examples:
            print(f"\n📝 Examples:")
            for example in examples[:4]:  # Show max 4 examples
                print(f"  {example}") 