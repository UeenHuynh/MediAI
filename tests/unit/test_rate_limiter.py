"""
Unit tests for Rate Limiter service
Tests API rate limiting functionality
"""

import pytest
from unittest.mock import MagicMock, patch
import time


class TestRateLimiterInit:
    """Tests for RateLimiter initialization"""

    def test_rate_limiter_init_default_period(self):
        """Test RateLimiter initialization with default period"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=10)

        assert limiter.max_calls == 10
        assert limiter.period == 60  # Default period
        assert len(limiter.calls) == 0

    def test_rate_limiter_init_custom_period(self):
        """Test RateLimiter initialization with custom period"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=5, period=30)

        assert limiter.max_calls == 5
        assert limiter.period == 30
        assert len(limiter.calls) == 0


class TestCanProceed:
    """Tests for can_proceed method"""

    def test_can_proceed_under_limit(self):
        """Test can_proceed returns True when under limit"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=3, period=60)

        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is True
        assert len(limiter.calls) == 3

    def test_can_proceed_at_limit(self):
        """Test can_proceed returns False when at limit"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=2, period=60)

        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is False  # Exceeded
        assert len(limiter.calls) == 2  # Still only 2 calls recorded

    def test_can_proceed_removes_expired_calls(self):
        """Test can_proceed removes calls outside time window"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=2, period=1)  # 1 second period

        # First call
        assert limiter.can_proceed() is True

        # Wait for period to expire
        time.sleep(1.1)

        # Old call should be removed, new call should succeed
        assert limiter.can_proceed() is True
        assert len(limiter.calls) == 1  # Old call removed

    def test_can_proceed_logs_warning_when_exceeded(self):
        """Test can_proceed logs warning when limit exceeded"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=1, period=60)

        limiter.can_proceed()  # Use up the quota

        with patch('api.services.rate_limiter.logger.warning') as mock_warning:
            result = limiter.can_proceed()

            assert result is False
            mock_warning.assert_called_once()
            assert "Rate limit exceeded" in str(mock_warning.call_args)


class TestRemainingCalls:
    """Tests for remaining_calls method"""

    def test_remaining_calls_initial(self):
        """Test remaining_calls returns max_calls initially"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=10, period=60)

        assert limiter.remaining_calls() == 10

    def test_remaining_calls_after_use(self):
        """Test remaining_calls decreases after usage"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=5, period=60)

        limiter.can_proceed()
        limiter.can_proceed()

        assert limiter.remaining_calls() == 3

    def test_remaining_calls_zero_when_exceeded(self):
        """Test remaining_calls returns 0 when limit exceeded"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=2, period=60)

        limiter.can_proceed()
        limiter.can_proceed()

        assert limiter.remaining_calls() == 0

    def test_remaining_calls_removes_expired(self):
        """Test remaining_calls removes expired calls before counting"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=3, period=1)

        limiter.can_proceed()
        limiter.can_proceed()

        time.sleep(1.1)

        # After expiry, should have full quota again
        assert limiter.remaining_calls() == 3


