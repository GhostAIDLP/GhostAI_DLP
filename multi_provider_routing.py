#!/usr/bin/env python3
"""
GhostAI Multi-Provider Routing & Failover
Handles 1M req/day e-commerce with OpenAI/Anthropic failover
"""

import requests
import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"

@dataclass
class ProviderConfig:
    name: str
    api_base: str
    api_key: str
    max_rpm: int  # requests per minute
    timeout: int
    priority: int  # 1 = highest priority
    cost_per_1k_tokens: float
    status: ProviderStatus = ProviderStatus.HEALTHY
    last_check: float = 0.0
    error_count: int = 0
    success_count: int = 0

class MultiProviderRouter:
    """Routes requests across multiple LLM providers with failover."""
    
    def __init__(self):
        self.providers = {}
        self.health_check_interval = 30  # seconds
        self.circuit_breaker_threshold = 5  # errors before circuit opens
        self.circuit_breaker_timeout = 60  # seconds
        
    def add_provider(self, config: ProviderConfig):
        """Add a provider to the router."""
        self.providers[config.name] = config
        
    def get_healthy_providers(self) -> List[ProviderConfig]:
        """Get list of healthy providers sorted by priority."""
        now = time.time()
        
        # Update health status
        for provider in self.providers.values():
            if now - provider.last_check > self.health_check_interval:
                self._check_provider_health(provider)
                provider.last_check = now
        
        # Return healthy providers sorted by priority
        healthy = [p for p in self.providers.values() if p.status == ProviderStatus.HEALTHY]
        return sorted(healthy, key=lambda x: x.priority)
    
    def _check_provider_health(self, provider: ProviderConfig):
        """Check if a provider is healthy."""
        try:
            # Simple health check - try to make a minimal request
            headers = {"Authorization": f"Bearer {provider.api_key}"}
            response = requests.get(
                f"{provider.api_base}/health",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                provider.status = ProviderStatus.HEALTHY
                provider.error_count = 0
            else:
                provider.status = ProviderStatus.DEGRADED
                provider.error_count += 1
                
        except Exception as e:
            provider.status = ProviderStatus.DOWN
            provider.error_count += 1
            
        # Circuit breaker logic
        if provider.error_count >= self.circuit_breaker_threshold:
            provider.status = ProviderStatus.DOWN
            # Reset after timeout
            if time.time() - provider.last_check > self.circuit_breaker_timeout:
                provider.error_count = 0
                provider.status = ProviderStatus.HEALTHY
    
    def route_request(self, request_data: Dict, preferred_provider: Optional[str] = None) -> Tuple[Dict, str]:
        """Route a request to the best available provider."""
        
        # Get healthy providers
        healthy_providers = self.get_healthy_providers()
        
        if not healthy_providers:
            raise Exception("No healthy providers available")
        
        # Use preferred provider if available and healthy
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if provider.status == ProviderStatus.HEALTHY:
                return self._make_request(provider, request_data)
        
        # Try providers in priority order
        for provider in healthy_providers:
            try:
                return self._make_request(provider, request_data)
            except Exception as e:
                print(f"Provider {provider.name} failed: {e}")
                continue
        
        raise Exception("All providers failed")
    
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
        
        response = requests.post(
            f"{provider.api_base}/v1/chat/completions",
            headers=headers,
            json=request_data,
            timeout=provider.timeout
        )
        
        if response.status_code == 200:
            provider.success_count += 1
            return response.json(), provider.name
        else:
            provider.error_count += 1
            raise Exception(f"Provider {provider.name} returned {response.status_code}")
    
    def get_routing_stats(self) -> Dict:
        """Get routing statistics."""
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = {
                "status": provider.status.value,
                "success_count": provider.success_count,
                "error_count": provider.error_count,
                "success_rate": provider.success_count / max(provider.success_count + provider.error_count, 1),
                "cost_per_1k_tokens": provider.cost_per_1k_tokens
            }
        return stats

def simulate_1m_requests_per_day():
    """Simulate 1M requests per day routing."""
    
    print("🚀 Simulating 1M Requests/Day Multi-Provider Routing")
    print("=" * 60)
    
    # Initialize router
    router = MultiProviderRouter()
    
    # Add providers (realistic 2025 pricing)
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
    
    # Simulate requests
    total_requests = 1000  # Simulate 1000 requests
    successful_requests = 0
    failed_requests = 0
    provider_usage = {}
    total_cost = 0.0
    
    print(f"📊 Simulating {total_requests} requests...")
    
    for i in range(total_requests):
        try:
            # Simulate request
            request_data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": f"Test request {i}"}],
                "max_tokens": 100
            }
            
            # Route request
            response, provider_name = router.route_request(request_data)
            
            successful_requests += 1
            provider_usage[provider_name] = provider_usage.get(provider_name, 0) + 1
            
            # Calculate cost (simplified)
            tokens_used = 50  # Estimated tokens per request
            cost = tokens_used / 1000 * router.providers[provider_name].cost_per_1k_tokens
            total_cost += cost
            
            # Simulate occasional provider failures
            if random.random() < 0.05:  # 5% failure rate
                router.providers[provider_name].error_count += 1
                if router.providers[provider_name].error_count >= 5:
                    router.providers[provider_name].status = ProviderStatus.DOWN
            
        except Exception as e:
            failed_requests += 1
            print(f"Request {i} failed: {e}")
    
    # Print results
    print(f"\n📈 Routing Results:")
    print(f"   Successful Requests: {successful_requests}")
    print(f"   Failed Requests: {failed_requests}")
    print(f"   Success Rate: {successful_requests/total_requests:.2%}")
    print(f"   Total Cost: ${total_cost:.2f}")
    
    print(f"\n🔀 Provider Usage:")
    for provider, count in provider_usage.items():
        percentage = count / successful_requests * 100
        print(f"   {provider}: {count} requests ({percentage:.1f}%)")
    
    print(f"\n📊 Provider Stats:")
    stats = router.get_routing_stats()
    for provider, stat in stats.items():
        print(f"   {provider}:")
        print(f"     Status: {stat['status']}")
        print(f"     Success Rate: {stat['success_rate']:.2%}")
        print(f"     Cost per 1K tokens: ${stat['cost_per_1k_tokens']:.3f}")
    
    # Scale to 1M requests/day
    daily_cost = total_cost * 1000  # Scale up
    print(f"\n🌍 Scaled to 1M Requests/Day:")
    print(f"   Daily Cost: ${daily_cost:.2f}")
    print(f"   Monthly Cost: ${daily_cost * 30:.2f}")
    print(f"   Annual Cost: ${daily_cost * 365:.2f}")

if __name__ == "__main__":
    simulate_1m_requests_per_day()
