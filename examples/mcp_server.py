import subprocess
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

# Base directory for all file operations
TESTING_DIR = os.path.join(os.getcwd(), "testing")

def ensure_testing_dir():
    """Ensure the testing directory exists"""
    if not os.path.exists(TESTING_DIR):
        os.makedirs(TESTING_DIR)

def get_safe_path(filename: str) -> str:
    """Get a safe path within the testing directory"""
    ensure_testing_dir()
    # Remove any path traversal attempts and join with testing dir
    safe_filename = os.path.basename(filename)
    return os.path.join(TESTING_DIR, safe_filename)

def get_safe_directory_path(directory: str = ".") -> str:
    """Get a safe directory path within the testing directory"""
    ensure_testing_dir()
    if directory == "." or directory == "":
        return TESTING_DIR
    # Remove any path traversal attempts
    safe_dir = os.path.basename(directory)
    full_path = os.path.join(TESTING_DIR, safe_dir)
    # Ensure the directory exists
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path

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

# File Operations (all within /testing directory)
@mcp.tool()
def write_file(filename: str, content: str) -> str:
    """Write content to a file in the testing directory"""
    try:
        safe_path = get_safe_path(filename)
        with open(safe_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {os.path.relpath(safe_path, TESTING_DIR)} in testing directory"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@mcp.tool()
def read_file(filename: str) -> str:
    """Read content from a file in the testing directory"""
    try:
        safe_path = get_safe_path(filename)
        with open(safe_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List files in a directory within the testing directory"""
    try:
        safe_dir = get_safe_directory_path(directory)
        files = os.listdir(safe_dir)
        return json.dumps(files, indent=2)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
def file_exists(filename: str) -> bool:
    """Check if a file exists in the testing directory"""
    safe_path = get_safe_path(filename)
    return os.path.exists(safe_path)


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

