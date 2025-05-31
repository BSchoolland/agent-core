# agent-core
A framework for working with LLMs and creating agentic AI workflows compatible with [MCP](https://github.com/modelcontextprotocol) meant to replace my earlier ai-tools repo and power the v2v-chatbot-api, future AI projects, and work across both JavaScript and Python

## Features

- 🎯 AI agents in fewer than 20 lines of code
- 🛠️ Super easy MCP integration
- 🤖 Near universal support (OpenAI, Anthropic, Google Gemini, Ollama)
- 📝 Automatic conversation management with history

## Usage

### 1. Clone the Repository

``` bash
git clone https://github.com/BSchoolland/agent-core.git
cd agent-core
```

### 2. Environment Setup

Copy .env.example to a new file called .env and replace any of the three API keys with your actual key (which you'll need to obtain from the provider).  

``` bash
cp .env.example .env
```

For this example I'll use Gemini because as of June 2025 thir API has a free tier and obtaining an API key is super simple provided you have a Google account.

### 3. Installation

Set up a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependancies
``` bash
pip install -r requirements.txt

# For CLI usage (optional)
pip install -e .
```

### 4. Use AI Agents

``` python
from core.agent.agent import Agent
import asyncio

async def main():
    agent = await Agent.create(
        model='gemini-2.0-flash', # any valid model name you have access to
        mcp_servers=['examples/mcp_server.py']
    )
    await agent.run("Generate 2 random numbers between 1-100, add them together and save the result in a file called 'result.txt'")
    await agent.close()

if __name__ == '__main__':
    asyncio.run(main())
```


### 5. Profit

Claim your agents can replace all workers in 6 months and raise millions of dollars using pure AI hype.

## Local model setup (optional)

Local models are managed through the Ollama CLI. See [ollama.com](https://ollama.com/) for installation instructions.  

A model must be installed through the Ollama CLI before it can be used with agent-core.  You can install a model by running `ollama pull <model-name>` once Ollama is installed.

## Documentation

- [CLI Documentation](cli/README.md) - Detailed CLI usage and examples
- [Core Documentation](core/) - Framework internals and API reference
- [Examples](examples/) - Code examples for library usage and sample MCP server
- [FastMCP](https://github.com/jlowin/fastmcp) - Suggested framework for building MCP servers.  Note that you don't *have* to use this, you can use any MCP server you want.  I just think this is nice and easy.

## Supported Models

The framework automatically detects which models are actually available from each provider:

- **OpenAI**: All available models (gpt-4o, gpt-4o-mini, o1, etc.)
- **Anthropic**: All available Claude models (claude-3-5-sonnet, claude-3-haiku, etc.)
- **Google**: All available Gemini models (gemini-2.5-pro, gemini-2.5-flash, etc.)
- **Ollama**: All locally installed models available through the Ollama CLI, from Meta, Google, DeepSeek, etc.

Use `./agentcore list` to see exactly which models are available to your system right now.

## Roadmap
- Make this avalible as a python package
- CLI support for agents
- Multi-MCP server support, right now it's a one at a time thing
- Release as an npm package using a js wrapper
