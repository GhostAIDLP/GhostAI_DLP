#!/usr/bin/env python3
"""
GhostAI Security Firewall - Advanced threat detection and blocking
A comprehensive security gateway for AI services
"""

import os
import sys
import argparse
from ghostai.proxy_api.firewall import GhostAIFirewall

def main():
    parser = argparse.ArgumentParser(description='GhostAI Security Firewall')
    parser.add_argument('--mode', choices=['firewall', 'proxy', 'monitor'], 
                       default='firewall', help='Firewall operation mode')
    parser.add_argument('--port', type=int, default=5004, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--config', help='Path to firewall config file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--mock', action='store_true', help='Use mock LLM (no external API)')
    
    args = parser.parse_args()
    
    print("🔥 GhostAI Security Firewall")
    print("=" * 50)
    print(f"🛡️  Mode: {args.mode.upper()}")
    print(f"🌐 Host: {args.host}:{args.port}")
    
    # Check if we should use mock mode
    use_mock = args.mock or os.getenv('USE_MOCK_LLM', 'true').lower() == 'true'
    
    if use_mock:
        print("🤖 Using Mock LLM Server (no external API calls)")
        print("📍 Mock LLM: http://localhost:5005")
    else:
        print("🌐 Using OpenAI API")
        if 'OPENAI_API_KEY' not in os.environ:
            os.environ['OPENAI_API_KEY'] = 'dummy-key-for-testing'
    
    # Initialize firewall
    firewall = GhostAIFirewall(
        use_mock=use_mock,
        firewall_config=args.config
    )
    
    print("🔥 Starting security firewall...")
    print("📍 Firewall Endpoint: http://localhost:5004/v1/chat/completions")
    print("🔍 Health Check: http://localhost:5004/health")
    print("📊 Firewall Stats: http://localhost:5004/firewall/stats")
    print("\n📝 Test with curl:")
    print('curl -X POST http://localhost:5004/v1/chat/completions \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"model": "gpt-3.5-turbo", "messages":[{"role":"user","content":"My SSN is 123-45-6789"}]}\'')
    print("\n⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        firewall.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n🔥 Firewall stopped.")

if __name__ == "__main__":
    main()
