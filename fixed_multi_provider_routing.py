#!/usr/bin/env python3
"""
FIXED Multi-Provider Health Checks & Routing
Uses real provider status APIs and circuit breakers
"""

import requests
import time
import random
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import deque
import threading

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    CIRCUIT_OPEN = "circuit_open"

@dataclass
class ProviderConfig:
    name: str
    api_base: str
    api_key: str
    max_rpm: int
    timeout: int
    priority: int
    cost_per_1k_tokens: float
    status: ProviderStatus = ProviderStatus.HEALTHY
    last_check: float = 0.0
    error_count: int = 0
    success_count: int = 0
    response_times: deque = None
    circuit_breaker_failures: int = 0
    circuit_breaker_reset_time: float = 0.0

class FixedMultiProviderRouter:
    """Fixed multi-provider router with real health checks and circuit breakers."""
    
    def __init__(self):
        self.providers = {}
        self.health_check_interval = 30  # seconds
        self.circuit_breaker_threshold = 5  # failures before circuit opens
        self.circuit_breaker_timeout = 60  # seconds
        self.max_response_time = 10  # seconds
        
        # Provider status APIs
        self.status_apis = {
            "openai": "https://status.openai.com/api/v2/status.json",
            "anthropic": "https://status.anthropic.com/api/v2/status.json",
            "cohere": "https://status.cohere.com/api/v2/status.json"
        }
        
        # Health check thread
        self.health_check_thread = None
        self.running = False
        
    def add_provider(self, config: ProviderConfig):
        """Add a provider to the router."""
        if config.response_times is None:
            config.response_times = deque(maxlen=100)
        self.providers[config.name] = config
        
    def start_health_monitoring(self):
        """Start background health monitoring."""
        self.running = True
        self.health_check_thread = threading.Thread(target=self._health_monitor_loop)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        print("🔍 Started health monitoring thread")
    
    def stop_health_monitoring(self):
        """Stop background health monitoring."""
        self.running = False
        if self.health_check_thread:
            self.health_check_thread.join()
        print("🛑 Stopped health monitoring thread")
    
    def _health_monitor_loop(self):
        """Background health monitoring loop."""
        while self.running:
            try:
                self._check_all_providers()
                time.sleep(self.health_check_interval)
            except Exception as e:
                print(f"Health monitoring error: {e}")
                time.sleep(5)
    
    def _check_provider_status_api(self, provider_name: str) -> bool:
        """Check provider status using their status API."""
        if provider_name not in self.status_apis:
            return True  # Assume healthy if no status API
        
        try:
            response = requests.get(self.status_apis[provider_name], timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Check if status indicates healthy
                status = data.get('status', {}).get('indicator', 'unknown')
                return status in ['none', 'minor', 'operational']
            return False
        except Exception as e:
            print(f"Status API check failed for {provider_name}: {e}")
            return False
    
    def _check_provider_health(self, provider: ProviderConfig) -> bool:
        """Check if a provider is healthy using multiple methods."""
        now = time.time()
        
        # Check circuit breaker
        if provider.status == ProviderStatus.CIRCUIT_OPEN:
            if now - provider.circuit_breaker_reset_time > self.circuit_breaker_timeout:
                provider.status = ProviderStatus.HEALTHY
                provider.circuit_breaker_failures = 0
                print(f"🔄 Circuit breaker reset for {provider.name}")
            else:
                return False
        
        # Check status API
        if not self._check_provider_status_api(provider.name):
            provider.status = ProviderStatus.DOWN
            return False
        
        # Check with actual API call (lightweight)
        try:
            start_time = time.time()
            
            # Make a minimal request to check health
            headers = {"Authorization": f"Bearer {provider.api_key}"}
            
            # Use a lightweight endpoint if available
            health_endpoints = [
                f"{provider.api_base}/health",
                f"{provider.api_base}/v1/models",
                f"{provider.api_base}/v1/chat/completions"
            ]
            
            success = False
            for endpoint in health_endpoints:
                try:
                    response = requests.get(
                        endpoint,
                        headers=headers,
                        timeout=5
                    )
                    if response.status_code in [200, 401, 403]:  # 401/403 means API is up but auth failed
                        success = True
                        break
                except:
                    continue
            
            if success:
                response_time = time.time() - start_time
                provider.response_times.append(response_time)
                
                # Update status based on response time
                if response_time < 2.0:
                    provider.status = ProviderStatus.HEALTHY
                elif response_time < 5.0:
                    provider.status = ProviderStatus.DEGRADED
                else:
                    provider.status = ProviderStatus.DOWN
                
                provider.error_count = 0
                provider.success_count += 1
                provider.last_check = now
                return True
            else:
                provider.status = ProviderStatus.DOWN
                provider.error_count += 1
                return False
                
        except Exception as e:
            print(f"Health check failed for {provider.name}: {e}")
            provider.status = ProviderStatus.DOWN
            provider.error_count += 1
            return False
    
    def _check_all_providers(self):
        """Check health of all providers."""
        for provider in self.providers.values():
            self._check_provider_health(provider)
    
    def get_healthy_providers(self) -> List[ProviderConfig]:
        """Get list of healthy providers sorted by priority and performance."""
        now = time.time()
        
        # Update health status for providers that need checking
        for provider in self.providers.values():
            if now - provider.last_check > self.health_check_interval:
                self._check_provider_health(provider)
        
        # Filter healthy providers
        healthy = [p for p in self.providers.values() 
                  if p.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]]
        
        # Sort by priority and performance
        def sort_key(provider):
            # Priority (lower is better)
            priority_score = provider.priority
            
            # Performance score (lower response time is better)
            if provider.response_times:
                avg_response_time = sum(provider.response_times) / len(provider.response_times)
                performance_score = avg_response_time
            else:
                performance_score = 5.0  # Default if no data
            
            # Status penalty
            status_penalty = 0 if provider.status == ProviderStatus.HEALTHY else 1
            
            return (priority_score, performance_score, status_penalty)
        
        return sorted(healthy, key=sort_key)
    
    def route_request(self, request_data: Dict, preferred_provider: Optional[str] = None) -> Tuple[Dict, str]:
        """Route a request to the best available provider."""
        
        # Get healthy providers
        healthy_providers = self.get_healthy_providers()
        
        if not healthy_providers:
            raise Exception("No healthy providers available")
        
        # Use preferred provider if available and healthy
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if provider.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]:
                try:
                    return self._make_request(provider, request_data)
                except Exception as e:
                    print(f"Preferred provider {preferred_provider} failed: {e}")
                    self._handle_provider_failure(provider)
        
        # Try providers in priority order
        for provider in healthy_providers:
            try:
                return self._make_request(provider, request_data)
            except Exception as e:
                print(f"Provider {provider.name} failed: {e}")
                self._handle_provider_failure(provider)
                continue
        
        raise Exception("All providers failed")
    
    def _handle_provider_failure(self, provider: ProviderConfig):
        """Handle provider failure and update circuit breaker."""
        provider.error_count += 1
        provider.circuit_breaker_failures += 1
        
        if provider.circuit_breaker_failures >= self.circuit_breaker_threshold:
            provider.status = ProviderStatus.CIRCUIT_OPEN
            provider.circuit_breaker_reset_time = time.time()
            print(f"🔴 Circuit breaker opened for {provider.name}")
    
    def _make_request(self, provider: ProviderConfig, request_data: Dict) -> Tuple[Dict, str]:
        """Make a request to a specific provider."""
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        # Add provider-specific headers
        if provider.name == "anthropic":
            headers["anthropic-version"] = "2023-06-01"
        elif provider.name == "cohere":
            headers["cohere-version"] = "2022-12-06"
        
        start_time = time.time()
        
        response = requests.post(
            f"{provider.api_base}/v1/chat/completions",
            headers=headers,
            json=request_data,
            timeout=provider.timeout
        )
        
        response_time = time.time() - start_time
        provider.response_times.append(response_time)
        
        if response.status_code == 200:
            provider.success_count += 1
            provider.error_count = 0
            return response.json(), provider.name
        else:
            provider.error_count += 1
            raise Exception(f"Provider {provider.name} returned {response.status_code}: {response.text}")
    
    def get_routing_stats(self) -> Dict:
        """Get comprehensive routing statistics."""
        stats = {}
        for name, provider in self.providers.items():
            avg_response_time = 0
            if provider.response_times:
                avg_response_time = sum(provider.response_times) / len(provider.response_times)
            
            success_rate = 0
            total_requests = provider.success_count + provider.error_count
            if total_requests > 0:
                success_rate = provider.success_count / total_requests
            
            stats[name] = {
                "status": provider.status.value,
                "success_count": provider.success_count,
                "error_count": provider.error_count,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "circuit_breaker_failures": provider.circuit_breaker_failures,
                "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                "last_check": provider.last_check
            }
        return stats

