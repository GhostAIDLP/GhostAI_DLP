#!/usr/bin/env python3
"""
Debug the firewall issue
"""

import requests
import json

def test_firewall():
    """Test the firewall with detailed debugging."""
    url = "http://localhost:5004/v1/chat/completions"
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello test"}]
    }
    
    print("🔍 Testing firewall with detailed debugging...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📊 Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_firewall()
