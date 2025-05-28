#!/usr/bin/env python3
"""
Main CLI entry point for agent-core.
"""

import sys
import argparse
from .commands import run_command, list_command
from . import __version__


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='agentcore',
        description='Agent Core CLI - Chat with AI models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentcore run gpt-4o-mini
  agentcore run claude-3-sonnet-20240229
  agentcore list
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'agentcore {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser(
        'run',
        help='Start a chat session with the specified model'
    )
    run_parser.add_argument(
        'model',
        help='Model name to use (e.g., gpt-4o-mini, claude-3-sonnet-20240229)'
    )
    run_parser.add_argument(
        '--system-prompt',
        help='System prompt to use for the conversation'
    )
    run_parser.add_argument(
        '--provider',
        help='Force a specific provider (openai, anthropic, google, ollama)'
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
        if args.command == 'run':
            run_command(args)
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