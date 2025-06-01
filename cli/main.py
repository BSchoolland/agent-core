#!/usr/bin/env python3
"""
Main CLI entry point for agent-core.
"""

import sys
import argparse
from .commands import chat_command, agent_command, list_command
from . import __version__


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='agentcore',
        description='Agent Core CLI - Chat with AI models and run AI agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentcore chat gpt-4o-mini
  agentcore agent gpt-4o-mini "Generate 2 random numbers and save to file"
  agentcore list
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'agentcore {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Chat command (replaces run)
    chat_parser = subparsers.add_parser(
        'chat',
        help='Start an interactive chat session with the specified model'
    )
    chat_parser.add_argument(
        'model',
        help='Model name to use (e.g., gpt-4o-mini, claude-3-sonnet-20240229)'
    )
    chat_parser.add_argument(
        '--system-prompt',
        help='System prompt to use for the conversation'
    )
    chat_parser.add_argument(
        '--provider',
        help='Force a specific provider (openai, anthropic, google, ollama)'
    )
    
    # Agent command (new)
    agent_parser = subparsers.add_parser(
        'agent',
        help='Run an AI agent with a specific goal'
    )
    agent_parser.add_argument(
        'model',
        help='Model name to use (e.g., gpt-4o-mini, claude-3-sonnet-20240229)'
    )
    agent_parser.add_argument(
        'goal',
        help='The goal for the agent to accomplish'
    )
    agent_parser.add_argument(
        '--system-prompt',
        help='System prompt to use for the agent'
    )
    agent_parser.add_argument(
        '--provider',
        help='Force a specific provider (openai, anthropic, google, ollama)'
    )
    agent_parser.add_argument(
        '--type',
        choices=['react', 'planner', 'hybrid', 'simple'],
        default='react',
        help='Type of agent to use (default: react)'
    )
    agent_parser.add_argument(
        '--mcp-servers',
        nargs='+',
        help='MCP servers to connect to (space-separated list)'
    )
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List all available models from all providers'
    )
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'chat':
            chat_command(args)
        elif args.command == 'agent':
            agent_command(args)
        elif args.command == 'list':
            list_command(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 