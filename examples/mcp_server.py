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
mcp = FastMCP("Enhanced Productivity Tools")

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

# Text Processing Tools
@mcp.tool()
def count_words(text: str) -> int:
    """Count the number of words in text"""
    return len(text.split())

@mcp.tool()
def count_characters(text: str) -> int:
    """Count the number of characters in text"""
    return len(text)

@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse the given text"""
    return text[::-1]

@mcp.tool()
def uppercase_text(text: str) -> str:
    """Convert text to uppercase"""
    return text.upper()

@mcp.tool()
def lowercase_text(text: str) -> str:
    """Convert text to lowercase"""
    return text.lower()

@mcp.tool()
def find_and_replace(text: str, find: str, replace: str) -> str:
    """Find and replace text"""
    return text.replace(find, replace)

# Data Analysis Tools
@mcp.tool()
def calculate_average(numbers: str) -> float:
    """Calculate average of comma-separated numbers"""
    try:
        nums = [float(x.strip()) for x in numbers.split(',')]
        return sum(nums) / len(nums)
    except Exception as e:
        return f"Error calculating average: {str(e)}"

@mcp.tool()
def find_max(numbers: str) -> float:
    """Find maximum value in comma-separated numbers"""
    try:
        nums = [float(x.strip()) for x in numbers.split(',')]
        return max(nums)
    except Exception as e:
        return f"Error finding max: {str(e)}"

@mcp.tool()
def find_min(numbers: str) -> float:
    """Find minimum value in comma-separated numbers"""
    try:
        nums = [float(x.strip()) for x in numbers.split(',')]
        return min(nums)
    except Exception as e:
        return f"Error finding min: {str(e)}"

@mcp.tool()
def sort_numbers(numbers: str, ascending: bool = True) -> str:
    """Sort comma-separated numbers"""
    try:
        nums = [float(x.strip()) for x in numbers.split(',')]
        sorted_nums = sorted(nums, reverse=not ascending)
        return ', '.join(map(str, sorted_nums))
    except Exception as e:
        return f"Error sorting numbers: {str(e)}"

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
def hash_text(text: str, algorithm: str = "md5") -> str:
    """Generate hash of text using specified algorithm (md5, sha1, sha256)"""
    try:
        if algorithm == "md5":
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(text.encode()).hexdigest()
        else:
            return "Error: Unsupported algorithm. Use md5, sha1, or sha256"
    except Exception as e:
        return f"Error generating hash: {str(e)}"

@mcp.tool()
def sleep_seconds(seconds: int) -> str:
    """Sleep for specified number of seconds"""
    time.sleep(seconds)
    return f"Slept for {seconds} seconds"

# JSON Tools
@mcp.tool()
def create_json(data: str) -> str:
    """Create JSON from key-value pairs (format: key1=value1,key2=value2)"""
    try:
        pairs = data.split(',')
        result = {}
        for pair in pairs:
            key, value = pair.split('=', 1)
            result[key.strip()] = value.strip()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating JSON: {str(e)}"

@mcp.tool()
def parse_json(json_string: str) -> str:
    """Parse JSON and return formatted output"""
    try:
        data = json.loads(json_string)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error parsing JSON: {str(e)}"

# This is necessary to run the server in stdio mode
if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())

