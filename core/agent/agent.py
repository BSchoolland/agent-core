import concurrent.futures
from difflib import get_close_matches
from core.providers.anthropicProvider import AnthropicProvider
from core.providers.googleGeminiProvider import GoogleGeminiProvider
from core.providers.ollamaProvider import OllamaProvider
from core.providers.openAIProvider import OpenAIProvider
from core.mcp.client import MCPClient
import asyncio
import logging
import json
import traceback

# Set up logging for cleanup warnings
logger = logging.getLogger(__name__)
# Set up more detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# possible states for an agent
AGENT_STATE_WORKING = 'working'
AGENT_STATE_SUCCESS = 'success'
AGENT_STATE_FAILED = 'failed'
AGENT_STATE_CANCELLED = 'cancelled'

# Class for performing agentic workflows
class Agent:
    def __init__(self):
        raise RuntimeError("Agent cannot be instantiated directly. Use Agent.create() instead.")
    
    @classmethod
    async def create(cls, **kwargs):
        """
        Async factory method to create and initialize a Agent instance.
        
        Args:
            model: The model to use
            provider: The provider to use (optional, will be inferred if not provided)
            system_prompt: System prompt for the conversation (optional)
            mcp_servers: List of MCP servers to connect to (optional)
        
        Returns:
            Agent: Initialized agent instance
        """
        # Create instance bypassing __init__
        instance = cls.__new__(cls)
        
        # Initialize instance variables
        instance.model = kwargs.get('model')
        instance._closed = False
        
        # Handle provider - can be string name or provider instance
        provider_param = kwargs.get('provider')
        if provider_param:
            if isinstance(provider_param, str):
                instance.provider = instance._get_provider_by_name(provider_param)
            else:
                instance.provider = provider_param
        else:
            instance.provider = await instance.infer_provider(instance.model)
            
        instance.system_prompt = kwargs.get('system_prompt') or None
        if instance.system_prompt:
            instance.history = [{'role': 'system', 'content': instance.system_prompt}]
        else:
            instance.history = []
        
        instance.mcp_servers = kwargs.get('mcp_servers') or None
        # FIXME: accept multiple mcp servers
        if instance.mcp_servers:
            instance.mcp_client = await MCPClient.create(instance.mcp_servers[0])
        else:
            instance.mcp_client = None
        # agent type
        type = kwargs.get('type') or 'react'
        if type == 'react':
            instance.run = instance.react_run
        elif type == 'planner':
            instance.run = instance.planner_run
        elif type == 'hybrid':
            instance.run = instance.hybrid_run
        elif type == 'simple':
            instance.run = instance.simple_run
        else:
            raise ValueError(f"Unknown agent type: {type} (must be one of 'react', 'planner', 'hybrid', 'simple')")
        return instance

    def __del__(self):
        """Automatic cleanup when object is garbage collected."""
        if hasattr(self, '_closed') and not self._closed and hasattr(self, 'mcp_client') and self.mcp_client:
            # Log a helpful warning instead of failing silently
            logger.warning(
                "Agent was garbage collected without calling close(). "
                "For best practices, call 'await agent.close()' when done. "
                "Attempting automatic cleanup..."
            )
            # Try to schedule cleanup, but don't fail if event loop is closed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule cleanup for next iteration
                    loop.create_task(self._safe_close())
                else:
                    # Event loop is not running, can't do async cleanup
                    logger.info("Event loop not running, skipping async cleanup")
            except RuntimeError:
                # No event loop available, that's okay
                logger.info("No event loop available for cleanup, resources will be cleaned up by OS")

    async def _safe_close(self):
        """Internal method for safe cleanup that won't raise exceptions."""
        try:
            await self.close()
        except Exception as e:
            logger.warning(f"Error during automatic cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        await self.close()
    
    async def close(self):
        """Clean up resources, especially MCP client connections."""
        if self._closed:
            return  # Already closed
            
        self._closed = True
        if hasattr(self, 'mcp_client') and self.mcp_client:
            await self.mcp_client.close()
            self.mcp_client = None

    def _get_provider_by_name(self, provider_name: str):
        """
        Get provider instance by name.
        """
        providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'google': GoogleGeminiProvider(),
            'gemini': GoogleGeminiProvider(),
            'ollama': OllamaProvider()
        }
        
        provider_name_lower = provider_name.lower()
        if provider_name_lower in providers:
            return providers[provider_name_lower]
        else:
            raise ValueError(f"Unknown provider: {provider_name}. Available providers: {list(providers.keys())}")

    async def infer_provider(self, model: str): 
        """
        Infer which provider a model belongs to by checking all providers in parallel.
        Returns the appropriate provider instance or raises ValueError with suggestions.
        """
        # Initialize all providers
        providers = { 
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'google': GoogleGeminiProvider(),
            'ollama': OllamaProvider()
        }
        
        # Function to get models from a single provider
        def get_provider_models(provider_name, provider_instance):
            try:
                models = provider_instance.list_models()
                return provider_name, models
            except Exception:
                return provider_name, []
        
        # Get all models from all providers in parallel
        provider_models = {}
        # FIXME: this is not the right way to do this in async
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: 
            future_to_provider = {
                executor.submit(get_provider_models, name, provider): name 
                for name, provider in providers.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_provider):
                provider_name, models = future.result()
                provider_models[provider_name] = models
        
        # Check which provider contains the model
        for provider_name, models in provider_models.items():
            if model in models:
                return providers[provider_name]
        
        # If no exact match found throw ValueError
        raise ValueError(f"Model '{model}' not found.")
    


    def setGoal(self, goal: str):
        self.history.append({'role': 'user', 'content': f"Your goal is: {goal}"})

    # run method, overwritted by .create() based on agent type
    async def run(self, goal: str):
        pass

    # simple run achitecture, used by Simple agents
    async def simple_run(self, goal: str):
        try:
            self.setGoal(goal)
            state = AGENT_STATE_WORKING
            while state == AGENT_STATE_WORKING:
                await self.act()
                state = await self.check_completion()
            return {'history': self.history, 'state': state, 'type': 'simple'}
        except Exception as e:
            return {'history': self.history, 'state': AGENT_STATE_FAILED, 'error': str(e), 'type': 'simple'}

    # ReAct run achitecture, used by ReAct agents
    async def react_run(self, goal: str):
        try:
            logger.info(f"Starting ReAct run with goal: {goal}")
            self.setGoal(goal)
            state = AGENT_STATE_WORKING
            step_count = 0
            max_steps = 20  # Prevent infinite loops
            
            while state == AGENT_STATE_WORKING and step_count < max_steps:
                step_count += 1
                logger.info(f"ReAct step {step_count}: Starting reason phase")
                try:
                    await self.reason()
                    logger.info(f"ReAct step {step_count}: Reason phase completed")
                except Exception as e:
                    logger.error(f"ReAct step {step_count}: Error in reason phase: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise
                
                logger.info(f"ReAct step {step_count}: Starting act phase")
                try:
                    await self.act()
                    logger.info(f"ReAct step {step_count}: Act phase completed")
                except Exception as e:
                    logger.error(f"ReAct step {step_count}: Error in act phase: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise
                
                logger.info(f"ReAct step {step_count}: Checking completion")
                try:
                    state = await self.check_completion()
                    logger.info(f"ReAct step {step_count}: Completion check result: {state}")
                except Exception as e:
                    logger.error(f"ReAct step {step_count}: Error in completion check: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise
            
            if step_count >= max_steps:
                logger.warning(f"ReAct agent reached maximum steps ({max_steps})")
                state = AGENT_STATE_FAILED
                
            logger.info(f"ReAct run completed with state: {state}")
            return {'history': self.history, 'state': state, 'type': 'react'}
        except Exception as e:
            logger.error(f"ReAct run failed with error: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {'history': self.history, 'state': AGENT_STATE_FAILED, 'error': str(e), 'type': 'react'}

    # Planner run achitecture, used by Planner agents
    async def planner_run(self, goal: str):
        try:
            self.setGoal(goal)
            state = AGENT_STATE_WORKING
            await self.plan()
            while state == AGENT_STATE_WORKING:
                await self.act()
                state = await self.check_completion()
            return {'history': self.history, 'state': state, 'type': 'planner'}
        except Exception as e:
            return {'history': self.history, 'state': AGENT_STATE_FAILED, 'error': str(e), 'type': 'planner'}

    # Hybrid run achitecture, used by Hybrid agents
    async def hybrid_run(self, goal: str):
        try:
            self.setGoal(goal)
            state = AGENT_STATE_WORKING
            await self.plan()
            while state == AGENT_STATE_WORKING:
                await self.reason()
                await self.act()
                state = await self.check_completion()
            return {'history': self.history, 'state': state, 'type': 'hybrid'}
        except Exception as e:
            return {'history': self.history, 'state': AGENT_STATE_FAILED, 'error': str(e), 'type': 'hybrid'}
    
    # the plan step, used by Planner and Hybrid agents
    async def plan(self):
        # Pass MCP client but instruct not to use tools
        self.history.append({
            'role': 'user', 
            'content': 'Create a plan for achieving the goal. Do NOT call any tools in this step - only provide a text-based plan.',
            'temporary': True
        })
        
        tool_calls, plan = await self.provider.generate_response(self.history, self.model, self.mcp_client) 
        self.history.append({'role': 'assistant', 'content': plan})
        self.remove_temporary_messages()

    # the reason step, used by ReAct and Hybrid agents
    async def reason(self):
        logger.info("Starting reason step")
        self.history.append({
            'role': 'user', 
            'content': 'Think about your next action. Do NOT call any tools in this step - only provide your reasoning in text.',
            'temporary': True
        })
        logger.info("Added reasoning prompt to history")
        
        try:
            # Pass MCP client but instruct not to use tools
            logger.info("Calling provider.generate_response for reasoning")
            tool_calls, reason = await self.provider.generate_response(self.history, self.model, self.mcp_client)
            logger.info(f"Reasoning response received: {reason[:100]}..." if reason else "No reasoning response")
            logger.info(f"Tool calls in reasoning (should be empty): {tool_calls}")
            
            self.history.append({'role': 'assistant', 'content': reason})
            self.remove_temporary_messages()
            logger.info("Reason step completed successfully")
        except Exception as e:
            logger.error(f"Error in reason step: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    # the act step, used by all agents
    async def act(self, fails = 0):
        logger.info(f"Starting act step (attempt {fails + 1})")
        if fails > 2:  # Increased from 0 to 2 for better debugging
            logger.error(f"Agent failed to act after {fails + 1} attempts")
            raise RuntimeError(f"Agent failed to act after {fails + 1} attempts")
        
        self.history.append({
            'role': 'user',
            'content': 'Perform an action by calling a tool',
            'temporary': True
        })
        logger.info("Added action prompt to history")
        
        try:
            # MCP client given as the act is expected to be a tool call
            logger.info("Calling provider.generate_response for action with MCP client")
            tool_calls, assistant_message = await self.provider.generate_response(self.history, self.model, self.mcp_client)
            logger.info(f"Action response received - Tool calls: {len(tool_calls) if tool_calls else 0}, Message: {assistant_message[:100] if assistant_message else 'None'}...")
            
            if tool_calls:
                logger.info(f"Processing {len(tool_calls)} tool calls")
                # Append the assistant's tool call message
                self.history.append({
                    'role': 'assistant',
                    'content': assistant_message,
                    'tool_calls': tool_calls
                })
                if assistant_message:
                    logger.warning('TODO: implement a solution to handle simultaneous tool calls + assistant message.  Current implementation simply ignores the assistant message.')

                for i, tool_call in enumerate(tool_calls):
                    logger.info(f"Executing tool call {i+1}/{len(tool_calls)}: {tool_call['name']}")
                    try:
                        # Handle both string (OpenAI) and dict (Gemini) parameter formats
                        parameters = tool_call['parameters']
                        if isinstance(parameters, str):
                            parameters = json.loads(parameters)
                        
                        result = await self.mcp_client.call_tool(
                            tool_call['name'],
                            parameters
                        )
                        logger.info(f"Tool call {tool_call['name']} returned: {str(result)[:200]}...")
                        # Append tool result message
                        self.history.append({
                            'role': 'tool',
                            'tool_call_id': tool_call['id'],
                            'content': result
                        })
                    except Exception as e:
                        logger.error(f"Error executing tool call {tool_call['name']}: {str(e)}")
                        logger.error(f"Tool call parameters: {tool_call['parameters']}")
                        raise
            else:
                self.history.append({
                    'role': 'assistant',
                    'content': assistant_message,
                    'tool_calls': tool_calls
                })
                logger.warning("No tool calls returned from agent's act step. Trying again...")
                logger.info(f"Instead of calling tools agent said: {assistant_message}")
                # Final assistant message after tool calls
                self.history.append({
                    'role': 'user', 
                    'content': 'Response rejected: you MUST call a tool at this step.  Please try again.', 
                    'temporary': False
                    }) # not temporary because we want to make sure the agent remembers this failure
                await self.act(fails + 1)
            
            self.remove_temporary_messages()
            logger.info("Act step completed successfully")
        except Exception as e:
            logger.error(f"Error in act step: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    # check completion step, used by all agents
    async def check_completion(self):
        logger.info("Starting completion check")
        self.history.append({
            'role': 'user',
            'content': 'Given the original goal, have you completed the entire task? Respond only "yes" or "no". Do NOT call any tools in this step.',
            'temporary': True
        })
        logger.info("Added completion check prompt to history")
        
        try:
            # Pass MCP client but instruct not to use tools
            tool_calls, response = await self.provider.generate_response(self.history, self.model, self.mcp_client)
            logger.info(f"Completion check response: {response}")
            logger.info(f"Tool calls in completion check (should be empty): {tool_calls}")
            
            # we don't need to add this to the context because it's not relevant to the model's thought and action process
            self.remove_temporary_messages()
            
            if response and 'yes' in response.lower():
                logger.info("Task marked as complete")
                return AGENT_STATE_SUCCESS
            else:
                logger.info("Task not yet complete, continuing")
                return AGENT_STATE_WORKING
        except Exception as e:
            logger.error(f"Error in completion check: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    def remove_temporary_messages(self):
        # remove all temporary messages from the history
        self.history = [message for message in self.history if not message.get('temporary', False)]
    
    
    
    