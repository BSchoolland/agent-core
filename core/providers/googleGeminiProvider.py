# core/providers/googleGeminiProvider.py
import os
from dotenv import load_dotenv
from google import genai
from .providerClass import Provider

# Load environment variables from .env file
load_dotenv()

class GoogleGeminiProvider(Provider):
    def __init__(self, API_KEY=None):
        super().__init__(API_KEY)
        if self.API_KEY is None:
            self.API_KEY = os.getenv('GEMINI_API_KEY')
        
        if self.API_KEY:
            self.client = genai.Client(api_key=self.API_KEY)
            self.ready = True
        else:
            self.client = None
            self.ready = False

    def initialize(self):
        if not self.ready and self.API_KEY:
            self.client = genai.Client(api_key=self.API_KEY)
            self.ready = True

    def list_models(self):
        """List available models from Google Gemini"""
        if not self.ready:
            return []
        
        try:
            models = self.client.models.list()
            return [model.name.replace('models/', '') for model in models]
        except Exception:
            # Return empty list if API call fails
            return []

    async def generate_response(self, history, model, mcp_client=None):
        if not self.ready:
            raise Exception("Google Gemini provider not ready. Please provide API key.")
        
        # Convert history to Gemini format
        gemini_history = self.history_to_provider_format(history)
        
        try:
            # Get tools if MCP client is available
            tools = await self.tools_to_provider_format(mcp_client) if mcp_client else []
            
            # Use generate_content instead of chat for better tool support
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=gemini_history,
                config=genai.types.GenerateContentConfig(
                    tools=tools,
                    temperature=0
                )
            )
            
            # Extract text content properly, handling function calls
            message = None
            if response.candidates and response.candidates[0].content.parts:
                text_parts = []
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                message = ''.join(text_parts) if text_parts else None
            
            tool_calls = self.provider_to_std_tool_calls_format(response.candidates[0].content.parts if response.candidates else [])
            
            print('gemini tool calls:', tool_calls)
            return tool_calls, message
            
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")

    def tool_calls_to_provider_format(self, tool_calls):
        """Convert standard tool calls to Gemini format"""
        provider_tool_calls = []
        for tool_call in tool_calls:
            provider_tool_calls.append(genai.types.FunctionCall(
                name=tool_call['name'],
                args=tool_call['parameters']  # This should be a dict, not JSON string
            ))
        return provider_tool_calls

    def history_to_provider_format(self, history):
        """Convert standard history format to Gemini format"""
        gemini_history = []
        system_instruction = None
        
        for msg in history:
            if msg["role"] == "system":
                # Gemini handles system messages separately
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_history.append(genai.types.Content(
                    role="user",
                    parts=[genai.types.Part(text=msg["content"])]
                ))
            elif msg["role"] == "assistant":
                parts = []
                if msg.get("content"):
                    parts.append(genai.types.Part(text=msg["content"]))
                
                if msg.get("tool_calls"):
                    for tool_call in msg["tool_calls"]:
                        parts.append(genai.types.Part(
                            function_call=genai.types.FunctionCall(
                                name=tool_call["name"],
                                args=tool_call["parameters"] if isinstance(tool_call["parameters"], dict) else {}
                            )
                        ))
                
                if parts:
                    gemini_history.append(genai.types.Content(
                        role="model",  # Gemini uses "model" instead of "assistant"
                        parts=parts
                    ))
            elif msg["role"] == "tool":
                # Tool response messages
                gemini_history.append(genai.types.Content(
                    role="function",
                    parts=[genai.types.Part(
                        function_response=genai.types.FunctionResponse(
                            name=msg.get("tool_call_id", "unknown"),
                            response={"result": str(msg["content"])}
                        )
                    )]
                ))
        
        # Add system instruction if present
        if system_instruction and gemini_history:
            # Prepend system instruction to first user message
            first_user_msg = None
            for i, content in enumerate(gemini_history):
                if content.role == "user":
                    first_user_msg = i
                    break
            
            if first_user_msg is not None:
                original_text = gemini_history[first_user_msg].parts[0].text
                gemini_history[first_user_msg] = genai.types.Content(
                    role="user",
                    parts=[genai.types.Part(text=f"System: {system_instruction}\n\nUser: {original_text}")]
                )
        
        return gemini_history

    def provider_to_std_history_format(self, provider_history):
        """Convert Gemini format back to standard format"""
        # This is complex due to Gemini's structure, implementing basic version
        return provider_history

    def provider_to_std_tool_calls_format(self, parts):
        """Convert Gemini function calls to standard format"""
        tool_calls = []
        
        for part in parts:
            if hasattr(part, 'function_call') and part.function_call:
                func_call = part.function_call
                tool_calls.append({
                    'id': f"call_{func_call.name}_{len(tool_calls)}",  # Generate ID
                    'name': func_call.name,
                    'parameters': func_call.args if func_call.args else {}
                })
        
        return tool_calls

    async def tools_to_provider_format(self, mcp_client):
        """Convert MCP tools to Gemini function declarations"""
        if mcp_client is None:
            return []
        
        tools = await mcp_client.get_tools()
        gemini_tools = []
        
        for tool in tools:
            function_declaration = genai.types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or "No description provided",
                parameters=tool.inputSchema
            )
            gemini_tools.append(genai.types.Tool(
                function_declarations=[function_declaration]
            ))
        
        return gemini_tools