def test_fixed_routing():
    """Test the fixed multi-provider routing."""
    
    print("🧪 Testing FIXED Multi-Provider Routing")
    print("=" * 60)
    
    # Initialize router
    router = FixedMultiProviderRouter()
    
    # Add providers with realistic configs
    router.add_provider(ProviderConfig(
        name="openai",
        api_base="https://api.openai.com/v1",
        api_key="sk-test-key",
        max_rpm=10000,
        timeout=30,
        priority=1,
        cost_per_1k_tokens=0.002
    ))
    
    router.add_provider(ProviderConfig(
        name="anthropic",
        api_base="https://api.anthropic.com/v1",
        api_key="sk-ant-test-key",
        max_rpm=8000,
        timeout=30,
        priority=2,
        cost_per_1k_tokens=0.003
    ))
    
    router.add_provider(ProviderConfig(
        name="cohere",
        api_base="https://api.cohere.ai/v1",
        api_key="co-test-key",
        max_rpm=5000,
        timeout=30,
        priority=3,
        cost_per_1k_tokens=0.001
    ))
    
    # Start health monitoring
    router.start_health_monitoring()
    
    print("🔍 Health monitoring started...")
    time.sleep(2)  # Let health checks run
    
    # Test routing
    print("\n📊 Provider Status:")
    stats = router.get_routing_stats()
    for name, stat in stats.items():
        print(f"   {name}: {stat['status']} (success rate: {stat['success_rate']:.2%})")
    
    # Test request routing
    print("\n🚀 Testing Request Routing:")
    request_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    
    try:
        # This will fail because we don't have real API keys, but it tests the routing logic
        response, provider_name = router.route_request(request_data)
        print(f"✅ Request routed to {provider_name}")
    except Exception as e:
        print(f"❌ Request failed (expected): {e}")
    
    # Test circuit breaker
    print("\n🔴 Testing Circuit Breaker:")
    for provider in router.providers.values():
        # Simulate failures to trigger circuit breaker
        for _ in range(6):
            router._handle_provider_failure(provider)
    
    print("📊 Provider Status After Circuit Breaker:")
    stats = router.get_routing_stats()
    for name, stat in stats.items():
        print(f"   {name}: {stat['status']} (failures: {stat['circuit_breaker_failures']})")
    
    # Stop health monitoring
    router.stop_health_monitoring()
    
    print("\n✅ Fixed routing test completed!")

if __name__ == "__main__":
    test_fixed_routing()
