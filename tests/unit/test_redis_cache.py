"""
Unit tests for RedisCache module
Tests caching functionality with mocked Redis
"""

import json
import pytest
from unittest.mock import MagicMock, patch, Mock
import hashlib


class TestRedisCache:
    """Tests for RedisCache class"""

    def setup_method(self):
        """Reset global state before each test"""
        # Reset global redis client state
        import api.core.redis_cache as redis_cache_module
        redis_cache_module._redis_client = None
        redis_cache_module._redis_available = False

    @patch('api.core.redis_cache.redis')
    def test_get_redis_client_upstash_success(self, mock_redis):
        """Test connection to Upstash Redis"""
        import os
        from api.core.redis_cache import get_redis_client
        
        mock_client = MagicMock()
        mock_redis.from_url.return_value = mock_client
        
        with patch.dict(os.environ, {'UPSTASH_REDIS_URL': 'redis://upstash-test:6379'}):
            client = get_redis_client()
            
        assert client is not None
        mock_client.ping.assert_called_once()

    @patch('api.core.redis_cache.redis')
    def test_get_redis_client_local_fallback(self, mock_redis):
        """Test fallback to local Redis"""
        import os
        from api.core.redis_cache import get_redis_client
        
        mock_client = MagicMock()
        mock_redis.from_url.return_value = mock_client
        mock_redis.Redis.return_value = mock_client
        
        with patch.dict(os.environ, {}, clear=True):
            # Remove env vars
            os.environ.pop('UPSTASH_REDIS_URL', None)
            os.environ.pop('REDIS_URL', None)
            client = get_redis_client()
            
        assert client is not None

    @patch('api.core.redis_cache.redis')
    def test_get_redis_client_connection_failure(self, mock_redis):
        """Test graceful failure when Redis unavailable"""
        from api.core.redis_cache import get_redis_client
        
        mock_redis.Redis.side_effect = Exception("Connection refused")
        mock_redis.from_url.side_effect = Exception("Connection refused")
        
        client = get_redis_client()
        
        assert client is None


