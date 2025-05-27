#!/usr/bin/env python3
"""
Test runner for all provider implementations.
This script will test all providers and show which ones work based on API key availability.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_provider(provider_name, test_module):
    """Test a single provider and return the result."""
    print(f"\n{'='*50}")
    print(f"Testing {provider_name} Provider")
    print(f"{'='*50}")
    
    try:
        success = test_module.test_provider()
        if success:
            print(f"✅ {provider_name} provider tests PASSED!")
            return True
        else:
            print(f"❌ {provider_name} provider tests FAILED!")
            return False
    except Exception as e:
        print(f"❌ {provider_name} provider tests FAILED with exception: {e}")
        return False

def main():
    """Run all provider tests."""
    print("🚀 Running all provider tests...")
    
    # Import test modules
    try:
        from test_ollama_provider import test_ollama_provider
        from test_openai_provider import test_openai_provider  
        from test_anthropic_provider import test_anthropic_provider
        from test_gemini_provider import test_gemini_provider
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        sys.exit(1)
    
    # Test results
    results = {}
    
    # Test Ollama (should work without API key)
    print("\n🔧 Testing local providers...")
    results['Ollama'] = test_provider('Ollama', type('', (), {'test_provider': test_ollama_provider}))
    
    # Test API-based providers
    print("\n🌐 Testing API-based providers...")
    results['OpenAI'] = test_provider('OpenAI', type('', (), {'test_provider': test_openai_provider}))
    results['Anthropic'] = test_provider('Anthropic', type('', (), {'test_provider': test_anthropic_provider}))
    results['Google Gemini'] = test_provider('Google Gemini', type('', (), {'test_provider': test_gemini_provider}))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = 0
    
    for provider, success in results.items():
        total += 1
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{provider:<15} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} providers working")
    
    if passed == 0:
        print("\n⚠️  No providers are working. Check your setup.")
        sys.exit(1)
    elif passed < total:
        print(f"\n⚠️  {total - passed} provider(s) failed. Check API keys in .env file.")
        print("\nTo test API providers, add these to your .env file:")
        if not results['OpenAI']:
            print("  OPENAI_API_KEY=your_openai_api_key_here")
        if not results['Anthropic']:
            print("  ANTHROPIC_API_KEY=your_anthropic_api_key_here")
        if not results['Google Gemini']:
            print("  GOOGLE_API_KEY=your_google_api_key_here")
    else:
        print("\n🎉 All providers are working correctly!")

if __name__ == "__main__":
    main() 