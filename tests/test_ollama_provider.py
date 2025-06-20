import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agent_core.providers.ollamaProvider import OllamaProvider

def test_ollama_provider():
    print("Testing Ollama Provider...")
    
    # Initialize provider
    provider = OllamaProvider()
    
    if not provider.ready:
        print("❌ Ollama provider not ready")
        return False
    
    print("✅ Ollama provider initialized successfully")
    
    # Test history format conversion
    test_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    converted_history = provider.history_to_provider_format(test_history)
    assert converted_history == test_history, "History conversion failed"
    print("✅ History format conversion works correctly")
    
    # Test response generation
    try:
        tool_calls, message = provider.generate_response(test_history, "gemma3:1b-it-qat")
        assert message is not None, "No message returned"
        assert isinstance(message, str), "Message is not a string"
        print(f"✅ Response generated successfully: {message}...")
        return True
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama_provider()
    if success:
        print("\n🎉 All Ollama provider tests passed!")
    else:
        print("\n💥 Ollama provider tests failed!")
        sys.exit(1) 