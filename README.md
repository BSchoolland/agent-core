# agent-core
A framework for working with LLMs and creating agentic AI workflows compatible with MCP meant to replace my earlier ai-tools repo and power the v2v-chatbot-api, future AI projects, and work across both JavaScript and Python

## Features

- 🤖 Multi-provider support (OpenAI, Anthropic, Google Gemini, Ollama)
- 💬 Interactive CLI for chatting with models
- 📝 Conversation management with history
- 🛠️ Tool calling support
- 🎯 MCP (Model Context Protocol) compatibility

## Quick Start

### CLI Usage

Start chatting with any supported model:

```bash
# Make the CLI executable
chmod +x agentcore

# List available models
./agentcore list

# Chat with GPT-4o-mini
./agentcore run gpt-4o-mini

# Chat with Claude
./agentcore run claude-3-sonnet-20240229

# Chat with local Ollama model
./agentcore run gemma3:1b-it-qat

# Use a custom system prompt
./agentcore run gpt-4.1-mini --system-prompt "You are a helpful coding assistant"
```

### Programmatic Usage

```python
from core.chatbot.conversation import Conversation

# Create a conversation
conversation = Conversation(
    model="gpt-4o-mini",
    system_prompt="You are a helpful assistant"
)

# Generate a response
tool_calls, response = conversation.generate_response("Hello!")
print(response)
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For CLI usage (optional)
pip install -e .
```

## Environment Setup

Set up your API keys.  You ONLY need to set the API keys for the providers you want to use, so if you want to use Ollama, you can skip this step entirely.

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GEMINI_API_KEY="your-google-api-key"
# Ollama runs locally, no API key needed
```

## Local model setup (optional)

Local models are managed through the Ollama CLI. See [ollama.com](https://ollama.com/) for installation instructions.  

A model must be installed through the Ollama CLI before it can be used with agent-core.  You can install a model by running `ollama pull <model-name>` once Ollama is installed.

## Documentation

- [CLI Documentation](cli/README.md) - Detailed CLI usage and examples
- [Core Documentation](core/) - Framework internals and API reference
- [Examples](examples/) - Code examples for library usage

## Examples

Run the example script to see library usage:

```bash
python3 examples/basic_usage.py
```

This demonstrates:
- Simple conversations with automatic provider detection
- Using specific providers
- Multi-turn conversations with context
- Listing available models programmatically

## Supported Models

The framework automatically detects which models are actually available from each provider:

- **OpenAI**: All available models (gpt-4o, gpt-4o-mini, o1, etc.)
- **Anthropic**: All available Claude models (claude-3-5-sonnet, claude-3-haiku, etc.)
- **Google**: All available Gemini models (gemini-2.5-pro, gemini-2.5-flash, etc.)
- **Ollama**: Any and all locally installed models available through the Ollama CLI, from Meta, Google, DeepSeek, etc.

Use `./agentcore list` to see exactly which models are available on your system right now.