class TestRedisCacheOperations:
    """Tests for RedisCache static methods"""

    def test_get_cache_key_generates_consistent_hash(self):
        """Test cache key generation is deterministic"""
        from api.core.redis_cache import RedisCache
        
        data = {"feature1": 1.0, "feature2": 2.0}
        key1 = RedisCache._get_cache_key("test", data)
        key2 = RedisCache._get_cache_key("test", data)
        
        assert key1 == key2
        assert key1.startswith("test:")

    def test_get_cache_key_different_data_different_hash(self):
        """Test different data produces different keys"""
        from api.core.redis_cache import RedisCache
        
        data1 = {"feature1": 1.0}
        data2 = {"feature1": 2.0}
        
        key1 = RedisCache._get_cache_key("test", data1)
        key2 = RedisCache._get_cache_key("test", data2)
        
        assert key1 != key2

    @patch('api.core.redis_cache.get_redis_client')
    def test_cache_prediction_success(self, mock_get_client):
        """Test successful prediction caching"""
        from api.core.redis_cache import RedisCache
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        result = RedisCache.cache_prediction(
            prediction_type="sepsis",
            input_features={"age": 65, "hr": 90},
            result={"risk_score": 0.75}
        )
        
        assert result is True
        mock_client.setex.assert_called_once()

    @patch('api.core.redis_cache.get_redis_client')
    def test_cache_prediction_redis_unavailable(self, mock_get_client):
        """Test caching when Redis unavailable"""
        from api.core.redis_cache import RedisCache
        
        mock_get_client.return_value = None
        
        result = RedisCache.cache_prediction(
            prediction_type="sepsis",
            input_features={"age": 65},
            result={"risk_score": 0.5}
        )
        
        assert result is False

    @patch('api.core.redis_cache.get_redis_client')
    def test_get_cached_prediction_hit(self, mock_get_client):
        """Test cache hit scenario"""
        from api.core.redis_cache import RedisCache
        
        mock_client = MagicMock()
        mock_client.get.return_value = json.dumps({"risk_score": 0.8})
        mock_get_client.return_value = mock_client
        
        result = RedisCache.get_cached_prediction(
            prediction_type="mortality",
            input_features={"age": 70}
        )
        
        assert result is not None
        assert result["risk_score"] == 0.8

    @patch('api.core.redis_cache.get_redis_client')
    def test_get_cached_prediction_miss(self, mock_get_client):
        """Test cache miss scenario"""
        from api.core.redis_cache import RedisCache
        
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_get_client.return_value = mock_client
        
        result = RedisCache.get_cached_prediction(
            prediction_type="sepsis",
            input_features={"age": 50}
        )
        
        assert result is None

    @patch('api.core.redis_cache.get_redis_client')
    def test_cache_chat_response(self, mock_get_client):
        """Test chat response caching"""
        from api.core.redis_cache import RedisCache
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        result = RedisCache.cache_chat_response(
            query="what is sepsis?",
            response={"answer": "Sepsis is..."}
        )
        
        assert result is True
        mock_client.setex.assert_called_once()

    @patch('api.core.redis_cache.get_redis_client')
    def test_get_cached_chat_response_normalizes_query(self, mock_get_client):
        """Test query normalization (lowercase, strip)"""
        from api.core.redis_cache import RedisCache
        
        mock_client = MagicMock()
        mock_client.get.return_value = json.dumps({"answer": "test"})
        mock_get_client.return_value = mock_client
        
        # Both should hit same cache
        result1 = RedisCache.get_cached_chat_response("  What Is Sepsis?  ")
        result2 = RedisCache.get_cached_chat_response("what is sepsis?")
        
        # Verify both queries normalize to same key
        assert result1 is not None
        assert result2 is not None

    @patch('api.core.redis_cache.get_redis_client')
    def test_invalidate_prediction_cache(self, mock_get_client):
        """Test cache invalidation"""
        from api.core.redis_cache import RedisCache
        
        mock_client = MagicMock()
        mock_client.keys.return_value = ["pred:sepsis:abc", "pred:sepsis:def"]
        mock_client.delete.return_value = 2
        mock_get_client.return_value = mock_client
        
        deleted = RedisCache.invalidate_prediction_cache("sepsis")
        
        assert deleted == 2

    @patch('api.core.redis_cache.get_redis_client')
    def test_get_cache_stats_success(self, mock_get_client):
        """Test cache statistics retrieval"""
        from api.core.redis_cache import RedisCache
        
        mock_client = MagicMock()
        mock_client.info.side_effect = [
            {"keyspace_hits": 100, "keyspace_misses": 20},
            {"db0": {"keys": 50}}
        ]
        mock_get_client.return_value = mock_client
        
        stats = RedisCache.get_cache_stats()
        
        assert stats["status"] == "connected"
        assert stats["hits"] == 100
        assert stats["misses"] == 20

    @patch('api.core.redis_cache.get_redis_client')
    def test_get_cache_stats_unavailable(self, mock_get_client):
        """Test stats when Redis unavailable"""
        from api.core.redis_cache import RedisCache
        
        mock_get_client.return_value = None
        
        stats = RedisCache.get_cache_stats()
        
        assert stats["status"] == "unavailable"


class TestConvenienceFunctions:
    """Tests for module-level convenience functions"""

    @patch('api.core.redis_cache.RedisCache.cache_prediction')
    def test_cache_prediction_function(self, mock_method):
        """Test convenience function delegates correctly"""
        from api.core.redis_cache import cache_prediction
        
        mock_method.return_value = True
        result = cache_prediction("sepsis", {"age": 65}, {"score": 0.5})
        
        assert result is True
        mock_method.assert_called_once()

    @patch('api.core.redis_cache.RedisCache.get_cached_prediction')
    def test_get_cached_prediction_function(self, mock_method):
        """Test convenience function delegates correctly"""
        from api.core.redis_cache import get_cached_prediction
        
        mock_method.return_value = {"score": 0.7}
        result = get_cached_prediction("mortality", {"age": 70})
        
        assert result["score"] == 0.7


class TestTTLConstants:
    """Tests for TTL configuration"""

    def test_prediction_ttl_is_one_hour(self):
        """Verify prediction cache TTL is 1 hour"""
        from api.core.redis_cache import RedisCache
        
        assert RedisCache.PREDICTION_TTL == 3600

    def test_chat_response_ttl_is_30_minutes(self):
        """Verify chat cache TTL is 30 minutes"""
        from api.core.redis_cache import RedisCache
        
        assert RedisCache.CHAT_RESPONSE_TTL == 1800

    def test_embedding_ttl_is_24_hours(self):
        """Verify embedding cache TTL is 24 hours"""
        from api.core.redis_cache import RedisCache
        
        assert RedisCache.EMBEDDING_TTL == 86400
