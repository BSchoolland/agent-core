# Agent Core CLI

A simple command-line interface for chatting with various AI models through different providers.

## Features

- 🤖 Support for multiple AI providers (OpenAI, Anthropic, Google Gemini, Ollama)
- 💬 Interactive chat sessions
- 🔧 Automatic provider detection based on model name
- 📝 Custom system prompts
- 🎯 Manual provider selection
- 📋 Dynamic model listing from all providers

## Installation

### For Development
```bash
# Make the script executable and run directly
chmod +x agentcore
./agentcore run gpt-4o-mini
```

### For Production
```bash
# Install the package
pip install -e .

# Use the installed command
agentcore run gpt-4o-mini
```

## Usage

### Basic Commands
```bash
# Start a chat with a specific model
agentcore run gpt-4o-mini
agentcore run claude-3-sonnet-20240229
agentcore run gemma3:1b-it-qat

# List all available models
agentcore list

# Show version
agentcore --version

# Get help
agentcore --help
agentcore run --help
```

### Advanced Usage
```bash
# Use a custom system prompt
agentcore run gpt-4o-mini --system-prompt "You are a helpful coding assistant"

# Force a specific provider
agentcore run gpt-4o-mini --provider openai
```

## Commands

### `agentcore run <model>`
Start an interactive chat session with the specified model.

**Options:**
- `--system-prompt TEXT`: Custom system prompt for the conversation
- `--provider PROVIDER`: Force a specific provider (openai, anthropic, google, ollama)

### `agentcore list`
List all available models from all configured providers. This command dynamically fetches the actual available models rather than showing static suggestions.

### `agentcore --version`
Show the current version of agent-core.


## Environment Setup

Make sure you have the necessary API key(s) for the models you want to use set up in your environment:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For Google Gemini
export GOOGLE_API_KEY="your-google-api-key"

# Ollama runs locally, no API key needed
```

## Interactive Commands

Once in a chat session:
- Type your message and press Enter to chat
- Type `quit`, `exit`, or `q` to end the session
- Press `Ctrl+C` to exit immediately

## Examples

```bash
# Quick chat with GPT-4o-mini
./agentcore run gpt-4o-mini

# Chat with Claude using a coding assistant prompt
./agentcore run claude-3-sonnet-20240229 --system-prompt "You are an expert Python developer"

# Use Ollama with a local model
./agentcore run gemma3:1b-it-qat

# List all available models first, then choose one
./agentcore list
./agentcore run devstral:latest
``` 