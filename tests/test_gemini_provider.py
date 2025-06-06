import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agent_core.providers.googleGeminiProvider import GoogleGeminiProvider

def test_gemini_provider():
    print("Testing Google Gemini Provider...")
    
    # Initialize provider
    provider = GoogleGeminiProvider()
    
    if not provider.ready:
        print("❌ Google Gemini provider not ready - check GEMINI_API_KEY in .env file")
        return False
    
    print("✅ Google Gemini provider initialized successfully")
    
    # Test history format conversion
    test_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    converted_history = provider.history_to_provider_format(test_history)
    expected_history = [
        {"role": "user", "content": "System instruction: You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    assert converted_history == expected_history, "History conversion failed"
    print("✅ History format conversion works correctly")
    
    # Test response generation
    try:
        tool_calls, message = provider.generate_response(test_history, "gemini-1.5-flash")
        assert message is not None, "No message returned"
        assert isinstance(message, str), "Message is not a string"
        print(f"✅ Response generated successfully: {message}...")
        return True
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_provider()
    if success:
        print("\n🎉 All Google Gemini provider tests passed!")
    else:
        print("\n💥 Google Gemini provider tests failed!")
        sys.exit(1) 