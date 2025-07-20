from mcp.server.fastmcp import FastMCP
import asyncio
import logging
from datetime import datetime

# Silence FastMCP debug messages
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("fastmcp").setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.WARNING)

# Create an enhanced MCP server
mcp = FastMCP("Example MCP Server")

@mcp.tool()
def get_current_time() -> str:
    """Get current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# This is necessary to run the server in stdio mode
if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())