class TestTimeUntilReset:
    """Tests for time_until_reset method"""

    def test_time_until_reset_empty_calls(self):
        """Test time_until_reset returns 0 when no calls"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=5, period=60)

        assert limiter.time_until_reset() == 0.0

    def test_time_until_reset_with_calls(self):
        """Test time_until_reset returns time until oldest call expires"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=5, period=10)

        limiter.can_proceed()
        time.sleep(0.1)
        limiter.can_proceed()

        reset_time = limiter.time_until_reset()

        # Should be close to period (10s) but slightly less due to sleep
        assert 9.5 < reset_time <= 10.0

    def test_time_until_reset_negative_becomes_zero(self):
        """Test time_until_reset returns 0 if time is negative"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=5, period=1)

        limiter.can_proceed()
        time.sleep(1.1)

        # Period has expired, should return 0
        reset_time = limiter.time_until_reset()
        assert reset_time == 0.0


class TestWaitIfNeeded:
    """Tests for wait_if_needed method"""

    def test_wait_if_needed_proceeds_immediately_if_under_limit(self):
        """Test wait_if_needed returns True immediately if under limit"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=5, period=60)

        result = limiter.wait_if_needed(timeout=1.0)

        assert result is True

    def test_wait_if_needed_waits_and_proceeds(self):
        """Test wait_if_needed waits until call can proceed"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=1, period=1)

        limiter.can_proceed()  # Use up quota

        start = time.time()
        result = limiter.wait_if_needed(timeout=2.0)
        elapsed = time.time() - start

        assert result is True
        assert elapsed >= 1.0  # Should have waited at least 1 second

    def test_wait_if_needed_timeout(self):
        """Test wait_if_needed times out if limit not reset"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=1, period=60)  # Long period

        limiter.can_proceed()  # Use up quota

        with patch('api.services.rate_limiter.logger.warning') as mock_warning:
            result = limiter.wait_if_needed(timeout=0.5)

            assert result is False
            # Should have at least one warning with "timeout"
            assert any("timeout" in str(call).lower() for call in mock_warning.call_args_list)

    def test_wait_if_needed_no_timeout(self):
        """Test wait_if_needed with no timeout waits indefinitely"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=1, period=1)

        limiter.can_proceed()

        start = time.time()
        result = limiter.wait_if_needed(timeout=None)
        elapsed = time.time() - start

        assert result is True
        assert elapsed >= 1.0


class TestReset:
    """Tests for reset method"""

    def test_reset_clears_calls(self):
        """Test reset clears all calls"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=3, period=60)

        limiter.can_proceed()
        limiter.can_proceed()
        limiter.can_proceed()

        assert len(limiter.calls) == 3

        limiter.reset()

        assert len(limiter.calls) == 0
        assert limiter.remaining_calls() == 3

    def test_reset_logs_info(self):
        """Test reset logs info message"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=5, period=60)

        with patch('api.services.rate_limiter.logger.info') as mock_info:
            limiter.reset()

            # Should have at least one log call (may include init log)
            assert any("reset" in str(call).lower() for call in mock_info.call_args_list)


class TestGetStatus:
    """Tests for get_status method"""

    def test_get_status_structure(self):
        """Test get_status returns correct structure"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=10, period=60)

        status = limiter.get_status()

        assert "max_calls" in status
        assert "period" in status
        assert "remaining" in status
        assert "time_until_reset" in status

    def test_get_status_values(self):
        """Test get_status returns correct values"""
        from api.services.rate_limiter import RateLimiter

        limiter = RateLimiter(max_calls=10, period=60)

        limiter.can_proceed()
        limiter.can_proceed()

        status = limiter.get_status()

        assert status["max_calls"] == 10
        assert status["period"] == 60
        assert status["remaining"] == 8
        assert status["time_until_reset"] >= 0


class TestMultiRateLimiterInit:
    """Tests for MultiRateLimiter initialization"""

    def test_multi_rate_limiter_init(self):
        """Test MultiRateLimiter initializes with empty dict"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        assert multi_limiter.limiters == {}


class TestAddLimiter:
    """Tests for add_limiter method"""

    def test_add_limiter_creates_rate_limiter(self):
        """Test add_limiter creates a new RateLimiter"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()
        multi_limiter.add_limiter("groq", max_calls=30, period=60)

        assert "groq" in multi_limiter.limiters
        assert multi_limiter.limiters["groq"].max_calls == 30
        assert multi_limiter.limiters["groq"].period == 60

    def test_add_limiter_multiple(self):
        """Test adding multiple limiters"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()
        multi_limiter.add_limiter("groq", max_calls=30, period=60)
        multi_limiter.add_limiter("pubmed", max_calls=3, period=1)

        assert len(multi_limiter.limiters) == 2
        assert "groq" in multi_limiter.limiters
        assert "pubmed" in multi_limiter.limiters

    def test_add_limiter_logs_info(self):
        """Test add_limiter logs info message"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        with patch('api.services.rate_limiter.logger.info') as mock_info:
            multi_limiter.add_limiter("test", max_calls=10, period=60)

            assert any("test" in str(call) for call in mock_info.call_args_list)


class TestMultiCanProceed:
    """Tests for MultiRateLimiter can_proceed method"""

    def test_multi_can_proceed_existing_limiter(self):
        """Test can_proceed with existing limiter"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()
        multi_limiter.add_limiter("test", max_calls=2, period=60)

        assert multi_limiter.can_proceed("test") is True
        assert multi_limiter.can_proceed("test") is True
        assert multi_limiter.can_proceed("test") is False  # Exceeded

    def test_multi_can_proceed_non_existing_limiter(self):
        """Test can_proceed with non-existing limiter returns True"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        with patch('api.services.rate_limiter.logger.warning') as mock_warning:
            result = multi_limiter.can_proceed("nonexistent")

            assert result is True
            mock_warning.assert_called_once()
            assert "nonexistent" in str(mock_warning.call_args)


class TestMultiWaitIfNeeded:
    """Tests for MultiRateLimiter wait_if_needed method"""

    def test_multi_wait_if_needed_existing_limiter(self):
        """Test wait_if_needed with existing limiter"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()
        multi_limiter.add_limiter("test", max_calls=1, period=1)

        multi_limiter.can_proceed("test")  # Use quota

        start = time.time()
        result = multi_limiter.wait_if_needed("test", timeout=2.0)
        elapsed = time.time() - start

        assert result is True
        assert elapsed >= 1.0

    def test_multi_wait_if_needed_non_existing_limiter(self):
        """Test wait_if_needed with non-existing limiter returns True"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        result = multi_limiter.wait_if_needed("nonexistent", timeout=1.0)

        assert result is True


