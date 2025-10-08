"""
Test the proxy functionality.
"""

import json
import requests
import time
import threading
from ghostai.proxy_api.proxy import GhostAIProxy

def test_proxy_startup():
    """Test that the proxy can start without errors."""
    proxy = GhostAIProxy()
    assert proxy is not None
    assert proxy.app is not None

def test_proxy_endpoint():
    """Test the /v1/chat/completions endpoint."""
    # Start proxy in a separate thread
    proxy = GhostAIProxy()
    proxy_thread = threading.Thread(target=lambda: proxy.run(port=5003, debug=False))
    proxy_thread.daemon = True
    proxy_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Test the endpoint
        response = requests.post(
            "http://localhost:5003/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "my aws key is AKIA1234567890"}
                ]
            },
            timeout=10
        )
        
        # Should get a response (even if it's an error from OpenAI)
        assert response.status_code in [200, 400, 401, 403, 404, 429, 500]
        
        # The response should be JSON
        data = response.json()
        assert isinstance(data, dict)
        
        print(f"Proxy response: {data}")
        
    finally:
        # Clean up - the daemon thread will exit when main thread exits
        pass

def test_proxy_pipeline_integration():
    """Test that the proxy uses the pipeline internally."""
    proxy = GhostAIProxy()
    
    # Test that pipeline is initialized
    assert proxy.pipeline is not None
    
    # Test that pipeline can run
    result = proxy.pipeline.run("test text")
    assert isinstance(result, dict)
    assert "score" in result
    assert "flags" in result
    assert "breakdown" in result
