from mcp.server.fastmcp import FastMCP
import asyncio

# Create an example MCP server
mcp = FastMCP("Basic Math Tools")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    # log the tool call to a file to confirm it's working
    with open('tool_calls.txt', 'a') as f:
        f.write(f"add({a}, {b})\n")
    """Add two numbers"""
    return a + b

# Add a subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

# Add a multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# Add a division tool
@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    return a / b

# This is necessary to run the server in stdio mode
if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())

