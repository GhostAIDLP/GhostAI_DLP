#!/usr/bin/env python3
"""
GhostAI DLP SDK - Localhost Proxy Runner
Simple Flask proxy server for localhost testing
"""

import os
import sys
from ghostai.proxy_api.proxy import GhostAIProxy

def main():
    print("🚀 GhostAI DLP Proxy - Localhost Runner")
    print("=" * 50)
    
    # Check if we should use mock mode
    use_mock = os.getenv('USE_MOCK_LLM', 'true').lower() == 'true'
    
    if use_mock:
        print("🤖 Using Mock LLM Server (no external API calls)")
        print("📍 Mock LLM: http://localhost:5005")
    else:
        print("🌐 Using OpenAI API")
        # Use environment variable or set default
        if 'OPENAI_API_KEY' not in os.environ:
            os.environ['OPENAI_API_KEY'] = 'dummy-key-for-testing'
    
    # Initialize proxy
    proxy = GhostAIProxy(use_mock=use_mock)
    
    print("🌐 Starting proxy server...")
    print("📍 API Endpoint: http://localhost:5004/v1/chat/completions")
    print("🔍 Health Check: http://localhost:5004/health")
    print("\n📝 Test with curl:")
    print('curl -X POST http://localhost:5004/v1/chat/completions \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"messages":[{"role":"user","content":"My SSN is 123-45-6789"}]}\'')
    print("\n⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        proxy.run(host='0.0.0.0', port=5004, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Proxy stopped.")

if __name__ == "__main__":
    main()
