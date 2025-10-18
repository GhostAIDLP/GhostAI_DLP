"""
Redis cache utility for GhostAI firewall SDK.
Handles caching of frequent queries and scan results.
"""

import json
import time
from typing import Any, Optional, Dict
import redis
from loguru import logger


class RedisCache:
    """Handles Redis caching for firewall scan results and queries."""
    
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0, password: Optional[str] = None):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Optional Redis password
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning("Failed to initialize Redis cache: {}", e)
            self.redis_client = None
    
    def cache_scan_result(self, session_id: str, result: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Cache a scan result.
        
        Args:
            session_id: Session identifier
            result: Scan result dictionary
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            True if caching succeeded, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            key = f"scan:{session_id}:{int(time.time())}"
            value = json.dumps(result)
            self.redis_client.setex(key, ttl, value)
            logger.debug("Cached scan result for session: {}", session_id)
            return True
        except Exception as e:
            logger.error("Failed to cache scan result: {}", e)
            return False
    
    def get_recent_scans(self, session_id: str, limit: int = 10) -> list:
        """
        Get recent scans for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of scans to return
            
        Returns:
            List of recent scan results
        """
        if not self.redis_client:
            return []
        
        try:
            pattern = f"scan:{session_id}:*"
            keys = self.redis_client.keys(pattern)
            
            # Sort by timestamp (newest first) and limit
            keys.sort(reverse=True)
            keys = keys[:limit]
            
            results = []
            for key in keys:
                value = self.redis_client.get(key)
                if value:
                    results.append(json.loads(value))
            
            return results
        except Exception as e:
            logger.error("Failed to get recent scans: {}", e)
            return []
    
    def cache_frequent_query(self, query_type: str, query_params: str, result: Any, ttl: int = 1800) -> bool:
        """
        Cache a frequent query result.
        
        Args:
            query_type: Type of query (e.g., "recent_scans", "analytics")
            query_params: Query parameters as string
            result: Query result
            ttl: Time to live in seconds (default 30 minutes)
            
        Returns:
            True if caching succeeded, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            key = f"query:{query_type}:{hash(query_params)}"
            value = json.dumps(result)
            self.redis_client.setex(key, ttl, value)
            logger.debug("Cached query result: {}", query_type)
            return True
        except Exception as e:
            logger.error("Failed to cache query result: {}", e)
            return False
    
    def get_cached_query(self, query_type: str, query_params: str) -> Optional[Any]:
        """
        Get a cached query result.
        
        Args:
            query_type: Type of query
            query_params: Query parameters as string
            
        Returns:
            Cached result or None if not found
        """
        if not self.redis_client:
            return None
        
        try:
            key = f"query:{query_type}:{hash(query_params)}"
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Failed to get cached query: {}", e)
            return None
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate all cached data for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if invalidation succeeded, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            pattern = f"scan:{session_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.debug("Invalidated {} keys for session: {}", len(keys), session_id)
            return True
        except Exception as e:
            logger.error("Failed to invalidate session cache: {}", e)
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get Redis cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            logger.error("Failed to get cache stats: {}", e)
            return {"error": str(e)}


# Global instance for easy access
_redis_cache = None

def get_redis_cache() -> RedisCache:
    """Get the global Redis cache instance."""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache
