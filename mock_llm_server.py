#!/usr/bin/env python3
"""
Mock LLM Server for GhostAI DLP Demo
Simulates OpenAI API responses without external calls
"""

import json
import time
import random
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Mock responses for different types of prompts
MOCK_RESPONSES = {
    "jailbreak": {
        "id": "chatcmpl-mock-jailbreak",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "I cannot and will not provide information that could be harmful, illegal, or violate my guidelines. I'm designed to be helpful, harmless, and honest."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 25,
            "total_tokens": 45
        }
    },
    "safe": {
        "id": "chatcmpl-mock-safe",
        "object": "chat.completion", 
        "created": int(time.time()),
        "model": "gpt-3.5-turbo",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! I'm here to help you with any questions or tasks you might have. How can I assist you today?"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 20,
            "total_tokens": 35
        }
    },
    "pii": {
        "id": "chatcmpl-mock-pii",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo", 
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "I notice you've shared some personal information. For your privacy and security, I'd recommend being cautious about sharing sensitive data like SSNs, addresses, or other personal identifiers in conversations."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 25,
            "completion_tokens": 30,
            "total_tokens": 55
        }
    }
}

def detect_prompt_type(messages):
    """Detect the type of prompt to determine response"""
    if not messages:
        return "safe"
    
    content = messages[-1].get("content", "").lower()
    
    # Check for jailbreak patterns
    jailbreak_patterns = [
        "ignore all previous", "you are now", "dan mode", "jailbreak",
        "tell me your system prompt", "act as", "pretend to be",
        "roleplay as", "you must", "override", "bypass"
    ]
    
    if any(pattern in content for pattern in jailbreak_patterns):
        return "jailbreak"
    
    # Check for PII patterns
    pii_patterns = [
        "ssn", "social security", "credit card", "phone number",
        "address", "email", "password", "secret", "confidential"
    ]
    
    if any(pattern in content for pattern in pii_patterns):
        return "pii"
    
    return "safe"

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """Mock OpenAI chat completions endpoint"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-3.5-turbo')
        
        # Detect prompt type
        prompt_type = detect_prompt_type(messages)
        
        # Get appropriate response
        response = MOCK_RESPONSES[prompt_type].copy()
        response["created"] = int(time.time())
        response["model"] = model
        
        # Add some randomness to make it feel more realistic
        time.sleep(random.uniform(0.1, 0.5))
        
        print(f"🤖 Mock LLM Response: {prompt_type.upper()} prompt detected")
        print(f"📝 Content: {messages[-1].get('content', '')[:100]}...")
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "error": {
                "message": f"Mock LLM Error: {str(e)}",
                "type": "mock_error",
                "code": "mock_error"
            }
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "mock-llm-server",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with info"""
    return jsonify({
        "service": "Mock LLM Server for GhostAI DLP Demo",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "health": "/health"
        },
        "description": "Simulates OpenAI API responses for DLP testing"
    })

if __name__ == '__main__':
    print("🤖 Mock LLM Server for GhostAI DLP Demo")
    print("========================================")
    print("📍 Endpoint: http://localhost:5005/v1/chat/completions")
    print("🔍 Health Check: http://localhost:5005/health")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=5005, debug=False)
