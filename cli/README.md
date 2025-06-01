# Agent Core CLI

A command-line interface for chatting with AI models and running AI agents with specific goals.

## Features

- 🤖 Support for multiple AI providers (OpenAI, Anthropic, Google Gemini, Ollama)
- 💬 Interactive chat sessions
- 🎯 AI agents that can accomplish specific goals
- 🛠️ MCP (Model Context Protocol) server integration for agents
- 🔧 Automatic provider detection based on model name
- 📝 Custom system prompts
- 🎯 Manual provider selection
- 📋 Dynamic model listing from all providers

## Installation

### For Development
```bash
# Make the script executable and run directly
chmod +x agentcore
./agentcore chat gpt-4o-mini
```

### For Production
```bash
# Install the package
pip install -e .

# Use the installed command
agentcore chat gpt-4o-mini
```

## Usage

### Basic Commands
```bash
# Start a chat with a specific model
agentcore chat gpt-4o-mini
agentcore chat claude-3-sonnet-20240229
agentcore chat gemma3:1b-it-qat

# Run an agent with a goal
agentcore agent gpt-4o-mini "Generate 2 random numbers and save to file"
agentcore agent claude-3-sonnet-20240229 "Analyze the current directory structure"

# List all available models
agentcore list

# Show version
agentcore --version

# Get help
agentcore --help
agentcore chat --help
agentcore agent --help
```

### Advanced Usage
```bash
# Chat with a custom system prompt
agentcore chat gpt-4o-mini --system-prompt "You are a helpful coding assistant"

# Force a specific provider for chat
agentcore chat gpt-4o-mini --provider openai

# Run an agent with specific configuration
agentcore agent gpt-4o-mini "Create a Python script" --type planner --system-prompt "You are an expert Python developer"

# Run an agent with MCP servers
agentcore agent gpt-4o-mini "Analyze files in current directory" --mcp-servers examples/mcp_server.py
```

## Commands

### `agentcore chat <model>`
Start an interactive chat session with the specified model.

**Options:**
- `--system-prompt TEXT`: Custom system prompt for the conversation
- `--provider PROVIDER`: Force a specific provider (openai, anthropic, google, ollama)

### `agentcore agent <model> <goal>`
Run an AI agent with a specific goal. The agent will work autonomously to accomplish the goal.

**Arguments:**
- `model`: Model name to use
- `goal`: The goal for the agent to accomplish (should be quoted if it contains spaces)

**Options:**
- `--system-prompt TEXT`: Custom system prompt for the agent
- `--provider PROVIDER`: Force a specific provider (openai, anthropic, google, ollama)
- `--type TYPE`: Type of agent to use (react, planner, hybrid, simple). Default: react
- `--mcp-servers SERVER [SERVER ...]`: MCP servers to connect to (space-separated list)

**Agent Types:**
- `react`: Follows the pattern reason→act→reason→act... (default, great for most tasks)
- `planner`: Follows the pattern plan→act→act→act... (ideal for straightforward tasks)
- `hybrid`: Follows the pattern plan→reason→act→reason→act... (best for complex, well-defined tasks)
- `simple`: Follows the pattern act→act→act... (faster and cheaper for simple tasks)

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
export GEMINI_API_KEY="your-google-api-key"

# Ollama runs locally, no API key needed
```

## Interactive Commands

### Chat Session Commands
Once in a chat session:
- Type your message and press Enter to chat
- Type `quit`, `exit`, or `q` to end the session
- Press `Ctrl+C` to exit immediately

### Agent Execution
Agents run autonomously and will:
- Display their progress as they work
- Show a summary when complete
- Automatically stop when the goal is achieved or if they encounter an error
- Can be interrupted with `Ctrl+C`

## Examples

```bash
# Quick chat with GPT-4o-mini
./agentcore chat gpt-4o-mini

# Chat with Claude using a coding assistant prompt
./agentcore chat claude-3-sonnet-20240229 --system-prompt "You are an expert Python developer"

# Use Ollama with a local model for chat
./agentcore chat gemma3:1b-it-qat

# Run a simple agent task
./agentcore agent gpt-4o-mini "Create a file called hello.txt with 'Hello World' in it"

# Run a planner agent with a more complex task
./agentcore agent claude-3-sonnet-20240229 "Analyze all Python files in the current directory and create a summary report" --type planner

# Run an agent with MCP server integration
./agentcore agent gpt-4o-mini "Generate random numbers and perform calculations" --mcp-servers examples/mcp_server.py

# List all available models first, then choose one
./agentcore list
./agentcore agent devstral:latest "Write a simple Python function to calculate fibonacci numbers"
``` 