#!/usr/bin/env python3
"""
Setup script for agent-core library.
"""

from setuptools import setup, find_packages
import os

# Read version from agent_core/__init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'agent_core', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agent-core",
    version=get_version(),
    author="Agent Core Team",
    author_email="",
    description="A Python library for building AI agents with various LLM providers and MCP support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agent-core",  # Update with your actual repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai, agents, llm, openai, anthropic, gemini, ollama, mcp",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "cli": [
            "rich>=13.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agentcore=cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 