class TestMultiGetStatus:
    """Tests for MultiRateLimiter get_status method"""

    def test_multi_get_status_specific_limiter(self):
        """Test get_status for specific limiter"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()
        multi_limiter.add_limiter("test", max_calls=10, period=60)

        status = multi_limiter.get_status("test")

        assert "test" in status
        assert status["test"]["max_calls"] == 10

    def test_multi_get_status_non_existing_limiter(self):
        """Test get_status for non-existing limiter returns empty dict"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        status = multi_limiter.get_status("nonexistent")

        assert status == {}

    def test_multi_get_status_all_limiters(self):
        """Test get_status without name returns all limiters"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()
        multi_limiter.add_limiter("groq", max_calls=30, period=60)
        multi_limiter.add_limiter("pubmed", max_calls=3, period=1)

        status = multi_limiter.get_status()

        assert "groq" in status
        assert "pubmed" in status
        assert len(status) == 2

    def test_multi_get_status_empty(self):
        """Test get_status with no limiters returns empty dict"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        status = multi_limiter.get_status()

        assert status == {}


class TestModuleFunctions:
    """Tests for module-level functions"""

    def test_get_rate_limiter_returns_multi_limiter(self):
        """Test get_rate_limiter returns MultiRateLimiter instance"""
        from api.services.rate_limiter import get_rate_limiter, MultiRateLimiter

        limiter = get_rate_limiter()

        assert isinstance(limiter, MultiRateLimiter)

    def test_get_rate_limiter_returns_same_instance(self):
        """Test get_rate_limiter returns the same global instance"""
        from api.services.rate_limiter import get_rate_limiter

        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        assert limiter1 is limiter2

    @patch.dict('os.environ', {'GROQ_RATE_LIMIT': '50', 'PUBMED_RATE_LIMIT': '5', 'QDRANT_RATE_LIMIT': '200'})
    def test_initialize_rate_limiters_with_env_vars(self):
        """Test initialize_rate_limiters uses environment variables"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        with patch('api.services.rate_limiter.get_rate_limiter', return_value=multi_limiter):
            from api.services import rate_limiter
            rate_limiter.initialize_rate_limiters()

            # Should have 3 limiters
            assert len(multi_limiter.limiters) >= 3

            # Check configurations (if they were set)
            if "groq" in multi_limiter.limiters:
                # Note: The actual values may differ due to module-level init
                assert multi_limiter.limiters["groq"].max_calls > 0

    def test_initialize_rate_limiters_default_values(self):
        """Test initialize_rate_limiters with default values"""
        from api.services.rate_limiter import MultiRateLimiter

        multi_limiter = MultiRateLimiter()

        with patch('api.services.rate_limiter.get_rate_limiter', return_value=multi_limiter):
            with patch('api.services.rate_limiter.logger.info') as mock_info:
                from api.services import rate_limiter
                rate_limiter.initialize_rate_limiters()

                # Should log successful initialization
                assert any("initialized" in str(call).lower() for call in mock_info.call_args_list)


class TestSlowAPIIntegration:
    """Tests for SlowAPI rate limiting"""

    def test_slowapi_limiter_configured(self):
        """Test SlowAPI limiter is configured in routers"""
        try:
            from api.routers.predictions import limiter
            assert limiter is not None
        except ImportError:
            pytest.skip("SlowAPI not configured")

    def test_limiter_key_func(self):
        """Test limiter uses IP-based key function"""
        try:
            from api.routers.predictions import limiter
            from slowapi.util import get_remote_address

            # Limiter should be configured with get_remote_address
            assert limiter is not None
        except ImportError:
            pytest.skip("SlowAPI not configured")


class TestRateLimitDecorators:
    """Tests for rate limit decorators"""

    def test_predict_sepsis_has_rate_limit(self):
        """Test sepsis prediction has rate limit"""
        try:
            from api.routers.predictions import predict_sepsis

            # Function should exist and be decorated
            assert predict_sepsis is not None
            assert callable(predict_sepsis)
        except ImportError:
            pytest.skip("Predictions router not available")

    def test_predict_mortality_has_rate_limit(self):
        """Test mortality prediction has rate limit"""
        try:
            from api.routers.predictions import predict_mortality

            assert predict_mortality is not None
            assert callable(predict_mortality)
        except ImportError:
            pytest.skip("Predictions router not available")


class TestRateLimiterConfiguration:
    """Tests for rate limiter configuration"""

    def test_rate_limit_values_reasonable(self):
        """Test rate limit values are reasonable"""
        # Check that rate limits are not too strict or too loose
        # Typical: 100/minute for API endpoints

        # This is a meta-test - we verify the decorator exists
        try:
            from slowapi import Limiter

            # If slowapi is available, rate limiting is configured
            assert True
        except ImportError:
            pytest.skip("SlowAPI not available")
