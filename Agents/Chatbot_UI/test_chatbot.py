#!/usr/bin/env python3
"""
Test script for the enhanced Qwen chatbot
"""

import requests
import json

def test_ollama_connection():
    """Test if Ollama is running and Qwen is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            qwen_available = any(model['name'].startswith('qwen2.5') for model in models)
            print(f"✅ Ollama is running")
            print(f"📋 Available models: {[model['name'] for model in models]}")
            if qwen_available:
                print("✅ Qwen2.5 model is available")
                return True
            else:
                print("❌ Qwen2.5 model not found")
                return False
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 Make sure Ollama is running with: ollama serve")
        return False

def test_qwen_response():
    """Test sending a simple message to Qwen"""
    payload = {
        "model": "qwen2.5:3b",
        "prompt": "Hello! Please respond with 'Test successful' if you can read this.",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 50
        }
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        ai_response = result.get('response', '')
        print(f"🤖 AI Response: {ai_response}")
        return True
    except Exception as e:
        print(f"❌ Error testing Qwen: {e}")
        return False

def main():
    print("🧪 Testing Enhanced Qwen Chatbot")
    print("=" * 40)
    
    # Test Ollama connection
    if not test_ollama_connection():
        print("\n❌ Please start Ollama first:")
        print("   ollama serve")
        return
    
    print()
    
    # Test Qwen response
    if test_qwen_response():
        print("\n✅ All tests passed! Your chatbot should work correctly.")
        print("\n🚀 To run the chatbot:")
        print("   python Qwentin")
    else:
        print("\n❌ Qwen test failed")

if __name__ == "__main__":
    main()
