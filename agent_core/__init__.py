"""
Agent Core - A Python library for building AI agents with various providers and MCP support.

This library provides a unified interface for creating AI agents that can work with
different LLM providers (OpenAI, Anthropic, Google Gemini, Ollama) and integrate
with Model Context Protocol (MCP) servers for tool usage.
"""

from .agent.agent import Agent

__version__ = "1.0.0"
__all__ = ["Agent"] 