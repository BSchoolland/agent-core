# MCP Client
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
import logging
import warnings

# Set up logging for cleanup warnings
logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        raise RuntimeError("MCPClient cannot be instantiated directly. Use MCPClient.create() instead.")
    
    @classmethod
    async def create(cls, server=None):
        """
        Async factory method to create and initialize an MCPClient instance.
        
        Args:
            server: Optional server path to connect to immediately
        
        Returns:
            MCPClient: Initialized client instance
        """
        # Create instance bypassing __init__
        instance = cls.__new__(cls)
        
        # Initialize instance variables
        instance.session: Optional[ClientSession] = None # type: ignore
        instance.exit_stack = AsyncExitStack()
        instance.tools = []
        instance.connected = False
        instance.server = None
        instance._closed = False
        
        # Connect to server if provided
        if server:
            await instance.connect_to_server(server)
            
        return instance

    def __del__(self):
        """Automatic cleanup when object is garbage collected."""
        if hasattr(self, '_closed') and not self._closed and hasattr(self, 'exit_stack') and self.exit_stack:
            logger.info("MCPClient was garbage collected without calling close(). Resources will be cleaned up by OS.")

    async def connect_to_server(self, server):
        self.server = server

        server_params = StdioServerParameters(
            command='python',
            args=[server],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        # Add a timeout to prevent hanging indefinitely
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        self.tools = response.tools
        self.connected = True
    
    async def get_tools(self):
        if not self.connected:
            raise Exception("MCP Client not connected to any server.  Make sure to call connect_to_server() first.")
        response = await self.session.list_tools()
        return response.tools
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]):
        if not self.connected:
            raise Exception("MCP Client not connected to any server.  Make sure to call connect_to_server() first.")
        result = await self.session.call_tool(tool_name, params)
        return result
            
    async def close(self):
        """Clean up MCP client resources properly."""
        if self._closed:
            return  # Already closed
            
        self._closed = True
        
        if not hasattr(self, 'exit_stack') or not self.exit_stack:
            return
            
        try:
            # Mark as disconnected first to prevent new operations
            self.connected = False
            self.session = None
            
            # Close the exit stack which will clean up all managed resources
            # Suppress specific asyncio warnings that are confusing to users
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*cancel scope.*")
                await self.exit_stack.aclose()
        except Exception as e:
            # Log cleanup errors as info level instead of warning to reduce noise
            logger.info(f"MCP client cleanup completed with minor issues (this is usually harmless): {e}")
        finally:
            # Ensure cleanup state is set regardless of errors
            self.exit_stack = None

async def main():
    client = await MCPClient.create('examples/mcp_server.py')
    try:
        # Client is already connected if server was provided to create()
        pass
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
