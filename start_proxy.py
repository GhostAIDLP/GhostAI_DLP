#!/usr/bin/env python3
"""
Simple proxy starter that handles port conflicts automatically
"""
import socket
from ghostai.proxy_api.proxy import GhostAIProxy

def find_free_port(start_port=5000, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports found in range {start_port}-{start_port + max_attempts}")

if __name__ == "__main__":
    try:
        port = find_free_port()
        print(f"🚀 Starting GhostAI Proxy on port {port}")
        print(f"📍 API Endpoint: http://localhost:{port}/v1/chat/completions")
        print(f"🔍 Health Check: http://localhost:{port}/health")
        print("\n⏹️  Press Ctrl+C to stop")
        print("-" * 50)
        
        proxy = GhostAIProxy()
        proxy.run(host="0.0.0.0", port=port, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Proxy stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
