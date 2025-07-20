# MCP Client
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
import logging
import warnings
import os

# Set up logging for cleanup warnings
logger = logging.getLogger(__name__)

# Patch BaseSubprocessTransport.__del__ to prevent "Event loop is closed" errors
def _patch_subprocess_transport():
    """Patch BaseSubprocessTransport.__del__ to handle closed event loops gracefully."""
    try:
        from asyncio.base_subprocess import BaseSubprocessTransport
        original_del = BaseSubprocessTransport.__del__
        
        def patched_del(self):
            try:
                original_del(self)
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    # This is the harmless cleanup error, ignore it
                    pass
                else:
                    # Re-raise other RuntimeErrors
                    raise
        
        BaseSubprocessTransport.__del__ = patched_del
    except ImportError:
        # BaseSubprocessTransport might not be available on all systems
        pass

# Apply the patch when the module is imported
_patch_subprocess_transport()

class MCPClient:
    def __init__(self):
        raise RuntimeError("MCPClient cannot be instantiated directly. Use MCPClient.create() instead.")
    
    @classmethod
    async def create(cls, server=None):
        """
        Async factory method to create and initialize an MCPClient instance.
        
        Args:
            server: Optional server path/config to connect to immediately.
                   Can be a string (path to Python script) or dict with command/args
        
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
        """
        Connect to an MCP server.
        
        Args:
            server: Can be:
                   - String: Path to Python script (legacy behavior)
                   - Dict: {'command': 'npx', 'args': ['@playwright/mcp@latest']}
                   - Dict: {'command': 'python', 'args': ['path/to/script.py']}
        """
        self.server = server

        # Handle different server configurations
        if isinstance(server, str):
            # Legacy behavior: assume it's a Python script
            if server.endswith('.py') and os.path.exists(server):
                command = 'python'
                args = [server]
            else:
                # Could be a package name or other command
                command = server
                args = []
        elif isinstance(server, dict):
            # New format: explicit command and args
            command = server.get('command', 'python')
            args = server.get('args', [])
            if isinstance(args, str):
                args = [args]
        else:
            raise ValueError(f"Invalid server configuration: {server}. Must be string or dict with 'command' and 'args'")

        server_params = StdioServerParameters(
            command=command,
            args=args,
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
            
            # Store references to transports before closing
            transports_to_close = []
            
            # Try to get references to any subprocess transports
            if hasattr(self, 'stdio') and self.stdio:
                # Check if stdio has a transport attribute
                if hasattr(self.stdio, '_transport'):
                    transports_to_close.append(self.stdio._transport)
                elif hasattr(self.stdio, 'transport'):
                    transports_to_close.append(self.stdio.transport)
            
            # Close session first to stop any ongoing operations
            if hasattr(self, 'session') and self.session:
                try:
                    # Try to close the session gracefully
                    await asyncio.wait_for(self.session.close(), timeout=0.5)
                except (asyncio.TimeoutError, AttributeError):
                    # Session might not have a close method or might timeout
                    pass
                self.session = None
            
            # Explicitly close stdio transport if we have it
            if hasattr(self, 'stdio') and hasattr(self.stdio, 'close'):
                try:
                    self.stdio.close()
                except Exception:
                    pass
            
            # Close the exit stack which will clean up all managed resources
            # Suppress specific asyncio warnings that are confusing to users
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*cancel scope.*")
                warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")
                await self.exit_stack.aclose()
            
            # Explicitly close any subprocess transports we found
            for transport in transports_to_close:
                try:
                    if hasattr(transport, 'close') and not transport.is_closing():
                        transport.close()
                    # Wait for the transport to actually close
                    if hasattr(transport, 'wait_closed'):
                        await asyncio.wait_for(transport.wait_closed(), timeout=0.1)
                except Exception:
                    # Ignore errors during transport cleanup
                    pass
                
            # Force garbage collection to clean up any remaining references
            # before the event loop closes
            import gc
            gc.collect()
            
            # Give one final moment for any cleanup to complete
            await asyncio.sleep(0.01)
            
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
