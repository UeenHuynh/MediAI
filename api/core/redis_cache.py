"""
Redis Cache Module

Provides caching functionality using Upstash Redis or local Redis.
Gracefully degrades if Redis is unavailable.
"""

import hashlib
import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client = None
_redis_available = False


def get_redis_client():
    """
    Get or create Redis client.

    Tries to connect to:
    1. UPSTASH_REDIS_URL (production)
    2. REDIS_URL (local/docker)
    3. localhost:6379 (fallback)
    """
    global _redis_client, _redis_available

    if _redis_client is not None:
        return _redis_client if _redis_available else None

    try:
        import redis

        # Try Upstash first (production)
        upstash_url = os.getenv("UPSTASH_REDIS_URL")
        if upstash_url:
            _redis_client = redis.from_url(
                upstash_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            _redis_client.ping()
            _redis_available = True
            logger.info("✅ Connected to Upstash Redis")
            return _redis_client

        # Try generic REDIS_URL
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            _redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            _redis_client.ping()
            _redis_available = True
            logger.info("✅ Connected to Redis via REDIS_URL")
            return _redis_client

        # Try localhost fallback
        _redis_client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2,
        )
        _redis_client.ping()
        _redis_available = True
        logger.info("✅ Connected to local Redis")
        return _redis_client

    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching disabled.")
        _redis_available = False
        return None


class RedisCache:
    """
    Redis caching wrapper with graceful fallback.

    If Redis is unavailable, all operations are no-ops.
    """

    # Default TTLs (in seconds)
    PREDICTION_TTL = 3600  # 1 hour
    CHAT_RESPONSE_TTL = 1800  # 30 minutes
    EMBEDDING_TTL = 86400  # 24 hours

    @staticmethod
    def _get_cache_key(prefix: str, data: dict) -> str:
        """Generate cache key from prefix and data dict"""
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_val}"

    @staticmethod
    def cache_prediction(
        prediction_type: str, input_features: dict, result: dict, ttl: int = None
    ) -> bool:
        """
        Cache a prediction result.

        Args:
            prediction_type: 'sepsis' or 'mortality'
            input_features: Input features used for prediction
            result: Prediction result to cache
            ttl: Time-to-live in seconds

        Returns:
            True if cached successfully, False otherwise
        """
        client = get_redis_client()
        if not client:
            return False

        try:
            key = RedisCache._get_cache_key(f"pred:{prediction_type}", input_features)
            ttl = ttl or RedisCache.PREDICTION_TTL
            client.setex(key, ttl, json.dumps(result))
            logger.debug(f"Cached prediction: {key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache prediction: {e}")
            return False

    @staticmethod
    def get_cached_prediction(
        prediction_type: str, input_features: dict
    ) -> Optional[dict]:
        """
        Get cached prediction result.

        Args:
            prediction_type: 'sepsis' or 'mortality'
            input_features: Input features to look up

        Returns:
            Cached result or None if not found
        """
        client = get_redis_client()
        if not client:
            return None

        try:
            key = RedisCache._get_cache_key(f"pred:{prediction_type}", input_features)
            cached = client.get(key)
            if cached:
                logger.debug(f"Cache hit: {key}")
                return json.loads(cached)
            return None
        except Exception as e:
            logger.warning(f"Failed to get cached prediction: {e}")
            return None

    @staticmethod
    def cache_chat_response(query: str, response: dict, ttl: int = None) -> bool:
        """
        Cache a chat/RAG response.

        Args:
            query: User query
            response: Chat response to cache
            ttl: Time-to-live in seconds

        Returns:
            True if cached successfully
        """
        client = get_redis_client()
        if not client:
            return False

        try:
            key = RedisCache._get_cache_key("chat", {"query": query.lower().strip()})
            ttl = ttl or RedisCache.CHAT_RESPONSE_TTL
            client.setex(key, ttl, json.dumps(response))
            logger.debug(f"Cached chat response: {key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache chat response: {e}")
            return False

    @staticmethod
    def get_cached_chat_response(query: str) -> Optional[dict]:
        """
        Get cached chat response.

        Args:
            query: User query

        Returns:
            Cached response or None
        """
        client = get_redis_client()
        if not client:
            return None

        try:
            key = RedisCache._get_cache_key("chat", {"query": query.lower().strip()})
            cached = client.get(key)
            if cached:
                logger.debug(f"Chat cache hit: {key}")
                return json.loads(cached)
            return None
        except Exception as e:
            logger.warning(f"Failed to get cached chat: {e}")
            return None

    @staticmethod
    def invalidate_prediction_cache(prediction_type: str = None) -> int:
        """
        Invalidate prediction cache.

        Args:
            prediction_type: Optional type to invalidate, or all if None

        Returns:
            Number of keys deleted
        """
        client = get_redis_client()
        if not client:
            return 0

        try:
            pattern = f"pred:{prediction_type or '*'}:*"
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Failed to invalidate cache: {e}")
            return 0

    @staticmethod
    def get_cache_stats() -> dict:
        """Get cache statistics"""
        client = get_redis_client()
        if not client:
            return {"status": "unavailable"}

        try:
            info = client.info("stats")
            keys = client.info("keyspace")
            return {
                "status": "connected",
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "total_keys": sum(
                    db_info.get("keys", 0)
                    for db_info in keys.values()
                    if isinstance(db_info, dict)
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Convenience functions
def cache_prediction(prediction_type: str, input_features: dict, result: dict) -> bool:
    """Cache a prediction result"""
    return RedisCache.cache_prediction(prediction_type, input_features, result)


def get_cached_prediction(prediction_type: str, input_features: dict) -> Optional[dict]:
    """Get cached prediction"""
    return RedisCache.get_cached_prediction(prediction_type, input_features)


def cache_chat_response(query: str, response: dict) -> bool:
    """Cache a chat response"""
    return RedisCache.cache_chat_response(query, response)


def get_cached_chat_response(query: str) -> Optional[dict]:
    """Get cached chat response"""
    return RedisCache.get_cached_chat_response(query)
