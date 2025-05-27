import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.providers.openAIProvider import OpenAIProvider

def test_openai_provider():
    print("Testing OpenAI Provider...")
    
    # Initialize provider
    provider = OpenAIProvider()
    
    if not provider.ready:
        print("❌ OpenAI provider not ready - check OPENAI_API_KEY in .env file")
        return False
    
    print("✅ OpenAI provider initialized successfully")
    
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
        tool_calls, message = provider.generate_response(test_history, "gpt-4o-mini")
        assert message is not None, "No message returned"
        assert isinstance(message, str), "Message is not a string"
        print(f"✅ Response generated successfully: {message}...")
        return True
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_provider()
    if success:
        print("\n🎉 All OpenAI provider tests passed!")
    else:
        print("\n💥 OpenAI provider tests failed!")
        sys.exit(1) 