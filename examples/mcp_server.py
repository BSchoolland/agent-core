from mcp.server.fastmcp import FastMCP
import asyncio
import logging
import json
import os
import random
import time
from datetime import datetime
import hashlib

# Silence FastMCP debug messages
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("fastmcp").setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.WARNING)

# Create an enhanced MCP server
mcp = FastMCP("Example MCP Server")

# Math Tools
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    if b == 0:
        return "Error: Division by zero"
    return a / b

@mcp.tool()
def power(base: int, exponent: int) -> int:
    """Calculate base raised to the power of exponent"""
    return base ** exponent

@mcp.tool()
def factorial(n: int) -> int:
    """Calculate factorial of a number"""
    if n < 0:
        return "Error: Factorial not defined for negative numbers"
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# File Operations
@mcp.tool()
def write_file(filename: str, content: str) -> str:
    """Write content to a file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@mcp.tool()
def read_file(filename: str) -> str:
    """Read content from a file"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List files in a directory"""
    try:
        files = os.listdir(directory)
        return json.dumps(files, indent=2)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
def file_exists(filename: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(filename)


# Utility Tools
@mcp.tool()
def generate_random_number(min_val: int = 1, max_val: int = 100) -> int:
    """Generate a random number between min_val and max_val"""
    return random.randint(min_val, max_val)

@mcp.tool()
def get_current_time() -> str:
    """Get current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def sleep_seconds(seconds: int) -> str:
    """Sleep for specified number of seconds"""
    time.sleep(seconds)
    return f"Slept for {seconds} seconds"

# This is necessary to run the server in stdio mode
if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())

